from app.models import Entries, Activities
from app import db
from sqlalchemy import func
from datetime import datetime
from flask import flash

def get_user_statistics(username):
    # Query all activities for the current user
    activities = db.session.query(Activities).filter(Activities.username == username).all()

    if not activities:
        return {
            "total_time": 0,
            "most_consumed_media": None,
            "daily_average_time": 0
        }

    # Calculate total time spent (in hours)
    total_duration = sum(
        db.session.query(func.sum(Entries.duration)).filter(Entries.activity_id == activity.id).scalar() or 0
        for activity in activities
    )
    total_time = total_duration / 60  # Convert minutes to hours

    # Find the most consumed media type
    media_type_counts = {}
    for activity in activities:
        total_activity_duration = db.session.query(func.sum(Entries.duration)).filter(Entries.activity_id == activity.id).scalar() or 0
        media_type_counts[activity.media_type] = media_type_counts.get(activity.media_type, 0) + total_activity_duration

    most_consumed_media = max(media_type_counts, key=media_type_counts.get) if media_type_counts else None

    # Calculate the daily average time
    unique_dates = {
        entry.date for activity in activities
        for entry in db.session.query(Entries).filter(Entries.activity_id == activity.id).all()
    }
    daily_average_time = total_duration / len(unique_dates) if unique_dates else 0

    return {
        "total_time": round(total_time, 2),
        "most_consumed_media": most_consumed_media,
        "daily_average_time": round(daily_average_time / 60, 2)  # Convert minutes to hours
    }

def get_current_activities(username):
    # Fetch current activities grouped by media_name and media_type
    return db.session.query(
        Activities.media_name,
        Activities.media_type,
        Activities.activity_id,
        func.sum(Entries.duration).label('total_duration')
    ).join(Entries).filter(Activities.username == username).group_by(Activities.media_name, Activities.media_type).all()

def handle_dashboard_form(username, form):
    """
    Handle form submissions for the dashboard route.
    """
    if 'add_duration' in form:  # Add duration to an existing media
        activity_id = form.get('activity_id')
        duration = form.get('duration')
        if activity_id and duration:
            handle_add_duration(username, activity_id, duration)
            flash(f'Duration added to activity ID {activity_id}.', 'success')
    elif 'add_new_entry' in form:  # Add a new media entry
        media_type = form.get('media_type')
        media_subtype = form.get('media_subtype')
        media_name = form.get('media_name')
        if media_type and media_name:
            # Add a new activity and its first media entry
            new_activity = Activities(
                username=username,
                media_type=media_type,
                media_subtype=media_subtype if media_subtype else None,
                media_name=media_name,
                start_date=datetime.now().date(),
                rating=None,
                comment=None
            )
            db.session.add(new_activity)
            db.session.commit()
            flash(f'New media entry "{media_name}" added.', 'success')

def handle_add_duration(username, activity_id, duration, comment=None):
    """
    Add a new media entry (duration and optional comment) to an existing activity.
    """
    # Fetch the activity
    activity = Activities.query.filter_by(id=activity_id, username=username).first()
    if not activity:
        flash(f"Activity with id {activity_id} not found or unauthorized.", "danger")
        return False

    # Create a new entry
    new_entry = Entries(
        activity_id=activity.id,
        date=datetime.now().date(),
        duration=duration,
        comment=comment
    )
    db.session.add(new_entry)

    try:
        db.session.commit()
        flash(f"Duration added to activity '{activity.media_name}' successfully.", "success")
        return True
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while adding the duration: {e}", "danger")
        return False

def get_current_activities(username):
    """
    Fetch all current activities (where status = 'in_progress') for the given user.
    """
    # Query activities with status = 'in_progress'
    current_activities = Activities.query.filter_by(username=username, status='ongoing').all()

    activities = []
    for activity in current_activities:
        # Calculate the total duration for the activity
        total_duration = db.session.query(
            func.sum(Entries.duration)
        ).filter_by(activity_id=activity.id).scalar()
        # Append the activity details to the list
        activities.append({
            "media_name": activity.media_name,
            "media_type": activity.media_type,
            "total_duration": total_duration or 0,
            "activity_id": activity.id
        })

    return activities