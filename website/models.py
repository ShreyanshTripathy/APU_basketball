from . import db
from flask_login import UserMixin
from sqlalchemy import func

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(150))
    events = db.relationship('Event', backref='admin', lazy=True)
    matches = db.relationship('Match', backref='admin', lazy=True)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, default=func.current_date())
    end_date = db.Column(db.Date, default=func.current_date())
    link = db.Column(db.String(255), nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)

    matches = db.relationship('Match', backref='event', lazy=True)
    teams = db.relationship('Team', backref='event', lazy=True)
    galleries = db.relationship('GalleryAlbum', backref='event', lazy=True)


class CoreMembers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Number = db.Column(db.String(15), nullable=False)
    email_id = db.Column(db.String(100), nullable=False)
    picture = db.Column(db.String(255), nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(100), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    members = db.relationship('TeamMembers', backref='team', lazy=True)
    matches_as_team_a = db.relationship('Match', foreign_keys='Match.team_a_id', backref='team_a', lazy=True)
    matches_as_team_b = db.relationship('Match', foreign_keys='Match.team_b_id', backref='team_b', lazy=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)

class TeamMembers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    year = db.Column(db.Integer)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_a_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    team_b_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    date_time = db.Column(db.DateTime, default=func.now())
    team_a_score = db.Column(db.Integer)
    team_b_score = db.Column(db.Integer)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

class GalleryAlbum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=True)
    date_created = db.Column(db.Date, default=func.current_date())
    images = db.relationship('GalleryImage', backref='album', lazy=True)

class GalleryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('gallery_album.id'), nullable=False)
