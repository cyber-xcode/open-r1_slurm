#!/bin/bash

# Check if path_name argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <path_name>"
    echo "Example: $0 my_folder"
    exit 1
fi

path_name="$1"

# Configuration - Update these variables according to your setup
REMOTE_USER="wjd_cuda122"
REMOTE_HOST="10.0.104.97"
REMOTE_PORT=8870
REMOTE_BASE_PATH="/home/wjd_cuda122/wj_code/dl_loop/open-r1/"
LOCAL_ROOT_DIR=$(cat where_is_root_dir.txt)

mkdir -p "$LOCAL_ROOT_DIR"

# SSH key configuration - using local files
SSH_KEY_PATH="./id_rsa"
SSH_PUB_KEY_PATH="./id_rsa.pub"

echo "Processing folder: $path_name"

# Function to setup SSH key authentication
setup_ssh_key() {
    echo "Setting up SSH key authentication using local key files..."
    
    # Check if local SSH key files exist
    if [ ! -f "$SSH_KEY_PATH" ] || [ ! -f "$SSH_PUB_KEY_PATH" ]; then
        echo "Error: SSH key files not found in current directory"
        echo "Required files: id_rsa and id_rsa.pub"
        return 1
    fi
    
    # Set correct permissions for private key
    chmod 600 "$SSH_KEY_PATH"
    chmod 644 "$SSH_PUB_KEY_PATH"
    echo "SSH key files found and permissions set"
    
    # Test SSH connection without password using local key and port
    echo "Testing SSH connection with local key..."
    ssh -o BatchMode=yes -o ConnectTimeout=5 -i "$SSH_KEY_PATH" -p "$REMOTE_PORT" "${REMOTE_USER}@${REMOTE_HOST}" exit 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "SSH key authentication already working with local key"
        return 0
    else
        echo "SSH key authentication not working. Setting up..."
        
        # Copy SSH key to remote server
        echo "Copying local SSH public key to remote server..."
        echo "You will be prompted for the remote server password this one time:"
        
        ssh-copy-id -i "$SSH_PUB_KEY_PATH" -p "$REMOTE_PORT" "${REMOTE_USER}@${REMOTE_HOST}"
        
        if [ $? -eq 0 ]; then
            echo "SSH key successfully copied to remote server"
            
            # Test again with local key
            ssh -o BatchMode=yes -o ConnectTimeout=5 -i "$SSH_KEY_PATH" -p "$REMOTE_PORT" "${REMOTE_USER}@${REMOTE_HOST}" exit 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "SSH key authentication now working with local key"
                return 0
            else
                echo "Error: SSH key authentication still not working"
                return 1
            fi
        else
            echo "Error: Failed to copy SSH key to remote server"
            return 1
        fi
    fi
}

# Setup SSH key authentication
setup_ssh_key
if [ $? -ne 0 ]; then
    echo "Error: Failed to setup SSH key authentication"
    exit 1
fi

# Step 1: Check if local path exists, if not rsync from remote
if [ ! -d "${LOCAL_ROOT_DIR}/${path_name}" ]; then
    mkdir -p "${LOCAL_ROOT_DIR}/${path_name}" 
    echo "Local folder '${LOCAL_ROOT_DIR}/${path_name}' does not exist. Syncing from remote..."
    
    # Rsync from remote to local using local SSH key and port
    rsync -avz --progress -e "ssh -o BatchMode=yes -i ${SSH_KEY_PATH} -p ${REMOTE_PORT}" --exclude "checkpoint-*" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_BASE_PATH}/${path_name}/" "${LOCAL_ROOT_DIR}/${path_name}/"
    
    if [ $? -eq 0 ]; then
        echo "Successfully synced '$path_name' from remote"
    else
        echo "Error: Failed to sync '$path_name' from remote"
        exit 1
    fi
else
    echo "Local folder '${LOCAL_ROOT_DIR}/${path_name}' already exists. Skipping rsync."
fi

# Step 2: Run the task script
echo "Running task script for '$path_name'..."
if [ -f "vllm_msg_tmp.sh" ]; then
    bash vllm_msg_tmp.sh "$path_name"
    task_exit_code=$?
    
    if [ $task_exit_code -eq 0 ]; then
        echo "Task script completed successfully"
    else
        echo "Warning: Task script exited with code $task_exit_code"
    fi
else
    echo "Error: vllm_msg_tmp.sh not found in current directory"
    exit 1
fi

# Step 3: Delete the local folder
echo "Cleaning up: Deleting local folder '${LOCAL_ROOT_DIR}/${path_name}'..."
if [ -d "${LOCAL_ROOT_DIR}/${path_name}" ]; then
    rm -rf "${LOCAL_ROOT_DIR}/${path_name}"
    if [ $? -eq 0 ]; then
        echo "Successfully deleted local folder '${LOCAL_ROOT_DIR}/${path_name}'"
    else
        echo "Error: Failed to delete local folder '${LOCAL_ROOT_DIR}/${path_name}'"
        exit 1
    fi
else
    echo "Warning: Local folder '${LOCAL_ROOT_DIR}/${path_name}' not found for cleanup"
fi

echo "Process completed for '$path_name'"

