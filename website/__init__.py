from flask import Flask, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
import os
from datetime import timedelta

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

# Database name
DB_NAME = 'basketball_db.sqlite3'

def create_app():
    """
    Application factory to create and configure the Flask app instance.
    """
    app = Flask(__name__)
<<<<<<< HEAD
=======
    app.debug = True
    app.config['SECRET_KEY'] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"
>>>>>>> 3719b3d81093853cd794739f61999b6ef6a4da2f

    # Basic configuration
    app.debug = True
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
<<<<<<< HEAD
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=100)  # Sessions expire after 30 minutes

    # Ensure the database directory exists
    if not os.path.exists('instance'):
        os.makedirs('instance')

    # Initialize extensions
=======
>>>>>>> 3719b3d81093853cd794739f61999b6ef6a4da2f
    db.init_app(app)

    # Import and register blueprints
    from .views import views
    from .auth import auth
<<<<<<< HEAD
    from .add_event import add_event
    from .add_contact import add_contact
    from.team import Teams
=======

    from .models import Admin
    from .models import Event
    from .models import Team
    from .models import Match

    # without this login won't be possible
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please log-in if you're admin"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Admin.query.get(int(id))
>>>>>>> 3719b3d81093853cd794739f61999b6ef6a4da2f

    app.register_blueprint(views)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(add_event, url_prefix='/add')
    app.register_blueprint(add_contact, url_prefix='/contact')
    app.register_blueprint(Teams, url_prefix='/teams')

    # Create database tables (if they don't exist already)
    with app.app_context():
        db.create_all()

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'web_auth.login'
    login_manager.login_message = "Please log in to access this page."

    # Handle session clearing (alternative to `before_first_request`)
    first_request_flag = {"handled": False}

    @app.before_request
    def clear_session_on_startup():
        if not first_request_flag["handled"]:
            session.clear()
            first_request_flag["handled"] = True
            app.logger.info("Session cleared on app startup.")

    # Debugging: Check user status before each request
    @app.before_request
    def check_user_status():
        if current_user.is_authenticated:
            app.logger.info(f"Logged in as {current_user.user_name} (ID: {current_user.id})")
        else:
            app.logger.info("No user is logged in.")

    return app

@login_manager.user_loader
def load_user(user_id):
    """
    Callback function to reload the user object from the user ID stored in the session.
    """
    from .models import Admin  # Import Admin model here to avoid circular imports
    return Admin.query.get(int(user_id))
