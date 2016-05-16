import collections
import itertools
import random
import operator

from strategy import Strategy
from collections import deque
from player import Player

from deuces import Card
from deuces import Evaluator



class Agent(Player):

    def __init__(self, buy_in, n_players, ID=0):
        self.n_opponents = n_players-1
        self.earnings = 0
        self.states = [buy_in, 0, None]   # [current funds, bet amount, action]
        self.id = ID
        
        self.Q = {}
        self.prev_state = None
        self.prev_action = None
        self.iterations_trained = 0

        self.e = 0.25 # value for e-greedy
        self.alpha = 0.1 # learning rate (will decrease with time)
        
        self.evaluator = Evaluator()

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

        action = None

        # can't call 
        if diff > cur_funds:
            action = 'F'

        # can't raise
        if raise_bet > cur_funds:
            # you can call automatically 
            if diff == 0:
                action = 'C'
            
            else:
                action_set = ['F', 'C']

        # can do anything
        else:
            if diff == 0:
                action_set = ['C', 'R']
            
            else: 
                action_set = ['F', 'C', 'R']        

        hand_tag = self.getHandTag()
        other_player_actions = tuple(game.last_player_actions)
        cur_state = (hand_tag, other_player_actions)


        r = random.uniform(0, 1)

        if cur_state in self.Q:
            action_values = self.Q[cur_state]
            sorted_actions = sorted(action_values.items(), key=operator.itemgetter(1), reverse=True) # actions ordered by value
            #print sorted_actions
            max_action_value = sorted_actions[0][1]

            # action has not been decided yet
            if not action: 
                for a in sorted_actions:
                    # a : (action, value)
                    if a[0] in action_set: 
                        action = a[0]
                        break

                # e-greedy exploration
                if r < self.e:
                    action = random.choice(action_set)

        else:
            self.Q[cur_state] = {'F' : 0, 'C' : 0, 'R' : 0}
            
            if not action:
                action = random.choice(action_set)

            max_action_value = 0



        if self.prev_state:
            # learning update
            self.Q[self.prev_state][self.prev_action] += self.alpha * (max_action_value - self.Q[self.prev_state][self.prev_action])

        self.prev_state = cur_state
        self.prev_action = action
        self.iterations_trained += 1

        self.alpha *= .99
        self.e *= 0.99

        return action


    # update states upon winning a round
    def winUpdate(self, winnings):
        Player.winUpdate(self, winnings)
        self.QReward(winnings)


    # update states upon losing a round
    def loseUpdate(self):
        Player.loseUpdate(self)
        self.QReward(self.states[1])


    # update Q funciton using reward gained or lost
    def QReward(self, reward):
        if self.prev_state:
            self.Q[self.prev_state][self.prev_action] += self.alpha * (reward - self.Q[self.prev_state][self.prev_action])

            self.prev_state = None
            self.prev_action = None 

        # otherwise opponent folded at start of game (could update opponent modeling here)           





