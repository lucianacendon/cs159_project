import collections
import itertools
import random

SUIT_LIST = ("Hearts", "Spades", "Diamonds", "Clubs")
NUMERAL_LIST = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace")


class Deck(set):
    def __init__(self):
        for numeral, suit in itertools.product(NUMERAL_LIST, SUIT_LIST):  # Equivalent to nested for-loops in a generator expression: 
                                                                          # intertools.product(A, B) returns the same as ((x,y) 
                                                                          # for x in A for y in B).
            self.add((numeral, suit))           
    def get_card(self):
        a_card = random.sample(self, 1)[0]  # random.sample(a,b) returns b samples with no replacement from set a
                                            # the "[0]" gets the value out of the list
        self.remove(a_card)
        return a_card

    def get_pre_flop(self, number_of_cards=2):
        card_list = [self.get_card() for x in range(number_of_cards)]
        return card_list

    def get_flop(self, number_of_cards=3):
        card_list = [self.get_card() for x in range(number_of_cards)]
        return card_list

    def get_turn(self, number_of_cards=1): 
        card_list = [self.get_card() for x in range(number_of_cards)]
        return card_list

    def get_river(self, number_of_cards=1):
        card_list = [self.get_card() for x in range(number_of_cards)]
        return card_list

class Hand():
    def __init__(self, card_list):
        self.card_list = card_list

    def __repr__(self):
        descrip = "Nothing"
        num_dict = collections.defaultdict(int)
        suit_dict = collections.defaultdict(int)
        for card in self.card_list:
            num_dict[card[0]] += 1
            suit_dict[card[1]] += 1

        # Pair 
        if (len(self.card_list)-len(num_dict)) == 1:
            descrip = "One pair"
       # Two pair or 3-of-a-kind
        elif (len(self.card_list)-len(num_dict)) == 2:
            if 3 in num_dict.values():
                descrip = "Three-of-a-kind"
            else:
                descrip = "Two pairs"
        # Full house or 4-of-a-kind
        elif (len(self.card_list)-len(num_dict)) == 3:
            if 2 in num_dict.values():
                descrip = "Full house"
            else:
                descrip = "Four-of-a-kind"
        else:
            if (len(self.card_list) >= 4):
                # Flushes and straights
                straight, flush = False, False
                if len(suit_dict) == 1:
                    flush = True
                min_num = min([NUMERAL_LIST.index(x) for x in num_dict.keys()])
                max_num = max([NUMERAL_LIST.index(x) for x in num_dict.keys()])
                if int(max_num) - int(min_num) == 4:
                    straight = True
                low_straight = set(("Ace", "2", "3", "4", "5"))
                if not set(num_dict.keys()).difference(low_straight):
                    straight = True
                if straight and not flush:
                    descrip ="Straight"
                elif flush and not straight:
                    descrip ="Flush"
                elif flush and straight:
                    descrip ="Straight flush"

        return "({descrip})".format(**locals())


class Player():
    # strategy is a function
    def __init__(self, strategy):
        # is this how you set functions
        self.get_action = strategy


    def set_hole_cards(self, cards):
        self.cards = cards

    # these will be done in the simulator
    # def receive_flop(self):
    #     flop_cards = self.deck.get_flop()
    #     for i in range(len(flop_cards)):
    #         self.cards.append(self.deck.get_flop()[i])

    # def receive_turn(self):
    #     self.cards.append(self.deck.get_flop()[0])

    # def receive_river(self):
    #     self.cards.append(self.deck.get_river()[0])

    def get_action(self, state):
        pass

    def Fold(self):
        pass
    def Call(self):
        pass
    def Raise(self):
        pass

class Simulator:
    # players is a list of players
    def __init__(self, num_games, players, buy_in, small_blind, big_blind, raise_amounts):
        self.players = players
        self.win_stats = [0] * len(players)
        pass

    # simulate num_games games, train agent, record statistics, etc.
    def simulate():
        pass

    def play_game(num_rounds):
        d = Deck()

        n = len(self.players)
        player_states = []
        for p in self.players:
            p.set_hole_cards(d.get_pre_flop())
            # 2nd entry is player's current funds, 3rd is current bet amount, 4th is last action (F/C/R)
            player_states.append([p, self.buy_in, 0, None])

        dealer = 0 # position of delear chip
        cur_bet = 0 # call this to remain in the game
        pot = 0
        if self.small_blind:
            p_state = self.player_states[dealer + 1]
            p_state[1] -= self.small_blind
            p_state[2] += self.small_blind
            pot += self.small_blind
            cur_bet = self.small_blind

        
        if self.big_blind:
            self.player_states[(dealer + 2) % n]
            p_state = self.player_states[(dealer + 2) % n]
            p_state[1] -= self.big_blind
            p_state[2] += self.big_blind
            pot += self.big_blind
            cur_bet = self.big_blind

        i = 3
        cur_player = (dealer + i) % n
        p_state = self.player_states[cur_player]
        # players bet until everyone either calls or folds
        while not (p_state[3] == 'C' and p_state[2] == cur_bet):
            action = p_state[0].get_action(player_states)

            if action == 'F':
                p_state[2] = 0
                p_state[3] = 'F'

            if action == 'C':
                diff = cur_bet - p_state[2]
                p_state[1] -= diff
                p_state[2] += diff
                pot += diff
                p_state[2] = 'C'

            # need to decide raising conventions
            if action == 'R':
                pass

            # move to next player (array viewed as circular table)
            i += 1
            cur_player = (dealer + i) % n
            p_state = self.player_states[cur_player]


        ## TODO: make another loop that gathers players still in the game
        ## and go to showdown immediately, give pot to winner











def main():
    d = Deck()

    P1 = Player(None)
    P1.set_hole_cards(d.get_pre_flop())
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









