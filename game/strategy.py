import random

'''
Refer to appendix A: https://docs.google.com/document/d/1zoIaEfRAAT-VjQAq6Jvh9zhmUQAf13CJb77YE9rOhT8/edit

All methods return a Action
'''


class Strategy:

    @staticmethod
    def randomStrategy(player=None, env_state=None, raise_amt=1):
        decision = random.uniform(0, 3)

        if decision < 1 or env_state[player][0] < raise_amt:
            return "Fold"

        elif decision < 2:
            return "Call"

        elif decision < 3:
            return "Raise"

    @staticmethod
    def aggresiveStrategy(player=None, env_state=None):
        return "Raise"

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
