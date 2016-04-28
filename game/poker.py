import collections
import itertools
import random

import sys
import os

from deck import Deck
from player import Player

class Game:
    # players is a list of players
    def __init__(self, num_games, players, buy_in, small_blind, big_blind, raise_amounts, number_of_starting_cards):
        
        self.players = players
        self.player_count = len(players)
        self.win_stats = [0] * len(players)
        self.deck = Deck()

        self.number_of_starting_cards = number_of_starting_cards
    

    def initializePlayersStates(self):

        deck = self.deck
        players = self.players
        
        self.player_states = []

        for player in players:
            player.setHoleCards(deck.getPreFlop(number_of_cards=self.number_of_starting_cards))

            state = [player, self.buy_in, 0, None]
            self.player_states.append(state)

        return self.player_states


    ''' This method needs to be a little more robust to edge cases. '''
    def setBlinds(self):
        
        self.curr_bet = 0   # call this to remain in the game

        dealer = 0          # position of dealer chip
        pot = 0

        if self.small_blind > 0:
            
            state = self.player_states[dealer + 1]
            state[1] -= self.small_blind
            state[2] += self.small_blind
            
            pot += self.small_blind
            self.curr_bet = self.small_blind

        
        if self.big_blind > 0:
            
            state = self.player_states[(dealer + 2) % n]
            state[1] -= self.big_blind
            state[2] += self.big_blind
            
            pot += self.big_blind
            self.curr_bet = self.big_blind

        return pot, cur_bet


    def placeBets(self, i=3):

        curr_player = (dealer + i) % self.player_count 
        curr_state = player_states[curr_player]

        # players bet until everyone either calls or folds
        ''' Loop condition seems wrong. Check edge cases '''
        while not (curr_state[3] == 'Call' and curr_state[2] == self.curr_bet):

            if curr_state[3] != 'Fold':

                action = curr_state[0].get_action(player_states)

                if action == 'Fold':

                    curr_state[2] = 0
                    curr_state[3] = 'Fold'

                if action == 'Call':

                    diff = cur_bet - curr_state[2]
                    curr_state[1] -= diff
                    curr_state[2] += diff
                    pot += diff
                    curr_state[3] = 'Call'

                # need to decide raising conventions
                #if action == 'R':
                #    pass

            # move to next player (array viewed as circular table)
            i += 1
            curr_player = (dealer + i) % self.player_count 
            curr_state = self.player_states[curr_player]


    def getCurrentPlayers(self):
        
        self.ingame_players = []
        for p_state in player_states:

            if p_state[3] != 'Fold':
                self.ingame_players.append(p_state)


    def playGame(self, num_rounds):
        

        n = len(self.players)
        
        self.initializePlayersStates()
        self.setBlinds()

        self.placeBets(i=3)        
        self.getCurrentPlayers()


        ''' Deal community cards now if more than one player in in_game_players. no more raises '''
        ## TODO: 



def main():
    
    d = Deck()

    P1 = Player(None)
    P1.setHoleCards(d.getPreFlop())
    print P1.cards

    # P1 = Player()
    # print P1.cards, P1.hand
    # P1.receive_flop()
    # print P1.cards, P1.hand
    # P1.receive_turn()
    # print P1.cards, P1.hand
    # P1.receive_river()
    # print P1.cards, P1.hand


if __name__ == '__main__':
    main()

