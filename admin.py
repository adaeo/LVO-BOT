import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Get owner ID from .env
load_dotenv()
BOT_OWNER_ID = os.getenv('bot_owner_id')

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='responds with bot latency')
    async def ping(self, ctx):
        # Pings bot and returns latency in ms
        await ctx.send(f"pong! {round(self.bot.latency * 1000)}ms")

    @commands.command(help='sets status of bot')
    async def setstatus(self, ctx, *, text=None):
        # sets status message of bot. Only owner can use.
        if (str(ctx.message.author.id) != BOT_OWNER_ID):
            return await ctx.send("You must be the owner to set the status.")

        if text is None: 
            return await ctx.send("You must specify an argument.")

        await ctx.send(f"Setting status to {str(text)}")
        await self.bot.change_presence(activity=discord.Game(name=str(text)))