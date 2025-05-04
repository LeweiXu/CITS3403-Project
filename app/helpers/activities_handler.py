from app.models import Entries, Activities
from app import db
from flask import flash
from datetime import datetime
from sqlalchemy import func, cast, Integer

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
    Include activities even if there are no corresponding entries.
    """
    # Query uncompleted activities
    query = (db.session.query(
        Activities.id.label('activity_id'),
        Activities.media_type,
        Activities.media_subtype,
        Activities.media_name,
        func.coalesce(func.sum(cast(Entries.duration, Integer)), 0).label('total_duration'),
        func.min(Entries.date).label('start_date')  # Get the earliest date for the activity
    ).outerjoin(Entries, Activities.id == Entries.activity_id).filter(
        Activities.username == username,
        Activities.status == 'ongoing'  # Uncompleted activities
    ).group_by(
        Activities.id, Activities.media_type, Activities.media_name
    )
    )
    query = apply_activity_filters(query, filters)
    results = query.order_by(Activities.id.desc()).all()
    return results


def get_completed_activities(username, filters):
    """
    Fetch completed activities (status != 'ongoing') for the given user.
    """
    # Query completed activities
    query = (db.session.query(
        Activities.id.label('activity_id'),
        Activities.media_type,
        Activities.media_subtype,
        Activities.media_name,
        func.sum(cast(Entries.duration, Integer)).label('total_duration'),
        func.min(Entries.date).label('start_date'),  # Get the earliest date for the activity
        func.max(Entries.date).label('end_date'),  # Get the latest date for the activity
        Activities.rating
    ).join(Activities, Activities.id == Entries.activity_id).filter(
        Activities.username == username,
        Activities.status != 'ongoing'  # Completed activities
    ).group_by(
        Activities.id, Activities.media_type, Activities.media_name, Activities.end_date, Activities.rating, Activities.comment
    )
    )

    query = apply_activity_filters(query, filters)
    # Map media_type to main type
    results = query.order_by(Activities.id.desc()).all()
    return results

def apply_activity_filters(query, filters):
    # Apply filters to the query
    if filters.get('start_date'):
        query = query.filter(Entries.date >= filters['start_date'])
    if filters.get('end_date'):
        query = query.filter(Entries.date <= filters['end_date'])
    if filters.get('media_name'):
        query = query.filter(Activities.media_name.ilike(f"%{filters['media_name']}%"))
    if filters.get('media_type'):
        query = query.filter(Activities.media_type.ilike(f"%{filters['media_type']}%"))
    if filters.get('min_duration'):
        min_d = int(filters['min_duration'])
        query = query.having(func.sum(cast(Entries.duration, Integer)) >= min_d)
    if filters.get('max_duration'):
        max_d = int(filters['max_duration'])
        query = query.having(func.sum(cast(Entries.duration, Integer)) <= max_d)
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