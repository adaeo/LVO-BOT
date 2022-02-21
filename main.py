import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import requests
import json
import io
import aiohttp

from music import Music_Player


# Custom Exceptions
class VoiceError(Exception):
    pass

class YTDLError(Exception):
    pass

# Get the API token from the .env
load_dotenv()
DISCORD_TOKEN = os.getenv("discord_token")
DISCORD_GUILD = os.getenv('discord_guild')

# Initialise
intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

# utility function retrieves image from danbooru API and returns JSON
def get_image():
    rand_response = requests.get('https://danbooru.donmai.us/posts/random')
    response = requests.get(rand_response.url + '.json')
    json_data = json.loads(response.text)
    return json_data['file_url']
    
@bot.event
async def on_ready():
    
    guild = discord.utils.get(bot.guilds, name=DISCORD_GUILD)

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name} (id: {guild.id})'
    )
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

@bot.command(name='hello', help='responds hello')
async def say_hello(ctx):
    await ctx.send('Hello!')

@bot.command(name='danbooru', help='responds random danbooru img')
async def danbooru(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get(get_image()) as resp:
            if resp.status != 200:
                return ctx.send('Could not download file...')
            data = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(data, 'random_img.png'))

# setup cogs after the bot is ready to prevent empty fields e.g. Guild ID
async def setup():
    await bot.wait_until_ready()
    bot.add_cog(Music_Player(bot))

bot.loop.create_task(setup())
bot.run(DISCORD_TOKEN)