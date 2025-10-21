import os
from datetime import datetime, timezone
from flask import Flask, redirect, url_for, session
from flask_dance.contrib.github import make_github_blueprint, github
from models import db, User , Organization
from sqlalchemy.dialects.postgresql import JSONB
from flask import jsonify
from dotenv import load_dotenv

load_dotenv()
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # allow HTTP locally

app = Flask(__name__)
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

    return f"Hello, {user.username}! You are logged in."

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
            "description": org.description,
            "logo_url": org.logo_url,
            "website_url": org.website_url,
            "ideas_url": org.ideas_url,
            "source_code_url": org.source_code_url,
            "tech_tags": org.tech_tags or [],
            "topic_tags": org.topic_tags or [],
            "categories": org.categories or [],
            "github_url": org.github_url,
            "github_data": org.github_data or {}
        })
    return jsonify(org_list)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
