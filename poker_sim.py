import collections
import itertools
import random

SUIT_LIST = ("Hearts", "Spades", "Diamonds", "Clubs")
NUMERAL_LIST = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace")

class card:
    def __init__(self, numeral, suit):
        self.numeral = numeral
        self.suit = suit
        self.card = self.numeral, self.suit
    def __repr__(self):
        return self.numeral + "-" + self.suit


class Deck(set):
	def __init__(self):
	    for numeral, suit in itertools.product(NUMERAL_LIST, SUIT_LIST):  # Equivalent to nested for-loops in a generator expression: 
	    																  # intertools.product(A, B) returns the same as ((x,y) 
	    																  # for x in A for y in B).
	    	self.add(card(numeral, suit))	    	
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
			num_dict[card.numeral] += 1
			suit_dict[card.suit] += 1

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
	def __init__(self):
		self.deck = Deck()
		self.cards = self.deck.get_pre_flop()
		self.hand = Hand(self.cards)

	def receive_flop(self):
		flop_cards = self.deck.get_flop()
		for i in range(len(flop_cards)):
			self.cards.append(self.deck.get_flop()[i])

	def receive_turn(self):
		self.cards.append(self.deck.get_flop()[0])

	def receive_river(self):
		self.cards.append(self.deck.get_river()[0])

	def Fold(self):
		pass
	def Call(self):
		pass
	def Raise(self):
		pass


def main():

	P1 = Player()
	print P1.cards, P1.hand
	P1.receive_flop()
	print P1.cards, P1.hand
	P1.receive_turn()
	print P1.cards, P1.hand
	P1.receive_river()
	print P1.cards, P1.hand


if __name__ == '__main__':
    main()









