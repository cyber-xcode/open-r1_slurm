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
    ln -s "$rootdir/tmp_dir_json" "$HOME/.cache/huggingface/datasets/json"
fi

set -x -e
source ~/.bashrc
export CUDA_HOME=/opt/apps/software/CUDA/12.6.0/

cd "/common/home/users/j/jwang/scratchDirectory/wj_code/dl_loop/vanilla_direct"

if [ ! -d "$HOME/envs/${hostname}_openr1" ]; then 
    uv venv "$HOME/envs/${hostname}_openr1" --python 3.11 
fi 

source "$HOME/envs/${hostname}_openr1/bin/activate"

# Test Python environment for CUDA, flash-attn, and vllm support
# If any component is missing or broken, reinstall all packages

echo "Testing Python environment..."

# Function to test CUDA support
test_cuda() {
    python -c "
import torch
try:
    print(f'PyTorch version: {torch.__version__}')
    print(f'CUDA available: {torch.cuda.is_available()}')
    if torch.cuda.is_available():
        print(f'CUDA version: {torch.version.cuda}')
        print(f'CUDA device count: {torch.cuda.device_count()}')
        print(f'Current device: {torch.cuda.current_device()}')
        print(f'Device name: {torch.cuda.get_device_name(0)}')
        # Test basic CUDA operation
        x = torch.randn(2, 3).cuda()
        y = x * 2
        print('CUDA tensor operations: OK')
    else:
        raise Exception('CUDA not available')
except Exception as e:
    print(f'CUDA test failed: {e}')
    exit(1)
" 2>/dev/null
    return $?
}

# Function to test flash-attn
test_flash_attn() {
    python -c "
try:
    import flash_attn
    print(f'flash-attn version: {flash_attn.__version__}')
    from flash_attn import flash_attn_func
    print('flash-attn import: OK')
except Exception as e:
    print(f'flash-attn test failed: {e}')
    exit(1)
" 2>/dev/null
    return $?
}

# Function to test vllm
test_vllm() {
    python -c "
try:
    import vllm
    print(f'vllm version: {vllm.__version__}')
    from vllm import LLM
    print('vllm import: OK')
except Exception as e:
    print(f'vllm test failed: {e}')
    exit(1)
" 2>/dev/null
    return $?
}

# Run tests
echo "=== Testing CUDA support ==="
if test_cuda; then
    echo "✓ CUDA test passed"
    CUDA_OK=1
else
    echo "✗ CUDA test failed"
    CUDA_OK=0
fi

echo ""
echo "=== Testing flash-attn ==="
if test_flash_attn; then
    echo "✓ flash-attn test passed"
    FLASH_ATTN_OK=1
else
    echo "✗ flash-attn test failed"
    FLASH_ATTN_OK=0
fi

echo ""
echo "=== Testing vllm ==="
if test_vllm; then
    echo "✓ vllm test passed"
    VLLM_OK=1
else
    echo "✗ vllm test failed"
    VLLM_OK=0
fi

echo ""
echo "=== Test Summary ==="
echo "CUDA: $([ $CUDA_OK -eq 1 ] && echo '✓ PASS' || echo '✗ FAIL')"
echo "flash-attn: $([ $FLASH_ATTN_OK -eq 1 ] && echo '✓ PASS' || echo '✗ FAIL')"
echo "vllm: $([ $VLLM_OK -eq 1 ] && echo '✓ PASS' || echo '✗ FAIL')"

# Check if all tests passed
if [ $CUDA_OK -eq 1 ] && [ $FLASH_ATTN_OK -eq 1 ] && [ $VLLM_OK -eq 1 ]; then
    echo ""
    echo "🎉 All tests passed! Environment is ready."
    echo "Skipping package installation."
else
    echo ""
    echo "⚠️  Some tests failed. Installing/reinstalling packages..."
    echo ""
    
    # Install packages
    echo "Installing setuptools..."
    uv pip install setuptools 
    echo "Installing/upgrading vllm and torch..."
    uv pip install -U vllm torch  --force-reinstall
    
    echo "Installing flash-attn..."
    uv pip install flash-attn --no-build-isolation --force-reinstall
    
    echo "Uninstalling torchvision..."
    uv pip uninstall torchvision 
    
    echo "Installing development and utility packages..."
    uv pip install pytest-timeout pytest z3-solver ftfy redis pytest-asyncio gunicorn uvicorn supervisor backoff tensorboardX tensorboard 
    
    echo "Installing core packages..."
    uv pip install  fire \
        stop-sequencer \
        wget \
        appdirs \
        tempdir \
        multipledispatch \
        numpy \
        tqdm \
        termcolor \
        rich \
        openai \
        datasets \
        psutil \
        anthropic \
        google-generativeai \
        boto3 
    
    echo "Installing/upgrading vllm and torch..."
    uv pip install -U vllm torch  --force-reinstall
    
    echo ""
    echo "✅ Package installation completed!"
    echo ""
    echo "Re-running tests to verify installation..."
    
    # Re-run tests
    echo "=== Re-testing CUDA support ==="
    if test_cuda; then
        echo "✓ CUDA test passed"
    else
        echo "✗ CUDA test still failing"
    fi
    
    echo ""
    echo "=== Re-testing flash-attn ==="
    if test_flash_attn; then
        echo "✓ flash-attn test passed"
    else
        echo "✗ flash-attn test still failing"
    fi
    
    echo ""
    echo "=== Re-testing vllm ==="
    if test_vllm; then
        echo "✓ vllm test passed"
    else
        echo "✗ vllm test still failing"
    fi
fi


bash test_flash.sh 

echo ""
echo "Script completed at $(date)"



echo "START TIME: $(date)"

MODEL=$1

#python -m torch.utils.collect_env

# NCCL debugging options (commented out)
#export NCCL_ASYNC_ERROR_HANDLING=1
#export NCCL_DEBUG=INFO
#export CUDA_LAUNCH_BLOCKING=1
#export TORCH_NCCL_ASYNC_ERROR_HANDLING=1 
#export NCCL_DEBUG_SUBSYS=COLL
#export NCCL_SOCKET_NTHREADS=1
#export NCCL_NSOCKS_PERTHREAD=1

export LAUNCHER="HF_HUB_ENABLE_HF_TRANSFER=1 ACCELERATE_LOG_LEVEL=info TRANSFORMERS_VERBOSITY=info bash pre_prepare_model_v2.sh"
echo "LAUNCHER......"$LAUNCHER

# SRUN arguments
SRUN_ARGS=" \
    --wait=60 \
    --kill-on-bad-exit=1 \
    "

echo "MODEL---"$MODEL
echo "LAUNCHER--"$LAUNCHER
echo "SLURM_JOB_ID--"$SLURM_JOB_ID
echo "SRUN_ARGS---"$SRUN_ARGS
echo "---<----done"

# Check if MODEL is provided
if [ -z "$MODEL" ]; then
    echo "Error: MODEL parameter is required"
    exit 1
fi

# Run the main command
srun $SRUN_ARGS bash -c "$LAUNCHER $MODEL" 2>&1

echo "END TIME: $(date)"
