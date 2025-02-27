from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
import os
from datetime import datetime
from .models import Event,GalleryImage, GalleryAlbum
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

        if not title or not description or not image:
            flash('Please fill in all fields!', category='error')
            return redirect(url_for('add_event.add_new_event'))
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
        image_path = os.path.join('website', 'static', 'assets', 'img', image_filename)
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
                link=link  # Save the link
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
        link = request.form.get('link')  # Capture the link value
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

        if image and allowed_file(image.filename):
            image_filename = secure_filename(image.filename)
            image_path = os.path.join('website', 'static', 'assets', 'img', image_filename)
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
    db.session.delete(event)
    db.session.commit()
    flash("Event deleted successfully.", category='success')
    return redirect(url_for('views.home'))

@add_event.route('/event/<int:event_id>', methods=['GET'], endpoint='event_page')
def event_page(event_id):
    event = Event.query.get_or_404(event_id)
    if event.end_date and event.end_date <= datetime.now().date():
        abort(404)
    # Query all images from albums that are associated with this event
    gallery_images = GalleryImage.query.join(GalleryAlbum).filter(GalleryAlbum.event_id == event.id).all()
    return render_template('event_page.html', event=event, gallery_images=gallery_images)



