from gym import Wrapper
from gym_trafficlight.trafficenvs import TrafficEnv
class TrafficParameterSetWrapper(Wrapper):
    def __init__(self, env, wrapper_kwargs):
        print('adding wrapper for trafficenvs, please make sure this wrapper is used in the init phase, after wrapping the wrapper, original data will be lost')
        ori_env = env
        if env.unwrapped:
            ori_env = env.unwrapped
        print('the original env is {}'.format(ori_env.__class__.__name__))
        if not ori_env.__class__.__name__=='TrafficEnv':
            print('WARNING: This wrapper only work for class TrafficEnv')
        ori_env = ori_env.reinitialize_parameters(**wrapper_kwargs)
        super().__init__(env)

        return
