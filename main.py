import requests
from bs4 import BeautifulSoup
import json
import os

# Define the JSON file to store event titles
EVENTS_JSON_FILE = "events.json"
LINE_NOTIFY_API_URL = "https://notify-api.line.me/api/notify"
ACCESS_TOKEN = os.getenv("LINE_NOTIFY_ACCESS_TOKEN")

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

def send_line_notification(message):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    data = {"message": message}
    response = requests.post(LINE_NOTIFY_API_URL, headers=headers, data=data)

    if response.status_code == 200:
        print("Notification sent successfully.")
    else:
        print(f"Failed to send notification. Status code: {response.status_code}, Response: {response.text}")

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

    # Send new events to LINE Notify
    if new_events:
        print("New events found:")
        for event in new_events:
            print(event)

        # Create a single message with all the new events
        message = "<<New Events Found:>>\n" + "\n".join(new_events)

        # Send the message to LINE Notify
        send_line_notification(message)

        # Update the stored events to include the new ones
        updated_events = stored_events + new_events
        save_events_to_json(updated_events)

        print(f"Updated JSON file with {len(new_events)} new events.")
    else:
        print("No new events.")

    # Update the stored events with current ones (in case there were changes)
    save_events_to_json(current_events)

if __name__ == "__main__":
    main()