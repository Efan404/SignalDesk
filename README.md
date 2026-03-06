# SignalDesk

An AI-powered email triage assistant that automatically processes your Gmail inbox and delivers a personalized daily digest.

## Features

- **Gmail Integration** - Fetches emails via Google Workspace CLI (gws)
- **LLM-Powered Triage** - Uses AI to classify emails by importance, urgency, and actionability
- **Smart Routing** - Categorizes emails into: Urgent, Important, To Review, and Silent
- **Daily Digest** - Generates a concise summary delivered via Telegram
- **SQLite Storage** - Persists email events and triage decisions locally
- **CLI-First** - Full command-line interface with Rich terminal UI
- **Telegram Bot** - Interactive task management via `/task` command

## Architecture

```
Gmail (gws) → SQLite → LLM Triage → Digest → Telegram
```

## Prerequisites

- Python 3.12+
- [gws](https://github.com/AndreMayer/gws) - Google Workspace CLI
- OpenAI API key (or LiteLLM-compatible endpoint)
- Telegram Bot Token (optional, for notifications)

## Quick Start

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/yourusername/SignalDesk.git
cd SignalDesk

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -e .
```

### 2. Configure

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```bash
# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=your_openai_api_key_here

# Telegram Notifications (optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Digest Settings
DIGEST_TIME=20:00
MAX_EMAILS_PER_DIGEST=10
```

### 3. Run Manually

```bash
# Process emails and send digest
signaldesk run

# Show recent triage decisions
signaldesk status

# Generate and preview digest (without sending)
signaldesk digest

# Start Telegram bot for interactive task management
signaldesk bot
```

## Commands

| Command | Description |
|---------|-------------|
| `signaldesk run` | Process emails and send digest to Telegram |
| `signaldesk status` | Display recent triage decisions in a table |
| `signaldesk digest` | Generate digest and send via Telegram |
| `signaldesk bot` | Start Telegram bot for task management |

## Telegram Bot Commands

When running `signaldesk bot`, you can interact with the bot via Telegram:

| Command | Description |
|---------|-------------|
| `/task` | Create a new task (starts multi-turn conversation) |
| `/tasks` | List all your tasks |
| `/help` | Show help message |
| `/cancel` | Cancel current operation |

### Options

- `--max N` - Maximum number of emails to process (default: 10)

## Automated Deployment

### macOS (Launch Agent)

Create `~/Library/LaunchAgents/com.signaldesk.digest.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.signaldesk.digest</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/SignalDesk/run_digest.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>20</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</dict>
</plist>
```

Load the agent:

```bash
launchctl load ~/Library/LaunchAgents/com.signaldesk.digest.plist
```

### Linux (systemd)

Install the service and timer:

```bash
# Copy service files
sudo cp signaldesk.service /etc/systemd/system/
sudo cp signaldesk.timer /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start the timer
sudo systemctl enable signaldesk.timer
sudo systemctl start signaldesk.timer
```

## Configuration Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM provider (openai/anthropic) | openai |
| `LLM_MODEL` | Model to use for triage | gpt-4o-mini |
| `LLM_API_KEY` | API key for LLM | - |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | - |
| `TELEGRAM_CHAT_ID` | Telegram chat ID | - |
| `DIGEST_TIME` | Daily digest time (HH:MM) | 20:00 |
| `MAX_EMAILS_PER_DIGEST` | Max emails per digest | 10 |
| `IMPORTANCE_THRESHOLD` | Triage importance threshold (1-5) | 3 |
| `URGENCY_THRESHOLD` | Triage urgency threshold (1-5) | 3 |

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=src
```

### Code Quality

```bash
# Lint with ruff
ruff check src/

# Type check with mypy
mypy src/
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please open an issue or PR on GitHub.
