from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = "uwu"  # Store this securely in production

from app import routes