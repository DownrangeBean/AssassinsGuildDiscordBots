import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('COMMAND_PREFIX', '!')  # Default to '!' if not specified

# Set up intents (permissions)
intents = discord.Intents.default()
intents.message_content = True  # Needed to read message content for commands

# Initialize the bot with command prefix and intents
bot = commands.Bot(command_prefix=PREFIX, intents=intents)


# Function to load all cogs
async def load_cogs():
    """Load all cogs from the cogs directory."""
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'Loaded extension: {filename[:-3]}')
            except Exception as e:
                print(f'Failed to load extension {filename[:-3]}: {e}')


@bot.event
async def on_ready():
    """Event triggered when the bot is ready and connected to Discord."""
    print(f'{bot.user.name} has connected to Discord!')
    print(f'Bot ID: {bot.user.id}')
    print(f'Command prefix: {PREFIX}')

    # Load all cogs
    await load_cogs()

    # Set the bot's status
    await bot.change_presence(activity=discord.Game(name=f"Type {PREFIX}help"))


@bot.command(name='ping', help='Responds with the bot\'s latency')
async def ping(ctx):
    """Simple command to check if the bot is responsive."""
    latency = round(bot.latency * 1000)  # Convert to milliseconds
    await ctx.send(f'Pong! Latency: {latency}ms')


@bot.command(name='hello', help='Says hello to the user')
async def hello(ctx):
    """Greets the user who invoked the command."""
    await ctx.send(f'Hello, {ctx.author.mention}! How are you today?')


@bot.event
async def on_command_error(ctx, error):
    """Global error handler for command errors."""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Command not found. Type `{PREFIX}help` for a list of commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument. Type `{PREFIX}help {ctx.command}` for proper usage.")
    else:
        await ctx.send(f"An error occurred: {str(error)}")
        # Log the error for debugging
        print(f"Error in command {ctx.command}: {error}")


# Run the bot
if __name__ == '__main__':
    if not TOKEN:
        print("Error: No Discord token found in .env file")
        print("Please add your bot token to the .env file as DISCORD_TOKEN=your_token_here")
        exit(1)

    print("Starting bot...")
    bot.run(TOKEN)
