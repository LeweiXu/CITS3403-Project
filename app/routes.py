import matplotlib.pyplot as plt
import pandas as pd
import os
from io import BytesIO
import base64
from flask import render_template, request, redirect, url_for, flash, session
from app import app
from backend.process_csv import parse_csv, calc_total_time, find_highest_media_type, calc_average_daily_consumption, calc_weekly_durations

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
        # In a real application, you would validate against a database
        if username == "asd" and password == "asd":
            return redirect(url_for('overview'))
        else:
            return render_template('login.html', error="Invalid credentials")

@app.route('/overview')
def overview():
    # Retrieve statistics from the session
    total_time = session.get('total_time', 0)
    most_consumed_media = session.get('most_consumed_media', 'N/A')
    daily_average_time = session.get('daily_average_time', 0)
    weekly_averages = session.get('weekly_averages', {})

    # Generate the graph for the last 10 weeks
    if weekly_averages:
        df = pd.DataFrame(list(weekly_averages.items()), columns=['week_start', 'daily_average'])
        df['week_start'] = pd.to_datetime(df['week_start'])
        df = df.sort_values('week_start', ascending=False).head(10).sort_values('week_start')

        # Plot the graph
        plt.figure(figsize=(10, 6))
        plt.plot(df['week_start'], df['daily_average'], marker='o', linestyle='-', color='b')
        plt.title('Daily Average Media Consumption (Last 10 Weeks)')
        plt.xlabel('Week Starting')
        plt.ylabel('Daily Average (Hours)')
        plt.grid(True)

        # Save the graph to a BytesIO object
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()
        plt.close()
    else:
        graph_url = None

    return render_template(
        'overview.html',
        total_time=total_time,
        most_consumed_media=most_consumed_media,
        daily_average_time=daily_average_time,
        graph_url=graph_url
    )

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Define the absolute path to the uploads directory
        upload_folder = os.path.join(app.root_path, 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        file = request.files['csvFile']
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)

        # Process the uploaded CSV file
        data = parse_csv(file_path)
        total_time = calc_total_time(data)
        most_consumed_media, most_consumed_duration = find_highest_media_type(data)
        daily_average_time = calc_average_daily_consumption(data)
        weekly_averages = calc_weekly_durations(data)

        # Store the statistics in the session
        session['total_time'] = round(total_time / 60, 2)  # Convert to hours
        session['most_consumed_media'] = f"{most_consumed_media} ({round(most_consumed_duration / 60, 2)} hours)"
        session['daily_average_time'] = round(daily_average_time / 60, 2)  # Convert to hours
        session['weekly_averages'] = weekly_averages

        flash('File uploaded and processed successfully!')
        return redirect(url_for('overview'))

    return render_template('upload.html')

@app.route('/register')
def register():
    return render_template('register.html')