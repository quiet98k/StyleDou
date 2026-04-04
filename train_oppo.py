import os


# Reuse the baseline parser to keep CLI compatibility with train.py.
from douzero.dmc.arguments import parser


# Import after alias injection.
from oppo_modeling.dmc.dmc import train


if __name__ == "__main__":
    # Add missing arg required by oppo_modeling/dmc/dmc.py.
    if not any(action.dest == "oppo_interval" for action in parser._actions):
        parser.add_argument(
            "--oppo_interval",
            default=30,
            type=int,
            help="Interval (in minutes) for opponent update logic",
        )
    if not any(action.dest == "oppo_init_dir" for action in parser._actions):
        parser.add_argument(
            "--oppo_init_dir",
            default="most_recent_model",
            type=str,
            help="Optional directory containing bootstrap weights for opponent training",
        )
    if not any(action.dest == "run_eval_on_checkpoint" for action in parser._actions):
        parser.add_argument(
            "--run_eval_on_checkpoint",
            action="store_true",
            help="Run ADP/SL test scripts when checkpoints are saved",
        )
    if not any(action.dest == "eval_num_games" for action in parser._actions):
        parser.add_argument(
            "--eval_num_games",
            default=10000,
            type=int,
            help="Number of games to generate for periodic evaluation",
        )
    if not any(action.dest == "eval_gpu_device" for action in parser._actions):
        parser.add_argument(
            "--eval_gpu_device",
            default="0",
            type=str,
            help="GPU id passed to evaluation scripts when run_eval_on_checkpoint is enabled",
        )

    # Use an independent default experiment id/checkpoint path for clean comparisons.
    parser.set_defaults(xpid="oppo_model", savedir="douzero_checkpoints/oppo")

    flags = parser.parse_args()
    os.environ["CUDA_VISIBLE_DEVICES"] = flags.gpu_devices
    train(flags)
