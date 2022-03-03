import discord
from objects.deck import Deck
from objects.card import Card

class Player(object):
    def __init__(self, user: discord.member.Member):
        self.user = user
        self.cards = []
        self.score = 0

    def Draw(self, deck: Deck):
        # Draw a card into this player's hand from a Deck
        drawn_card = deck.Draw()
        self.cards.append(drawn_card)
        # Add to player's score.
        self.score += drawn_card.GetVal()

    def GetHand(self):
        # Get the hand of this player
        return self.cards

    def GetUser(self):
        # Get user of this player 
        return self.user
    
    def GetScore(self):
        # Get score of this player
        return self.score

    def SetScore(self, score: int):
        # Override current user score
        self.score = score

    
