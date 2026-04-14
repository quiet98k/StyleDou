#!/bin/bash
#SBATCH --job-name=douzero_train_baseline
#SBATCH --nodes=1
#SBATCH --gres=gpu:a5000:3
#SBATCH --cpus-per-task=32
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

CONDA_SH="$HOME/miniconda3/etc/profile.d/conda.sh"
if [[ ! -f "$CONDA_SH" ]]; then
  echo "Conda init script not found: $CONDA_SH" >&2
  exit 1
fi

source "$CONDA_SH"
conda activate dou

cd "$WORKDIR"
mkdir -p logs

# ------------------------------
# Training config (override via env)
# Example:
# sbatch --export=ALL,GPU_DEVICES=0,1,NUM_ACTOR_DEVICES=2,NUM_ACTORS=10,TRAINING_DEVICE=0,TOTAL_FRAMES=500000000 scripts/train_baseline.sbatch
# ------------------------------
GPU_DEVICES=${GPU_DEVICES:-}
NUM_ACTOR_DEVICES=${NUM_ACTOR_DEVICES:-}
NUM_ACTORS=${NUM_ACTORS:-}
TRAINING_DEVICE=${TRAINING_DEVICE:-0}
OBJECTIVE=${OBJECTIVE:-adp}
TOTAL_FRAMES=${TOTAL_FRAMES:-500000000}
XPID=${XPID:-baseline}
SAVEDIR=${SAVEDIR:-douzero_checkpoints/baseline}
SAVE_INTERVAL=${SAVE_INTERVAL:-60}
BATCH_SIZE=${BATCH_SIZE:-32}
UNROLL_LENGTH=${UNROLL_LENGTH:-100}
NUM_BUFFERS=${NUM_BUFFERS:-50}
NUM_THREADS=${NUM_THREADS:-4}

export PYTHONHASHSEED=0

echo "Allocated GPUs (CUDA_VISIBLE_DEVICES from Slurm): $CUDA_VISIBLE_DEVICES"
nvidia-smi

GPU_COUNT=$(nvidia-smi -L | wc -l | tr -d ' ')
if [[ "$GPU_COUNT" -lt 1 ]]; then
  echo "Expected at least 1 GPU on this node, but only saw ${GPU_COUNT}."
  exit 1
fi

# Derive defaults from allocated GPUs when not provided.
if [[ -z "$GPU_DEVICES" ]]; then
  if [[ "$GPU_COUNT" -eq 1 ]]; then
    GPU_DEVICES="0"
  else
    GPU_DEVICES=$(seq -s, 0 $((GPU_COUNT - 1)))
  fi
fi
if [[ -z "$NUM_ACTOR_DEVICES" ]]; then
  NUM_ACTOR_DEVICES="$GPU_COUNT"
fi
if [[ -z "$NUM_ACTORS" ]]; then
  NUM_ACTORS=10
fi

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
