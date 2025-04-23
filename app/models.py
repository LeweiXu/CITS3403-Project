from app import db

class Users(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String(80), primary_key=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    media_entries = db.relationship('Entries', backref='user', lazy=True)

class Entries(db.Model):
    __tablename__ = 'media_entries'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('users.username'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    media_type = db.Column(db.String(50), nullable=False)
    media_name = db.Column(db.String(120), nullable=False)
    duration = db.Column(db.Integer, nullable=False)

class Activities(db.Model):
    __tablename__ = 'current_activities'
    id = db.Column(db.Integer, primary_key=True)
    start_entry_id = db.Column(db.Integer, db.ForeignKey('media_entries.id'), nullable=False)
    end_entry_id = db.Column(db.Integer, db.ForeignKey('media_entries.id'), nullable=True)
    rating = db.Column(db.Float, nullable=True)
    comment = db.Column(db.Text, nullable=True)

    start_entry = db.relationship('Entries', foreign_keys=[start_entry_id], backref='start_activities', lazy=True)
    end_entry = db.relationship('Entries', foreign_keys=[end_entry_id], backref='end_activities', lazy=True)