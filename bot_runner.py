import os
import time
import json
import logging
from booking_bot import BookingBot

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

def main():
    bot = BookingBot(config)

    time_check_limit = config['time_check_limit']
    time_check_count = 0

    while not bot.is_time_to_book():  
        logging.info("Waiting for the right time to book...")
        time.sleep(60)  

        time_check_count += 1  

        if time_check_count >= time_check_limit:
            logging.info("Reached the limit for time checks. Exiting.")
            return None
    
    bot.run()

if __name__ == "__main__":
    main()