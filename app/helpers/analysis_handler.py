from app.models import Activities, Entries
from app import db
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from sqlalchemy import case

def get_analysis_data(username):
    """
    Fetch data for the analysis page, including statistics, rankings, and graph data.
    """
    # Overall Statistics
    total_books = db.session.query(func.sum(Entries.duration)).join(Activities).filter(
        Activities.username == username,
        Entries.media_type.ilike('%book%')
    ).scalar() or 0

    total_visual_media = db.session.query(func.sum(Entries.duration)).join(Activities).filter(
        Activities.username == username,
        Entries.media_type.ilike('%movie%') | Entries.media_type.ilike('%tv%')
    ).scalar() or 0

    total_games = db.session.query(func.sum(Entries.duration)).join(Activities).filter(
        Activities.username == username,
        Entries.media_type.ilike('%game%')
    ).scalar() or 0

    # Time spent in the past week
    one_week_ago = datetime.now().date() - timedelta(days=7)
    week_books = db.session.query(func.sum(Entries.duration)).join(Activities).filter(
        Activities.username == username,
        Entries.media_type.ilike('%book%'),
        Entries.date >= one_week_ago
    ).scalar() or 0

    week_visual_media = db.session.query(func.sum(Entries.duration)).join(Activities).filter(
        Activities.username == username,
        (Entries.media_type.ilike('%movie%') | Entries.media_type.ilike('%tv%')),
        Entries.date >= one_week_ago
    ).scalar() or 0

    week_games = db.session.query(func.sum(Entries.duration)).join(Activities).filter(
        Activities.username == username,
        Entries.media_type.ilike('%game%'),
        Entries.date >= one_week_ago
    ).scalar() or 0

    # Longest activity
    longest_activity = db.session.query(
        Entries.media_name, func.sum(Entries.duration).label('total_duration')
    ).join(Activities).filter(
        Activities.username == username
    ).group_by(Entries.media_name).order_by(func.sum(Entries.duration).desc()).first()

    # Rankings
    activities_by_duration = db.session.query(
        Activities.id, Entries.media_name, Entries.media_type,
        func.sum(Entries.duration).label('total_duration'),
        func.min(Entries.date).label('start_date'),
        func.max(Entries.date).label('end_date')
    ).join(Entries).filter(
        Activities.username == username
    ).group_by(Activities.id, Entries.media_name, Entries.media_type).order_by(
        func.sum(Entries.duration).desc()
    ).limit(10).all()

    entries_by_duration = db.session.query(
        Entries.media_name, Entries.media_type, Entries.duration
    ).join(Activities).filter(
        Activities.username == username
    ).order_by(Entries.duration.desc()).limit(10).all()

    activities_by_start_date = db.session.query(
        Activities.id, Entries.media_name, Entries.media_type,
        func.min(Entries.date).label('start_date'),
        func.sum(Entries.duration).label('total_duration')
    ).join(Entries).filter(
        Activities.username == username
    ).group_by(Activities.id, Entries.media_name, Entries.media_type).order_by(
        func.min(Entries.date).asc()
    ).limit(10).all()

    entries_by_media_type = db.session.query(
        Entries.media_type, func.sum(Entries.duration).label('total_duration')
    ).join(Activities).filter(
        Activities.username == username
    ).group_by(Entries.media_type).order_by(func.sum(Entries.duration).desc()).limit(10).all()

    # Graph Data
    daily_time_past_week = db.session.query(
        Entries.date, func.sum(Entries.duration).label('total_duration')
    ).join(Activities).filter(
        Activities.username == username,
        Entries.date >= one_week_ago
    ).group_by(Entries.date).order_by(Entries.date).all()

    weekly_average_past_10_weeks = db.session.query(
        func.strftime('%Y-%W', Entries.date).label('week'),
        func.avg(Entries.duration).label('average_duration')
    ).join(Activities).filter(
        Activities.username == username,
        Entries.date >= datetime.now().date() - timedelta(weeks=10)
    ).group_by('week').order_by('week').all()

    daily_category_past_week = db.session.query(
        Entries.date,
        func.sum(case((Entries.media_type.ilike('%book%'), Entries.duration), else_=0)).label('books'),
        func.sum(case((Entries.media_type.ilike('%movie%') | Entries.media_type.ilike('%tv%'), Entries.duration), else_=0)).label('visual_media'),
        func.sum(case((Entries.media_type.ilike('%game%'), Entries.duration), else_=0)).label('games')
    ).join(Activities).filter(
        Activities.username == username,
        Entries.date >= one_week_ago
    ).group_by(Entries.date).order_by(Entries.date).all()

    return {
        "statistics": {
            "total_books": round(total_books / 60, 2),
            "total_visual_media": round(total_visual_media / 60, 2),
            "total_games": round(total_games / 60, 2),
            "week_books": round(week_books / 60, 2),
            "week_visual_media": round(week_visual_media / 60, 2),
            "week_games": round(week_games / 60, 2),
            "longest_activity": {
                "media_name": longest_activity[0] if longest_activity else "N/A",
                "duration": round(longest_activity[1] / 60, 2) if longest_activity else 0
            }
        },
        "rankings": {
            "activities_by_duration": activities_by_duration,
            "entries_by_duration": entries_by_duration,
            "activities_by_start_date": activities_by_start_date,
            "entries_by_media_type": entries_by_media_type
        },
        "graphs": {
            "daily_time_past_week": daily_time_past_week,
            "weekly_average_past_10_weeks": weekly_average_past_10_weeks,
            "daily_category_past_week": daily_category_past_week
        }
    }