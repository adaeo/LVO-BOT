from discord.ext import commands
from discord import utils
from discord import Embed
import lavalink
import asyncio

class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.music = lavalink.Client(self.bot.user.id)
        self.bot.music.add_node('localhost', 7000, 'lvopwd', 'oce', 'music-node')
        self.bot.add_listener(self.bot.music.voice_update_handler, 'on_socket_response')
        self.bot.music.add_event_hook(self.track_hook)

    @commands.command(name='join', help='Joins voice channel.')
    async def join(self, ctx):
        # Attempt to join the voice channel of a user who uses this command.
        await self.join_channel(ctx)

    @commands.command(name='leave', help='Leaves voice channel')
    async def leave(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        
        if player is None or not player.is_connected:
            return await ctx.send("Not connected to a voice channel.")

        player.queue.clear()
        await player.stop()
        await self.connect_to(ctx.guild.id, None)
        print(player.is_connected)
        await self.disconnect(ctx)

    @commands.command(name='skip')
    async def skip(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        await player.skip()
    
    @commands.command(name='play')
    async def play(self, ctx, *, query):
        try:       
            if ctx.voice_client is None:
                await self.join_channel(ctx)

            player = self.bot.music.player_manager.get(ctx.guild.id)
            query = f'ytsearch:{query}'
            results = await player.node.get_tracks(query)
            tracks = results['tracks'][0:10]
            i = 0
            query_result = ''
            for track in tracks:
                i += 1
                query_result = query_result + f'{i}) {track["info"]["title"]} - {track["info"]["uri"]}\n'
            embed = Embed()
            embed.description = query_result
            embed.title= "Please type a number corresponding to the song you want to play."
            query_result = await ctx.channel.send(embed=embed, delete_after=20)

            def check(m): # Check author is same as author who issued initial command
                return m.author.id == ctx.author.id 
            response = await self.bot.wait_for('message', check=check, timeout=20)
            track = tracks[int(response.content)-1]

            # Clean up commands in channel
            await response.delete()
            await query_result.delete()

            player.add(requester=ctx.author.id, track=track)

            if not player.is_playing:
                await player.play()
            else:
                await ctx.send(f"Your song has been queued in position {len(player.queue)} {ctx.author.mention}.")     

            #! TESTING CODE    
            print(player.current['title'])

        except AttributeError:
            message = f"You must be in a voice channel {ctx.author.mention}!"
            await ctx.send(message, delete_after=5)
            await ctx.message.delete(delay=5)
        except IndexError:
            message = f"You must choose a number from the list {ctx.author.mention}!"
            await ctx.send(message, delete_after=5)
            await ctx.message.delete(delay=5)
        except asyncio.TimeoutError:
            message = f"Selection timed out {ctx.author.mention}."
            await ctx.send(message, delete_after=5)
            await ctx.message.delete(delay=5)

    @play.error
    async def on_command_error(self, ctx, error):
        # Handles errors related to ~play function.
        if isinstance(error, commands.MissingRequiredArgument):
            message = f"You must provide a query {ctx.author.mention}!"
        
        await ctx.send(message, delete_after=5)
        await ctx.message.delete(delay=5)

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            player = event.player
            await asyncio.sleep(60)
            if player.is_playing: # interrupt if begins playing again
                return
            print("Inactive too long: Disconnecting")
            guild_id = int (event.player.guild_id)
            await self.connect_to(guild_id, None)

    async def join_channel(self, ctx):
        if ctx.voice_client is None:
            member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
            if member is not None and member.voice is not None:
                channel = member.voice.channel
                player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
                await player.set_volume(50) # Set half default volume
                player.store('channel', ctx.channel.id)
                await self.connect_to(ctx.guild.id, str(channel.id))
                await ctx.message.delete()
            else:
                message = message = f"You must be in a voice channel {ctx.author.mention}!"
                await ctx.send(message, delete_after=5)
                await ctx.message.delete(delay=5)

    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)

    async def disconnect(self, guild_id: int):
        await self.connect_to(guild_id, None)



# DOCUMENTATION lavalink exam https://github.com/Devoxin/Lavalink.py/blob/master/examples/music.py
# LAVALINK DOCS https://lavalink.readthedocs.io/en/master/lavalink.html
# SOME CODE BASED ON https://www.youtube.com/watch?v=X1DEos_9dJo