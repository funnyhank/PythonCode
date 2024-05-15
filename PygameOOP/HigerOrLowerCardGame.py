'''
In this game, eight cards are randomly chosen from a deck. The first card is shown
face up. The game asks the player to predict whether the next card in the selection
will have a higher or lower value than the currently showing card.
For example, say the card that’s shown is a 3. The player chooses “higher,” and the
 next card is shown. If that card has a higher value, the player is correct. In this
 example, if the player had chosen “lower,” they would have been incorrect.
If the player guesses correctly, they get 20 points. If they choose incorrectly, they
 lose 15 points. If the next card to be turned over has the
same value as the previous card, the player is incorrect.
'''
import random

SUIT_TUPLE = ('Spades', 'Hearts', 'Clubs', 'Diamonds')
Rank_TUPLE = ('Ace', '2', '3', '4', '5', '6', '7', '8', '9',
              '10', 'Jack', 'Queen', 'King')

NCARDS = 8


def getCard(deckListIn):  # this function returns a random card from the deck
    thisCard = deckListIn.pop()
    return thisCard


def shuffle(deckListIn):  # this function returns a shuffled copy of the deck
    deckListOut = deckListIn.copy()
    random.shuffle(deckListOut)
    return deckListOut
