export PYTHONPATH="./src"

#export CUDA_VISIBLE_DEVICES=0,1,2,3


export NCCL_DEBUG="INFO"



config_files=(
	"recipes/Qwen2.5-1.5B-Instruct/sft_aha_1b5_7b/g_d2ba74c17369a4d208b8df3b66ccc3e0_1b5.yaml"
	"recipes/Qwen2.5-1.5B-Instruct/sft_aha_1b5_7b/g_effba7d9b1a177d4ac42f9aee6e43d8d_1b5.yaml"
	"recipes/Qwen2.5-1.5B-Instruct/sft_aha_1b5_7b/g_593d97829ffca5fd3f37c7f983278d60_1b5_large.yaml"
	"recipes/Qwen2.5-1.5B-Instruct/sft_aha_1b5_7b/g_c3cd54bbb7e22b44e1299bf0e8c778d6_1b5_verylarge.yaml"
)




for config in "${config_files[@]}"; do

  # Generate a random port
  PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
  
  # Extract a base name for the log file
  log_name=$(basename "$config" .yaml)
  
  echo "Running with config: $config"
  echo "Logging to: ddp_grpo_${log_name}.log"
  
  accelerate launch --config_file recipes/accelerate_configs/zero3.yaml \
    --num_processes 4 \
    --main_process_port $PORT \
    src/open_r1/sft_raw.py \
    --per_device_train_batch_size 1 \
    --config "$config" \
     2>&1 | tee "zero3_sft_${log_name}.log"
  
  echo "Finished running $config"
  echo "----------------------------------------"

  sleep 5 
done




