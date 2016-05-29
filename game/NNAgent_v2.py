from __future__ import division

import collections
import itertools
import random
import operator
import numpy as np
import csv

from neuralnet import NeuralNetwork
from Agent import Agent

from math import exp

from strategy import Strategy
from collections import deque
from player import Player

from deuces import Card
from deuces import Evaluator



#cardRank = {'A' : 12, 'K' : 11, 'Q' : 10, 'J' : 9, 'T' : 8, '9' : 7, '8' : 6, '7' : 5, '6' : 4, '5' : 3, '4' : 2, '3' : 1, '2' : 0}
#suitRank = {'s' : 3, 'c' : 2, 'd' : 1, 'h' : 0}
action_numbers = {'F' : 0.2 , 'C' : 0.4, 'R' : 0.6, 'S' : 0.8, 'O' : 1, 0 : 0}
actions = ['F', 'C', 'R']


class NNAgent_v2(Agent):

    def __init__(self, buy_in, n_players, ID=0):
        self.n_opponents = n_players - 1
        self.states = [buy_in, 0, None]   # [current funds, bet amount, action]
        self.earnings = 0
        self.id = ID
        self.evaluator = Evaluator()

        self.num_opp_actions = 5
       # self.num_feature_elements = 169 + (self.num_opp_actions * self.n_opponents) + 3
        self.num_feature_elements = 1 + self.n_opponents+1 +1   # one element representing the hand, "n_opponents"+1 representing the 
                                                                # actions of each player and one more representing the action of the agent
        self.batch_size = 50000 # could have this as a parameter

        # initialize neural network
        self.network = NeuralNetwork(test_mnist=False, input_layer_size=self.num_feature_elements)

        # array of feature vectors
        #self.X_train = np.empty([self.batch_size, self.num_feature_elements])
        self.X_train = np.empty([self.batch_size, self.num_feature_elements])
        # array of target values (i.e. Q(feature vector))
        self.y_train = np.empty([self.batch_size, 1])        

        self.prev_state_action_vector = None
        self.e = 0.3 # value for e-greedy
        self.iteration_num = 0

        self.tag_dict = {}

        self.create_tag_dict()

    def create_tag_dict(self):
        # Assigns normalized values to each tag

        index = float(1/169)
        tag_dict = {}
        with open('./data/tag_list.txt', 'rb') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                tag_dict[row[0]] = round(index,3)
                index += float(1/169)
            
        self.tag_dict = tag_dict



    def getCardNum(self, c):
        return self.tag_dict[c]        

    
    # get output of neural network
    def Q(self, vector):
        return self.network.predict(vector)

    def trainQ(self):
        self.network.updateData(train_data=self.X_train, train_labels=self.y_train, input_layer_size=self.num_feature_elements)
        self.network.train(num_epochs=10)

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

        # 52 elements to represent the hand, number opponents elements * 3 elements to represent last actions, 3 elements to represent agents action
        state_action_vector = np.zeros(1 + self.n_opponents+1 +1)

        # indicating the hand
        state_action_vector[0] = self.getCardNum(self.getHandTag())

       # other_player_actions = tuple(game.last_player_actions)

        for i in range(len(game.last_player_actions)):
            state_action_vector[i+1] = action_numbers[game.last_player_actions[i]]
        # indicating the opp. actions
        #for i in xrange(self.n_opponents):
            
           # state_action_vector[ + self.num_opp_actions * i + action_numbers[other_player_actions[i]]] = 1
    
    #    num_state_features = 52 + (self.num_opp_actions * self.n_opponents)
        
        if not action:
            # net has not been trained yet
            if self.iteration_num < self.batch_size:
                max_action_value = 0
                action = random.choice(action_set)

            else:
                r = random.uniform(0, 1)
                
                max_action_value = -np.inf
                max_legal_action_value = -np.inf # might not be able to do every action

                # choose best possible action
             #   for (i, a) in enumerate(actions):
                for i in actions:           
                    state_action_vector[len(state_action_vector)-1] = action_numbers[i]

                    action_value = self.Q(state_action_vector)

                    if action_value > max_action_value: 
                        max_action_value = action_value
                    
                    if i in action_set:
                        if action_value > max_legal_action_value:
                            max_legal_action_value = action_value
                            action = i

                    # state_action_vector[num_state_features + i] = 0

                # e-greedy exploration
                if r < self.e:
                    action = random.choice(action_set)

        else:
            max_action_value = 0
                
        # print action
       # state_action_vector[num_state_features + action_numbers[action]] = 1

        if self.prev_state_action_vector is not None:
            self.X_train[self.iteration_num % self.batch_size] = self.prev_state_action_vector
            self.y_train[self.iteration_num % self.batch_size] = np.array(max_action_value)

            self.iteration_num += 1
            if self.iteration_num % self.batch_size == 0:
                self.trainQ()

        self.prev_state_action_vector = state_action_vector

        state_action_vector[len(state_action_vector)-1] = action_numbers[action]

        return action

    # add reward to training set
    def QReward(self, reward):
        if self.prev_state_action_vector is not None:
            self.X_train[self.iteration_num % self.batch_size] = self.prev_state_action_vector
            self.y_train[self.iteration_num % self.batch_size] = np.array(reward)

            self.iteration_num += 1
            if self.iteration_num % self.batch_size == 0:
                self.trainQ()

            self.prev_state_action_vector = None


