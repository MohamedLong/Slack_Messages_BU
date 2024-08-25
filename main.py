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
replies_url = 'https://slack.com/api/conversations.replies'
info_url = 'https://slack.com/api/conversations.info'
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
            for message in data.get('messages', []):
                # Fetch replies for each message
                replies = fetch_replies(channel_id, message.get('thread_ts'))
                message['replies'] = replies
                messages.append(message)
            if data.get('response_metadata') and data['response_metadata'].get('next_cursor'):
                params['cursor'] = data['response_metadata']['next_cursor']
                time.sleep(1)  # To handle rate limits
            else:
                break
        else:
            print("Error fetching messages:", data.get('error'))
            break
    return messages

def fetch_replies(channel_id, thread_ts):
    if not thread_ts:
        return []
    params = {
        'channel': channel_id,
        'ts': thread_ts,
        'limit': 1000,  # Adjust as needed
    }
    replies = []
    while True:
        response = requests.get(replies_url, headers=headers, params=params)
        data = response.json()
        if data.get('ok'):
            replies.extend(data.get('messages', []))
            if data.get('response_metadata') and data['response_metadata'].get('next_cursor'):
                params['cursor'] = data['response_metadata']['next_cursor']
                time.sleep(1)  # To handle rate limits
            else:
                break
        else:
            print("Error fetching replies:", data.get('error'))
            break
    return replies

def check_if_app_installed(channel_id):
    # Check if the app is mentioned in the channel's messages
    messages = fetch_messages(channel_id)
    for message in messages:
        if 'text' in message and 'Message Backup App' in message['text']:
            return True
    return False

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
    all_messages = new_messages + existing_messages  # New messages come first
    
    # Remove duplicates based on timestamp or any unique identifier if needed
    seen_message_ids = set()
    unique_messages = []
    for message in all_messages:
        message_id = message.get('ts')  # Assuming 'ts' is the unique identifier for messages
        if message_id not in seen_message_ids:
            seen_message_ids.add(message_id)
            unique_messages.append(message)
    
    # Sort messages by timestamp in descending order
    unique_messages.sort(key=lambda msg: float(msg.get('ts', 0)), reverse=True)
    
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
    
    # Check if the file already exists
    if os.path.exists(file_path):
        print(f"File already exists: {file_path}")
        return

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
        channel_id = channel['id']
        channel_name = channel['name']
        if check_if_app_installed(channel_id):
            print(f"Fetching messages for channel: {channel_name} ({channel_id})")
            new_messages = fetch_messages(channel_id)
            save_backup(channel_name, new_messages)
        else:
            print(f"App not installed in channel: {channel_name} ({channel_id})")

if __name__ == "__main__":
    main()
