import os
from datetime import datetime
from flask import Flask, redirect, url_for
from flask_dance.contrib.github import make_github_blueprint, github
from models import db, User
from flask import session
from dotenv import load_dotenv

load_dotenv()
# Allow HTTP for local testing
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

db.init_app(app)

# OAuth setup
github_bp = make_github_blueprint(
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET")
)
app.register_blueprint(github_bp, url_prefix="/login")

# Home route
@app.route("/")
def index():
    if not github.authorized:
        return redirect(url_for("github.login"))

    # Fetch GitHub user info
    resp = github.get("/user")
    assert resp.ok, resp.text
    github_info = resp.json()

    # Check if user exists
    user = User.query.filter_by(
        provider="github",
        provider_user_id=str(github_info["id"])
    ).first()

    if not user:
        # Create new user
        user = User(
            provider="github",
            provider_user_id=str(github_info["id"]),
            username=github_info.get("login"),
            email=github_info.get("email") or "",  # handle None
            avatar_url=github_info.get("avatar_url"),
        )
        db.session.add(user)

    # Update last login timestamp
    user.last_login = datetime.utcnow()
    db.session.commit()

    return f"Hello, {user.username}! You are logged in."



@app.route("/logout")
def logout():
    # Clear GitHub OAuth token
    if "github_oauth_token" in session:
        session.pop("github_oauth_token")
    return "Logged out. You can now login again."


# Run the app
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)

