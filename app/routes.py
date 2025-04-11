from flask import render_template, request, redirect, url_for
from app import app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    # Placeholder logic for login validation
    username = request.form.get('username')
    password = request.form.get('password')
    if username == "testuser" and password == "password":  # Replace with real authentication
        return redirect(url_for('overview'))
    return render_template('index.html', error="Invalid credentials")

@app.route('/overview')
def overview():
    return render_template('overview.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')