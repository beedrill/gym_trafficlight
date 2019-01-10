'''
This is an example of how to use and set environment
'''
############################################Making the environment#############################################################################
import gym
import gym_trafficlight
from gym_trafficlight.trafficenvs import TrafficEnv
from gym_trafficlight.wrappers import  TrafficParameterSetWrapper
## making environment:
env = gym.make('TrafficLight-v0')
###########################################Changing Env Parameters############################################################################
## specify env parameters: (this will re-init the class, and lose all the original class, do it only at initial stage)
# args = TrafficEnv.get_default_init_parameters()
# args.update({'penetration_rate': 0.5})
# env = TrafficParameterSetWrapper(env, args).unwrapped

############################################Running the Env #################################################################################################
# args = TrafficEnv.get_default_init_parameters()
# args.update({'state_representation': 'full'})
# env = TrafficParameterSetWrapper(env, args).unwrapped
# env.reset()
# for _ in range(0,1000):
#     action = env.action_space.sample()
#     next_state, reward, terminal, info = env.step(action)
#     print(next_state, reward, terminal)

##################################################Visualizing Environment####################################################################
## visualize env (this will not run inside of docker, run it outside in a sumo-installed machine):
from gym_trafficlight.wrappers import TrafficVisualizationWrapper
args = TrafficEnv.get_default_init_parameters()
args.update({'state_representation': 'full'})
env = TrafficParameterSetWrapper(env, args).unwrapped
env = TrafficVisualizationWrapper(env).unwrapped
env.reset()
for _ in range(0,1000):
    action = env.action_space.sample()
    next_state, reward, terminal, info = env.step(action)
    print(next_state, reward, terminal)
