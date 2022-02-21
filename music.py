import discord
from discord.ext import commands
import pafy
import youtube_dl

class Music_Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}

        self.setup()

    def setup(self):
        for guild in self.bot.guilds:
            self.song_queue[guild.id] = []

    async def check_queue(self, ctx):
        if len(self.song_queue[ctx.guild.id]) > 0:
            ctx.voice_client.stop()
            await self.play_song(ctx, self.song_queue[ctx.guild.id][0])
            self.song_queue[ctx.guild.id].pop(0)

    async def search_song(self, amount, song, get_url=False):
        info = await self.bot.loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL(
            {"format" : "bestaudio", "quiet" : True}).extract_info(
                f"ytsearch{amount}:{song}", download=False, ie_key="YoutubeSearch"))

        if len(info['entries']) == 0: return None

        return [entry['webpage_url'] for entry in info['entries']] if get_url else info

    async def play_song(self, ctx, song):
        url = pafy.new(song).getbestaudio().url
        ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url, executable="ffmpeg.exe")), 
        after=lambda error: self.bot.loop.create_task(self.check_queue(ctx)))

        ctx.voice_client.source.volume = 0.5


    @commands.command(help="Joins voice channel of message author.")
    async def join(self, ctx):
        if ctx.author.voice is None:
            return await ctx.send("You are not connected to a voice channel.")

        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()

        await ctx.author.voice.channel.connect()

    @commands.command(help="Leaves current voice channel.")
    async def leave(self, ctx):
        if ctx.voice_client is not None:
            return await ctx.voice_client.disconnect()
        
        await ctx.send("I am not connected to a voice channel.")

    @commands.command(help="Play a song using url or first result from keywords.")
    async def play(self, ctx, *, song=None):
        if song is None:
            return await ctx.send("You must include a song to play.")

        if ctx.voice_client is None:
            return await ctx.send("I must be in a voice channel to play a song.")
        
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
        await ctx.send(f"Now playing {song}")

    @commands.command(help="Returns top 5 URL's based on keyword search.")
    async def search(self, ctx, *, song=None):
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

    @commands.command(help="Display current queue")
    async def queue(self, ctx): # display the current guild's queue
        if len(self.song_queue[ctx.guild.id]) == 0:
            return await ctx.send("No songs in queue.")

        embed = discord.Embed(title="Song Queue", description="", colour=discord.Colour.dark_gold())
        i = 1
        for url in self.song_queue[ctx.guild.id]:
            embed.description += f"{i}) {url}\n"

            i+1
        
        embed.set_footer(text="Working as intended.")
        await ctx.send(embed=embed)

    @commands.command(help="Skips current song.")
    async def skip(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("I am not playing any song.")
        if ctx.author.voice is None:
            return await ctx.send("You are not in a voice channel.")
        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send("I am not playing any songs for you right now.")

        embed= discord.Embed(title="Skipping now.")
        ctx.voice_client.stop()
        await self.check_queue(ctx)
        
# Based on https://www.youtube.com/watch?v=46ZHJcNnPJ8