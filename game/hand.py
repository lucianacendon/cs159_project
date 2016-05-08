import collections
import itertools
import random


class Hand():

    def __init__(self, card_list):

        assert card_list is not None
        assert len(card_list) != 0

        self.card_list = card_list
        self.SUIT_LIST = ("h", "d", "c", "s")
        self.NUMERAL_LIST = ("2", "3", "4", "5", "6", "7",
                             "8", "9", "T", "J", "Q", "K", "A")
        self.description = self.getDescription()

    def getDescription(self):
        description = "Nothing"
        num_dict = collections.defaultdict(int)
        suit_dict = collections.defaultdict(int)

        for card in self.card_list:
            num_dict[card[0]] += 1
            suit_dict[card[1]] += 1

        # Pair
        if (len(self.card_list) - len(num_dict)) == 1:
            description = "One pair"

       # Two pair or 3-of-a-kind
        elif (len(self.card_list) - len(num_dict)) == 2:
            if 3 in num_dict.values():
                description = "Three-of-a-kind"
            else:
                description = "Two pairs"

        # Full house or 4-of-a-kind
        elif (len(self.card_list) - len(num_dict)) == 3:
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
                min_num = min([self.NUMERAL_LIST.index(x)
                               for x in num_dict.keys()])
                max_num = max([self.NUMERAL_LIST.index(x)
                               for x in num_dict.keys()])
                if int(max_num) - int(min_num) == 4:
                    straight = True
                low_straight = set(("A", "2", "3", "4", "5"))
                if not set(num_dict.keys()).difference(low_straight):
                    straight = True
                if straight and not flush:
                    description = "Straight"
                elif flush and not straight:
                    description = "Flush"
                elif flush and straight:
                    description = "Straight flush"

        return description

    def __repr__(self):
        return "({self.description})".format(**locals())


if __name__ == '__main__':

    pair1 = ['2h', '2d']
    pair2 = ['2h', '2d', '3h']
    pair3 = ['2h', '2d',
             '3h', '4h']
    pair4 = ['2h', '2d',
             '3h', '4h', '5h']

    two_pairs1 = ['2h', '2d',
                  'Ah', 'Ad']
    two_pairs2 = ['2h', '2d',
                  'Ah', 'Ad', '5h']

    three_of_a_kind1 = ['2h', 'As',
                        'Ah', 'Ad']
    three_of_a_kind2 = ['2h', 'As',
                        'Ah', 'Ad', '5h']

    four_of_a_kind1 = ['Ah', 'As',
                       'Ah', 'Ad']
    four_of_a_kind2 = ['Ah', 'As',
                       'Ah', 'Ad', '5h']

    straight1 = ['Ah', '2s',
                 '3h', '4d', '5h']
    straight2 = ['2h', '3s',
                 '4h', '5d', '6h']
    straight3 = ['Th', 'Js',
                 'Qh', 'Kd', 'Ah']

    flush1 = ['Th', '2h',
              '3h', '4h', '5h']

    straight_flush1 = ['Th', 'Jh',
                       'Qh', 'Kh', 'Ah']
    straight_flush2 = ['Ah', '2h',
                       '3h', '4h', '5h']
    straight_flush3 = ['2h', '3h',
                       '4h', '5h', '6h']

    tests = [pair1, pair2, pair3, pair4, two_pairs1, two_pairs2, three_of_a_kind1, three_of_a_kind2, four_of_a_kind1,
             four_of_a_kind2, straight1, straight2, straight3, flush1, straight_flush1, straight_flush2, straight_flush3]

    hands = {}
    for test in tests:
        h = Hand(test)

        if h.description in hands:
            hands[h.description] += 1
        else:
            hands[h.description] = 1
    try:
        assert hands['One pair'] == 4
        assert hands['Two pairs'] == 2
        assert hands['Three-of-a-kind'] == 2
        assert hands['Four-of-a-kind'] == 2
        assert hands['Straight'] == 3
        assert hands['Flush'] == 1
        assert hands['Straight flush'] == 3
    except AssertionError as e:
        raise
    else:
        print "All tests passed!"
