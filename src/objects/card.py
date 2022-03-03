# French-suited standard playing card format
class Card(object):     

    def __init__(self, suit: str, value: int, type: str, name=None):
        self.suit = suit
        self.value = value
        self.type = type
        self.name = f"{name} of {suit}" if name is not None else f"{str(value)} of {suit}" # Set name if specified, else value.

    def GetSuit(self):
        # Get suit of card.
        return self.suit
    
    def GetVal(self):
        # Get value of card.
        return self.value

    def GetName(self):
        # Get name of card.
        return self.name

    def GetType(self):
        # Get type of card.
        return self.type