import os
import typing
import logging
import sys
import traceback
import numpy as np
from collections import Counter
import time

import torch
from torch import multiprocessing as mp
import torch.nn.functional as F
from style_modeling.dmc.env_utils import Environment
from style_modeling.env.env import Env, OPPONENT_ORDER
from style_modeling.env.move_detector import get_move_type
from style_modeling.env.utils import TYPE_15_WRONG

Card2Column = {3: 0, 4: 1, 5: 2, 6: 3, 7: 4, 8: 5, 9: 6, 10: 7,
               11: 8, 12: 9, 13: 10, 14: 11, 17: 12}

NumOnes2Array = {0: np.array([0, 0, 0, 0]),
                 1: np.array([1, 0, 0, 0]),
                 2: np.array([1, 1, 0, 0]),
                 3: np.array([1, 1, 1, 0]),
                 4: np.array([1, 1, 1, 1])}


class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL,
    }

    def __init__(self, filename, level='info', when='D', backCount=3,
                 fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)
        self.logger.setLevel(self.level_relations.get(level))
        sh = logging.StreamHandler()
        sh.setFormatter(format_str)
        self.logger.addHandler(sh)


log = Logger('all.log', level='info')
Buffers = typing.Dict[str, typing.List[torch.Tensor]]


def create_env(flags):
    return Env(flags.objective)


def get_batch(free_queue, full_queue, buffers, flags, lock):
    with lock:
        indices = [full_queue.get() for _ in range(flags.batch_size)]
    batch = {
        key: torch.stack([buffers[key][m] for m in indices], dim=1)
        for key in buffers
    }
    for m in indices:
        free_queue.put(m)
    return batch


def create_optimizers(flags, learner_model):
    positions = ['landlord', 'landlord_up', 'landlord_down']
    optimizers = {}
    for position in positions:
        optimizer = torch.optim.RMSprop(
            learner_model.parameters(position),
            lr=flags.learning_rate,
            momentum=flags.momentum,
            eps=flags.epsilon,
            alpha=flags.alpha)
        optimizers[position] = optimizer
    return optimizers


def create_buffers(flags):
    T = flags.unroll_length
    positions = ['landlord', 'landlord_up', 'landlord_down']
    buffers = []
    use_cpu = getattr(flags, 'actor_device_cpu', False)
    for device in range(flags.num_actor_devices):
        device_obj = torch.device('cpu') if use_cpu else torch.device('cuda:' + str(device))
        buffers.append({})
        for position in positions:
            x_dim = 319 if position == 'landlord' else 430
            specs = dict(
                done=dict(size=(T,), dtype=torch.bool),
                episode_return=dict(size=(T,), dtype=torch.float32),
                target=dict(size=(T,), dtype=torch.float32),
                obs_x_no_action=dict(size=(T, x_dim), dtype=torch.int8),
                obs_action=dict(size=(T, 54), dtype=torch.int8),
                obs_z=dict(size=(T, 5, 162), dtype=torch.int8),
                opp_z=dict(size=(T, 2, 5, 162), dtype=torch.int8),
                opp_action_type=dict(size=(T, 2), dtype=torch.int8),
            )
            _buffers: Buffers = {key: [] for key in specs}
            for _ in range(flags.num_buffers):
                for key in _buffers:
                    _buffer = torch.empty(**specs[key]).to(device_obj)
                    if device_obj.type == 'cpu':
                        _buffer.share_memory_()
                    _buffers[key].append(_buffer)
            buffers[device][position] = _buffers
    return buffers


def _action_to_type(action):
    move = action.copy()
    move.sort()
    move_type = get_move_type(move)['type']
    if move_type == TYPE_15_WRONG:
        return -1
    return move_type


def act(i, device, free_queue, full_queue, model, buffers, flags):
    positions = ['landlord', 'landlord_up', 'landlord_down']
    try:
        T = flags.unroll_length
        log.logger.info('Device %s Actor %i started.', device, i)

        env = create_env(flags)
        env = Environment(env, device)

        done_buf = {p: [] for p in positions}
        episode_return_buf = {p: [] for p in positions}
        target_buf = {p: [] for p in positions}
        obs_x_no_action_buf = {p: [] for p in positions}
        obs_action_buf = {p: [] for p in positions}
        obs_z_buf = {p: [] for p in positions}
        opp_z_buf = {p: [] for p in positions}
        opp_action_type_buf = {p: [] for p in positions}
        pending = {p: {opp: [] for opp in OPPONENT_ORDER[p]} for p in positions}
        size = {p: 0 for p in positions}

        position, obs, env_output = env.initial()

        while True:
            while True:
                obs_x_no_action_buf[position].append(env_output['obs_x_no_action'])
                obs_z_buf[position].append(env_output['obs_z'])
                opp_z_buf[position].append(env_output['obs_opp_z'])

                opp_action_type_buf[position].append([-1, -1])
                pending_index = len(opp_action_type_buf[position]) - 1
                for slot, opponent in enumerate(OPPONENT_ORDER[position]):
                    pending[position][opponent].append((pending_index, slot))

                with torch.no_grad():
                    agent_output = model.forward(
                        position,
                        obs['z_batch'],
                        obs['x_batch'],
                        obs['opp_z'],
                        flags=flags,
                    )
                _action_idx = int(agent_output['action'].cpu().detach().numpy())
                action = obs['legal_actions'][_action_idx]

                action_type = _action_to_type(action)
                for pos in positions:
                    if position not in pending[pos]:
                        continue
                    for idx, slot in pending[pos][position]:
                        opp_action_type_buf[pos][idx][slot] = action_type
                    pending[pos][position].clear()

                obs_action_buf[position].append(_cards2tensor(action))
                size[position] += 1
                position, obs, env_output = env.step(action)
                if env_output['done']:
                    for p in positions:
                        diff = size[p] - len(target_buf[p])
                        if diff > 0:
                            done_buf[p].extend([False for _ in range(diff - 1)])
                            done_buf[p].append(True)

                            episode_return = env_output['episode_return'] if p == 'landlord' else -env_output['episode_return']
                            episode_return_buf[p].extend([0.0 for _ in range(diff - 1)])
                            episode_return_buf[p].append(episode_return)
                            target_buf[p].extend([episode_return for _ in range(diff)])
                    break

            for p in positions:
                if size[p] > T:
                    index = free_queue[p].get()
                    if index is None:
                        break
                    for t in range(T):
                        buffers[p]['done'][index][t, ...] = done_buf[p][t]
                        buffers[p]['episode_return'][index][t, ...] = episode_return_buf[p][t]
                        buffers[p]['target'][index][t, ...] = target_buf[p][t]

                        buffers[p]['obs_x_no_action'][index][t, ...] = obs_x_no_action_buf[p][t]
                        buffers[p]['obs_action'][index][t, ...] = obs_action_buf[p][t]
                        buffers[p]['obs_z'][index][t, ...] = obs_z_buf[p][t]
                        buffers[p]['opp_z'][index][t, ...] = opp_z_buf[p][t]
                        buffers[p]['opp_action_type'][index][t, ...] = torch.tensor(
                            opp_action_type_buf[p][t],
                            dtype=torch.int8,
                            device=buffers[p]['opp_action_type'][index].device,
                        )

                    full_queue[p].put(index)
                    done_buf[p] = done_buf[p][T:]
                    episode_return_buf[p] = episode_return_buf[p][T:]
                    target_buf[p] = target_buf[p][T:]
                    obs_x_no_action_buf[p] = obs_x_no_action_buf[p][T:]
                    obs_action_buf[p] = obs_action_buf[p][T:]
                    obs_z_buf[p] = obs_z_buf[p][T:]
                    opp_z_buf[p] = opp_z_buf[p][T:]
                    opp_action_type_buf[p] = opp_action_type_buf[p][T:]
                    for opponent in pending[p]:
                        new_pending = []
                        for idx, slot in pending[p][opponent]:
                            if idx >= T:
                                new_pending.append((idx - T, slot))
                        pending[p][opponent] = new_pending
                    size[p] -= T

    except KeyboardInterrupt:
        pass
    except Exception as e:
        exc_type, exc_value, exc_obj = sys.exc_info()
        log.logger.error(traceback.format_exc())
        traceback.print_exc()
        print()
        raise e


def _cards2tensor(list_cards):
    if len(list_cards) == 0:
        return torch.zeros(54, dtype=torch.int8)

    matrix = np.zeros([4, 13], dtype=np.int8)
    jokers = np.zeros(2, dtype=np.int8)
    counter = Counter(list_cards)
    for card, num_times in counter.items():
        if card < 20:
            matrix[:, Card2Column[card]] = NumOnes2Array[num_times]
        elif card == 20:
            jokers[0] = 1
        elif card == 30:
            jokers[1] = 1
    matrix = np.concatenate((matrix.flatten('F'), jokers))
    matrix = torch.from_numpy(matrix)
    return matrix
