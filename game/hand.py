import collections
import itertools
import random


class Hand():
    def __init__(self, card_list):
        self.card_list = card_list
        self.SUIT_LIST = ("Hearts", "Spades", "Diamonds", "Clubs")
        self.NUMERAL_LIST = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace")

    def __repr__(self):

        description = "Nothing"
        num_dict = collections.defaultdict(int)
        suit_dict = collections.defaultdict(int)

        for card in self.card_list:
            num_dict[card[0]] += 1
            suit_dict[card[1]] += 1

        # Pair 
        if (len(self.card_list)-len(num_dict)) == 1:
            description = "One pair"
       
       # Two pair or 3-of-a-kind
        elif (len(self.card_list)-len(num_dict)) == 2:
            if 3 in num_dict.values():
                description = "Three-of-a-kind"
            else:
                description = "Two pairs"
       
        # Full house or 4-of-a-kind
        elif (len(self.card_list)-len(num_dict)) == 3:
            if 2 in num_dict.values():
                description = "Full house"
            else:
                description = "Four-of-a-kind"
        else:
            if (len(self.card_list) >= 4):
                # Flushes and straights
                straight, flush = False, False
                if len(suit_dict) == 1:
                    flush = True
                min_num = min([self.NUMERAL_LIST.index(x) for x in num_dict.keys()])
                max_num = max([self.NUMERAL_LIST.index(x) for x in num_dict.keys()])
                if int(max_num) - int(min_num) == 4:
                    straight = True
                low_straight = set(("Ace", "2", "3", "4", "5"))
                if not set(num_dict.keys()).difference(low_straight):
                    straight = True
                if straight and not flush:
                    description ="Straight"
                elif flush and not straight:
                    description ="Flush"
                elif flush and straight:
                    description ="Straight flush"

        return "({description})".format(**locals())


if __name__ == '__main__':
    pass
    ''' Put test cases here '''