#!/bin/bash
#SBATCH --job-name=eval_direct

# --- resources ----------------------------------------------------------
#SBATCH --nodes=1                       # one node
#SBATCH --ntasks=1                      # one MPI task
#SBATCH --cpus-per-task=32              # ≤ 32 CPU (limit)
#SBATCH --gres=gpu:1                # 1 GPU (≤ 2) and force A40s
#SBATCH --mem=128G                      # ≤ 384 G (limit)
# ------------------------------------------------------------------------

# --- scheduling / accounting --------------------------------------------
#SBATCH --partition=researchshort       # or whatever partition you normally use
#SBATCH --qos=research-1-qos            # **NEW** QoS that enforces the limits
#SBATCH --account=xiaofeiresearch
# ------------------------------------------------------------------------

# --- I/O -----------------------------------------------------------------
#SBATCH --output=./logs/%x_%j.out
#SBATCH --error=./logs/%x_%j.err
# ------------------------------------------------------------------------

module load CUDA/12.6.0
module load cuDNN/9.5.0.50-CUDA-12.6.0
module load Anaconda3/2024.06-1





hostname=$(hostname)

echo "hostname..."$hostname
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


#cd  "./open-r1_formal" 
cd "/common/home/users/j/jwang/scratchDirectory/wj_code/dl_loop/vanilla_direct"

if [ ! -d   "$HOME/envs/${hostname}_openr1"  ]; then 
        uv venv "$HOME/envs/${hostname}_openr1" --python 3.11 
fi 

source  "$HOME/envs/${hostname}_openr1"/bin/activate && uv pip install --upgrade pip

#uv pip install vllm==0.7.2 --force-reinstall 
uv pip install setuptools 
uv pip install flash-attn --no-build-isolation  --force-reinstall
uv pip uninstall torchvision
uv pip install pytest-timeout   pytest z3-solver  ftfy  redis pytest_asyncio gunicorn uvicorn  supervisor backoff ftfy tensorboardX tensorboard 
uv pip install  fire \
stop-sequencer \
wget \
appdirs \
tempdir \
multipledispatch \
numpy \
tqdm \
termcolor \
fire \
rich \
openai \
datasets \
psutil \
anthropic \
google-generativeai \
boto3 

uv pip install -U vllm torch #--force-reinstall 



#source  "$HOME/envs/${hostname}_openr1"/bin/activate && uv pip install --upgrade pip









echo "START TIME: $(date)"



MODEL=$1

MASTER_PORT=${7}
if [ -z $MASTER_PORT ]; then 
        MASTER_PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
fi 




python  -m  torch.utils.collect_env




# force crashing on nccl issues like hanging broadcast
#export NCCL_ASYNC_ERROR_HANDLING=1
#export NCCL_DEBUG=INFO
#export CUDA_LAUNCH_BLOCKING=1
#export TORCH_NCCL_ASYNC_ERROR_HANDLING=1 

#export NCCL_DEBUG_SUBSYS=COLL
#export NCCL_SOCKET_NTHREADS=1
#export NCCL_NSOCKS_PERTHREAD=1
# export CUDA_LAUNCH_BLOCKING=1


export LAUNCHER="HF_HUB_ENABLE_HF_TRANSFER=1 ACCELERATE_LOG_LEVEL=info TRANSFORMERS_VERBOSITY=info bash pre_prepare_model_v2.sh "


echo "LAUNCHER......"$LAUNCHER


# --wait=60: wait 60 sec after the first task terminates before terminating all remaining tasks
# --kill-on-bad-exit=1: terminate a step if any task exits with a non-zero exit code

SRUN_ARGS=" \
    --wait=60 \
    --kill-on-bad-exit=1 \
    "

echo "MODEL---"$MODEL
echo "LAUNCHER--"$LAUNCHER
echo "SLURM_JOB_ID--"$SLURM_JOB_ID
echo "SRUN_ARGS---"$SRUN_ARGS

echo "---<----done "

clear; srun $SRUN_ARGS --jobid $SLURM_JOB_ID bash -c "$LAUNCHER  $MODEL  " 2>&1


echo "END TIME: $(date)"

