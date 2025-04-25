from app.models import Entries, Activities
from app import db
from flask import flash
from datetime import datetime
from sqlalchemy.sql import func

def fetch_past_activities(username, request):
    """
    Fetch uncompleted and completed activities for the given user based on query parameters.
    """
    # Get filter criteria from query parameters
    filters = {
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
        'media_name': request.args.get('media_name'),
        'media_type': request.args.get('media_type'),
        'min_duration': request.args.get('min_duration'),
        'max_duration': request.args.get('max_duration')
    }

    # Fetch uncompleted and completed activities
    uncompleted_activities = get_uncompleted_activities(username, filters)
    completed_activities = get_completed_activities(username, filters)

    return {
        "uncompleted_activities": uncompleted_activities,
        "completed_activities": completed_activities
    }

def get_uncompleted_activities(username, filters):
    """
    Fetch uncompleted activities (status = 'in_progress') for the given user.
    """
    # Query uncompleted activities
    query = Activities.query.filter(
        Activities.username == username,
        Activities.status == 'in_progress'  # Uncompleted activities
    )

    # Apply filters
    query = apply_activity_filters(query, filters)

    # Fetch required attributes
    return query.with_entities(
        Activities.id.label('activity_id'),
        Entries.media_type,
        Entries.media_name,
        func.sum(Entries.duration).label('total_duration'),
        func.min(Entries.date).label('start_date')  # Get the earliest date for the activity
    ).join(Entries, Activities.id == Entries.activity_id).group_by(
        Activities.id, Entries.media_type, Entries.media_name
    ).order_by(Activities.id.desc()).all()


def get_completed_activities(username, filters):
    """
    Fetch completed activities (status != 'in_progress') for the given user.
    """
    # Query completed activities
    query = Activities.query.filter(
        Activities.username == username,
        Activities.status != 'in_progress'  # Completed activities
    )

    # Apply filters
    query = apply_activity_filters(query, filters)

    # Fetch required attributes
    return query.with_entities(
        Activities.id.label('activity_id'),
        Entries.media_type,
        Entries.media_name,
        func.sum(Entries.duration).label('total_duration'),
        func.min(Entries.date).label('start_date'),  # Get the earliest date for the activity
        func.max(Entries.date).label('end_date'),  # Get the latest date for the activity
        Activities.rating
    ).join(Entries, Activities.id == Entries.activity_id).group_by(
        Activities.id, Entries.media_type, Entries.media_name, Activities.rating
    ).order_by(Activities.id.desc()).all()

def apply_activity_filters(query, filters):
    # Apply filters to the query
    if filters.get('start_date'):
        query = query.filter(Entries.date >= filters['start_date'])
    if filters.get('end_date'):
        query = query.filter(Entries.date <= filters['end_date'])
    if filters.get('media_name'):
        query = query.filter(Entries.media_name.ilike(f"%{filters['media_name']}%"))
    if filters.get('media_type'):
        query = query.filter(Entries.media_type.ilike(f"%{filters['media_type']}%"))
    if filters.get('min_duration'):
        query = query.filter(Entries.duration >= int(filters['min_duration']))
    if filters.get('max_duration'):
        query = query.filter(Entries.duration <= int(filters['max_duration']))
    return query

def handle_end_activity(activity_id, username, rating=None, comment=None):
    """
    Handle ending an activity by setting its status to 'completed', updating the rating, comment, and end_date fields.
    """
    # Fetch the activity
    activity = Activities.query.filter_by(id=activity_id, username=username).first()
    if not activity:
        flash(f"Activity with id {activity_id} not found or unauthorized.", "danger")
        return False

    # Set the status to 'completed'
    activity.status = 'completed'

    # Set the end_date to the current date
    activity.end_date = datetime.now().date()

    # Update the rating and comment if provided
    if rating is not None:  # Allow decimal ratings
        activity.rating = float(rating)
    if comment:
        activity.comment = comment

    try:
        db.session.commit()
        flash(f"Activity {activity_id} marked as completed successfully.", "success")
        return True
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while completing the activity: {e}", "danger")
        return False
    
def handle_add_new_activity(username, media_type, media_name, duration):
    # Add a new activity and its first media entry
    new_activity = Activities(
        username=username,
        start_date=datetime.now().date(),
        rating=None,
        comment=None
    )
    db.session.add(new_activity)
    db.session.commit()

    new_entry = Entries(
        activity_id=new_activity.id,
        media_type=media_type,
        media_name=media_name,
        duration=duration,
        date=datetime.now().date()
    )
    db.session.add(new_entry)
    db.session.commit()

    # Update the activity's start_entry_id to the new entry's id
    new_activity.start_entry_id = new_entry.id
    db.session.commit()