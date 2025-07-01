#!/bin/bash

# Get list of JSONL files and store in array
#mapfile -t jsonl_files < <(find data_dir/aha_dir/ -name '*jsonl' | sort)

jsonl_files=(
data_dir/sft_train_full_24k_dc38a75a4c94f2002004ac9c217d4396_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__assert100.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__assert100_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__assert100_oneindex_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__assert_lt20.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__assert_lt20_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__assert_lt20_oneindex_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__assert_null_or_zero.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__assert_null_or_zero_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__assert_null_or_zero_oneindex_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__content100.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__content100_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__content100_oneindex_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__content2085_assert2085.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__content2085_assert2085_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__content2085_assert2085_oneindex_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__contentgt85_assertgt85.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__contentgt85_assertgt85_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__contentgt85_assertgt85_oneindex_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__content_lt20.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__content_lt20_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__content_lt20_oneindex_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__content_null_or_zero.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__content_null_or_zero_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__content_null_or_zero_oneindex_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__null.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__null_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__null_oneindex_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__same.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__same_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__same_oneindex_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__unk.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__unk_oai.jsonl
data_dir/aha_dir/sft_train_formated_dk_phi4_qwen3_v2_processed_scored_qwen25b7__unk_oneindex_oai.jsonl
)

# Template YAML file
template_file="major_voted_dk_asssim2580_conten2580_oai.yaml"

# Check if template file exists
if [ ! -f "$template_file" ]; then
    echo "Error: Template file '$template_file' not found!"
    exit 1
fi

echo "Found ${#jsonl_files[@]} JSONL files in data_dir/aha_dir/"
echo "Processing files..."
echo ""

# Process each JSONL file
for jsonl_file in "${jsonl_files[@]}"; do
    # Extract the base filename without path and extension
    model_basename=$(basename "$jsonl_file" .jsonl)
    
    # Create output directory path
    output_dir="save_ahacorrect_4096_dir/$model_basename"
    
    # Create new YAML filename
    new_yaml_file="${model_basename}.yaml"
    
    # Copy template and modify it
    cp "$template_file" "$new_yaml_file"
    
    # Replace dataset_name
    sed -i "s|dataset_name:.*|dataset_name: $jsonl_file|" "$new_yaml_file"
    
    # Replace output_dir (but not overwrite_output_dir)
    sed -i "s|^output_dir:.*|output_dir: $output_dir|" "$new_yaml_file"
    
    echo "Created: $new_yaml_file"
    echo "  dataset_name: $jsonl_file"
    echo "  output_dir: $output_dir"
    echo ""
done

echo "Processing complete!"
echo "Generated ${#jsonl_files[@]} new YAML files."

