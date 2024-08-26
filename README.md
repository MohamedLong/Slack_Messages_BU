# Slack Message Backup Tool

The Slack Message Backup Tool is designed to help free Slack users who lose their old messages due to Slack's limitations on message history for free accounts. This tool automatically backs up your Slack messages and attachments, ensuring you never lose important communication.

# Features

- **Initial Backup**: Fetches all messages from each channel and stores them in individual JSON files.
- **Daily Updates**: Updates the JSON files with only new messages and attachments.
- **Media Downloads**: Downloads and saves media files shared within channels.

# Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/yourusername/slack-message-backup.git
    cd slack-message-backup
    ```

2. **Set Up Environment**

    Make sure you have Python 3 installed. Create a virtual environment and install the required packages:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3. **Configure Environment Variables**

    Set the `SLACK_TOKEN` environment variable with your Slack OAuth token. You can set this in your terminal or use a `.env` file if you use a library like `python-dotenv`.

    ```bash
    export SLACK_TOKEN='your-slack-token'
    ```

# Usage

1. **Run the Backup Tool**

    Execute the tool to start the backup process:

    ```bash
    python main.py
    ```

2. **Scheduled Backups**

    To schedule the backup to run daily at 10 PM, use a cron job (Linux/macOS) or Task Scheduler (Windows).

    **Example Cron Job**

    Open the crontab editor:

    ```bash
    crontab -e
    ```

    Add the following line to run the script daily at 10 PM:

    ```bash
    0 22 * * * /path/to/your/python /path/to/slack-message-backup/main.py
    ```

# Permissions

Ensure your Slack OAuth token has the following scopes:

- `channels:history` – to read messages from public channels.
- `groups:history` – to read messages from private channels.
- `files:read` – to download files from Slack.
- `users:read` – to fetch user information.

Configure these permissions in your Slack app settings. For more information, refer to Slack’s [OAuth Scopes Documentation](https://api.slack.com/scopes).

# Troubleshooting

- **Error: `missing_scope`**: Ensure your token has the required scopes.
- **Empty Messages**: Verify your Slack token has access to the channels and they are correctly listed in your workspace.

# Contributing

If you have suggestions or improvements, feel free to create a pull request or open an issue.
