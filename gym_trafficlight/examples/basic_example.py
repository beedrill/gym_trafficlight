'''
This is an example of how to use and set environment
'''
import gym
import gym_trafficlight
from gym_trafficlight.trafficenvs import TrafficEnv
from gym_trafficlight.wrappers import  TrafficParameterSetWrapper
## making environment:
env = gym.make('TrafficLight-v0')
## specify env parameters: (this will re-init the class, and lose all the original class, do it only at initial stage)
args = TrafficEnv.get_default_init_parameters()
args.update({'penetration_rate': 0.5})
env = TrafficParameterSetWrapper(env, args)

## visualize env (this will not run inside of docker, run it outside in a sumo-installed machine):
from gym_trafficlight.wrappers import TrafficVisualizationWrapper
env = TrafficVisualizationWrapper(env)
