from app.models import Entries, Activities, SharedUsers
from sqlalchemy import cast, Integer
from flask import render_template
from app import db
from flask import flash, redirect, url_for
from app.forms import DeleteEntryForm

def get_entries(username, request):
    """
    Fetch filtered entries for the given user based on query parameters.
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

    # Get filtered entries
    entries = get_filtered_entries(username, filters, sort_field, sort_order)
    ## 2) pagination parameters
    PER_PAGE    = 20
    page        = request.args.get('page', 1, type=int)
    total       = len(entries)
    total_pages = (total + PER_PAGE - 1) // PER_PAGE
    start_idx   = (page - 1) * PER_PAGE
    # 3) slice out just this page
    entries = entries[start_idx : start_idx + PER_PAGE]
    # Build a copy of request.args **without** the 'page' key
    args = request.args.to_dict()
    args.pop('page', None)

    delete_entry_forms = {entry.id: DeleteEntryForm(entry_id=entry.id) for entry in entries}

    return render_template(
        'viewdata.html',
        entries=entries,
        page=page,
        total_pages=total_pages,
        request_args=args,
        username=username,
        delete_entry_forms=delete_entry_forms
    )

def get_filtered_entries(username, filters, sort_field, sort_order):
    """
    Fetch and filter media entries based on the provided filters.
    """
    # Extract filter criteria
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    media_name = filters.get('media_name')
    media_type = filters.get('media_type')
    min_duration = filters.get('min_duration')
    max_duration = filters.get('max_duration')

    # Build the query
    query = Entries.query.join(Activities).filter(Activities.username == username)

    if start_date:
        query = query.filter(Entries.date >= start_date)
    if end_date:
        query = query.filter(Entries.date <= end_date)
    if media_name:
        query = query.filter(Activities.media_name.ilike(f"%{media_name}%"))
    if media_type:
        query = query.filter(
            db.or_(
                Activities.media_type.ilike(f"%{media_type}%"),
                Activities.media_subtype.ilike(f"%{media_type}%")
            )
        )
    if min_duration:
        query = query.filter(cast(Entries.duration, Integer) >= int(min_duration))
    if max_duration:
        query = query.filter(cast(Entries.duration, Integer) <= int(max_duration))

    # Sorting logic
    sort_fields = {
        'date': Entries.date,
        'media_type': Activities.media_type,
        'media_name': Activities.media_name,
        'duration': Entries.duration
    }
    sort_col = sort_fields.get(sort_field, Entries.date)
    if sort_order == 'asc':
        query = query.order_by(sort_col.asc(), Entries.id.asc())
    else:
        query = query.order_by(sort_col.desc(), Entries.id.desc())

    return query.all()

def handle_delete_entry(form):
    entry_id = form.entry_id.data
    entry = db.session.get(Entries, entry_id)
    if entry:
        db.session.delete(entry)
        db.session.commit()
        flash('Entry deleted successfully.', 'success')
    else:
        flash('Entry not found.', 'danger')
    return redirect(url_for('main.viewdata'))

def handle_add_entry(username, form):
    activity_id = form.activity_id.data
    duration = form.duration.data
    date = form.date.data
    comment = form.comment.data
    comment = comment if comment else None
    
    if not activity_id or not duration:
        flash("Activity ID and duration are required.", "danger")
        return redirect(url_for('main.dashboard'))
        
    activity = Activities.query.filter_by(id=activity_id, username=username).first()
    if not activity:
        flash("Activity not found or unauthorized.", "danger")
        return redirect(url_for('main.dashboard'))
        
    new_entry = Entries(
        activity_id=activity.id,
        date=date,
        duration=duration,
        comment=comment,
    )
    db.session.add(new_entry)

    try:
        db.session.commit()
        flash(f"Duration added to activity '{activity.media_name}' successfully.", "success")
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while adding the duration: {e}", "danger")
        return redirect(url_for('main.dashboard'))
