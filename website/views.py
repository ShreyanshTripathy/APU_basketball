from datetime import datetime
from flask import Blueprint, render_template
from .models import Event

views = Blueprint('views', __name__)

@views.route('/')
def home():
<<<<<<< HEAD
    # Filter events where the end_date is greater than the current date and time
    active_events = Event.query.filter(Event.end_date > datetime.now()).all()
    return render_template('home.html', events=active_events)
=======
    return render_template("home.html")

>>>>>>> 3719b3d81093853cd794739f61999b6ef6a4da2f
