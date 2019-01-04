from gym import RewardWrapper
from gym_trafficlight.trafficenvs import TrafficEnv

class SingleAgentWrapper(RewardWrapper):
    '''
    This agent wrap the originalal environment reward (returned as an array for multiagent) into a single reward
    '''

    def reward(self, reward):
        #print(reward)
        return sum(reward)
