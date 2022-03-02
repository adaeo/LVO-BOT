# Contains custom exceptions
class NotInMyChannel(Exception):
    # Raised when user is not in the same voice channel as the bot
    def __init__(self, ctx):
        self.message = f"You are not in my voice channel {ctx.author.mention}!"
        super().__init__(self.message)

class NotInAChannel(Exception):
    # Raised when user is not in any voice channel
    def __init__(self, ctx):
        self.message = f"You are not connected to any channel {ctx.author.mention}!"
        super().__init__(self.message)

class NotPlaying(Exception):
    # Raised when a command is called on a player that is not active
    def __init__(self, ctx):
        self.message = f"I am not playing anything right now {ctx.author.mention}!"
        super().__init__(self.message)

class AlreadyPaused(Exception):
    # Raised when pause() is called on a player that is paused
    def __init__(self, ctx):
        self.message = f"The player is already paused {ctx.author.mention}!"
        super().__init__(self.message)

class AlreadyPlaying(Exception):
    # Raised when resume() is called on a player that is playing
    def __init__(self, ctx):
        self.message = f"The player is already playing {ctx.author.mention}!"
        super().__init__(self.message)

class DownloadException(Exception):
    # Raised when an error occurs during a download
    def __init__(self, ctx):
        self.message = f"Something went wrong during download {ctx.author.mention}."
        super().__init__(self.message)