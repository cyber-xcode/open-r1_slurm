#!/bin/bash

export NCCL_DEBUG=INFO
#"recipes/Qwen2.5-1.5B-Instruct/grpo_removed_5k_coder/sft40_5k1.yaml"
#"recipes/Qwen2.5-1.5B-Instruct/grpo_removed_5k_coder/vn_5k2.yaml"
#"recipes/Qwen2.5-1.5B-Instruct/grpo_removed_5k_coder/sft40_5k3.yaml"

# Define config files array
config_files=(

"recipes/Qwen2.5-1.5B-Instruct/grpo_removed_5k_coder/sft40_5k2.yaml"
"recipes/Qwen2.5-1.5B-Instruct/grpo_removed_5k_coder/vn_5k1.yaml"
"recipes/Qwen2.5-1.5B-Instruct/grpo_removed_5k/sft40_5k1.yaml"
"recipes/Qwen2.5-1.5B-Instruct/grpo_removed_5k/sft40_5k2.yaml"
"recipes/Qwen2.5-1.5B-Instruct/grpo_removed_5k/vn_5k1.yaml"
"recipes/Qwen2.5-1.5B-Instruct/grpo_removed_5k/vn_5k2.yaml"
"recipes/Qwen2.5-1.5B-Instruct/grpo_removed_5k/vn_5k3.yaml"

)

shuffled_configs=($(printf '%s\n' "${config_files[@]}" | shuf))


for config in "${shuffled_configs[@]}"; do
    echo "Processing config: $config"
    
    sleep 15
    #PORT_VLLM=8002 
    PORT_VLLM=$(( RANDOM % 101 + 8000 ))

    #$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))

  # Determine model based on config path
  if [[ $config == *"coder"* ]]; then
    model="Qwen/Qwen2.5-Coder-1.5B-Instruct"
  else
    model="Qwen/Qwen2.5-1.5B-Instruct"
  fi


    # Start the vllm-serve process and capture its PID
    CUDA_VISIBLE_DEVICES=3 nohup trl vllm-serve --model $model --tensor-parallel-size 1 --data-parallel-size 1 --port $PORT_VLLM 2>&1 >/dev/null &
    VLLM_PID=$!

    echo "Started vllm-serve process with PID: $VLLM_PID"

    sleep 60 

    PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
    
    # Extract config name for log file
    config_name=$(basename "$config" .yaml)
    
    accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
             --num_processes 3 \
            --main_process_port $PORT \
                      src/open_r1/grpo.py \
            --config "$config" \
	    --vllm_server_port $PORT_VLLM \
        --per_device_train_batch_size 16  2>&1 | tee "${config_name}.log"



# Kill parent + all child processes
if kill -0 $VLLM_PID 2>/dev/null; then
    echo "Killing vllm-serve (PID: $VLLM_PID) and its subprocesses..."
    CHILD_PIDS=$(pgrep -P $VLLM_PID)  # Get all direct child PIDs
    kill -9 $VLLM_PID $CHILD_PIDS 2>/dev/null  # Terminate aggressively
    echo "Killed parent PID $VLLM_PID and children: $CHILD_PIDS"

    echo "Parent process $VLLM_PID already dead. Cleaning up stragglers..."
    pkill -f "trl vllm-serve.*$PORT_VLLM"  # Fallback to port-based kill
    ps -ef | awk '$3 == 1 && $8 ~ /python/ && /multiprocessing/'|awk '{print $2}'|xargs kill -9 
fi



#ps -ef|grep "$VLLM_PID"|awk '{print $2}'|xargs kill -9 


    sleep 150
    
    echo "Completed processing config: $config"
    echo "----------------------------------------"
done
