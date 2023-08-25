import os
import json
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException

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
        webdriver.Chrome: A Chrome browser session if the login is successful.
        None: If the login fails or if email/password are not set in environment variables.

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

    # Set Chrome options for headless mode
    OPTIONS = webdriver.ChromeOptions()
    OPTIONS.headless = True

    # Start a new browser session with the options
    driver = webdriver.Chrome(options = OPTIONS)

    # Navigate to the login URL
    driver.get(config['login_url'])

    try:
        # Find the email and password input fields using the placeholder text
        email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Email']")))
        password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']")))

        # Input the email and password
        email_input.send_keys(email)
        password_input.send_keys(password)

        # Find the 'Sign In' button by its text and click it
        sign_in_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[text()='Sign In']")))
        sign_in_button.click()

        # Wait for a short duration to allow the page to process the login and display any error messages
        error_message = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Sorry, that username/password was not recognized.')]")))
        
        if error_message:
            logger.info("Login failed: Incorrect username or password.")
            driver.quit()   # Close the browser session
            return None

    except (NoSuchElementException, TimeoutException) as e:
        logger.info(f"Error during login: {e}")
        driver.quit()
        return None

    # If no error message is found, the login is assumed to be successful
    logger.info("Login successful!")

    # Return the driver in case you want to perform more actions in the same session
    return driver


def click_book_now(driver):
    '''
    Hover over the 'Book Now' drop-down menu and then select the desired location.

    Parameters:
        driver (webdriver.Chrome): The active Chrome browser session.

    Returns:
        bool: True if the desired location is successfully selected, False otherwise.
    '''

    try:
        # Locate the 'Book Now' drop-down menu
        book_now_dropdown = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[text()='Book Now']")))
        
        # Hover over the 'Book Now' drop-down menu
        hover = ActionChains(driver).move_to_element(book_now_dropdown)
        hover.perform()

        # Select the desired location from the drop-down menu
        desired_location = config['desired_location']
        location_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//*[text()='{desired_location}']")))
        location_element.click()

        return True
    
    except (NoSuchElementException, TimeoutException) as e:
        logger.info(f"Error selecting location from 'Book Now' dropdown: {e}")
        return False


def select_session(driver):
    '''
    Select the specified session/timing based on the detailed session information.

    Parameters:
        driver (webdriver.Chrome): The active Chrome browser session.

    Returns:
        bool: True if the desired session is successfully selected, False otherwise.
    '''

    try:
        # Break down the XPath construction for readability
        location_xpath = f"//*[text()='{config['desired_session']['location']}']"
        instructor_xpath = f"./following-sibling::*[text()='{config['desired_session']['instructor']}'][1]"
        time_xpath = f"./following-sibling::*[text()='{config['desired_session']['time']}'][1]"
        duration_xpath = f"./following-sibling::*[text()='{config['desired_session']['duration']}'][1]"

        # Combine the individual XPaths to form the complete XPath expression
        session_xpath = f"{location_xpath}{instructor_xpath}{time_xpath}{duration_xpath}"
        
        # Click on the session to select it
        session_timing = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, session_xpath)))
        session_timing.click()
        return True
    
    except (NoSuchElementException, TimeoutException) as e:
        logger.info(f"Error selecting session: {e}")
        return False
    

def select_seat(driver):
    '''
    Select the desired seat for the session.

    Parameters:
        driver (webdriver.Chrome): The active Chrome browser session.

    Returns:
        str: A message indicating the outcome of the seat selection.
    '''

    desired_seat = config['desired_seat']

    try:
        # Locate the seat element
        seat_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//*[text()='{desired_seat}']")))

        # Check if the seat is available (not grey)
        seat_color = seat_element.value_of_css_property("color")
        if "rgb(" in seat_color:   
            return "Seat is already booked."

        # Click on the seat
        seat_element.click()

        # Check for the outcome messages
        no_series_message = "You don't have a series in your account that's applicable for this class."
        success_message = "You have been successfully enrolled in the class highlighted below."

        try:
            if WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{no_series_message}')]"))):
                return "No applicable series in account."
        except TimeoutException:
            pass

        try:
            if WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{success_message}')]"))):
                return "Successfully enrolled in the class."
        except TimeoutException:
            return "Unknown outcome after seat selection."

    except (NoSuchElementException, TimeoutException) as e:
        return f"Error during seat selection: {e}"