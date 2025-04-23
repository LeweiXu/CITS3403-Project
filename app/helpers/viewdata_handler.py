from app.models import Entries
from sqlalchemy import cast, Integer

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
    query = Entries.query.filter_by(username=username)

    if start_date:
        query = query.filter(Entries.date >= start_date)
    if end_date:
        query = query.filter(Entries.date <= end_date)
    if media_name:
        query = query.filter(Entries.media_name.ilike(f"%{media_name}%"))
    if media_type:
        query = query.filter(Entries.media_type.ilike(f"%{media_type}%"))
    if min_duration:
        query = query.filter(cast(Entries.duration, Integer) >= int(min_duration))
    if max_duration:
        query = query.filter(cast(Entries.duration, Integer) <= int(max_duration))

    # Execute the query and return the results
    return query.order_by(Entries.date.desc()).all()