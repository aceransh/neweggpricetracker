from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize Flask app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '../price_tracker.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set the secret key for session management
app.config['SECRET_KEY'] = os.urandom(24)  # Generate a random secret key

if os.getenv('FLASK_ENV') == 'development':
    app.config['DEBUG'] = True

# Initialize the database
db = SQLAlchemy(app)

from app import routes