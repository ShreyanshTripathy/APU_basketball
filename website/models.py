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

    matches = db.relationship('Match', backref='event', lazy=True)
    teams = db.relationship('Team', backref='event', lazy=True)


class CoreMembers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Number = db.Column(db.String(15), nullable=False)  # Use String for flexible phone formats
    email_id = db.Column(db.String(100), nullable=False)
    picture = db.Column(db.String(255), nullable=True)  # Store the path to the uploaded image

    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id')) 


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(100), nullable=False)

    members = db.relationship('TeamMembers', backref='team', lazy=True)

    # Matches where this team is Team A
    matches_as_team_a = db.relationship('Match', foreign_keys='Match.team_a_id', backref='team_a', lazy=True)

    # Matches where this team is Team B
    matches_as_team_b = db.relationship('Match', foreign_keys='Match.team_b_id', backref='team_b', lazy=True)

    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False) 


class TeamMembers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    designation = db.Column(db.String(100)) # Captain/Male-Beginner/Male-Intermediate/Non-male/Faculty
    year = db.Column(db.Integer)

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)


# We can schedule future matches as well, and then later update the scores
class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    team_a_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    team_b_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)

    date_time = db.Column(db.DateTime, default=func.now()) # Match date and timings
    team_a_score = db.Column(db.Integer)
    team_b_score = db.Column(db.Integer)

    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
