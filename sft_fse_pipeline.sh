export CUDA_HOME="/opt/apps/software/CUDA/12.6.0/"
export PYTHONPATH="./src"
#export NCCL_DEBUG="INFO"

config_files=(
	recipes_paper/reduce_rq4/sft_reduce_full.yaml

)


readarray -t reversed < <(printf '%s\n' "${config_files[@]}" | tac)


for config in "${reversed[@]}"; do
  # Generate a random port
  PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
  
  # Extract a base name for the log file
  log_name=$(basename "$config" .yaml)
  
  echo "Running with config: $config"
  echo "Logging to: ddp_grpo_${log_name}.log"
  
  accelerate launch --config_file recipes/accelerate_configs/fsdp.yaml \
    --num_processes 4 \
    --main_process_port $PORT \
    src/open_r1/sft_raw.py \
    --config "$config" \
     2>&1 | tee "zero3_sft_${log_name}.log"
  
  echo "Finished running $config"
  echo "----------------------------------------"

  sleep 5 
done















#cd /common/home/users/j/jwang/scratchDirectory/wj_code/dl_loop/vanilla_direct
#bash r_large.sh 
#cd /common/home/users/j/jwang/scratchDirectory/wj_code/dl_loop/open-r1_formal


#vllm serve Qwen/Qwen3-30B-A3B --enable-prefix-caching --reasoning-parser deepseek_r1 --port 8001  -tp 4 


