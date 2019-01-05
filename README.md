# Gym environment for Reinforcement Learning based traffic lights
The environment support intelligent traffic lights with full detection, as well as
partial detection (new wireless communication based traffic lights)

The environment currently does not implement **render()**, but the same functionality is achieved by using sumo-gui (setting `visual=True`), refer to [here](https://github.com/beedrill/gym_trafficlight#visualize-performance) for an example)

# Installation
## Install env
`pip install -e .`

## Run Openai Baselines

To run baselines algorithm for the environment, __use this [folked version of baselines](https://github.com/beedrill/baselines)__,
, this version of baselines is slightly modified to adapt TrafficEnv. After cloning this repo and baselines repo, run the following command to run and configure in a docker.

- For GPU enabled machines:

```
nvidia-docker run -it --name rltl_baselines -e SUMO_HOME='/home/sumo' -e OPENAI_LOGDIR='/home/training_logs' -e OPENAI_LOG_FORMAT='stdout,csv,tensorboard' -v ~/training_logs:/home/training_logs -v ~/gym_trafficlight:/home/gym_trafficlight -v ~/baselines:/home/baselines -v ~/saved_models:/home/saved_models beedrill/rltl-docker:gpu-py3 /bin/bash
cd /home/baselines
pip install -e .
cd /home/gym_trafficlight
pip install -e .
```

- For CPU only machines:

```
docker run -it --name rltl_baselines -e SUMO_HOME='/home/sumo' -e OPENAI_LOGDIR='/home/training_logs' -e OPENAI_LOG_FORMAT='stdout,csv,tensorboard' -v ~/training_logs:/home/training_logs -v ~/gym_trafficlight:/home/gym_trafficlight -v ~/baselines:/home/baselines -v ~/saved_models:/home/saved_models beedrill/rltl-docker:cpu-py3 /bin/bash
cd /home/baselines
pip install -e .
cd /home/gym_trafficlight
pip install -e .
```
## Test Installation
to check installation, directly running this script:

`python3 gym_trafficlight/examples/test_install.py`

if successfully installed, it should print "installation success"

# Examples


## Make Environment
To make the environment, refer to __gym_trafficlight/examples/test_install.py__:
```
import gym
import gym_trafficlight
from gym_trafficlight import TrafficEnv
from gym_trafficlight.wrappers import  TrafficParameterSetWrapper
args = TrafficEnv.get_default_init_parameters()
args.update({'penetration_rate': 0.5})
env = gym.make('TrafficLight-v0')
env = TrafficParameterSetWrapper(env, args)

```

## Visualize Environment
Refer also to [here](https://github.com/beedrill/gym_trafficlight#visualize-performance), here is another example:
```
args = TrafficEnv.get_default_init_parameters()
args.update({'visual': True})
env = TrafficParameterSetWrapper(env, args)

```

or use visualization wrapper:
```
from gym_trafficlight.wrappers import TrafficVisualizationWrapper
env = TrafficVisualizationWrapper(env)
```

the difference between the above two approaches is that the first one can only be use in the init phase, it will re-init everything and lose all the data in the class, the second one will only switch the env  to be visual, hence can apply whenever.
## To specify parameters for TrafficEnv:
```
import gym
import gym_trafficlight
from gym_trafficlight.wrapper import TrafficParameterSetWrapper

```

## Change Env Parameters
One can change parameters by directly passing it:

`python3 run_env.py --alg=a2c --penetration_rate=0.5`

The arg `--parameter_rate=0.5` will be directly passed to the env constructor. The parameter updating is done through a wrapper.

## Training
an example of running a2c from baselines can be found in __gym_trafficlight/examples/run_env.py__:

`python3 run_env.py --alg=a2c --network=mlp --num_timesteps=2e7`

## Save Trained Model
Here is an example of saving the model:

`python3 run_env.py --alg=a2c --network=mlp --num_timesteps=2e7 --save_path=/path/to/your/saved_models`

it will save the final model after training

## Loading and Visualize Training Results

A more thorough tutorial can be found [here](https://github.com/openai/baselines/blob/master/docs/viz/viz.ipynb)

We give an example, in the host machine, do:

```
cd ~/training_logs/tb
tensorboard --logdir=.
```

## View average waiting time curves
You can also visualize traffic env specific results such as average waiting time of each episode, by adding `--log_waiting_time=True`

## Visualize Performance
### installing SUMO
The traffic environment is based on an open source simulator [SUMO](http://sumo.dlr.de/wiki/Simulation_of_Urban_MObility_-_Wiki).
Visualization of performance can't be directly observed within the docker container, one need to run the script outside of the container, that means the need of [installing SUMO](http://sumo.dlr.de/wiki/Installing) and [have SUMO_HOME environment parameter properly configured](http://sumo.dlr.de/wiki/Basics/Basic_Computer_Skills#SUMO_HOME)

### Installing Dependency
As visualization is running [traci](http://sumo.dlr.de/wiki/TraCI) as interface, it is not required to install libsumo (which is installed in the docker image). But there is still the need of installing some other dependencies. Here gives an example of configuring a conda virtual environment using [Anaconda](https://www.anaconda.com/) (for visualization purpose, only a cpu version of tensorflow is sufficient). **when creating the virtual environment, make sure the default python of the virtual environment is python 3.6**

```
conda create -n rltl_baselines tensorflow
conda activate rltl_baselines
cd ~/baselines
pip install -e .
cd ~/gym_trafficlight
pip install -e .
```

### Example of Visualization
one example of visualizaing the performance is, again, using the example __gym_trafficlight/examples/run_env.py__ script, for example:

`python3 run_env.py --alg=a2c --network=mlp --num_timesteps=0 --load_path=/your/model/path --play`

make sure the args in the loading should be the same as args in training, otherwise loading will fail.

## More Examples
Here is an example that trains an agent with a2c:

```
python3 run_env.py --alg=a2c --network=mlp --num_timesteps=2e7 --save_path=/path/to/saved/model --layer_norm=True --nsteps=200
```
