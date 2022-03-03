from discord.ext import commands
from discord import utils
from objects.deck import Deck
from objects.player import Player
import utility.exceptions as exceptions

class Blackjack(commands.Cog):
    MIN_PLAYERS = 2
    MAX_PLAYERS = 7
    BLACKJACK = 21
    NORMAL_OPTIONS = "\nType: _stand or _hit"

    def __init__(self, bot : commands.Bot):
        self.bot = bot
        self.game_instance = {} # Holds Player objects
        self.dealer = None
        self.dealer_msg = None
        self.game_window = None

    async def send_error(self, ctx: commands.Context, message: str):
        await ctx.send(message, delete_after=3)
        await ctx.message.delete(delay=3)

    async def game_result(self, ctx: commands.Context, game_instance: list, dealer: Player):
        players = game_instance[2:]

        dealer_result = "The dealer "
        dealer_score = dealer.GetScore()
        if dealer_score < self.BLACKJACK:
            dealer_result += "did not go bust."
        elif dealer_score == self.BLACKJACK:
            dealer_result += "got BLACKJACK!"
        else:
            dealer_result += "went bust."

        dealer_cards = "\nDealer's cards:"
        for card in dealer.GetHand():
            dealer_cards += f"\n- {card.GetName()}"
        dealer_score_msg = f"\nThe dealer's score was: {dealer.GetScore()}"

        all_player_result = ""
        for player in players:
            score = player.GetScore()
            player_result = f"\n\n{player.GetUser()}'s result: "
            if score == dealer_score and score <= self.BLACKJACK:
                player_result += "DRAW."
                # DRAW
            elif score > dealer.score and score <= self.BLACKJACK:
                player_result += "WIN."
                # WIN
            elif score <= self.BLACKJACK and dealer.score > self.BLACKJACK:
                player_result += "WIN."
                #WIN
            else:
                player_result += "LOSE."
                #LOSE
            player_cards = f"\n{player.GetUser()}'s cards:"
            for card in player.GetHand():
                player_cards += f"\n- {card.GetName()}"
            player_score = f"\n{player.GetUser()}'s score is {player.GetScore()}."
            all_player_result += player_result + player_cards + player_score

        msg_content = dealer_result + dealer_cards + dealer_score_msg + all_player_result
        msg = "```\n" + msg_content + "\n```"
        await self.game_window.delete()
        self.game_window = await ctx.send(msg)
        await self.end_game(ctx)


    async def score_logic(self, player: Player):
        hand = player.GetHand()
        aces = [x for x in hand if x.GetType() == "ACE"]
        if len(aces) > 0:
            max_ace_score = 10 + len(aces) # Maximum legal score is 11+1+1+1
            score = 0
            for card in hand:
                if card.GetType() != "ACE":
                    score += card.GetVal() # Get score of all non-ACE cards.            
            if (score+max_ace_score) > self.BLACKJACK:
                score += len(aces) # Add all aces to score as 1
                player.SetScore(score)
                return # End func
            else:
                score += max_ace_score # Add max score from combined aces
                player.SetScore(score)
                return # End func

    async def game_logic(self, ctx: commands.Context, game_instance: list, player: Player):
        deck = game_instance[0]
        await self.score_logic(player)

        player_cards = f"\n\n{player.GetUser()}'s cards:"
        for card in player.GetHand():
            player_cards += f"\n- {card.GetName()}"
        player_score = f"\n\nYour score is currently {player.GetScore()}."
        msg_content = (self.dealer_msg + 
                        player_cards + 
                        player_score)

        if player.GetScore() < self.BLACKJACK:
            msg_content += self.NORMAL_OPTIONS
            msg = "```\n" + msg_content + "\n```"
            await self.game_window.delete()
            self.game_window = await ctx.send(msg)
            def check(m):
                return (
                    (m.content.lower() == "_stand" or
                    m.content.lower() == "_hit")
                    and m.channel.id == ctx.channel.id
                    and m.author.id == player.GetUser().id
                )
            response = await self.bot.wait_for('message', check=check)
            await response.delete(delay=2)
            
            if response.content == "_hit":
                player.Draw(deck)
                await self.game_logic(ctx, game_instance, player)

        elif player.GetScore() == self.BLACKJACK:
            msg_content += "\nBLACKJACK!\tType: _next"
            msg = "```\n" + msg_content + "\n```"
            await self.game_window.delete()
            self.game_window = await ctx.send(msg)
            def check(m):
                return (
                m.content.lower() == "_next"
                and m.channel.id == ctx.channel.id
                and m.author.id == player.GetUser().id
                )
            response = await self.bot.wait_for('message', check=check)
            await response.delete()
        else:
            msg_content += "\nBUST!\tType: _next"
            msg = "```\n" + msg_content + "\n```"
            await self.game_window.delete()
            self.game_window = await ctx.send(msg)
            def check(m):
                    return (
                m.content.lower() == "_next"
                and m.channel.id == ctx.channel.id
                and m.author.id == player.GetUser().id
                )
            response = await self.bot.wait_for('message', check=check)
            await response.delete()

    async def dealer_logic(self, ctx: commands.Context, game_instance: list, dealer: Player):
        deck = game_instance[0]
        await self.score_logic(dealer)
        
        if dealer.GetScore() < 17:
            dealer.Draw(deck)
            await self.dealer_logic(ctx, game_instance, dealer)
        else:
            await self.game_result(ctx, game_instance, dealer)

    async def dealer_turn(self, ctx: commands.Context):
        this_guild = ctx.guild.id
        this_game_instance = self.game_instance[this_guild]
        await self.dealer_logic(ctx, this_game_instance, self.dealer)    

    async def start_turn(self, ctx: commands.Context, turn: int):
        this_guild = ctx.guild.id
        this_game_instance = self.game_instance[this_guild]
        num_players = len(this_game_instance)-2
        player = this_game_instance[turn+1]

        self.game_window = await ctx.send(f"Beginning turn {str(turn)}.")
        await self.game_logic(ctx, this_game_instance, player)

        if turn == num_players:
            await self.dealer_turn(ctx)
        else:
            await self.start_turn(ctx, turn+1)

    async def end_game(self, ctx: commands.Context):
        await ctx.send("Ending game...", delete_after=3)
        self.game_instance.pop(ctx.guild.id, None)
        self.dealer = None
        self.dealer_msg = None
        self.game_window = None

    @commands.command(help='Begin a blackjack game.')
    async def blackjack(self, ctx: commands.Context):
        try:
            this_guild = ctx.guild.id
            if this_guild not in self.game_instance:
                init_msg = await ctx.send("Building deck... Please wait.")
                self.game_instance[this_guild] = [Deck("blackjack", 0)]
                this_game_instance = self.game_instance[this_guild]
                deck = this_game_instance[0]
                deck.Shuffle()
                await init_msg.delete()
            else:
                raise exceptions.GameExists(ctx)

            prompt = await ctx.send(f"{ctx.author.mention} has started a Blackjack game! React below to join!" +
                                "\n Original user should type \'start\' once everyone has joined or \'cancel\'.")
            checkmark = "\u2705"
            await prompt.add_reaction(checkmark)
            cache_msg = utils.get(self.bot.cached_messages, id=prompt.id)

            def check(m):
                return (
                    (m.content.lower() == "start" or
                    m.content.lower() == "cancel")
                    and m.channel.id == ctx.channel.id
                    and m.author.id == ctx.author.id
                )
            response = await self.bot.wait_for('message', check=check)
            await response.delete()
            if response.content == "start":
                reaction = utils.get(cache_msg.reactions, emoji=checkmark)
                users = []
                start_msg = "Starting game with: "
                async for user in reaction.users():
                    users.append(user)
                    start_msg += f"{user.mention}"

                await prompt.delete()                
                if (len(users) < self.MIN_PLAYERS): raise exceptions.NotEnoughPlayers(ctx, self.MIN_PLAYERS)
                if (len(users) > self.MAX_PLAYERS): raise exceptions.TooManyPlayers(ctx, self.MAX_PLAYERS)

                for user in users:
                    this_game_instance.append(Player(user))
                
                await ctx.send(start_msg, delete_after=5)
                for player in this_game_instance[1:]:
                    player.Draw(deck)
                    player.Draw(deck)

                self.dealer = this_game_instance[1]
                self.dealer_msg = f"The dealer has {self.dealer.GetHand()[0].GetName()} and one card face down."
                await self.start_turn(ctx, 1)
            else:
                await prompt.delete()
                raise exceptions.GameCancelled(ctx)

        except exceptions.GameCancelled as error:
            await self.end_game(ctx)
            await self.send_error(ctx, error.message)
        except exceptions.NotEnoughPlayers as error:
            await self.end_game(ctx)
            await self.send_error(ctx, error.message)
        except exceptions.GameExists as error:
            await self.send_error(ctx, error.message)

# Rules based on: https://bicyclecards.com/how-to-play/blackjack/