import numpy as np
import torch


def _resolve_device(device):
    if isinstance(device, str):
        if device == "cpu":
            return torch.device("cpu")
        return torch.device(device)
    if device is None:
        return torch.device("cpu")
    return torch.device('cuda:' + str(device))


def _format_observation(obs, device):
    position = obs['position']
    device = _resolve_device(device)
    x_batch = torch.from_numpy(obs['x_batch']).to(device)
    z_batch = torch.from_numpy(obs['z_batch']).to(device)
    x_no_action = torch.from_numpy(obs['x_no_action']).to(device)
    z = torch.from_numpy(obs['z']).to(device)
    opp_z = torch.from_numpy(obs['opp_z']).to(device)

    obs = {
        'x_batch': x_batch,
        'z_batch': z_batch,
        'legal_actions': obs['legal_actions'],
        'opp_z': opp_z,
    }
    return position, obs, x_no_action, z, opp_z


class Environment:
    def __init__(self, env, device):
        self.env = env
        self.device = device
        self.episode_return = None

    def initial(self):
        initial_position, initial_obs, x_no_action, z, opp_z = _format_observation(
            self.env.reset(), self.device
        )
        initial_reward = torch.zeros(1, 1)
        self.episode_return = torch.zeros(1, 1)
        initial_done = torch.ones(1, 1, dtype=torch.bool)

        return initial_position, initial_obs, dict(
            done=initial_done,
            episode_return=self.episode_return,
            obs_x_no_action=x_no_action,
            obs_z=z,
            obs_opp_z=opp_z,
        )

    def step(self, action):
        obs, reward, done, _ = self.env.step(action)

        self.episode_return += reward
        episode_return = self.episode_return

        if done:
            obs = self.env.reset()
            self.episode_return = torch.zeros(1, 1)

        position, obs, x_no_action, z, opp_z = _format_observation(obs, self.device)
        reward = torch.tensor(reward).view(1, 1)
        done = torch.tensor(done).view(1, 1)

        return position, obs, dict(
            done=done,
            episode_return=episode_return,
            obs_x_no_action=x_no_action,
            obs_z=z,
            obs_opp_z=opp_z,
        )

    def close(self):
        self.env.close()
