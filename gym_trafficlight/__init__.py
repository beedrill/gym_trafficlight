import logging
from gym.envs.registration import register
from gym_trafficlight.trafficenvs import TrafficEnv, TrafficLightLuxembourg
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
    entry_point='gym_trafficlight.trafficenvs:TrafficEnv',
    timestep_limit=3000,
    nondeterministic = True,
)

register(
    id='TrafficLight-Simple-v0',
    entry_point='gym_trafficlight.trafficenvs:TrafficEnv',
    timestep_limit=3000,
    nondeterministic = True,
)

args = TrafficEnv.get_default_init_parameters()
args['traffic_light_module'] = TrafficLightLuxembourg
register(
    id='TrafficLight-Luxembourg-v0',
    entry_point='gym_trafficlight.trafficenvs:TrafficEnv',
    timestep_limit=3000,
    nondeterministic = True,
    kwargs = args
)
#print('registered to gym env')
