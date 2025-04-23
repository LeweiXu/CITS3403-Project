from app.models import Entries, Activities
from sqlalchemy.orm import aliased
from sqlalchemy import literal

def get_uncompleted_activities(username, filters):
    # Alias for the Entries table to join start_entry and end_entry
    start_entry = aliased(Entries)

    query = Activities.query.join(start_entry, Activities.start_entry_id == start_entry.id).filter(
        start_entry.username == username,
        Activities.end_entry_id == None  # Uncompleted activities
    )

    # Apply filters
    query = apply_activity_filters(query, filters, start_entry)

    # Fetch required attributes
    return query.with_entities(
        start_entry.media_type,
        start_entry.media_name,
        start_entry.duration.label('total_duration'),
        start_entry.date.label('start_date'),
        literal(None).label('end_date')  # Use literal(None) for no end date
    ).order_by(Activities.id.desc()).all()  # Sort by latest created first

def get_completed_activities(username, filters):
    # Alias for the Entries table to join start_entry and end_entry
    start_entry = aliased(Entries)
    end_entry = aliased(Entries)

    query = Activities.query.join(start_entry, Activities.start_entry_id == start_entry.id).join(
        end_entry, Activities.end_entry_id == end_entry.id
    ).filter(
        start_entry.username == username,
        Activities.end_entry_id != None  # Completed activities
    )

    # Apply filters
    query = apply_activity_filters(query, filters, start_entry)

    # Fetch required attributes
    return query.with_entities(
        start_entry.media_type,
        start_entry.media_name,
        start_entry.duration.label('total_duration'),
        start_entry.date.label('start_date'),
        end_entry.date.label('end_date')
    ).order_by(end_entry.date.desc()).all()  # Sort by latest completion date

def apply_activity_filters(query, filters, start_entry):
    if filters.get('start_date'):
        query = query.filter(start_entry.date >= filters['start_date'])
    if filters.get('end_date'):
        query = query.filter(start_entry.date <= filters['end_date'])
    if filters.get('media_name'):
        query = query.filter(start_entry.media_name.ilike(f"%{filters['media_name']}%"))
    if filters.get('media_type'):
        query = query.filter(start_entry.media_type.ilike(f"%{filters['media_type']}%"))
    if filters.get('min_duration'):
        query = query.filter(start_entry.duration >= int(filters['min_duration']))
    if filters.get('max_duration'):
        query = query.filter(start_entry.duration <= int(filters['max_duration']))
    return query