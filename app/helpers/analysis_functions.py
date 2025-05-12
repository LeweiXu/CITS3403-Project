from app.models import Activities, Entries
from app import db
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from sqlalchemy import case
from flask import render_template

def get_analysis_page(username):
    """
    Fetch data for the analysis page, including statistics, rankings, and graph data.
    """
    # Overall Statistics
    total_visual_media = db.session.query(func.sum(Entries.duration)).join(Activities).filter(
        Activities.username == username,
        Activities.media_type == 'Visual Media'
    ).scalar() or 0

    total_audio_media = db.session.query(func.sum(Entries.duration)).join(Activities).filter(
        Activities.username == username,
        Activities.media_type == 'Audio Media'
    ).scalar() or 0

    total_text_media = db.session.query(func.sum(Entries.duration)).join(Activities).filter(
        Activities.username == username,
        Activities.media_type == 'Text Media'
    ).scalar() or 0

    total_interactive_media = db.session.query(func.sum(Entries.duration)).join(Activities).filter(
        Activities.username == username,
        Activities.media_type == 'Interactive Media'
    ).scalar() or 0

    # Time spent in the past week by main media type
    one_week_ago = datetime.now().date() - timedelta(days=7)

    week_visual_media = db.session.query(func.sum(Entries.duration)).join(Activities).filter(
        Activities.username == username,
        Activities.media_type == 'Visual Media',
        Entries.date >= one_week_ago
    ).scalar() or 0

    week_audio_media = db.session.query(func.sum(Entries.duration)).join(Activities).filter(
        Activities.username == username,
        Activities.media_type == 'Audio Media',
        Entries.date >= one_week_ago
    ).scalar() or 0

    week_text_media = db.session.query(func.sum(Entries.duration)).join(Activities).filter(
        Activities.username == username,
        Activities.media_type == 'Text Media',
        Entries.date >= one_week_ago
    ).scalar() or 0

    week_interactive_media = db.session.query(func.sum(Entries.duration)).join(Activities).filter(
        Activities.username == username,
        Activities.media_type == 'Interactive Media',
        Entries.date >= one_week_ago
    ).scalar() or 0

    # Longest activity
    longest_activity = db.session.query(
        Activities.media_name, func.sum(Entries.duration).label('total_duration')
    ).join(Entries).filter(
        Activities.username == username
    ).group_by(Activities.media_name).order_by(func.sum(Entries.duration).desc()).first()

    # Rankings
    activities_by_duration = db.session.query(
        Activities.id, Activities.media_name, Activities.media_type,
        func.sum(Entries.duration).label('total_duration'),
        func.min(Entries.date).label('start_date'),
        func.max(Entries.date).label('end_date')
    ).join(Entries).filter(
        Activities.username == username
    ).group_by(Activities.id, Activities.media_name, Activities.media_type).order_by(
        func.sum(Entries.duration).desc()
    ).limit(10).all()

    entries_by_duration = db.session.query(
        Activities.media_name, Activities.media_type, Entries.duration
    ).join(Entries).filter(
        Activities.username == username
    ).order_by(Entries.duration.desc()).limit(10).all()

    activities_by_start_date = db.session.query(
        Activities.id, Activities.media_name, Activities.media_type,
        func.min(Entries.date).label('start_date'),
        func.sum(Entries.duration).label('total_duration')
    ).join(Entries).filter(
        Activities.username == username
    ).group_by(Activities.id, Activities.media_name, Activities.media_type).order_by(
        func.min(Entries.date).asc()
    ).limit(10).all()

    entries_by_media_subtype = db.session.query(
        Activities.media_subtype, func.sum(Entries.duration).label('total_duration')
    ).join(Entries).filter(
        Activities.username == username
    ).group_by(Activities.media_subtype).order_by(func.sum(Entries.duration).desc()).limit(10).all()

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
    func.sum(case((Activities.media_type == 'Visual Media', Entries.duration), else_=0)).label('visual_media'),
    func.sum(case((Activities.media_type == 'Audio Media', Entries.duration), else_=0)).label('audio_media'),
    func.sum(case((Activities.media_type == 'Text Media', Entries.duration), else_=0)).label('text_media'),
    func.sum(case((Activities.media_type == 'Interactive Media', Entries.duration), else_=0)).label('interactive_media')
).join(Activities).filter(
    Activities.username == username,
    Entries.date >= one_week_ago
).group_by(Entries.date).order_by(Entries.date).all()

    # Convert query results to dictionaries
    activities_by_duration = [
        {
            'media_name': a.media_name,
            'media_type': a.media_type,
            'total_duration': round(a.total_duration / 60, 2),
            'start_date': a.start_date.strftime('%Y-%m-%d'),
            'end_date': a.end_date.strftime('%Y-%m-%d') if a.end_date else None
        } for a in activities_by_duration
    ]

    entries_by_duration = [
        {
            'media_name': e.media_name,
            'media_type': e.media_type,
            'duration': round(e.duration / 60, 2)
        } for e in entries_by_duration
    ]

    activities_by_start_date = [
        {
            'media_name': a.media_name,
            'media_type': a.media_type,
            'start_date': a.start_date.strftime('%Y-%m-%d'),
            'total_duration': round(a.total_duration / 60, 2)
        } for a in activities_by_start_date
    ]

    entries_by_media_subtype = [
        {
            'media_subtype': e.media_subtype,
            'total_duration': round(e.total_duration / 60, 2)
        } for e in entries_by_media_subtype
    ]

    daily_time_past_week = [
        {
            'date': d.date.strftime('%Y-%m-%d'),
            'total_duration': d.total_duration
        } for d in daily_time_past_week
    ]

    weekly_average_past_10_weeks = [
        {
            'week': w.week,
            'average_duration': w.average_duration
        } for w in weekly_average_past_10_weeks
    ]

    daily_category_past_week = [
        {
            'date': d.date.strftime('%Y-%m-%d'),
            'visual_media': d.visual_media,
            'audio_media': d.audio_media,
            'text_media': d.text_media,
            'interactive_media': d.interactive_media
        } for d in daily_category_past_week
    ]

    return render_template('analysis.html', analysis_data={
        "statistics": {
            "total_visual_media": round(total_visual_media / 60, 2),
            "total_audio_media": round(total_audio_media / 60, 2),
            "total_text_media": round(total_text_media / 60, 2),
            "total_interactive_media": round(total_interactive_media / 60, 2),
            "week_visual_media": round(week_visual_media / 60, 2),
            "week_audio_media": round(week_audio_media / 60, 2),
            "week_text_media": round(week_text_media / 60, 2),
            "week_interactive_media": round(week_interactive_media / 60, 2),
            "longest_activity": {
                "media_name": longest_activity[0] if longest_activity else "N/A",
                "duration": round(longest_activity[1] / 60, 2) if longest_activity else 0
            }
        },
        "rankings": {
            "activities_by_duration": activities_by_duration,
            "entries_by_duration": entries_by_duration,
            "activities_by_start_date": activities_by_start_date,
            "entries_by_media_subtype": entries_by_media_subtype
        },
        "graphs": {
            "daily_time_past_week": daily_time_past_week,
            "weekly_average_past_10_weeks": weekly_average_past_10_weeks,
            "daily_category_past_week": daily_category_past_week
        }
    })