# Training and Evaluation Report (Baseline vs Opponent Model)

This report explains how training and evaluation work for the baseline and the opponent-model variants, based on the current codebase.

## Files reviewed

- train.py, train_oppo.py
- douzero/dmc/dmc.py, douzero/dmc/utils.py, douzero/dmc/env_utils.py, douzero/dmc/models.py, douzero/dmc/arguments.py
- douzero/evaluation/simulation.py, douzero/evaluation/deep_agent.py
- oppo_modeling/dmc/dmc.py, oppo_modeling/dmc/utils.py, oppo_modeling/dmc/env_utils.py, oppo_modeling/dmc/models.py
- oppo_modeling/evaluation/simulation.py, oppo_modeling/evaluation/deep_agent.py, oppo_modeling/evaluation/baseline_agent.py
- generate_eval_data.py, evaluate.py
- oppo_modeling/test/ADP_test.py, oppo_modeling/test/sl_test.py, oppo_modeling/test/evaluate.py

## Baseline training (train.py -> douzero/dmc/dmc.py)

### Entry point and config

- train.py parses CLI args from douzero/dmc/arguments.py, sets CUDA_VISIBLE_DEVICES, and calls douzero.dmc.dmc.train.
- Key args include:
  - objective: adp or wp (reward mode)
  - total_frames, unroll_length, batch_size, num_actors, num_actor_devices
  - exp_epsilon (epsilon-greedy), learning_rate, RMSprop settings
  - save_interval, savedir, xpid

### Data flow and processes

- Actor processes (multiprocessing, spawn context) run in parallel on actor devices.
- Shared-memory buffers are created per CUDA device (torch.cuda.device_count()) and per position (landlord, landlord_up, landlord_down).
- Each actor interacts with Env(flags.objective) wrapped by Environment (douzero/dmc/env_utils.py).
- For each step:
  - The environment returns obs with x_batch, z_batch, legal_actions and internal features.
  - The model picks an action using argmax of value logits, with optional epsilon-greedy (exp_epsilon).
  - Actions are encoded to 54-dim card tensors (utils._cards2tensor).
  - Episode returns are assigned to targets; farmers use negative landlord return.
- Buffers store unrolls of length T (unroll_length). When filled, indices are pushed to full_queue.

### Learner threads and loss

- Learner threads (one per position per device) call get_batch to build a batch from shared buffers.
- The value loss is mean squared error between predicted value and target return:
  - loss = mean((V - target)^2)
- Gradients are clipped (max_grad_norm) and optimized with RMSprop per position.
- After each optimization step, actor models are synchronized with learner weights.

### Checkpointing and logging

- FileWriter logs stats to CSV and metadata to JSON under savedir/xpid.
- Checkpoint cadence is time-based (save_interval in minutes).
- Each checkpoint writes:
  - model.tar (full state dicts + optimizer states)
  - per-position weights: landlord_weights_<frames>.ckpt, landlord_up_weights_<frames>.ckpt, landlord_down_weights_<frames>.ckpt

## Baseline model architecture (douzero/dmc/models.py)

- Each position uses an LSTM over z (sequence length 5, feature size 162).
- LSTM output (128) is concatenated with x, then passed through 5 x 512-layer MLP to a scalar value.
- Input dimensions:
  - Landlord: x_dim = 319 + 54 = 373
  - Farmer: x_dim = 430 + 54 = 484
- Action selection uses argmax on per-action values.

## Baseline evaluation (evaluate.py -> douzero/evaluation/simulation.py)

### Evaluation data

- generate_eval_data.py creates a shuffled deck per game and saves a list to eval_data.pkl.
- Each entry contains:
  - landlord: 20 cards
  - landlord_up: 17 cards
  - landlord_down: 17 cards
  - three_landlord_cards: cards 17:20 from the shuffled deck

### Simulation loop

- evaluate.py loads eval_data.pkl and spawns a multiprocessing pool.
- Each worker runs GameEnv(players) and plays all assigned games.
- Players are constructed by model path:
  - rlcard -> RLCardAgent
  - random -> RandomAgent
  - otherwise -> DeepAgent (loads a checkpoint)

### Metrics

- Win rate (WP):
  - landlord win rate = num_landlord_wins / num_total_wins
- Score (ADP):
  - landlord score rate = num_landlord_scores / num_total_wins
  - farmer score rate = (2 * num_farmer_scores) / num_total_wins

## Opponent-model training (train_oppo.py -> oppo_modeling/dmc/dmc.py)

### Entry point and config

- train_oppo.py reuses douzero/dmc/arguments.py parser and adds:
  - oppo_interval: interval for opponent updates (currently unused in code)
  - oppo_init_dir: directory for bootstrap weights (default: most_recent_model)
  - run_eval_on_checkpoint: whether to run evaluation scripts on checkpoints
  - eval_num_games, eval_gpu_device
- Defaults are set for a separate experiment path:
  - xpid = oppo_model, savedir = douzero_checkpoints/oppo

### Core idea

The opponent model introduces a prediction network (Pre_model) that estimates the next player hand distribution. The decision model takes this prediction as an additional input.

### Data flow in actors (oppo_modeling/dmc/utils.py)

- The environment wrapper includes extra fields:
  - hand_legal: legal mask for predicted hand outputs
  - down_label: ground-truth label for the next player hand
- For each step:
  - pre_model predicts a hand distribution using obs_z and obs_x_no_action
  - predicted hand probabilities are flattened and appended to decision model input
  - decision model selects the action
- Buffers store additional tensors:
  - hand_legal (15 x 5) and down_label (15)

### Learner updates

- Decision loss: same MSE value loss as baseline.
- Prediction loss: cross-entropy over predicted hand logits vs down_label.
- Total loss = value_loss + prediction_loss.
- One RMSprop optimizer per position updates both decision and prediction parameters.
- Actor models for both networks are synchronized with learner weights after each update.

### Initialization from checkpoints

- oppo_modeling/dmc/dmc.py tries to load compatible tensors from:
  1) oppo_init_dir (default: most_recent_model)
  2) douzero_checkpoints/baseline/baseline (fallback)
- It searches for decision and prediction weights with names like:
  - landlord0.ckpt, landlord_weights_0.ckpt, landlord.ckpt
  - pre_landlord0.ckpt, pre_landlord_weights_0.ckpt, pre_landlord.ckpt

### Checkpointing and optional evaluation

- Checkpoints include both decision and prediction weights:
  - pre_landlord_weights_<frames>.ckpt, etc.
- If run_eval_on_checkpoint is enabled:
  - generate_eval_data.py runs
  - oppo_modeling/test/ADP_test.py and sl_test.py are launched in background

## Opponent-model evaluation (oppo_modeling/evaluation)

### Player selection

- simulation.py chooses the agent based on model path:
  - If path contains "baseline": BaseAgent is used
  - Otherwise: DeepAgent loads decision + prediction weights

### Opponent-aware DeepAgent

- deep_agent.py loads both decision and pre_ weights.
- It uses test_get_obs to compute features, then:
  1) pre_model predicts opponent hand (with mask)
  2) decision model evaluates legal actions using predicted hand input
  3) argmax selects the action

### Baseline agent used in tests

- baseline_agent.py loads baseline_sl, baseline_ADP, or baseline_WP
- It uses the baseline model architecture and test_get_obs features

### Test scripts

- ADP_test.py and sl_test.py:
  - copy most recent weights via get_most_recent.sh
  - run evaluate.py twice to test landlord and farmer roles
  - append results to ADP_test.log and sl_test.log

## External dependencies and missing code

Some key environment code is not present in this workspace:

- douzero.env.Env
- douzero.env.game.GameEnv
- douzero.env.env.get_obs / test_get_obs

These are required for full runtime behavior and feature definitions (x_batch, z_batch, hand_legal, down_label). The report above describes how the training/eval loops use these APIs, but the internal game logic and observation encoding live outside this repo.
