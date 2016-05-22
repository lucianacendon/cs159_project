import collections
import itertools
import operator
from collections import OrderedDict
from collections import deque

import random
import matplotlib.pyplot as plt
import csv

import sys
import os

from Agent import Agent
from Agent import Agent_1
from deck import Deck
from player import Player
from strategy import Strategy

from deuces import Card
from deuces import Evaluator


N_PLAYERS = 3   # TODO: incorporate this into the game when initializing the players. Let the user decide how many players and its 
                # respective strategies

# Game Variables:
BUY_IN = 100
RAISE_AMT = 2

class Game:

    def __init__(self, small_blind=0, big_blind=0, raise_amounts=1, starting_card_count=2, community_card_count=5):

        # Constructor parameters
        self.players = OrderedDict()
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.raise_amounts = raise_amounts
        self.starting_card_count = starting_card_count
        self.community_card_count = community_card_count
        self.player_count = 0
        self.players_in_game = 0
        self.opp_actions = []

        # Rotate blinds
        self.iteration = 0
        self.dealer = 0   # position of dealer chip

        # Initialize deck
        self.deck = Deck()
        self.call = 0       # call this to remain in the game
        self.pot = 0



        self.blind_count = (small_blind > 0) + (big_blind > 0)

        # Create table containing preflop odds (to be consulted by strategies)
        self.preflop_odds_table = self.create_preflop_odds_table()


    def add_player(self, player):
        """
            This function adds a players to the game
        """
        self.players[self.player_count] = player   
        self.players[self.player_count].id = self.player_count  # This gives the players a fixed numerical index (an 'I.D')

        # Total players
        self.player_count += 1                                                
        
        # Total players that haven't folded
        self.players_in_game += 1
        

    def initializePlayerCards(self):
        """
            This function initializes player's hole cards (and the most recent actions set)
        """
        # most recent actions of all players before the current player
        self.last_player_actions = deque((self.player_count - 1) * [0], maxlen=(self.player_count - 1))
 
        for i in range(self.player_count):
            self.players[i].setHoleCards(self.deck.getPreFlop(
                number_of_cards=self.starting_card_count))
        return self.players


    def create_preflop_odds_table(self):
        """
            This function creates a python dictionary structure containing the probability that each possible preflop 
            hand will end-up being the best hand. This was done by using a table with precalculated odds (for speed)
            Reference: http://www.natesholdem.com/pre-flop-odds.php
            Note: 's' in the hand names means 'suited' and 'o' means 'off suit' 
        """
        preflop_odds = {}
        with open('./data/preflop_odds.txt', 'rb') as csv_file:
            reader = csv.reader(csv_file, delimiter='\t')
            for row in reader:
                preflop_odds[row[0]] = [row[1:]]

        return preflop_odds
    

    def create_hand_ranking(self):
        """
            Returns a list of handtags in increasing order of strenght (based on pre-flop odds)
        """
        i = 0
        handtag_rank = {}
        with open('./data/preflop_odds.txt', 'rb') as csv_file:
            reader = csv.reader(csv_file, delimiter='\t')
            for row in reader:
                if i > 0:
                    handtag_rank[row[0]] = row[self.player_count - 1]
                i += 1
        
        handtag_rank = sorted(handtag_rank.items(), key=operator.itemgetter(1))
        return handtag_rank


    def setBlinds(self):
        
        # Rotate dealer
        self.dealer = self.iteration % self.player_count
        self.iteration += 1

        if self.small_blind > 0:

            state = self.players[(self.dealer + 1) % self.player_count].states
            state[0] -= self.small_blind
            state[1] += self.small_blind
            state[2] = None 

            self.pot += self.small_blind
            self.call = self.small_blind

            self.last_player_actions.append('S')

        if self.big_blind > 0:

            state = self.players[
                (self.dealer + 2) % self.player_count].states
            state[0] -= self.big_blind
            state[1] += self.big_blind
            state[2] = None

            self.pot += self.big_blind
            self.call = self.big_blind

            self.last_player_actions.append('B')

        return self.pot, self.call

    
    def placeBets(self):

        i = self.blind_count + 1
        cur_player_index = (self.dealer + i) % self.player_count
        cur_player = self.players[cur_player_index]
        cur_state = self.players[cur_player_index].states                                                           

        # players bet until everyone either calls or folds
        # Maximum amount of bets is 4 per player
        allowed_rounds = 4 * self.player_count
        while not (cur_state[1] == self.call and (cur_state[2] == 'C' or cur_state[2] == 'R')) and allowed_rounds > 0:

            if self.players_in_game == 1:
                break 

            if cur_state[2] != 'F':

                if isinstance(cur_player, Agent):
                    action = cur_player.getAction(
                        game=self,
                        call=self.call,
                        raise_amt=RAISE_AMT)                

                else:   
                    action = self.players[cur_player_index].getAction(
                        player=self.players[cur_player_index],
                        game=self,
                        call=self.call,
                        raise_amt=RAISE_AMT)

                    self.opp_actions.append(action)
                

                if action == 'C':
                    diff = self.call - cur_state[1]

                    # your current funds must be at least the amount you bet
                    if cur_state[0] < diff:
                        # Set action to Fold and pass down to the Fold clause.
                        action = 'F'
                    else:
                        cur_state[0] -= diff
                        cur_state[1] += diff
                        self.pot += diff
                        cur_state[2] = 'C'
                        self.last_player_actions.append('C')

                # here we could also potentially set the bet amount to 0
                if action == 'F':
                    cur_state[2] = 'F'
                    self.last_player_actions.append('F')
                    self.players_in_game -= 1

                # need to decide raising conventions
                if action == 'R':                    # in real poker you can raise even if you haven't called (i.e. calling and raising above the call in one move)
                    diff = (self.call - cur_state[1]) + RAISE_AMT

                    cur_state[0] -= diff
                    cur_state[1] += diff
                    self.pot += diff

                    self.call += RAISE_AMT
                    cur_state[2] = 'R'
                    self.last_player_actions.append('R')

            # update recent actions to indicate player is out of game 'O' (he has folded in a previous round)
            else:
                self.last_player_actions.append('O')
                

            # move to next player (array viewed as circular table)
            i += 1
            cur_player_index = (self.dealer + i) % self.player_count
            cur_player = self.players[cur_player_index]
            cur_state = self.players[cur_player_index].states
            allowed_rounds -= 1

    
    def getCurrentPlayers(self):

        self.ingame_players = []

        for i in range(self.player_count):
            if self.players[i].states[2] != 'F':
                self.ingame_players.append(self.players[i].id)   # Keeps their ID stored to make it easier to identify them 
                                                                 # in the updatePlayerEarnings function

        return self.ingame_players


    # Here we also reset number of players_in_game
    # we might want to update the current funds in here as well
    def updatePlayerEarnings(self):

        winnings = (1.0 * self.pot) / len(self.ingame_players)

        # update current funds and earnings of the winners
        # also reset bet and last action
        for player_id in self.ingame_players:
            self.players[player_id].winUpdate(winnings)

        # Update the losers' states
        for player_id in range(self.player_count):
            if player_id not in self.ingame_players:
                self.players[player_id].loseUpdate()

        self.players_in_game = self.player_count

    # sets the funds of all the players back to the buy_in (to prevent accumulation)
    # note earnings is not reset
    def resetFunds(self, buy_in):
        for i in self.players:
            self.players[i].states[0] = buy_in

    def resetPot(self):
        self.pot = 0
    
    # We might want to make this a field of the Game objet instead of setting it for every player, but it prbly doesn't matter
    def showCommunityCards(self):

        community_cards = self.deck.getFlop(number_of_cards=5)

        for player_id in self.ingame_players:
            self.players[player_id].setCommunityCards(community_cards)


    # for debugging
    def printPlayerStates(self):
        for i in range(self.player_count):
            print self.players[i].states

    def playGame(self):

        self.resetPot()
        self.initializePlayerCards()
        self.setBlinds()
        self.placeBets()
        self.getCurrentPlayers()

        # Move onto post flop round
        if len(self.ingame_players) > 1:
            hand_scores = []
            self.showCommunityCards()       
            
            for player_id in self.ingame_players:
                hand_scores.append(self.players[player_id].getHandScore())

            best_score = min(hand_scores)
            winners = []
            for i in range(len(hand_scores)):
                if hand_scores[i] == best_score:
                    winners.append(self.ingame_players[i])

            self.ingame_players = winners


        # End game
        self.updatePlayerEarnings()



def main(): 

    action_numbers = {'F' : -1, 'C' : 0, 'R' : 1}
    numGames = 1000000
    n_players = 2
    buy_in = 20

    P = Player(Strategy.aggressiveStrategy, buy_in, n_players)
    A = Agent_1(buy_in, n_players)

    game = Game(small_blind=1, raise_amounts=1, starting_card_count=2)
    game.add_player(P)
    game.add_player(A)

    for j in xrange(1):
        for i in xrange(numGames):
            # print "============= Game %d =============" % i
            game.deck = Deck()

            # game.testPlayGame()
            game.playGame()

            if (i + 1) % 5 == 0:
                game.resetFunds(buy_in)

        print "Final Opponent Earnings:" + str(P.earnings / numGames)
        print "Final Agent Earnings: " + str(A.earnings / numGames)  
        # print A.Q  

    #     P.earnings = 0
    #     A.earnings = 0        

    hand_ranking = game.create_hand_ranking()

    # (call value + raise value) / 2 for each hand
    # This is calculated for the aggressive opponent, so the previous action will always be 'R'
    Q = A.Q
    learned_hand_values = []
    learned_best_actions = []
    for h in hand_ranking:
        state_tag = (h[0], ('R',))
        if state_tag in Q:
            action_values = Q[state_tag]
            sorted_actions = sorted(action_values.items(), key=operator.itemgetter(1), reverse=True)

        
            # print Q[state_tag]
            learned_hand_values.append(sorted_actions[0][1])
            learned_best_actions.append(action_numbers[sorted_actions[0][0]])

    # print learned_hand_values


    plt.plot(learned_hand_values)
    plt.xlabel('Hands (ordered by pre-flop odds)')
    plt.ylabel('Learned Value of Hand (value of max action given hand)')
    plt.title('Learned Hand Strength (%d iterations)' % numGames)
    plt.savefig('Learned Hand Strength (%d iterations)' % numGames, bbox_inches='tight')
    plt.clf()

    plt.plot(learned_best_actions, 'o')
    plt.xlabel('Hands (ordered by pre-flop odds)')
    plt.ylabel('Learned Best Action for Hand (F = -1, C = 1, R = 1)')
    plt.title('Learned Best Actions (%d iterations)' % numGames)
    plt.savefig('Learned Best Actions (%d iterations)' % numGames, bbox_inches='tight')
    plt.clf()


    # P.earnings = 0
    # A.earnings = 0

    # p_earnings = []
    # a_earnings = []
    # # it = []

    # for i in xrange(numGames):
    #     game.deck = Deck()

    #     game.playGame()

    #     p_earnings.append(P.earnings / (i + 1))
    #     a_earnings.append(A.earnings / (i + 1))
    #    # it.append(i)

    #     if (i + 1) % 5 == 0:
    #         game.resetFunds(buy_in)


    # Useful for debugging / analysis: writing opponent actions to a file for control
    # with open('opp_actions.txt','w') as f:
    #    for a in game.opp_actions:
    #        f.write(str(a) + '  ')

    # plt.semilogx(p_earnings,label='Opponent')
    # plt.semilogx(a_earnings,label='Agent')
    # plt.legend()
    # plt.xlabel('N. iterations')
    # plt.ylabel('Earnings')

    # plt.show()
    # print "Final Opponent Earnings:" + str(P.earnings / numGames)
    # print "Final Agent Earnings: " + str(A.earnings / numGames)

if __name__ == '__main__':
    main()












