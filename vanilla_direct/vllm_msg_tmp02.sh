#!/bin/bash

# Check if argument is provided
if [ $# -eq 0 ]; then
    echo "Error: Please provide a data directory name as an argument."
    exit 1
fi

name="$1"
model_root=$(cat where_is_root_dir.txt)

# Validate model_root exists
if [ ! -d "$model_root" ]; then
    echo "Error: Model root directory '$model_root' does not exist."
    exit 1
fi

# Get available GPUs
CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-$(nvidia-smi --query-gpu=index --format=csv,noheader | paste -sd ",")}

# Split into an array
IFS=',' read -ra GPU_LIST <<< "$CUDA_VISIBLE_DEVICES"

# Count the number of available GPUs
NUM_GPUS=${#GPU_LIST[@]}

echo "Total NUM_GPUS: $NUM_GPUS"

# Validate input file exists
input_file="data_dir/verified_z3_benchmarks_LaM4Inv_Linear_c_f046820b70f5d4b52fa7d6fc91989446.jsonl"
if [ ! -f "$input_file" ]; then
    echo "Error: Input file '$input_file' not found."
    exit 1
fi

# Create save directory if it doesn't exist
save_dir="./save_dir"
mkdir -p "$save_dir"

# Run the Python script
python collect_chat.py \
    "$name" \
    "$input_file" \
    "$save_dir" \
    --model_root "$model_root" \
    --tp "$NUM_GPUS" \
    --bs 20 \
    --n_samples 20 \
    --temperature 0.2 \
    --resume \
    --backend vllm \
    --prompt_type think_answer

# Check if Python script succeeded
if [ $? -ne 0 ]; then
    echo "Error: Python script execution failed."
    exit 1
fi

echo "Script completed successfully."

