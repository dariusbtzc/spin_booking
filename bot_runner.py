import os
import time
import json
import logging
from booking_bot import is_time_to_book, login_to_website, click_book_now, select_session, select_seat

# Ensure the 'log' directory exists
if not os.path.exists('log'):
    os.makedirs('log')

# Set up logging
logging.basicConfig(filename = 'log/booking_bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the configuration from the JSON file
with open('config.json', 'r') as file:
    config = json.load(file)

MAX_TRIES = config['max_tries']

def main():
    if not is_time_to_book():
        logging.info("It's not the right time to book yet. Exiting.")
        return None

    for attempt in range(1, MAX_TRIES + 1):
        logging.info(f"Attempt {attempt} of {MAX_TRIES}...")

        # Start the booking process
        driver = login_to_website()

        if driver:  
            if click_book_now(driver):
                if select_session(driver):
                    result = select_seat(driver)
                    if "Successfully enrolled" in result:
                        logging.info("Booking successful!")
                        driver.quit()
                        return
                    else:
                        logging.warning(result)
            driver.quit()

        # Wait for a short duration before the next attempt
        time.sleep(10)  # Wait for 10 seconds

    logging.error("Reached maximum number of tries without success. Please try again later.")

if __name__ == "__main__":
    main()