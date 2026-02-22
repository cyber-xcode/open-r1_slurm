
#CUDA_VISIBLE_DEVICES=0

name=$1
#"data_h200/grpo_sftl40s_q15b_prompt_type3"
model_root="../open-r1_formal"



CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-$(nvidia-smi --query-gpu=index --format=csv,noheader | paste -sd ",")}
IFS=',' read -ra GPU_LIST <<< "$CUDA_VISIBLE_DEVICES"
NUM_GPUS=${#GPU_LIST[@]}



echo "total NUM_GPUS=="$NUM_GPUS


python collect_chat.py \
        $name   \
        data_dir/verified_z3_benchmarks_LaM4Inv_Linear_c_f046820b70f5d4b52fa7d6fc91989446.jsonl \
        ./save_dir/  \
        --model_root $model_root --tp $NUM_GPUS \
         --bs 20  --n_samples 20 --temperature 0.8   --resume --backend vllm   --prompt_type think_answer  



python collect_chat.py \
        $name   \
        data_dir/verified_z3_benchmarks_LaM4Inv_Linear_c_f046820b70f5d4b52fa7d6fc91989446.jsonl \
        ./save_dir/  \
        --model_root $model_root --tp $NUM_GPUS \
         --bs 20  --n_samples 20 --temperature 0.2   --resume --backend vllm   --prompt_type think_answer  




python collect_chat.py \
        $name   \
        data_dir/verified_z3_benchmarks_LaM4Inv_Linear_c_f046820b70f5d4b52fa7d6fc91989446.jsonl \
        ./save_dir/  \
	--model_root $model_root  --tp $NUM_GPUS \
        --greedy --resume --backend vllm   --prompt_type think_answer  

