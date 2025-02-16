
from flask import Blueprint, render_template, flash, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from .models import Admin
from . import db

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password = request.form.get('password')
        user = Admin.query.filter_by(user_name=user_name).first()
<<<<<<< HEAD

        if user and check_password_hash(user.password, password):
            flash('Logged in successfully!', category='success')
            login_user(user, remember=False)
=======
        if user and check_password_hash(user.password, password):
            flash('Logged in', category='success')
            login_user(user, remember=True)
>>>>>>> 3719b3d81093853cd794739f61999b6ef6a4da2f
            return redirect(url_for('views.home'))
        else:
            flash("Incorrect username or password", category='error')
    return render_template('login.html')

@auth.route('/log-out')
@login_required
def log_out():
    logout_user()
    flash("You're logged-out successfully.", category='success')
    return redirect(url_for('views.home'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    user = Admin.query.filter_by(id=1).first()
    if user:
        return "Bro, there is already a admin. Please don't try to open this link. Okkay!"

    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash("Passwords aren't matching", category='error')
        elif len(password) < 5:
            flash("Password must be at least 5 characters long", category='error')
        else:
            new_user = Admin(user_name=user_name, password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully!", category='success')
            login_user(new_user, remember=False)
            return redirect(url_for('views.home'))

    return render_template('sign_up.html')
<<<<<<< HEAD


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", category='success')
    return redirect(url_for('web_auth.seller_login'))
=======
>>>>>>> 3719b3d81093853cd794739f61999b6ef6a4da2f
