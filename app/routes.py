from flask import render_template, request, redirect, url_for, flash, session, Response
from app import app, db
from app.models import Entries
from app.helpers.upload_handler import handle_upload
from app.helpers.dashboard_handler import *
from app.helpers.export_csv_handler import generate_csv
from app.helpers.viewdata_handler import handle_viewdata
from app.helpers.activities_handler import fetch_past_activities, handle_end_activity

@app.route('/')
def index():
    return render_template('index.html')

from app.helpers.auth_handler import handle_login, handle_register

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        result = handle_login(request)
        if result:
            return result  # Redirect to dashboard if login is successful
        return render_template('login.html', error="Invalid credentials")  # Render login page with error
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        result = handle_register(request)
        return result  # Redirect to login or register page based on the result
    return render_template('register.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        flash('Please log in to view your dashboard.', 'danger')
        return redirect(url_for('login'))

    username = session['username']

    # Handle form submissions
    if request.method == 'POST':
        handle_dashboard_form(username, request.form)
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

    # Convert empty strings to None
    rating = float(rating) if rating else None
    comment = comment if comment else None

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

    # Delegate the logic to the handler
    entries = handle_viewdata(username, request)

    return render_template('viewdata.html', entries=entries)

@app.route('/delete_entry/<int:entry_id>')
def delete_entry(entry_id):
    entry = Entries.query.get(entry_id)
    if entry:
        # Check if the entry belongs to the logged-in user
        activity = Activities.query.filter_by(id=entry.activity_id, username=session.get('username')).first()
        if activity:
            db.session.delete(entry)
            db.session.commit()
            flash('Entry deleted successfully.', 'success')
        else:
            flash('Entry not found or unauthorized.', 'danger')
    else:
        flash('Entry not found.', 'danger')
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

@app.route('/past_activities', methods=['GET'])
def past_activities():
    if 'username' not in session:
        flash('Please log in to view your activities.', 'danger')
        return redirect(url_for('login'))
    
    # Delegate the logic to the handler
    activities = fetch_past_activities(session['username'], request)

    return render_template(
        'past_activities.html',
        uncompleted_activities=activities["uncompleted_activities"],
        completed_activities=activities["completed_activities"]
    )