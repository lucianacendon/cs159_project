import collections
import itertools
import random

import sys
import os

from collections import OrderedDict
from deck import Deck
from player import Player
from strategy import Strategy

from deuces import Card
from deuces import Evaluator


class Game:
    # players is a list of players

    def __init__(self, players, small_blind=0, big_blind=0, buy_in=100, raise_amounts=1, starting_card_count=2, community_card_count=5):

        # Constructor parameters
        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.buy_in = buy_in
        self.raise_amounts = raise_amounts
        self.starting_card_count = starting_card_count
        self.community_card_count = community_card_count

        self.player_count = len(players)

        # Initialize deck
        self.deck = Deck()
        self.curr_bet = 0   # call this to remain in the game
        self.dealer = 0          # position of dealer chip
        self.pot = 0

        self.blind_count = (small_blind > 0) + (big_blind > 0)

        # player states
        self.player_states = OrderedDict()

    
    def initializePlayersStates(self):

        for player in self.players:
            player.setHoleCards(self.deck.getPreFlop(
                number_of_cards=self.starting_card_count))

            # [current funds, bet amount, action, score]
            self.player_states[player] = [self.buy_in, 0, None, 0]

        return self.player_states

    
    def setBlinds(self):

        if self.small_blind > 0:

            state = self.player_states[self.players[self.dealer + 1]]
            state[0] -= self.small_blind
            state[1] += self.small_blind
            state[2] = None

            self.pot += self.small_blind
            self.curr_bet = self.small_blind

        if self.big_blind > 0:

            state = self.player_states[self.players[
                (self.dealer + 2) % self.player_count]]
            state[0] -= self.big_blind
            state[1] += self.big_blind
            state[2] = None

            self.pot += self.big_blind
            self.curr_bet = self.big_blind

        return self.pot, self.curr_bet

    
    def placeBets(self):
       
        i = self.blind_count + 1
        curr_player_index = (self.dealer + i) % self.player_count
        curr_state = self.player_states[self.players[curr_player_index]]

        # players bet until everyone either calls or folds
        # TODO: Infinite loop occurs occasionally. Fix
        while not (curr_state[2] == 'Call' and curr_state[1] == self.curr_bet):

            if curr_state[2] != 'Fold':
                action = self.players[curr_player_index].getAction(
                    player=self.players[curr_player_index],
                    env_state=self.player_states,
                    raise_amt=5)

                # here we could also potentially set the bet amount to 0
                if action == 'Fold':
                    curr_state[2] = 'Fold'

                if action == 'Call':
                    diff = self.curr_bet - curr_state[1]

                    # your current funds must be at least the amount you bet
                    assert(curr_state[0] >= diff)

                    curr_state[0] -= diff
                    curr_state[1] += diff
                    self.pot += diff
                    curr_state[2] = 'Call'

                # need to decide raising conventions
                if action == 'Raise':
                    raise_amt = 5

                    # in real poker you can raise even if you haven't called (i.e. calling and raising above the call in one move)
                    diff = (self.curr_bet - curr_state[1]) + raise_amt
                    assert(curr_state[0] >= diff) # TODO: this returns an error sometimes, need to fix

                    curr_state[0] -= diff
                    curr_state[1] += diff
                    self.pot += diff

                    self.curr_bet += raise_amt
                    curr_state[2] = 'Raise'

            # move to next player (array viewed as circular table)
            i += 1
            curr_player_index = (self.dealer + i) % self.player_count
            curr_state = self.player_states[self.players[curr_player_index]]

    
    def getCurrentPlayers(self):

        self.ingame_players = []
        for player in self.player_states:

            if self.player_states[player][2] != 'Fold':
                self.ingame_players.append(player)

        return self.ingame_players

    
    def updatePlayerEarnings(self):
        # Winner 
        # we might want to update the current funds in here as well 
        # currently we're updating the score and the earnings (seems like they're both recording the same thing)
        # if len(self.ingame_players) == 1:
        #     self.player_states[self.ingame_players[0]][3] = self.pot
        #     self.ingame_players[0].earnings += self.pot

        winnings = (1.0 * self.pot) / len(self.ingame_players)
        # update current funds, score, and earnings (we might want to delete one of those two) of the winners
        # also reset bet and last action
        for player in self.ingame_players:
            self.player_states[player][0] += winnings
            self.player_states[player][3] += winnings
            player.earnings += winnings

            self.player_states[player][1] = 0
            self.player_states[player][2] = None


        # Update the losers' states
        for player in self.player_states:
            if player not in self.ingame_players:

                loss = self.player_states[player][1]

                self.player_states[player][3] -= loss
                player.earnings -= loss

                self.player_states[player][1] = 0
                self.player_states[player][2] = None

    
    # We might want to make this a field of the Game objet instead of setting it for every player, but it prbly doesn't matter
    def showCommunityCards(self):

        community_cards = self.deck.getFlop(number_of_cards=5)

        for player in self.ingame_players:
            player.setCommunityCards(community_cards)


    # for debugging
    def printPlayerStates(self):
        
        i = 1
        for p in self.player_states:
            print str(i) + " :" + str(self.player_states[p])
            i += 1

        print

    def playGame(self):

        self.initializePlayersStates()        
        self.setBlinds()
        self.placeBets()
        self.getCurrentPlayers()

        # Move onto post flop round
        if len(self.ingame_players) > 1:
            hand_scores = []
            self.showCommunityCards()
            
            for player in self.ingame_players:
                hand_scores.append(player.getHandScore())

            best_score = min(hand_scores)
            winners = []
            for i in xrange(len(hand_scores)):
                if hand_scores[i] == best_score:
                    winners.append(self.ingame_players[i])

            self.ingame_players = winners


        # End game
        self.updatePlayerEarnings()


    def testPlayGame(self):

        self.initializePlayersStates()
        print "Initial states :"
        self.printPlayerStates()
        
        self.setBlinds()
        print "After blinds :"
        self.printPlayerStates()

        self.placeBets()
        print "After betting round :"
        self.printPlayerStates()

        self.getCurrentPlayers()
        print "Players in after betting :"
        print self.ingame_players

        # Move onto post flop round
        if len(self.ingame_players) > 1:
            hand_scores = []
            self.showCommunityCards()
            
            for player in self.ingame_players:
                hand_scores.append(player.getHandScore())

            best_score = min(hand_scores)
            winners = []
            for i in xrange(len(hand_scores)):
                if hand_scores[i] == best_score:
                    winners.append(self.ingame_players[i])

            self.ingame_players = winners

            print "Winners :"
            print self.ingame_players

        # End game
        self.updatePlayerEarnings()

        print "After updating earnings :"
        self.printPlayerStates()


def main():

    P1 = Player(Strategy.randomStrategy)
    P2 = Player(Strategy.randomStrategy)
    P3 = Player(Strategy.randomStrategy)
    P4 = Player(Strategy.randomStrategy)
    P5 = Player(Strategy.randomStrategy)

    game = Game([P1, P2, P3, P4, P5], small_blind=5, big_blind=10,
                buy_in=50, raise_amounts=2, starting_card_count=2)
    game.initializePlayersStates()
    game.setBlinds()

    game.placeBets()
    game.getCurrentPlayers()

    try:

        call_count = 0
        for i, key in enumerate(game.player_states):
            assert game.players[i] is key
            call_count += game.player_states[key][2] == 'Call'

        assert call_count == len(game.ingame_players)

    except AssertionError as e:
        raise
    else:
        print "All tests passed!"

    game = Game([P1, P2, P3, P4, P5], small_blind=5, big_blind=10,
                buy_in=50, raise_amounts=2, starting_card_count=2)

    game.testPlayGame()




if __name__ == '__main__':
    main()


























