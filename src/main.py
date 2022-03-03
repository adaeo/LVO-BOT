import discord
from discord.ext import commands
import os

# Import from modules
from cogs.music import MusicPlayer
from cogs.admin import Admin
from cogs.blackjack import Blackjack
from utility.webserver import keep_alive

#! Get tokens from the .env
# from dotenv import load_dotenv
# load_dotenv()
# DISCORD_TOKEN = os.getenv("discord_token")
# DISCORD_GUILD = os.getenv('discord_guild')

#? Get tokens from Replit env
DISCORD_TOKEN = os.environ['discord_token']
DISCORD_GUILD = os.environ['discord_guild']

# Initialise
intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='~', intents=intents)

# Confirm ready status in console output
@bot.event
async def on_ready():
    game = discord.Game("~help")
    await bot.change_presence(activity=game)
    guild = discord.utils.get(bot.guilds, name=DISCORD_GUILD)
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name} (id: {guild.id})'
    )
    # members = '\n - '.join([member.name for member in guild.members])
    # print(f'Guild Members:\n - {members}')

# Setup cogs after the bot is ready to prevent empty fields e.g. Guild ID
async def setup():
    await bot.wait_until_ready()
    bot.add_cog(MusicPlayer(bot))
    bot.add_cog(Admin(bot))
    bot.add_cog(Blackjack(bot))
    
bot.loop.create_task(setup())
keep_alive()

try:
    bot.run(DISCORD_TOKEN)
except:
    os.system("kill 1") # If bot fails to run, kill current Replit container.

