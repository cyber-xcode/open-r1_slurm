export CUDA_HOME="/opt/apps/software/CUDA/12.6.0/"
export PYTHONPATH="./src"
export CUDA_VISIBLE_DEVICES=0,1,2,3
export NCCL_DEBUG="INFO"


shuffled_configs=(
	recipes_paper/reduce_rq4/grpo_reduce5k_full.yaml
)


for config in "${shuffled_configs[@]}"; do
    echo "Processing config: $config"
    log_name=$(basename "$config" .yaml)

        sleep 6 

        PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
        accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
                 --num_processes 4 \
                --main_process_port $PORT \
                          src/open_r1/grpo.py \
                --config $config \
                    --vllm_mode "colocate" --vllm_tensor_parallel_size 4 --vllm_gpu_memory_utilization 0.3 \
            --per_device_train_batch_size 8 2>&1 | tee   "grpo_${log_name}.log"


        sleep 50
done



