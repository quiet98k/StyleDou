import numpy as np
import torch 

def _format_observation(obs, device):
    position = obs['position']
    device = torch.device('cuda:'+str(device))
    x_batch = torch.from_numpy(obs['x_batch']).to(device)
    z_batch = torch.from_numpy(obs['z_batch']).to(device)
    x_no_action = torch.from_numpy(obs['x_no_action']).to(device)
    z = torch.from_numpy(obs['z']).to(device)

    hand_legal = obs.get('hand_legal', None)
    if hand_legal is None:
        hand_legal = torch.ones((15, 5), dtype=torch.float32, device=device)
    elif isinstance(hand_legal, torch.Tensor):
        hand_legal = hand_legal.to(device)
    else:
        hand_legal = torch.as_tensor(hand_legal, dtype=torch.float32, device=device)

    down_label = obs.get('down_label', None)
    if down_label is None:
        down_label = torch.zeros((15,), dtype=torch.int8, device=device)
    elif isinstance(down_label, torch.Tensor):
        down_label = down_label.to(device)
    else:
        down_label = torch.as_tensor(down_label, dtype=torch.int8, device=device)

    obs = {'x_batch': x_batch,
           'z_batch': z_batch,
           'legal_actions': obs['legal_actions'],
           'down_label': down_label,           # Record the information of cards of next player.
           'hand_legal': hand_legal
           }
    return position, obs, x_no_action, z

class Environment:
    def __init__(self, env, device):
        self.env = env
        self.device = device
        self.episode_return = None

    def initial(self):
        initial_position, initial_obs, x_no_action, z = _format_observation(self.env.reset(), self.device)
        initial_reward = torch.zeros(1, 1)
        self.episode_return = torch.zeros(1, 1)
        initial_done = torch.ones(1, 1, dtype=torch.bool)

        return initial_position, initial_obs, dict(
            done=initial_done,
            episode_return=self.episode_return,
            obs_x_no_action=x_no_action,
            obs_z=z,
            )
        
    def step(self, action):
        obs, reward, done, _ = self.env.step(action)

        self.episode_return += reward
        episode_return = self.episode_return 

        if done:
            obs = self.env.reset()
            self.episode_return = torch.zeros(1, 1)

        position, obs, x_no_action, z = _format_observation(obs, self.device)
        reward = torch.tensor(reward).view(1, 1)
        done = torch.tensor(done).view(1, 1)
        
        return position, obs, dict(
            done=done,
            episode_return=episode_return,
            obs_x_no_action=x_no_action,
            obs_z=z,
            )

    def close(self):
        self.env.close()
