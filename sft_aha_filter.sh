export CUDA_HOME="/opt/apps/software/CUDA/12.6.0/"
export PYTHONPATH="./src"



export NCCL_DEBUG="INFO"



config_files=(
recipes/Qwen2.5-1.5B-Instruct/sft_aha_1b5_7b_filterscore/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__assert100_oneindex_oai.yaml
recipes/Qwen2.5-1.5B-Instruct/sft_aha_1b5_7b_filterscore/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__assert_lt20_oneindex_oai.yaml
recipes/Qwen2.5-1.5B-Instruct/sft_aha_1b5_7b_filterscore/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__assert_null_or_zero_oneindex_oai.yaml
recipes/Qwen2.5-1.5B-Instruct/sft_aha_1b5_7b_filterscore/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__content2085_assert2085_oneindex_oai.yaml
recipes/Qwen2.5-1.5B-Instruct/sft_aha_1b5_7b_filterscore/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__contentgt85_assertgt85_oneindex_oai.yaml
recipes/Qwen2.5-1.5B-Instruct/sft_aha_1b5_7b_filterscore/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__null_oneindex_oai.yaml
recipes/Qwen2.5-1.5B-Instruct/sft_aha_1b5_7b_filterscore/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__same_oneindex_oai.yaml
recipes/Qwen2.5-1.5B-Instruct/sft_aha_1b5_7b_filterscore/sft_train_full_24k_dc38a75a4c94f2002004ac9c217d4396_oai.yaml
recipes/Qwen2.5-1.5B-Instruct/sft_aha_1b5_7b_filterscore/sft_train_full_24k_dc38_feedback_content2085_oai_24k1.yaml
recipes/Qwen2.5-1.5B-Instruct/sft_aha_1b5_7b_filterscore/sft_train_full_24k_dc38_feedback_content2085_oai_24k2.yaml
recipes/Qwen2.5-1.5B-Instruct/sft_aha_1b5_7b_filterscore/sft_train_full_24k_dc38_feedback_content2085_oai_24k3.yaml
recipes/Qwen2.5-1.5B-Instruct/sft_aha_1b5_7b_filterscore/sft_train_full_24k_dc38_feedback_content2085_oai.yaml
)


for config in "${config_files[@]}"; do

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
    --per_device_train_batch_size 64 \
    --config "$config" \
     2>&1 | tee "zero3_sft_${log_name}.log"
  
  echo "Finished running $config"
  echo "----------------------------------------"

  sleep 5 
done







