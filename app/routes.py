from flask import render_template, request, redirect, url_for, flash, session
from app import app
from app.models import User
from app import db
from app.helpers.upload_handler import handle_upload
from app.helpers.dashboard_handler import get_user_statistics
from app.models import MediaEntry

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

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please log in to view your dashboard.', 'danger')
        return redirect(url_for('login'))

    username = session['username']
    stats = get_user_statistics(username)

    return render_template(
        'dashboard.html',
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

@app.route('/viewdata')
def viewdata():
    if 'username' not in session:
        flash('Please log in to view your data.', 'danger')
        return redirect(url_for('login'))

    username = session['username']
    entries = MediaEntry.query.filter_by(username=username).order_by(MediaEntry.date.desc()).all()

    return render_template('viewdata.html', entries=entries)

@app.route('/delete_entry/<int:entry_id>')
def delete_entry(entry_id):
    entry = MediaEntry.query.get(entry_id)
    if entry and entry.username == session.get('username'):
        db.session.delete(entry)
        db.session.commit()
        flash('Entry deleted successfully.', 'success')
    else:
        flash('Entry not found or unauthorized.', 'danger')
    return redirect(url_for('viewdata'))

# @app.route('/edit_entry/<int:entry_id>', methods=['GET', 'POST'])
# def edit_entry(entry_id):
#     entry = MediaEntry.query.get(entry_id)
#     if not entry or entry.username != session.get('username'):
#         flash('Entry not found or unauthorized.', 'danger')
#         return redirect(url_for('viewdata'))

#     if request.method == 'POST':
#         entry.date = request.form.get('date')
#         entry.media_type = request.form.get('media_type')
#         entry.media_name = request.form.get('media_name')
#         entry.duration = request.form.get('duration')
#         db.session.commit()
#         flash('Entry updated successfully.', 'success')
#         return redirect(url_for('viewdata'))

#     return render_template('edit_entry.html', entry=entry)

@app.route('/sharedata')
def sharedata():
    return render_template('sharedata.html')

@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))  # Redirect to the login page