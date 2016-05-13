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
        self.earnings = 0
        self.states = [buy_in, 0, None]   # [current funds, bet amount, action]
        self.id = ID

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

    # return tag summarizing two card hand as a string 
    def getHandTag(self):
        card1Num, card1Suit = self.hole_cards[0][0], self.hole_cards[0][1]
        card2Num, card2Suit = self.hole_cards[1][0], self.hole_cards[1][1]

        if card1Num == card2Num:
            return card1Num + card2Num

        if card1Suit == card2Suit:
            card1Val = cardRank[card1Num]
            card2Val = cardRank[card2Num]

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

        
    # these will be done in the simulator
    # def receive_flop(self):
    #     flop_cards = self.deck.get_flop()
    #     for i in range(len(flop_cards)):
    #         self.cards.append(self.deck.get_flop()[i])

    # def receive_turn(self):
    #     self.cards.append(self.deck.get_flop()[0])

    # def receive_river(self):
    #     self.cards.append(self.deck.get_river()[0])

    def getAction(self, game, call, raise_amt):
        pass




class Agent(Player):

    def __init__(self, buy_in, n_players, ID=0):
        self.n_opponents = n_players-1
        self.earnings = 0
        self.states = [buy_in, 0, None, 0]   # [current funds, bet amount, action]
        self.id = ID
        
        self.Q = {}
        self.last_state = None
        self.last_action = None
        self.iterations_trained = 0
        self.e = .01 # value for e-greedy
        self.alpha = .1 # learning rate (will decrease with time)


    def updateAlpha(self):
        n = self.iterations_trained / 1000
        self.alpha *= (.99 ** n)

    # Load Q function from file. Also loads the #iterations and updates the alpha
    def loadQ(self, fName):
        pass


    # For now, this is just training the Q-function using e-greedy. Eventually, we should have two functions, one that trains
    # and one that picks the optimal action that we use for testing.
    # We could combine all the state information into one state using a tuple (to make it Q[state][action]) vs. splitting it up
    def getAction(self, game, call, raise_amt):
        cur_funds = self.states[0]
        cur_bet = self.states[1]
        diff = call - cur_bet
        raise_bet = diff + raise_amt

        # can't call
        if diff > cur_funds:
            return 'F'

        # can't raise
        if raise_bet > cur_funds:
            action_set = ['F', 'C']

        # can do anything
            action_set = ['F', 'C', 'R']        

        hand_tag = self.getHandTag()
        prev_actions = tuple(game.last_player_actions)
        # pot = game.pot
        cur_state = (hand_tag, prev_actions) 

        r = random.uniform(0, 1)

        if cur_state in self.Q:
            # get action with max value
            action_values = self.Q[cur_state]
            action = max(action_values.iteritems(), key=operator.itemgetter(1))[0]

            # value of Q(state, action)
            cur_value = self.Q[cards][prev_actions][action]
            
            # e-greedy exploration
            if r < self.e:
                action = random.choice(['F', 'C', 'R'])

        else:
            self.Q[cur_state] = {'F' : 0, 'C' : 0, 'R' : 0}
            action = random.choice(['F', 'C', 'R'])

            cur_value = 0

        # learning update (cur_value is max value at current state)
        self.Q[self.last_state][self.last_action] += self.alpha * (cur_value - self.Q[self.last_state][self.last_action])

        return action


    # get reward for current round, update agent fields
    def endRound(self, game, reward):
        Q_prev_state = self.Q[self.last_state[0]][self.last_state[1]]
        Q_prev_state[self.last_action] += self.learningRate() * (reward - Q_prev_state[self.last_action])


    # def lear















# if __name__ == '__main__':

    # random_player = Player(Strategy.randomStrategy)

    # histRandom = {"Call": 0, "Fold": 0, "Raise": 0}
    # for x in range(100000):
    #     action = random_player.getAction()
    #     histRandom[action] += 1.0 / 100000

#    aggresive_player = Player(Strategy.aggresiveStrategy)

#    histAggresive = {"Call": 0, "Fold": 0, "Raise": 0}
#    for x in range(100000):
#        action = aggresive_player.getAction()
#        histAggresive[action] += 1

#    try:
        # for action in histRandom:
        #     assert histRandom[action] < 0.35

#        assert histAggresive['Raise'] / 100000 == 1

 #   except AssertionError as e:
 #       raise
 #   else:
 #       print "All tests passed!"























