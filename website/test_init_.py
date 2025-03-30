from flask import Flask, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_mail import Mail  # Import Flask-Mail
import os

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()  # Create an instance of Mail

DB_NAME = 'basketball_db.sqlite3'

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    # Configure Flask-Mail settings
    app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USERNAME='basketballclub@apu.edu.in',       # Sender email
        MAIL_PASSWORD='Apu@2020',                         # Sender email password
        MAIL_DEFAULT_SENDER='basketballclub@apu.edu.in'   # Default sender address
    )


    db.init_app(app)
    mail.init_app(app)  # Initialize mail with the app

    # Import and register blueprints
    from .views import views
    from .auth import auth
    from .add_event import add_event
    from .add_contact import add_contact
    from .team import Teams
    from .gallery import gallery
    from .admin_homepage import admin_homepage

    app.register_blueprint(views)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(add_event, url_prefix='/add')
    app.register_blueprint(add_contact, url_prefix='/contact')
    app.register_blueprint(Teams, url_prefix='/teams')
    app.register_blueprint(gallery, url_prefix='/gallery')
    app.register_blueprint(admin_homepage, url_prefix='/admin')

    # Create database tables (if they don't exist already)
    with app.app_context():
        db.create_all()

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please log in to access this page."

    # Clear session on the very first request only
    first_request_flag = {"handled": False}
    @app.before_request
    def clear_session_on_startup():
        if not first_request_flag["handled"]:
            session.clear()
            first_request_flag["handled"] = True
            app.logger.info("Session cleared on app startup.")

    @app.before_request
    def check_user_status():
        if current_user.is_authenticated:
            app.logger.info(f"Logged in as {current_user.user_name} (ID: {current_user.id})")
        else:
            app.logger.info("No user is logged in.")

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import Admin
    return Admin.query.get(int(user_id))
