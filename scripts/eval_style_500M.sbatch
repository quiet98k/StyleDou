#!/bin/bash
#SBATCH --job-name=eval_style_500M
#SBATCH --nodes=1
#SBATCH --gres=gpu:a6000:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=1-00:00:00
#SBATCH --output=logs/eval_style_500M_%j.log
#SBATCH --partition=compsci-gpu

set -e
set -o pipefail

echo -e "\n========================================"
echo "Start time: $(date)"
echo "Node: $(hostname)"
echo "Working dir: $(pwd)"
echo "========================================"

WORKDIR=/home/users/yf201/Code/RL-Project/StyleDou
cd "$WORKDIR"

source "$WORKDIR/.venv/bin/activate"

echo "Allocated GPUs (CUDA_VISIBLE_DEVICES): $CUDA_VISIBLE_DEVICES"
nvidia-smi

echo -e "\n========================================"
echo "Checking PyTorch CUDA..."
echo "========================================"
python3 - <<'EOF'
import torch
print("CUDA available:", torch.cuda.is_available())
print("Device count:", torch.cuda.device_count())
if torch.cuda.is_available():
    print("Devices:", [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())])
else:
    raise RuntimeError("CUDA NOT AVAILABLE - check PyTorch install")
EOF

export PYTHONHASHSEED=0

echo -e "\n========================================"
echo "Verifying checkpoints..."
echo "========================================"
for ckpt in \
    most_recent_model/style_model_500M/landlord.ckpt \
    most_recent_model/style_model_500M/landlord_up.ckpt \
    most_recent_model/style_model_500M/landlord_down.ckpt \
    most_recent_model/style_model_1B/landlord.ckpt \
    most_recent_model/style_model_1B/landlord_up.ckpt \
    most_recent_model/style_model_1B/landlord_down.ckpt \
    most_recent_model/baseline_500M/landlord.ckpt \
    most_recent_model/baseline_500M/landlord_up.ckpt \
    most_recent_model/baseline_500M/landlord_down.ckpt; do
    if [[ ! -f "$ckpt" ]]; then
        echo "ERROR: Missing checkpoint: $ckpt" >&2
        exit 1
    fi
    echo "  OK: $ckpt"
done

echo -e "\n========================================"
echo "Running style_model_500M focused evaluation (15 matchups)..."
echo "========================================"
TEMP_SUFFIX=_style_500M_tmp
python3 evaluate_all_models.py \
    --eval-data eval_data.pkl \
    --num-games 10000 \
    --num-workers 16 \
    --style-dir most_recent_model/style_model_500M \
    --style-model-name style_model_500M \
    --extra-baseline-agent style_model_1B:most_recent_model/style_model_1B \
    --extra-baseline-agent baseline_500M:most_recent_model/baseline_500M \
    --focus-agent style_model_500M \
    --output-suffix "$TEMP_SUFFIX" \
    --output-dir model_eval_results \
    --no-mixed

echo -e "\n========================================"
echo "Merging focused results into model_round_robin..."
echo "========================================"
python3 - <<'EOF'
from pathlib import Path
import csv
import evaluate_all_models as eam

root = Path('/home/users/yf201/Code/RL-Project/StyleDou')
output_dir = root / 'model_eval_results'
main_csv = output_dir / 'model_round_robin.csv'
temp_csv = output_dir / 'model_round_robin_style_500M_tmp.csv'
main_md = output_dir / 'model_round_robin.md'
temp_md = output_dir / 'model_round_robin_style_500M_tmp.md'


def read_rows(path: Path):
    with path.open(newline='') as handle:
        return list(csv.DictReader(handle))


combined = {}
for row in read_rows(main_csv) + read_rows(temp_csv):
    for key in ('wp_landlord', 'wp_farmer', 'adp_landlord', 'adp_farmer'):
        row[key] = float(row[key])
    combined[(row['landlord_agent'], row['farmer_agent'])] = row

agent_names = [
    'style_model_1B',
    'style_model_500M',
    'baseline_500M',
    'baseline_ADP',
    'baseline_WP',
    'baseline_SL',
    'rlcard',
    'random',
]
ordered_rows = [combined[(landlord, farmer)] for landlord in agent_names for farmer in agent_names]
eam.write_csv(ordered_rows, main_csv)
eam.write_markdown(agent_names, ordered_rows, main_md)

temp_csv.unlink(missing_ok=True)
temp_md.unlink(missing_ok=True)
EOF

echo -e "\n========================================"
echo "Evaluation complete!"
echo "End time: $(date)"
echo "========================================"
