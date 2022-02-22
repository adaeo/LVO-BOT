import discord
from discord.ext import commands
import pafy
import youtube_dl

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

class Music_Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}
        self.currently_playing = None

        self.setup()

    def setup(self):
        for guild in self.bot.guilds:
            self.song_queue[guild.id] = []

    async def check_queue(self, ctx):
        # Checks current queue of the guild
        if len(self.song_queue[ctx.guild.id]) > 0:
            ctx.voice_client.stop()
            await self.play_song(ctx, self.song_queue[ctx.guild.id][0])
            self.song_queue[ctx.guild.id].pop(0)
        else:
            ctx.voice_client.stop()

    async def search_song(self, amount, song, get_url=False):
        # Retrieves results for a search query
        info = await self.bot.loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL(
            {"format" : "bestaudio/best", "quiet" : True}).extract_info(
                f"ytsearch{amount}:{song}", download=False, ie_key="YoutubeSearch"))

        if len(info['entries']) == 0: return None

        return [entry['webpage_url'] for entry in info['entries']] if get_url else info

    async def play_song(self, ctx, song):
        # Plays next song in queue
        song = pafy.new(song)
        url = song.getbestaudio().url
        ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url, executable="ffmpeg.exe", **FFMPEG_OPTIONS)), 
        after=lambda error: self.bot.loop.create_task(self.check_queue(ctx)))
        ctx.voice_client.source.volume = 0.5
        self.currently_playing = song.title


    @commands.command(help="Joins voice channel of message author.")
    async def join(self, ctx):
        # Joins voice channel of message author
        if ctx.author.voice is None:
            return await ctx.send("You are not connected to a voice channel.")

        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()

        await ctx.author.voice.channel.connect()

    @commands.command(help="Leaves current voice channel.")
    async def leave(self, ctx):
        # Leaves currently joined voice channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.disconnect()
        
        await ctx.send("I am not connected to a voice channel.")

    @commands.command(help="Play a song using url or first result from keywords.")
    async def play(self, ctx, *, song=None):
        print(ctx.voice_client.source)
        # Attempt to play song using url or first search result
        if song is None:
            return await ctx.send("You must include a song to play.")

        if ctx.voice_client is None:
            return await ctx.send("I must be in a voice channel to play a song. Use ~join in a voice channel.")
        
        # handle song wehre song isn't a url
        if not ("youtube.com/watch?" in song or "https://youtu.be/" in song):
            await ctx.send("Searching for a song... Please wait...")

            result = await self.search_song(1, song, get_url=True)

            if result is None:
                return await ctx.send("Could not find the song, try using the search command.")

            song = result[0]

        if ctx.voice_client.source is not None:
            queue_len = len(self.song_queue[ctx.guild.id])
            if queue_len < 25:
                self.song_queue[ctx.guild.id].append(song)
                return await ctx.send(f"I am currently playing a song, this song has been added to queue at postion: {queue_len+1}.")

            else:
                return await ctx.send("Max queue length of 25 reached, please wait for the current song to finish.")

        await self.play_song(ctx, song)
        await ctx.send(f"Now playing {self.currently_playing}\n {song}")

    @commands.command(help="Returns top 5 URL's based on keyword search.")
    async def search(self, ctx, *, song=None):
        # Returns top 5 search results of search query
        if song is None: return await ctx.send("Please include a song to search for...")

        await ctx.send("Searching for song, this may take a few seconds.")

        info = await self.search_song(5, song)

        embed = discord.Embed(title=f"results for '{song}':", description="*Use one of these URL's with the !play command for the exact song.*\n")

        amount = 0
        for entry in info["entries"]:
            embed.description += f"[{entry['title']}]({entry['webpage_url']})\n"
            amount += 1
        
        embed.set_footer(text=f"Displaying the first {amount} results")
        await ctx.send(embed=embed)

    @commands.command(help="Display current queue.")
    async def queue(self, ctx): 
        # display the current guild's queue
        if len(self.song_queue[ctx.guild.id]) == 0:
            return await ctx.send("No songs in queue.")

        embed = discord.Embed(title="Song Queue", description="", colour=discord.Colour.dark_gold())
        i = 1
        for url in self.song_queue[ctx.guild.id]:
            embed.description += f"{i}) {url}\n"

            i+1
        
        embed.set_footer(text="Working as intended.")
        await ctx.send(embed=embed)

    @commands.command(help="Clears queue.")
    async def clear(self, ctx):
        # Clear current guild's queue
        if len(self.song_queue[ctx.guild.id]) == 0:
            return await ctx.send("No songs in queue.")
        
        self.song_queue[ctx.guild.id].clear()
        await ctx.send("Queue cleared.")

    @commands.command(help="Skips current song.")
    async def skip(self, ctx):
        # Skip current playing song
        if ctx.voice_client is None:
            return await ctx.send("I am not playing any song.")
        if ctx.author.voice is None:
            return await ctx.send("You are not in a voice channel.")
        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send("I am not playing any songs for you right now.")

        embed= discord.Embed(title="Skipping now.")
        await ctx.send(embed=embed)
        ctx.voice_client.stop()
        await self.check_queue(ctx)
        
    @commands.command(help="Pause current song.")
    async def pause(self, ctx):
        # Pause current playing song
        if ctx.voice_client is None:
            return await ctx.send("I am not playing any song.")
        if ctx.author.voice is None:
            return await ctx.send("You are not in a voice channel.")
        if ctx.voice_client.is_paused():
            return await ctx.send("I'm already paused!")
        
        ctx.voice_client.pause()
        await ctx.send("Now paused...")
        
    @commands.command(help="Resume current song.")
    async def resume(self, ctx):
        # Resume current paused song
        if ctx.voice_client is None:
            return await ctx.send("I am not playing any song.")
        if ctx.author.voice is None:
            return await ctx.send("You are not in a voice channel.")
        if ctx.voice_client.is_playing():
            return await ctx.send("I'm already playing!")
        
        ctx.voice_client.resume()
        await ctx.send("Now resuming...")

    @commands.command(help="Name current playing song.")
    async def current(self, ctx):
        # Name current playing song
        if ctx.voice_client is None:
            return await ctx.send("I am not playing any song.")
        if ctx.author.voice is None:
            return await ctx.send("You are not in a voice channel.")
        await ctx.send(f"Currently Playing: {self.currently_playing}")

# Based on https://www.youtube.com/watch?v=46ZHJcNnPJ8