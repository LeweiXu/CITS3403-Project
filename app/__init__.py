from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import sqliteConfig

app = Flask(__name__)
app.config['SECRET_KEY'] = "uwu"  # Store this securely in production
app.config.from_object(sqliteConfig)  # Load configuration
db = SQLAlchemy(app)

from app import routes