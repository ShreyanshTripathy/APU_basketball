from flask import Flask, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
import os

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
    app.debug = True
    # Use environment variable if available, else default secret key
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    db.init_app(app)

    # Import and register blueprints
    from .views import views
    from .auth import auth
    from .add_event import add_event
    from .add_contact import add_contact
    from .team import Teams
    from .gallery import gallery  

    app.register_blueprint(views)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(add_event, url_prefix='/add')
    app.register_blueprint(add_contact, url_prefix='/contact')
    app.register_blueprint(Teams, url_prefix='/teams')
    app.register_blueprint(gallery, url_prefix='/gallery')  

    # Create database tables (if they don't exist already)
    with app.app_context():
        db.create_all()

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Updated login endpoint
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
    """
    Callback function to reload the user object from the user ID stored in the session.
    """
    from .models import Admin  
    return Admin.query.get(int(user_id))
