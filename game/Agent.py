import collections
import itertools
import random
import operator
import numpy as np

from math import exp

from strategy import Strategy
from collections import deque
from player import Player

from deuces import Card
from deuces import Evaluator


class Agent(Player):

    def __init__(self, buy_in, n_players, ID=0):
        self.n_opponents = n_players - 1
        self.states = [buy_in, 0, None]   # [current funds, bet amount, action]
        self.earnings = 0.0
        self.id = ID
        self.Q = {}
        self.evaluator = Evaluator()

    def updateAlpha(self):
        n = self.iterations_trained / 1000
        self.alpha *= (.99 ** n)


    # Load Q function from file. Also loads the #iterations and updates the alpha
    def loadQ(self, fName):
        pass

    # update states upon winning a round
    def winUpdate(self, winnings):
        Player.winUpdate(self, winnings)
        self.QReward(winnings)

    # update states upon losing a round
    def loseUpdate(self):
        loss = Player.loseUpdate(self)
        # print "loss", loss
        self.QReward(loss)

        # otherwise opponent folded at start of game (could update opponent modeling here)            


class Agent_1(Agent):
    def __init__(self, buy_in, n_players, ID=0):
        Agent.__init__(self, buy_in, n_players, ID=0)
        
        self.prev_state = None
        self.prev_action = None                                 
        self.iterations_trained = 0
        self.e = 0.3 # value for e-greedy
        self.alpha = 0.1 # learning rate (will decrease with time)

        self.n_call = 0
        self.n_raise = 0
        self.n_games = 0 

    # update Q funciton using reward gained or lost
    def QReward(self, reward):
        if self.prev_state:
            # print reward
            # print self.alpha * (reward - self.Q[self.prev_state][self.prev_action])
            self.Q[self.prev_state][self.prev_action] += self.alpha * (reward - self.Q[self.prev_state][self.prev_action])

            self.prev_state = None
            self.prev_action = None 
        
    # We could combine all the state information into one state using a tuple (to make it Q[state][action]) vs. splitting it up
    # Learn Q-function using e-greedy. 
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
            action_set = ['F', 'C']

        # can do anything
        else:   
            action_set = ['F', 'C', 'R']        

        hand_tag = self.getHandTag()
        other_player_actions = tuple(game.last_player_actions)
        cur_state = (hand_tag, other_player_actions)


        r = random.uniform(0, 1)

        if cur_state in self.Q:
            action_values = self.Q[cur_state]
         #   print action_values
            sorted_actions = sorted(action_values.items(), key=operator.itemgetter(1), reverse=True) # actions ordered by value
         #   print sorted_actions
            max_action_value = sorted_actions[0][1]
         #   print max_action_value

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


        # slow-down learning
        if self.iterations_trained % 10000 == 0:
            self.alpha *= .99

        if self.iterations_trained % 50000 == 0:
            self.e *= .7

        self.action = action

        return action


    # get best action according to learned Q function (no exploration)
    def getActionTest(self, game, call, raise_amt):
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
            action_set = ['F', 'C']

        # can do anything
        else:   
            action_set = ['F', 'C', 'R']        

        hand_tag = self.getHandTag()
        other_player_actions = tuple(game.last_player_actions)
        cur_state = (hand_tag, other_player_actions)


        if cur_state in self.Q:
            action_values = self.Q[cur_state]
            sorted_actions = sorted(action_values.items(), key=operator.itemgetter(1), reverse=True) # actions ordered by value

            # action has not been decided yet
            if not action: 
                for a in sorted_actions:
                    # a : (action, value)
                    if a[0] in action_set: 
                        action = a[0]
                        break

        else:
            action = random.choice(action_set)

        return action


class Agent_2(Agent):
    """
        This agent is very similar to agent 1, but it also take into account also the actions 
        and respective cards of players in the last game 
    """
    def __init__(self, buy_in, n_players, ID=0):
        Agent.__init__(self, buy_in, n_players, ID=0)

        self.prev_state = None
        self.prev_action = None  
        self.iterations_trained = 0
        self.e = 0.3  # E value for e-greedy
        self.alpha = 0.1  # learning rate (decrease with time)

    def QReward(self, reward):
        if self.prev_state:

            self.Q[self.prev_state][self.prev_action] += self.alpha * (reward - self.Q[self.prev_state][self.prev_action])

            self.prev_state = None
            self.prev_action = None 


    def getAction(self, game, call, raise_amt):
        cur_funds = self.states[0]
        cur_bet = self.states[1]
        diff = call - cur_bet
        raise_bet = diff + raise_amt

        action = None
        
        if diff > cur_funds:  # can't call 
            action = 'F'   
        if raise_bet > cur_funds:   # can't raise
            action_set = ['F', 'C']
        else:    # can do anyt
            action_set = ['F', 'C', 'R']   

        hand_tag = self.getHandTag()

        # Actions and respective cards of all Opponents in previous game
        # The indexing removes the agent itself from the list
        opp_ac_prev_game = game.last_game_actions_list[:self.id] + game.last_game_actions_list[(self.id+1):]  
        opp_card_prev_game = game.last_game_actions_cards[:self.id] + game.last_game_actions_cards[(self.id+1):]

        action_cards = [0] * self.n_opponents

        for i in range(self.n_opponents):
            action_cards[i] = (opp_ac_prev_game[i], opp_card_prev_game[i])

        cur_state = (hand_tag, tuple(action_cards))

        print cur_state

        r = random.uniform(0, 1)


        if cur_state in self.Q:
            action_values = self.Q[cur_state]    # Contains the value of each action given the current state
            sorted_actions = sorted(action_values.items(), key=operator.itemgetter(1), reverse=True)  # actions ordered by value
            max_action_value = sorted_actions[0][1]  # Contains the maximum Q-value across all different actions 

            # if action has not been decided yet (still 'None')
            if not action:
                for a in sorted_actions:  # a = (action, value)
                    if a[0] in action_set:
                        action = a[0]      # maximum value action is the first one (actions are sorted)
                        break

                # E-greedy exploration
                if r < self.e:
                    action = random.choice(action_set)

        else:
            self.Q[cur_state] = {'F' : 0, 'C' : 0, 'R' : 0}  # initialize Q-value for this state

            if not action:
                action = random.choice(action_set)  # Randomly explores any action when there is not a good option to follow 
            max_action_value = 0


        if self.prev_state:
            # Learning update
            self.Q[self.prev_state][self.prev_action] += self.alpha * (max_action_value - self.Q[self.prev_state][self.prev_action])

        self.prev_state = cur_state
        self.prev_action = action
        self.iterations_trained += 1 

        # Slowing-down learning
        if self.iterations_trained % 10000 == 0:
            self.alpha *= .99

        if self.iterations_trained % 50000 == 0:
            self.e *= .7

        return action


# picks an action with probability proportional to its value
def weightedChoice(action_values):
    weights = []
    value = 0
    for a in action_values:
        value += exp(action_values[a])
        weights.append((a, value))

    r = random.uniform(0, value)
    for w in weights:
        if r < w[1]:
            return w[0]


class Agent_3(Agent_1):
    """
        Same as Agent_1, but uses softmax of each action value to nondeterministacally select an action
    """

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
            action_set = ['F', 'C']

        # can do anything
        else:   
            action_set = ['F', 'C', 'R']        

        hand_tag = self.getHandTag()
        other_player_actions = tuple(game.last_player_actions)
        cur_state = (hand_tag, other_player_actions)


        r = random.uniform(0, 1)

        if cur_state in self.Q:
            action_values = self.Q[cur_state]
            sorted_actions = sorted(action_values.items(), key=operator.itemgetter(1), reverse=True) # actions ordered by value
        
            max_action_value = sorted_actions[0][1]

            action = weightedChoice(action_values)


            # # e-greedy exploration
            # if r < self.e:
            #     action = random.choice(action_set)

        else:
            self.Q[cur_state] = {'F' : 0, 'C' : 0, 'R' : 0}
            
            if not action:
                action = random.choice(action_set)

            max_action_value = 0


        if self.prev_state:
            # Learning update 
            self.Q[self.prev_state][self.prev_action] += self.alpha * (max_action_value - self.Q[self.prev_state][self.prev_action])

        self.prev_state = cur_state
        self.prev_action = action
        self.iterations_trained += 1


        # Slowing-down learning
        if self.iterations_trained % 10000 == 0:
            self.alpha *= .99

        if self.iterations_trained % 50000 == 0:
            self.e *= .7

        return action



class Agent_4(Agent_1):
    """
        Agent_1, but also incorporates the pot into the state
    """

    def __init__(self, buy_in, n_players, ID=0):
        Agent_1.__init__(self, buy_in, n_players, ID=0)

        self.e = 0.2 # value for e-greedy

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
            action_set = ['F', 'C']

        # can do anything
        else:   
            action_set = ['F', 'C', 'R']        

        hand_tag = self.getHandTag()
        other_player_actions = tuple(game.last_player_actions)
        cur_state = (hand_tag, game.pot, other_player_actions) # also incorporate pot


        r = random.uniform(0, 1)

        if cur_state in self.Q:
            action_values = self.Q[cur_state]
            sorted_actions = sorted(action_values.items(), key=operator.itemgetter(1), reverse=True) # actions ordered by value
        
            max_action_value = sorted_actions[0][1]

            action = weightedChoice(action_values)


            # # e-greedy exploration
            # if r < self.e:
            #     action = random.choice(action_set)

        else:
            self.Q[cur_state] = {'F' : 0, 'C' : 0, 'R' : 0}
            
            if not action:
                action = random.choice(action_set)

            max_action_value = 0


        if self.prev_state:
            # Learning update 
            self.Q[self.prev_state][self.prev_action] += self.alpha * (max_action_value - self.Q[self.prev_state][self.prev_action])

        self.prev_state = cur_state
        self.prev_action = action
        self.iterations_trained += 1


        # Slowing-down learning
        if self.iterations_trained % 200000 == 0:
            self.alpha *= .99

        if self.iterations_trained % 500000 == 0:
            self.e *= .7

        return action



class Agent_5(Agent):
    # Agent 1, but also incorporates opponent modeling #

    def __init__(self, buy_in, n_players, ID=0):
        Agent.__init__(self, buy_in, n_players, ID=0)

        self.prev_state = None
        self.prev_action = None  
        self.iterations_trained = 0
        self.e = 0.3  # E value for e-greedy
        self.alpha = 0.1  # learning rate (decrease with time)

        self.n_call = 0
        self.n_raise = 0
        self.n_games = 0 

    def QReward(self, reward):
        if self.prev_state:

            self.Q[self.prev_state][self.prev_action] += self.alpha * (reward - self.Q[self.prev_state][self.prev_action])

            self.prev_state = None
            self.prev_action = None 

    
    def getAction(self, game, call, raise_amt):
        cur_funds = self.states[0]
        cur_bet = self.states[1]
        diff = call - cur_bet
        raise_bet = diff + raise_amt

        action = None
        
        if diff > cur_funds:  # can't call 
            action = 'F'   
        if raise_bet > cur_funds:   # can't raise
            action_set = ['F', 'C']
        else:    # can do anything
            action_set = ['F', 'C', 'R']   

        hand_tag = self.getHandTag()
        other_player_actions = tuple(game.last_player_actions)

        # Actions and respective cards of all Opponents in previous game
        # The indexing removes the agent itself from the list
        prev_game_call_rate = game.prev_game_call_track[:self.id] + game.prev_game_call_track[(self.id+1):] 
        prev_game_raise_rate = game.prev_game_raise_track[:self.id] + game.prev_game_raise_track[(self.id+1):] 

        cur_state = (hand_tag, other_player_actions, tuple(prev_game_call_rate), tuple(prev_game_raise_rate))

        #print cur_state

        r = random.uniform(0, 1)


        if cur_state in self.Q:
            action_values = self.Q[cur_state]    # Contains the value of each action given the current state
            sorted_actions = sorted(action_values.items(), key=operator.itemgetter(1), reverse=True)  # actions ordered by value
            max_action_value = sorted_actions[0][1]  # Contains the maximum Q-value across all different actions 

            # if action has not been decided yet (still 'None')
            if not action:
                for a in sorted_actions:  # a = (action, value)
                    if a[0] in action_set:
                        action = a[0]      # maximum value action is the first one (actions are sorted)
                        break

                # E-greedy exploration
                if r < self.e:
                    action = random.choice(action_set)

        else:
            self.Q[cur_state] = {'F' : 0, 'C' : 0, 'R' : 0}  # initialize Q-value for this state

            if not action:
                action = random.choice(action_set)  # Randomly explores any action when there is not a good option to follow 
            max_action_value = 0


        if self.prev_state:
            # Learning update
            self.Q[self.prev_state][self.prev_action] += self.alpha * (max_action_value - self.Q[self.prev_state][self.prev_action])

        self.prev_state = cur_state
        self.prev_action = action
        self.iterations_trained += 1 

        # Slowing-down learning
        if self.iterations_trained % 10000 == 0:
            self.alpha *= .99

        if self.iterations_trained % 50000 == 0:
            self.e *= .7

        return action

