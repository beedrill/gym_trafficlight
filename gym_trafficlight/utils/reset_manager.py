'''
Here provides several classes to handle extra changes when an env needs to reset
'''

class ResetManager():
    '''
    the manager managing reset of the simulator, needs simulator to bind itself with it, in the simulator __init__:
    self.reset_manager.bind(self)
    '''
    def __init__(self):
        self.num_reset = 0
        self.simulator = None

    def on_reset(self):
        if self.simulator == None:
            print('this reset manager is not binded to any simulator yet')
        self.num_reset+=1
        return

    def bind(self, sim):
        self.simulator = sim

class PenetrationRateManager(ResetManager):
    def __init__(self,
                trend = 'linear',
                transition_time = 3*365, #default 3 years of transition
                pr_start = 0.1, #starting penetration rate
                pr_end = 1
                ):
        ResetManager.__init__(self)
        self.simulator = None
        self.trend = trend
        self.transition_time = transition_time
        self.pr_start = pr_start
        self.pr = self.pr_start
        self.pr_end = pr_end

    def set_penetration(self):
        self.simulator.penetration_rate = self.pr
    def on_reset(self):

        super().on_reset()
        if self.trend == 'linear':
            increment = (self.pr_end - self.pr_start)/self.transition_time
            self.pr += increment
            if self.pr>self.pr_end:
                self.pr = self.pr_end
        self.set_penetration()
