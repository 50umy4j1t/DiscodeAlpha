# Discode

A Discord bot that generates beautiful, standalone HTML pages and mini web apps from natural language — and hosts them instantly with a public URL.
[Try here](https://discord.gg/mznphrc3)

![Discode](https://cdn.discordapp.com/attachments/1484135354541019277/1484135691746152610/Gemini_Generated_Image_gbyl02gbyl02gbyl.png?ex=69bd2092&is=69bbcf12&hm=3c9682903cbe567c7929da88e71b3127fcc7eb4d7f687b6713f586ffc01b2f39&)

## How It Works

```
User messages Discord bot
        ↓
Agno Agent processes request using Ollama LLM (kimi-k2.5:cloud)
        ↓
Agent generates complete HTML (inline CSS + JS)
        ↓
save_and_host tool writes file, starts HTTP server, creates ngrok tunnel
        ↓
Bot returns public URL to user
```

1. User sends a message like *"make me a snake game"* in Discord
2. The agent interprets the request and generates a complete, self-contained HTML page
3. The `save_and_host` tool saves the file to `generated_sites/`, spins up a local HTTP server, and creates a public ngrok tunnel
4. The bot replies with a clickable public URL

All generated pages are fully self-contained — no external dependencies, just inline HTML, CSS, and JavaScript.

## Setup

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.com) installed and running
- A Discord bot token ([Discord Developer Portal](https://discord.com/developers/applications))
- An ngrok auth token ([ngrok dashboard](https://dashboard.ngrok.com))

### Install

```bash
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install agno ollama sqlalchemy pyngrok python-dotenv discord.py
```

### Configure

Create a `.env` file:

```env
DISCORD_BOT_TOKEN=your_discord_bot_token
NGROK_AUTH_TOKEN=your_ngrok_auth_token
```

### Run

Make sure Ollama is running, then:

```bash
python app.py
```

The bot will connect to Discord and start listening for messages.

## Project Structure

```
discode/
├── app.py                 # Entry point — Agno agent + Discord client
├── tools/
│   ├── __init__.py
│   └── html_host.py       # HTML hosting toolkit (save, host, ngrok tunnel)
├── generated_sites/       # Output directory for generated HTML files
├── discode.db             # SQLite conversation history
└── .env                   # Secrets (not committed)
```

## Discord Bot Setup

1. Create a new application at [discord.com/developers](https://discord.com/developers/applications)
2. Go to **Bot** → enable **Message Content Intent** and **Server Members Intent**
3. Go to **OAuth2** → URL Generator → select `bot` scope
4. Grant permissions: Send Messages, Read Message History, Embed Links
5. Copy the generated URL, open it, and invite the bot to your server
6. Copy the bot token to `.env`

## Tech Stack

- **[Agno](https://docs.agno.com)** — Agent framework with Discord integration
- **[Ollama](https://ollama.com)** — Local/cloud LLM inference (kimi-k2.5:cloud)
- **[discord.py](https://discordpy.readthedocs.io)** — Discord API wrapper
- **[pyngrok](https://github.com/alexdlaird/pyngrok)** — Public URL tunneling
- **SQLite** — Conversation history persistence


This is currently a WIP for future development, no more stuff would be posted in this repo anymore a better more complete version is yet to come at https://github.com/virusdumb no more development to be done in this repo

![Discode](https://cdn.discordapp.com/attachments/1484135354541019277/1484135692903911495/Gemini_Generated_Image_8oooxz8oooxz8ooo.png?ex=69bd2093&is=69bbcf13&hm=26e34eb66c1d64bb0d809b18a1f892eed7dbbd81dc581584d827b3c7e70205e9&)
