from gym import Wrapper
class TrafficVisualizationWrapper(Wrapper):
    def __init__(self, env):
        super().__init__(env)
        ori_env = env
        if env.unwrapped:
            ori_env = env.unwrapped
        print('the original env is {}'.format(ori_env.__class__.__name__))
        if hasattr(ori_env, 'visual'):
            ori_env.visual = True
            ori_env.cmd[0] = 'sumo-gui'
            print('visualization wrapper applied, now the cmd of the traffic environment is set to {}'.format(ori_env.cmd))
        else:
            print('warning: env doesn\'t have visual attribute, this wrapper only support *traffic env*')
        return
