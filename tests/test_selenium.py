import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
from selenium.webdriver.chrome.service import Service as ChromeService # Import ChromeService

# Configuration
BASE_URL = "http://127.0.0.1:5000/" # Double check this IP, usually it's 127.0.0.1, may different in yours

class AuthTests(unittest.TestCase):

    def setUp(self):
        # --- IMPORTANT ---
        # Replace the placeholder path below with the ABSOLUTE path to your chromedriver executable.
        # Example for macOS if it's in your Downloads folder and then in 'chromedriver-mac-arm64':
        # driver_path = '/Users/your_username/Downloads/chromedriver-mac-arm64/chromedriver'
        # Example for Windows if it's in a 'drivers' folder on C drive:
        # driver_path = 'C:\\drivers\\chromedriver.exe'

        driver_path = '/Users/neickof/webdrivers/chromedriver-mac-arm64/chromedriver' # <-- !!! REPLACE THIS LINE !!!

        # Initialize the WebDriver using ChromeService
        try:
            service = ChromeService(executable_path=driver_path)
            self.driver = webdriver.Chrome(service=service)
        except Exception as e:
            print(f"Error initializing WebDriver: {e}")
            print(f"Please ensure the path to chromedriver is correct: '{driver_path}'")
            print("And that your Flask application is running.")
            raise

        self.driver.implicitly_wait(10) # Implicit wait for elements
        self.driver.maximize_window()
        self.unique_timestamp = str(int(time.time())) # For creating unique users

    def tearDown(self):
        # Close the browser window
        if hasattr(self, 'driver'): # Check if driver was initialized
            self.driver.quit()

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

    def test_01_open_registration_modal_from_home(self):
        """Test opening the registration modal from the 'Get Started' button on the home page."""
        self.driver.get(BASE_URL)
        
        get_started_button = self.find_element_with_wait(By.XPATH, "//a[@data-bs-target='#registerModal' and contains(@class, 'btn-primary')]")
        get_started_button.click()
        
        register_modal = self.find_element_with_wait(By.ID, "registerModal")
        WebDriverWait(self.driver, 10).until(EC.visibility_of(register_modal))
        self.assertTrue(register_modal.is_displayed(), "Registration modal should be visible.")
        
        self.find_element_with_wait(By.ID, "reg-username")

    def test_02_open_registration_modal_from_nav(self):
        """Test opening the registration modal from the navigation bar."""
        self.driver.get(BASE_URL)

        register_nav_link = self.find_element_with_wait(By.XPATH, "//nav//a[@data-bs-target='#registerModal']")
        register_nav_link.click()

        register_modal = self.find_element_with_wait(By.ID, "registerModal")
        WebDriverWait(self.driver, 10).until(EC.visibility_of(register_modal))
        self.assertTrue(register_modal.is_displayed(), "Registration modal should be visible after clicking nav link.")
        self.find_element_with_wait(By.ID, "reg-username") 

    def test_03_successful_registration(self):
        """Test successful user registration."""
        self.driver.get(BASE_URL)
        self.click_element_with_wait(By.XPATH, "//nav//a[@data-bs-target='#registerModal']")

        username = f"testuser_{self.unique_timestamp}"
        email = f"test_{self.unique_timestamp}@example.com"
        password = "Password123!"

        self.find_element_with_wait(By.ID, "reg-username").send_keys(username)
        self.find_element_with_wait(By.ID, "reg-email").send_keys(email)
        self.find_element_with_wait(By.ID, "reg-password").send_keys(password)
        
        self.click_element_with_wait(By.XPATH, "//form[@id='registerForm']//input[@type='submit']")

        try:
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            self.assertIn("Registration successful! Please log in.", alert.text)
            alert.accept()
        except TimeoutException:
            self.fail("Alert not shown after registration.")

        login_modal = self.find_element_with_wait(By.ID, "loginModal")
        WebDriverWait(self.driver, 10).until(EC.visibility_of(login_modal))
        self.assertTrue(login_modal.is_displayed(), "Login modal should be visible after successful registration.")
        
    # def test_04_register_existing_username(self):
    #     """Test registration with an already existing username."""
    #     username = f"existinguser_{self.unique_timestamp}"
    #     email_unique_part = self.unique_timestamp
    #     initial_email = f"initial_{email_unique_part}@example.com"
    #     password = "Password123!"

    #     self.driver.get(BASE_URL)
    #     self.click_element_with_wait(By.XPATH, "//nav//a[@data-bs-target='#registerModal']")
    #     self.find_element_with_wait(By.ID, "reg-username").send_keys(username)
    #     self.find_element_with_wait(By.ID, "reg-email").send_keys(initial_email)
    #     self.find_element_with_wait(By.ID, "reg-password").send_keys(password)
    #     self.click_element_with_wait(By.XPATH, "//form[@id='registerForm']//input[@type='submit']")
    #     try:
    #         WebDriverWait(self.driver, 5).until(EC.alert_is_present())
    #         self.driver.switch_to.alert.accept()
    #     except TimeoutException:
    #         self.fail("Alert for successful registration did not appear for the first user.")
        
    #     WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "loginModal")))
    #     self.click_element_with_wait(By.XPATH, "//div[@id='loginModal']//button[@class='btn-close']")
    #     WebDriverWait(self.driver, 10).until_not(EC.visibility_of_element_located((By.ID, "loginModal")))

    #     self.click_element_with_wait(By.XPATH, "//nav//a[@data-bs-target='#registerModal']")
    #     WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "reg-username")))

    #     self.find_element_with_wait(By.ID, "reg-username").send_keys(username) 
    #     self.find_element_with_wait(By.ID, "reg-email").send_keys(f"new_{email_unique_part}@example.com") 
    #     self.find_element_with_wait(By.ID, "reg-password").send_keys(password)
    #     self.click_element_with_wait(By.XPATH, "//form[@id='registerForm']//input[@type='submit']")

    #     error_message_div = self.find_element_with_wait(By.ID, "username-error")
    #     WebDriverWait(self.driver, 10).until(lambda d: error_message_div.text != "")
    #     self.assertIn("Username already exists.", error_message_div.text)
        
    #     username_field = self.find_element_with_wait(By.ID, "reg-username")
    #     self.assertIn("is-invalid", username_field.get_attribute("class"))

    # def test_05_register_existing_email(self):
    #     """Test registration with an already existing email."""
    #     username_unique_part = self.unique_timestamp
    #     email = f"existing_email_{self.unique_timestamp}@example.com"
    #     password = "Password123!"

    #     self.driver.get(BASE_URL)
    #     self.click_element_with_wait(By.XPATH, "//nav//a[@data-bs-target='#registerModal']")
    #     self.find_element_with_wait(By.ID, "reg-username").send_keys(f"anotheruser_{username_unique_part}")
    #     self.find_element_with_wait(By.ID, "reg-email").send_keys(email)
    #     self.find_element_with_wait(By.ID, "reg-password").send_keys(password)
    #     self.click_element_with_wait(By.XPATH, "//form[@id='registerForm']//button[@type='submit']")
    #     try:
    #         WebDriverWait(self.driver, 5).until(EC.alert_is_present())
    #         self.driver.switch_to.alert.accept()
    #     except TimeoutException:
    #         self.fail("Alert for successful registration did not appear for the first user.")

    #     WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "loginModal")))
    #     self.click_element_with_wait(By.XPATH, "//div[@id='loginModal']//button[@class='btn-close']")
    #     WebDriverWait(self.driver, 10).until_not(EC.visibility_of_element_located((By.ID, "loginModal")))

    #     self.click_element_with_wait(By.XPATH, "//nav//a[@data-bs-target='#registerModal']")
    #     WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "reg-email")))

    #     self.find_element_with_wait(By.ID, "reg-username").send_keys(f"newuser_{username_unique_part}") 
    #     self.find_element_with_wait(By.ID, "reg-email").send_keys(email) 
    #     self.find_element_with_wait(By.ID, "reg-password").send_keys(password)
    #     self.click_element_with_wait(By.XPATH, "//form[@id='registerForm']//button[@type='submit']")

    #     error_message_div = self.find_element_with_wait(By.ID, "email-error")
    #     WebDriverWait(self.driver, 10).until(lambda d: error_message_div.text != "")
    #     self.assertIn("Email already exists.", error_message_div.text)

    #     email_field = self.find_element_with_wait(By.ID, "reg-email")
    #     self.assertIn("is-invalid", email_field.get_attribute("class"))

    def test_06_open_login_modal_from_nav(self):
        """Test opening the login modal from the navigation bar."""
        self.driver.get(BASE_URL)

        login_nav_link = self.find_element_with_wait(By.XPATH, "//nav//a[@data-bs-target='#loginModal']")
        login_nav_link.click()

        login_modal = self.find_element_with_wait(By.ID, "loginModal")
        WebDriverWait(self.driver, 10).until(EC.visibility_of(login_modal))
        self.assertTrue(login_modal.is_displayed(), "Login modal should be visible.")
        
        self.find_element_with_wait(By.ID, "username") 

if __name__ == "__main__":
    unittest.main(verbosity=2)