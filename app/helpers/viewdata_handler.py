from app.models import Entries, Activities
from sqlalchemy import cast, Integer
from flask import render_template
from app import db
from flask import flash, redirect, url_for, session

def get_entries(username, request):
    """
    Fetch filtered entries for the given user based on query parameters.
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

    # Get filtered entries
    entries = get_filtered_entries(username, filters)
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

    return render_template(
        'viewdata.html',
        entries=entries,
        page=page,
        total_pages=total_pages,
        request_args=args,
        visitor=False
    )


def get_filtered_entries(username, filters):
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

    # Execute the query and return the results
    return query.order_by(Entries.date.desc(),Entries.id.desc()).all()

def handle_delete_entry(entry_id, username):
    entry = Entries.query.get(entry_id)
    if entry:
        # Check if the entry belongs to the logged-in user
        activity = Activities.query.filter_by(id=entry.activity_id, username=username).first()
        if activity:
            db.session.delete(entry)
            db.session.commit()
            flash('Entry deleted successfully.', 'success')
        else:
            flash('Entry not found or unauthorized.', 'danger')
    else:
        flash('Entry not found.', 'danger')
    return redirect(url_for('viewdata'))