import os

#ignore this, eventually will need to use sqlite to allow user data to persist and store authentication info
class sqliteConfig:
    SECRET_KEY = 'UwU'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

