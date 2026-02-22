#!/bin/bash

#set -euo pipefail

# Check if input file is provided
if [[ -z "${1:-}" ]]; then
    echo "Usage: $0 <model_list_file>"
    exit 1
fi

mpath="$1"

# Check if file exists
if [[ ! -f "$mpath" ]]; then
    echo "Error: File '$mpath' not found!"
    exit 1
fi


while IFS= read -r i || [[ -n $i ]]; do
    [[ -z $i ]] && continue

    echo "Preparing model: $i"

    # 1. Protect the list file from being read inside prepare_model.sh
    if ! bash prepare_model.sh "$i" < /dev/null; then
        echo "prepare_model.sh failed for $i (rc=$?), continuing…" >&2
    fi
done < "$mpath"



echo "All models processed successfully!"

