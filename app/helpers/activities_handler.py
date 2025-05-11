from app.models import Entries, Activities
from app import db
from flask import flash, render_template, redirect, url_for
from datetime import datetime
from sqlalchemy import func, cast, Integer

def get_activities(username, request):
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

    # Combine for simple pagination
    combined    = uncompleted_activities + completed_activities
    PER_PAGE    = 20
    page        = request.args.get('page', 1, type=int)
    total       = len(combined)
    total_pages = (total + PER_PAGE - 1) // PER_PAGE
    start_idx   = (page - 1) * PER_PAGE

    page_slice = combined[start_idx : start_idx + PER_PAGE]
    # split back
    uncompleted_activities   = [a for a in page_slice if a in uncompleted_activities]
    completed_activities = [a for a in page_slice if a in completed_activities]

    # **strip** the 'page' param before passing into template
    args = request.args.to_dict()
    args.pop('page', None)

    return render_template(
        'activities.html',
        uncompleted_activities=uncompleted_activities,
        completed_activities=completed_activities,
        page=page,
        total_pages=total_pages,
        request_args=args,
        visitor=False
    )

def get_uncompleted_activities(username, filters):
    """
    Fetch uncompleted activities (status = 'in_progress') for the given user.
    Include activities even if there are no corresponding entries.
    """
    # Query uncompleted activities
    query = (db.session.query(
        Activities.id.label('id'),  # Ensure activity ID is passed to the HTML page
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
        Activities.id.label('id'),
        Activities.media_type,
        Activities.media_subtype,
        Activities.media_name,
        func.sum(cast(Entries.duration, Integer)).label('total_duration'),
        func.min(Entries.date).label('start_date'),  # Get the earliest date for the activity
        func.max(Entries.date).label('end_date'),  # Get the latest date for the activity
        Activities.rating,
        Activities.comment
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

def handle_end_activity(username, request):
    """
    Handle ending an activity by setting its status to 'completed', updating the rating, comment, and end_date fields.
    """
    activity_id = request.form.get('activity_id')
    rating = request.form.get('rating')  # Get the rating from the form
    comment = request.form.get('comment')  # Get the comment from the form

    # Convert empty strings to None
    rating = float(rating) if rating else None
    comment = comment if comment else None

    if activity_id:
        success = handle_end_activity(activity_id, username, rating=rating, comment=comment)
        if success:
            flash('Activity ended successfully.', 'success')
        else:
            flash('Failed to end activity.', 'danger')

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
        return redirect(url_for('dashboard'))
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while completing the activity: {e}", "danger")
        return None
    
def handle_reopen_activity(activity_id, username):
    """
    Given an entry_id and the current username, mark its parent activity
    back to 'ongoing' so it shows up in Current Activities.
    Returns True if successful, False otherwise.
    """
    activity = Activities.query.get(activity_id)
    if not activity:
        return False

    # Only allow the owner to reopen
    if activity.username != username:
        return False

    activity.status = 'ongoing'
    activity.end_date   = None
    activity.rating     = None
    activity.comment    = None

    db.session.commit()
    return True