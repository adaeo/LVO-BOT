from discord.ext import commands
from discord import utils, Embed, errors
import wavelink
import asyncio
import exceptions


class MusicPlayer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        # Music Cog
        self.bot = bot
        self.song_queue = {}
        self.now_playing = None
        self.nowplay_embed = None
        self.last_ctx = None

        bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        # Connect to Lavalink Nodes
        await self.bot.wait_until_ready()
        # Local Connection
        # await wavelink.NodePool.create_node(bot=self.bot,
        #                             host='127.0.0.1',
        #                             port=2333,
        #                             password='youshallnotpass')
        # Replit Connection
        await wavelink.NodePool.create_node(bot=self.bot, 
                                            host='lavalink-replit.adaeo.repl.co',
                                            port=443,
                                            password='lvopwd', 
                                            https=True)

    async def is_connected(self, ctx: commands.Context):
        # Returns if the voice_client is connected to a voice channel
        voice_client = utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        return voice_client and voice_client.is_connected()

    async def connect_to(self, ctx: commands.Context):
        try:
            if ctx.author.voice is None: raise exceptions.NotInAChannel(ctx)
            if ctx.voice_client is not None: await ctx.voice_client.disconnect()

            await ctx.send(f"Joining voice channel: {ctx.author.voice.channel}.", delete_after=2)
            vc : wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
            await vc.set_volume(50) # Set volume to 50%

        except exceptions.NotInAChannel as error:
            await self.send_error(ctx, error.message)

    async def check_queue(self, player: wavelink.Player):
        vc : wavelink.Player = player
        # Checks current queue of the guild
        if len(self.song_queue[vc.guild.id]) > 0:
            await vc.play(self.song_queue[vc.guild.id][0])
            self.now_playing = self.song_queue[vc.guild.id][0]
            self.song_queue[vc.guild.id].pop(0)
        else:
            await vc.stop()

    async def send_np_embed(self, ctx: commands.Context):
        track = self.now_playing
        embed = Embed()
        embed.description = f"{track.title}"
        embed.title = "Now Playing:"
        self.nowplay_embed = await ctx.send(embed=embed)  

    async def send_error(self, ctx, message):
        await ctx.send(message, delete_after=3)
        await ctx.message.delete(delay=3)

    @commands.command()
    async def join(self, ctx: commands.Context):
        # Joins voice channel of message author
        await self.connect_to(ctx)
        await ctx.message.delete(delay=2)

    @commands.command()
    async def leave(self, ctx: commands.Context):
        try:
            # Stops player and leaves voice channel
            vc : wavelink.Player = ctx.voice_client
            if ctx.author.voice is None: raise exceptions.NotInMyChannel(ctx)
            if (ctx.author.voice.channel != vc.channel): raise exceptions.NotInMyChannel(ctx)
            await vc.stop() # Completely stops player
            await vc.disconnect() # Disconnect from voice channel
            self.song_queue[vc.guild.id] = []
            await ctx.send(f"Leaving voice channel: {vc.channel}.", delete_after=2)
            await ctx.message.delete(delay=2)
            if self.nowplay_embed is not None: await self.nowplay_embed.delete() # Delete Now Playing Embed

        except AttributeError:
            message = f"I am not in a voice channel {ctx.author.mention}!"
            await self.send_error(ctx, message)
        except exceptions.NotInMyChannel as error:
            await self.send_error(ctx, error.message)

    @commands.command()
    async def play(self, ctx: commands.Context, *, query: str):
        try:
            if not (await self.is_connected(ctx)): await self.connect_to(ctx)

            vc : wavelink.Player = ctx.voice_client
            if (ctx.author.voice.channel != vc.channel): raise exceptions.NotInMyChannel(ctx)

            # Set last important context
            self.last_ctx = ctx

            # Clean up initial command
            await ctx.message.delete() 
            wait_msg = await ctx.send("Searching Youtube... Please Wait...")

            results = await wavelink.YouTubeTrack.search(query=query)
            tracks = results[0:10]
            track_num = 0
            query_result = ''
            for track in tracks:
                track_num += 1
                query_result = query_result + f'{track_num}) {track} - {track.uri}\n'

            result_embed = Embed()
            result_embed.description = query_result
            result_embed.title= "Please type a number corresponding to the song you want to play."
            query_result = await ctx.channel.send(embed=result_embed, delete_after=20)
            await wait_msg.delete()

            # Check author is same as author who issued initial command
            def check(m): 
                return m.author.id == ctx.author.id 
            response = await self.bot.wait_for('message', check=check, timeout=20)

            # Clean up commands in channel
            await query_result.delete()
            await response.delete()

            if int(response.content) < 1: raise IndexError
            track = tracks[int(response.content)-1]

            if vc.guild.id not in self.song_queue:
                self.song_queue[vc.guild.id] = []

            if ctx.voice_client.source is not None:
                queue_len = len(self.song_queue[vc.guild.id])
                if queue_len < 10:
                    self.song_queue[vc.guild.id].append(track)
                    return await ctx.send(f"I am currently playing {self.now_playing}, your song is position {queue_len+1} in queue.", delete_after=3)
                else:
                    return await ctx.send("Max queue length of 10 reached, please wait for the current song to finish.", delete_after=3)            

            # If no tracks in queue
            await vc.play(track)     

        except exceptions.NotInMyChannel as error:
            await self.send_error(ctx, error.message)
        except IndexError:
            message = f"Please choose a number from above {ctx.author.mention}!"
            await self.send_error(ctx, message)
        except asyncio.TimeoutError:
            message = f"Selection timed out {ctx.author.mention}."
            await self.send_error(ctx, message)

    @play.error
    async def on_command_error(self, ctx, error):
        # Handles errors related to ~play function.
        if isinstance(error, commands.MissingRequiredArgument):
            message = f"You must provide a query {ctx.author.mention}!"
            await self.send_error(ctx, message)

    @commands.command()
    async def skip(self, ctx: commands.Context):
        try:
            # No in-built skip function, just override current song with play()
            vc : wavelink.Player = ctx.voice_client
            if (ctx.author.voice.channel != vc.channel): raise exceptions.NotInMyChannel(ctx)
            await vc.stop()
            await ctx.send(f"Now skipping {self.now_playing.title}", delete_after=2)
            await ctx.message.delete(delay=2)

        except exceptions.NotInMyChannel as error:
            await self.send_error(ctx, error.message)
        except AttributeError:
            message = f"I am not in a voice channel {ctx.author.mention}!"
            await self.send_error(ctx, message)

    @commands.command()
    async def queue(self, ctx: commands.Context):
        try: 
            vc : wavelink.Player = ctx.voice_client
            if (ctx.author.voice.channel != vc.channel): raise exceptions.NotInMyChannel(ctx)

            queue = ''
            track_num = 0
            for track in self.song_queue[vc.guild.id]:
                track_num += 1
                queue = queue + f'{track_num}) {track} - {track.uri}\n'

            queue_embed = Embed()
            queue_embed.description = queue
            await ctx.send(embed=queue_embed, delete_after=30)
            await ctx.message.delete(delay=30)

        except exceptions.NotInMyChannel as error:
            await self.send_error(ctx, error.message)
        except AttributeError:
            message = f"I am not in a voice channel {ctx.author.mention}!"
            await self.send_error(ctx, message)
        except errors.HTTPException:
            message = f"The queue is empty!"
            await self.send_error(ctx, message)
        except KeyError:
            message = f"The queue is empty!"
            await self.send_error(ctx, message)

    @commands.command()
    async def now_playing(self, ctx: commands.Context):
        try:
            vc : wavelink.Player = ctx.voice_client
            if (ctx.author.voice.channel != vc.channel): 
                raise exceptions.NotInMyChannel(ctx)
            elif not vc.is_playing() or self.now_playing is None: 
                await ctx.send("I am not playing anything!", delete_after=3)
            else: 
                await ctx.send(f"Now Playing: {self.now_playing}", delete_after=5)
            await ctx.message.delete(delay=2)

        except exceptions.NotInMyChannel as error:
            await self.send_error(ctx, error.message)
        except AttributeError:
            message = f"I am not in a voice channel {ctx.author.mention}!"
            await self.send_error(ctx, message)

    @commands.command()
    async def pause(self, ctx: commands.Context):
        try:
            vc : wavelink.Player = ctx.voice_client
            if ctx.author.voice is None: raise exceptions.NotInAChannel(ctx)
            if (ctx.author.voice.channel != vc.channel): raise exceptions.NotInMyChannel(ctx)
            if not vc.is_playing() or self.now_playing is None: raise exceptions.NotPlaying(ctx)
            if vc.is_paused(): raise exceptions.AlreadyPaused(ctx)
            await vc.pause()
            await ctx.send(f"Now Pausing: {self.now_playing}", delete_after=3)
            await ctx.message.delete()
        except exceptions.NotInAChannel as error:
            await self.send_error(ctx, error.message)
        except exceptions.NotInMyChannel as error:
            await self.send_error(ctx, error.message)
        except exceptions.AlreadyPaused as error:
            await self.send_error(ctx, error.message)
        except exceptions.NotPlaying as error:
            await self.send_error(ctx, error.message)
        except AttributeError:
            message = f"I am not in a voice channel {ctx.author.mention}!"
            await self.send_error(ctx, message)

    @commands.command()
    async def resume(self, ctx: commands.Context):
        try:
            vc : wavelink.Player = ctx.voice_client
            if ctx.author.voice is None: raise exceptions.NotInAChannel(ctx)
            if (ctx.author.voice.channel != vc.channel): raise exceptions.NotInMyChannel(ctx)
            if not vc.is_playing() or self.now_playing is None: raise exceptions.NotPlaying(ctx)
            if not vc.is_paused(): raise exceptions.AlreadyPlaying(ctx)
            await vc.resume()
            await ctx.send(f"Now Resuming: {self.now_playing}", delete_after=3)
            await ctx.message.delete()
        except exceptions.NotInAChannel as error:
            await self.send_error(ctx, error.message)
        except exceptions.NotInMyChannel as error:
            await self.send_error(ctx, error.message)
        except exceptions.AlreadyPlaying as error:
            await self.send_error(ctx, error.message)
        except exceptions.NotPlaying as error:
            await self.send_error(ctx, error.message)
        except AttributeError:
            message = f"I am not in a voice channel {ctx.author.mention}!"
            await self.send_error(ctx, message)

    @commands.command(hidden=True)
    async def status(self, ctx: commands.Context):
        print(ctx.voice_client)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        # Fire evennt on connection to a node.
        print(f'Node: <{node.identifier}> is ready!\n')

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        await self.check_queue(player) # Check queue for songs
        await self.nowplay_embed.delete() # Delete Now Playing Embed

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player, track):
        self.now_playing = track # Set current playing track
        await self.send_np_embed(self.last_ctx) # Send Now Playing Embed
        