import random
from objects.card import Card

# Build deck of playing cards using Card object.
class Deck(object):

    def __init__(self, version: str, joker: int):
        self.cards = [] # initialise empty 
        self.Build(version, joker)

    def Build(self, version: str, joker: int):
        if (version == "standard"): # Standard 52-deck
            suits = ["Clubs", "Diamonds", "Hearts", "Spades"]
            names = {1: "Ace", 11: "Jack", 12: "Queen", 13: "King"}
            for suit in suits:
                for i in range(1, 14):
                    if i < 2:
                        self.cards.append(Card(suit, i, "ACE", names[i]))
                    elif i > 10:
                        self.cards.append(Card(suit, i, "FACE", names[i]))
                    else:
                        self.cards.append(Card(suit, i, "NUMBER"))
        elif(version == "blackjack"): # Standard 52-deck with scores for Blackjack
            suits = ["Clubs", "Diamonds", "Hearts", "Spades"]
            names = {1: "Ace", 11: "Jack", 12: "Queen", 13: "King"}
            for suit in suits:
                for i in range(1, 14):
                    if i < 2:
                        self.cards.append(Card(suit, i, "ACE", names[i]))
                    elif i > 10:
                        self.cards.append(Card(suit, 10, "FACE", names[i]))
                    else:
                        self.cards.append(Card(suit, i, "NUMBER"))

        for i in range(0, joker): # Add specified Jokers.
            self.cards.append(Card("Joker", 0, "SPECIAL"))

    def Shuffle(self):
        # Shuffle deck
        random.shuffle(self.cards) # Using random module to shuffle list.

    def Draw(self): 
        # Get card from top deck and remove from deck
        card = self.cards[0] # Get top card from deck
        self.cards.pop(0) # Remove top card from deck
        return card 

    def Show(self):
        # Get cards in deck
        return self.cards


