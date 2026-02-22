#!/bin/bash

# Script to fix flash-attn compatibility issues
# The undefined symbol error indicates version mismatch between flash-attn and PyTorch/CUDA

echo "=== Flash-Attention Compatibility Fix ==="
echo "Current time: $(date)"

# Check current versions
echo ""
echo "=== Current Environment ==="
python -c "
import sys
print(f'Python version: {sys.version}')
try:
    import torch
    print(f'PyTorch version: {torch.__version__}')
    print(f'CUDA available: {torch.cuda.is_available()}')
    if torch.cuda.is_available():
        print(f'CUDA version: {torch.version.cuda}')
        print(f'cuDNN version: {torch.backends.cudnn.version()}')
except:
    print('PyTorch not properly installed')

try:
    import flash_attn
    print(f'flash-attn version: {flash_attn.__version__}')
except:
    print('flash-attn not installed or broken')
"

echo ""
echo "=== Fixing flash-attn installation ==="





# Step 3: Verify PyTorch installation
echo "Step 3: Verifying PyTorch installation..."
python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    device_count = torch.cuda.device_count()
    print(f'CUDA devices: {device_count}')
    for i in range(device_count):
        print(f'  Device {i}: {torch.cuda.get_device_name(i)}')
else:
    print('WARNING: CUDA not available!')
"




# Step 4: Install flash-attn
echo "Step 4: Installing flash-attn..."
# Set environment variables for compilation
export CUDA_HOME=${CUDA_HOME:-/opt/apps/software/CUDA/12.6.0/}
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH



# Step 5: Test installation
echo "Step 5: Testing flash-attn installation..."
python -c "
try:
    import flash_attn
    print(f'✓ flash-attn version: {flash_attn.__version__}')
    
    from flash_attn import flash_attn_func
    print('✓ flash_attn_func import successful')
    
    import torch
    if torch.cuda.is_available():
        # Test with minimal tensors
        q = torch.randn(1, 1, 2, 16, dtype=torch.float16, device='cuda')
        k = torch.randn(1, 1, 2, 16, dtype=torch.float16, device='cuda')  
        v = torch.randn(1, 1, 2, 16, dtype=torch.float16, device='cuda')
        
        out = flash_attn_func(q, k, v)
        print('✓ flash-attn functional test passed')
        print(f'✓ Output shape: {out.shape}')
    else:
        print('⚠ CUDA not available, skipping functional test')
        
except ImportError as e:
    print(f'✗ Import error: {e}')
    exit(1)
except Exception as e:
    print(f'✗ Runtime error: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Flash-attention installation successful!"
else
    echo ""
    echo "❌ Flash-attention installation failed!"
    echo ""
    echo "=== Troubleshooting suggestions ==="
    echo "1. Check CUDA installation: ls -la $CUDA_HOME"
    echo "2. Verify CUDA version compatibility"
    echo "3. Try installing from source:"
    echo "   git clone https://github.com/Dao-AILab/flash-attention.git"
    echo "   cd flash-attention && pip install ."
    echo "4. Check for conflicting installations in system Python"



	# Step 1: Clean uninstall
	echo "Step 1: Cleaning existing installations..."
	uv pip uninstall flash-attn 
	uv pip uninstall torch torchvision torchaudio
	uv pip install torch -U
	# Install with specific flags
	#uv pip install --no-cache-dir --no-build-isolation flash-attn
	# Step 2: Install compatible PyTorch with CUDA 12.1
	#echo "Step 2: Installing PyTorch with CUDA 12.1..."
	#uv pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
	uv pip install https://github.com/Dao-AILab/flash-attention/releases/download/v2.7.4.post1/flash_attn-2.7.4.post1+cu12torch2.6cxx11abiTRUE-cp311-cp311-linux_x86_64.whl
fi

echo ""
echo "Script completed at $(date)"
