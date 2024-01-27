# Zombie-2100
Zombie 2100 is a short vasual strategy survival game made by @blueboxsw. This repository implement the code as a python RL-environment to allow experimentation.

original game link : https://labs.blueboxsw.com/z21/zombie2100/

# requirements
```python
python
numpy
```

## How to use
You will use it as a normal gym environment

```python
from zombie_env import Zombie_2100_Env
import numpy as np

env = Zombie_2100_Env()
action_space = env.action_space
obs_space = env.obs_space
num_steps = 100

state = env.reset()

for _ in range(num_steps) :
    action = np.random.randint(0, action_space)
    next_state, reward, done, message = env.step(action=action)

    if done :
        state = env.reset()
    else :
        state = next_state
```
The state value is already normalized, if you need to regular value :
```python
env = Zombie_2100_Env(normalize=False)
state = env.reset()

# if you need to have access to read regular values at any point
infos = env.show_board()
print(infos)
```

## Details
The game is finished when the agent has survived 7 days or has been eaten by zombies

* The rewards for finishing an episode is +28
* The rewards for all other state is 0
* The reward for losing an episode is equal to the total number of turns before finishing the game

The action space consist of 7 possible actions
```python
actions = ['move1','move2','move3','food','gas','ammo',"hide"]
```