#!/bin/bash

# List of dataset names (all with consistent data_dir/ prefix)
dataset_name_list=(
    "data_dir/ablation_dir/reduce_sft_train_full_24k_dc38a75a4c94f2002004ac9c217d4396_oai_5kall.jsonl"
    "data_dir/ablation_dir/reduce_sft_train_full_24k_dc38a75a4c94f2002004ac9c217d4396_oai_15kall.jsonl"
    "data_dir/ablation_dir/reduce_sft_train_full_24k_dc38a75a4c94f2002004ac9c217d4396_oai_10kall.jsonl"
    "data_dir/ablation_dir/reduce_sft_train_full_24k_dc38a75a4c94f2002004ac9c217d4396_oai_filtered_exclude_5k.jsonl"
    "data_dir/ablation_dir/reduce_sft_train_full_24k_dc38a75a4c94f2002004ac9c217d4396_oai_filtered_include_10k.jsonl"
    "data_dir/ablation_dir/reduce_sft_train_full_24k_dc38a75a4c94f2002004ac9c217d4396_oai_filtered_exclude_review_10k.jsonl"
    "data_dir/ablation_dir/reduce_sft_train_full_24k_dc38a75a4c94f2002004ac9c217d4396_oai_filtered_include_5k.jsonl"
    "data_dir/ablation_dir/reduce_sft_train_full_24k_dc38a75a4c94f2002004ac9c217d4396_oai_filtered_exclude_review_5k.jsonl"
)

# Template YAML file
template_file="sft_feedmixdirect_qw25b7_24k.yaml"

# Process each dataset
for dataset in "${dataset_name_list[@]}"; do
    # Extract basename without extension for creating output paths
    dataset_basename=$(basename "$dataset" .jsonl)
    
    # Create output directory path
    output_dir="ablation_dir/code_sft_qw25b15_${dataset_basename}"
    
    # Create new YAML filename
    new_yaml_file="qw25b15_${dataset_basename}.yaml"
    
    # Copy template and modify it
    cp "$template_file" "$new_yaml_file"
    
    # Replace dataset_name (no need to add data_dir/ since it's already in the path)
    sed -i "s|dataset_name:.*|dataset_name: $dataset|" "$new_yaml_file"
    
    # Replace output_dir (but not overwrite_output_dir)
    sed -i "s|^output_dir:.*|output_dir: $output_dir|" "$new_yaml_file"
    
    echo "Created: $new_yaml_file"
    echo "  dataset_name: $dataset"
    echo "  output_dir: $output_dir"
    echo ""
done

echo "Processing complete!"

