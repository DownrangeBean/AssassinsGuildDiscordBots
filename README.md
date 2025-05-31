# Discord Bot

A simple Discord bot built with discord.py.

## Features

- Command system with prefix customization
- Modular command structure using cogs
- Basic commands: ping, hello, info, serverinfo
- Utility commands: roll (dice roller), choose (random choice), time (current UTC time)
- Error handling for commands

## Setup

### Prerequisites

- Python 3.8 or higher
- A Discord account
- A Discord bot token (see below for instructions)

### Creating a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" tab and click "Add Bot"
4. Under the "TOKEN" section, click "Copy" to copy your bot token
5. Keep this token secure and don't share it with anyone

### Installation

1. Clone this repository or download the files
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Edit the `.env` file and replace `your_discord_bot_token_here` with your actual bot token
4. Optionally, change the command prefix in the `.env` file (default is `!`)

### Inviting the Bot to Your Server

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application
3. Go to the "OAuth2" tab and then "URL Generator"
4. Select the "bot" scope
5. Select the permissions your bot needs (recommended: "Send Messages", "Read Message History", "Embed Links")
6. Copy the generated URL and open it in your browser
7. Select the server you want to add the bot to and click "Authorize"

### Running the Bot

#### Option 1: Using the command line
```
python bot.py
```

#### Option 2: Using the batch file (Windows)
Simply double-click the `run.bat` file. This will:
1. Create a virtual environment if it doesn't exist
2. Install all required dependencies
3. Start the bot

## Adding Commands

To add new commands, you can either:

1. Add them directly to `bot.py`
2. Create a new cog file in the `cogs` directory (recommended)

### Creating a New Cog

1. Create a new Python file in the `cogs` directory (e.g., `mycog.py`)
2. Use the following template:

```python
import discord
from discord.ext import commands

class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='mycommand', help='Description of my command')
    async def my_command(self, ctx):
        await ctx.send('Hello from my command!')

async def setup(bot):
    await bot.add_cog(MyCog(bot))
```

The bot will automatically load all cogs in the `cogs` directory when it starts.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
