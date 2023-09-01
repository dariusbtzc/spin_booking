import os
import time
import json
import logging
from booking_bot import is_time_to_book, login_to_website, click_book_now, select_session, select_bike

# Ensure the 'logs' directory exists
if not os.path.exists('logs'):
    os.makedirs('logs')

# Get the current timestamp
current_timestamp = time.strftime("%Y%m%d_%H%M%S")

# Set up logging with a timestamped filename
logging.basicConfig(filename = f'logs/booking_bot_{current_timestamp}.log', level = logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s')

# Load the configuration from the JSON file
with open('config.json', 'r') as file:
    config = json.load(file)

MAX_TRIES = config['max_tries']

def main():
    time_check_limit = config['time_check_limit']
    time_check_count = 0

    while not is_time_to_book():  
        logging.info("Not time to book yet. Waiting...")
        time.sleep(60)  

        time_check_count += 1  

        if time_check_count >= time_check_limit:
            logging.info("Reached the limit for time checks. Exiting.")
            return None
    
    # Load the list of desired bikes
    desired_bikes = config['desired_bikes']

    for desired_bike in desired_bikes:
        booking_successful = False

        for attempt in range(1, MAX_TRIES + 1):
            logging.info(f"Attempt {attempt} of {MAX_TRIES} for bike {desired_bike}...")

            try:
                # Start the booking process
                driver = login_to_website()
            except Exception as e:
                logging.error(f"Error during login: {e}")
                continue

            if driver:  
                if click_book_now(driver):
                    if select_session(driver):
                        result = select_bike(driver, desired_bike)
                        if "successfully enrolled" in result:
                            logging.info(f"Booking successful for bike {desired_bike}!")
                            driver.quit()
                            booking_successful = True
                            break 
                        else:
                            logging.info(result)
                driver.quit()

            # Wait for a short duration before the next attempt
            time.sleep(3)   # Wait for 3 seconds

        if not booking_successful:
            logging.error(f"Maximum number of tries without success reached for bike {desired_bike}. Please try again later.")

if __name__ == "__main__":
    main()