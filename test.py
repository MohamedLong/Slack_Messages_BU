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
user_info_url = 'https://slack.com/api/users.info'

headers = {
    'Authorization': f'Bearer {slack_token}',
    'Content-Type': 'application/json',
}

def fetch_dm_channels():
    params = {'types': 'im'}
    response = requests.get(list_url, headers=headers, params=params)
    data = response.json()

    if data.get('ok'):
        return data.get('channels', [])
    else:
        print("Error fetching DM channels:", data.get('error'))
        return []

def fetch_messages(channel_id):
    params = {'channel': channel_id, 'limit': 1000}
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
            print(f"Error fetching messages from channel {channel_id}: {data.get('error')}")
            break
    return messages

def fetch_user_info(user_id):
    params = {'user': user_id}
    response = requests.get(user_info_url, headers=headers, params=params)
    data = response.json()

    if data.get('ok'):
        return data['user']['name']
    else:
        print(f"Error fetching user info for user_id {user_id}: {data.get('error')}")
        return f"unknown_user_{user_id}"

def save_backup(channel_name, messages):
    channel_dir = os.path.join("BU", channel_name)
    os.makedirs(channel_dir, exist_ok=True)
    message_file_path = os.path.join(channel_dir, "messages.json")

    with open(message_file_path, 'w') as f:
        json.dump(messages, f, indent=2)

    print(f"Backup saved at {message_file_path}")

def main():
    dm_channels = fetch_dm_channels()
    for dm_channel in dm_channels:
        channel_id = dm_channel['id']
        user_id = dm_channel.get('user', 'direct_message')
        user_name = fetch_user_info(user_id)
        channel_name = f"DMs/{user_name}"
        print(f"Fetching direct messages for channel: {channel_name} ({channel_id})")
        messages = fetch_messages(channel_id)
        save_backup(channel_name, messages)

if __name__ == "__main__":
    main()
