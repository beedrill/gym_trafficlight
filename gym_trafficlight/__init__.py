import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)

register(
    id='TrafficLight-v0',
    entry_point='gym_trafficlight.envs:TrafficEnv',
    timestep_limit=1000,
    reward_threshold=1.0,
    nondeterministic = True,
)
#print('registered to gym env')
