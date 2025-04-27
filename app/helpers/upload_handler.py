import os
import csv
from flask import session, flash, redirect, url_for
from app.models import Entries, Activities
from app import db
from datetime import datetime

def handle_upload(request, app):
    if 'csvFile' in request.files and request.files['csvFile'].filename != '':
        csv_file = request.files['csvFile']
        csv_path = os.path.join(app.instance_path, 'uploads', csv_file.filename)
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        csv_file.save(csv_path)

        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            print(headers)
            if 'id' in headers and 'status' in headers and 'start_date' in headers and 'media_type' in headers and 'media_name' in headers:
                for row in reader:
                    new_activity = Activities(
                        id=int(row['id']),
                        username=session['username'],
                        media_type=row['media_type'],
                        media_name=row['media_name'],
                        status=row['status'],
                        start_date=datetime.strptime(row['start_date'], '%Y-%m-%d').date() if row['start_date'] else None,
                        end_date=datetime.strptime(row['end_date'], '%Y-%m-%d').date() if row['end_date'] else None,
                        rating=float(row['rating']) if row['rating'] else None,
                        comment=row['comment']
                    )
                    db.session.add(new_activity)

            elif 'activity_id' in headers and 'date' in headers and 'duration' in headers:
                # Entries dataset
                for row in reader:
                    new_entry = Entries(
                        activity_id=int(row['activity_id']),
                        date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                        duration=int(row['duration']),
                        comment=row['comment']
                    )
                    db.session.add(new_entry)

            else:
                flash('Invalid CSV format.', 'danger')
                return redirect(url_for('upload'))

        db.session.commit()
        flash('CSV data uploaded successfully!', 'success')
        return redirect(url_for('viewdata'))

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

        new_entry = Entries(username=username, date=date, media_type=media_type, media_name=media_name, duration=duration)
        db.session.add(new_entry)
        db.session.commit()

        flash('Media entry added successfully!', 'success')
        return redirect(url_for('viewdata'))

    return None