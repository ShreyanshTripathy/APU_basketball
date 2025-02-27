from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
import os
from . import db
from .models import HomePageContent

admin_homepage = Blueprint('admin_homepage', __name__)

UPLOAD_FOLDER = os.path.join('static', 'assets', 'img')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_homepage.route('/edit_homepage', methods=['GET', 'POST'])
def edit_homepage():
    home_content = HomePageContent.query.first()
    if not home_content:
        home_content = HomePageContent()
        db.session.add(home_content)
        db.session.commit()
    
    if request.method == 'POST':
        home_content.header_title = request.form.get('header_title')
        home_content.header_subtitle = request.form.get('header_subtitle')
        home_content.main_paragraph_1 = request.form.get('main_paragraph_1')
        home_content.main_paragraph_2 = request.form.get('main_paragraph_2')
        home_content.main_paragraph_3 = request.form.get('main_paragraph_3')
        
        if 'header_image' in request.files:
            file = request.files['header_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
                file.save(file_path)
                home_content.header_image = filename
        
        db.session.commit()
        flash("Homepage content updated successfully!", "success")
        return redirect(url_for('views.home'))
    
    return render_template('edit_homepage.html', home_content=home_content)
