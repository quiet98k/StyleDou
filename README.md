# StyleDou

StyleDou is a DouDizhu reinforcement-learning project built on top of the
original [DouZero](https://github.com/kwai/DouZero) codebase and the
[DouZero+](https://github.com/submit-paper/Doudizhu_plus) opponent-modeling
extension. The project keeps the original DouZero training and evaluation flow,
adds the DouZero+-style opponent modeling branch, and introduces a
style-conditioned model that learns opponent behavior from public action
history.

The main research question is whether explicit opponent-style features can
improve DouZero-style agents in three-player imperfect-information DouDizhu.

## What Is Included

- Baseline DouZero training and evaluation under `douzero/`.
- DouZero+-inspired opponent modeling under `oppo_modeling/`.
- Style modeling under `style_modeling/`, including:
  - opponent-style encoders over public action history,
  - style-conditioned decision networks,
  - auxiliary opponent-action prediction loss,
  - checkpoint-time evaluation hooks.
- Round-robin evaluation tooling for baseline, style, RLCard, and random agents.
- Evaluation summaries and plots from the project runs.

## Repository Layout

```text
.
|-- douzero/                  # Original DouZero-style baseline code
|-- oppo_modeling/            # DouZero+-style opponent modeling branch
|-- style_modeling/           # Style-conditioned model implementation
|-- scripts/                  # Slurm training/evaluation job scripts
|-- model_eval_results/       # Round-robin CSV/Markdown evaluation outputs
|-- plots/                    # Loss and evaluation plots
|-- documents/                # Upstream/reference documentation
|-- train.py                  # Baseline DouZero training entry point
|-- train_oppo.py             # Opponent-model training entry point
|-- train_style.py            # Style-model training entry point
|-- generate_eval_data.py     # Evaluation deal generator
|-- evaluate.py               # Basic evaluation runner
`-- evaluate_all_models.py    # Round-robin evaluation runner
```

## Installation

Python 3.9 is recommended. A GPU environment is strongly recommended for full
training runs.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

If you are running on a cluster, the Slurm scripts in `scripts/` assume a local
virtual environment at `.venv/` unless `VENV_DIR` is provided.

## Quick Start

Generate evaluation data:

```bash
python generate_eval_data.py --output eval_data --num_games 10000
```

Evaluate three checkpoint files:

```bash
python evaluate.py \
  --landlord most_recent_model/style_model_1B/landlord.ckpt \
  --landlord_up most_recent_model/style_model_1B/landlord_up.ckpt \
  --landlord_down most_recent_model/style_model_1B/landlord_down.ckpt \
  --eval_data eval_data.pkl \
  --num_workers 5 \
  --gpu_device 0
```

Run a full round-robin evaluation:

```bash
python evaluate_all_models.py \
  --style-dir most_recent_model/style_model_1B \
  --style-model-name style_model_1B \
  --extra-baseline-agent style_model_500M:most_recent_model/style_model_500M \
  --extra-baseline-agent baseline_500M:most_recent_model/baseline_500M \
  --num-games 10000 \
  --num-workers 5 \
  --output-dir model_eval_results
```

The round-robin script writes CSV and Markdown summaries to
`model_eval_results/`.

## Training

### Baseline DouZero

```bash
python train.py \
  --xpid baseline_500M \
  --savedir douzero_checkpoints/baseline \
  --objective adp \
  --total_frames 500000000 \
  --gpu_devices 0 \
  --num_actor_devices 1 \
  --num_actors 5
```

### Opponent Modeling

```bash
python train_oppo.py \
  --xpid oppo_model \
  --savedir douzero_checkpoints/oppo \
  --oppo_init_dir most_recent_model \
  --objective adp \
  --total_frames 500000000 \
  --gpu_devices 0 \
  --num_actor_devices 1 \
  --num_actors 5
```

### Style Modeling

```bash
python train_style.py \
  --xpid style_model \
  --savedir douzero_checkpoints/style \
  --style_init_dir most_recent_model \
  --objective adp \
  --total_frames 1000000000 \
  --gpu_devices 0 \
  --num_actor_devices 1 \
  --num_actors 5 \
  --aux_loss_weight 0.2 \
  --style_embed_dim 64 \
  --history_embed_dim 128 \
  --run_eval_on_checkpoint \
  --eval_num_games 10000
```

For cluster execution, use the provided Slurm scripts:

```bash
sbatch scripts/train_baseline.sbatch
sbatch scripts/train_oppo.sbatch
sbatch scripts/train_style.sbatch
sbatch scripts/eval.sbatch
```

Most Slurm settings can be overridden with exported environment variables. See
the scripts themselves for the supported variables.

## Outputs

Training writes checkpoints and logs to:

```text
douzero_checkpoints/<branch>/<xpid>/
```

Exported checkpoints are expected under:

```text
most_recent_model/
|-- baseline_500M/
|-- style_model_500M/
`-- style_model_1B/
```

Checkpoint directories such as `douzero_checkpoints/`, `most_recent_model/`,
and `baselines/` are ignored by git. Keep trained weights locally or distribute
them through an external artifact store.

Evaluation outputs include:

- `model_eval_results/model_round_robin.csv`
- `model_eval_results/model_round_robin.md`
- optional mixed-seat round-robin files
- plots in `plots/`

The latest included round-robin summary compares `style_model_1B`,
`style_model_500M`, `baseline_500M`, DouZero baseline agents, RLCard, and a
random agent. See `model_eval_results/model_round_robin.md` for the complete
matrix.

## Reference Docs

The `documents/` directory preserves upstream/reference notes:

- `documents/Douzero_README.md` contains the original DouZero README.
- `documents/Douzero_PLUS_README.md` contains the DouZero+ reference README.

## Attribution

This repository is derived from and extends:

- DouZero: https://github.com/kwai/DouZero
- DouZero+: https://github.com/submit-paper/Doudizhu_plus,
  represented in this repo by the bundled `documents/Douzero_PLUS_README.md`
  notes and `oppo_modeling/` implementation lineage.

Please cite and respect the licenses of the upstream DouZero and DouZero+
projects when using this repository. This project-specific work adds the
style-modeling branch, evaluation scripts, and experiment outputs on top of
those foundations.
