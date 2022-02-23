import discord
from discord.ext import commands
import os

# Import from modules
from music import MusicPlayer
from danbooru import Danbooru
from admin import Admin

# Get tokens from the .env
from dotenv import load_dotenv
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
    game = discord.Game("~help")
    await bot.change_presence(activity=game)
    guild = discord.utils.get(bot.guilds, name=DISCORD_GUILD)
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name} (id: {guild.id})'
    )
    # members = '\n - '.join([member.name for member in guild.members])
    # print(f'Guild Members:\n - {members}')

@bot.command(name="amogus", hidden=True)
async def amogus(ctx):
    await ctx.send("https://c.tenor.com/fWICUw1py9UAAAAd/among-us-meme.gif")

@bot.command(name='moyai', hidden=True)
async def rules(ctx):
    await ctx.send("https://c.tenor.com/Yu6oaGFXFVAAAAAC/ratio-moyai.gif")

# Setup cogs after the bot is ready to prevent empty fields e.g. Guild ID
async def setup():
    await bot.wait_until_ready()
    bot.add_cog(MusicPlayer(bot))
    bot.add_cog(Danbooru(bot))
    bot.add_cog(Admin(bot))

bot.loop.create_task(setup())
bot.run(DISCORD_TOKEN)