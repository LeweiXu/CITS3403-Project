from app.models import Entries, Activities
from app import db
from sqlalchemy import func
from datetime import datetime
from flask import flash, render_template

def get_dashboard_data(username, add_activity_form):
    stats = get_user_statistics(username)
    current_activities = get_current_activities(username)
    return render_template(
        'dashboard.html',
        total_time=stats['total_time'],
        most_consumed_media=stats['most_consumed_media'],
        daily_average_time=stats['daily_average_time'],
        current_activities=current_activities,
        add_activity_form=add_activity_form
    )

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

# def get_current_activities(username):
#     # Fetch current activities grouped by media_name and media_type
#     return db.session.query(
#         Activities.media_name,
#         Activities.media_type,
#         Activities.activity_id,
#         func.sum(Entries.duration).label('total_duration')
#     ).join(Entries).filter(Activities.username == username).group_by(Activities.media_name, Activities.media_type).all()