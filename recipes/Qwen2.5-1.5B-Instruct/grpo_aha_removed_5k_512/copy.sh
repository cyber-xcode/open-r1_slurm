#!/bin/bash

# List of model paths
models=(
    "save_ahacorrect_4096_dir/major_voted_dk_asssim2580_2k5_oai"
    "save_ahacorrect_4096_dir/major_voted_dk_asssim2580_conten2580_oai"
    "save_ahacorrect_4096_dir/major_voted_dk_asssim2580_oai"
    "save_ahacorrect_4096_dir/xsft_traindeepseek_formated_one_idx_b39f1c0f45b5eaf7ae970d6a06d8908c_1b5"
    "save_ahacorrect_4096_dir/xsft_train_formated_one_idx_1573d0418d6823bfc5056ee477dca2a0_1b5"
    "save_ahacorrect_4096_dir/xsft_traindeepseek_formated_3d2d45bd870235ca7bf69b94de6a334e_1b5"
    "save_ahacorrect_4096_dir/xsft_train_formated_0ef9f335cf4c6d77625f2e2a780c8054_1b5"
)

# Template YAML file (assuming sft40_5k3.yaml exists)
template_file="sft40_5k3.yaml"

# Process each model
for model_path in "${models[@]}"; do
    # Extract the part after the last slash for creating output paths
    model_basename=$(basename "$model_path")
    
    # Create output directory path by replacing slashes with underscores
    output_dir_suffix=$(echo "$model_path" | sed 's/\//__/g')
    output_dir="data_removed/grpo_${output_dir_suffix}"
    
    # Create new YAML filename
    new_yaml_file="grpo_grpo_${output_dir_suffix}.yaml"
    
    # Copy template and modify it
    cp "$template_file" "$new_yaml_file"
    
    # Replace model_name_or_path
    sed -i "s|model_name_or_path:.*|model_name_or_path: $model_path|" "$new_yaml_file"
    
    # Replace output_dir (but not overwrite_output_dir)
    sed -i "s|^output_dir:.*|output_dir: $output_dir|" "$new_yaml_file"
    
    echo "Created: $new_yaml_file"
    echo "  model_name_or_path: $model_path"
    echo "  output_dir: $output_dir"
    echo ""
done

echo "Processing complete!"

