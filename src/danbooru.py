from discord.ext import commands
import requests
import json
import exceptions

class Danbooru(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
      
    async def send_error(self, ctx, message):
      await ctx.send(message, delete_after=3)
      await ctx.message.delete(delay=3)
    
    async def get_image(self, ctx):
        # Retrieves image from danbooru API as JSON
        rand_response = requests.get('https://danbooru.donmai.us/posts/random')
        response = requests.get(rand_response.url + '.json')
        json_data = json.loads(response.text)
        return json_data['file_url']

    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.command(help="Returns a random image from Danbooru")
    async def danbooru(self, ctx):
      try:
          retrieve_msg = await ctx.send("Retrieving image... this will take a few seconds.", delete_after=5)
          image_link = await self.get_image(ctx)          
          await retrieve_msg.delete()
          await ctx.send(image_link)
      except exceptions.DownloadException as error:
          await self.retrieve_msg.delete()
          await self.send_error(ctx, error.message)
          

    @danbooru.error
    async def on_command_error(self, ctx, error):
        message = f"Something went wrong, please try again."

        if isinstance(error, commands.CommandOnCooldown):
            message = f"{error} {ctx.author.mention}"
        
        await self.send_error(ctx, message)