from flask import render_template, request, redirect, url_for, flash, session, Response
from app import app, db
from app.models import Entries, SharedUsers, Users
from app.helpers.upload_handler import handle_upload
from app.helpers.dashboard_handler import *
from app.helpers.export_csv_handler import generate_csv
from app.helpers.viewdata_handler import handle_viewdata
from app.helpers.activities_handler import fetch_past_activities, handle_end_activity
from app.helpers.analysis_handler import get_analysis_data
from app.helpers.sharedata_handler import share_data_handler

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
    # Fetch all entries for the logged-in user
    all_entries = handle_viewdata(username, request)
    ## 2) pagination parameters
    PER_PAGE    = 20
    page        = request.args.get('page', 1, type=int)
    total       = len(all_entries)
    total_pages = (total + PER_PAGE - 1) // PER_PAGE
    start_idx   = (page - 1) * PER_PAGE
    # 3) slice out just this page
    entries = all_entries[start_idx : start_idx + PER_PAGE]
    # Build a copy of request.args **without** the 'page' key
    args = request.args.to_dict()
    args.pop('page', None)



    return render_template(
        'viewdata.html',
        entries=entries,
        page=page,
        total_pages=total_pages,
        request_args=args
    )

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

@app.route('/sharedata', methods=['GET', 'POST'])
def sharedata():
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

    username = session['username']

    shared_with_me, shared_with = share_data_handler(username, request)

    return render_template('sharedata.html', shared_with_me=shared_with_me, shared_with=shared_with)

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
    username = session['username']
    data     = fetch_past_activities(username, request)
    uncompleted = data["uncompleted_activities"]
    completed   = data["completed_activities"]
    # Combine for simple pagination
    combined    = uncompleted + completed
    PER_PAGE    = 20
    page        = request.args.get('page', 1, type=int)
    total       = len(combined)
    total_pages = (total + PER_PAGE - 1) // PER_PAGE
    start_idx   = (page - 1) * PER_PAGE

    page_slice = combined[start_idx : start_idx + PER_PAGE]
    # split back
    ongoing_page   = [a for a in page_slice if a in uncompleted]
    completed_page = [a for a in page_slice if a in completed]

    # **strip** the 'page' param before passing into template
    args = request.args.to_dict()
    args.pop('page', None)


    return render_template(
        'past_activities.html',
        uncompleted_activities=ongoing_page,
        completed_activities=completed_page,
        page=page,
        total_pages=total_pages,
        request_args=args
    )
@app.route('/analysis', methods=['GET'])
def analysis():
    if 'username' not in session:
        flash('Please log in to view the analysis page.', 'danger')
        return redirect(url_for('login'))

    username = session['username']
    analysis_data = get_analysis_data(username)
    return render_template('analysis.html', analysis_data=analysis_data)

@app.route('/view_shared_data/<data_type>', methods=['GET','POST'])
def view_shared_data(data_type):
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

    username = session['username']
    # 1) grab target_user from form (POST) or args (GET)
    if request.method == 'POST':
        target_user = request.form.get('target_user')
    else:
        target_user = request.args.get('target_user')
    # Check if the target_user has shared their data with the current user
    shared_entry = SharedUsers.query.filter_by(username=target_user, shared_username=username).first()
    if not shared_entry:
        flash('You do not have permission to view this user’s data.', 'danger')
        return redirect(url_for('sharedata'))

    if data_type == 'analysis':
        analysis_data = get_analysis_data(target_user)
        return render_template('analysis.html', analysis_data=analysis_data)
    if data_type == 'activities':
        activities = fetch_past_activities(target_user, request)
        combined = activities["uncompleted_activities"] + activities["completed_activities"]
        template ='past_activities.html'
    
    elif data_type == 'history':
        combined = handle_viewdata(target_user, request)
        template ='viewdata.html'
    else:
        flash('Invalid data type requested.', 'danger')
        return redirect(url_for('sharedata'))
    # 5) pagination logic
    PER_PAGE    = 20
    page        = request.args.get('page', 1, type=int)
    total       = len(combined)
    total_pages = (total + PER_PAGE - 1) // PER_PAGE
    start_idx   = (page - 1) * PER_PAGE
    page_slice  = combined[start_idx : start_idx + PER_PAGE]

    # 6) clean up args for url_for (remove any existing 'page')
    args = request.args.to_dict()
    args.pop('page', None)
    args['target_user'] = target_user

    # 7) render with correct context
    if data_type == 'activities':
        ongoing = [a for a in page_slice if a in activities["uncompleted_activities"]]
        done    = [a for a in page_slice if a in activities["completed_activities"]]
        return render_template(
            template,
            uncompleted_activities=ongoing,
            completed_activities=done,
            page=page,
            total_pages=total_pages,
            request_args=args
        )

    # history case
    return render_template(
        template,
        entries=page_slice,
        page=page,
        total_pages=total_pages,
        request_args=args
    )