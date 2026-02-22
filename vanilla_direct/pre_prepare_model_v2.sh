#!/bin/bash

# Enhanced model processing script with benchmark detection
# Usage: ./script.sh <model_list_file>

#set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
BENCHMARK_THRESHOLD=5960
SAVE_DIR="save_dir"
BENCHMARK_TEMPLATE="verified_z3_benchmarks_LaM4Inv_Linear_c_f046820b70f5d4b52fa7d6fc91989446_%s_vllm_temp_0.2_think_answer_answer.jsonl"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Check if input file is provided
if [[ -z "${1:-}" ]]; then
    echo "Usage: $0 <model_list_file>"
    echo "Example: $0 models.txt"
    exit 1
fi

model_list_file="$1"

# Check if file exists and is readable
if [[ ! -f "$model_list_file" ]]; then
    log "${RED}Error: File '$model_list_file' not found!${NC}" >&2
    exit 1
fi

if [[ ! -r "$model_list_file" ]]; then
    log "${RED}Error: File '$model_list_file' is not readable!${NC}" >&2
    exit 1
fi

# Create save directory if it doesn't exist
mkdir -p "$SAVE_DIR"

# Counters for statistics
total_models=0
skipped_models=0
processed_models=0
failed_models=0

log "Starting model processing from: $model_list_file"

# Process each model in the list
while IFS= read -r model_name || [[ -n "$model_name" ]]; do
    # Skip empty lines and comments
    [[ -z "$model_name" ]] && continue
    [[ "$model_name" =~ ^[[:space:]]*# ]] && continue
    
    # Trim whitespace
    model_name=$(echo "$model_name" | xargs)
    [[ -z "$model_name" ]] && continue
    
    ((total_models++))
    
    # Generate the expected benchmark filename
    model_slug="${model_name//\//--}"  # Replace slashes with double dashes
    benchmark_file=$(printf "$SAVE_DIR/$BENCHMARK_TEMPLATE" "$model_slug")
    
    log "Processing model: ${GREEN}$model_name${NC}"
    log "Expected benchmark: $benchmark_file"
    
    # Check if benchmark file exists and has sufficient lines
    if [[ -f "$benchmark_file" ]]; then
        if [[ -r "$benchmark_file" ]]; then
            line_count=$(wc -l < "$benchmark_file" 2>/dev/null || echo "0")
            
            if (( line_count > BENCHMARK_THRESHOLD )); then
                log "${GREEN}✓ Benchmark complete ($line_count lines > $BENCHMARK_THRESHOLD) - skipping $model_name${NC}"
                ((skipped_models++))
                continue
            else
                log "${YELLOW}⚠ Benchmark incomplete ($line_count lines ≤ $BENCHMARK_THRESHOLD) - reprocessing $model_name${NC}"
            fi
        else
            log "${YELLOW}⚠ Benchmark file exists but not readable - reprocessing $model_name${NC}"
        fi
    else
        log "${RED}✗ Benchmark missing - processing $model_name${NC}"
    fi
    
    # Run prepare_model.sh with error handling
    log "Executing: bash prepare_model.sh '$model_name'"
    
    if bash prepare_model.sh "$model_name" < /dev/null; then
        log "${GREEN}✓ Successfully processed $model_name${NC}"
        ((processed_models++))
        
        # Verify the benchmark was created successfully
        if [[ -f "$benchmark_file" ]]; then
            final_line_count=$(wc -l < "$benchmark_file" 2>/dev/null || echo "0")
            log "Final benchmark line count: $final_line_count"
        fi
    else
        exit_code=$?
        log "${RED}✗ Error: prepare_model.sh failed for $model_name (exit code: $exit_code)${NC}" >&2
        ((failed_models++))
        
        # Optionally continue processing other models instead of failing completely
        # Remove the next line if you want to stop on first failure
        continue
    fi
    
    log "---"
    
done < "$model_list_file"

# Final statistics
log "==================== SUMMARY ===================="
log "Total models in list: $total_models"
log "${GREEN}Successfully processed: $processed_models${NC}"
log "${YELLOW}Skipped (already complete): $skipped_models${NC}"
log "${RED}Failed: $failed_models${NC}"

if (( failed_models > 0 )); then
    log "${RED}Some models failed to process. Check the logs above.${NC}"
    exit 1
else
    log "${GREEN}All models processed successfully!${NC}"
fi

