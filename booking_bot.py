import os
import time
import json
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

logger = logging.getLogger()

# Load the configuration from the JSON file
with open('config.json', 'r') as file:
    config = json.load(file)


def is_time_to_book():
    '''
    Check if the current day and time match the booking criteria defined in the config.json file.

    Returns:
        bool: True if the current day and time are within the booking window, False otherwise.

    Configuration (from config.json):
        - booking_day: The day of the week for booking (e.g., "Monday").
        - booking_hour: The hour of the day for booking (e.g., 12 for 12PM).
        - booking_minute_start: The starting minute of the booking window (e.g., 0 for 12:00PM).
        - booking_minute_end: The ending minute of the booking window (e.g., 15 for 12:15PM).
    '''
    
    # Get the current date and time
    now = datetime.now()

    # Log the current day and time
    logger.info(f"Current day and time: {now.strftime('%A, %H:%M')}")

    # Check if today matches the booking day
    if now.strftime('%A') == config['booking_day']:

        # Check if the time is within the booking window
        if now.hour == config['booking_hour'] and config['booking_minute_start'] <= now.minute <= config['booking_minute_end']:
            logger.info("It's within the booking window!")
            return True
        else:
            logger.info("It's not the right time to book yet.")
            return False
        
    else:
        logger.info("Today is not the booking day.")
        return False


def login_to_website():
    '''
    Attempt to log in to the website using the credentials set in environment variables.

    Returns:
        driver (webdriver.Chrome): A Chrome browser session if the login is successful.
        None: If the login fails or if email / password are not set in environment variables.

    Environment Variables:
        - CRU_BOOKING_EMAIL: The email to use for logging in.
        - CRU_BOOKING_PASSWORD: The password to use for logging in.
    '''

    # Get email and password from environment variables
    email = os.environ.get('CRU_BOOKING_EMAIL')
    password = os.environ.get('CRU_BOOKING_PASSWORD')

    if not email or not password:
        logger.info("Error: Email or password not set in environment variables.")
        return None

    # Set Chrome options for headless mode (i.e., browser session not visible)
    OPTIONS = Options()
    OPTIONS.add_argument('--headless=new')

    # Start a new browser session with the options
    driver = webdriver.Chrome(service = ChromeService(ChromeDriverManager().install()), options = OPTIONS)

    # Navigate to the login URL
    driver.get(config['login_url'])

    try:
        # Switch to the iframe
        iframe_element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe_element)

        # Find the email and password input fields 
        email_input = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "username")))
        password_input = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "password")))

        # Input the email and password
        email_input.send_keys(email)
        password_input.send_keys(password)

        # Find the 'Sign In' button
        sign_in_button = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        sign_in_button.click()

        # Wait for a short duration to check for the error message
        time.sleep(3)  
        error_message = None

        try:
            error_message = driver.find_element(By.CLASS_NAME, "alert")
        except NoSuchElementException:
            pass

        if error_message and error_message.is_displayed():
            logger.info("Login failed: Incorrect username or password.")
            driver.quit()
            return None
        else:
            logger.info("Login successful!")
            driver.switch_to.default_content()
            return driver

    except (NoSuchElementException, TimeoutException) as e:
        logger.info(f"Error during login: {e}")
        driver.quit()
        return None


def click_book_now(driver):
    '''
    Hover over the 'Book Now' drop-down menu and select the desired location.

    Parameters:
        driver (webdriver.Chrome): The active Chrome browser session.

    Returns:
        bool: True if the desired location is successfully selected, False otherwise.
    '''

    try:
        # Locate the 'Book Now' drop-down menu
        book_now_dropdown = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, "book-now")))

        # Hover over the 'Book Now' drop-down menu
        hover = ActionChains(driver).move_to_element(book_now_dropdown)
        hover.perform()

        # Click the desired location from the drop-down menu
        desired_location = config['desired_location']
        location = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.LINK_TEXT, desired_location)))
        location.click()

        logger.info(f"Clicked 'Book Now' > {desired_location}!")
        return True
    
    except (NoSuchElementException, TimeoutException) as e:
        logger.info(f"Error selecting location from 'Book Now' drop-down: {e}")
        return False


def select_session(driver):
    '''
    Select the specified session based on the desired session information.

    Parameters:
        driver (webdriver.Chrome): The active Chrome browser session.

    Returns:
        bool: True if the desired session is successfully selected, False otherwise.
    '''

    try:
        # Switch to the iframe
        iframe_element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe_element)

        # Locate the desired session day
        desired_session_day = config['desired_session']['day']
        session_day = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, desired_session_day)))
        session_day_class_attribute = session_day.get_attribute('class')
        logger.info(f"Located desired session day: {session_day_class_attribute}!")

        # Locate the desired instructor (via data-instructor)
        desired_session_data_instructor = config['desired_session']['data_instructor']
        session_day_data_instructor = WebDriverWait(session_day, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, f"div[data-instructor = '{desired_session_data_instructor}']")))
        session_day_data_instructor_text = session_day_data_instructor.text
        logger.info(f"Session data instructor element:\n{session_day_data_instructor_text}")

        # Confirm and click on the desired session activity
        desired_session_activity = config['desired_session']['activity']
        desired_session_instructor = config['desired_session']['instructor']

        if (desired_session_activity in session_day_data_instructor_text) and (desired_session_instructor in session_day_data_instructor_text):
            session_day_activity = WebDriverWait(session_day_data_instructor, 3).until(EC.element_to_be_clickable((By.TAG_NAME, "a")))
            driver.execute_script("arguments[0].scrollIntoView();", session_day_activity)   # Scroll the element into view
            session_day_activity.click()
            
            logger.info(f"Clicked on '{desired_session_activity}, {desired_session_instructor}'!")
            driver.switch_to.default_content()
            return True
        else:
            logger.info("Unable to find the correct activity and/or instructor.")
            return False
    
    except (NoSuchElementException, TimeoutException) as e:
        logger.info(f"Error selecting session: {e}")
        return False
    

def select_bike(driver, desired_bike):
    '''
    Select the desired bike for the session.

    Parameters:
        driver (webdriver.Chrome): The active Chrome browser session.

    Returns:
        str: A message indicating the outcome of the bike selection.
    '''

    try:
        # Switch to the iframe
        iframe_element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe_element)

        # Locate and click the desired bike
        bike = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.LINK_TEXT, desired_bike)))
        bike.click()

        # Wait for a short duration to check for the outcome message
        time.sleep(3)  

        no_series_msg_element = None

        try:
            no_series_msg_element = driver.find_element(By.CSS_SELECTOR, "a[data-dismiss = 'alert']")
        except NoSuchElementException:
            pass

        if no_series_msg_element:
            return "You don't have a series in your account that's applicable for this class."
        else:
            pass

        success_msg_element = None

        try:
            success_msg_element = driver.find_element(By.CLASS_NAME, "success-message")
        except NoSuchElementException:
            pass
        
        try:
            if success_msg_element and success_msg_element.is_displayed():
                return success_msg_element.text
        except TimeoutException:
            return "Unknown outcome after seat selection."

    except (NoSuchElementException, TimeoutException) as e:
        return f"Error during seat selection: {e}"