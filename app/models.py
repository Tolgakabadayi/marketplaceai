from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    projects = db.relationship('Project', backref='owner', lazy='dynamic')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), index=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    tech_stack = db.Column(db.String(250))
    price = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # GitHub integration
    github_url = db.Column(db.String(300), nullable=True)  # Seller-only, hidden from buyers
    
    # Image uploads (comma-separated filenames)
    images = db.Column(db.Text, nullable=True)
    
    # Relationships
    ai_analysis = db.relationship('AIAnalysis', backref='project', uselist=False, cascade="all, delete-orphan")
    analytics = db.relationship('Analytics', backref='project', uselist=False, cascade="all, delete-orphan")

    def get_images(self):
        if self.images:
            return [img.strip() for img in self.images.split(',') if img.strip()]
        return []

    def __repr__(self):
        return f'<Project {self.title}>'

class AIAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    tags = db.Column(db.Text)
    complexity_score = db.Column(db.String(50))
    niche = db.Column(db.String(100))
    potential_star = db.Column(db.Integer, default=1)
    health_score = db.Column(db.Integer, default=0)
    insight_comment = db.Column(db.Text)
    suggestion = db.Column(db.Text)

    def __repr__(self):
        return f'<AIAnalysis for Project {self.project_id}>'

class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    views = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    heatmap_data = db.Column(db.Text, default="{}")

    def __repr__(self):
        return f'<Analytics for Project {self.project_id}>'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Message {self.id} from {self.sender_id}>'
