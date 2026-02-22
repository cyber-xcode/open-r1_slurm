#!/usr/bin/env python3
"""
JSONL file cleaner for temperature-based sampling files.
Ensures each unique task_id has at most 20 samples for files with temp_0.8 or temp_0.2 in filename.
"""

import json
import argparse
import os
import sys
from collections import defaultdict, Counter
from typing import Dict, List, Tuple


def load_jsonl(filepath: str) -> List[dict]:
    """Load JSONL file and return list of dictionaries."""
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON on line {line_num}: {e}")
                    continue
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{filepath}': {e}")
        sys.exit(1)
    
    return data


def save_jsonl(data: List[dict], filepath: str) -> None:
    """Save data to JSONL file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"Error writing file '{filepath}': {e}")
        sys.exit(1)


def analyze_task_ids(data: List[dict]) -> Tuple[Counter, Dict[str, List[int]]]:
    """Analyze task_id distribution and return counts and indices."""
    task_id_counts = Counter()
    task_id_indices = defaultdict(list)
    
    for idx, item in enumerate(data):
        task_id = item.get('task_id', 'MISSING_TASK_ID')
        task_id_counts[task_id] += 1
        task_id_indices[task_id].append(idx)
    
    return task_id_counts, task_id_indices


def should_process_file(filename: str) -> bool:
    """Check if file should be processed based on filename patterns."""
    return "temp_0.8" in filename or "temp_0.2" in filename


def clean_data(data: List[dict], task_id_indices: Dict[str, List[int]], max_samples: int = 20) -> List[dict]:
    """Clean data by keeping only first max_samples for each task_id."""
    indices_to_keep = set()
    
    for task_id, indices in task_id_indices.items():
        # Keep only first max_samples indices for each task_id
        indices_to_keep.update(indices[:max_samples])
    
    # Return filtered data maintaining original order
    return [data[i] for i in sorted(indices_to_keep)]


def main():
    parser = argparse.ArgumentParser(
        description="Clean JSONL files with temperature-based sampling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python jsonl_cleaner.py file.jsonl                    # Check and warn only
  python jsonl_cleaner.py file.jsonl --force           # Clean in-place
  python jsonl_cleaner.py file.jsonl --max-samples 15  # Custom limit
        """
    )
    
    parser.add_argument('filepath', help='Path to JSONL file to process')
    parser.add_argument('--force', action='store_true', 
                       help='Force clean the file in-place (remove extra samples)')
    parser.add_argument('--max-samples', type=int, default=20,
                       help='Maximum samples per task_id (default: 20)')
    parser.add_argument('--backup', action='store_true',
                       help='Create backup before cleaning (adds .backup extension)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.filepath):
        print(f"Error: File '{args.filepath}' does not exist.")
        sys.exit(1)
    
    filename = os.path.basename(args.filepath)
    
    # Check if file should be processed
    if not should_process_file(filename):
        print(f"⚠️  WARNING: {filename} does not contain 'temp_0.8' or 'temp_0.2'")
        return
    
    # Load data
    data = load_jsonl(args.filepath)
    
    # Analyze task_ids
    task_id_counts, task_id_indices = analyze_task_ids(data)
    
    # Check for issues
    exceeded_task_ids = {task_id: count for task_id, count in task_id_counts.items() 
                        if count > args.max_samples}
    non_exact_task_ids = {task_id: count for task_id, count in task_id_counts.items() 
                         if count != args.max_samples}
    
    # Warning 1: Any task_id exceeded the limit
    if exceeded_task_ids:
        print(f"⚠️  WARNING: {args.filepath} has task_ids exceeding {args.max_samples} samples")
    
    # Warning 3: Any task_id count not equal to expected (for matching pattern files)
    elif non_exact_task_ids:
        print(f"⚠️  WARNING: {args.filepath} task_ids with sample counts != {args.max_samples}")
    
    # If no exceeded task_ids, no cleaning needed
    if not exceeded_task_ids:
        return
    
    if not args.force:
        return
    
    # Create backup if requested
    if args.backup:
        backup_path = args.filepath + '.backup'
        try:
            import shutil
            shutil.copy2(args.filepath, backup_path)
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")
    
    # Clean data
    cleaned_data = clean_data(data, task_id_indices, args.max_samples)
    
    # Save cleaned data
    save_jsonl(cleaned_data, args.filepath)


if __name__ == "__main__":
    main()



