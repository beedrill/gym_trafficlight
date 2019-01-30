import logging
from gym.envs.registration import register
from gym_trafficlight.trafficenvs import TrafficEnv, TrafficLightLuxembourg
from gym_trafficlight.utils import PenetrationRateManager
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
    id='TrafficLight-simple-sparse-v0',
    entry_point='gym_trafficlight.trafficenvs:TrafficEnv',
    timestep_limit=3000,
    nondeterministic = True,
    kwargs = {'route_file':'1-intersection/traffic-sparse.rou.xml'},
)

register(
    id='TrafficLight-simple-medium-v0',
    entry_point='gym_trafficlight.trafficenvs:TrafficEnv',
    timestep_limit=3000,
    nondeterministic = True,
    kwargs = {'route_file':'1-intersection/traffic-medium.rou.xml'},
)

register(
    id='TrafficLight-simple-dense-v0',
    entry_point='gym_trafficlight.trafficenvs:TrafficEnv',
    timestep_limit=3000,
    nondeterministic = True,
    kwargs = {'route_file':'1-intersection/traffic-dense.rou.xml'},
)

#args = TrafficEnv.get_default_init_parameters()
args = {}
args['traffic_light_module'] = TrafficLightLuxembourg
args['map_file'] = '1-intersection-Lust-12408/2/traffic.net.xml'
args['route_file'] = '1-intersection-Lust-12408/2/traffic.rou.xml'
args['num_traffic_state'] = 26
register(
    id='TrafficLight-Lust12408-midnight-v0',
    entry_point='gym_trafficlight.trafficenvs:TrafficEnv',
    timestep_limit=3000,
    nondeterministic = True,
    kwargs = args,
)

args['map_file'] = '1-intersection-Lust-12408/8/traffic.net.xml'
args['route_file'] = '1-intersection-Lust-12408/8/traffic.rou.xml'

register(
    id='TrafficLight-Lust12408-rush-hour-v0',
    entry_point='gym_trafficlight.trafficenvs:TrafficEnv',
    timestep_limit=3000,
    nondeterministic = True,
    kwargs = args,
)

args['map_file'] = '1-intersection-Lust-12408/14/traffic.net.xml'
args['route_file'] = '1-intersection-Lust-12408/14/traffic.rou.xml'

register(
    id='TrafficLight-Lust12408-regular-time-v0',
    entry_point='gym_trafficlight.trafficenvs:TrafficEnv',
    timestep_limit=3000,
    nondeterministic = True,
    kwargs = args,
)

args = {}
args['traffic_light_module'] = TrafficLightLuxembourg
args['map_file'] = '1-intersection-Lust-12408/detailed/traffic.net.xml'
args['route_file'] = '1-intersection-Lust-12408/detailed/traffic-2.rou.xml'
args['num_traffic_state'] = 26

register(
    id='TrafficLight-Lust12408-midnight-eval-v0',
    entry_point='gym_trafficlight.trafficenvs:TrafficEnv',
    timestep_limit=3000,
    nondeterministic = True,
    kwargs = args,
)

args['route_file'] = '1-intersection-Lust-12408/detailed/traffic-8.rou.xml'

register(
    id='TrafficLight-Lust12408-rush-hour-eval-v0',
    entry_point='gym_trafficlight.trafficenvs:TrafficEnv',
    timestep_limit=3000,
    nondeterministic = True,
    kwargs = args,
)

args['route_file'] = '1-intersection-Lust-12408/detailed/traffic-14.rou.xml'

register(
    id='TrafficLight-Lust12408-regular-time-eval-v0',
    entry_point='gym_trafficlight.trafficenvs:TrafficEnv',
    timestep_limit=3000,
    nondeterministic = True,
    kwargs = args,
)
#print('registered to gym env')
#TODO add different environments as a benchmark
