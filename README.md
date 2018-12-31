# Gym environment for Reinforcement Learning based traffic lights
The environment support intelligent traffic lights with full detection, as well as
partial detection (new wireless communication based traffic lights)

The environment currently does not implement render() functionality, one can visualize by using sumo-gui (setting visual = True)

# Installation
If only need to run traffic env, to avoid redundant installation, __use this [folked version of baselines](https://github.com/beedrill/baselines)__
after cloning this repo and baselines repo, run the following command to run and configure in a docker

- For GPU enabled machine:
```
nvidia-docker run -it --name rltl_baselines -e SUMO_HOME='/home/sumo' -v ~/gym_trafficlight:/home/gym_trafficlight -v ~/baselines:/home/baselines -v ~/saved_models:/home/saved_models beedrill/rltl-docker:gpu-py3 /bin/bash
cd /home/baselines
pip install -e .
cd /home/gym_trafficlight
pip install -e .
```

- For CPU, run:

```
docker run -it --name rltl_baselines -e SUMO_HOME='/home/sumo' -v ~/gym_trafficlight:/home/gym_trafficlight -v ~/baselines:/home/baselines -v ~/saved_models:/home/saved_models beedrill/rltl-docker:cpu-py3 /bin/bash
cd /home/baselines
pip install -e .
cd /home/gym_trafficlight
pip install -e .
```
## testing installation
to check installation, directly running this script:

`python3 gym_trafficlight/examples/test_install.py`

if successfully installed, it should print "installation success"

# Example


## make env
To make the environment, refer to __gym_trafficlight/examples/test_install.py__:
```
import gym
import gym_trafficlight
gym.make('TrafficLight-v0')
```

## example of running baselines alg
an example of running a2c from baselines can be found in __gym_trafficlight/examples/run_env.py__:
`python3 run_env.py --alg=a2c --network=mlp --num_timesteps=2e7`

## visualize performance
Visualization of performance can't be directly observed within the docker container, one need to run the script outside of the container, with [SUMO](http://sumo.dlr.de/wiki/Installing) properly installed and [SUMO_HOME environment parameter properly configured](http://sumo.dlr.de/wiki/Basics/Basic_Computer_Skills#SUMO_HOME), one example of visualizaing the performance is using the example run_env.py script:

'python3 run_env.py --alg=a2c --network=mlp --num_timesteps=0 --load=/your/model/path --play'
