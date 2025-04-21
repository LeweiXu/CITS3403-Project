from flask import render_template, request, redirect, url_for, flash, session
from app import app
from utils.upload_handler import *
from app.models import User
from app import db
from utils.upload_handler import handle_upload
from utils.overview_handler import get_user_statistics

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Query the database for the user
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:  # Replace with hashed password check in production
            session['username'] = username  # Store username in session
            flash('Login successful!', 'success')
            return redirect(url_for('overview'))
        else:
            flash('Invalid username or password.', 'danger')
            return render_template('login.html', error="Invalid credentials")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))

        # Create new user
        try:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('An error occurred during registration.', 'danger')
            print(f"Error: {e}")  # Debugging output
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/overview')
def overview():
    if 'username' not in session:
        flash('Please log in to view your overview.', 'danger')
        return redirect(url_for('login'))

    username = session['username']
    stats = get_user_statistics(username)

    return render_template(
        'overview.html',
        total_time=stats['total_time'],
        most_consumed_media=stats['most_consumed_media'],
        daily_average_time=stats['daily_average_time']
    )

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        result = handle_upload(request, app)
        if result:  # If the function returns a redirect or flash message
            return result
    return render_template('upload.html')

@app.route('/sharedata')
def sharedata():
    return render_template('sharedata.html')

@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))  # Redirect to the login page