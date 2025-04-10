from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from .models import CoreMembers
from . import db
import os

# Blueprint for adding contacts
add_contact = Blueprint('add_contact', __name__)

# Allowed extensions for picture uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@add_contact.route('/add_contact', methods=['GET', 'POST'])
def add_contact_view():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        # number = request.form.get('number')
        # email = request.form.get('email')
        picture = request.files.get('picture')

        # # Validate input
        # if not name or not number or not email:
        #     flash('All fields are required!', 'danger')
        #     return redirect(url_for('add_contact.add_contact_view'))

        if not name :
            flash('Name required!', 'danger')
            return redirect(url_for('add_contact.add_contact_view'))

        if picture and not allowed_file(picture.filename):
            flash('Invalid file type. Allowed types are png, jpg, jpeg, gif.', 'danger')
            return redirect(url_for('add_contact.add_contact_view'))

        # Save picture if uploaded
        picture_filename = None
        if picture and allowed_file(picture.filename):

            image_filename = secure_filename(picture.filename)
            image_path = os.path.join(current_app.root_path,'static', 'assets', 'img', 'Contact', image_filename)

            picture.save(image_path)
        # Add core member to the database
        new_member = CoreMembers(
            Name=name,
            # Number=number,
            # email_id=email,
            picture=image_filename
        )
        db.session.add(new_member)
        db.session.commit()

        flash('Contact added successfully!', 'success')
        return redirect(url_for('add_contact.new_contact'))

    return render_template('add_contact.html')

@add_contact.route('/contact')
def new_contact():
    # Fetch all members from the database
    members = CoreMembers.query.all()
    return render_template('contact.html', members=members)

@add_contact.route('/edit_contact/<int:contact_id>', methods=['GET', 'POST'])
def edit_contact(contact_id):
    contact = CoreMembers.query.get_or_404(contact_id)
    if request.method == 'POST':
        contact.Name = request.form.get('name')
        # contact.Number = request.form.get('number')
        # contact.email_id = request.form.get('email')

        # Handle picture update
        picture = request.files.get('picture')
        if picture and allowed_file(picture.filename):


            image_filename = secure_filename(picture.filename)
            image_path = os.path.join(current_app.root_path,'static', 'assets', 'img', 'Contact', image_filename)

            picture.save(image_filename)


        db.session.commit()
        flash('Contact updated successfully!', 'success')
        return redirect(url_for('add_contact.new_contact'))

    return render_template('edit_contact.html', contact=contact)


@add_contact.route('/delete_contact/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    contact = CoreMembers.query.get_or_404(contact_id)

    image_path = os.path.join(current_app.root_path, 'assets', 'img', 'Contact', contact.picture)
    if os.path.exists(image_path):
        os.remove(image_path)
    db.session.delete(contact)
    db.session.commit()
    flash('Contact deleted successfully!', 'success')
    return redirect(url_for('add_contact.new_contact'))

