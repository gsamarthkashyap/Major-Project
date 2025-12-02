import os
from datetime import datetime, timezone
from flask import Flask, redirect, url_for, session, jsonify
from flask_dance.contrib.github import make_github_blueprint, github
from sqlalchemy import func
from models import db, User, Organization, GithubMetrics
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # allow HTTP locally

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db.init_app(app)

# OAuth setup with redirect_to /authorize route
github_bp = make_github_blueprint(
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
    redirect_to="index"
)
app.register_blueprint(github_bp, url_prefix="/login")

@app.route("/authorize")
def index():
    # Force login if not authorized
    if not github.authorized:
        return redirect(url_for("github.login", _external=True, prompt="login"))

    # Try to fetch GitHub user info
    resp = github.get("/user")
    print(resp.json())

    # If token is revoked or invalid, clear session and re-login
    if not resp.ok:
        session.clear()
        return redirect(url_for("github.login", _external=True, prompt="login"))

    github_info = resp.json()

    # Get or create user in DB
    user = User.query.filter_by(
        provider="github",
        provider_user_id=str(github_info["id"])
    ).first()

    if not user:
        user = User(
            provider="github",
            provider_user_id=str(github_info["id"]),
            username=github_info.get("login"),
            email=github_info.get("email") or "",
            avatar_url=github_info.get("avatar_url"),
        )
        db.session.add(user)

    # Update last login with timezone-aware datetime
    user.last_login = datetime.now(timezone.utc)
    db.session.commit()

    # Redirect back to frontend dashboard
    return redirect("http://localhost:3000/Dashboard")

@app.route("/logout")
def logout():
    session.clear()  # clear all session keys
    return "Logged out. You can now login again."

@app.route("/api/organizations", methods=["GET"])
def get_organizations():
    organizations = Organization.query.all()
    org_list = []
    for org in organizations:
        org_list.append({
            "slug": org.slug,
            "name": org.name,
            "tagline": org.tagline,
            # "description": getattr(org, "description", None),
            "logo_url": org.logo_url,
            "website_url": org.website_url,
            "ideas_url": getattr(org, "ideas_url", None),  # Safe access
            "source_code_url": getattr(org, "source_code_url", None),
            "tech_tags": getattr(org, "tech_tags", []) or [],
            "topic_tags": getattr(org, "topic_tags", []) or [],
            "categories": getattr(org, "categories", []) or [],
            "github_url": getattr(org, "github_url", None),
            "github_repo": getattr(org, "github_url", None),  # Direct use
            "github_data": getattr(org, "github_data", {}) or {}
        })
    return jsonify(org_list)

from flask import request
from sqlalchemy import func

@app.route("/api/organizations/<path:name>", methods=["GET"])
def get_organization(name):

    # 1. Proper decoding of "%20", "%2F", etc
    decoded_name = request.view_args["name"]
    decoded_name = decoded_name.replace("%20", " ")

    # 2. Normalize: trim → lowercase → collapse multiple spaces
    normalized_name = " ".join(decoded_name.split()).strip().lower()

    # 3. Query Organizations (case-insensitive)
    org = (
        Organization.query
        .filter(func.lower(func.trim(Organization.name)) == normalized_name)
        .first()
    )

    if not org:
        return jsonify({"error": "Organization not found"}), 404

    # 4. Query GithubMetrics (case-insensitive)
    metrics = (
        GithubMetrics.query
        .filter(func.lower(func.trim(GithubMetrics.name)) == normalized_name)
        .first()
    )

    github_metrics = {}
    if metrics:
        github_metrics = {
            "name": metrics.name,
            "slug": metrics.slug,
            "github_followers": metrics.github_followers,
            "github_repos": metrics.github_repos,
            "github_bio": metrics.github_bio,
            "fetched_at": metrics.fetched_at,
            "pull_requests": metrics.pull_requests,
            "merged_prs": metrics.merged_prs,
            "merge_frequency": metrics.merge_frequency
        }

    org_data = {
        "id": org.id,
        "slug": org.slug,
        "name": org.name,
        "logo_url": org.logo_url,
        "website_url": org.website_url,
        "tagline": org.tagline,
        "contact_links": org.contact_links or [],
        "date_created": org.date_created,
        "tech_tags": org.tech_tags or [],
        "topic_tags": org.topic_tags or [],
        "categories": org.categories or [],
        "program_slug": org.program_slug,
        "logo_bg_color": org.logo_bg_color,
        "description_html": org.description_html,
        "ideas_list_url": org.ideas_list_url,
        "github_url": org.github_url,
        "github_followers": org.github_followers,
        "github_repos": org.github_repos,
        "github_bio": org.github_bio,
        "year": org.year,
        "fetched_at": org.fetched_at,
        "github_metrics": github_metrics
    }

    return jsonify(org_data)




if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure this is included only if you want auto-table creation
    app.run(debug=True, host="127.0.0.1", port=5000)
