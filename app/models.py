from app import db

# Users table, pretty self explanatory, username as PK makes it unique by default
class Users(db.Model):
    __tablename__ = 'Users'
    username = db.Column(db.String(80), primary_key=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    media_entries = db.relationship('Activities', backref='user', lazy=True)

# Media entries table, stores all media entries
# Each entry is associated an Activity (Activities.id)
# The idea is that each activity is made up of multiple media entries
class Entries(db.Model):
    __tablename__ = 'Entries'
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('Activities.id'), nullable=True)
    date = db.Column(db.Date, nullable=False)
    media_type = db.Column(db.String(50), nullable=False)
    media_name = db.Column(db.String(120), nullable=False)
    duration = db.Column(db.Integer, nullable=False)

# Activities table, each Activity is associated with a user (Users.username)
# Each activity has a start and end entry, rating and comment
# The idea is that a user can start an activity, add multiple media entries to it, then finally end an activity (by setting the end entry_id)
class Activities(db.Model):
    __tablename__ = 'Activities'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('Users.username'), nullable=False)
    start_entry_id = db.Column(db.Integer, nullable=False)
    end_entry_id = db.Column(db.Integer, nullable=True)
    rating = db.Column(db.Float, nullable=True)
    comment = db.Column(db.Text, nullable=True)

    media_entries = db.relationship('Entries', backref='activity', lazy=True)