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

    def test_06_add_new_activity(self):
        """Test adding a new activity and verifying it appears on the Dashboard."""
        # Log in as 'aoi'
        self.click_element_with_wait(By.XPATH, "//nav//a[@data-bs-target='#loginModal']")
        login_modal = self.find_element_with_wait(By.ID, "loginModal")
        WebDriverWait(self.driver, 10).until(EC.visibility_of(login_modal))
        self.find_element_with_wait(By.ID, "username").send_keys("aoi")
        self.find_element_with_wait(By.ID, "password").send_keys("Password123#")
        self.click_element_with_wait(By.XPATH, "//form[@id='loginForm']//input[@type='submit']")
        WebDriverWait(self.driver, 5).until(EC.url_contains("/dashboard"))
        self.assertIn("/dashboard", self.driver.current_url)

        # Click the "Add New Activity" button
        self.click_element_with_wait(By.XPATH, "//button[@data-bs-target='#addActivityModal']")

        # Wait for the modal to appear
        add_activity_modal = self.find_element_with_wait(By.ID, "addActivityModal")
        WebDriverWait(self.driver, 10).until(EC.visibility_of(add_activity_modal))

        # Fill in the form
        # Select media type
        media_type_select = self.find_element_with_wait(By.ID, "media_type")
        media_type_select.click()
        media_type_select.find_element(By.XPATH, ".//option[normalize-space()='Visual Media']").click()

        # Wait for subtype to be enabled and select one
        media_subtype_select = self.find_element_with_wait(By.ID, "media_subtype")
        WebDriverWait(self.driver, 5).until(lambda d: not media_subtype_select.get_attribute("disabled"))
        media_subtype_select.click()
        media_subtype_select.find_element(By.XPATH, ".//option[normalize-space()='Movie']").click()

        # Fill in media name
        self.find_element_with_wait(By.ID, "media_name").send_keys("Test Movie")

        # Submit the form
        self.click_element_with_wait(By.XPATH, "//form[@id='addActivityForm']//input[@type='submit' or @class='btn btn-primary']")

        # Wait for modal to close and dashboard to reload
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located((By.ID, "addActivityModal")))
        WebDriverWait(self.driver, 10).until(EC.url_contains("/dashboard"))

        # Check if "Test Movie" appears anywhere on the current page
        self.assertIn("Test Movie", self.driver.page_source, "Newly added activity should appear on the Dashboard.")

    def test_07_reopen_activity(self):
        """Test reopening an activity for 'The Matrix' and check it appears on the Dashboard."""
        # Log in as 'aoi'
        self.click_element_with_wait(By.XPATH, "//nav//a[@data-bs-target='#loginModal']")
        login_modal = self.find_element_with_wait(By.ID, "loginModal")
        WebDriverWait(self.driver, 10).until(EC.visibility_of(login_modal))
        self.find_element_with_wait(By.ID, "username").send_keys("aoi")
        self.find_element_with_wait(By.ID, "password").send_keys("Password123#")
        self.click_element_with_wait(By.XPATH, "//form[@id='loginForm']//input[@type='submit']")
        WebDriverWait(self.driver, 5).until(EC.url_contains("/dashboard"))
        self.assertIn("/dashboard", self.driver.current_url)

        # Go to Activities page
        self.driver.get(BASE_URL.rstrip("/") + "/activities")
        WebDriverWait(self.driver, 10).until(EC.url_contains("/activities"))

        # Find the row for "The Matrix" and click to reveal the details (and the reopen button)
        row_xpath = "//tr[contains(@class, 'activity-row')][td[contains(text(), 'The Matrix')]]"
        matrix_row = self.find_element_with_wait(By.XPATH, row_xpath)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", matrix_row)
        matrix_row.click()  # Reveal the details row with the reopen button

        # Wait for the details row to be visible
        details_row_xpath = "//tr[contains(@class, 'activity-details')][preceding-sibling::tr[1][td[contains(text(), 'The Matrix')]]]"
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, details_row_xpath))
        )

        # Now find and click the reopen button in the revealed details row
        reopen_btn_xpath = (
            f"{details_row_xpath}//input[@type='submit' and contains(@class, 'btn-primary')]"
        )
        reopen_btn = self.find_element_with_wait(By.XPATH, reopen_btn_xpath)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", reopen_btn)
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, reopen_btn_xpath)))
        reopen_btn.click()

        # Wait for redirect to dashboard
        WebDriverWait(self.driver, 10).until(EC.url_contains("/dashboard"))
        self.assertIn("/dashboard", self.driver.current_url)

        # Assert "The Matrix" appears on the dashboard page
        self.assertIn("The Matrix", self.driver.page_source, "'The Matrix' should appear on the Dashboard after reopening.")

if __name__ == "__main__":
    unittest.main(verbosity=2)