# Gym environment for Reinforcement Learning based traffic lights
The environment support intelligent traffic lights with full detection, as well as
partial detection (new wireless communication based traffic lights)

# To run
```
nvidia-docker run -it --name rltl_baselines  -v ~/gym_trafficlight:/home/gym_trafficlight beedrill/rltl-docker:gpu-py3 /bin/bash
cd /home
git clone https://github.com/openai/baselines.git
cd baselines
pip install -e .
cd /home/gym_trafficlight
pip install -e .
```
