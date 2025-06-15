#!/bin/bash
#SBATCH --job-name=open-r1-sft
#SBATCH --nodes=1                  # Request 2 nodes
#SBATCH --gres=gpu:4               # 2 GPUs per node (total: 4 GPUs)
#SBATCH --constraint=h200
#SBATCH --account=xiaofeiresearch
#SBATCH --qos=jwangqos-20250431
#SBATCH --partition=researchshort
#SBATCH --mem=400G                 # Per-node memory
#SBATCH --cpus-per-task=120         # CPUs per task (for data loading)
#SBATCH --output=./logs/%x_%j.out
#SBATCH --error=./logs/%x_%j.err
#SBATCH --gres-flags=enforce-binding

#srun   --account=xiaofeiresearch --partition=researchshort   --qos=jwangqos-20250431  --pty --mem=400G --cpus-per-task=120 --gres=gpu:4         --constraint=h200  enroot start  cuda_container_root  sh -c "sleep infinity" 
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

uv pip install wandb
wandb offline 



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

python  -m  torch.utils.collect_env




# force crashing on nccl issues like hanging broadcast
export NCCL_ASYNC_ERROR_HANDLING=1
#export NCCL_NSOCKS_PERTHREAD=1
# export CUDA_LAUNCH_BLOCKING=1

echo "LAUNCHER......"$LAUNCHER
SRUN_ARGS=" \
    --wait=60 \
    --kill-on-bad-exit=1 \
    "
clear; srun $SRUN_ARGS --jobid $SLURM_JOB_ID bash -c "bash r_gpu2c.sh" 2>&1

echo "END TIME: $(date)"

