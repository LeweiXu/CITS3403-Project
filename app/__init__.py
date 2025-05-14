from flask import Flask, app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from app.config import DeploymentConfig

db = SQLAlchemy()
migrate = Migrate(db)
login = LoginManager()
login.login_view = 'main.index'

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    from app.blueprints import blueprint
    app.register_blueprint(blueprint)

    db.init_app(app)
    login.init_app(app)

    return app

app = create_app(DeploymentConfig)
migrate = Migrate(app, db)

# from app import routes

# app = Flask(__name__)
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback_secret_key')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.debug = True  # Set to False in production
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)
# login = LoginManager(app)
# login.login_view = 'index'  # Redirect to login page if not logged in

# from app import routes