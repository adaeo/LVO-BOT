import discord
from discord.ext import commands


# Get owner ID
BOT_OWNER_ID = 302967111980941312

class Admin(commands.Cog):
    def __init__(self, bot : commands.Bot):
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

    # Miscellaneous
    @commands.command(name="amogus", hidden=True)
    async def amogus(ctx):
        await ctx.send("https://c.tenor.com/fWICUw1py9UAAAAd/among-us-meme.gif")

    @commands.command(name='moyai', hidden=True)
    async def rules(ctx):
        await ctx.send("https://c.tenor.com/Yu6oaGFXFVAAAAAC/ratio-moyai.gif")

    @commands.command(name="danbooru", hidden=True)
    async def danbooru(ctx):
        await ctx.send("This feature has been disabled. Sorry.", delete_after=5)
        await ctx.message.delete(delay=5)