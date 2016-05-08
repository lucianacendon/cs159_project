import collections
import itertools
import random
from strategy import Strategy

from deuces import Card
from deuces import Evaluator


class Player():
    # strategy is a function

    def __init__(self, strategy):
        self.getAction = strategy
        self.earnings = 0

    def setHoleCards(self, cards):
        assert len(cards) == 2
        self.hole_cards = cards

    def setCommunityCards(self, cards):
        assert len(cards) == 5
        self.community_cards = cards 

    # return score of best hand made up of hole cards and community cards
    def getHandScore(self):
        evaluator = Evaluator()
        hand = []
        board = []

        for c in self.hole_cards:
            hand.append(Card.new(c))

        for c in self.community_cards:
            board.append(Card.new(c))

        return evaluator.evaluate(board, hand)

        
    # these will be done in the simulator
    # def receive_flop(self):
    #     flop_cards = self.deck.get_flop()
    #     for i in range(len(flop_cards)):
    #         self.cards.append(self.deck.get_flop()[i])

    # def receive_turn(self):
    #     self.cards.append(self.deck.get_flop()[0])

    # def receive_river(self):
    #     self.cards.append(self.deck.get_river()[0])

    def getAction(self, env_state, raiseAmount):
        pass

    def fold(self):
        pass

    def call(self):
        pass

    def raiseAmount(self, amount):
        pass


if __name__ == '__main__':

    # random_player = Player(Strategy.randomStrategy)

    # histRandom = {"Call": 0, "Fold": 0, "Raise": 0}
    # for x in range(100000):
    #     action = random_player.getAction()
    #     histRandom[action] += 1.0 / 100000

    aggresive_player = Player(Strategy.aggresiveStrategy)

    histAggresive = {"Call": 0, "Fold": 0, "Raise": 0}
    for x in range(100000):
        action = aggresive_player.getAction()
        histAggresive[action] += 1

    try:
        # for action in histRandom:
        #     assert histRandom[action] < 0.35

        assert histAggresive['Raise'] / 100000 == 1

    except AssertionError as e:
        raise
    else:
        print "All tests passed!"
