from app.models import Entries, Activities, SharedUsers
from app import db
from flask import flash, render_template, redirect, url_for
from datetime import datetime
from sqlalchemy import func, cast, Integer
from app.forms import EndActivityForm, ReopenActivityForm, DeleteActivityForm

def get_activities(username, request):
    """
    Fetch uncompleted and completed activities for the given user based on query parameters.
    """
    # Check if the user is allowed to view the target user's data
    target_user = request.args.get('username', username)
    if target_user != username:
        if not SharedUsers.query.filter_by(username=target_user, shared_username=username).first():
            flash('You do not have permission to view this user’s data.', 'danger')
            return redirect(url_for('main.sharedata'))

    # Get filter criteria from query parameters
    filters = {
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
        'media_name': request.args.get('media_name'),
        'media_type': request.args.get('media_type'),
        'min_duration': request.args.get('min_duration'),
        'max_duration': request.args.get('max_duration')
    }
    sort_field = request.args.get('sort_field', 'date')
    sort_order = request.args.get('sort_order', 'desc')

    # Fetch uncompleted and completed activities
    uncompleted_activities = get_uncompleted_activities(username, sort_field, sort_order, filters)
    completed_activities = get_completed_activities(username, sort_field, sort_order, filters)

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

    end_activity_form = EndActivityForm()  # Create an instance of the EndActivityForm
    reopen_activity_forms = {
        activity.id: ReopenActivityForm(activity_id=activity.id) for activity in completed_activities
    }
    delete_activity_forms = {
        activity.id: DeleteActivityForm(activity_id=activity.id)
        for activity in uncompleted_activities + completed_activities
    }

    return render_template(
        'activities.html',
        uncompleted_activities=uncompleted_activities,
        completed_activities=completed_activities,
        page=page,
        total_pages=total_pages,
        request_args=args,
        username=username,
        end_activity_form=end_activity_form,
        reopen_activity_forms=reopen_activity_forms,
        delete_activity_forms=delete_activity_forms
    )

def get_uncompleted_activities(username, sort_field, sort_order, filters=None):
    """
    Fetch uncompleted activities (status = 'in_progress') for the given user.
    Include activities even if there are no corresponding entries.
    """
    # Query uncompleted activities
    query = (db.session.query(
        Activities.id.label('id'),
        Activities.media_type,
        Activities.media_subtype,
        Activities.media_name,
        Activities.start_date,
        func.coalesce(func.sum(cast(Entries.duration, Integer)), 0).label('total_duration'),
    ).outerjoin(Entries, Activities.id == Entries.activity_id).filter(
        Activities.username == username,
        Activities.status == 'ongoing'
    ).group_by(
        Activities.id, Activities.media_type, Activities.media_subtype, Activities.media_name, Activities.start_date
    )
    )
    if filters:
        query = apply_activity_filters(query, filters)

    # Sorting logic
    sort_fields = {
        'start_date': Activities.start_date,
        'end_date': Activities.end_date,
        'media_name': Activities.media_name,
        'media_type': Activities.media_type,
        'media_subtype': Activities.media_subtype,
        'total_duration': func.coalesce(func.sum(cast(Entries.duration, Integer)), 0),
        'rating': Activities.rating
    }
    sort_col = sort_fields.get(sort_field, Activities.start_date)
    if sort_order == 'asc':
        query = query.order_by(sort_col.asc(), Activities.id.asc())
    else:
        query = query.order_by(sort_col.desc(), Activities.id.desc())

    results = query.all()
    return results


def get_completed_activities(username, sort_field, sort_order, filters=None):
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
        Activities.start_date,
        Activities.end_date,
        Activities.rating,
        Activities.comment
    ).join(Activities, Activities.id == Entries.activity_id).filter(
        Activities.username == username,
        Activities.status != 'ongoing'
    ).group_by(
        Activities.id, Activities.media_type, Activities.media_subtype, Activities.media_name, Activities.start_date, Activities.end_date, Activities.rating, Activities.comment
    )
    )

    query = apply_activity_filters(query, filters)

    # Sorting logic
    sort_fields = {
        'start_date': Activities.start_date,
        'end_date': Activities.end_date,
        'media_name': Activities.media_name,
        'media_type': Activities.media_type,
        'media_subtype': Activities.media_subtype,
        'total_duration': func.sum(cast(Entries.duration, Integer)),
        'rating': Activities.rating
    }
    sort_col = sort_fields.get(sort_field, Activities.start_date)
    if sort_order == 'asc':
        query = query.order_by(sort_col.asc(), Activities.id.asc())
    else:
        query = query.order_by(sort_col.desc(), Activities.id.desc())

    results = query.all()
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
        media_type_filter = filters['media_type']
        query = query.filter(
            db.or_(
                Activities.media_type.ilike(f"%{media_type_filter}%"),
                Activities.media_subtype.ilike(f"%{media_type_filter}%")
            )
        )
    if filters.get('min_duration'):
        min_d = int(filters['min_duration'])
        query = query.having(func.sum(cast(Entries.duration, Integer)) >= min_d)
    if filters.get('max_duration'):
        max_d = int(filters['max_duration'])
        query = query.having(func.sum(cast(Entries.duration, Integer)) <= max_d)
    return query

def handle_end_activity(username, form):
    """
    Handle ending an activity by setting its status to 'completed', updating the rating, comment, and end_date fields.
    """
    activity_id = form.activity_id.data  # Get the activity ID from the form
    rating = form.rating.data  # Get the rating from the form
    comment = form.comment.data  # Get the comment from the form
    # Convert empty strings to None
    rating = float(rating) if rating else None
    comment = comment if comment else None

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
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while completing the activity: {e}", "danger")
        return None
    
def handle_reopen_activity(form):
    activity_id = form.activity_id.data
    if not activity_id:
        flash('Missing data for reopen.', 'danger')
        return redirect(url_for('main.viewdata'))

    activity = db.session.get(Activities, activity_id)
    if not activity:
        flash('Activity not found.', 'danger')
        return redirect(url_for('main.viewdata'))

    activity.status = 'ongoing'
    activity.end_date   = None
    activity.rating     = None
    activity.comment    = None
    db.session.commit()

    flash('Activity reopened.', 'success')
    return redirect(url_for('main.dashboard'))

def handle_add_activity(username, form):
    """
    Handle adding a new activity.
    """
    media_name = form.media_name.data
    media_type = form.media_type.data
    media_subtype = form.media_subtype.data
    start_date = form.date.data

    # Create a new activity
    new_activity = Activities(
        username=username,
        media_name=media_name,
        media_type=media_type,
        media_subtype=media_subtype,
        status='ongoing',
        start_date=start_date
    )

    db.session.add(new_activity)
    db.session.commit()
    flash(f"Activity '{media_name}' added successfully.", "success")
    return redirect(url_for('main.dashboard'))
        
def handle_delete_activity(form):
    activity_id = form.activity_id.data
    activity = Activities.query.filter_by(id=activity_id).first()
    if not activity:
        flash('Activity not found or unauthorized.', 'danger')
        return redirect(url_for('main.activities'))

    # Delete all related entries in the Entries table
    related_entries = Entries.query.filter_by(activity_id=activity.id).all()
    for entry in related_entries:
        db.session.delete(entry)

    # Delete the activity itself
    db.session.delete(activity)
    db.session.commit()
    
    flash('Activity and all related entries deleted successfully.', 'success')
    return redirect(url_for('main.activities'))