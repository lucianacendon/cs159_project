        if cards in self.Q:
            if prev_actions in self.Q[cards]:
                # get action with max value
                action_values = self.Q[cards][prev_actions]
                action = max(action_values.iteritems(), key=operator.itemgetter(1))[0]

                # value of Q(state, action)
                curr_value = self.Q[cards][prev_actions][action]
                
                # e-greedy exploration
                if r < self.e:
                    action = random.choice(['F', 'C', 'R'])


            else:
                self.Q[cards][prev_actions] = {'F' : 0, 'C' : 0, 'R' : 0}
                action = random.choice(['F', 'C', 'R'])

                curr_value = 0                                 

        else:
            self.Q[cards] = {}
            self.Q[cards][prev_actions] = {'F' : 0, 'C' : 0, 'R' : 0}
            action = random.choice(['F', 'C', 'R'])

            curr_value = 0