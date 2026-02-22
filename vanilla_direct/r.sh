#!/bin/bash
export CUDA_HOME="/opt/apps/software/CUDA/12.6.0/"

source ~/envs/honey_openr1_llamafatory/bin/activate

# Available GPU devices
#GPUS=(0 1 2 3)
#NUM_GPUS=${#GPUS[@]}

GPUS=($(nvidia-smi --query-gpu=index --format=csv,noheader))

# Count how many GPUs were found
NUM_GPUS=${#GPUS[@]}



cd /common/home/users/j/jwang/scratchDirectory/wj_code/dl_loop/open-r1_formal
find -L save_dir_sft -name '*safetensors'|grep -v checkpoint|awk -F "/model-000" '{print $1}'|sort |uniq | shuf > /common/home/users/j/jwang/scratchDirectory/wj_code/dl_loop/vanilla_direct/m.list 
#find -L save_dir* -name 'trainer_*'|sort|awk -F "/trainer_state" '{print $1}'  |grep assess |shuf  > /common/home/users/j/jwang/scratchDirectory/wj_code/dl_loop/vanilla_direct/m.list
cd /common/home/users/j/jwang/scratchDirectory/wj_code/dl_loop/vanilla_direct

# Check if m.list exists
if [ ! -f "m.list" ]; then
    echo "Error: m.list file not found"
    exit 1
fi

# Get total number of tasks
TOTAL_TASKS=$(wc -l < m.list)
echo "Total tasks: $TOTAL_TASKS"
echo "Available GPUs: ${GPUS[*]}"

# Function to run tasks on a specific GPU
run_on_gpu() {
    local gpu_id=$1
    local start_line=$2
    local end_line=$3
    
    echo "GPU $gpu_id: Processing lines $start_line to $end_line"
    
    # Set CUDA_VISIBLE_DEVICES for this entire process
    export CUDA_VISIBLE_DEVICES=$gpu_id
    
    # Process each line sequentially for this GPU
    for line_num in $(seq $start_line $end_line); do
        if [ $line_num -le $TOTAL_TASKS ]; then
            line=$(sed -n "${line_num}p" m.list)
            if [ ! -z "$line" ]; then
                echo "GPU $gpu_id: Processing $line"
                bash local_vlm_all.sh "$line"
                echo "GPU $gpu_id: Completed $line"
            fi
        fi
    done
    
    echo "GPU $gpu_id: All tasks completed"
}

# Calculate tasks per GPU
TASKS_PER_GPU=$((TOTAL_TASKS / NUM_GPUS))
REMAINDER=$((TOTAL_TASKS % NUM_GPUS))

echo "Tasks per GPU: $TASKS_PER_GPU"
if [ $REMAINDER -gt 0 ]; then
    echo "Remainder tasks: $REMAINDER (will be distributed to first $REMAINDER GPUs)"
fi

# Start background processes for each GPU
PIDS=()
current_line=1

for i in "${!GPUS[@]}"; do
    gpu_id=${GPUS[$i]}
    
    # Calculate start and end lines for this GPU
    start_line=$current_line
    tasks_for_this_gpu=$TASKS_PER_GPU
    
    # Give remainder tasks to first few GPUs
    if [ $i -lt $REMAINDER ]; then
        tasks_for_this_gpu=$((tasks_for_this_gpu + 1))
    fi
    
    end_line=$((start_line + tasks_for_this_gpu - 1))
    
    # Only start process if there are tasks to process
    if [ $start_line -le $TOTAL_TASKS ]; then
        echo "Starting GPU $gpu_id: lines $start_line-$end_line"
        run_on_gpu $gpu_id $start_line $end_line &
        PIDS+=($!)
        current_line=$((end_line + 1))
    fi
done

# Wait for all background processes to complete
echo "Waiting for all GPU processes to complete..."
echo "Started ${#PIDS[@]} parallel processes"

for i in "${!PIDS[@]}"; do
    pid=${PIDS[$i]}
    gpu_id=${GPUS[$i]}
    echo "Waiting for GPU $gpu_id (PID: $pid)..."
    wait $pid
    exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "GPU $gpu_id (PID: $pid) completed successfully"
    else
        echo "GPU $gpu_id (PID: $pid) failed with exit code $exit_code"
    fi
done

echo "All tasks completed!"

