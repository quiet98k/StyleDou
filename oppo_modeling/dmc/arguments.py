import argparse

parser = argparse.ArgumentParser(
    description="DouZero Opponent Modeling: PyTorch DouDizhu AI"
)

# General settings.
parser.add_argument(
    "--xpid",
    default="oppo_model",
    help="Experiment id (default: oppo_model)",
)
parser.add_argument(
    "--save_interval",
    default=30,
    type=int,
    help="Time interval (in minutes) at which to save the model",
)
parser.add_argument(
    "--objective",
    default="adp",
    type=str,
    choices=["adp", "wp"],
    help="Use ADP or WP as reward (default: ADP)",
)

# Training settings.
parser.add_argument(
    "--gpu_devices",
    default="0",
    type=str,
    help="Which GPUs to be used for training",
)
parser.add_argument(
    "--actor_device_cpu",
    action="store_true",
    help="Use CPU as actor device",
)
parser.add_argument(
    "--num_actor_devices",
    default=1,
    type=int,
    help="The number of devices used for simulation",
)
parser.add_argument(
    "--num_actors",
    default=5,
    type=int,
    help="The number of actors for each simulation device",
)
parser.add_argument(
    "--training_device",
    default=0,
    type=int,
    help="The index of the GPU used for training models",
)
parser.add_argument(
    "--load_model",
    action="store_true",
    help="Load an existing model",
)
parser.add_argument(
    "--disable_checkpoint",
    action="store_true",
    help="Disable saving checkpoint",
)
parser.add_argument(
    "--savedir",
    default="douzero_checkpoints/oppo",
    help="Root dir where experiment data will be saved",
)

# Hyperparameters.
parser.add_argument(
    "--total_frames",
    default=100000000000,
    type=int,
    help="Total environment frames to train for",
)
parser.add_argument(
    "--exp_epsilon",
    default=0.01,
    type=float,
    help="The probability for exploration",
)
parser.add_argument(
    "--batch_size",
    default=32,
    type=int,
    help="Learner batch size",
)
parser.add_argument(
    "--unroll_length",
    default=100,
    type=int,
    help="The unroll length (time dimension)",
)
parser.add_argument(
    "--num_buffers",
    default=50,
    type=int,
    help="Number of shared-memory buffers",
)
parser.add_argument(
    "--num_threads",
    default=4,
    type=int,
    help="Number learner threads",
)
parser.add_argument(
    "--max_grad_norm",
    default=40.0,
    type=float,
    help="Max norm of gradients",
)

# Optimizer settings.
parser.add_argument(
    "--learning_rate",
    default=0.0001,
    type=float,
    help="Learning rate",
)
parser.add_argument(
    "--alpha",
    default=0.99,
    type=float,
    help="RMSProp smoothing constant",
)
parser.add_argument(
    "--momentum",
    default=0,
    type=float,
    help="RMSProp momentum",
)
parser.add_argument(
    "--epsilon",
    default=1e-5,
    type=float,
    help="RMSProp epsilon",
)

# Opponent modeling settings.
parser.add_argument(
    "--oppo_interval",
    default=30,
    type=int,
    help="Interval (in minutes) for opponent update logic",
)
parser.add_argument(
    "--oppo_init_dir",
    default="most_recent_model",
    type=str,
    help="Optional directory containing bootstrap weights for opponent training",
)
parser.add_argument(
    "--run_eval_on_checkpoint",
    action="store_true",
    help="Run ADP/SL test scripts when checkpoints are saved",
)
parser.add_argument(
    "--eval_num_games",
    default=10000,
    type=int,
    help="Number of games to generate for periodic evaluation",
)
parser.add_argument(
    "--eval_gpu_device",
    default="0",
    type=str,
    help="GPU id passed to evaluation scripts when run_eval_on_checkpoint is enabled",
)
