
export PYTHONPATH="./src"




# List of config paths
config_paths=(
  "recipes/Qwen2.5-1.5B-Instruct/grpo_test/qwencode_config1_reward_222_both_9090only_z3.yaml"
  "recipes/Qwen2.5-1.5B-Instruct/grpo_test/config1_reward_222_133_both.yaml"
  "recipes/Qwen2.5-1.5B-Instruct/grpo_test/qwencode_config1_reward_222_both_908.yaml"
  "recipes/Qwen2.5-1.5B-Instruct/grpo_test_general/config1_reward_222_133_both.yaml"
  "recipes/Qwen2.5-1.5B-Instruct/grpo_test_general/qwencode_config1_reward_222_both_908.yaml"
  "recipes/Qwen2.5-1.5B-Instruct/grpo_test_general/qwencode_config1_reward_222_both_9090only_z3.yaml"
)

# Loop over each config path and launch the process
for config_path in "${config_paths[@]}"; do
        PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
    echo "Launching with config: $config_path"



    ACCELERATE_LOG_LEVEL=info accelerate launch \
        --config_file recipes/accelerate_configs/ddp.yaml \
        --main_process_port "$PORT" \
        --num_processes=3 src/open_r1/grpo.py \
        --config "$config_path" \
	--wandb_project "oper1_a800" 
done

