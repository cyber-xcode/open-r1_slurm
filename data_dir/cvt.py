
import json

def split_jsonl_file(input_file, output_file_1, output_file_2):
    # Initialize two lists to hold the split data
    list_1 = []
    list_2 = []

    # Read the input JSON Lines file
    with open(input_file, 'r') as infile:
        for line in infile:
            # Parse the JSON object from each line
            data = json.loads(line)
            
            # Extract the 'idx' field and convert it to an integer
            if "test" in data["idx"]:
                continue
            idx = int(data['idx'].split('.')[0])  # Assuming 'idx' is like "123.c"
            
            # Split the data based on the 'idx' value
            if 0 <= idx <= 133:
                list_1.append(data)
            else:
                list_2.append(data)

    # Write the first list to new.jsonl
    with open(output_file_1, 'w') as outfile1:
        for item in list_1:
            outfile1.write(json.dumps(item) + '\n')

    # Write the second list to new_134.jsonl
    with open(output_file_2, 'w') as outfile2:
        for item in list_2:
            outfile2.write(json.dumps(item) + '\n')

# Example usage
input_file = 'evalset_asserty_smt.jsonl'
output_file_1 = 'evalset_asserty_smt_0to133.jsonl'
output_file_2 = 'evalset_asserty_smt_134.jsonl'

split_jsonl_file(input_file, output_file_1, output_file_2)
