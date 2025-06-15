
export PYTHONPATH="./src"

export CUDA_VISIBLE_DEVICES=0,1,2,3


export NCCL_DEBUG="INFO"



config_files=(
	"recipes/Qwen2.5-1.5B-Instruct/onlyz3_sft_grpo/sft_fromz3only.yaml"
#	"recipes/Qwen2.5-1.5B-Instruct/onlyz3_sft_grpo/sft_vanilla_1b5.yaml"
#	"recipes/Qwen2.5-1.5B-Instruct/onlyz3_sft_grpo/sft_vanilla_7b.yaml"
#	"recipes/Qwen2.5-1.5B-Instruct/onlyz3_sft_grpo/sft_vanillacoder_1b5.yaml"
#	"recipes/Qwen2.5-1.5B-Instruct/onlyz3_sft_grpo/sft_vanillacoder_7b.yaml"
)


ps -ef|grep python |grep -E "vllm|multiprocessing"|awk '{print $2}'|xargs kill -9 
sleep 15


for config in "${config_files[@]}"; do

  # Generate a random port
  PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
  
  # Extract a base name for the log file
  log_name=$(basename "$config" .yaml)
  
  echo "Running with config: $config"
  echo "Logging to: ddp_grpo_${log_name}.log"
  
  accelerate launch --config_file recipes/accelerate_configs/fsdp.yaml \
    --num_processes 4 \
    --main_process_port $PORT \
    src/open_r1/sft_raw.py \
    --config "$config" \
     2>&1 | tee "fsdp_sft_${log_name}.log"
  
  echo "Finished running $config"
  echo "----------------------------------------"

  sleep 5 
done









bash grpo_continue_v5.sh




ps -ef|grep python |grep -E "vllm|multiprocessing"|awk '{print $2}'|xargs kill -9 
sleep 15

CUDA_VISIBLE_DEVICES=3 nohup trl vllm-serve --model Qwen/Qwen2.5-1.5B-Instruct --tensor-parallel-size 1 --data-parallel-size 1 --port 8000 2>&1 >/dev/null &


sleep 60 

PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
         --num_processes 3 \
	--main_process_port $PORT \
                  src/open_r1/grpo.py \
        --config recipes/Qwen2.5-1.5B-Instruct/onlyz3_sft_grpo/grpo_fromonlyze3_thensft_removehard_esbmc_full.yaml \
    --per_device_train_batch_size 16  2>&1 | tee sft_fromz3only_continue_then_grpo_11.log



ps -ef|grep python |grep -E "vllm|multiprocessing"|awk '{print $2}'|xargs kill -9 
sleep 150 



ps -ef|grep python |grep -E "vllm|multiprocessing"|awk '{print $2}'|xargs kill -9 
sleep 15

CUDA_VISIBLE_DEVICES=3 nohup trl vllm-serve --model Qwen/Qwen2.5-1.5B-Instruct --tensor-parallel-size 1 --data-parallel-size 1 --port 8000 2>&1 >/dev/null &


sleep 60 

PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
         --num_processes 3 \
	--main_process_port $PORT \
                  src/open_r1/grpo.py \
        --config recipes/Qwen2.5-1.5B-Instruct/onlyz3_sft_grpo/grpo_fromonlyze3_thensft__esbmc_full.yaml \
    --per_device_train_batch_size 16  2>&1 | tee sft_fromz3only_continue_then_grpo.log



ps -ef|grep python |grep -E "vllm|multiprocessing"|awk '{print $2}'|xargs kill -9 
sleep 150 
