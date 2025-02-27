from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from .models import GalleryAlbum, GalleryImage, Event
from . import db
from flask_login import login_required, current_user
import os

gallery = Blueprint('gallery', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Gallery overview: list all albums
@gallery.route('/')
def gallery_view():
    albums = GalleryAlbum.query.all()
    return render_template('gallery.html', albums=albums)

# Add a new album with multiple images
@gallery.route('/add', methods=['GET', 'POST'])
@login_required
def add_gallery():
    if current_user.id != 1:
        flash('Only admin can add gallery albums.', 'danger')
        return redirect(url_for('gallery.gallery_view'))
    
    events = Event.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        event_id = request.form.get('event_id')
        if event_id == "":
            event_id = None
        images = request.files.getlist('images')
        
        if not title or not description or not images or len(images) == 0:
            flash('Title, description, and at least one image are required!', 'danger')
            return redirect(url_for('gallery.add_gallery'))
        
        # Create the album first.
        new_album = GalleryAlbum(
            title=title,
            description=description,
            event_id=event_id
        )
        db.session.add(new_album)
        db.session.commit()  # Commit so new_album.id is available.
        
        upload_folder = os.path.join('website', 'static', 'assets', 'img')
        os.makedirs(upload_folder, exist_ok=True)
        
        for image in images:
            if image and allowed_file(image.filename):
                image_filename = secure_filename(image.filename)
                image_path = os.path.join(upload_folder, image_filename)
                image.save(image_path)
                new_image = GalleryImage(
                    image_url=image_filename,
                    album_id=new_album.id
                )
                db.session.add(new_image)
            else:
                flash('One of the files is not a valid image format.', 'warning')
        db.session.commit()
        flash('Gallery album created successfully!', 'success')
        return redirect(url_for('gallery.gallery_view'))
    
    return render_template('add_gallery.html', events=events)

# Album detail: view all images in an album
@gallery.route('/<int:album_id>')
def gallery_detail(album_id):
    album = GalleryAlbum.query.get_or_404(album_id)
    return render_template('gallery_detail.html', album=album)

# Edit album details and add new images
@gallery.route('/edit/<int:album_id>', methods=['GET', 'POST'])
@login_required
def edit_gallery(album_id):
    if current_user.id != 1:
        flash('Only admin can edit gallery albums.', 'danger')
        return redirect(url_for('gallery.gallery_view'))
    
    album = GalleryAlbum.query.get_or_404(album_id)
    events = Event.query.all()
    
    if request.method == 'POST':
        album.title = request.form.get('title')
        album.description = request.form.get('description')
        event_id = request.form.get('event_id')
        if event_id == "":
            album.event_id = None
        else:
            album.event_id = event_id
        
        # Handle additional image uploads (optional)
        new_images = request.files.getlist('images')
        upload_folder = os.path.join('website', 'static', 'assets', 'img')
        os.makedirs(upload_folder, exist_ok=True)
        
        for image in new_images:
            if image and allowed_file(image.filename):
                image_filename = secure_filename(image.filename)
                image_path = os.path.join(upload_folder, image_filename)
                image.save(image_path)
                new_image = GalleryImage(
                    image_url=image_filename,
                    album_id=album.id
                )
                db.session.add(new_image)
        db.session.commit()
        flash('Gallery album updated successfully!', 'success')
        return redirect(url_for('gallery.gallery_detail', album_id=album.id))
    
    return render_template('edit_gallery_album.html', album=album, events=events)

# Delete an entire album (and its images)
@gallery.route('/delete/<int:album_id>', methods=['POST'])
@login_required
def delete_gallery(album_id):
    if current_user.id != 1:
        flash('Only admin can delete gallery albums.', 'danger')
        return redirect(url_for('gallery.gallery_view'))
    
    album = GalleryAlbum.query.get_or_404(album_id)
    # Optionally delete image files from the server.
    for image in album.images:
        image_path = os.path.join('website', 'static', 'assets', 'img', image.image_url)
        if os.path.exists(image_path):
            os.remove(image_path)
        db.session.delete(image)
    db.session.delete(album)
    db.session.commit()
    flash('Gallery album deleted successfully!', 'success')
    return redirect(url_for('gallery.gallery_view'))

# Delete a single image from an album
@gallery.route('/delete_image/<int:image_id>', methods=['POST'])
@login_required
def delete_gallery_image(image_id):
    if current_user.id != 1:
        flash('Only admin can delete images.', 'danger')
        return redirect(url_for('gallery.gallery_view'))
    
    image = GalleryImage.query.get_or_404(image_id)
    album_id = image.album_id
    image_path = os.path.join('website', 'static', 'assets', 'img', image.image_url)
    if os.path.exists(image_path):
        os.remove(image_path)
    db.session.delete(image)
    db.session.commit()
    flash('Image deleted successfully!', 'success')
    return redirect(url_for('gallery.edit_gallery', album_id=album_id))
