from datetime import datetime
from flask import Blueprint, render_template
from .models import Event

views = Blueprint('views', __name__)

@views.route('/')
def home():
    # Filter events where the end_date is greater than the current date and time
    active_events = Event.query.filter(Event.end_date > datetime.now()).all()
    return render_template('home.html', events=active_events)
