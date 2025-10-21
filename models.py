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
    __tablename__ = "organisation"
    slug = db.Column(db.String, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    tagline = db.Column(db.Text)
    description = db.Column(db.Text)
    logo_url = db.Column(db.Text)
    website_url = db.Column(db.Text)
    ideas_url = db.Column(db.Text)
    source_code_url = db.Column(db.Text)
    tech_tags = db.Column(JSONB)
    topic_tags = db.Column(JSONB)
    categories = db.Column(JSONB)
    github_url = db.Column(db.Text)
    github_data = db.Column(JSONB)
