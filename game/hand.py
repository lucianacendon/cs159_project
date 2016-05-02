import collections
import itertools
import random


class Hand():
    def __init__(self, card_list):
        
        assert card_list is not None
        assert len(card_list) != 0

        self.card_list = card_list
        self.SUIT_LIST = ("Hearts", "Spades", "Diamonds", "Clubs")
        self.NUMERAL_LIST = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace")
        self.description = self.getDescription()
 

    def getDescription(self):
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

        return description


    def __repr__(self):
        return "({self.description})".format(**locals())


if __name__ == '__main__':
    
    pair1 = [('2', 'Hearts'), ('2', 'Diamonds')]
    pair2 = [('2', 'Hearts'), ('2', 'Diamonds'), ('3', 'Hearts')]
    pair3 = [('2', 'Hearts'), ('2', 'Diamonds'), ('3', 'Hearts'), ('4', 'Hearts')]
    pair4 = [('2', 'Hearts'), ('2', 'Diamonds'), ('3', 'Hearts'), ('4', 'Hearts'), ('5', 'Hearts')]

    two_pairs1 = [('2', 'Hearts'), ('2', 'Diamonds'), ('Ace', 'Hearts'), ('Ace', 'Diamonds')]
    two_pairs2 = [('2', 'Hearts'), ('2', 'Diamonds'), ('Ace', 'Hearts'), ('Ace', 'Diamonds'), ('5', 'Hearts')]

    three_of_a_kind1 = [('2', 'Hearts'), ('Ace', 'Spades'), ('Ace', 'Hearts'), ('Ace', 'Diamonds')]
    three_of_a_kind2 = [('2', 'Hearts'), ('Ace', 'Spades'), ('Ace', 'Hearts'), ('Ace', 'Diamonds'), ('5', 'Hearts')]
    
    four_of_a_kind1 = [('Ace', 'Hearts'), ('Ace', 'Spades'), ('Ace', 'Hearts'), ('Ace', 'Diamonds')]
    four_of_a_kind2 = [('Ace', 'Hearts'), ('Ace', 'Spades'), ('Ace', 'Hearts'), ('Ace', 'Diamonds'), ('5', 'Hearts')]

    straight1 = [('Ace', 'Hearts'), ('2', 'Spades'), ('3', 'Hearts'), ('4', 'Diamonds'), ('5', 'Hearts')]
    straight2 = [('2', 'Hearts'), ('3', 'Spades'), ('4', 'Hearts'), ('5', 'Diamonds'), ('6', 'Hearts')]
    straight3 = [('10', 'Hearts'), ('Jack', 'Spades'), ('Queen', 'Hearts'), ('King', 'Diamonds'), ('Ace', 'Hearts')]

    flush1 = [('10', 'Hearts'), ('2', 'Hearts'), ('3', 'Hearts'), ('4', 'Hearts'), ('5', 'Hearts')]

    straight_flush1 = [('10', 'Hearts'), ('Jack', 'Hearts'), ('Queen', 'Hearts'), ('King', 'Hearts'), ('Ace', 'Hearts')]
    straight_flush2 = [('Ace', 'Hearts'), ('2', 'Hearts'), ('3', 'Hearts'), ('4', 'Hearts'), ('5', 'Hearts')]
    straight_flush3 = [('2', 'Hearts'), ('3', 'Hearts'), ('4', 'Hearts'), ('5', 'Hearts'), ('6', 'Hearts')]

    tests = [pair1, pair2, pair3, pair4, two_pairs1, two_pairs2, three_of_a_kind1, three_of_a_kind2, four_of_a_kind1, four_of_a_kind2, straight1, straight2, straight3, flush1, straight_flush1, straight_flush2, straight_flush3]

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

