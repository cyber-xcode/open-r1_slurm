
export PYTHONPATH="./src"

#export NCCL_IB_DISABLE=1
#export NCCL_P2P_DIRECT_DISABLE=1
#export NCCL_DEBUG=INFO

#export NCCL_P2P_LEVEL=NODE

export CUDA_VISIBLE_DEVICES=0,1,2,3



for i in {0..1} ; do 

PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))






#ACCELERATE_LOG_LEVEL=info accelerate launch \
#        --config_file recipes/accelerate_configs/ddp.yaml \
#        --main_process_port $PORT \
#           --num_processes=3 src/open_r1/grpo.py \
#                  --config \
#		recipes/Qwen2.5-1.5B-Instruct/grpo_train_general_benchasref_a800/qwengene_train_onlyz3.yaml  2>&1 | tee verl_demo11.log



#ACCELERATE_LOG_LEVEL=info accelerate launch \
#        --config_file recipes/accelerate_configs/ddp.yaml \
#        --main_process_port $PORT \
#           --num_processes=3 src/open_r1/grpo.py \
#                  --config \
#	recipes/Qwen2.5-1.5B-Instruct/grpo_train_general_benchasref_a800/qwengene_train_format_noseformal.yaml  2>&1 | tee verl_demo13.log





ACCELERATE_LOG_LEVEL=info accelerate launch \
        --config_file recipes/accelerate_configs/ddp.yaml \
        --main_process_port $PORT \
           --num_processes=3 src/open_r1/grpo.py \
                  --config \
	recipes/Qwen2.5-1.5B-Instruct/grpo_train_general_benchasref_a800/qwengene_train_formay_promptype3.yaml  2>&1 | tee verl_demo12222.log



#ACCELERATE_LOG_LEVEL=info accelerate launch \
#        --config_file recipes/accelerate_configs/ddp.yaml \
#        --main_process_port $PORT \
#           --num_processes=3 src/open_r1/grpo.py \
#                  --config \
#	recipes/Qwen2.5-1.5B-Instruct/grpo_train_general_benchasref_a800/qwengene_train_formay.yaml  2>&1 | tee verl_demo12.log

done 
