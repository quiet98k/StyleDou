#!/bin/bash
#SBATCH --job-name=douzero_eval
#SBATCH --nodes=1
#SBATCH --gres=gpu:a5000:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=1-00:00:00
#SBATCH --output=logs/eval_%j.log
#SBATCH --partition=compsci-gpu

set -e
set -o pipefail

echo -e "\n========================================"
echo "Start time: $(date)"
echo "Node: $(hostname)"
echo "Working dir: $(pwd)"
echo "========================================"

CONDA_SH="$HOME/miniconda3/etc/profile.d/conda.sh"
if [[ ! -f "$CONDA_SH" ]]; then
    echo "Conda init script not found: $CONDA_SH" >&2
    exit 1
fi

source "$CONDA_SH"
conda activate dou

cd /home/users/yf201/Code/RL-Project/StyleDou

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
echo "Using existing most recent checkpoints..."
echo "========================================"
missing_ckpt=0
for ckpt in most_recent_model/landlord.ckpt most_recent_model/landlord_up.ckpt most_recent_model/landlord_down.ckpt; do
    if [[ ! -f "$ckpt" ]]; then
        echo "Missing checkpoint: $ckpt"
        missing_ckpt=1
    fi
done

if [[ "$missing_ckpt" -eq 1 ]]; then
    echo "Refreshing most_recent_model from douzero_checkpoints/style/style_model..."
    bash get_most_recent.sh douzero_checkpoints/style/style_model most_recent_model
fi

echo -e "\n========================================"
echo "Running full round-robin evaluation..."
echo "========================================"
python3 evaluate_all_models.py \
    --eval-data eval_data.pkl \
    --num-games 10000 \
    --num-workers 16 \
    --style-dir most_recent_model \
    --output-dir model_eval_results

echo -e "\n========================================"
echo "Evaluation complete!"
echo "End time: $(date)"
echo "========================================"