from flask import session, flash, redirect, url_for
from flask_login import login_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Users
from app import db

def handle_login(request):
    username = request.form.get('username')
    password = request.form.get('password')

    # Query the database for the user
    user = Users.query.filter_by(username=username).first()

    # Verify the password using check_password_hash
    if user and check_password_hash(user.password, password):
        login_user(user)  # Log the user in with Flask-Login
        session['username'] = username  # Store username in session
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid username or password.', 'danger')
        return None
    
def handle_register(request):
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

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
        flash('Registration successful! Please log in.', 'success')
        return 'success'
    except Exception as e:
        print(f"Error: {e}")  # Debugging output
        return 'error'