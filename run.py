from app import db, create_app

def clear_database():
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print(f"Clearing table {table.name}...")
        db.session.execute(table.delete())
    db.session.commit()

# Create the Flask app and push the application context
app = create_app()
with app.app_context():
    clear_database()