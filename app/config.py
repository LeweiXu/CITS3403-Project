import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
default_base_dir = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback_secret_key')
    SQLALCHEMY_DATABASE_URI = default_base_dir

class DeploymentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', Config.SQLALCHEMY_DATABASE_URI)
    DEBUG = False

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory'
    TESTING = True
    WTF_CSRF_ENABLED = False