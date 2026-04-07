# Style Modeling: Run Guide

This guide explains how to run style modeling training, what each parameter means, and provides smoke and full run examples with eval-on-checkpoint enabled.

## Entry Point

- Training script: train_style.py
- Outputs: douzero_checkpoints/style/<xpid>/

## Parameters

General
- --xpid: Experiment id. All checkpoints and logs are saved under douzero_checkpoints/style/<xpid>/.
- --save_interval: Minutes between checkpoint saves and eval runs (when enabled).
- --objective: Reward type. adp uses bomb-weighted returns, wp uses win/loss only.

Training devices
- --gpu_devices: Comma-separated GPU ids to expose (used via CUDA_VISIBLE_DEVICES).
- --actor_device_cpu: Use CPU for actors (recommended if CUDA shared-memory issues).
- --num_actor_devices: Number of actor devices (must be <= number of visible GPUs).
- --num_actors: Actors per device.
- --training_device: Index of GPU to run the learner on.
- --load_model: Resume from the latest model.tar in the xpid directory.
- --disable_checkpoint: Disable checkpoint saving entirely.
- --savedir: Root output dir (default: douzero_checkpoints/style).

Training hyperparameters
- --total_frames: Total frames to train.
- --exp_epsilon: Epsilon for exploration in the actor.
- --batch_size: Learner batch size.
- --unroll_length: Unroll length for each actor buffer.
- --num_buffers: Number of shared-memory buffers per device.
- --num_threads: Learner threads per device.
- --max_grad_norm: Gradient clipping norm.

Optimizer
- --learning_rate: RMSprop learning rate.
- --alpha: RMSprop smoothing constant.
- --momentum: RMSprop momentum.
- --epsilon: RMSprop epsilon.

Style modeling
- --aux_loss_weight: Weight for auxiliary opponent-action loss.
- --style_embed_dim: Hidden size for opponent style encoder.
- --history_embed_dim: Hidden size for public action history encoder.

Evaluation
- --oppo_interval: Unused placeholder, mirrors oppo_modeling.
- --style_init_dir: Optional bootstrap weight dir for style training.
- --run_eval_on_checkpoint: Run ADP/SL/WP/Random/RLCard tests on each checkpoint.
- --eval_num_games: Number of games for each eval.
- --eval_gpu_device: GPU id passed to eval scripts.

## Smoke Run (fast, eval on checkpoint)

This uses CPU actors, small eval size, and small batch/unroll to validate the pipeline.

```bash
/home/quiet98k/Code/Spring26/RL-Project/StyleDou/.venv/bin/python train_style.py \
  --xpid style_smoke \
  --run_eval_on_checkpoint \
  --save_interval 0 \
  --total_frames 1000000 \
  --num_actor_devices 1 \
  --num_actors 1 \
  --num_threads 1 \
  --batch_size 8 \
  --unroll_length 32 \
  --actor_device_cpu \
  --eval_num_games 100
```

Outputs and eval CSVs:
- douzero_checkpoints/style/style_smoke/logs/adp_eval.csv
- douzero_checkpoints/style/style_smoke/logs/sl_eval.csv
- douzero_checkpoints/style/style_smoke/logs/wp_eval.csv
- douzero_checkpoints/style/style_smoke/logs/random_eval.csv
- douzero_checkpoints/style/style_smoke/logs/rlcard_eval.csv

## Actual Run (long, eval on checkpoint)

This uses GPU learner, multiple actors, and default-sized eval runs.

```bash
/home/quiet98k/Code/Spring26/RL-Project/StyleDou/.venv/bin/python train_style.py \
  --xpid style_model \
  --run_eval_on_checkpoint \
  --save_interval 30 \
  --total_frames 1000000000 \
  --gpu_devices 0 \
  --num_actor_devices 1 \
  --num_actors 5 \
  --num_threads 4 \
  --batch_size 32 \
  --unroll_length 100 \
  --eval_num_games 10000
```

## Notes

- If you see CUDA shared-memory errors, add --actor_device_cpu.
- Eval-on-checkpoint runs ADP/SL/WP/Random/RLCard tests and writes CSVs in the logs/ directory.
- Decision weights are saved as landlord_weights_<frames>.ckpt (and similar for up/down). Style weights are saved as style_landlord_weights_<frames>.ckpt (and similar for up/down).
