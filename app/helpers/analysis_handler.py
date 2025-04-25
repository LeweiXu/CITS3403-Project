from sqlalchemy.sql import func
from datetime import datetime, timedelta
from app.models import Entries, Activities
from app import db
from sqlalchemy import func
from datetime import datetime

def get_analysis_data(username):
    """
    Fetch insights and graph data for the analysis page.
    """
    # Total time spent on all activities
    total_duration = db.session.query(func.sum(Entries.duration)).join(Activities).filter(Activities.username == username).scalar() or 0

    # Example: Total time spent reading Twilight
    twilight_duration = db.session.query(func.sum(Entries.duration)).join(Activities).filter(
        Activities.username == username,
        Entries.media_name.ilike('%Twilight%')
    ).scalar() or 0

    # Example: Total time spent playing Valorant
    valorant_duration = db.session.query(func.sum(Entries.duration)).join(Activities).filter(
        Activities.username == username,
        Entries.media_name.ilike('%Valorant%')
    ).scalar() or 0

    # Example: Days taken to read 1984
    days_to_read_1984 = db.session.query(
        func.julianday(func.max(Entries.date)) - func.julianday(func.min(Entries.date))
    ).join(Activities).filter(
        Activities.username == username,
        Entries.media_name.ilike('%1984%')
    ).scalar() or 0

    # Weekly time spent reading for the past 10 weeks
    today = datetime.now().date()
    ten_weeks_ago = today - timedelta(weeks=10)
    weekly_reading_data = db.session.query(
        func.strftime('%Y-%W', Entries.date).label('week'),
        func.sum(Entries.duration).label('total_duration')
    ).join(Activities).filter(
        Activities.username == username,
        Entries.media_type.ilike('%Reading%'),
        Entries.date >= ten_weeks_ago
    ).group_by('week').order_by('week').all()

    # Prepare data for graphs
    weekly_labels = [week[0] for week in weekly_reading_data]
    weekly_durations = [week[1] for week in weekly_reading_data]

    return {
        "total_duration": round(total_duration / 60, 2),  # Convert minutes to hours
        "twilight_duration": round(twilight_duration / 60, 2),
        "valorant_duration": round(valorant_duration / 60, 2),
        "days_to_read_1984": round(days_to_read_1984, 2),
        "weekly_labels": weekly_labels,
        "weekly_durations": weekly_durations
    }