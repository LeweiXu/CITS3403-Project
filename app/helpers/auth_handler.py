from flask import session, flash, redirect, url_for
from app.models import Users
from app import db

def handle_login(request):
    username = request.form.get('username')
    password = request.form.get('password')

    # Query the database for the user
    user = Users.query.filter_by(username=username).first()

    if user and user.password == password:  # Replace with hashed password check in production
        session['username'] = username  # Store username in session
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid username or password.', 'danger')
        return None  # Return None to indicate an error

def handle_register(request):
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    # Check if user already exists
    if Users.query.filter_by(username=username).first():
        flash('Username already exists!', 'danger')
        return redirect(url_for('register'))

    # Create new user
    try:
        new_user = Users(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    except Exception as e:
        flash('An error occurred during registration.', 'danger')
        print(f"Error: {e}")  # Debugging output
        return redirect(url_for('register'))