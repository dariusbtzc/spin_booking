import os
import time
import json
import logging
from booking_bot import BookingBot
from concurrent.futures import ThreadPoolExecutor

# Ensure the 'logs' directory exists
if not os.path.exists('logs'):
    os.makedirs('logs')

# Load the configuration from the JSON file
with open('config.json', 'r') as file:
    config = json.load(file)

 
def book_bike(desired_bike):
    '''
    Function to book a specific bike using the BookingBot class.
    Sets up logging and initiates the booking process for the given bike.

    Parameters:
        desired_bike (str): The bike to be selected.

    Returns:
        None
    '''

    # Get the current timestamp
    current_timestamp = time.strftime("%Y%m%d_%H%M%S")

    log_filename = f'logs/booking_bot_{desired_bike}_{current_timestamp}.log'
    
    # Create a new logger
    logger = logging.getLogger(desired_bike)
    logger.setLevel(logging.INFO)
    
    # Create a file handler
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.INFO)
    
    # Create a formatter and set the formatter for the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Add the handler to the logger
    logger.addHandler(file_handler)

    # Run bike booking bot
    bot = BookingBot(config, logger)
    bot.run(desired_bike)


def main():
    '''
    Main function to initiate the booking process for each desired bike.
    Creates a thread pool and runs the booking process for each bike in parallel.

    Returns:
        None
    '''

    desired_bikes = config['desired_bikes']

    with ThreadPoolExecutor() as executor:
        executor.map(book_bike, desired_bikes)


if __name__ == "__main__":
    main()