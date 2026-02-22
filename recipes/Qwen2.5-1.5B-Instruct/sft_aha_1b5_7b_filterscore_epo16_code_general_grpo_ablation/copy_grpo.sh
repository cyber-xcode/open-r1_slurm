#!/bin/bash

# List of dataset names for train section
dataset_name_list=(
    "data_dir/c_train_smt_benchmark_as_ref_valid_train_decontaminated_4a5bd042d9d9fc58dfeffc34f68d3307_1000.jsonl"
    "data_dir/c_train_smt_benchmark_as_ref_valid_train_decontaminated_4a5bd042d9d9fc58dfeffc34f68d3307_3000.jsonl"
    "data_dir/c_train_smt_benchmark_as_ref_valid_train_decontaminated_4a5bd042d9d9fc58dfeffc34f68d3307_5000.jsonl"
    "data_dir/c_train_smt_benchmark_as_ref_valid_train_decontaminated_4a5bd042d9d9fc58dfeffc34f68d3307_500.jsonl"
    "data_dir/c_train_smt_benchmark_as_ref_valid_train_decontaminated_4a5bd042d9d9fc58dfeffc34f68d3307_5k.jsonl"
    "data_dir/c_train_smt_benchmark_as_ref_valid_train_decontaminated_4a5bd042d9d9fc58dfeffc34f68d3307.jsonl"
)

# Template YAML file
template_file="makeup001_grpocode_sft40_5k1_onlyz3_format.yaml"

# Process each dataset
for dataset in "${dataset_name_list[@]}"; do
    # Extract the suffix after the long hash (1000, 3000, 5000, etc.)
    if [[ "$dataset" =~ _4a5bd042d9d9fc58dfeffc34f68d3307_([^.]+)\.jsonl$ ]]; then
        dataset_suffix="${BASH_REMATCH[1]}"
    elif [[ "$dataset" =~ _4a5bd042d9d9fc58dfeffc34f68d3307\.jsonl$ ]]; then
        # For the file without suffix
        dataset_suffix="base"
    else
        # Fallback: use last part of basename
        dataset_suffix=$(basename "$dataset" .jsonl | sed 's/.*_//')
    fi
    
    # Create output directory path with the expected format
    output_dir="ablation_dir/grpo_qw25b15_3307_${dataset_suffix}_onlyz3format"
    
    # Create new YAML filename  
    new_yaml_file="makeup_grpo_3307_${dataset_suffix}.yaml"
    
    # Copy template and modify it
    cp "$template_file" "$new_yaml_file"
    
    # Replace the train dataset line specifically (with proper indentation)
    sed -i "s|  train: .*|  train: $dataset|" "$new_yaml_file"
    
    # Replace the specific pattern in output_dir
    # Original: save_ahacorrect_4096_dir/makeup_code_sft_train_full_24k_dc38a75a4c94f2002004ac9c217d4396_oai_epo16_grpo_4a5bd_5k_onlyz3format
    # Target:   ablation_dir/grpo_qw25b15_3307_1000_onlyz3format
    sed -i "s|makeup_code_sft_train_full_24k_dc38a75a4c94f2002004ac9c217d4396_oai_epo16_grpo_4a5bd_5k_onlyz3format|grpo_qw25b15_3307_${dataset_suffix}_onlyz3format|" "$new_yaml_file"
    
    echo "Processing: $dataset"
    echo "Extracted suffix: $dataset_suffix"
    echo "Created: $new_yaml_file"
    echo "  train dataset: $dataset"
    echo "  output_dir: $output_dir"
    echo ""
done

echo "Processing complete!"

