from gym import Wrapper
class TrafficVisualizationWrapper(Wrapper):
    def __init__(self, env):
        if hasattr(env, 'visual'):
            env.visual = True
            env.cmd[0] = 'sumo-gui'
        else:
            print('warning: env doesn\'t have visual attribute, this wrapper only support *traffic env*')
        return
