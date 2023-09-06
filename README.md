## Overview
Scripts for automating bookings on [Cru](https://www.cru68.com/).

## Requirements
- Python 3.x
- Compatible with macOS and Linux

## Booking details
- Booking configurations can be found in `config.json`.
- The main execution script is `bot_runner.py`, which utilises functions from `booking_bot.py`.

### Booking steps:
1. Verify if the current day and time fall within the desired booking window.
2. Log into the booking site using environment variables for credentials.
3. Upon successful login:
    1. Hover over the 'Book Now' drop-down menu and select the desired location.
    2. Choose the desired session.
    3. Pick the preferred seat.

## Dependencies
- Selenium
- WebDriver Manager

Run `pip install -r requirements.txt` to install the required packages.

## CRON instructions
1. Open the CRON editor using the command: `crontab -e`
2. Add a CRON job by appending: `0 12 * * 1 cd /path/to/your/bot_folder && export CRU_BOOKING_EMAIL='your_email' && export CRU_BOOKING_PASSWORD='your_password' && /path/to/your/python bot_runner.py`
    - This configuration schedules the script to run every Monday at 12:00PM.
    - Replace `/path/to/your/bot_folder` with the path to the folder where you store the `bot_runner.py` script.
    - Replace `your_email` and `your_password` with the actual email and password. 
    - Replace `/path/to/your/python` with the actual path to your Python interpreter.

**Note**: The local computer must be switched on for the CRON job to run.