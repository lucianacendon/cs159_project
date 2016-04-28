import collections
import itertools
import random

class Player():
    # strategy is a function
    def __init__(self, strategy):
        # is this how you set functions
        self.get_action = strategy


    def setHoleCards(self, cards):
        self.cards = cards

    # these will be done in the simulator
    # def receive_flop(self):
    #     flop_cards = self.deck.get_flop()
    #     for i in range(len(flop_cards)):
    #         self.cards.append(self.deck.get_flop()[i])

    # def receive_turn(self):
    #     self.cards.append(self.deck.get_flop()[0])

    # def receive_river(self):
    #     self.cards.append(self.deck.get_river()[0])

    def getAction(self, state):
        pass

    def fold(self):
        pass
    def call(self):
        pass
    def raiseAmount(self):
        pass