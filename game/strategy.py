import random

'''
Refer to appendix A: https://docs.google.com/document/d/1zoIaEfRAAT-VjQAq6Jvh9zhmUQAf13CJb77YE9rOhT8/edit

All methods return a Action
'''


class Strategy:

    # TODO: incorporate All In later
    # player considers possible options and chooses between them uniformly at random
    # SPECIAL CASE: if player can automatically call (i.e. big blind), then he/she will not fold 
    @staticmethod
    def randomStrategy(player=None, env_state=None, call=0, raise_amt=1):
        
        decision = random.uniform(0, 3)

        cur_funds = env_state[player][0]
        cur_bet = env_state[player][1]
        diff = call - cur_bet
        raise_bet = diff + raise_amt

        # Big blind
        if diff == 0:
            if raise_bet > cur_funds:
                return 'C'

            else:
                if decision < 1.5: 
                    return 'C'

                else: 
                    return 'R'

        # can't call
        if diff > cur_funds:
            return 'F'

        # can't raise
        if raise_bet > cur_funds:
            if decision < 1.5: 
                return 'F'

            else: 
                return 'C'

        # can do anything
        if decision < 1:
            return 'F'

        elif decision < 2:
            return 'C'

        elif decision < 3:
            return 'R'

    @staticmethod
    def aggresiveStrategy(player=None, env_state=None):
        return 'R'

    @staticmethod
    def preflopProbabilisticStrategy(player=None, env_state=None):
        pass

    @staticmethod
    def probabalisticStrategy(player=None, env_state=None):
        pass

    @staticmethod
    def LookAheadProbabilisticStrategy(player=None, env_state=None):
        pass

    @staticmethod
    def lessPredictableFastLookAheadStrategy(player=None, env_state=None):
        pass
