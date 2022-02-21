import discord
from discord.ext import commands
import requests
import json
import io
import aiohttp

class Danbooru(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_image(self, ctx):
        # Retrieves image from danbooru API as JSON
        rand_response = requests.get('https://danbooru.donmai.us/posts/random')
        response = requests.get(rand_response.url + '.json')
        json_data = json.loads(response.text)
        return json_data['file_url']

    @commands.command(help="Returns a random image from Danbooru")
    async def danbooru(self, ctx):
        # Attempts to send random danbooru image
        await ctx.send("Retrieving image... this will take a few seconds.")
        async with aiohttp.ClientSession() as session:
            async with session.get(await self.get_image(ctx)) as resp:
                if resp.status != 200:
                    return await ctx.send('Could not download file...')
                data = io.BytesIO(await resp.read())
                await ctx.send(file=discord.File(data, 'random_img.png'))