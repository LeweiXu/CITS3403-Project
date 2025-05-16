import unittest
from app import app, create_app, db
from app.config import TestConfig
from app.models import Users, Activities, Entries
from datetime import datetime, date
from tests.populate_db import populate_users_and_data as populate
class MediaTrackerTests(unittest.TestCase):
    def setUp(self):
        testApp = create_app(TestConfig)
        self.app_ctx = testApp.app_context()
        self.app_ctx.push()
        # Populate database with test data and users "aoi" and "neko" with password "Password123#"
        populate(testApp, db)
        self.client = testApp.test_client()

    # Clean up after each test
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_ctx.pop()

    def test_register_user(self):
        """Test user registration"""
        # Make test user, use POST request to /register
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test123!@#'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Check if test user exists in database and matches email
        user = Users.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')

    def test_successful_login(self):
        """Test login with valid account"""
        response = self.client.post('/login', data={
            'username': 'aoi',
            'password': 'Password123#'
        })
        # Test if login redirects to dashboard
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'{"redirect_url":"/dashboard","success":true}', response.data)  # Verify we see the login page

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        # Attempt login with wrong password
        login_response = self.client.post('/login', data={
            'username': 'aoi',
            'password': 'wrongpassword'
        }, follow_redirects=True)
    
        self.assertEqual(login_response.status_code, 200)
        self.assertIn(b'Invalid username or password', login_response.data) # Check title to see if we went back to index

    def test_unauthorised_access(self):
        """Test accessing protected routes without login"""
        response = self.client.get('/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)  # Redirect to login
        self.assertIn(b'Track Your Media Consumption', response.data)  # Verify we see the login page

    def test_get_user_activities(self):
        """Test retrieving user's activities"""
        # Login as user "aoi"
        self.client.post('/login', data={
            'username': 'aoi',
            'password': 'Password123#'
        })
            
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Elden Ring', response.data)

        # login as user "neko"
        self.client.post('/login', data={
            'username': 'neko',
            'password': 'Password123#'
        })
            
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Cyberpunk 2077', response.data)

    def test_activity_creation(self):
        """Test creating a new activity"""
        # Register and login
        self.client.post('/login', data={
        'username': 'aoi',
        'password': 'Password123#'
        })
        # Create new activity by POST to /add_acticity (new)
        response = self.client.post('/add_activity', data={
            'media_type': 'Visual Media',
            'media_subtype': 'Movie',
            'media_name': 'Test Movie',
            'add_new_entry': True
        })
        self.assertEqual(response.status_code, 302)
        
        # Checks if activity exists in database and media type matches input
        activity = Activities.query.filter_by(media_name='Test Movie').first()
        self.assertIsNotNone(activity)
        self.assertEqual(activity.media_type, 'Visual Media')
    
    def test_add_entry(self):
        """Test adding an entry to an activity"""
        # Gotta register and login fr
        self.client.post('/login', data={
            'username': 'aoi',
            'password': 'Password123#'
        })

        # Add entry via POST to /add_entry (new)
        response = self.client.post('/add_entry', data={
            'activity_id': 15,
            'duration': 120,
            'date': date.today().strftime('%Y-%m-%d'),
            'add_duration': True
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)  # Should redirect after successful add
        # Checks if entry exists and duration matches
        
        entry = Entries.query.filter_by(activity_id=15).order_by(Entries.id.desc()).first()
        self.assertIsNotNone(entry) 
        self.assertEqual(entry.duration, 120)

    def test_end_activity(self):
        """Test ending an activity with rating and comment"""
        # Gotta register and login 
        self.client.post('/login', data={
            'username': 'aoi',
            'password': 'Password123#'
        })

        # End activity with optional stuff in it
        response = self.client.post('/end_activity', data={
            'activity_id': 15,
            'rating': '8',
            'comment': 'Great movie!'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Checks if activity has end date, all optional stuff matches
        activity = db.session.get(Activities, 15)
        self.assertIsNotNone(activity)
        self.assertIsNotNone(activity.end_date)
        self.assertEqual(activity.rating, 8)
        self.assertEqual(activity.comment, 'Great movie!')
        self.assertEqual(activity.status, 'completed')

    def test_delete_entry(self):
        """Test deleting an entry from an activity"""
        # Register and login
        self.client.post('/login', data={
            'username': 'aoi',
            'password': 'Password123#'
        })
        # Delete entry
        response = self.client.post('/delete_entry', data={
            'entry_id': 1
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        deleted_entry = db.session.get(Entries, 1)
        self.assertIsNone(deleted_entry)

    def test_reopen_activity(self):
        """Test reopening a completed activity"""
        # Register and login
        self.client.post('/login', data={
            'username': 'aoi',
            'password': 'Password123#'
        })
        # Reopen activity
        response = self.client.post('/reopen_activity', data={
            'activity_id': 20
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        reopened_activity = db.session.get(Activities, 20)
        self.assertEqual(reopened_activity.status, 'ongoing')
        self.assertIsNone(reopened_activity.end_date)
        self.assertIsNone(reopened_activity.rating)
        self.assertIsNone(reopened_activity.comment)

    def test_delete_activity(self):
        """Test deleting an activity and its entries"""
        # Register and login
        self.client.post('/login', data={
            'username': 'aoi',
            'password': 'Password123#'
        })
        # Delete activity
        response = self.client.post('/delete_activity', data={
            'activity_id': 20
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        deleted_activity = db.session.get(Activities, 20)
        deleted_entries = Entries.query.filter_by(activity_id=20).all()
        self.assertIsNone(deleted_activity)
        self.assertEqual(len(deleted_entries), 0)  # All entries should be deleted