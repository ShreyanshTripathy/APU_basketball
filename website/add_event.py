from flask import Blueprint, render_template, flash, redirect, url_for, request, abort,current_app
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
import os
from datetime import datetime
from .models import Event,GalleryImage, GalleryAlbum, Team
from . import db

add_event = Blueprint('add_event', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@add_event.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_new_event():
    if current_user.id != 1:
        flash("You do not have permission to access this page.", category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        link = request.form.get('link')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        image = request.files.get('image')
        # NEW: Determine if it's a league event (checkbox returns a truthy value if checked)
        is_league = True if request.form.get('is_league') else False

        if not title or not description or not image:
            flash('Please fill in all fields!', category='error')
            return render_template(
                    "add_event.html",
                    title=title,
                    description=description,
                    link=link,
                    start_date=start_date_str,
                    end_date=end_date_str,
                    is_league=request.form.get('is_league')
                )
        if not allowed_file(image.filename):
            flash('Invalid image format! Allowed formats: png, jpg, jpeg.', category='error')
            return redirect(url_for('add_event.add_new_event'))

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
        except ValueError:
            flash("Invalid date format. Please use the correct format.", category='error')
            return redirect(url_for('add_event.add_new_event'))

        if start_date and end_date and start_date > end_date:
            flash("Start date cannot be after end date.", category='error')
            return redirect(url_for('add_event.add_new_event'))

        image_filename = secure_filename(image.filename)
        image_path = os.path.join(current_app.root_path, 'static', 'assets', 'img', 'Event', image_filename)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)

        try:
            image.save(image_path)
            new_event = Event(
                title=title,
                description=description,
                img_url=image_filename,
                start_date=start_date,
                end_date=end_date,
                admin_id=current_user.id,
                link=link,
                is_league=is_league    # NEW FIELD ASSIGNMENT
            )
            db.session.add(new_event)
            db.session.commit()

            flash('Event added successfully!', category='success')
            return redirect(url_for('views.home'))

        except Exception as e:
            flash(f"An error occurred: {str(e)}", category='error')
            return redirect(url_for('add_event.add_new_event'))

    return render_template("add_event.html")


@add_event.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    if current_user.id != 1:
        flash("You do not have permission to edit events.", category='error')
        return redirect(url_for('views.home'))

    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        link = request.form.get('link')  # Capture the event link
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        image = request.files.get('image')

        if not title or not description:
            flash("Title and description are required.", category='error')
            return redirect(url_for('add_event.edit_event', event_id=event_id))
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
        except ValueError:
            flash("Invalid date format.", category='error')
            return redirect(url_for('add_event.edit_event', event_id=event_id))

        if start_date and end_date and start_date > end_date:
            flash("Start date cannot be after end date.", category='error')
            return redirect(url_for('add_event.edit_event', event_id=event_id))

        event.title = title
        event.description = description
        event.link = link  # Update the link field
        event.start_date = start_date
        event.end_date = end_date

        # Update the league event status based on the checkbox value.
        event.is_league = True if request.form.get('is_league') else False

        if image and allowed_file(image.filename):
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(current_app.root_path, 'static', 'assets', 'img', 'Event', image_filename)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            image.save(image_path)
            event.img_url = image_filename

        db.session.commit()
        flash("Event updated successfully.", category='success')
        return redirect(url_for('add_event.event_page', event_id=event.id))

    return render_template("edit_event.html", event=event)


@add_event.route('/delete_event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    if current_user.id != 1:
        flash("You do not have permission to delete events.", category='error')
        return redirect(url_for('views.home'))

    event = Event.query.get_or_404(event_id)
    if len(event.galleries)>0:
        flash("This event containas images, delete the images from galleries to delete the event")
        return event_page(event_id)

    image_path = os.path.join(current_app.root_path, 'static', 'assets', 'img', 'Event', event.img_url)
    if os.path.exists(image_path):
        os.remove(image_path)

    db.session.delete(event)
    db.session.commit()
    flash("Event deleted successfully.", category='success')
    return redirect(url_for('views.home'))

@add_event.route('/event/<int:event_id>', methods=['GET'], endpoint='event_page')
def event_page(event_id):
    event = Event.query.get_or_404(event_id)
    if event.end_date and event.end_date <= datetime.now().date():
        abort(404)

    # Query all images from albums associated with this event
    gallery_images = GalleryImage.query.join(GalleryAlbum).filter(GalleryAlbum.event_id == event.id).all()

    # Fetch teams and include team_id
    teams = Team.query.filter_by(event_id=event_id).all()
    team_data = {
        t.team_name: {
            "team_id": t.id,
            "captain": t.captain_name,
            "members": [(m.name, m.level, m.gender) for m in t.members]
        } for t in teams
    }

    # Sort matches:
    # Define upcoming matches as those without both scores (i.e. not yet played)
    # Completed matches have both scores entered.
    matches = event.matches
    upcoming_matches = [m for m in matches if m.team_a_score is None or m.team_b_score is None]
    completed_matches = [m for m in matches if m.team_a_score is not None and m.team_b_score is not None]

    # Sort upcoming matches by date_time ascending (earliest first)
    upcoming_matches.sort(key=lambda m: m.date_time)
    # Optionally, sort completed matches by date_time ascending as well
    completed_matches.sort(key=lambda m: m.date_time)

    # Combine: upcoming fixtures on top, then completed ones at the bottom
    sorted_matches = upcoming_matches + completed_matches

    return render_template('event_page.html', event=event, gallery_images=gallery_images, team=team_data, matches=sorted_matches)
