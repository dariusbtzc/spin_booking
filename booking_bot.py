import os
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

class BookingBot:

    def __init__(self, config, logger = None):
        '''
        Initialise the BookingBot with the given configuration.

        Parameters:
            config (dict): Configuration settings loaded from a JSON file.
            logger (logging.Logger, optional): Logger object for logging events. Defaults to the root logger.
        '''

        self.config = config
        self.logger = logger or logging.getLogger()
        self.driver = None
        self.lag = config['default_lag']


    def is_time_to_book(self):
        '''
        Check if the current day and time match the booking criteria defined in the config.json file.
        Logs the current day and time and whether it's the right time to book.

        Returns:
            bool: True if the current day and time are within the booking window, False otherwise.
        '''
        
        # Get the current date and time
        now = datetime.now()

        # Log the current day and time
        self.logger.info(f"Current day and time: {now.strftime('%A, %H:%M')}")

        # Check if today matches the booking day
        if now.strftime('%A') == self.config['booking_day']:

            # Check if the time is within the booking window
            if now.hour == self.config['booking_hour'] and self.config['booking_minute_start'] <= now.minute <= self.config['booking_minute_end']:
                self.logger.info("It's within the booking window!")
                return True
            else:
                self.logger.info("It's not the right time to book yet.")
                return False
            
        else:
            self.logger.info("Today is not the booking day.")
            return False


    def start_driver(self):
        '''
        Initialise the Selenium WebDriver with Chrome as the browser.
        Logs the start event.

        Returns:
            None
        '''
        
        OPTIONS = Options()
        # OPTIONS.add_argument('--headless=new')  # headless: browser session not visible
        self.driver = webdriver.Chrome(service = ChromeService(ChromeDriverManager().install()), options = OPTIONS)
        self.logger.info("Started the Chrome driver.")


    def stop_driver(self):
        '''
        Terminate the Selenium WebDriver session.
        Closes the browser window and releases the resources.
        Logs the stop event.

        Returns:
            None
        '''
        
        if self.driver:
            self.driver.quit()
            self.driver = None
        self.logger.info("Stopped the Chrome driver.")


    def login_to_website(self):
        '''
        Attempt to log in to the website using the credentials set in environment variables.
        This method will start the driver if it's not already started.

        Returns:
            bool: True if the login is successful, False otherwise.

        Environment Variables:
            - CRU_BOOKING_EMAIL: The email to use for self.logger in.
            - CRU_BOOKING_PASSWORD: The password to use for self.logger in.
        '''

        if not self.driver:
            self.start_driver()

        # Navigate to the login URL
        self.driver.get(self.config['login_url'])

        try:
            # Get email and password from environment variables
            email = os.environ.get('CRU_BOOKING_EMAIL')
            password = os.environ.get('CRU_BOOKING_PASSWORD')

            if not email or not password:
                self.logger.info("Error: Email or password not set in environment variables.")
                return False
        except Exception as e:
            self.logger.error(f"Error reading environment variables: {e}")
            return False

        try:
            # Switch to the iframe
            iframe_element = WebDriverWait(self.driver, self.lag).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
            self.driver.switch_to.frame(iframe_element)

            # Find the email and password input fields 
            email_input = WebDriverWait(self.driver, self.lag).until(EC.presence_of_element_located((By.ID, "username")))
            password_input = WebDriverWait(self.driver, self.lag).until(EC.presence_of_element_located((By.ID, "password")))

            # Input the email and password
            email_input.send_keys(email)
            password_input.send_keys(password)

            # Click the 'Sign In' button
            sign_in_button = WebDriverWait(self.driver, self.lag).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
            sign_in_button.click()

            # Wait for a short duration to check for the error message
            time.sleep(self.lag)  
            
            try:
                error_message = self.driver.find_element(By.CLASS_NAME, "alert")
                if error_message.is_displayed():
                    self.logger.info("Login failed: Incorrect username or password.")
                    return False
            except (NoSuchElementException, TimeoutException):
                self.logger.info("Login successful!")
                self.driver.switch_to.default_content()
                return True

        except (NoSuchElementException, TimeoutException) as e:
            self.logger.info(f"Error during login: {e}")
            return False


    def click_book_now(self):
        '''
        Hover over the 'Book Now' drop-down menu and select the desired location.

        Returns:
            bool: True if the desired location is successfully selected, False otherwise.
        '''

        try:
            # Locate the 'Book Now' drop-down menu
            book_now_dropdown = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.ID, "book-now")))

            # Hover over the 'Book Now' drop-down menu
            hover = ActionChains(self.driver).move_to_element(book_now_dropdown)
            hover.perform()

            # Click the desired location from the drop-down menu
            desired_location = self.config['desired_location']
            location = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.LINK_TEXT, desired_location)))
            location.click()

            self.logger.info(f"Clicked 'Book Now' > {desired_location}!")
            return True
        
        except (NoSuchElementException, TimeoutException) as e:
            self.logger.info(f"Error selecting location from 'Book Now' drop-down: {e}")
            return False


    def select_session(self):
        '''
        Select the specified session based on the desired session information.
        This method can handle multiple sessions by the same instructor on the same day.
        Note, this method also clicks the "NEXT WEEK" button to navigate to the sessions for the following week.

        Returns:
            bool: True if the desired session is successfully selected, False otherwise.
        '''

        try:
            # Switch to the iframe
            iframe_element = WebDriverWait(self.driver, self.lag).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
            self.driver.switch_to.frame(iframe_element)

            # Click "NEXT WEEK" button
            next_week_button = WebDriverWait(self.driver, self.lag).until(EC.presence_of_element_located((By.CLASS_NAME, "next")))
            next_week_link = WebDriverWait(next_week_button, self.lag).until(EC.element_to_be_clickable((By.TAG_NAME, "a")))
            self.driver.execute_script("arguments[0].scrollIntoView();", next_week_link)  # Scroll the element into view
            next_week_link.click()
            self.logger.info(f"Click 'NEXT WEEK' button!")

            # Locate the desired session day
            desired_session_day = self.config['desired_session']['day']
            session_day = WebDriverWait(self.driver, self.lag).until(EC.presence_of_element_located((By.CLASS_NAME, desired_session_day)))
            session_day_class_attribute = session_day.get_attribute('class')
            self.logger.info(f"Located desired session day: {session_day_class_attribute}!")

            # Locate the desired instructor (via data-instructor)
            # Note: An instructor can have multiple sessions in a day
            desired_session_data_instructor = self.config['desired_session']['data_instructor']
            all_sessions_day_data_instructor = WebDriverWait(session_day, self.lag).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, f"div[data-instructor = '{desired_session_data_instructor}']")))

            # Locate, confirm and click on the desired session activity
            desired_session_activity = self.config['desired_session']['activity']
            desired_session_instructor = self.config['desired_session']['instructor']
            desired_session_time = self.config['desired_session']['time']

            for session in all_sessions_day_data_instructor:
                session_text = session.text
                if (desired_session_activity in session_text) and (desired_session_instructor in session_text) and (desired_session_time in session_text):
                    session_day_activity = WebDriverWait(session, self.lag).until(EC.element_to_be_clickable((By.TAG_NAME, "a")))
                    self.driver.execute_script("arguments[0].scrollIntoView();", session_day_activity)   # Scroll the element into view
                    session_day_activity.click()
                    
                    self.logger.info(f"Clicked on:\n{session_text}")
                    self.driver.switch_to.default_content()
                    return True
            
            self.logger.info("Unable to find the correct activity and/or instructor.")
            return False
        
        except (NoSuchElementException, TimeoutException) as e:
            self.logger.info(f"Error selecting session: {e}")
            return False
    

    def select_bike(self, desired_bike):
        '''
        Select the desired bike for the session.

        Parameters:
            desired_bike (str): The bike to be selected.

        Returns:
            str: A message indicating the outcome of the bike selection. This could be one of the following:
                - A success message if the bike is successfully booked.
                - An error message if there was an issue during the booking.
                - A message indicating that the user doesn't have a series in their account that's applicable for this class.
        '''

        try:
            # Switch to the iframe
            iframe_element = WebDriverWait(self.driver, self.lag).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
            self.driver.switch_to.frame(iframe_element)

            # Locate and click the desired bike
            bike = WebDriverWait(self.driver, self.lag).until(EC.element_to_be_clickable((By.LINK_TEXT, desired_bike)))
            bike.click()

            # Wait for a short duration to check for the outcome message
            time.sleep(self.lag)  

            try:
                no_series_msg_element = self.driver.find_element(By.CSS_SELECTOR, "a[data-dismiss = 'alert']")
                if no_series_msg_element.is_displayed():
                    return "You don't have a series in your account that's applicable for this class."
            except (NoSuchElementException, TimeoutException):
                pass

            try:
                success_msg_element = self.driver.find_element(By.CLASS_NAME, "success-message")
                if success_msg_element.is_displayed():
                    return success_msg_element.text
            except (NoSuchElementException, TimeoutException):
                return "Unknown outcome after seat selection."

        except (NoSuchElementException, TimeoutException) as e:
            return f"Error during seat selection: {e}"
        
    
    def run(self, desired_bike):
        '''
        Main function to execute the booking process.
        
        This function will attempt to the book desired bike based on the configuration settings.
        Each bike booking will go through a series of steps: login, select location, select session and select bike.
        Each bike booking will be attempted for a maximum number of tries as specified in the configuration.
        The function also checks if it's the right time to book based on the configuration settings.
        Logs each attempt and the outcome.

        Parameters:
            desired_bike (str): The bike to be selected.

        Returns:
            None
        '''

        # time_check_limit = self.config['time_check_limit']
        # time_check_count = 0

        # while not self.is_time_to_book():  
        #     self.logger.info("Waiting for the right time to book...")
        #     time.sleep(60)  

        #     time_check_count += 1  

        #     if time_check_count >= time_check_limit:
        #         self.logger.info("Reached the limit for time checks. Exiting.")
        #         return None

        max_tries = self.config['max_tries']
        booking_successful = False

        for attempt in range(1, max_tries + 1):
            self.logger.info(f"Attempt {attempt} of {max_tries} for bike {desired_bike}...")

            try:
                if self.login_to_website():
                    if self.click_book_now():
                        if self.select_session():
                            result = self.select_bike(desired_bike)
                            if "successfully enrolled" in result:
                                self.logger.info(f"Booking successful for bike {desired_bike}!")
                                booking_successful = True
                                break
                            else:
                                self.logger.info(result)
            finally:
                self.stop_driver()

            # Wait for a short duration before the next attempt
            time.sleep(self.lag)
        
        if not booking_successful:
            self.logger.error(f"Maximum number of tries without success reached for bike {desired_bike}. Please try again later.")