import os
import csv
from flask import session, flash, redirect, url_for
from app.models import MediaEntry
from app import db
from datetime import datetime  # Import datetime for date conversion

def handle_upload(request, app):
    if 'csvFile' in request.files and request.files['csvFile'].filename != '':
        # Handle CSV file upload
        csv_file = request.files['csvFile']
        upload_folder = os.path.join(app.root_path, 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        file_path = os.path.join(upload_folder, csv_file.filename)
        csv_file.save(file_path)

        # Parse CSV file and add entries to the database
        with open(file_path, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                username = session.get('username')
                if not username:
                    flash('Please log in to upload media entries.', 'danger')
                    return redirect(url_for('login'))

                # Convert date string to Python date object
                try:
                    date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                except ValueError:
                    flash(f"Invalid date format in row: {row}", 'danger')
                    return redirect(url_for('upload'))

                # Create a new MediaEntry object
                new_entry = MediaEntry(
                    username=username,
                    date=date,  # Use the converted date object
                    media_type=row['media_type'],
                    media_name=row['media_name'],
                    duration=row['duration']
                )
                db.session.add(new_entry)
            db.session.commit()

        flash('CSV file uploaded and processed successfully!', 'success')
        return redirect(url_for('overview'))

    elif 'mediaType' in request.form:
        # Handle individual media entry submission
        if 'username' not in session:
            flash('Please log in to add media entries.', 'danger')
            return redirect(url_for('login'))

        username = session['username']
        date_str = request.form.get('date')
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return redirect(url_for('upload'))

        media_type = request.form.get('mediaType')
        media_name = request.form.get('mediaName')
        duration = request.form.get('duration')

        new_entry = MediaEntry(username=username, date=date, media_type=media_type, media_name=media_name, duration=duration)
        db.session.add(new_entry)
        db.session.commit()

        flash('Media entry added successfully!', 'success')
        return redirect(url_for('overview'))

    return None