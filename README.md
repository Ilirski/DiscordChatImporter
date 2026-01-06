# DiscordChatImporter

Discord Chat Importer allows you to import archived chats (JSON/HTML) saved with [Discord Chat Exporter](https://github.com/Tyrrrz/DiscordChatExporter) into any Discord text channel.

## Features

- Import HTML and JSON exports from Discord Chat Exporter
- Webhook-based message importing with author impersonation (profile pictures and names)
- Reply preservation with clickable jump buttons
- Full emoji support:
  - Default/Unicode emojis display normally
  - Custom emotes appear as text (`:example:`) or as the actual emote if available on your server
- File attachments (images, videos, audio, and other files) are uploaded to the server
- Large file handling: files exceeding server size limits can be appended as links instead

## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) (recommended package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Ilirski/DiscordChatImporter.git
cd DiscordChatImporter
```

2. Install dependencies with uv:
```bash
uv sync
```

3. Create a `.env` file with your Discord bot token:
```
DISCORD_TOKEN=your_bot_token_here
```

## Usage

1. Run the bot:
```bash
uv run python main.py
```

2. Invite the bot to your server with appropriate permissions (Manage Webhooks, Send Messages, Attach Files, Read Message History)

3. Use the import commands to upload your chat exports

## Configuration

Create a `.env` file in the project root with the following variables:

- `DISCORD_TOKEN` - Your Discord bot token (required)

## Examples

![Import Example 1](https://github.com/Ilirski/DiscordChatImporter/assets/24876805/f19f0340-264c-4137-ab17-e3af9ab37693)
![Import Example 2](https://github.com/Ilirski/DiscordChatImporter/assets/24876805/a816d50d-a00d-426b-a329-8bf804fee873)
![Import Example 3](https://github.com/Ilirski/DiscordChatImporter/assets/24876805/fa636dd2-7022-4b98-b3e0-747b4dd1de95)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.
