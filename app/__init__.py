from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
# from flask_migrate import Migrate
import logging
from logging.handlers import RotatingFileHandler
import os

# get the relavent path
base_dir = os.path.abspath(os.path.dirname(__file__))

# set the path of the log file
user_log_file = os.path.join(base_dir, 'static/logs/user_logs.txt')
system_log_file = os.path.join(base_dir, 'static/logs/system_logs.txt')

# initialize the db
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


# create an app instance
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Debugging information
    print(f"Debug mode: {app.debug}")

    # Set log level to INFO or DEBUG
    app.logger.setLevel(logging.INFO)

    # Set up logging to a txt file
    if not app.debug:
        # Create a rotating file handler to write user logs to a .txt file
        user_handler = RotatingFileHandler(
            user_log_file, maxBytes=10240, backupCount=1)
        user_handler.setLevel(logging.INFO)
        user_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        user_handler.setFormatter(user_formatter)
        app.logger.addHandler(user_handler)

        # Create a rotating file handler to write system logs to a .txt file
        system_handler = RotatingFileHandler(
            system_log_file, maxBytes=10240, backupCount=1)
        system_handler.setLevel(logging.INFO)
        system_formatter = logging.Formatter(
            '%(asctime)s - %(message)s')
        system_handler.setFormatter(system_formatter)
        logging.getLogger('werkzeug').addHandler(system_handler)

    else:
        print("Logging is not set up because the app is in debug mode.")
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)  # For debug mode, set to DEBUG
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)

    # Debugging: print current log level
    # Print the current log level
    print(f"Current log level: {logging.getLevelName(app.logger.level)}")

    db.init_app(app)
    # migrate = Migrate(app, db)
    login_manager.init_app(app)

    # register the auth blueprint
    from app.routes import main
    app.register_blueprint(main)

    # create the db
    with app.app_context():
        # db.create_all()
        create_admin_user()

    return app


# create a manager role
def create_admin_user():
    from app.models import User
    # check if the admin account exists
    admin = User.query.filter_by(username='Kim').first()
    if not admin:
        # create an admin account
        admin = User(username='Kim', email='Kim@kim.com', role='manager')
        admin.set_password('Kim721')
        db.session.add(admin)
        db.session.commit()
        print("Admin account created successfully!")
    else:
        print("Admin account already exists.")
