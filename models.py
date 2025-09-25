from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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
