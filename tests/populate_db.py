import csv
from app.models import Users, Activities, Entries
from werkzeug.security import generate_password_hash
from datetime import datetime

def populate_users_and_data(app, db):
    with app.app_context():
        db.drop_all()
        db.create_all()
        # Create users
        users = [
            Users(username='aoi', email='aoi@example.com', password=generate_password_hash('Password123#')),
            Users(username='neko', email='neko@example.com', password=generate_password_hash('Password123#'))
        ]
        db.session.add_all(users)
        db.session.commit()

        # Helper to load activities and entries
        def load_activities_entries(user, activities_csv, entries_csv):
            activity_id_map = {}
            # Load activities
            with open(activities_csv, newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    activity = Activities(
                        username=user,
                        media_type=row['media_type'],
                        media_subtype=row.get('media_subtype'),
                        media_name=row['media_name'],
                        status=row['status'],
                        start_date=datetime.strptime(row['start_date'], '%Y-%m-%d').date() if row['start_date'] else None,
                        end_date=datetime.strptime(row['end_date'], '%Y-%m-%d').date() if row['end_date'] else None,
                        rating=float(row['rating']) if row['rating'] else None,
                        comment=row['comment'] if row['comment'] else None
                    )
                    db.session.add(activity)
                    db.session.flush()  # Get activity.id before commit
                    activity_id_map[row['id']] = activity.id
                db.session.commit()
            # Load entries
            with open(entries_csv, newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Map CSV activity_id to DB activity.id
                    act_id = activity_id_map.get(row['activity_id'])
                    if not act_id:
                        continue
                    entry = Entries(
                        activity_id=act_id,
                        date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                        duration=int(row['duration']),
                        comment=row['comment'] if 'comment' in row else None
                    )
                    db.session.add(entry)
                db.session.commit()

        # Populate for both users
        load_activities_entries('aoi', 'tests/test_activities_aoi.csv', 'tests/test_entries_aoi.csv')
        load_activities_entries('neko', 'tests/test_activities_neko.csv', 'tests/test_entries_neko.csv')

if __name__ == '__main__':
    populate_users_and_data()
