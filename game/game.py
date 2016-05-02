import collections
import itertools
import random

import sys
import os

from collections import OrderedDict
from deck import Deck
from player import Player
from strategy import Strategy


class Game:
    # players is a list of players

    def __init__(self, players, small_blind=0, big_blind=0, buy_in=100, raise_amounts=1, starting_card_count=2):

        # Constructor parameters
        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.buy_in = buy_in
        self.raise_amounts = raise_amounts
        self.starting_card_count = starting_card_count

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
            state[2] = 'None'

            self.pot += self.small_blind
            self.curr_bet = self.small_blind

        if self.big_blind > 0:

            state = self.player_states[self.players[
                (self.dealer + 2) % self.player_count]]
            state[0] -= self.big_blind
            state[1] += self.big_blind
            state[2] = 'None'

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

                if action == 'Fold':
                    curr_state[2] = 'Fold'

                if action == 'Call':
                    diff = self.curr_bet - curr_state[1]
                    curr_state[0] -= diff
                    curr_state[1] += diff
                    self.pot += diff
                    curr_state[2] = 'Call'

                # need to decide raising conventions
                if action == 'Raise':
                    raise_amt = 5
                    curr_state[0] -= raise_amt
                    curr_state[1] += raise_amt
                    self.pot += raise_amt
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

    def updatePlayerEarnings(self):
        # Winner
        if len(self.ingame_players) == 1:
            self.player_states[self.ingame_players[0]][3] = self.pot
            self.ingame_players[0].earnings += self.pot

        # Update the ones who have folded
        else:
            for player in self.player_states:
                if player not in self.ingame_players:

                    loss = self.player_states[player][1]

                    self.player_states[player][3] -= loss
                    player.earnings -= loss

    def playGame(self, num_rounds):

        self.initializePlayersStates()
        self.setBlinds()
        self.placeBets()

        self.getCurrentPlayers()
        self.updatePlayerEarnings()

        # Move onto post flop round
        # TODO: Deal community cards now if more than one player in
        # in_game_players. no more raises

        # End game
        self.updatePlayerEarnings()


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


if __name__ == '__main__':
    main()
