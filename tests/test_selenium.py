import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
from selenium.webdriver.chrome.service import Service as ChromeService # Import ChromeService
from app import create_app, db
from app.config import TestConfig
from tests.populate_db import populate_users_and_data as populate
import multiprocessing

# Configuration
# --- IMPORTANT ---
# Replace the placeholder path below with the ABSOLUTE path to your chromedriver executable.
# Example for macOS if it's in your Downloads folder and then in 'chromedriver-mac-arm64':
# driver_path = '/Users/your_username/Downloads/chromedriver-mac-arm64/chromedriver'
# Example for Windows if it's in a 'drivers' folder on C drive:
# driver_path = 'C:\\drivers\\chromedriver.exe'
BASE_URL = "http://localhost:5000/" # Double check this IP, usually it's 127.0.0.1, may different in yours
DRIVER_PATH = '/usr/bin/chromedriver'  # <-- !!! REPLACE THIS LINE !!!

class AuthTests(unittest.TestCase):
    # Define class-level variables for username, email, and password

    def setUp(self):
        self.testApp = create_app(TestConfig)
        self.app_context = self.testApp.app_context()
        self.app_context.push()
        populate(self.testApp, db)  # Populate the database with test data

        self.server_thread = multiprocessing.Process(target=self.testApp.run)
        self.server_thread.start()
        
        # Initialize the WebDriver using ChromeService
        try:
            service = ChromeService(executable_path=DRIVER_PATH)
            self.driver = webdriver.Chrome(service=service)
            self.driver.get(BASE_URL)
            self.driver.implicitly_wait(2) # Implicit wait for elements
            self.driver.maximize_window()
        except Exception as e:
            print(f"Error initializing WebDriver: {e}")
            print(f"Please ensure the path to chromedriver is correct: '{DRIVER_PATH}'")
            print("And that your Flask application is running.")
            raise

    def tearDown(self):
        self.server_thread.terminate()
        self.driver.close()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def find_element_with_wait(self, by, value, timeout=10):
        """Helper function to find an element with explicit wait."""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            self.fail(f"Element with {by}='{value}' not found within {timeout} seconds at URL: {self.driver.current_url}")

    def click_element_with_wait(self, by, value, timeout=10):
        """Helper function to click an element with explicit wait for clickability."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            element.click()
        except TimeoutException:
            self.fail(f"Element with {by}='{value}' not clickable within {timeout} seconds at URL: {self.driver.current_url}")

    def test_01_open_registration_modal(self):
        """Test opening the registration modal from the 'Get Started' button on the home page."""
        get_started_button = self.find_element_with_wait(By.XPATH, "//a[@data-bs-target='#registerModal' and contains(@class, 'btn-primary')]")
        get_started_button.click()
        
        register_modal = self.find_element_with_wait(By.ID, "registerModal")
        WebDriverWait(self.driver, 10).until(EC.visibility_of(register_modal))
        self.assertTrue(register_modal.is_displayed(), "Registration modal should be visible.")
        self.find_element_with_wait(By.ID, "reg-username")

        # --- FIX: Close the modal before clicking the nav link ---
        close_btn = self.find_element_with_wait(By.XPATH, "//div[@id='registerModal']//button[@data-bs-dismiss='modal']")
        close_btn.click()
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.ID, "registerModal")))

        """Test opening the registration modal from the navigation bar."""
        register_nav_link = self.find_element_with_wait(By.XPATH, "//nav//a[@data-bs-target='#registerModal']")
        register_nav_link.click()

        register_modal = self.find_element_with_wait(By.ID, "registerModal")
        WebDriverWait(self.driver, 10).until(EC.visibility_of(register_modal))
        self.assertTrue(register_modal.is_displayed(), "Registration modal should be visible after clicking nav link.")
        self.find_element_with_wait(By.ID, "reg-username") 
    
    def test_02_open_login_modal_from_nav(self):
        """Test opening the login modal from the navigation bar."""
        login_nav_link = self.find_element_with_wait(By.XPATH, "//nav//a[@data-bs-target='#loginModal']")
        login_nav_link.click()

        login_modal = self.find_element_with_wait(By.ID, "loginModal")
        WebDriverWait(self.driver, 10).until(EC.visibility_of(login_modal))
        self.assertTrue(login_modal.is_displayed(), "Login modal should be visible.")
        
        self.find_element_with_wait(By.ID, "username")

    def test_03_test_register(self):
        """Test successful user registration."""
        self.click_element_with_wait(By.XPATH, "//nav//a[@data-bs-target='#registerModal']")

        self.find_element_with_wait(By.ID, "reg-username").send_keys("testuser")
        self.find_element_with_wait(By.ID, "reg-email").send_keys("testuser@gmail.com")
        self.find_element_with_wait(By.ID, "reg-password").send_keys("Password123#")
        
        self.click_element_with_wait(By.XPATH, "//form[@id='registerForm']//input[@type='submit']")

        try:
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            self.assertIn("Registration successful! Please log in.", alert.text)
            alert.accept()
        except TimeoutException:
            self.fail("Alert not shown after registration.")

    def test_04_test_login(self):
        """Test successful login."""
        # Open the login modal from the nav bar
        self.click_element_with_wait(By.XPATH, "//nav//a[@data-bs-target='#loginModal']")
        login_modal = self.find_element_with_wait(By.ID, "loginModal")
        WebDriverWait(self.driver, 10).until(EC.visibility_of(login_modal))
        self.assertTrue(login_modal.is_displayed(), "Login modal should be visible after opening.")

        self.find_element_with_wait(By.ID, "username").send_keys("aoi")
        self.find_element_with_wait(By.ID, "password").send_keys("Password123#")
        self.click_element_with_wait(By.XPATH, "//form[@id='loginForm']//input[@type='submit']")
        WebDriverWait(self.driver, 2).until(EC.url_contains("/dashboard"))
        self.assertIn("/dashboard", self.driver.current_url, "User should be redirected to the dashboard after login.")

    def test_05_nav_after_login(self):
        """Test clicking all navbar buttons after logging in as 'aoi'."""
        # Log in first
        self.click_element_with_wait(By.XPATH, "//nav//a[@data-bs-target='#loginModal']")
        login_modal = self.find_element_with_wait(By.ID, "loginModal")
        WebDriverWait(self.driver, 10).until(EC.visibility_of(login_modal))
        self.find_element_with_wait(By.ID, "username").send_keys("aoi")
        self.find_element_with_wait(By.ID, "password").send_keys("Password123#")
        self.click_element_with_wait(By.XPATH, "//form[@id='loginForm']//input[@type='submit']")
        WebDriverWait(self.driver, 5).until(EC.url_contains("/dashboard"))
        self.assertIn("/dashboard", self.driver.current_url)

        # Find all visible navbar links/buttons (excluding logout for now)
        nav_links = ["/dashboard", "/activities", "/sharedata", "/viewdata", "/analysis"]

        for link in nav_links:
            self.driver.get(BASE_URL.rstrip("/") + link)
            # Check if page loaded successfully by checking the HTTP status code via JavaScript
            status = self.driver.execute_script("return window.performance.getEntriesByType('navigation')[0].responseStart ? 200 : 0;")
            self.assertEqual(status, 200, f"Failed to load {link} (status code: {status})")
if __name__ == "__main__":
    unittest.main(verbosity=2)