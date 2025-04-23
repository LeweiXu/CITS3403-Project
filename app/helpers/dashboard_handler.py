from app.models import Entries, Activities
from app import db
from sqlalchemy import func
from datetime import datetime

def get_user_statistics(username):
    # Query all media entries for the current user
    media_entries = Entries.query.filter_by(username=username).all()

    if not media_entries:
        return {
            "total_time": 0,
            "most_consumed_media": None,
            "daily_average_time": 0
        }

    # Calculate total time spent (in hours)
    total_duration = sum(int(entry.duration) for entry in media_entries)
    total_time = total_duration / 60  # Convert minutes to hours

    # Find the most consumed media type
    media_type_counts = {}
    for entry in media_entries:
        media_type_counts[entry.media_type] = media_type_counts.get(entry.media_type, 0) + int(entry.duration)

    most_consumed_media = max(media_type_counts, key=media_type_counts.get)

    # Calculate the daily average time
    unique_dates = {entry.date for entry in media_entries}
    daily_average_time = total_duration / len(unique_dates) if unique_dates else 0

    return {
        "total_time": round(total_time, 2),
        "most_consumed_media": most_consumed_media,
        "daily_average_time": round(daily_average_time / 60, 2)  # Convert minutes to hours
    }

def get_current_media(username):
    # Fetch current media entries grouped by media_name and media_type
    return db.session.query(
        Entries.media_name,
        Entries.media_type,
        func.sum(Entries.duration).label('total_duration')
    ).filter_by(username=username).group_by(Entries.media_name, Entries.media_type).all()

def handle_add_duration(username, media_name, media_type, duration):
    # Add a new entry with the given duration
    new_entry = Entries(
        username=username,
        media_name=media_name,
        media_type=media_type,
        duration=duration,
        date=datetime.now().date()
    )
    db.session.add(new_entry)
    db.session.commit()

def handle_add_new_entry(username, media_type, media_name):
    # Add a new media entry with duration set to 0
    new_entry = Entries(
        username=username,
        media_type=media_type,
        media_name=media_name,
        duration=0,
        date=datetime.now().date()
    )
    db.session.add(new_entry)
    db.session.commit()

    # Add a corresponding entry in Activities
    new_activity = Activities(
        start_entry_id=new_entry.id,
        end_entry_id=None
    )
    db.session.add(new_activity)
    db.session.commit()

def get_current_activities(username):
    # Fetch all current activities (where end_entry_id is NULL)
    current_activities = Activities.query.filter_by(end_entry_id=None).all()

    activities = []
    for activity in current_activities:
        # Fetch the Entries corresponding to the start_entry_id
        start_entry = Entries.query.get(activity.start_entry_id)
        if not start_entry or start_entry.username != username:
            continue

        # Calculate the total duration for the media_name for the given user
        total_duration = db.session.query(
            func.sum(Entries.duration)
        ).filter_by(username=username, media_name=start_entry.media_name).scalar()

        # Append the activity details to the list
        activities.append({
            "media_name": start_entry.media_name,
            "media_type": start_entry.media_type,
            "total_duration": total_duration or 0,
            "activity_id": activity.id
        })

    return activities

def handle_add_new_entry(username, media_type, media_name, duration):
    # Add a new media entry with the specified duration
    new_entry = Entries(
        username=username,
        media_type=media_type,
        media_name=media_name,
        duration=duration,
        date=datetime.now().date()
    )
    db.session.add(new_entry)
    db.session.commit()

    # Add a corresponding entry in Activities
    new_activity = Activities(
        start_entry_id=new_entry.id,
        end_entry_id=None
    )
    db.session.add(new_activity)
    db.session.commit()

def handle_end_activity(activity_id, username, rating=None, comment=None):
    # Fetch the activity
    activity = Activities.query.get(activity_id)
    if not activity:
        return False

    # Fetch the MediaEntry object for the start_entry_id
    start_entry = Entries.query.get(activity.start_entry_id)
    if not start_entry or start_entry.username != username:
        return False

    # Find the newest entry with the same media_name for the user
    newest_entry = Entries.query.filter_by(
        username=username,
        media_name=start_entry.media_name
    ).order_by(Entries.id.desc()).first()

    if not newest_entry:
        return False

    # Update the CurrentActivities table with the newest entry's ID
    activity.end_entry_id = newest_entry.id

    # Add rating and comment if provided
    if rating:
        activity.rating = rating
    if comment:
        activity.comment = comment

    db.session.commit()
    return True