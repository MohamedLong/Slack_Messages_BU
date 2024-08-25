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
            if data.get('response_metadata') and data['response_metadata'].get('next_cursor'):
                params['cursor'] = data['response_metadata']['next_cursor']
                time.sleep(1)  # To handle rate limits
            else:
                break
        else:
            print("Error fetching messages:", data.get('error'))
            break
    return messages

def fetch_existing_messages(channel_name):
    channel_dir = os.path.join("BU", channel_name)
    message_file_path = os.path.join(channel_dir, "messages.json")
    
    if os.path.exists(message_file_path):
        with open(message_file_path, 'r') as f:
            return json.load(f)
    return []

def save_backup(channel_name, new_messages):
    channel_dir = os.path.join("BU", channel_name)
    os.makedirs(channel_dir, exist_ok=True)
    
    existing_messages = fetch_existing_messages(channel_name)
    all_messages = existing_messages + new_messages
    
    # Remove duplicates based on timestamp or any unique identifier if needed
    seen_message_ids = set()
    unique_messages = []
    for message in all_messages:
        message_id = message.get('ts')  # Assuming 'ts' is the unique identifier for messages
        if message_id not in seen_message_ids:
            seen_message_ids.add(message_id)
            unique_messages.append(message)
    
    # Save combined unique messages
    message_file_path = os.path.join(channel_dir, "messages.json")
    with open(message_file_path, 'w') as f:
        json.dump(unique_messages, f, indent=2)
    
    print(f"Backup updated at {message_file_path}")

    # Download files if present
    for message in new_messages:
        if 'files' in message:
            for file_info in message['files']:
                download_file(file_info, channel_name)

def download_file(file_info, channel_name):
    file_url = file_info['url_private']
    file_name = file_info['name']
    file_path = os.path.join("BU", channel_name, file_name)
    
    # To access private files, we need to include the token in the headers
    headers_with_token = {'Authorization': f'Bearer {slack_token}'}
    
    response = requests.get(file_url, headers=headers_with_token, stream=True)
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"File downloaded: {file_path}")
    else:
        print(f"Failed to download file: {response.status_code}, {response.text}")

def main():
    channels = fetch_channels()
    for channel in channels:
        if channel['name'] == "teamway":  # For testing, use your condition
            channel_id = channel['id']
            channel_name = channel['name']
            print(f"Fetching messages for channel: {channel_name} ({channel_id})")
            new_messages = fetch_messages(channel_id)
            save_backup(channel_name, new_messages)

if __name__ == "__main__":
    main()
