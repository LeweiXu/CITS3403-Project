from app import db

class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String(80), primary_key=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    media_entries = db.relationship('MediaEntry', backref='user', lazy=True)

class MediaEntry(db.Model):
    __tablename__ = 'media_entries'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('users.username'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    media_type = db.Column(db.String(50), nullable=False)
    media_name = db.Column(db.String(120), nullable=False)
    duration = db.Column(db.String(50), nullable=False)

class CurrentActivities(db.Model):
    __tablename__ = 'current_activities'
    id = db.Column(db.Integer, primary_key=True)
    start_entry_id = db.Column(db.Integer, db.ForeignKey('media_entries.id'), nullable=False)
    end_entry_id = db.Column(db.Integer, db.ForeignKey('media_entries.id'), nullable=True)