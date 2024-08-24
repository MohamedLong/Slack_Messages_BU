import os
import requests
import json
import time

# Get the Slack token from the environment variable
slack_token = os.getenv('SLACK_TOKEN')
if not slack_token:
    raise ValueError("SLACK_TOKEN environment variable not set")

list_url = 'https://slack.com/api/conversations.list'
history_url = 'https://slack.com/api/conversations.history'
headers = {
    'Authorization': f'Bearer {slack_token}',
    'Content-Type': 'application/json',
}

def fetch_channels():
    response = requests.get(list_url, headers=headers)
    print("Response status code:", response.status_code)  # Debugging line

    data = response.json()
    print("Response data:", data)  # Debugging line

    if data.get('ok'):
        return data.get('channels', [])
    else:
        print("Error:", data.get('error'))
        return []

def fetch_messages(channel_id):
    params = {
        'channel': channel_id,
        'limit': 1000,  # Adjust as needed
    }
    messages = []
    while True:
        response = requests.get(history_url, headers=headers, params=params)
        data = response.json()
        if data.get('ok'):
            messages.extend(data.get('messages', []))
            # Check if there's more messages to fetch
            if data.get('response_metadata') and data['response_metadata'].get('next_cursor'):
                params['cursor'] = data['response_metadata']['next_cursor']
                time.sleep(1)  # To handle rate limits
            else:
                break
        else:
            print("Error fetching messages:", data.get('error'))
            break
    return messages

def save_backup(channel_name, messages):
    filename = f"BU/{channel_name}.json"
    with open(filename, 'w') as f:
        json.dump(messages, f, indent=2)
    print(f"Backup saved to {filename}")

def main():
    channels = fetch_channels()
    for channel in channels:
        channel_id = channel['id']
        channel_name = channel['name']
        print(f"Fetching messages for channel: {channel_name} ({channel_id})")
        messages = fetch_messages(channel_id)
        save_backup(channel_name, messages)

if __name__ == "__main__":
    main()
