#!/bin/bash

# Comprehensive model processing script with configurable parameters
# Usage: ./run.sh <model_list_file> [options]
# Example: ./run.sh models.txt --temp 0.8 --bs 32 --n_samples 10

#set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Default configuration
DEFAULT_BENCHMARK_THRESHOLD=5960
DEFAULT_SAVE_DIR="save_dir"
DEFAULT_TEMPERATURE=0.2
DEFAULT_BATCH_SIZE=20
DEFAULT_N_SAMPLES=20
DEFAULT_TP=""  # Will auto-detect GPUs if not specified
DEFAULT_BACKEND="vllm"
DEFAULT_PROMPT_TYPE="think_answer"

# Remote server configuration
REMOTE_USER="wjd_cuda122"
REMOTE_HOST="10.0.104.97"
REMOTE_PORT=8870
REMOTE_BASE_PATH="/home/wjd_cuda122/wj_code/dl_loop/open-r1/"

# SSH key configuration
SSH_KEY_PATH="./id_rsa"
SSH_PUB_KEY_PATH="./id_rsa.pub"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Initialize variables with defaults
BENCHMARK_THRESHOLD="$DEFAULT_BENCHMARK_THRESHOLD"
SAVE_DIR="$DEFAULT_SAVE_DIR"
TEMPERATURE="$DEFAULT_TEMPERATURE"
BATCH_SIZE="$DEFAULT_BATCH_SIZE"
N_SAMPLES="$DEFAULT_N_SAMPLES"
TP="$DEFAULT_TP"
BACKEND="$DEFAULT_BACKEND"
PROMPT_TYPE="$DEFAULT_PROMPT_TYPE"
MODEL_LIST_FILE=""
RESUME="--resume"  # Default to resume mode

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 <model_list_file_or_model_name> [options]

Required:
  <model_list_file_or_model_name>   File containing list of models OR single model name

Options:
  --temp, --temperature FLOAT    Temperature for sampling (default: $DEFAULT_TEMPERATURE)
  --bs, --batch-size INT         Batch size (default: $DEFAULT_BATCH_SIZE)
  --n-samples INT                Number of samples (default: $DEFAULT_N_SAMPLES)
  --tp INT                       Tensor parallelism (default: auto-detect GPUs)
  --backend STRING               Backend to use (default: $DEFAULT_BACKEND)
  --prompt-type STRING           Prompt type (default: $DEFAULT_PROMPT_TYPE)
  --threshold INT                Benchmark threshold (default: $DEFAULT_BENCHMARK_THRESHOLD)
  --save-dir STRING              Save directory (default: $DEFAULT_SAVE_DIR)
  --no-resume                    Disable resume mode
  --help, -h                     Show this help message

Examples:
  # Process single model
  $0 mmmmat --temp 0.8 --bs 32
  $0 microsoft/DialoGPT-medium --temperature 0.5
  
  # Process models from file
  $0 models.txt --temp 0.8 --bs 32
  $0 models.txt --temperature 0.5 --n-samples 50 --tp 4
  $0 models.txt --temp 0.8 --prompt-type answer_only --no-resume

EOF
}

# Logging function
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to parse command line arguments
parse_arguments() {
    if [[ $# -eq 0 ]]; then
        show_usage
        exit 1
    fi

    # First argument should be the model list file
    MODEL_LIST_FILE="$1"
    shift

    # Parse remaining arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --temp|--temperature)
                if [[ -z "${2:-}" ]]; then
                    log "${RED}Error: --temperature requires a value${NC}"
                    exit 1
                fi
                TEMPERATURE="$2"
                shift 2
                ;;
            --bs|--batch-size)
                if [[ -z "${2:-}" ]]; then
                    log "${RED}Error: --batch-size requires a value${NC}"
                    exit 1
                fi
                BATCH_SIZE="$2"
                shift 2
                ;;
            --n-samples)
                if [[ -z "${2:-}" ]]; then
                    log "${RED}Error: --n-samples requires a value${NC}"
                    exit 1
                fi
                N_SAMPLES="$2"
                shift 2
                ;;
            --tp)
                if [[ -z "${2:-}" ]]; then
                    log "${RED}Error: --tp requires a value${NC}"
                    exit 1
                fi
                TP="$2"
                shift 2
                ;;
            --backend)
                if [[ -z "${2:-}" ]]; then
                    log "${RED}Error: --backend requires a value${NC}"
                    exit 1
                fi
                BACKEND="$2"
                shift 2
                ;;
            --prompt-type)
                if [[ -z "${2:-}" ]]; then
                    log "${RED}Error: --prompt-type requires a value${NC}"
                    exit 1
                fi
                PROMPT_TYPE="$2"
                shift 2
                ;;
            --threshold)
                if [[ -z "${2:-}" ]]; then
                    log "${RED}Error: --threshold requires a value${NC}"
                    exit 1
                fi
                BENCHMARK_THRESHOLD="$2"
                shift 2
                ;;
            --save-dir)
                if [[ -z "${2:-}" ]]; then
                    log "${RED}Error: --save-dir requires a value${NC}"
                    exit 1
                fi
                SAVE_DIR="$2"
                shift 2
                ;;
            --no-resume)
                RESUME=""
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                log "${RED}Error: Unknown option '$1'${NC}"
                show_usage
                exit 1
                ;;
        esac
    done

    # Validate required arguments
    if [[ -z "$MODEL_LIST_FILE" ]]; then
        log "${RED}Error: Model list file or model name is required${NC}"
        show_usage
        exit 1
    fi
}

# Function to generate benchmark template based on temperature
get_benchmark_template() {
    local temp_str
    if [[ "$TEMPERATURE" == "0.2" ]]; then
        temp_str="temp_0.2"
    else
        temp_str="temp_${TEMPERATURE}"
    fi
    echo "verified_z3_benchmarks_LaM4Inv_Linear_c_f046820b70f5d4b52fa7d6fc91989446_%s_vllm_${temp_str}_${PROMPT_TYPE}_answer.jsonl"
}

# Function to display current configuration
show_config() {
    log "${BLUE}==================== CONFIGURATION ====================${NC}"
    if [[ -f "$MODEL_LIST_FILE" ]]; then
        log "Model list file: ${GREEN}$MODEL_LIST_FILE${NC}"
    else
        log "Single model: ${GREEN}$MODEL_LIST_FILE${NC}"
    fi
    log "Temperature: ${GREEN}$TEMPERATURE${NC}"
    log "Batch size: ${GREEN}$BATCH_SIZE${NC}"
    log "Number of samples: ${GREEN}$N_SAMPLES${NC}"
    log "Tensor parallelism: ${GREEN}${TP:-auto-detect}${NC}"
    log "Backend: ${GREEN}$BACKEND${NC}"
    log "Prompt type: ${GREEN}$PROMPT_TYPE${NC}"
    log "Benchmark threshold: ${GREEN}$BENCHMARK_THRESHOLD${NC}"
    log "Save directory: ${GREEN}$SAVE_DIR${NC}"
    log "Resume mode: ${GREEN}${RESUME:-disabled}${NC}"
    log "Benchmark template: ${GREEN}$(get_benchmark_template)${NC}"
    log "${BLUE}=======================================================${NC}"
}

# Function to setup SSH key authentication
setup_ssh_key() {
    log "Setting up SSH key authentication using local key files..."
    
    # Check if local SSH key files exist
    if [ ! -f "$SSH_KEY_PATH" ] || [ ! -f "$SSH_PUB_KEY_PATH" ]; then
        log "${RED}Error: SSH key files not found in current directory${NC}"
        log "Required files: id_rsa and id_rsa.pub"
        return 1
    fi
    
    # Set correct permissions for private key
    chmod 600 "$SSH_KEY_PATH"
    chmod 644 "$SSH_PUB_KEY_PATH"
    log "SSH key files found and permissions set"
    
    # Test SSH connection without password using local key and port
    log "Testing SSH connection with local key..."
    ssh -o BatchMode=yes -o ConnectTimeout=5 -i "$SSH_KEY_PATH" -p "$REMOTE_PORT" "${REMOTE_USER}@${REMOTE_HOST}" exit 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log "${GREEN}SSH key authentication already working with local key${NC}"
        return 0
    else
        log "SSH key authentication not working. Setting up..."
        
        # Copy SSH key to remote server
        log "Copying local SSH public key to remote server..."
        log "You will be prompted for the remote server password this one time:"
        
        ssh-copy-id -i "$SSH_PUB_KEY_PATH" -p "$REMOTE_PORT" "${REMOTE_USER}@${REMOTE_HOST}"
        
        if [ $? -eq 0 ]; then
            log "${GREEN}SSH key successfully copied to remote server${NC}"
            
            # Test again with local key
            ssh -o BatchMode=yes -o ConnectTimeout=5 -i "$SSH_KEY_PATH" -p "$REMOTE_PORT" "${REMOTE_USER}@${REMOTE_HOST}" exit 2>/dev/null
            if [ $? -eq 0 ]; then
                log "${GREEN}SSH key authentication now working with local key${NC}"
                return 0
            else
                log "${RED}Error: SSH key authentication still not working${NC}"
                return 1
            fi
        else
            log "${RED}Error: Failed to copy SSH key to remote server${NC}"
            return 1
        fi
    fi
}

# Function to sync model from remote if not exists locally
sync_model_if_needed() {
    local path_name="$1"
    local local_root_dir="$2"
    
    if [ ! -d "${local_root_dir}/${path_name}" ]; then
        mkdir -p "${local_root_dir}/${path_name}" 
        log "Local folder '${local_root_dir}/${path_name}' does not exist. Syncing from remote..."
        
        # Rsync from remote to local using local SSH key and port
        rsync -avz --progress -e "ssh -o BatchMode=yes -i ${SSH_KEY_PATH} -p ${REMOTE_PORT}" --exclude "checkpoint-*" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_BASE_PATH}/${path_name}/" "${local_root_dir}/${path_name}/"
        
        if [ $? -eq 0 ]; then
            log "${GREEN}Successfully synced '$path_name' from remote${NC}"
            return 0
        else
            log "${RED}Error: Failed to sync '$path_name' from remote${NC}"
            return 1
        fi
    else
        log "Local folder '${local_root_dir}/${path_name}' already exists. Skipping rsync."
        return 0
    fi
}

# Function to run VLLM task
run_vllm_task() {
    local name="$1"
    local model_root="$2"
    
    log "Running VLLM task for '$name' with temperature $TEMPERATURE..."
    
    # Validate model_root exists
    if [ ! -d "$model_root" ]; then
        log "${RED}Error: Model root directory '$model_root' does not exist.${NC}"
        return 1
    fi

    # Determine number of GPUs to use
    local num_gpus
    if [[ -n "$TP" ]]; then
        num_gpus="$TP"
        log "Using specified tensor parallelism: $num_gpus"
    else
        # Auto-detect available GPUs
        CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-$(nvidia-smi --query-gpu=index --format=csv,noheader | paste -sd ",")}
        IFS=',' read -ra GPU_LIST <<< "$CUDA_VISIBLE_DEVICES"
        num_gpus=${#GPU_LIST[@]}
        log "Auto-detected NUM_GPUS: $num_gpus"
    fi

    # Validate input file exists
    input_file="data_dir/verified_z3_benchmarks_LaM4Inv_Linear_c_f046820b70f5d4b52fa7d6fc91989446.jsonl"
    if [ ! -f "$input_file" ]; then
        log "${RED}Error: Input file '$input_file' not found.${NC}"
        return 1
    fi

    # Create save directory if it doesn't exist
    mkdir -p "$SAVE_DIR"

    # Build the command arguments
    local cmd_args=(
        "$name"
        "$input_file"
        "$SAVE_DIR"
        --model_root "$model_root"
        --tp "$num_gpus"
        --bs "$BATCH_SIZE"
        --n_samples "$N_SAMPLES"
        --temperature "$TEMPERATURE"
        --backend "$BACKEND"
        --prompt_type "$PROMPT_TYPE"
    )

    # Add resume flag if enabled
    if [[ -n "$RESUME" ]]; then
        cmd_args+=("$RESUME")
    fi

    # Log the command being executed
    log "Executing: python collect_chat.py ${cmd_args[*]}"

    # Run the Python script
    python collect_chat.py "${cmd_args[@]}"

    # Check if Python script succeeded
    if [ $? -ne 0 ]; then
        log "${RED}Error: Python script execution failed.${NC}"
        return 1
    fi

    log "${GREEN}VLLM task completed successfully.${NC}"
    return 0
}

# Function to cleanup local model directory
cleanup_local_model() {
    local path_name="$1"
    local local_root_dir="$2"
    
    log "Cleaning up: Deleting local folder '${local_root_dir}/${path_name}'..."
    if [ -d "${local_root_dir}/${path_name}" ]; then
        rm -rf "${local_root_dir}/${path_name}"
        if [ $? -eq 0 ]; then
            log "${GREEN}Successfully deleted local folder '${local_root_dir}/${path_name}'${NC}"
        else
            log "${RED}Error: Failed to delete local folder '${local_root_dir}/${path_name}'${NC}"
            return 1
        fi
    else
        log "${YELLOW}Warning: Local folder '${local_root_dir}/${path_name}' not found for cleanup${NC}"
    fi
    return 0
}

# Main function to process a single model
process_model() {
    local model_name="$1"
    local local_root_dir="$2"
    local benchmark_template="$3"
    
    log "Processing model: ${GREEN}$model_name${NC}"
    
    # Generate the expected benchmark filename
    model_slug="${model_name//\//--}"  # Replace slashes with double dashes
    benchmark_file=$(printf "$SAVE_DIR/$benchmark_template" "$model_slug")
    
    log "Expected benchmark: $benchmark_file"
    
    # Check if benchmark file exists and has sufficient lines
    if [[ -f "$benchmark_file" ]]; then
        if [[ -r "$benchmark_file" ]]; then
            line_count=$(wc -l < "$benchmark_file" 2>/dev/null || echo "0")
            
            if (( line_count > BENCHMARK_THRESHOLD )); then
                log "${GREEN}✓ Benchmark complete ($line_count lines > $BENCHMARK_THRESHOLD) - skipping $model_name${NC}"
                return 0  # Skip this model
            else
                log "${YELLOW}⚠ Benchmark incomplete ($line_count lines ≤ $BENCHMARK_THRESHOLD) - reprocessing $model_name${NC}"
            fi
        else
            log "${YELLOW}⚠ Benchmark file exists but not readable - reprocessing $model_name${NC}"
        fi
    else
        log "${RED}✗ Benchmark missing - processing $model_name${NC}"
    fi
    
    # Step 1: Sync model from remote if needed
    if ! sync_model_if_needed "$model_name" "$local_root_dir"; then
        return 1
    fi
    
    # Step 2: Run VLLM task
    if ! run_vllm_task "$model_name" "$local_root_dir"; then
        return 1
    fi
    
    # Step 3: Cleanup local model directory
    if ! cleanup_local_model "$model_name" "$local_root_dir"; then
        return 1
    fi
    
    # Verify the benchmark was created successfully
    if [[ -f "$benchmark_file" ]]; then
        final_line_count=$(wc -l < "$benchmark_file" 2>/dev/null || echo "0")
        log "Final benchmark line count: $final_line_count"
    fi
    
    log "${GREEN}✓ Successfully processed $model_name${NC}"
    return 0
}

# Main script execution starts here
main() {
    # Parse command line arguments
    parse_arguments "$@"

    # Show current configuration
    show_config

    # Check if input is a file or a single model name
    if [[ -f "$MODEL_LIST_FILE" ]]; then
        # Check if file is readable
        if [[ ! -r "$MODEL_LIST_FILE" ]]; then
            log "${RED}Error: File '$MODEL_LIST_FILE' is not readable!${NC}" >&2
            exit 1
        fi
        PROCESS_AS_FILE=true
        log "Processing models from file: $MODEL_LIST_FILE"
    else
        # Treat as single model name
        PROCESS_AS_FILE=false
        log "Processing single model: $MODEL_LIST_FILE"
    fi

    # Get local root directory
    if [ ! -f "where_is_root_dir.txt" ]; then
        log "${RED}Error: where_is_root_dir.txt not found!${NC}"
        exit 1
    fi
    
    local_root_dir=$(cat where_is_root_dir.txt)
    mkdir -p "$local_root_dir"

    # Create save directory if it doesn't exist
    mkdir -p "$SAVE_DIR"

    # Get benchmark template based on current temperature
    benchmark_template=$(get_benchmark_template)

    # Setup SSH key authentication once at the beginning
    if ! setup_ssh_key; then
        log "${RED}Error: Failed to setup SSH key authentication${NC}"
        exit 1
    fi

    # Counters for statistics
    total_models=0
    skipped_models=0
    processed_models=0
    failed_models=0

    log "Starting model processing..."
    log "Local root directory: $local_root_dir"

    # Process models based on input type
    while IFS= read -r model_name || [[ -n "$model_name" ]]; do
        # Skip empty lines and comments
        [[ -z "$model_name" ]] && continue
        [[ "$model_name" =~ ^[[:space:]]*# ]] && continue
        
        # Trim whitespace
        model_name=$(echo "$model_name" | xargs)
        [[ -z "$model_name" ]] && continue
        
        ((total_models++))
        
        if process_model "$model_name" "$local_root_dir" "$benchmark_template"; then
            if [[ -f "$SAVE_DIR/$(printf "$benchmark_template" "${model_name//\//--}")" ]]; then
                line_count=$(wc -l < "$SAVE_DIR/$(printf "$benchmark_template" "${model_name//\//--}")" 2>/dev/null || echo "0")
                if (( line_count > BENCHMARK_THRESHOLD )); then
                    ((processed_models++))
                else
                    ((skipped_models++))
                fi
            else
                ((processed_models++))
            fi
        else
            log "${RED}✗ Error: Failed to process $model_name${NC}" >&2
            ((failed_models++))
            # Continue processing other models instead of failing completely
        fi
        
        log "---"
        
    done < "$MODEL_LIST_FILE"


    # Final statistics
    log "${BLUE}==================== SUMMARY ====================${NC}"
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
}

# Run main function with all arguments
main "$@"

