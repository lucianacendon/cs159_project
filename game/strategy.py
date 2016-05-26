import random

class Strategy:

    # TODO: incorporate All In later
    # player considers possible options and chooses between them uniformly at random
    # SPECIAL CASE: if player can automatically call (i.e. big blind), then he/she will not fold 
    @staticmethod
    def randomStrategy(player, game, call, raise_amt):
        """
            This strategy takes random decisions not taking into account its preflop hand
        """
        cur_funds = player.states[0]
        cur_bet = player.states[1]
        diff = call - cur_bet
        raise_bet = diff + raise_amt

        # Big blind
        if diff == 0:
            if raise_bet > cur_funds:
                return 'C'

            else:
                return random.choice(['C', 'R'])

        # can't call
        if diff > cur_funds:
            return 'F'

        # can't raise
        if raise_bet > cur_funds:
            return random.choice(['F', 'C'])

        # can do anything
        return random.choice(['F', 'C', 'R'])
            

    @staticmethod
    def aggressiveStrategy(player, game, call, raise_amt):
        """
            This strategy always Raises not taking into account its preflop hand
        """
        cur_funds = player.states[0]
        cur_bet = player.states[1]
        diff = call - cur_bet
        raise_bet = diff + raise_amt


        # Can't Raise
        if raise_bet > cur_funds:
            return 'F'

        return 'R'

    @staticmethod
    def RationalProbabilisticStrategy(player, game, call, raise_amt):
        """
            This strategy Folds, Calls or Raises according to its probability of winning given its preflop hand against its pot odds
        """
        cur_funds = player.states[0]
        cur_bet = player.states[1]
        diff = call - cur_bet
        raise_bet = diff + raise_amt

        # Can't Call
        if diff > cur_funds:
            return 'F'

        # Can't Raise
        if raise_bet > cur_funds:
            return 'F'
        
        # Other cases:
        # Calculating Preflop odds
        preflop_odds = player.get_preflop_odds(game.preflop_odds_table,player.hole_cards)
        #print player.hole_cards
        #print 'Preflop odds:'+str(preflop_odds)

        # Calculating Pot odds: the amount of money one need to invest over the amount of money one would win (i.e, the amount of 
        # the pot that would be coming from one's own funds)
        pot_odds = 100 * (cur_bet+diff)/(float(game.pot+diff))  # in percentage: "IS "diff" THE AMOUNT YOU NEED TO CALL IN THIS ROUND 
                                                                # IN ORDER TO CONTINUE IN THE GAME? That's what I considered in all
                                                                # strategies.
        #print 'Pot odds: '+str(pot_odds)

        pot_odds_raised = 100 * (cur_bet+diff+raise_amt)/(float(game.pot+diff+raise_amt))
        #print 'Pot odds if raised: '+str(pot_odds_raised)

        comparison = float(preflop_odds)-float(pot_odds)
        #print 'Comparison if called: '+str(comparison)
        comparison_raised = float(preflop_odds)-float(pot_odds_raised)
        #print 'Comparison if raised: '+str(comparison_raised)
        #print ''
        
        # Actual Strategy
        if comparison <= 0:
            return 'F'
        elif comparison > 0 and comparison_raised <= 0:
            return 'C'
        elif comparison > 0 and comparison_raised > 0: 
            return 'R'


    @staticmethod
    def SlightlyBlufflyProbabilisticStrategy(player, game, call, raise_amt):
        """
            This strategy calculates Preflop and Pot_Odds exactly like the "Rational"  one. However, when it has a bad hand 
            (i.e, the pot odds are higher than the preflop odds), it: 
                    Folds: 70percent of the time ; Calls: 20percent of the time ; Raises: 10percent of the time
        """
        cur_funds = player.states[0]
        cur_bet = player.states[1]
        diff = call - cur_bet
        raise_bet = diff + raise_amt

        # Can't Call
        if diff > cur_funds:
            return 'F'

        # Can't Raise
        if raise_bet > cur_funds:
            return 'F'
        
        # Other cases:
        preflop_odds = player.get_preflop_odds(game.preflop_odds_table,player.hole_cards)
        pot_odds = 100 * (cur_bet+diff)/(float(game.pot+diff))  
        pot_odds_raised = 100 * (cur_bet+diff+raise_amt)/(float(game.pot+diff+raise_amt))

        comparison = float(preflop_odds)-float(pot_odds)
        comparison_raised = float(preflop_odds)-float(pot_odds_raised)


        # Actual Strategy
        if comparison <= 0:   # In the "Fold", it takes a probabilistic decision
            decision = 100*random.uniform(0,1)
            if decision < 70:
                return 'F'
            elif decision >= 70 and decision < 90:
                return 'C'
            else:
                return 'R'

        elif comparison > 0 and comparison_raised <= 0:
            return 'C'
        elif comparison > 0 and comparison_raised > 0: 
            return 'R'


    @staticmethod
    def BlufflyProbabilisticStrategy(player, game, call, raise_amt):
        """
            This strategy calculates Preflop and Pot_Odds exactly like the "Rational"  one. However, when it has a bad hand 
            (i.e, the pot odds are higher than the preflop odds), it: 
                    Folds: 40percent of the time ; Calls: 40percent of the time ; Raises: 20percent of the time
        """
        cur_funds = player.states[0]
        cur_bet = player.states[1]
        diff = call - cur_bet
        raise_bet = diff + raise_amt

        # Can't Call
        if diff > cur_funds:
            return 'F'

        # Can't Raise
        if raise_bet > cur_funds:
            return 'F'
        
        # Other cases:
        preflop_odds = player.get_preflop_odds(game.preflop_odds_table,player.hole_cards)
        pot_odds = 100 * (cur_bet+diff)/(float(game.pot+diff))  
        pot_odds_raised = 100 * (cur_bet+diff+raise_amt)/(float(game.pot+diff+raise_amt))

        comparison = float(preflop_odds)-float(pot_odds)
        comparison_raised = float(preflop_odds)-float(pot_odds_raised)


        # Actual Strategy
        if comparison <= 0:   # In the "Fold", it takes a probabilistic decision
            decision = 100*random.uniform(0,1)
            if decision < 40:
                return 'F'
            elif decision >= 40 and decision < 80:
                return 'C'
            else:
                return 'R'

        elif comparison > 0 and comparison_raised <= 0:
            return 'C'
        elif comparison > 0 and comparison_raised > 0: 
            return 'R'


    @staticmethod
    def TimorousProbabilisticStrategy(player, game, call, raise_amt):
        """
            This strategy calculates Preflop and Pot_Odds exactly like the "Rational" one. However, when it has a good hand 
            (i.e, the pot odds are lower than the preflop odds), there are two cases:

                Good odds for calling but not for raising: 
                    Folds: 30percent of the time ; Calls: 70percent of the time 

                Good odds for raising: 
                    Calls: 60percent of the time ; Raises: 40percent of the time

            This strategy also accounts for specially good cases. In that case, it Raises everytime it has a specially good hand.
        """

        cur_funds = player.states[0]
        cur_bet = player.states[1]
        diff = call - cur_bet
        raise_bet = diff + raise_amt

        # Can't Call
        if diff > cur_funds:
            return 'F'

        # Can't Raise
        if raise_bet > cur_funds:
            return 'F'
        
        # Other cases:
        preflop_odds = player.get_preflop_odds(game.preflop_odds_table,player.hole_cards)
        pot_odds = 100 * (cur_bet+diff)/(float(game.pot+diff))  
        pot_odds_raised = 100 * (cur_bet+diff+raise_amt)/(float(game.pot+diff+raise_amt))

        comparison = float(preflop_odds)-float(pot_odds)
        comparison_raised = float(preflop_odds)-float(pot_odds_raised)


        # Actual Strategy
        if comparison <= 0:  
            return 'F'

        elif comparison > 0 and comparison_raised <= 0:
            decision = 100*random.uniform(0,1)
            if decision < 30:
                return 'F'
            elif decision >= 30:
                return 'C'
                
        elif comparison > 0 and comparison_raised > 0: 
            if comparison_raised >= 3:  # This accounts for the specialy good hand
                return 'R'
            else: 
                decision = 100*random.uniform(0,1)

                if decision <= 60:
                    return 'C'
                elif decision > 60:
                    return 'R'


    @staticmethod
    def TemperamentalProbabilisticStrategy(player, game, call, raise_amt):
        """
            This strategy calculates Preflop and Pot_Odds exactly like the "Rational"  one. However, when it has a bad hand 
            (i.e, the pot odds are higher than the preflop odds), it: 
                    Folds: 70percent of the time ; Calls: 20percent of the time ; Raises: 10percent of the time
                    (Like 'SlightBluffy' strategy)

            However, if it has a good hand, there are two cases:

                Good odds for calling but not for raising: 
                    Calls: 70percent of the time ; Raises: 15percent ; Folds: 15percent of the time 

                Good odds for raising: 
                    Raises: 80percent of the time ; Calls: 20percent of the time 

            This strategy accounts for specially good cases. In that case, it Raises everytime it has a specially good hand
        """

        cur_funds = player.states[0]
        cur_bet = player.states[1]
        diff = call - cur_bet
        raise_bet = diff + raise_amt

        # Can't Call
        if diff > cur_funds:
            return 'F'

        # Can't Raise
        if raise_bet > cur_funds:
            return 'F'
        
        # Other cases:
        preflop_odds = player.get_preflop_odds(game.preflop_odds_table,player.hole_cards)
        pot_odds = 100 * (cur_bet+diff)/(float(game.pot+diff))  
        pot_odds_raised = 100 * (cur_bet+diff+raise_amt)/(float(game.pot+diff+raise_amt))

        comparison = float(preflop_odds)-float(pot_odds)
        comparison_raised = float(preflop_odds)-float(pot_odds_raised)


        # Actual Strategy
        if comparison <= 0:  
            decision = 100*random.uniform(0,1)
            if decision <= 70:
                return 'F'
            elif decision > 70 and decision <= 90:
                return 'C'
            else:
                return 'R'
                

        elif comparison > 0 and comparison_raised <= 0:
            decision = 100*random.uniform(0,1)
            if decision <= 15:
                return 'F'
            elif decision > 15 and decision <= 85:
                return 'C'
            else:
                return 'R'

                
        elif comparison > 0 and comparison_raised > 0:                      
            if comparison_raised >= 3:  # This accounts for the specialy good hand
                return 'R'
            else: 
                decision = 100*random.uniform(0,1)

                if decision <= 20:
                    return 'C'
                else:
                    return 'R'


