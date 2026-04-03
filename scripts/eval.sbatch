#!/bin/bash
#SBATCH --job-name=douzero_eval
#SBATCH --nodes=1
#SBATCH --gres=gpu:a6000:2
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

source "$(conda info --base)/etc/profile.d/conda.sh"
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
echo "Generating evaluation data..."
echo "========================================"
python3 generate_eval_data.py --output eval_data --num_games 10000

echo -e "\n========================================"
echo "Eval 1/4: Trained Landlord vs Random Peasants"
echo "========================================"
python3 evaluate.py \
    --landlord baselines/douzero_ADP/landlord.ckpt \
    --landlord_up random \
    --landlord_down random \
    --eval_data eval_data.pkl \
    --num_workers 16 \
    --gpu_device "$CUDA_VISIBLE_DEVICES"

echo -e "\n========================================"
echo "Eval 2/4: Trained Landlord vs RLCard Peasants"
echo "========================================"
python3 evaluate.py \
    --landlord baselines/douzero_ADP/landlord.ckpt \
    --landlord_up rlcard \
    --landlord_down rlcard \
    --eval_data eval_data.pkl \
    --num_workers 16 \
    --gpu_device "$CUDA_VISIBLE_DEVICES"

echo -e "\n========================================"
echo "Eval 3/4: Trained Peasants vs Random Landlord"
echo "========================================"
python3 evaluate.py \
    --landlord random \
    --landlord_up baselines/douzero_ADP/landlord_up.ckpt \
    --landlord_down baselines/douzero_ADP/landlord_down.ckpt \
    --eval_data eval_data.pkl \
    --num_workers 16 \
    --gpu_device "$CUDA_VISIBLE_DEVICES"

echo -e "\n========================================"
echo "Eval 4/4: Trained Peasants vs RLCard Landlord"
echo "========================================"
python3 evaluate.py \
    --landlord rlcard \
    --landlord_up baselines/douzero_ADP/landlord_up.ckpt \
    --landlord_down baselines/douzero_ADP/landlord_down.ckpt \
    --eval_data eval_data.pkl \
    --num_workers 16 \
    --gpu_device "$CUDA_VISIBLE_DEVICES"

echo -e "\n========================================"
echo "Evaluation complete!"
echo "End time: $(date)"
echo "========================================"