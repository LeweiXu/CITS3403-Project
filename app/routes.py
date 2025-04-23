from flask import render_template, request, redirect, url_for, flash, session, Response
from app import app
from app.models import Users
from app import db
from app.helpers.upload_handler import handle_upload
from app.helpers.dashboard_handler import *
from app.models import Entries
from app.helpers.export_csv_handler import generate_csv
from app.helpers.viewdata_handler import get_filtered_entries

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
        user = Users.query.filter_by(username=username).first()

        if user and user.password == password:  # Replace with hashed password check in production
            session['username'] = username  # Store username in session
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
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

    return render_template('register.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        flash('Please log in to view your dashboard.', 'danger')
        return redirect(url_for('login'))

    username = session['username']

    # Handle form submissions
    if request.method == 'POST':
        if 'add_duration' in request.form:  # Add duration to an existing media
            media_name = request.form.get('media_name')
            media_type = request.form.get('media_type')
            duration = request.form.get('duration')
            if media_name and duration:
                handle_add_duration(username, media_name, media_type, duration)
                flash(f'Duration added to {media_name}.', 'success')
        elif 'add_new_entry' in request.form:  # Add a new media entry
            media_type = request.form.get('media_type')
            media_name = request.form.get('media_name')
            duration = request.form.get('duration')
            if media_type and media_name and duration:
                handle_add_new_entry(username, media_type, media_name, duration)
                flash(f'New media entry "{media_name}" added.', 'success')
        elif 'end_activity' in request.form:  # End an activity
            activity_id = request.form.get('activity_id')
            rating = request.form.get('rating')  # Get the rating from the form
            comment = request.form.get('comment')  # Get the comment from the form
            if activity_id:
                success = handle_end_activity(activity_id, username, rating=rating, comment=comment)
                if success:
                    flash('Activity ended successfully.', 'success')
                else:
                    flash('Failed to end activity.', 'danger')

        return redirect(url_for('dashboard'))

    # Fetch statistics and current activities
    stats = get_user_statistics(username)
    current_activities = get_current_activities(username)

    return render_template(
        'dashboard.html',
        total_time=stats['total_time'],
        most_consumed_media=stats['most_consumed_media'],
        daily_average_time=stats['daily_average_time'],
        current_activities=current_activities
    )

@app.route('/end_activity', methods=['POST'])
def end_activity():
    if 'username' not in session:
        flash('Please log in to perform this action.', 'danger')
        return redirect(url_for('login'))

    username = session['username']
    activity_id = request.form.get('activity_id')
    rating = request.form.get('rating')  # Get the rating from the form
    comment = request.form.get('comment')  # Get the comment from the form

    if activity_id:
        success = handle_end_activity(activity_id, username, rating=rating, comment=comment)
        if success:
            flash('Activity ended successfully.', 'success')
        else:
            flash('Failed to end activity.', 'danger')

    return redirect(url_for('dashboard'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        result = handle_upload(request, app)
        if result:  # If the function returns a redirect or flash message
            return result
    return render_template('upload.html')

@app.route('/viewdata', methods=['GET'])
def viewdata():
    if 'username' not in session:
        flash('Please log in to view your data.', 'danger')
        return redirect(url_for('login'))

    username = session['username']

    # Pass query parameters to the helper function
    filters = {
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
        'media_name': request.args.get('media_name'),
        'media_type': request.args.get('media_type'),
        'min_duration': request.args.get('min_duration'),
        'max_duration': request.args.get('max_duration')
    }

    # Get filtered entries
    entries = get_filtered_entries(username, filters)

    return render_template('viewdata.html', entries=entries)

@app.route('/delete_entry/<int:entry_id>')
def delete_entry(entry_id):
    entry = Entries.query.get(entry_id)
    if entry and entry.username == session.get('username'):
        db.session.delete(entry)
        db.session.commit()
        flash('Entry deleted successfully.', 'success')
    else:
        flash('Entry not found or unauthorized.', 'danger')
    return redirect(url_for('viewdata'))

@app.route('/sharedata')
def sharedata():
    return render_template('sharedata.html')

@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))  # Redirect to the login page

@app.route('/export_csv', methods=['GET'])
def export_csv():
    if 'username' not in session:
        flash('Please log in to export your data.', 'danger')
        return redirect(url_for('login'))
    
    entries = Entries.query.filter_by(username=session['username']).all()
    return Response(
        generate_csv(entries),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=media_entries.csv'}
    )