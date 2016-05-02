import collections
import itertools
import random

class Deck():
    def __init__(self):
        self.SUIT_LIST = ("Hearts", "Spades", "Diamonds", "Clubs")
        self.NUMERAL_LIST = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace")

        self.available_cards = set()

        # Equivalent to nested for-loops in a generator expression: 
        for numeral, suit in itertools.product(self.NUMERAL_LIST, self.SUIT_LIST):  
        
            self.available_cards.add((numeral, suit))    


    def getCard(self):

        assert len(self.available_cards) != 0

        # random.sample(a,b) returns b samples with no replacement from set. the "[0]" gets the value out of the list
        card = random.sample(self.available_cards, 1)[0]  
        self.available_cards.remove(card)

        return card

    def getPreFlop(self, number_of_cards=2):
        
        assert len(self.available_cards) >= number_of_cards

        card_list = [self.getCard() for x in range(number_of_cards)]
        return card_list

    def getFlop(self, number_of_cards=3):

        assert len(self.available_cards) >= number_of_cards

        card_list = [self.getCard() for x in range(number_of_cards)]
        return card_list

    def getTurn(self, number_of_cards=1): 

        assert len(self.available_cards) >= number_of_cards

        card_list = [self.getCard() for x in range(number_of_cards)]
        return card_list

    def getRiver(self, number_of_cards=1):

        assert len(self.available_cards) >= number_of_cards

        card_list = [self.getCard() for x in range(number_of_cards)]
        return card_list



if __name__ == '__main__':

    # Test cases
    deck = Deck()

    preflop = deck.getPreFlop()
    assert len(preflop) == 2
    print "Test 1: Working"

    for i in range(0, 26):
        try:
            deck.getPreFlop()
        except AssertionError:
            print "Test 2: Working"





