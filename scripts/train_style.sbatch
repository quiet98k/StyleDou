#!/bin/bash
#SBATCH --job-name=douzero_train_style
#SBATCH --nodes=1
#SBATCH --gres=gpu:a6000:3
#SBATCH --cpus-per-task=32
#SBATCH --mem=64G
#SBATCH --time=3-00:00:00
#SBATCH --output=logs/train_style_%j.log
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

VENV_DIR=${VENV_DIR:-$WORKDIR/.venv}
if [[ ! -f "$VENV_DIR/bin/activate" ]]; then
  echo "Virtualenv activate script not found: $VENV_DIR/bin/activate" >&2
  exit 1
fi

source "$VENV_DIR/bin/activate"

cd "$WORKDIR"
mkdir -p logs

# ------------------------------
# Training config (override via env)
# Example:
# sbatch --export=ALL,NUM_ACTOR_DEVICES=1,NUM_ACTORS=5,TRAINING_DEVICE=0,TOTAL_FRAMES=1000000000 scripts/train_style.sbatch
# ------------------------------
GPU_DEVICES=${GPU_DEVICES:-}
NUM_ACTOR_DEVICES=${NUM_ACTOR_DEVICES:-}
NUM_ACTORS=${NUM_ACTORS:-}
TRAINING_DEVICE=${TRAINING_DEVICE:-0}
OBJECTIVE=${OBJECTIVE:-adp}
TOTAL_FRAMES=${TOTAL_FRAMES:-500000000}
XPID=${XPID:-style_model_new}
SAVEDIR=${SAVEDIR:-douzero_checkpoints/style}
SAVE_INTERVAL=${SAVE_INTERVAL:-60}
BATCH_SIZE=${BATCH_SIZE:-32}
UNROLL_LENGTH=${UNROLL_LENGTH:-100}
NUM_BUFFERS=${NUM_BUFFERS:-50}
NUM_THREADS=${NUM_THREADS:-4}
EVAL_NUM_GAMES=${EVAL_NUM_GAMES:-10000}
EVAL_GPU_DEVICE=${EVAL_GPU_DEVICE:-0}
AUX_LOSS_WEIGHT=${AUX_LOSS_WEIGHT:-0.1}
STYLE_EMBED_DIM=${STYLE_EMBED_DIM:-128}
HISTORY_EMBED_DIM=${HISTORY_EMBED_DIM:-128}
ACTOR_DEVICE_CPU=${ACTOR_DEVICE_CPU:-0}

export PYTHONHASHSEED=0

if [[ "$ACTOR_DEVICE_CPU" == "1" ]]; then
  ACTOR_DEVICE_CPU_FLAG="--actor_device_cpu"
else
  ACTOR_DEVICE_CPU_FLAG=""
fi

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
echo "Starting style-model training"
echo "gpu_devices=${GPU_DEVICES}"
echo "num_actor_devices=${NUM_ACTOR_DEVICES}"
echo "num_actors=${NUM_ACTORS}"
echo "training_device=${TRAINING_DEVICE}"
echo "objective=${OBJECTIVE}"
echo "total_frames=${TOTAL_FRAMES}"
echo "save_interval_minutes=${SAVE_INTERVAL}"
echo "eval_num_games=${EVAL_NUM_GAMES}"
echo "eval_gpu_device=${EVAL_GPU_DEVICE}"
echo "xpid=${XPID}"
echo "savedir=${SAVEDIR}"
echo "actor_device_cpu=${ACTOR_DEVICE_CPU}"
echo "aux_loss_weight=${AUX_LOSS_WEIGHT}"
echo "style_embed_dim=${STYLE_EMBED_DIM}"
echo "history_embed_dim=${HISTORY_EMBED_DIM}"
echo "========================================"


python3 train_style.py \
  --load_model \
  --run_eval_on_checkpoint \
  --gpu_devices "${GPU_DEVICES}" \
  --num_actor_devices "${NUM_ACTOR_DEVICES}" \
  --num_actors "${NUM_ACTORS}" \
  --training_device "${TRAINING_DEVICE}" \
  --objective "${OBJECTIVE}" \
  --total_frames "${TOTAL_FRAMES}" \
  --save_interval "${SAVE_INTERVAL}" \
  --xpid "${XPID}" \
  --savedir "${SAVEDIR}" \
  --batch_size "${BATCH_SIZE}" \
  --unroll_length "${UNROLL_LENGTH}" \
  --num_buffers "${NUM_BUFFERS}" \
  --num_threads "${NUM_THREADS}" \
  --eval_num_games "${EVAL_NUM_GAMES}" \
  --eval_gpu_device "${EVAL_GPU_DEVICE}" \
  --aux_loss_weight "${AUX_LOSS_WEIGHT}" \
  --style_embed_dim "${STYLE_EMBED_DIM}" \
  --history_embed_dim "${HISTORY_EMBED_DIM}" \
  ${ACTOR_DEVICE_CPU_FLAG}

echo -e "\n========================================"
echo "Style-model training complete"
echo "End time: $(date)"
echo "========================================"
