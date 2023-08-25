## Overview
Scripts for automating bookings on Cru.

## Booking details
- Booking configurations can be found in `config.json`.
- The main execution script is `bot_runner.py`, which utilises functions from `booking_bot.py`.

### Booking steps:
1. Verify if the current day and time fall within the desired booking window.
2. Log into the booking site.
3. Upon successful login:
    1. Hover over the 'Book Now' drop-down menu and select the desired location.
    2. Choose the desired session.
    3. Pick the preferred seat.

## CRON instructions
1. Install the required packages: `pip install -r requirements.txt`
2. Open the CRON editor using the command: `crontab -e`.
3. Add a CRON job by appending: `0 12 * * 1 /path/to/your/python3/path/to/your/bot_runner.py`
    - This configuration schedules the script to run every Monday at 12:00PM.
    - Replace `/path/to/your/python3` with the path to your Python3 interpreter and `/path/to/your/` with the actual path to your `bot_runner.py`.
