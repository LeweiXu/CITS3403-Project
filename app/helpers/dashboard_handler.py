from app.models import Entries, Activities
from app import db
from sqlalchemy import func
from datetime import datetime
from flask import flash
from app.helpers.activities_handler import handle_add_new_activity

def get_user_statistics(username):
    # Query all media entries for the current user
    media_entries = db.session.query(Entries).join(Activities).filter(Activities.username == username).all()

    if not media_entries:
        return {
            "total_time": 0,
            "most_consumed_media": None,
            "daily_average_time": 0
        }

    # Calculate total time spent (in hours)
    total_duration = sum(int(entry.duration) for entry in media_entries)
    total_time = total_duration / 60  # Convert minutes to hours

    # Find the most consumed media type
    media_type_counts = {}
    for entry in media_entries:
        media_type_counts[entry.media_type] = media_type_counts.get(entry.media_type, 0) + int(entry.duration)

    most_consumed_media = max(media_type_counts, key=media_type_counts.get)

    # Calculate the daily average time
    unique_dates = {entry.date for entry in media_entries}
    daily_average_time = total_duration / len(unique_dates) if unique_dates else 0

    return {
        "total_time": round(total_time, 2),
        "most_consumed_media": most_consumed_media,
        "daily_average_time": round(daily_average_time / 60, 2)  # Convert minutes to hours
    }

def get_current_media(username):
    # Fetch current media entries grouped by media_name and media_type
    return db.session.query(
        Entries.media_name,
        Entries.media_type,
        func.sum(Entries.duration).label('total_duration')
    ).join(Activities).filter(Activities.username == username).group_by(Entries.media_name, Entries.media_type).all()

def handle_dashboard_form(username, form):
    """
    Handle form submissions for the dashboard route.
    """
    if 'add_duration' in form:  # Add duration to an existing media
        media_name = form.get('media_name')
        media_type = form.get('media_type')
        duration = form.get('duration')
        if media_name and duration:
            handle_add_duration(username, media_name, media_type, duration)
            flash(f'Duration added to {media_name}.', 'success')
    elif 'add_new_entry' in form:  # Add a new media entry
        media_type = form.get('media_type')
        media_name = form.get('media_name')
        duration = form.get('duration')
        if media_type and media_name and duration:
            handle_add_new_activity(username, media_type, media_name, duration)
            flash(f'New media entry "{media_name}" added.', 'success')

def handle_add_duration(username, media_name, media_type, duration):
    # Add a new entry with the given duration
    activity = Activities.query.filter_by(username=username).join(Entries).filter(Entries.media_name == media_name).first()
    if not activity:
        return False

    new_entry = Entries(
        activity_id=activity.id,
        media_name=media_name,
        media_type=media_type,
        duration=duration,
        date=datetime.now().date()
    )
    db.session.add(new_entry)
    db.session.commit()

def get_current_activities(username):
    """
    Fetch all current activities (where status = 'in_progress') for the given user.
    """
    # Query activities with status = 'in_progress'
    current_activities = Activities.query.filter_by(username=username, status='in_progress').all()

    activities = []
    for activity in current_activities:
        # Calculate the total duration for the activity
        total_duration = db.session.query(
            func.sum(Entries.duration)
        ).filter_by(activity_id=activity.id).scalar()

        # Fetch the media name and type from the first entry
        first_entry = Entries.query.filter_by(activity_id=activity.id).first()
        if not first_entry:
            continue

        # Append the activity details to the list
        activities.append({
            "media_name": first_entry.media_name,
            "media_type": first_entry.media_type,
            "total_duration": total_duration or 0,
            "activity_id": activity.id
        })

    return activities