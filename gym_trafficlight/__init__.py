import logging
from gym.envs.registration import register
import os,sys
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    #import traci
    #f.close()
else:
    print('warning: no SUMO_HOME declared, please declare SUMO_HOME')

logger = logging.getLogger(__name__)

register(
    id='TrafficLight-v0',
    entry_point='gym_trafficlight.envs:TrafficEnv',
    timestep_limit=1000,
    reward_threshold=1.0,
    nondeterministic = True,
)
#print('registered to gym env')
