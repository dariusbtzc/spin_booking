## Overview
Scripts for automating bookings on [Cru](https://www.cru68.com/). The scripts are designed to run on a schedule and will attempt to book bikes based on the configuration settings specified in `config.json`.

## Requirements
- Python 3.8.8
- Compatible with macOS and Linux
- Environment variables for login credentials

## Booking details
- Booking configurations can be found in `config.json`.
- The main execution script is `bot_runner.py`, which utilises the `BookingBot` class from `booking_bot.py` to perform the booking steps.

### Booking steps:
1. Continuously check if the current day and time fall within the desired booking window.
2. Log into the booking site using environment variables for credentials.
3. Upon successful login:
    1. Hover over the 'Book Now' drop-down menu and select the desired location.
    2. Navigate to the desired session and select it.
    3. Pick the preferred seat (bike).

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

## Logging 
- Logs are saved in the `logs/` directory.
- Each log file is timestamped and includes the name of the desired bike for easy identification.