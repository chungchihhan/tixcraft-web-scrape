import requests
from bs4 import BeautifulSoup
import json
import os

# Define the JSON file to store event titles
EVENTS_JSON_FILE = "events.json"
LINE_MESSAGING_API_URL = "https://api.line.me/v2/bot/message/push"

# Access tokens and user ID from the environment variables
ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
USER_ID = os.getenv("LINE_USER_ID")

def fetch_events():
    # Send a request to the website
    url = "https://tixcraft.com/activity"
    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to fetch the website")
        return []

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract event titles
    event_elements = soup.select(".data")
    events = []

    # Iterate over the selected elements and extract the date and title
    for event_element in event_elements:
        date = event_element.find('div', class_='date').text.strip() if event_element.find('div', class_='date') else 'No Date'
        title = event_element.find('div', class_='multi_ellipsis').text.strip() if event_element.find('div', class_='multi_ellipsis') else 'No Title'
        
        # Combine date and title into a string and add to the events list
        events.append(f"{date}: {title}")

    unique_events = list(set(events))
    return unique_events

def load_stored_events():
    if os.path.exists(EVENTS_JSON_FILE):
        with open(EVENTS_JSON_FILE, "r") as file:
            return json.load(file)
    return []

def save_events_to_json(events):
    with open(EVENTS_JSON_FILE, "w") as file:
        json.dump(events, file, indent=4)

def send_line_message(message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    data = {
        "to": USER_ID,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    response = requests.post(LINE_MESSAGING_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        print("Message sent successfully.")
    else:
        print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")

def main():
    # Fetch current events from the website
    current_events = fetch_events()

    if not current_events:
        print("No events found.")
        return

    # Load the stored events from the previous run
    stored_events = load_stored_events()

    # Find new events that are not in the stored events
    new_events = [event for event in current_events if event not in stored_events]

    # Send new events to LINE Messaging API
    if new_events:
        print("New events found:")
        for event in new_events:
            print(event)

        # Create a single message with all the new events
        message = "\n".join(new_events)

        # Send the message to LINE Messaging API
        send_line_message(message)

        # Update the stored events to include the new ones
        updated_events = stored_events + new_events
        save_events_to_json(updated_events)

        print(f"Updated JSON file with {len(new_events)} new events.")
    else:
        # send_line_message("No new events.")
        print("No new events.")

    # Update the stored events with current ones (in case there were changes)
    save_events_to_json(current_events)

if __name__ == "__main__":
    main()