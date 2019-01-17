try:
    import libsumo
except ImportError:
    print('libsumo not installed properly, please use traci only')
# comment this line if you dont have pysumo and set visual = True, it should still run traci
import os, sys
import inspect
import xml.etree.ElementTree as ET
import time # this is only for debugging
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    #import traci
    #f.close()
else:
    print('warning: no SUMO_HOME declared')
import traci

import numpy as np
import random

import gym
from gym import error, spaces, utils
from gym.utils import seeding
#import numpy as np

TRUNCATE_DISTANCE = 125.
MAX_LANE_REWARD = 20

def remove_duplicates(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]



class SimpleFlowManager():
    def __init__(self, simulator,
                 rush_hour_file = 'map/traffic-dense.rou.xml',
                 normal_hour_file = 'map/traffic-medium.rou.xml',
                 midnight_file = 'map/traffic-sparse.rou.xml'):

        self.rush_hour_file = rush_hour_file
        self.normal_hour_file = normal_hour_file
        self.midnight_file = midnight_file
        self.sim = simulator

    def travel_to_random_time(self):
        t = random.randint(0,23)
        self.travel_to_time(t)
    def reset_flow(self):
        print('no need to reset flow')

    def travel_to_time(self,t):
        route_file = self.get_carflow(t)
        self.sim.route_file = route_file
        self.sim.current_day_time = t
        self.sim.cmd[4] = route_file
        print('successfully travel to time: ', t)

    def get_carflow(self, t):
        if t >= 0 and t <=7:
            return self.midnight_file

        if t > 7 and t <= 9:
            return self.rush_hour_file

        if t > 9 and t <= 16:
            return self.normal_hour_file

        if t > 16 and t <= 19:
            return self.rush_hour_file

        if t > 19 and t <= 22:
            return self.normal_hour_file

        if t >22 and t <= 24:
            return self.midnight_file

        print('time:', t, 'is not a supported input, put something between 0 to 24')
class DoNothingFlowManager():
    def __init__(self, simulatior, file_name = ''):
        self.sim = 'nothing'
        self.file_name = 'nothing'
        return
    def travel_to_random_time(self):
        print('flow manager skip travel to random time')
    def travel_to_time(self):
        print('skipped travel to time')

    def get_carflow(self, t):
        print('skipped get carFlow')

class RandomShiftFlowManager(DoNothingFlowManager):
    def __init__(self, simulator, route_file_name = '', standard_file_name = '', std = 600):
        #std is the standard deviation the depart time can be, default set as 600 (10 minutes)
        self.sim = 'nothing'
        self.route_file_name = route_file_name
        self.standard_file_name = standard_file_name
        self.std = std
        return

    def reset_flow(self, std = None):
        print('flow manager is resetting flow')
        std = std or self.std
        tree = ET.parse(self.standard_file_name)
        root = tree.getroot()
        for child in root.findall('vehicle'):
            dt = float(child.attrib['depart'])
            temp = dt + random.gauss(0, std)
            dt =  temp if temp>0 else dt
            #dt = max(0, dt)
            dt = int(dt)
            #print(dt)
            child.attrib['depart'] = str(dt)
        sorted_list = sorted(root.findall('vehicle'), key = lambda x: float(x.attrib['depart']))
        for c in root.findall('vehicle'):
            root.remove(c)
        root.extend(sorted_list)
        for c in root.findall('vehicle'):
            c.set('departLane','best')
        tree.write(self.route_file_name)
        print('done ... !')
        return True
class HourlyFlowManager(SimpleFlowManager):
    def __init__(self, simulator, file_name = 'map/whole-day-flow/traffic'):
        self.sim = simulator
        self.file_name =file_name

    def get_carflow(self,t):
        return self.file_name+'-{}.rou.xml'.format(int(t))


class Vehicle():
    max_speed = 13.9

    def __init__(self, vid, simulator, equipped = True,):
        self.id = vid
        self.simulator = simulator
        self.depart_time = simulator.time
        self.latest_time = simulator.time
        self.waiting_time = 0
        self.equipped = equipped
        self.length = self._get_length()

    def _update_speed(self):
        if self.simulator.visual == False:
            self.speed = libsumo.vehicle_getSpeed(self.id)
            #print 'vehicle_getSpeed:', type(self.speed), self.speed
            return
        else:
            self.speed = traci.vehicle.getSpeed(self.id)
            return

    def _update_lane_position(self):
        if self.simulator.visual == False:
            self.lane_position = self.lane.length - libsumo.vehicle_getLanePosition(self.id)
            #print 'vehicle_getLanePosition:', type(self.lane_position), self.lane_position
            return
        else:
            self.lane_position = self.lane.length - traci.vehicle.getLanePosition(self.id)
            return

    def _update_appearance(self):
        if self.simulator.visual:
            if self.equipped:
                #traci.vehicle.setColor(self.id,(255,0,0,0))
                return

    def _get_length(self):
        if self.simulator.visual == False:
            return libsumo.vehicle_getLength(self.id)
        else:
            return traci.vehicle.getLength(self.id)

    def step(self):
        self._update_appearance()
        self._update_speed()
        self._update_lane_position()
        self.latest_time = self.simulator.time
        if self.speed < 1:
            self.waiting_time += 1


class TrafficLight():

    def __init__(self, tlid, simulator):
        self.id = tlid
        self.simulator = simulator

    def _set_phase(self, phase):
        self.current_phase = phase
        if self.simulator.visual == False:
            libsumo.trafficlight_setRedYellowGreenState(self.id, self.signal_groups[phase])
            return
        else:
            traci.trafficlights.setRedYellowGreenState(self.id,self.signal_groups[phase])
            return

    def step(self):
        print('specify this method in subclass before use')
        pass



class SimpleTrafficLight(TrafficLight):
    def __init__(self, tlid, simulator, max_phase_time= 40., min_phase_time = 5, yellow_time = 3, num_traffic_state = 10, lane_list = [], state_representation = '', reward_present_form = 'penalty', observation_processor = None):

        TrafficLight.__init__(self, tlid, simulator)
        self.signal_groups = ['rrrrGGGGrrrrGGGG','rrrryyyyrrrryyyy','GGGGrrrrGGGGrrrr','yyyyrrrryyyyrrrr']
        self.normal_phases = [0,2]
        self.yellow_phases = [1,3]

        self.current_phase = 0  # phase can be 0, 1, 2, 3
        self.current_phase_time = 0
        self.max_time = max_phase_time
        self.min_phase_time = min_phase_time
        self.yellow_time = yellow_time

        # Traffic State 1
        # (car num, .. , dist to TL, .., current phase time)
        self.num_traffic_state = num_traffic_state
        self.traffic_state = [None for i in range(0, self.num_traffic_state)]
        self.lane_list = lane_list
        self.n_lanes = len(lane_list)
        self.state_representation = state_representation
        # Traffic State 2
        # Lanes with car speed in its position
        #self.MAP_SPEED = False
        #self.lane_length = 252
        #self.lanes = 4
        #self.car_length = 4
        #if self.MAP_SPEED:
        #    self.traffic_state = np.zeros((self.lanes, self.lane_length))

        self.reward = None
        self.reward_present_form = reward_present_form
        self.observation_processor = observation_processor
        #print(self.observation_processor)
        #input()

    def updateRLParameters(self):
        if self.state_representation == 'original':
            self.updateRLParameters_original()
            return
        elif self.state_representation == 'sign':
            self.updateRLParameters_sign()
        elif self.state_representation == 'full':
            self.updateRLParameters_full()
        else:
            print('no such state representation supported')
            return
        self.wrap_observation()
        self.wrap_reward()
    def wrap_observation(self):
        if self.observation_processor:
            self.traffic_state = self.observation_processor(self.traffic_state)
    def wrap_reward(self):
        if self.reward_present_form == 'reward':
            self.reward = -self.reward
            max_reward = self.n_lanes * MAX_LANE_REWARD
            self.reward += max_reward
            if self.simulator.normalize_reward:
                self.reward /= max_reward
        elif not self.reward_present_form == 'penalty':
            print('reward type wrong')

    def updateRLParameters_occupation(self):
        #TODO: add occupation
        sim = self.simulator
        speed_occ = [sim.lane_list[lane_name].speed_occ for lane_name in self.lane_list]
        #vid_occ = [sim.lane_list[lane_name].vid_occ for lane_name in self.lane_list]
        #self.traffic_state = speed_occ+vid_occ
        self.traffic_state = speed_occ
        #For now we only use speed occupation
        #TODO: in the future, implement more occupations
        return self.traffic_state.copy()

    def updateRLParameters_full(self):
        occ_rep = self.updateRLParameters_occupation()
        ori_rep = self.updateRLParameters_original()
        self.traffic_state = (occ_rep, ori_rep)

        return self.traffic_state

    def updateRLParameters_sign(self):
        lane_list = self.lane_list  # temporary, in the future, get this from the .net.xml file
        sim = self.simulator
        self.reward = 0

        car_normalizing_number = 20. #1. # TODO generalize by length / car length

        # Traffic State 1
        for i in range(0, 4):
            self.traffic_state[i] = sim.lane_list[lane_list[i]].detected_car_number/car_normalizing_number
            temp = sim.lane_list[lane_list[i]].length
            for vid in sim.lane_list[lane_list[i]].vehicle_list:
                v = sim.veh_list[vid]
                if v.equipped == False:
                    continue
                if v.lane_position < temp and v.equipped:
                    temp = sim.veh_list[vid].lane_position
            #self.traffic_state[i+4] = temp/float(sim.lane_list[lane_list[i]].length)
            self.traffic_state[i+4] = 1 - temp / TRUNCATE_DISTANCE # TODO generalize
            #self.traffic_state[i+4] = temp
            self.reward += sim.lane_list[lane_list[i]].lane_reward
        self.traffic_state[8] = self.current_phase_time/float(self.max_time)
        if self.current_phase in [0,1]:
            self.traffic_state[0]*=-1
            self.traffic_state[1]*=-1
            self.traffic_state[4]*=-1
            self.traffic_state[5]*=-1
        else:
            self.traffic_state[2]*=-1
            self.traffic_state[3]*=-1
            self.traffic_state[6]*=-1
            self.traffic_state[7]*=-1
            self.traffic_state[8]*=-1

        self.traffic_state[9] = 1 if self.current_phase in [1,3] else -1

        if self.simulator.whole_day:
            self.traffic_state[10] = self.simulator.current_day_time/float(24)

        return self.traffic_state.copy()

        # Traffic State 2 I will update this part in another inherited class, I don't want to put this in the same class since it becomes messy
        #if self.MAP_SPEED:
        #    self.traffic_state = np.zeros((self.lanes, self.lane_length))
        #    for i in range(self.lanes):
        #        for vid in sim.lane_list[lane_list[i]].vehicle_list:
        #            v = sim.veh_list[vid]
        #            if v.lane_position < self.lane_length and v.equipped:
        #                self.traffic_state[i, v.lane_position] = v.speed / Vehicle.max_speed
        #        self.reward += sim.lane_list[lane_list[i]].lane_reward

    def updateRLParameters_original(self):
        self.traffic_state = [None for i in range(0, self.num_traffic_state)]
        lane_list = self.lane_list  # temporary, in the future, get this from the .net.xml file
        sim = self.simulator
        self.reward = 0

        car_normalizing_number = 20. #1. # TODO generalize by length / car length

        # Traffic State 1
        for i in range(0, 4):
            self.traffic_state[i] = sim.lane_list[lane_list[i]].detected_car_number/car_normalizing_number
            temp = sim.lane_list[lane_list[i]].length
            for vid in sim.lane_list[lane_list[i]].vehicle_list:
                v = sim.veh_list[vid]
                if v.equipped == False:
                    continue
                if v.lane_position < temp and v.equipped:
                    temp = sim.veh_list[vid].lane_position
            #self.traffic_state[i+4] = temp/float(sim.lane_list[lane_list[i]].length)
            self.traffic_state[i+4] = 1 - temp / TRUNCATE_DISTANCE # TODO generalize
            #self.traffic_state[i+4] = temp
            self.reward += sim.lane_list[lane_list[i]].lane_reward
        self.traffic_state[8] = self.current_phase_time/float(self.max_time)

        self.traffic_state[9] = self.current_phase

        if self.simulator.whole_day:
            self.traffic_state[10] = self.simulator.current_day_time/float(24)

        return self.traffic_state.copy()
    def step(self, action):
        self.current_phase_time += 1
        # make sure this phrase remain to keep track on current phase time

         # rGrG or GrGr
        if self.check_allow_change_phase():
            if action == 1 or self.current_phase_time > self.max_time:
           #if action == 1:
                self.move_to_next_phase()
                #elif self.correct_action(action):
            #    self.move_to_next_phase()
        elif self.current_phase in self.yellow_phases:
            # yellow phase, action doesn't affect
            if self.current_phase_time > self.yellow_time:
                self.move_to_next_phase()
            # if no appropriate action is given, phase doesn't change
            # if self.current_phase_time > self.yellow_time and self.correct_action(action):
            #     self.move_to_next_phase()
        self.updateRLParameters()
        # make sure this method is called last to avoid error

    #def correct_action(self, action):
    #    return action == (self.current_phase + 1) % len(self.actions)
    def check_allow_change_phase(self):
        if self.current_phase in self.normal_phases:
            if self.current_phase_time>self.min_phase_time:
                #print self.current_phase_time, self.min_phase_time
                return True
        return False

    def move_to_next_phase(self):
        self.current_phase = (self.current_phase + 1) % len(self.signal_groups)
        self._set_phase(self.current_phase)
        self.current_phase_time = 0

class TrafficLightLuxembourg(SimpleTrafficLight):
    def __init__(self, tlid, simulator ,
        max_phase_time= 40.,
        min_phase_time = 5,
        yellow_time = 3,
        num_traffic_state = 10,
        lane_list = [],
        state_representation = '',
        signal_groups = ['rrrGGGGgrrrGGGGg', 'rrryyyygrrryyyyg', 'rrrrrrrGrrrrrrrG', 'rrrrrrryrrrrrrry', 'GGgGrrrrGGgGrrrr', 'yygyrrrryygyrrrr', 'rrGrrrrrrrGrrrrr', 'rryrrrrrrryrrrrr'],
        reward_present_form = 'penalty',
        observation_processor = None):
        #signal_groups = ['rrrGGGGgrrrGGGGg', 'rrryyyygrrryyyyg', 'rrrrrrrGrrrrrrrG', 'rrrrrrryrrrrrrry', 'GGgGrrrrGGgGrrrr', 'yygyrrrryygyrrrr', 'rrGrrrrrrrGrrrrr', 'rryrrrrrrryrrrrr']):
        SimpleTrafficLight.__init__(self,tlid, simulator, max_phase_time= max_phase_time, min_phase_time = min_phase_time,
            yellow_time = yellow_time, num_traffic_state = num_traffic_state, lane_list = lane_list, state_representation = state_representation,reward_present_form = reward_present_form)
        self.signal_groups = signal_groups
        self.yellow_phases = []
        self.normal_phases = []
        for idx, phase in enumerate(self.signal_groups):
            if 'y' in phase.lower():
                self.yellow_phases.append(idx)
            else:
                self.normal_phases.append(idx)

    def updateRLParameters_sign(self):
        print("sign representation is currently unavailable")
    def updateRLParameters_original(self):

        lane_list = self.lane_list  # temporary, in the future, get this from the .net.xml file
        sim = self.simulator
        self.reward = 0

        #car_normalizing_number = 20. #1. # TODO generalize by length / car length
        n_lane = len(lane_list)

        # Traffic State 1
        for i in range(0, n_lane):
            lane = sim.lane_list[lane_list[i]]
            self.traffic_state[i] = lane.detected_car_number/lane.car_normalizing_number
            #temp = sim.lane_list[lane_list[i]].length
            temp = min(TRUNCATE_DISTANCE, lane.length)
            for vid in lane.vehicle_list:
                v = sim.veh_list[vid]
                if v.equipped == False:
                    continue
                if v.lane_position < temp and v.equipped:
                    temp = sim.veh_list[vid].lane_position
            #self.traffic_state[i+4] = temp/float(sim.lane_list[lane_list[i]].length)
            self.traffic_state[i+n_lane] = 1 - temp / min(TRUNCATE_DISTANCE, lane.length) # TODO generalize
            #self.traffic_state[i+4] = temp
            self.reward += sim.lane_list[lane_list[i]].lane_reward

        self.traffic_state[2*n_lane] = self.current_phase_time/float(self.max_time)

        self.traffic_state[2*n_lane+1] = self.current_phase
        if self.simulator.unstationary_flow:
            self.traffic_state[2*n_lane+2] = self.simulator.time/3600/24.
        elif self.simulator.whole_day:
            self.traffic_state[2*n_lane+2] = self.simulator.current_day_time/float(24)
            #print(self.simulator.current_day_time)
        return self.traffic_state.copy()

def build_path(rel_path):
    ## build abs path from relative path, return None if input is None
    abs_path = None
    map_folder = os.path.dirname(os.path.abspath(__file__))
    if rel_path:
        abs_path = os.path.join(map_folder,'map', rel_path)
    return abs_path
class TrafficEnv(gym.Env):
    """
        openAI gym environment
        action_space
        reset
            restart simulation
        step
            TL agent makes a step
            params:
                action
            returns:
                observation, reward, isterminal, info
    """


    def __init__(self, visual = False,
                 logger_type = None,
                 map_file = '1-intersection/traffic.net.xml',
                 config_file = None,
                 route_file = '1-intersection/traffic.rou.xml',
                 end_time = 3600,
                 episode_time = 3000,
                 additional_file = None,
                 gui_setting_file = "1-intersection/view.settings.xml",
                 penetration_rate = 1,
                 num_traffic_state = 10,
                 record_file = "record.txt",
                 whole_day = False,
                 state_representation = 'original',
                 flow_manager_file_prefix = '1-intersection/whole-day-flow/traffic',
                 traffic_light_module = SimpleTrafficLight,
                 tl_list = None,
                 unstationary_flow = False,
                 standard_file_name = '',
                 force_sumo = False,
                 reward_present_form = 'reward',
                 reward_type = 'local',
                 log_waiting_time = False,
                 normalize_reward = True,
                 observation_processor = None,
                 observation_as_np = True,
                 num_actions = 2,
                 reset_manager = None
                 ):
        '''
        Parameters:
        -----------
        visual:                         Is it for visualization, setting True will run sumo-gui as backend (much slower), setting False to run libsumo backend

        logger_type:                    'baselines_logger' to use the logger openai baselines offer, set to None to record to file

        map_file:                       sumo map file name, only support files in the trafficenvs/map map_folder

        config_file:                    sumo config file name, specifying this will override map_file and route_file

        route_file:                     sumo route file name

        end_time:                       simulation end time

        episode_time:                   episode length, must be smaller than end_time

        additional_file:                sumo additional file name

        gui_setting_file:               sumo gui setting file name

        penetration_rate:               the percentage of vehicle being detected

        num_traffic_state:              the traffic observation state's dimension

        record_file:                    the file name of record, not used anymore, use standard baselines logger instead

        whole_day:                      when setting true, every reset, it will call flow manager to reset flow and hour

        state_representation:           can be 'sign' or 'original', or 'full' as different ways of represent state

        flow_manager_file_prefix:       flow_manager's prefix parameter, will feed to flow manager

        traffic_light_module:           traffic light module

        tl_list:                        the list of all the intelligent traffic lights, traffic lights not on the list will
                                        not detect vehicles and change phases in the run time (they only change phase as preprogrammed)

        unstationary_flow:              by setting this to True, traffic agent will add an extra attribute to the state to set current time

        standard_file_name:             standard flow file, used to feed some specific flow manager

        force_sumo = False:             when set True, the env will use non-gui sumo as backend through Traci instead of libsumo, use it when
                                        libsumo cannot run properly, this will slow down the running speed as Traci interface will be slower

        reward_present_form:            can be 'reward' or 'penalty', the env will return either reward or penalty

        reward_type:                    can be 'global' or 'local' or 'partial',
                                        'global':
                                                    the reward will be the overall reward of all vehicles on the map
                                        'local':
                                                    the reward will be only the vehicles of that intersection
                                        'partial':
                                                    the reward will be only the vehicles at the intersection, which are detected

        log_waiting_time                when set True, it will log the waiting time at every reset

        normalize_reward                normalize reward

        observation_processor           a callable to process the observation into the desired format

        observation_as_np               set to true will call np.array() to format observation into numpy array
        '''
        super().__init__()
        self.reward_range = (-float('inf'), float('inf'))
        self.visual = visual
        self.map_file = build_path(map_file)
        self.logger = None
        self.logger_type = logger_type
        if logger_type == 'baselines_logger':
            from baselines import logger
            self.logger = logger
        self.log_waiting_time = log_waiting_time
        self.config_file = build_path(config_file)
        self.route_file = build_path(route_file)
        self.additional_file = build_path(additional_file)
        self.gui_setting_file = build_path(gui_setting_file)
        self.end_time = end_time
        self.normalize_reward = normalize_reward
        self.init_seed = None
        self.veh_list = {}
        self.tl_list = {}
        self.is_started = False
        self.time = 0
        self.reset_to_same_time = False
        self.state_representation = state_representation
        self.traffic_light_module = traffic_light_module
        self.reward_present_form = reward_present_form #can be reward or penalty
        self.reward_type = reward_type
        self.penetration_rate = penetration_rate
        self.reset_manager = reset_manager
        if reset_manager:
            self.reset_manager.bind(self)


        self.observation_processor = observation_processor
        self.observation_as_np = observation_as_np
        #self.return_as_reward = return_as_reward
        #lane_list = ['0_e_0', '0_n_0','0_s_0','0_w_0','e_0_0','n_0_0','s_0_0','w_0_0'] # temporary, in the future, get this from the .net.xml file
        #self.lane_list = {l:Lane(l,self,penetration_rate=penetration_rate) for l in lane_list}
        #tl_list = ['0'] # temporary, in the future, get this from .net.xml file
        #self.tl_id_list = tl_list
        self.num_traffic_state = num_traffic_state

        self._init_sumo_info(tl_list = tl_list)

        self.action_space = ActionSpaces(len(self.tl_list), num_actions) # action = 1 means move to next phase, otherwise means stay in current phase
        self.observation_space = ObservationSpaces(len(self.tl_list), self.num_traffic_state)
        #for tlid in tl_list:
        #    self.tl_list[tlid] = SimpleTrafficLight(tlid, self, num_traffic_state = self.num_traffic_state)
        ###RL parameters

        ##############
        self.episode_time = episode_time

        self.whole_day = whole_day
        self.current_day_time = 0 # this is a value from 0 to 24



        if self.visual == False:
            self.cmd = ['sumo',
                  '--net-file', self.map_file,
                  '--route-files', self.route_file,
                  '--end', str(self.end_time), '--random']
            if not additional_file == None:
                self.cmd+=['--additional-files', self.additional_file]
            if self.config_file: #config file will overwrite all the other files
                self.cmd = ['sumo', '-c', self.config_file]

        else:
            self.cmd = ['sumo-gui',
                  '--net-file', self.map_file,
                  '--route-files', self.route_file,
                  '--end', str(self.end_time)]
            if self.config_file: #config file will overwrite all the other files
                self.cmd = ['sumo-gui', '-c', self.config_file]
        if force_sumo:
            print('force to use sumo to overwrite sumo-gui')
            self.cmd[0] = 'sumo'
        self.unstationary_flow = False
        self.no_hard_end = False
        if unstationary_flow:
            self.whole_day = unstationary_flow
            self.unstationary_flow = unstationary_flow
            self.no_hard_end = True
            self.standard_file_name = standard_file_name
            self.flow_manager = RandomShiftFlowManager(self, route_file_name = self.route_file, standard_file_name = self.standard_file_name)

        elif whole_day:
            self.flow_manager = HourlyFlowManager(self, file_name=flow_manager_file_prefix)
            self.flow_manager.travel_to_random_time() #this will travel to a random current_day_time and modifie the carflow accordingly
        if not additional_file == None:
            self.cmd+=['--additional-files', self.additional_file]
        if not gui_setting_file == None:
            self.cmd+=['--gui-settings-file', self.gui_setting_file]
        self.record_file = record_file
    def reinitialize_parameters(self, **kwargs):
        self.__init__(**kwargs)
    def implement_seed(self):
        if '--random' in self.cmd:
            self.cmd.remove('--random')
        if '--seed' in self.cmd:
            i = self.cmd.index('--seed')
            self.cmd.pop(i+1)
            self.cmd.pop(i)
        self.cmd+= ['--seed', str(self.init_seed+int(time.time()))]
        print(self.cmd)
        #input()

    def seed(self, seed = None):
        self.init_seed = seed
        self.implement_seed()
        #self.seed += int(time.time())

        #print(self.cmd)
        #time.sleep(10)
        return

    def step_(self):
        #use step() for standard operation, this is only for normal traffic light
        self._simulation_step()
        for l in self.lane_list:
            self.lane_list[l].step()

    def _init_sumo_info(self, tl_list = None):
        cmd = ['sumo',
                  '--net-file', self.map_file,
                  '--route-files', self.route_file,
                  '--end', str(self.end_time)]
        print('init using cmd: {}'.format(cmd))
        traci.start(cmd)
        #time.sleep(1)
        if tl_list:
            self.tl_id_list = tl_list
        else:
            tl_list = traci.trafficlights.getIDList()
            #print 'tls:',tl_list
            self.tl_id_list = tl_list
        lane_list = []
        for tlid in self.tl_id_list:
            tl_lane_list = remove_duplicates(traci.trafficlights.getControlledLanes(tlid))
            self.tl_list[tlid] = self.traffic_light_module(tlid, self, num_traffic_state = self.num_traffic_state, lane_list = tl_lane_list,state_representation = self.state_representation, reward_present_form = self.reward_present_form, observation_processor = self.observation_processor)
            lane_list = lane_list + tl_lane_list
            #print 'controlled lane', self.tl_list[tlid].lane_list
        #lane_list = traci.lane.getIDList()
        self.lane_list = {}
        for l in lane_list:
            #print 'lane list', lane_list
            if l.startswith(':'):
                continue
            self.lane_list[l] = Lane(l,self, length = traci.lane.getLength(l))
            #print 'lane list', l

        #print len(self.lane_list.keys())

        traci.close()
    def _simulation_start(self):
        if self.visual == False:
            libsumo.start(self.cmd)
            return
        else:
            print('starting ... {}'.format(self.cmd))
            traci.start(self.cmd)
            return

    @staticmethod
    def get_default_init_parameters():
        signature = inspect.signature(TrafficEnv.__init__)
        return {
            k: v.default
            for k, v in signature.parameters.items()
            if v.default is not inspect.Parameter.empty
            }

    def _simulation_end(self):
        if self.visual == False:
            libsumo.close()
            return
        else:
            traci.close()
            return

    def _simulation_step(self):
        if self.visual == False:
            libsumo.simulationStep()
            self.time += 1
            #print('time is {}'.format(self.time))
            return
        else:
            self.time += 1
            traci.simulationStep()
            return
    def _simulation_check_end(self):
        if self.visual == False:

            terminal =  libsumo.simulation_getMinExpectedNumber() <= 0
            if terminal == True:
                print('simulation is ended because the Expected Number of car is 0')
                return True
            else:
                return False
        else:
            return traci.simulation.getMinExpectedNumber() <=0
    def decode_action(self, encoded_action):
        actions = []
        for _ in range(len(self.tl_id_list)):
            if encoded_action & 1 == 1:
                actions.append(1)
            else:
                actions.append(0)
            encoded_action >>= 1
        return actions

    def step(self, actions):

        self._simulation_step()
        for l in self.lane_list:
            self.lane_list[l].step()

        observation = []
        reward = []
        i = 0
        for tlid in self.tl_id_list:
            tl = self.tl_list[tlid]
            #print actions
            tl.step(actions[i])
            observation.append(tl.traffic_state)
            reward.append(tl.reward)
            i += 1

        #print(reward)
        if self.observation_as_np:
            observation = np.array(observation)
        reward = np.array(reward)
        info = (self.time, len(self.veh_list.keys()))
        #if not type( observation[0][0]) in ['int',np.float64]:
            #print('something wrong', observation[0][0], type(observation[0][0]))
        #print reward
        terminal = (self.time == self.episode_time)
        if self.no_hard_end:
            terminal = self._simulation_check_end()
        #print(terminal, self.time)
        print('observation: {}'.format(observation))
        print('reward: {}'.format(reward))
        return observation, reward, terminal, info

    def start(self):
        self._simulation_start()
        self.is_started = True

    def stop(self):
        if self.is_started == False:
            print('not started yet')
            return
        self._simulation_end()
        self.is_started = False
    def close(self):
        self.stop()

    def reset(self):
        return self._reset()

    def render(self, mode=None):
        ##render is not implemented, to visualize performance, set visual attribute to True and cmd[0] to 'sumo-gui'
        return

    def _reset(self):
        if self.is_started == True:
            self.stop()
        if self.init_seed:
            self.implement_seed()
        if self.whole_day and self.reset_to_same_time == False:
            self.flow_manager.travel_to_random_time()
            if self.flow_manager.reset_flow:
                self.flow_manager.reset_flow()
        if self.log_waiting_time:
            if self.logger_type is 'baselines_logger':
                t_a, t_e, t_u = self.get_waiting_time()
                self.logger.record_tabular("average waiting time", t_a)
                self.logger.record_tabular("equipped waiting time", t_e)
                self.logger.record_tabular("unequipped waiting time", t_u)
                self.logger.dump_tabular()
            elif self.logger is None:
                self.record_result()
        self.veh_list = {}
        self.time = 0
       #S if self.visual == False:
            #reload(libsumo)
        self.start()
        #print state
        #print len(state)

        observation = []
        reward = []
        info = (self.time, len(self.veh_list.keys()))

        for l in self.lane_list:
            self.lane_list[l].reset()
            self.lane_list[l].update_lane_reward()

        for tlid in self.tl_id_list:
            tl = self.tl_list[tlid]
            #print actions
            #tl.step(actions[i])
            tl.move_to_next_phase()
            tl.updateRLParameters()
            observation.append(tl.traffic_state)
            reward.append(self.tl_list[tlid].reward)

        if self.reset_manager:
            self.reset_manager.on_reset()

        return np.array(observation)
    def get_result(self):
        return self.get_waiting_time()
    def get_waiting_time(self):
        total_waiting = 0.
        equipped_waiting = 0.
        non_equipped_waiting = 0.

        n_total = 0.
        n_equipped = 0.
        n_non_equipped = 0.

        for vid in self.veh_list:
            v = self.veh_list[vid]

            n_total += 1
            total_waiting += v.waiting_time
            if v.equipped:
                n_equipped +=1
                equipped_waiting += v.waiting_time
            else:
                n_non_equipped += 1
                non_equipped_waiting += v.waiting_time

        #print('e:{}, u:{}'.format(n_equipped, n_non_equipped))
        self.average_waiting_time = total_waiting/n_total if n_total>0 else 0
        self.equipped_average_waiting_time = equipped_waiting/n_equipped if n_equipped>0 else 0
        self.nonequipped_average_waiting_time = non_equipped_waiting/n_non_equipped if n_non_equipped>0 else 0

        return self.average_waiting_time,self.equipped_average_waiting_time, self.nonequipped_average_waiting_time
    def print_status(self):

        tl = self.tl_list[self.tl_id_list[0]]
        print('current time:', self.time, ' total cars:', len(self.veh_list.keys()), 'traffic status', tl.traffic_state, 'reward:', tl.reward)




    def record_result(self):
        f = open(self.record_file, 'a')
        f.write('{}\t{}\t{}\n'.format(*(self.get_result())))
        f.close()
   # def _update_vehicles(self):
   #     if self.visual == False:
   #         self.current_veh_list = pysumo.vehicle_list()
   #         return


class Lane():
    def __init__(self,lane_id,simulator,length = 251):
        self.id = lane_id
        self.simulator = simulator
        self.vehicle_list = []
        self.length = length
        self.car_number = 0
        self.detected_car_number = 0
        self.lane_reward = 0
        #self.penetration_rate = penetration_rate
        self.car_normalizing_number = self.length/6
        self.speed_occ = np.full(int(TRUNCATE_DISTANCE),  -1)
        self.vid_occ = np.full(int(TRUNCATE_DISTANCE), 0)

    def update_lane_reward(self):
        self.lane_reward = 0
        for vid in self.vehicle_list:
            v = self.simulator.veh_list[vid]
            if v.lane_position< TRUNCATE_DISTANCE:
                #here implement reward type
                if self.simulator.reward_type == 'partial':
                    if v.equipped == False:
                        continue

                self.lane_reward+=(Vehicle.max_speed - v.speed)/Vehicle.max_speed
        #self.lane_reward = - self.lane_reward
        self.lane_reward = max(min(self.lane_reward, MAX_LANE_REWARD), 0) # reward should be possitive, trunccate with MAX_LANE_REWARD

    def _get_vehicles(self):
        if self.simulator.visual == False:
            return list(libsumo.lane_getLastStepVehicleIDs(self.id))

        else:
            return traci.lane.getLastStepVehicleIDs(self.id)

    def step(self):
        vidlist = self._get_vehicles()

        self.vehicle_list = vidlist
        self.car_number = len(vidlist)
        self.detected_car_number = 0
        for vid in vidlist:
            if not vid in self.simulator.veh_list.keys():
                self.simulator.veh_list[vid]= Vehicle(vid,self.simulator, equipped = random.random()<self.simulator.penetration_rate)
            self.simulator.veh_list[vid].lane = self
            self.simulator.veh_list[vid].step()
            if self.simulator.veh_list[vid].equipped == True and self.simulator.veh_list[vid].lane_position< TRUNCATE_DISTANCE:
                self.detected_car_number += 1


        self.update_lane_reward()
        if self.simulator.state_representation in ['full', 'occupation']:
            self.update_occupation()

    def reset(self):
        self.vehicle_list = []
        self.car_number = 0
        self.detected_car_number = 0
        self.lane_reward = 0

    def update_occupation(self):
        ##represent the vehicles on the lane as a vector of occupation
        length = int(TRUNCATE_DISTANCE)
        speed_occ = np.full(length,  -1, dtype = np.float32)
        vid_occ = np.full(length, 0, dtype = np.float32)
        temp_id = 1
        for vid in self.vehicle_list:
            v = self.simulator.veh_list[vid]
            if v.lane_position<length and v.equipped:
                beg = int(v.lane_position)
                end = min(beg+int(v.length),length)
                for d in range(beg, end):
                    speed_occ[d] = v.speed
                    vid_occ[d] = temp_id
                temp_id += 1
        self.speed_occ = speed_occ
        self.vid_occ = vid_occ

class ActionSpaces(spaces.MultiDiscrete):
    def __init__(self, num_TL, num_actions):
        spaces.MultiDiscrete.__init__(self, [num_actions for i in range(0, num_TL)])
        self.num_TL = num_TL
        self.n = num_actions

    #def sample(self):
    #    return np.random.randint(self.n, size=self.num_TL)

class ObservationSpaces(spaces.Box):
    def __init__(self, num_TL, num_attrs):
        spaces.Box.__init__(self,low = 0, high = 10, shape = (num_TL, num_attrs), dtype = np.float32)
if __name__ == '__main__':
    #
    # num_episode = 100
    # episode_time = 3000
    #
    # sim = Simulator(episode_time = episode_time,
    #                 visual=True,
    #                 penetration_rate = 1.,
    #                 map_file = 'map/whole-day-training-flow-LuST-12408/traffic.net.xml',
    #                 route_file = 'map/whole-day-training-flow-LuST-12408/traffic.rou.xml',
    #                 whole_day = True,
    #                 num_traffic_state = 27,
    #                 state_representation = 'original',
    #                 flow_manager_file_prefix = 'map/whole-day-training-flow-LuST-12408/traffic',
    #                 traffic_light_module = TrafficLightLuxembourg)
    # #sim = Simulator(visual = True, episode_time=episode_time)
    # # # use this commend if you don't have pysumo installed
    # sim.start()
    # for _ in range(num_episode):
    #      for i in range(episode_time):
    #      #while True:
    #          action = sim.action_space.sample()
    #          next_state, reward, terminal, info = sim.step(action)
    # #         #print reward
    #          sim.print_status()
    # #         #if terminal:
    #      state = sim.reset()
    # #         #    print state
    # #         #    array = np.array(state, np.float32)
    # #             #sim.print_status()
    # #         #    break
    # sim.stop()

    rfm = RandomShiftFlowManager(None,route_file_name = 'map/OneIntersectionLuSTScenario-12408/a.rou.xml',  standard_file_name = 'map/OneIntersectionLuSTScenario-12408/traffic-standard.rou.xml')
    rfm.reset_flow()
