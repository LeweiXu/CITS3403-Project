import unittest
from app import app, db
from app.models import Users, Activities, Entries
from datetime import datetime, date

class MediaTrackerTests(unittest.TestCase):
    def setUp(self):
        # Configure app for testing, runs before each tests
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'        # Use database in memory
        self.client = app.test_client()     # Create test client for requests
        
        # Create tables in test database
        with app.app_context():
            db.create_all()
            
    # Clean up after each test
    def tearDown(self):
        # Remove session and drop all tables, clean slate
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_user(self):
        """Test user registration"""
        # Make test user, use POST request to /register
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test123!@#'
        })
        self.assertEqual(response.status_code, 200)     # Response status code 200 is success
        
        # Check if test user exists in database and matches email
        with app.app_context():
            user = Users.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'test@example.com')

    def test_activity_creation(self):
        """Test creating a new activity"""
        # Register and login
        self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test123!@#'
        })
        
        with self.client.session_transaction() as session:
            session['username'] = 'testuser'
        
        # Create new activity by POST to /dashboard
        response = self.client.post('/dashboard', data={
            'media_type': 'Visual Media',
            'media_name': 'Test Movie',
            'add_new_entry': True
        })
        self.assertEqual(response.status_code, 302)  # Should redirect
        
        # Checks if activity exists in database and media type matches input
        with app.app_context():
            activity = Activities.query.filter_by(media_name='Test Movie').first()
            self.assertIsNotNone(activity)
            self.assertEqual(activity.media_type, 'Visual Media')
    
    def test_add_entry(self):
        """Test adding an entry to an activity"""
        # Setup user and activity 
        with app.app_context():
            user = Users(username='testuser', email='test@example.com', password='Test123!@#')
            activity = Activities(
                username='testuser',
                media_type='Visual Media',
                media_name='Test Movie',
                start_date=date.today()
            )
            db.session.add(user)
            db.session.add(activity)
            db.session.commit()
            activity_id = activity.id

        # Simulate logged in session
        with self.client.session_transaction() as session:
            session['username'] = 'testuser'

        # Add entry via POST to /dashboard
        response = self.client.post('/dashboard', data={
            'activity_id': activity_id,
            'duration': 120,
            'add_duration': True
        })
        
        # Checks if entry exists and duration matches
        with app.app_context():
            entry = Entries.query.filter_by(activity_id=activity_id).first()
            self.assertIsNotNone(entry)
            self.assertEqual(entry.duration, 120)

    def test_end_activity(self):
        """Test ending an activity with rating and comment"""
        # Setup user and activity
        with app.app_context():
            user = Users(username='testuser', email='test@example.com', password='Test123!@#')
            activity = Activities(
                username='testuser',
                media_type='Visual Media',
                media_name='Test Movie',
                start_date=date.today()
            )
            db.session.add(user)
            db.session.add(activity)
            db.session.commit()
            activity_id = activity.id

        # Simulates logged in session
        with self.client.session_transaction() as session:
            session['username'] = 'testuser'

        # End activity with optional stuff in it
        response = self.client.post('/end_activity', data={
            'activity_id': activity_id,
            'rating': 8.5,
            'comment': 'Great movie!'
        })
        
        # Checks if activity has end date, all optional stuff matches
        with app.app_context():
            activity = Activities.query.get(activity_id)
            self.assertIsNotNone(activity.end_date)
            self.assertEqual(activity.rating, 8.5)
            self.assertEqual(activity.comment, 'Great movie!')

if __name__ == '__main__':
    unittest.main()