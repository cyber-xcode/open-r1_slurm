#!/bin/bash
#SBATCH --job-name=open-r1-sft
#SBATCH --nodes=2                  # Request 2 nodes
#SBATCH --ntasks-per-node=1        # 1 task per node (for DDP, tasks = GPUs)
#SBATCH --gres=gpu:2               # 2 GPUs per node (total: 4 GPUs)
#SBATCH --account=xiaofeiresearch
#SBATCH --partition=researchshort
#SBATCH --mem=128G                 # Per-node memory
#SBATCH --cpus-per-task=32         # CPUs per task (for data loading)
#SBATCH --output=./logs/%x_%j.out
#SBATCH --error=./logs/%x_%j.err
#SBATCH --gres-flags=enforce-binding

# Load modules
module load CUDA/12.6.0 
module load cuDNN/9.5.0.50-CUDA-12.6.0
module load Anaconda3/2024.06-1


#/common/home/users/j/jwang/wj_code/dl_loop/open-r1/logs
# Specific configuration optimized for the Hugging Face Compute Cluster
module load CUDA/12.6.0 
module load cuDNN/9.5.0.50-CUDA-12.6.0
module load    Anaconda3/2024.06-1  


hostname=$(hostname)
echo "hostname..."$hostname
#export HF_TOKEN=$HF_TOKEN



echo "HF_TOKEN..."$HF_TOKEN
echo "WANDB_API_KEY..."$WANDB_API_KEY


export rootdir="/common/home/users/j/jwang/"
export workhome="/common/home/users/j/jwang/scratchDirectory/wj_code/dl_loop"
mkdir -p $workhome
cd $workhome

mkdir -p "$rootdir/tmp_dir_json"

if [[ ! -d "$HOME/.cache/huggingface/datasets/json" ]]; then 
	ln -s  "$rootdir/tmp_dir_json"  "$HOME/.cache/huggingface/datasets/json"
fi	


set -x -e

source ~/.bashrc


export CUDA_HOME=/opt/apps/software/CUDA/12.6.0/


#if [ ! -d "${workhome}/open-r1" ]; then 
#        git clone https://github.com/huggingface/open-r1 
#fi 

cd  "./open-r1_formal" 
if [ ! -d   "$HOME/envs/${hostname}_openr1"  ]; then 
        uv venv "$HOME/envs/${hostname}_openr1" --python 3.11 

	source  "$HOME/envs/${hostname}_openr1"/bin/activate && uv pip install --upgrade pip

	uv pip install vllm==0.7.2 --force-reinstall 
	uv pip install setuptools 
	uv pip install flash-attn --no-build-isolation  --force-reinstall
	GIT_LFS_SKIP_SMUDGE=1 uv pip install -e ".[dev]"  --force-reinstall
	uv pip uninstall torchvision
	uv pip install pytest-timeout   pytest z3-solver  ftfy  redis pytest_asyncio gunicorn uvicorn  supervisor backoff ftfy tensorboardX tensorboard 

fi 


source  "$HOME/envs/${hostname}_openr1"/bin/activate && uv pip install --upgrade pip




echo "START TIME: $(date)"

MODEL=$1
TASK=$2
CONFIG_SUFFIX=$3
ACCELERATOR=$4
OPTIONAL_ARGS=$5
GPUS_PER_NODE=${6:-8}

MASTER_PORT=${7}
if [ -z $MASTER_PORT ]; then 
	MASTER_PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
fi 

CONFIG_FILE=recipes/$MODEL/$TASK/config_$CONFIG_SUFFIX.yaml

if [[ ! -f $CONFIG_FILE ]]; then 
	CONFIG_FILE=$CONFIG_SUFFIX
fi 	


GRAD_ACC_STEPS=$(grep 'gradient_accumulation_steps' $CONFIG_FILE | awk '{print $2}')
MODEL=$(grep 'model_name_or_path:' $CONFIG_FILE | awk '{print $2}')
REVISION=$(grep 'model_revision:' $CONFIG_FILE | head -n 1 | awk '{print $2}')

# Distributed configuration
NUM_NODES=$SLURM_NNODES
#GPUS_PER_NODE=8
WORLD_SIZE=$(($NUM_NODES*$GPUS_PER_NODE))
NODELIST=($(scontrol show hostnames $SLURM_JOB_NODELIST))
MASTER_ADDR=${NODELIST[0]}  # First node for main process


TRAIN_NODES=("${NODELIST[@]}")

USE_VLLM="false"
if [[ -f "$CONFIG_FILE" ]] && grep -qE '^\s*use_vllm:\s*true' "$CONFIG_FILE"; then
    USE_VLLM="true"
fi
# if using vllm
if [[ "$USE_VLLM" == "true" ]]; then
     TRAIN_NODES=("${NODELIST[@]:0:$((NUM_NODES - 1))}")
     VLLM_NODE=${NODELIST[-1]} # Last node
     TP=$(python scripts/get_tensor_parallel_size.py --model_name $MODEL --revision $REVISION --default_tp $GPUS_PER_NODE)
     WORLD_SIZE=$((WORLD_SIZE - GPUS_PER_NODE))
     NUM_NODES=$((NUM_NODES - 1))
     srun --nodes=1 --ntasks=1 --nodelist=$VLLM_NODE trl vllm-serve --model $MODEL --revision $REVISION --tensor_parallel_size $TP &

     OPTIONAL_ARGS="$OPTIONAL_ARGS --vllm_server_host=$VLLM_NODE"
fi



echo "MASTER_ADDR::::"$MASTER_ADDR
echo "OPTIONAL_ARGS:::"$OPTIONAL_ARGS

if [[ "$MASTER_ADDR" == "candle" || \
      "$MASTER_ADDR" == "lexicon" || \
      "$MASTER_ADDR" == "lunar" || \
      "$MASTER_ADDR" == "comet" ]]; then
  OPTIONAL_ARGS="$OPTIONAL_ARGS --ddp_backend=gloo "
fi

if [[ "$MASTER_ADDR" == "analog" ]]; then 
  OPTIONAL_ARGS="$OPTIONAL_ARGS  --per_device_train_batch_size=4 "
fi



python  -m  torch.utils.collect_env




# force crashing on nccl issues like hanging broadcast
export NCCL_ASYNC_ERROR_HANDLING=1
#export NCCL_DEBUG=INFO
#export CUDA_LAUNCH_BLOCKING=1
#export TORCH_NCCL_ASYNC_ERROR_HANDLING=1 

#export NCCL_DEBUG_SUBSYS=COLL
#export NCCL_SOCKET_NTHREADS=1
#export NCCL_NSOCKS_PERTHREAD=1
# export CUDA_LAUNCH_BLOCKING=1

export CMD=" \
    src/open_r1/$TASK.py --config $CONFIG_FILE $OPTIONAL_ARGS
    "

export LAUNCHER="HF_HUB_ENABLE_HF_TRANSFER=1 ACCELERATE_LOG_LEVEL=info TRANSFORMERS_VERBOSITY=info accelerate launch \
    --config_file recipes/accelerate_configs/$ACCELERATOR.yaml  \
    --gradient_accumulation_steps $GRAD_ACC_STEPS \
    --num_machines $NUM_NODES \
    --num_processes $WORLD_SIZE \
    --main_process_ip $MASTER_ADDR \
    --main_process_port $MASTER_PORT \
    --machine_rank $SLURM_PROCID \
    --rdzv_backend=c10d \
    --max_restarts 1 \
    --role \$(hostname -s): \
    --tee 3 \
    "


echo "LAUNCHER......"$LAUNCHER
# srun error handling:
# --wait=60: wait 60 sec after the first task terminates before terminating all remaining tasks
# --kill-on-bad-exit=1: terminate a step if any task exits with a non-zero exit code
SRUN_ARGS=" \
    --wait=60 \
    --kill-on-bad-exit=1 \
    --nodes=$NUM_NODES \
    --ntasks=$NUM_NODES \
    --nodelist=$TRAIN_NODES
    "
clear; srun $SRUN_ARGS --jobid $SLURM_JOB_ID bash -c "$LAUNCHER --role \$SLURMD_NODENAME: $CMD" 2>&1

echo "END TIME: $(date)"

