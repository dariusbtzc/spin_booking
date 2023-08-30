## Overview
Scripts for automating bookings on [Cru](https://www.cru68.com/).

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
1. Install the required packages (if you haven't already): `pip install -r requirements.txt`
2. Open the CRON editor using the command: `crontab -e`.
3. Add a CRON job by appending: `0 12 * * 1 export CRU_BOOKING_EMAIL='your_email'; export CRU_BOOKING_PASSWORD='your_password'; /path/to/your/python3 /path/to/your/bot_runner.py`
    - This configuration schedules the script to run every Monday at 12:00PM.
    - Make sure to replace `your_email` and `your_password` with the actual email and password. 
    - Also, replace `/path/to/your/python3` with the actual path to your Python3 interpreter and `/path/to/your/bot_runner.py` with the path to your `bot_runner.py` script.

**Note**: The local computer needs to be switched on for the CRON job to run.