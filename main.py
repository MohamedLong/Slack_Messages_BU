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
    data = response.json()
    if data.get('ok'):
        return data.get('channels', [])
    else:
        print("Error:", data.get('error'))
        return []

def fetch_messages(channel_id, latest=None):
    params = {
        'channel': channel_id,
        'limit': 1000,
        'latest': latest
    }
    messages = []
    while True:
        response = requests.get(history_url, headers=headers, params=params)
        data = response.json()
        if data.get('ok'):
            messages.extend(data.get('messages', []))
            if data.get('response_metadata') and data['response_metadata'].get('next_cursor'):
                params['cursor'] = data['response_metadata']['next_cursor']
                time.sleep(1)
            else:
                break
        else:
            print("Error fetching messages:", data.get('error'))
            break
    return messages

def save_backup(channel_name, messages):
    filename = f"BU/{channel_name}.json"
    existing_messages = []
    
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            existing_messages = json.load(f)
    
    existing_messages_dict = {msg['ts']: msg for msg in existing_messages}
    existing_timestamps = sorted(existing_messages_dict.keys())
    
    # Create a dictionary of new messages indexed by timestamp
    new_messages_dict = {msg['ts']: msg for msg in messages}
    
    # Merge existing and new messages while preserving order
    all_timestamps = sorted(set(existing_timestamps) | set(new_messages_dict.keys()))
    all_messages = [existing_messages_dict.get(ts, new_messages_dict.get(ts)) for ts in all_timestamps]
    
    with open(filename, 'w') as f:
        json.dump(all_messages, f, indent=2)
    print(f"Backup updated in {filename}")

def main():
    channels = fetch_channels()
    for channel in channels:
        channel_id = channel['id']
        channel_name = channel['name']
        print(f"Fetching messages for channel: {channel_name} ({channel_id})")
        
        # Fetch the latest messages
        messages = fetch_messages(channel_id)
        
        # Save backup
        save_backup(channel_name, messages)

if __name__ == "__main__":
    main()
