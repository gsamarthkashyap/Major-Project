from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

db = SQLAlchemy()  # this will be linked to your app later

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(20), nullable=False)  # 'github' or 'google'
    provider_user_id = db.Column(db.String(100), nullable=False, unique=True)  # GitHub ID
    username = db.Column(db.String(100))
    email = db.Column(db.String(150))
    avatar_url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Organization(db.Model):
    __tablename__ = "gsoc_organizations"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.Text, nullable=False)  # Removed primary_key, uses 'id'
    name = db.Column(db.Text, nullable=False)
    logo_url = db.Column(db.Text)
    website_url = db.Column(db.Text)
    tagline = db.Column(db.Text)
    contact_links = db.Column(JSONB)
    date_created = db.Column(db.DateTime)
    tech_tags = db.Column(JSONB)
    topic_tags = db.Column(JSONB)
    categories = db.Column(JSONB)
    program_slug = db.Column(JSONB)
    logo_bg_color = db.Column(db.Text)
    description_html = db.Column(db.Text)
    ideas_list_url = db.Column(db.Text)
    github_url = db.Column(db.Text)
    github_followers = db.Column(db.Integer)
    github_repos = db.Column(db.Integer)
    github_bio = db.Column(db.Text)
    year = db.Column(db.Integer)
    fetched_at = db.Column(db.DateTime)



class GithubMetrics(db.Model):
    __tablename__ = "github_metrics"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text)
    slug = db.Column(db.Text, unique=True, nullable=False)
    github_followers = db.Column(db.Integer)
    github_repos = db.Column(db.Integer)
    github_bio = db.Column(db.Text)
    fetched_at = db.Column(db.DateTime)
    pull_requests = db.Column(db.Integer)
    merged_prs = db.Column(db.Integer)
    merge_frequency = db.Column(db.Float)  # DOUBLE PRECISION


    def __repr__(self):
        return f"<GithubMetrics {self.name}>"

