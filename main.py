import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv

# Import from modules
from music import Music_Player
from danbooru import Danbooru
from admin import Admin

# Get tokens from the .env
load_dotenv()
DISCORD_TOKEN = os.getenv("discord_token")
DISCORD_GUILD = os.getenv('discord_guild')

# Initialise
intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='~', intents=intents)
    
# Confirm ready status in console output
@bot.event
async def on_ready():
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
    bot.add_cog(Music_Player(bot))
    bot.add_cog(Danbooru(bot))
    bot.add_cog(Admin(bot))

bot.loop.create_task(setup())
bot.run(DISCORD_TOKEN)