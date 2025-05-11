from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import logout_user, login_required, current_user
from app import app, db
from app.forms import LoginForm, RegisterForm, AddActivityForm
from app.models import Entries, SharedUsers, Activities
from app.helpers.upload_handler import handle_upload
from app.helpers.dashboard_handler import *
from app.helpers.viewdata_handler import get_entries, handle_delete_entry
from app.helpers.activities_handler import *
from app.helpers.analysis_handler import get_analysis_data
from app.helpers.sharedata_handler import share_data_handler, search_users
from app.helpers.auth_handler import handle_login, handle_register

#<------------ PAGE ROUTES ------------>
# All routes get render_template() from a helper function and returns the result
@app.route('/')
@app.route('/index', methods=['GET'])
def index():
    # Index page also contains login/register information
    login_form = LoginForm()  # Create an instance of the LoginForm
    register_form = RegisterForm()
    return render_template('index.html', login_form=login_form, register_form=register_form)  # Pass the form to the template

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    add_activity_form = AddActivityForm()  # Create an instance of the AddActivityForm
    result = get_dashboard_data(current_user.username, add_activity_form)
    if result: return result  # Render the dashboard with the data

@app.route('/viewdata', methods=['GET'])
@login_required
def viewdata():
    result = get_entries(current_user.username, request)
    if result: return result

@app.route('/activities', methods=['GET'])
@login_required
def activities():
    result = get_activities(current_user.username, request)
    if result: return result

@app.route('/analysis', methods=['GET'])
@login_required
def analysis():
    analysis_data = get_analysis_data(current_user.username)
    return render_template('analysis.html', analysis_data=analysis_data)

@app.route('/sharedata', methods=['GET'])
@login_required
def sharedata():
    result = share_data_handler(current_user.username, request)
    if result: return result

@app.route('/advanced', methods=['GET'])
@login_required
def advanced():
    return render_template('advanced.html')

# <------------ BUTTON ROUTES ------------>
# Routes for GET button requests that don't require CSRF protection
@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    session['username'] = None  # Clear the session
    return redirect(url_for('index'))  # Redirect to the home page

# <------------ FORM ROUTES ------------>
# All routes that are not GET requests, uses WTForms for CSRF protection
@app.route('/login', methods=['POST'])
def login():
    form = LoginForm()  # Create a new instance of the LoginForm
    if form.validate_on_submit():  # Check if the form is submitted and valid
        result = handle_login(request)
        if result: return result  # Redirect to dashboard if login is successful

@app.route('/register', methods=['POST'])
def register():
    register_form = RegisterForm()  # Create a new instance of the RegisterForm
    if register_form.validate_on_submit():  # Check if the form is submitted and valid
        result = handle_register(request)
        if result: return result

@app.route('/add_activity', methods=['POST'])
@login_required
def add_activity():
    result = handle_add_activity(current_user.username, request)
    if result: return result  # Redirect to dashboard if activity is added successfully

@app.route('/end_activity', methods=['POST'])
@login_required
def end_activity():
    result = handle_end_activity(current_user.username, request)
    if result: return result

@app.route('/add_entry', methods=['POST'])
@login_required
def add_entry():
    result = handle_add_entry(current_user.username, request)
    if result: return result  # Redirect to viewdata if entry is added successfully

@app.route('/reopen_activity', methods=['POST'])
@login_required
def reopen_activity():
    result = handle_reopen_activity(request)
    if result: return result  # Redirect to viewdata if activity is reopened successfully

@app.route('/delete_activity', methods=['POST'])
@login_required
def delete_activity():
    result = handle_delete_activity(request)
    if result: return result  # Redirect to viewdata if activity is deleted successfully

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if request.method == 'POST':
        result = handle_upload(request, app)
        if result:  # If the function returns a redirect or flash message
            return result
    return render_template('upload.html')

@app.route('/delete_entry/<int:entry_id>')
@login_required
def delete_entry(entry_id):
    result = handle_delete_entry(entry_id, current_user.username)
    if result: return result  # Redirect to viewdata if deletion is successful

# Pass the username internally to defend against users editing the URL to see other users' data
@app.route('/view_shared_data/<data_type>', methods=['GET','POST'])
@login_required
def view_shared_data(data_type):
    # 1) grab target_user from form (POST) or args (GET)
    if request.method == 'POST':
        target_user = request.form.get('target_user')
    else:
        target_user = request.args.get('target_user')
    # Check if the target_user has shared their data with the current user
    shared_entry = SharedUsers.query.filter_by(username=target_user, shared_username=session['username']).first()
    if not shared_entry:
        flash('You do not have permission to view this user’s data.', 'danger')
        return redirect(url_for('sharedata'))

    if data_type == 'analysis':
        analysis_data = get_analysis_data(target_user)
        return render_template('analysis.html', analysis_data=analysis_data, visitor=True)
    if data_type == 'activities':
        activities = fetch_past_activities(target_user, request)
        combined = activities["uncompleted_activities"] + activities["completed_activities"]
        template ='activities.html'
    
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
            request_args=args,
            visitor=True
        )

    # history case
    return render_template(
        template,
        entries=page_slice,
        page=page,
        total_pages=total_pages,
        request_args=args,
        visitor=True
    )

@app.route('/search_users', methods=['GET'])
@login_required
def search_users_route():
    query = request.args.get('query', '')
    if query:
        matching_users = search_users(query)
        return jsonify(matching_users)
    return jsonify([])