from flask import session, flash, redirect, url_for, jsonify
from flask_login import login_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Users
from app import db
import re

def handle_login(form):
    username = form.username.data
    password = form.password.data
    # Query the database for the user
    user = Users.query.filter_by(username=username).first()

    # Verify the password using check_password_hash
    if user and check_password_hash(user.password, password):
        login_user(user)  # Log the user in with Flask-Login
        return jsonify({
            'success': True,
            'redirect_url': url_for('main.dashboard')
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid username or password.'
        })
    
def handle_register(form):
    username = form.username.data
    email = form.email.data
    password = form.password.data
    # Server-side validation for registration

    # Username validation
    if len(username) < 3 or len(username) > 20:
        return jsonify({'error': 'username', 'message': 'Username must be between 3 and 20 characters.'}), 400
    
    # Email validation
    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        return jsonify({'error': 'email', 'message': 'Invalid email address.'}), 400
    
    # Password validation
    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])[A-Za-z\d!@#$%^&*(),.?":{}|<>]{8,}$', password):
        return jsonify({'error': 'password', 'message': 'Password must contain at least 8 characters, one uppercase letter, one lowercase letter, and one number.'}), 400

    # Check for existing users
    if Users.query.filter_by(username=username).first():
        return jsonify({'error': 'username', 'message': 'Username already exists'}), 400
    if Users.query.filter_by(email=email).first():
        return jsonify({'error': 'email', 'message': 'Email already exists'}), 400

    # Check if user already exists
    if Users.query.filter_by(username=username).first():
        return 'username_exists'
    
    # Check if email already exists
    if Users.query.filter_by(email=email).first():
        return 'email_exists'

    # Hash the password using generate_password_hash
    hashed_password = generate_password_hash(password)

    # Create new user
    try:
        new_user = Users(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return 'success'
    except Exception as e:
        print(f"Error: {e}")  # Debugging output
        return None