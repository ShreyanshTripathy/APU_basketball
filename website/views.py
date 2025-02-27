from datetime import datetime
from flask import Blueprint, render_template
from .models import Event, HomePageContent

views = Blueprint('views', __name__)

@views.route('/')
def home():
    # Filter events where the end_date is greater than the current date and time
    active_events = Event.query.filter(Event.end_date > datetime.now()).all()
    home_content = HomePageContent.query.first()
    # If no homepage content exists, create a default one.
    if not home_content:
        from . import db
        home_content = HomePageContent()
        db.session.add(home_content)
        db.session.commit()
    return render_template('home.html', events=active_events, home_content=home_content)
