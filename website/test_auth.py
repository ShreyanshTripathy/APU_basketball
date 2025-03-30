from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message  # Import Flask-Mail's Message class
from .models import Admin
from . import db, mail  # Import the mail instance from __init__.py

auth = Blueprint('auth', __name__)

# Function to generate a secure reset token
def generate_reset_token(user):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(user.user_name, salt="password-reset")

def verify_reset_token(token, expiration=600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        user_name = serializer.loads(token, salt="password-reset", max_age=expiration)
    except Exception:
        return None
    return Admin.query.filter_by(user_name=user_name).first()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password = request.form.get('password')

        user = Admin.query.filter_by(user_name=user_name).first()

        if user and check_password_hash(user.password, password):
            flash('Logged in successfully!', category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
        else:
            flash("Incorrect username or password", category='error')

    return render_template('login.html')

@auth.route('/log-out')
@login_required
def log_out():
    logout_user()
    flash("You're logged out successfully.", category='success')
    return redirect(url_for('views.home'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    user = Admin.query.filter_by(id=1).first()
    if user:
        return "Bro, there is already an admin. Please don't try to open this link. Okkay!"

    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash("Passwords aren't matching", category='error')
        elif len(password) < 5:
            flash("Password must be at least 5 characters long", category='error')
        else:
            new_user = Admin(
                user_name=user_name,
                password=generate_password_hash(password, method='pbkdf2:sha256')
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully!", category='success')
            login_user(new_user, remember=False)
            return redirect(url_for('views.home'))

    return render_template('sign_up.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", category='success')
    return redirect(url_for('auth.login'))

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # Get the username (which is the email)
        user_name = request.form.get('user_name').strip()
        current_app.logger.info(f"Received username: '{user_name}'")
        user = Admin.query.filter_by(user_name=user_name).first()

        if not user:
            current_app.logger.error("No user found with that username.")
            flash("User not found", category='error')
            return redirect(url_for('auth.forgot_password'))

        token = generate_reset_token(user)
        reset_url = url_for('auth.reset_password', token=token, _external=True)

        sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'basketballclub@apu.edu.in')
        subject = "Password Reset Request"
        recipients = [user.user_name]  # This will be basketballclub@apu.edu.in if that's stored
        body = f"Hi {user.user_name},\n\nTo reset your password, please click the following link:\n{reset_url}\n\nIf you did not request this, please ignore this email."

        msg = Message(subject=subject, sender=sender, recipients=recipients, body=body)
        mail.send(msg)

        flash("Password reset link sent to your email!", category='success')
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')


@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    token = request.args.get('token')
    user = verify_reset_token(token)

    if not user:
        flash("Invalid or expired token", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == 'POST':
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if new_password != confirm_password:
            flash("Passwords do not match", "error")
        elif len(new_password) < 5:
            flash("Password must be at least 5 characters long", "error")
        else:
            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
            db.session.commit()
            flash("Password reset successful!", "success")
            return redirect(url_for("auth.login"))

    return render_template("reset_password.html", token=token)
