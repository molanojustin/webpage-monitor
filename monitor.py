import requests
import time
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Configuration
SOURCE_URL = os.getenv('SOURCE_URL') 
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 60))  # Interval in seconds between checks, default to 60 if not set

# Pushover settings
PUSHOVER_TOKEN = os.getenv('PUSHOVER_TOKEN')  # Replace with your Pushover API token
PUSHOVER_USER = os.getenv('PUSHOVER_USER')    # Replace with your Pushover user key

def send_push_notification(message):
    """Send a push notification using Pushover."""
    url = 'https://api.pushover.net/1/messages.json'
    data = {
        'token': PUSHOVER_TOKEN,
        'user': PUSHOVER_USER,
        'message': message,
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        print("Push notification sent!")
    except Exception as e:
        print("Failed to send push notification:", e)

def get_page_hash(url):
    """Fetch the webpage and return its MD5 hash."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        page_content = response.text
        return hashlib.md5(page_content.encode('utf-8')).hexdigest()
    except Exception as e:
        print("Error fetching page:", e)
        return None

def main(debug=False, pulseCheck=False):
    # Initialize the counter
    counter = 0

    last_hash = get_page_hash(SOURCE_URL)
    if last_hash is None:
        print("Initial fetch failed. Exiting.")
        return

    while True:
        time.sleep(CHECK_INTERVAL)
        current_hash = get_page_hash(SOURCE_URL)
        if current_hash is None:
            continue  # Skip this iteration if there was an error
        if current_hash != last_hash:
            domain = SOURCE_URL.split("www.")[-1].split(".com")[0] + ".com"
            send_push_notification(f"The webpage at {domain} has been updated.")
            last_hash = current_hash
            break  # Exit the loop after sending the notification
        else:
            # If no update, increment the counter
            counter += 1
            if pulseCheck:

                # Sends a notification every 300 checks (50 minutes if CHECK_INTERVAL is 10 seconds)
                if counter % 300 == 0:
                    send_push_notification(f"Still monitoring the webpage for updates. {counter} checks made.")
                    continue
                
                # Print a message every 10 checks (100 seconds if CHECK_INTERVAL is 10 seconds)
                if counter % 10 == 0:
                    print(f'Checked {counter} times. No update detected.')
                    continue
            elif debug:
                print(f'Search no.: {counter}. Current hash: {current_hash}, Last hash: {last_hash}')
                continue
            print("No update detected.")

if __name__ == '__main__':
    main()