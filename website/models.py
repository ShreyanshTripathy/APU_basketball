from . import db
from flask_login import UserMixin
from sqlalchemy import func


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(150))  # Increased length for hashed passwords

    # Relationships
    events = db.relationship('Event', backref='admin', lazy=True)
    matches = db.relationship('Match', backref='admin', lazy=True)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.DateTime, default=func.now())
    end_date = db.Column(db.DateTime, default=func.now())
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    # matches = db.relationship('Match', backref='event', lazy=True)
    
class Core_members(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Number = db.Column(db.String(15), nullable=False)  # Use String for flexible phone formats
    email_id = db.Column(db.String(100), nullable=False)
    picture = db.Column(db.String(255), nullable=True)  # Store the path to the uploaded image
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id')) 
    
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_name = db.Column(db.String(100), nullable=False)
    team_name = db.Column(db.String(100), nullable=False)
    captain = db.Column(db.Boolean, default=False)

    # Relationship for team A (matches where this team is in team_a_id)
    # team_a_matches = db.relationship('Match', foreign_keys='Match.team_a_id', back_populates='team_a')

    # Relationship for team B (matches where this team is in team_b_id)
    # team_b_matches = db.relationship('Match', foreign_keys='Match.team_b_id', back_populates='team_b')
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False) 


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_a_id = db.Column(db.Integer, nullable=False)
    team_b_id = db.Column(db.Integer, nullable=False)
    date_time = db.Column(db.DateTime, default=func.now())
    team_a_score = db.Column(db.Integer)
    team_b_score = db.Column(db.Integer)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

    # Explicitly define the reverse relationships using back_populates
    # team_a = db.relationship('Team', foreign_keys=[team_a_id], back_populates='team_a_matches')
    # team_b = db.relationship('Team', foreign_keys=[team_b_id], back_populates='team_b_matches')
