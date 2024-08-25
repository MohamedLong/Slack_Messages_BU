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

def download_file(file_info):
    file_url = file_info.get('url_private_download')
    if not file_url:
        return
    
    headers = {
        'Authorization': f'Bearer {slack_token}',
    }
    
    response = requests.get(file_url, headers=headers, stream=True)
    
    if response.status_code == 200:
        file_name = file_info.get('name', 'file')
        file_path = os.path.join("BU", file_name)
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"Downloaded: {file_path}")
        return file_path
    else:
        print(f"Failed to download file: {file_info['name']} (status code: {response.status_code})")
    return None

def save_backup(channel_name, messages):
    os.makedirs("BU", exist_ok=True)
    
    for message in messages:
        if 'files' in message:
            for file_info in message['files']:
                file_path = download_file(file_info)
                if file_path:
                    file_name = os.path.basename(file_path)
                    print(f"File saved at: {file_path}")

def main():
    channels = fetch_channels()
    for channel in channels:
        if channel['name'] == 'teamway':  # Filter by channel name
            channel_id = channel['id']
            channel_name = channel['name']
            print(f"Fetching messages for channel: {channel_name} ({channel_id})")
            messages = fetch_messages(channel_id)
            save_backup(channel_name, messages)

if __name__ == "__main__":
    main()
