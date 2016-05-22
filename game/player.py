import collections
import itertools
import random
import operator
from strategy import Strategy

from collections import deque

from deuces import Card
from deuces import Evaluator



cardRank = {'A' : 14, 'K' : 13, 'Q' : 12, 'J' : 11, 'T' : 10, '9' : 9, '8' : 8, '7' : 7, '6' : 6, '5' : 5, '4' : 4, '3' : 3, '2' : 2}

class Player():
    # strategy is a function

    def __init__(self, strategy, buy_in, n_players, ID=0):
        self.getAction = strategy
        self.n_opponents = n_players-1
        self.earnings = buy_in
        self.states = [buy_in, 0, None]   # [current funds, bet amount, action]
        self.id = ID
        self.evaluator = Evaluator()

    def setHoleCards(self, cards):
        assert len(cards) == 2
        self.hole_cards = cards


    def setCommunityCards(self, cards):
        assert len(cards) == 5
        self.community_cards = cards 

    # return score of best hand made up of hole cards and community cards
    def getHandScore(self):
        
        hand = [Card.new(c) for c in self.hole_cards]
        board = [Card.new(c) for c in self.community_cards]

        return self.evaluator.evaluate(board, hand)

    # update states upon winning a round
    # 0 = Current funds, 1 = bet amount, 2 = Action
    def winUpdate(self, winnings):
        self.states[0] += winnings
        self.earnings += winnings

        self.states[1] = 0
        self.states[2] = None

    # update states upon losing a round, returns loss
    # 0 = Current funds, 1 = bet amount, 2 = Action
    def loseUpdate(self):
        loss = self.states[1]

        self.earnings -= loss
        self.states[1] = 0
        self.states[2] = None

        return -loss  


    # return tag summarizing two card hand as a string 
    def getHandTag(self):

        card1Num, card1Suit = self.hole_cards[0][0], self.hole_cards[0][1]
        card2Num, card2Suit = self.hole_cards[1][0], self.hole_cards[1][1]

        if card1Num == card2Num:
            return card1Num + card2Num

        card1Val = cardRank[card1Num]
        card2Val = cardRank[card2Num]
        if card1Suit == card2Suit:
            if card1Val > card2Val:
                return card1Num + card2Num + 's'

            else:
                return card2Num + card1Num + 's'

        else: 
            if card1Val > card2Val:
                return card1Num + card2Num + 'o'

            else:
                return card2Num + card1Num + 'o'          


    def get_preflop_odds(self,preflop_odds_table,hole_cards):
        """
            This functions searches the preflop_odds_table for the winning odds of a given 
            preflop hand given by the "hole_cards" for a given number of players
        """
        # First, we need to assign a proper "tag" to be searched in the table
        card1 = list(hole_cards[0])
        card2 = list(hole_cards[1])

        # If the card number is the same, they cannot be suited
        if card1[0] == card2[0]:
            tag=str(card1[0])+str(card2[0])
            odds=preflop_odds_table[tag][0][self.n_opponents-1]

        else:
            try:
                # Checking if suit is the same
                if card1[1] == card2[1]:
                    tag=str(card1[0])+str(card2[0])+'s'
                else:
                    tag=str(card1[0])+str(card2[0])+'o'

                odds=preflop_odds_table[tag][0][self.n_opponents-1]

            except KeyError: # Higher value should come first in the tag
                if card1[1] == card2[1]:
                    tag=str(card2[0])+str(card1[0])+'s'
                else:
                    tag=str(card2[0])+str(card1[0])+'o'

                odds=preflop_odds_table[tag][0][self.n_opponents-1]

        return odds

    def getAction(self, game, call, raise_amt):
        pass














