

#recipes/Qwen2.5-1.5B-Instruct/onlyz3_sft_grpo/grpo_fromonlyze3_thensft_removehard_esbmc_full.yaml
#recipes/Qwen2.5-1.5B-Instruct/onlyz3_sft_grpo/grpo_fromonlyze3_thensft__esbmc_full.yaml

#"recipes/Qwen2.5-1.5B-Instruct/onlyz3_sft_grpo/grpo_vanillacoder_removehard__esbmc_5k.yaml"
#"recipes/Qwen2.5-1.5B-Instruct/onlyz3_sft_grpo/grpo_vanillacoder_removehard__esbmc_mix_5k.yaml"
#"recipes/Qwen2.5-1.5B-Instruct/onlyz3_sft_grpo/grpo_vanilla_removehard__esbmc_5k.yaml"
#"recipes/Qwen2.5-1.5B-Instruct/onlyz3_sft_grpo/grpo_vanilla_removehard__esbmc_mix_5k.yaml"


config_files=(

"recipes/Qwen2.5-1.5B-Instruct/onlyz3_sft_grpo/grpo_fromonlyze3_thensft__esbmc_5k.yaml"
"recipes/Qwen2.5-1.5B-Instruct/onlyz3_sft_grpo/grpo_fromonlyze3_thensft_removehard__esbmc_5k.yaml"
"recipes/Qwen2.5-1.5B-Instruct/onlyz3_sft_grpo/grpo_fromonlyze3_thensft_removehard__esbmc_mix_5k.yaml"

)

for config in "${config_files[@]}"; do

  ### 
  ps -ef|grep python |grep -E "vllm|multiprocessing"|awk '{print $2}'|xargs kill -9 
  sleep 5 

  CUDA_VISIBLE_DEVICES=3 nohup trl vllm-serve --model Qwen/Qwen2.5-1.5B-Instruct --tensor-parallel-size 1 --data-parallel-size 1 --port 8000 2>&1 >/dev/null &
  sleep 15

  # Generate a random port
  PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
  
  # Extract a base name for the log file
  log_name=$(basename "$config" .yaml)
  
  echo "Running with config: $config"
  echo "Logging to: ddp_grpo_${log_name}.log"
  
  accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
    --num_processes 3 \
    --main_process_port $PORT \
    src/open_r1/grpo.py \
    --config "$config" \
    --per_device_train_batch_size 16 2>&1 | tee "ddp_grpo_${log_name}.log"
  
  echo "Finished running $config"
  echo "----------------------------------------"

  ### 
  ps -ef|grep python |grep -E "vllm|multiprocessing"|awk '{print $2}'|xargs kill -9 
  sleep 5 
done
