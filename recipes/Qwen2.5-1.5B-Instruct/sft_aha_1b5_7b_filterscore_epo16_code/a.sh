#!/bin/bash

# Script to modify YAML files:
# 1. Replace num_train_epochs: 36 with num_train_epochs: 16
# 2. Add "_epo16" to output_dir paths

for file in *.yaml; do
    if [ -f "$file" ]; then
        echo "Processing: $file"
        
        # Create a backup
        cp "$file" "${file}.bak"
        
        # Use sed to make both modifications
        sed -i \
            -e 's/num_train_epochs: 36/num_train_epochs: 16/g' \
            -e 's|\(output_dir: save_ahacorrect_4096_dir/[^[:space:]]*\)|\1_epo16|g' \
            "$file"
        
        echo "Modified: $file (backup: ${file}.bak)"
    fi
done

echo "All files processed!"

