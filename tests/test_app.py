import unittest
from app import app, create_app, db
from app.config import TestConfig
from app.models import Users, Activities, Entries
from datetime import datetime, date
class MediaTrackerTests(unittest.TestCase):
    def setUp(self):
        testApp = create_app(TestConfig)
        self.app_ctx = testApp.app_context()
        self.app_ctx.push()
        db.create_all()
        self.client = testApp.test_client()
        return super().setUp()

    # Clean up after each test
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_ctx.pop()
        return super().tearDown()

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
        # Create user first
        self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test123!@#'
        })
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'Test123!@#'
        })
        # Test if login redirects to dashboard
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'{"redirect_url":"/dashboard","success":true}', response.data)  # Verify we see the login page

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        # Make new user and response
        register_response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test123!@#'
        }, follow_redirects=True)
        self.assertEqual(register_response.status_code, 200) # Make sure register is successful

        # Attempt login with wrong password
        login_response = self.client.post('/login', data={
            'username': 'testuser',
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
        # Register and login first to properly set up authentication
        self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test123!@#'
        })
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'Test123!@#'
        })
        
        # Setup user and activity
        activity = Activities(
            username='testuser',
            media_type='Visual Media',
            media_name='Test Movie',
            start_date=date.today()
        )
        db.session.add(activity)
        db.session.commit()
            
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Movie', response.data)

    def test_activity_creation(self):
        """Test creating a new activity"""
        # Register and login
        self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test123!@#'
        })
        self.client.post('/login', data={
        'username': 'testuser',
        'password': 'Test123!@#'
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
        self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test123!@#'
        })
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'Test123!@#'
        })

        # Create activity

        activity = Activities(
            username='testuser',
            media_type='Visual Media',
            media_subtype='Movie',
            media_name='Test Movie',
            start_date=date.today(),
            status='ongoing'
        )
        db.session.add(activity)
        db.session.commit()
        activity_id = activity.id

        # Add entry via POST to /add_entry (new)
        response = self.client.post('/add_entry', data={
            'activity_id': activity_id,
            'duration': 120,
            'date': date.today().strftime('%Y-%m-%d'),
            'add_duration': True
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)  # Should redirect after successful add
        # Checks if entry exists and duration matches
        
    # with app.app_context():
        entry = Entries.query.filter_by(activity_id=activity_id).first()
        self.assertIsNotNone(entry)
        self.assertEqual(entry.duration, 120)

    def test_end_activity(self):
        """Test ending an activity with rating and comment"""
        # Gotta register and login 
        self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test123!@#'
        })
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'Test123!@#'
        })

        # Setup activity
        activity = Activities(
            username='testuser',
            media_type='Visual Media',
            media_subtype='Movie',
            media_name='Test Movie'
        )
        db.session.add(activity)
        db.session.commit()
        activity_id = activity.id

        # End activity with optional stuff in it
        response = self.client.post('/end_activity', data={
            'activity_id': activity_id,
            'rating': '8',
            'comment': 'Great movie!'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Checks if activity has end date, all optional stuff matches
        activity = db.session.get(Activities, activity_id)
        self.assertIsNotNone(activity)
        self.assertIsNotNone(activity.end_date)
        self.assertEqual(activity.rating, 8)
        self.assertEqual(activity.comment, 'Great movie!')
        self.assertEqual(activity.status, 'completed')
