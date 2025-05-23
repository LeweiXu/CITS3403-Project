from flask import render_template, request, redirect, url_for, session, current_app
from flask_login import logout_user, login_required, current_user
#from app import app
from app.forms import *
from app.helpers.advanced_functions import *
from app.helpers.dashboard_functions import *
from app.helpers.entries_functions import *
from app.helpers.activities_functions import *
from app.helpers.analysis_functions import *
from app.helpers.sharedata_functions import *
from app.helpers.auth_functions import *
from app.blueprints import blueprint 

#<------------ PAGE ROUTES ------------>
# All routes get render_template() from a helper function and returns the result
@blueprint.route('/')
@blueprint.route('/index', methods=['GET'])
def index():
    # Index page also contains login/register information
    login_form = LoginForm()  # Create an instance of the LoginForm
    register_form = RegisterForm()
    return render_template('index.html', login_form=login_form, register_form=register_form)  # Pass the form to the template

@blueprint.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    result = get_dashboard_data(current_user.username)
    if result: return result
    
@blueprint.route('/viewdata', methods=['GET'])
@login_required
def viewdata():
    result = get_entries(current_user.username, request)
    if result: return result

@blueprint.route('/activities', methods=['GET'])
@login_required
def activities():
    result = get_activities(current_user.username, request)
    if result:
        return result
    
@blueprint.route('/analysis', methods=['GET'])
@login_required
def analysis():
    result = get_analysis_page(current_user.username)
    if result: return result

@blueprint.route('/sharedata', methods=['GET'])
@login_required
def sharedata():
    result = share_data_handler(current_user.username)
    if result: return result

@blueprint.route('/advanced', methods=['GET'])
@login_required
def advanced():
    return render_template('advanced.html')

# <------------ FORM ROUTES ------------>
# POST routes that are protected from CSRF attacks by Flask-WTF
@blueprint.route('/login', methods=['POST'])
def login():
    login_form = LoginForm()  # Create a new instance of the LoginForm
    if login_form.validate_on_submit():  # Check if the form is submitted and valid
        result = handle_login(login_form)
        if result: return result  # Redirect to dashboard if login is successful
        return redirect(url_for('main.index'))   # Redirect to index if unsuccessful
    return redirect(url_for('main.index'))

@blueprint.route('/register', methods=['POST'])
def register():
    register_form = RegisterForm()  # Create a new instance of the RegisterForm
    if register_form.validate_on_submit():  # Check if the form is submitted and valid
        result = handle_register(register_form)
        if result: return result

@blueprint.route('/add_activity', methods=['POST'])
@login_required
def add_activity():
    add_activity_form = AddActivityForm()  # Create an instance of the AddActivityForm
    if add_activity_form.validate_on_submit():  # Check if the form is submitted and valid
        result = handle_add_activity(current_user.username, add_activity_form)
        if result: return result  # Redirect to dashboard if activity is added successfully
    return redirect(url_for('main.dashboard')) # Fallback redirect

@blueprint.route('/end_activity', methods=['POST'])
@login_required
def end_activity():
    end_activity_form = EndActivityForm()  # Create an instance of the EndActivityForm
    if end_activity_form.validate_on_submit():  # Check if the form is submitted and valid
        result = handle_end_activity(current_user.username, end_activity_form)
        if result: return result
    return redirect(url_for('main.dashboard')) # Fallback redirect

@blueprint.route('/add_entry', methods=['POST'])
@login_required
def add_entry():
    add_entry_form = AddEntryForm()  # Create an instance of the AddEntryForm
    if add_entry_form.validate_on_submit():  # Check if the form is submitted and valid
        result = handle_add_entry(current_user.username, add_entry_form)
        if result: return result  # Redirect to viewdata if entry is added successfully
    return redirect(url_for('main.dashboard')) # Fallback redirect

@blueprint.route('/reopen_activity', methods=['POST'])
@login_required
def reopen_activity():
    reopen_activity_form = ReopenActivityForm()
    if reopen_activity_form.validate_on_submit():
        result = handle_reopen_activity(reopen_activity_form)
        if result: return result  # Redirect to viewdata if activity is reopened successfully
    return redirect(url_for('main.dashboard'))  # Add fallback redirect

@blueprint.route('/delete_activity', methods=['POST'])
@login_required
def delete_activity():
    delete_activity_form = DeleteActivityForm()
    if delete_activity_form.validate_on_submit():
        result = handle_delete_activity(delete_activity_form)
        if result: return result
    return redirect(url_for('main.dashboard'))  # Add fallback redirect
    
@blueprint.route('/delete_entry', methods=['POST'])
@login_required
def delete_entry():
    delete_entry_form = DeleteEntryForm()
    if delete_entry_form.validate_on_submit():
        result = handle_delete_entry(delete_entry_form)
        if result: return result 
    return redirect(url_for('main.dashboard'))  # Add fallback redirect

@blueprint.route('/view_shared_data', methods=['POST'])
@login_required
def view_shared_data():
    view_shared_data_form = ViewSharedDataForm()
    if view_shared_data_form.validate_on_submit():
        result = view_shared_data_handler(current_user.username, request, view_shared_data_form)
        if result: return result
    return redirect(url_for('main.dashboard'))  # Add fallback redirect

@blueprint.route('/delete_shared_user', methods=['POST'])
@login_required
def delete_shared_user():
    delete_shared_user_form = DeleteSharedUserForm()
    if delete_shared_user_form.validate_on_submit():
        result = delete_shared_user_handler(current_user.username, delete_shared_user_form)
        if result: return result
    return redirect(url_for('main.dashboard'))  # Add fallback redirect

@blueprint.route('/share_with_user', methods=['POST'])
@login_required
def share_with_user():
    share_with_user_form = ShareWithUserForm()
    if share_with_user_form.validate_on_submit():
        result = share_with_user_handler(current_user.username, share_with_user_form)
        if result: return result
    return redirect(url_for('main.dashboard'))  # Add fallback redirect

# <------------ BUTTON ROUTES ------------>
# Routes that don't really need to be protected by CSRF, but are still protected by Flask-Login
@blueprint.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('main.index'))  # Redirect to the home page

@blueprint.route('/search_users', methods=['GET'])
@login_required
def search_users_route():
    result = search_users(request)
    if result: return result
    return redirect(url_for('main.dashboard'))  # Add fallback redirect

@blueprint.route('/upload', methods=['POST'])
@login_required
def upload():
    result = handle_upload(request, current_app)
    if result: return result
    return redirect(url_for('main.dashboard'))  # Add fallback redirect