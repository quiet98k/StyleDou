import os
import threading
import time
import timeit
import pprint
import random
import logging
import sys
import traceback
from collections import deque

import torch
from torch import multiprocessing as mp
from torch import nn
import torch.nn.functional as F
from style_modeling.dmc.file_writer import FileWriter
from style_modeling.dmc.models import Model
from style_modeling.dmc.utils import get_batch, log, create_env, create_buffers, create_optimizers, act

mean_episode_return_buf = {p: deque(maxlen=100) for p in ['landlord', 'landlord_up', 'landlord_down']}


def _resolve_init_path(flags, relative_name):
    """Resolve initialization files from user-specified or default directories."""
    init_dir = getattr(flags, 'style_init_dir', 'most_recent_model')
    candidates = []
    if os.path.isabs(init_dir):
        candidates.append(os.path.join(init_dir, relative_name))
    else:
        candidates.append(os.path.join(os.getcwd(), init_dir, relative_name))
    candidates.append(os.path.join(os.getcwd(), 'douzero_checkpoints', 'baseline', 'baseline', relative_name))
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def _load_compatible_state_dict(module, checkpoint_path, map_location, model_name):
    """Load only parameters with matching names and shapes."""
    ckpt = torch.load(checkpoint_path, map_location=map_location)
    if isinstance(ckpt, dict) and 'state_dict' in ckpt:
        ckpt = ckpt['state_dict']

    module_state = module.state_dict()
    compatible = {
        key: value for key, value in ckpt.items()
        if key in module_state and module_state[key].shape == value.shape
    }

    if compatible:
        module.load_state_dict(compatible, strict=False)
        log.logger.info(
            "Loaded %d compatible tensors for %s from %s",
            len(compatible), model_name, checkpoint_path,
        )
    else:
        log.logger.warning(
            "No compatible tensors found for %s from %s; using random init.",
            model_name, checkpoint_path,
        )


def compute_loss(logits, targets):
    return ((logits.squeeze(-1) - targets) ** 2).mean()


def compute_aux_loss(aux_logits, labels):
    labels = labels.view(-1)
    logits = aux_logits.view(-1, aux_logits.size(-1))
    valid = labels != -1
    if valid.any():
        return F.cross_entropy(logits[valid], labels[valid])
    return torch.zeros((), device=aux_logits.device)


class ExceptionThread(threading.Thread):
    def __init__(self, target=None, name=None, args=()):
        threading.Thread.__init__(self)
        self._target = target
        self._args = args
        self._exc = None

    def run(self):
        try:
            if self._target:
                self._target(*self._args)
        except BaseException:
            self._exc = sys.exc_info()
            log.logger.error(traceback.format_exc())
            traceback.print_exc()
        finally:
            del self._target, self._args

    def join(self):
        threading.Thread.join(self)
        if self._exc:
            log.logger.info("Thread '%s' threw an exception: %s" % (self.getName(), self._exc[1]))



def learn(position, actor_models, model, batch, optimizer, flags, lock):
    """Performs a learning (optimization) step."""
    device = torch.device('cuda:' + str(flags.training_device))
    obs_x_no_action = batch['obs_x_no_action'].to(device)
    obs_action = batch['obs_action'].to(device)
    obs_x = torch.cat((obs_x_no_action, obs_action), dim=2).float()
    obs_x = torch.flatten(obs_x, 0, 1)
    obs_z = torch.flatten(batch['obs_z'].to(device), 0, 1).float()
    opp_z = torch.flatten(batch['opp_z'].to(device), 0, 1).float()
    target = torch.flatten(batch['target'].to(device), 0, 1)
    opp_action_type = torch.flatten(batch['opp_action_type'].to(device), 0, 1).long()
    episode_returns = batch['episode_return'][batch['done']]
    if episode_returns.numel() > 0:
        mean_episode_return_buf[position].append(torch.mean(episode_returns).to(device))

    with lock:
        learner_outputs = model(obs_z, obs_x, opp_z, return_value=True)
        value_loss = compute_loss(learner_outputs['values'], target)
        aux_loss = compute_aux_loss(learner_outputs['aux_logits'], opp_action_type)
        loss = value_loss + flags.aux_loss_weight * aux_loss
        if len(mean_episode_return_buf[position]) > 0:
            mean_return = torch.mean(torch.stack([_r for _r in mean_episode_return_buf[position]])).item()
        else:
            mean_return = 0.0
        stats = {
            'mean_episode_return_' + position: mean_return,
            'loss_' + position: loss.item(),
            'aux_loss_' + position: aux_loss.item(),
        }

        optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), flags.max_grad_norm)
        optimizer.step()

        for actor_model in actor_models:
            actor_model.get_model(position).load_state_dict(model.state_dict())

        return stats



def train(flags):
    plogger = FileWriter(
        xpid=flags.xpid,
        xp_args=flags.__dict__,
        rootdir=flags.savedir,
    )
    checkpointpath = os.path.expandvars(
        os.path.expanduser('%s/%s/%s' % (flags.savedir, flags.xpid, 'model.tar')))

    T = flags.unroll_length
    B = flags.batch_size

    models = []
    if not getattr(flags, 'actor_device_cpu', False):
        assert flags.num_actor_devices <= len(flags.gpu_devices.split(',')), (
            'The number of actor devices can not exceed the number of available devices'
        )
    for device in range(flags.num_actor_devices):
        actor_device = 'cpu' if getattr(flags, 'actor_device_cpu', False) else device
        model = Model(device=actor_device, style_dim=flags.style_embed_dim, history_dim=flags.history_embed_dim)
        model.share_memory()
        model.eval()
        models.append(model)

    buffers = create_buffers(flags)

    actor_processes = []
    ctx = mp.get_context('spawn')
    free_queue = []
    full_queue = []
    for device in range(flags.num_actor_devices):
        _free_queue = {'landlord': ctx.SimpleQueue(), 'landlord_up': ctx.SimpleQueue(), 'landlord_down': ctx.SimpleQueue()}
        _full_queue = {'landlord': ctx.SimpleQueue(), 'landlord_up': ctx.SimpleQueue(), 'landlord_down': ctx.SimpleQueue()}
        free_queue.append(_free_queue)
        full_queue.append(_full_queue)

    learner_model = Model(device=flags.training_device, style_dim=flags.style_embed_dim, history_dim=flags.history_embed_dim)

    optimizers = create_optimizers(flags, learner_model)

    stat_keys = [
        'mean_episode_return_landlord',
        'loss_landlord',
        'aux_loss_landlord',
        'mean_episode_return_landlord_up',
        'loss_landlord_up',
        'aux_loss_landlord_up',
        'mean_episode_return_landlord_down',
        'loss_landlord_down',
        'aux_loss_landlord_down',
    ]
    frames, stats = 0, {k: 0 for k in stat_keys}
    position_frames = {'landlord': 0, 'landlord_up': 0, 'landlord_down': 0}

    for k in ['landlord', 'landlord_up', 'landlord_down']:
        model_path = _resolve_init_path(flags, k + '0.ckpt')
        if model_path is None:
            model_path = _resolve_init_path(flags, k + '_weights_0.ckpt')
        if model_path is None:
            model_path = _resolve_init_path(flags, k + '.ckpt')

        style_model_path = _resolve_init_path(flags, 'style_' + k + '0.ckpt')
        if style_model_path is None:
            style_model_path = _resolve_init_path(flags, 'style_' + k + '_weights_0.ckpt')
        if style_model_path is None:
            style_model_path = _resolve_init_path(flags, 'style_' + k + '.ckpt')

        for device in range(flags.num_actor_devices):
            map_location = 'cpu' if getattr(flags, 'actor_device_cpu', False) else 'cuda:' + str(device)
            if model_path is not None:
                _load_compatible_state_dict(
                    models[device].get_model(k),
                    model_path,
                    map_location=map_location,
                    model_name='decision_' + k,
                )
            else:
                log.logger.warning('No init decision weights found for %s; using random init.', k)

            if style_model_path is not None:
                _load_compatible_state_dict(
                    models[device].get_model(k).style_model,
                    style_model_path,
                    map_location=map_location,
                    model_name='style_' + k,
                )

    if flags.load_model and os.path.exists(checkpointpath):
        checkpoint_states = torch.load(
            checkpointpath, map_location="cuda:" + str(flags.training_device)
        )
        for k in ['landlord', 'landlord_up', 'landlord_down']:
            learner_model.get_model(k).load_state_dict(checkpoint_states["model_state_dict"][k])
            optimizers[k].load_state_dict(checkpoint_states["optimizer_state_dict"][k])
            for device in range(flags.num_actor_devices):
                models[device].get_model(k).load_state_dict(learner_model.get_model(k).state_dict())
        stats = checkpoint_states["stats"]
        frames = checkpoint_states["frames"]
        position_frames = checkpoint_states["position_frames"]
        log.logger.info(f"Resuming preempted job, current stats:\n{stats}")

    for device in range(flags.num_actor_devices):
        for i in range(flags.num_actors):
            actor_device = 'cpu' if getattr(flags, 'actor_device_cpu', False) else device
            actor = ctx.Process(
                target=act,
                args=(i, actor_device, free_queue[device], full_queue[device], models[device], buffers[device], flags))
            actor.start()
            actor_processes.append(actor)

    def batch_and_learn(i, device, position, local_lock, position_lock, lock=threading.Lock()):
        """Thread target for the learning process."""
        nonlocal frames, position_frames, stats
        while frames < flags.total_frames:
            batch = get_batch(free_queue[device][position], full_queue[device][position], buffers[device][position], flags, local_lock)
            _stats = learn(position, models, learner_model.get_model(position), batch,
                           optimizers[position], flags, position_lock)

            with lock:
                for k in _stats:
                    stats[k] = _stats[k]
                to_log = dict(frames=frames)
                to_log.update({k: stats[k] for k in stat_keys})
                plogger.log(to_log)
                frames += T * B
                position_frames[position] += T * B

    for device in range(flags.num_actor_devices):
        for m in range(flags.num_buffers):
            free_queue[device]['landlord'].put(m)
            free_queue[device]['landlord_up'].put(m)
            free_queue[device]['landlord_down'].put(m)

    threads = []
    locks = [{'landlord': threading.Lock(), 'landlord_up': threading.Lock(), 'landlord_down': threading.Lock()} for _ in range(flags.num_actor_devices)]
    position_locks = {'landlord': threading.Lock(), 'landlord_up': threading.Lock(), 'landlord_down': threading.Lock()}

    for device in range(flags.num_actor_devices):
        for i in range(flags.num_threads):
            for position in ['landlord', 'landlord_up', 'landlord_down']:
                thread = ExceptionThread(
                    target=batch_and_learn, name='batch-and-learn-%d' % i,
                    args=(i, device, position, locks[device][position], position_locks[position]))
                thread.start()
                threads.append(thread)

    def checkpoint(frames):
        if flags.disable_checkpoint:
            return
        log.logger.info('Saving checkpoint to %s', checkpointpath)
        _models = learner_model.get_models()
        torch.save({
            'model_state_dict': {k: _models[k].state_dict() for k in _models},
            'optimizer_state_dict': {k: optimizers[k].state_dict() for k in optimizers},
            "stats": stats,
            'flags': vars(flags),
            'frames': frames,
            'position_frames': position_frames,
        }, checkpointpath)

        for position in ['landlord', 'landlord_up', 'landlord_down']:
            model_weights_dir = os.path.expandvars(os.path.expanduser(
                '%s/%s/%s' % (flags.savedir, flags.xpid, position + '_weights_' + str(frames) + '.ckpt')))
            torch.save(learner_model.get_model(position).state_dict(), model_weights_dir)
            style_weights_dir = os.path.expandvars(os.path.expanduser(
                '%s/%s/%s' % (flags.savedir, flags.xpid, 'style_' + position + '_weights_' + str(frames) + '.ckpt')))
            torch.save(learner_model.get_model(position).style_model.state_dict(), style_weights_dir)

    timer = timeit.default_timer
    try:
        last_checkpoint_time = timer() - flags.save_interval * 60
        initial_time = timer() - flags.save_interval * 60
        last_oppo_time = timer() - flags.oppo_interval * 60
        while frames < flags.total_frames:
            start_frames = frames
            position_start_frames = {k: position_frames[k] for k in position_frames}
            start_time = timer()
            time.sleep(10)

            if timer() - last_checkpoint_time > flags.save_interval * 60:
                saved_frames = frames
                checkpoint(saved_frames)
                last_checkpoint_time = timer()
                if getattr(flags, 'run_eval_on_checkpoint', False):
                    test_time = timer() - initial_time
                    num_games = getattr(flags, 'eval_num_games', 10000)
                    python_exec = sys.executable
                    os.system(f"{python_exec} generate_eval_data.py --num_games {num_games}")
                    time.sleep(10)
                    checkpoint_dir = os.path.join(os.getcwd(), flags.savedir, flags.xpid)
                    landlord_ckpt = os.path.join(checkpoint_dir, f"landlord_weights_{saved_frames}.ckpt")
                    landlord_up_ckpt = os.path.join(checkpoint_dir, f"landlord_up_weights_{saved_frames}.ckpt")
                    landlord_down_ckpt = os.path.join(checkpoint_dir, f"landlord_down_weights_{saved_frames}.ckpt")
                    test_dir = os.path.join(os.getcwd(), 'style_modeling', 'test')
                    os.system(
                        "cd " + test_dir + " && " + python_exec + " ADP_test.py"
                        + " --time " + str(test_time)
                        + " --frames " + str(saved_frames)
                        + " --checkpoint_dir " + checkpoint_dir
                        + " --landlord_ckpt " + landlord_ckpt
                        + " --landlord_up_ckpt " + landlord_up_ckpt
                        + " --landlord_down_ckpt " + landlord_down_ckpt
                        + " &"
                    )
                    time.sleep(10)
                    os.system(
                        "cd " + test_dir + " && " + python_exec + " sl_test.py"
                        + " --time " + str(test_time)
                        + " --frames " + str(saved_frames)
                        + " --checkpoint_dir " + checkpoint_dir
                        + " --landlord_ckpt " + landlord_ckpt
                        + " --landlord_up_ckpt " + landlord_up_ckpt
                        + " --landlord_down_ckpt " + landlord_down_ckpt
                        + " &"
                    )
                    time.sleep(10)
                    os.system(
                        "cd " + test_dir + " && " + python_exec + " WP_test.py"
                        + " --time " + str(test_time)
                        + " --frames " + str(saved_frames)
                        + " --checkpoint_dir " + checkpoint_dir
                        + " --landlord_ckpt " + landlord_ckpt
                        + " --landlord_up_ckpt " + landlord_up_ckpt
                        + " --landlord_down_ckpt " + landlord_down_ckpt
                        + " &"
                    )
                    time.sleep(10)
                    os.system(
                        "cd " + test_dir + " && " + python_exec + " random_test.py"
                        + " --time " + str(test_time)
                        + " --frames " + str(saved_frames)
                        + " --checkpoint_dir " + checkpoint_dir
                        + " --landlord_ckpt " + landlord_ckpt
                        + " --landlord_up_ckpt " + landlord_up_ckpt
                        + " --landlord_down_ckpt " + landlord_down_ckpt
                        + " &"
                    )
                    time.sleep(10)
                    os.system(
                        "cd " + test_dir + " && " + python_exec + " rlcard_test.py"
                        + " --time " + str(test_time)
                        + " --frames " + str(saved_frames)
                        + " --checkpoint_dir " + checkpoint_dir
                        + " --landlord_ckpt " + landlord_ckpt
                        + " --landlord_up_ckpt " + landlord_up_ckpt
                        + " --landlord_down_ckpt " + landlord_down_ckpt
                        + " &"
                    )

            end_time = timer()
            fps = (frames - start_frames) / (end_time - start_time)
            position_fps = {k: (position_frames[k] - position_start_frames[k]) / (end_time - start_time) for k in position_frames}
            log.logger.info(
                'After %i (L:%i U:%i D:%i) frames: @ %.1f fps (L:%.1f U:%.1f D:%.1f) Stats:\n%s',
                frames,
                position_frames['landlord'],
                position_frames['landlord_up'],
                position_frames['landlord_down'],
                fps,
                position_fps['landlord'],
                position_fps['landlord_up'],
                position_fps['landlord_down'],
                pprint.pformat(stats),
            )

    except KeyboardInterrupt:
        for actor in actor_processes:
            if actor.is_alive():
                actor.terminate()
        for actor in actor_processes:
            actor.join(timeout=2)
        return
    else:
        for thread in threads:
            thread.join()
        log.logger.info('Learning finished after %d frames.', frames)

    for actor in actor_processes:
        if actor.is_alive():
            actor.terminate()
    for actor in actor_processes:
        actor.join(timeout=2)

    checkpoint(frames)
    plogger.close()
