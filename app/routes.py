from flask import render_template, request, redirect, url_for, session
from flask_login import logout_user, login_required, current_user
from app import app
from app.forms import *
from app.helpers.upload_handler import *
from app.helpers.dashboard_handler import *
from app.helpers.viewdata_handler import *
from app.helpers.activities_handler import *
from app.helpers.analysis_handler import *
from app.helpers.sharedata_handler import *
from app.helpers.auth_handler import *

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
    result = get_dashboard_data(current_user.username)
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
    result = get_analysis_page(current_user.username)
    if result: return result

@app.route('/sharedata', methods=['GET'])
@login_required
def sharedata():
    result = share_data_handler(current_user.username, request)
    if result: return result

@app.route('/advanced', methods=['GET'])
@login_required
def advanced():
    return render_template('advanced.html')

# <------------ FORM ROUTES ------------>
# POST routes that are protected from CSRF attacks by Flask-WTF
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
    add_activity_form = AddActivityForm()  # Create an instance of the AddActivityForm
    if not add_activity_form.validate_on_submit():
        print("Form errors:", add_activity_form.errors)
    if add_activity_form.validate_on_submit():  # Check if the form is submitted and valid
        result = handle_add_activity(current_user.username, request)
        if result: return result  # Redirect to dashboard if activity is added successfully

@app.route('/end_activity', methods=['POST'])
@login_required
def end_activity():
    end_activity_form = EndActivityForm()  # Create an instance of the EndActivityForm
    if end_activity_form.validate_on_submit():  # Check if the form is submitted and valid
        result = handle_end_activity(current_user.username, request)
        if result: return result

@app.route('/add_entry', methods=['POST'])
@login_required
def add_entry():
    add_entry_form = AddEntryForm()  # Create an instance of the AddEntryForm
    if add_entry_form.validate_on_submit():  # Check if the form is submitted and valid
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
    if result: return result

@app.route('/delete_entry', methods=['POST'])
@login_required
def delete_entry():
    result = handle_delete_entry(request)
    if result: return result 

@app.route('/view_shared_data', methods=['POST'])
@login_required
def view_shared_data():
    result = view_shared_data_handler(current_user.username, request)
    if result: return result

@app.route('/delete_shared_user', methods=['POST'])
@login_required
def delete_shared_user():
    result = delete_shared_user_handler(current_user.username, request)
    if result: return result

@app.route('/share_with_user', methods=['POST'])
@login_required
def share_with_user():
    result = share_with_user_handler(current_user.username, request)
    if result: return result

# <------------ BUTTON ROUTES ------------>
# Routes that don't really need to be protected by CSRF, but are still protected by Flask-Login
@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('index'))  # Redirect to the home page

@app.route('/search_users', methods=['GET'])
@login_required
def search_users_route():
    result = search_users(request)
    if result: return result

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    result = handle_upload(request, app)
    if result: return result