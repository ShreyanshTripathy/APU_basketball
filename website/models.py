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
    is_league = db.Column(db.Boolean, default=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)

    # Relationships
    matches = db.relationship('Match', backref='event', lazy=True)
    teams = db.relationship('Team', backref='event', lazy=True, cascade='all, delete-orphan')
    galleries = db.relationship('GalleryAlbum', backref='event', lazy=True)


class CoreMembers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    # Number = db.Column(db.String(15), nullable=False)
    # email_id = db.Column(db.String(100), nullable=False)
    picture = db.Column(db.String(255), nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(100), nullable=False)
    captain_name = db.Column(db.String(100), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

    members = db.relationship('TeamMembers', backref='team', lazy=True, cascade='all, delete')
    matches_as_team_a = db.relationship('Match', foreign_keys='Match.team_a_id', backref='team_a', lazy=True, cascade='all, delete-orphan')
    matches_as_team_b = db.relationship('Match', foreign_keys='Match.team_b_id', backref='team_b', lazy=True, cascade='all, delete-orphan')
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)

class TeamMembers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    gender = db.Column(db.String(100))
    level = db.Column(db.String(20))


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

# New model for editable homepage content
class HomePageContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    header_title = db.Column(db.String(100), nullable=False, default="Basketball club")
    header_subtitle = db.Column(db.String(255), nullable=False, default="This is what we do.")
    header_image = db.Column(db.String(255), nullable=False, default="bb.jpg")
    main_paragraph_1 = db.Column(db.Text, nullable=False, default="Lorem ipsum dolor sit amet, consectetur adipisicing elit. Saepe nostrum ullam eveniet pariatur voluptates odit, fuga atque ea nobis sit soluta odio, adipisci quas excepturi maxime quae totam ducimus consectetur?")
    main_paragraph_2 = db.Column(db.Text, nullable=False, default="Lorem ipsum dolor sit amet, consectetur adipisicing elit. Eius praesentium recusandae illo eaque architecto error, repellendus iusto reprehenderit, doloribus, minus sunt. Numquam at quae voluptatum in officia voluptas voluptatibus, minus!")
    main_paragraph_3 = db.Column(db.Text, nullable=False, default="Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut consequuntur magnam, excepturi aliquid ex itaque esse est vero natus quae optio aperiam soluta voluptatibus corporis atque iste neque sit tempora!")
