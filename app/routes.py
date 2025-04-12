from flask import render_template, request, redirect, url_for, flash
from app import app
import os
from backend.process_csv import parse_csv

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    # In a real application, you would validate against a database
    if username == "asd" and password == "asd":
        return redirect(url_for('overview'))
    return render_template('index.html', error="Invalid credentials")

@app.route('/overview')
def overview():
    return render_template('overview.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Define the absolute path to the uploads directory
        upload_folder = os.path.join(app.root_path, 'uploads')
        
        file = request.files['csvFile']
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)
        data = parse_csv(file_path)
        
        flash('File uploaded and processed successfully!')
        return redirect(url_for('upload'))
    
    return render_template('upload.html')