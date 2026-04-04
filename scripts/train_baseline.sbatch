#!/bin/bash
#SBATCH --job-name=douzero_train_baseline
#SBATCH --nodes=1
#SBATCH --gres=gpu:a6000:2
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=7-00:00:00
#SBATCH --output=logs/train_baseline_%j.log
#SBATCH --partition=compsci-gpu

set -e
set -o pipefail

WORKDIR=/home/users/yf201/Code/RL-Project/StyleDou
cd "$WORKDIR"

echo -e "\n========================================"
echo "Start time: $(date)"
echo "Node: $(hostname)"
echo "Working dir: $WORKDIR"
echo "========================================"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate dou

cd "$WORKDIR"
mkdir -p logs

# ------------------------------
# Training config (override via env)
# Example:
# sbatch --export=ALL,GPU_DEVICES=0,1,2,3,NUM_ACTOR_DEVICES=3,NUM_ACTORS=15,TRAINING_DEVICE=3,TOTAL_FRAMES=50000000 scripts/train_baseline.sbatch
# ------------------------------
GPU_DEVICES=${GPU_DEVICES:-0,1}
NUM_ACTOR_DEVICES=${NUM_ACTOR_DEVICES:-1}
NUM_ACTORS=${NUM_ACTORS:-5}
TRAINING_DEVICE=${TRAINING_DEVICE:-0}
OBJECTIVE=${OBJECTIVE:-adp}
TOTAL_FRAMES=${TOTAL_FRAMES:-200000000}
XPID=${XPID:-baseline}
SAVEDIR=${SAVEDIR:-douzero_checkpoints/baseline}
SAVE_INTERVAL=${SAVE_INTERVAL:-30}
BATCH_SIZE=${BATCH_SIZE:-32}
UNROLL_LENGTH=${UNROLL_LENGTH:-100}
NUM_BUFFERS=${NUM_BUFFERS:-50}
NUM_THREADS=${NUM_THREADS:-4}

export PYTHONHASHSEED=0

echo "Allocated GPUs (CUDA_VISIBLE_DEVICES from Slurm): $CUDA_VISIBLE_DEVICES"
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
EOF

echo -e "\n========================================"
echo "Starting baseline training"
echo "gpu_devices=${GPU_DEVICES}"
echo "num_actor_devices=${NUM_ACTOR_DEVICES}"
echo "num_actors=${NUM_ACTORS}"
echo "training_device=${TRAINING_DEVICE}"
echo "objective=${OBJECTIVE}"
echo "total_frames=${TOTAL_FRAMES}"
echo "xpid=${XPID}"
echo "savedir=${SAVEDIR}"
echo "========================================"

python3 train.py \
  --load_model \
  --gpu_devices "${GPU_DEVICES}" \
  --num_actor_devices "${NUM_ACTOR_DEVICES}" \
  --num_actors "${NUM_ACTORS}" \
  --training_device "${TRAINING_DEVICE}" \
  --objective "${OBJECTIVE}" \
  --total_frames "${TOTAL_FRAMES}" \
  --xpid "${XPID}" \
  --savedir "${SAVEDIR}" \
  --save_interval "${SAVE_INTERVAL}" \
  --batch_size "${BATCH_SIZE}" \
  --unroll_length "${UNROLL_LENGTH}" \
  --num_buffers "${NUM_BUFFERS}" \
  --num_threads "${NUM_THREADS}"

echo -e "\n========================================"
echo "Baseline training complete"
echo "End time: $(date)"
echo "========================================"
