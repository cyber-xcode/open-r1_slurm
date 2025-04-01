
export PYTHONPATH="./src"

#export NCCL_IB_DISABLE=1
#export NCCL_P2P_DIRECT_DISABLE=1
#export NCCL_DEBUG=INFO

#export NCCL_P2P_LEVEL=NODE

export CUDA_VISIBLE_DEVICES=0,1,2,3



PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))




#ACCELERATE_LOG_LEVEL=info accelerate launch \
#	--config_file recipes/accelerate_configs/fsdp.yaml \
#	--main_process_port $PORT \
#	--num_processes=4 src/open_r1/sft.py \
#	--per_device_train_batch_size 64 \
#	--config \
#	recipes/Qwen2.5-1.5B-Instruct/grpo_train_general_benchasref_a800_full_sft_then_grpo_ddp__now/sft_from_l40s_q1b5_full.yaml 


for i in {0..3} ; do 


	PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))






	ACCELERATE_LOG_LEVEL=info accelerate launch \
		--config_file recipes/accelerate_configs/ddp.yaml \
		--main_process_port $PORT \
		   --num_processes=3 src/open_r1/grpo.py \
		   --per_device_train_batch_size 16 \
			  --config \
		recipes/Qwen2.5-1.5B-Instruct/grpo_train_general_benchasref_a800_full_sft_then_grpo_ddp__now/qwengene_train_formay_promptype3.yaml \
		--save_steps 100 2>&1 | tee verl_demo11111.log








	ACCELERATE_LOG_LEVEL=info accelerate launch \
		--config_file recipes/accelerate_configs/ddp.yaml \
		--main_process_port $PORT \
		   --num_processes=3 src/open_r1/grpo.py \
		   --per_device_train_batch_size 32 \
				  --config \
			recipes/Qwen2.5-1.5B-Instruct/grpo_train_general_benchasref_a800_full_sft_then_grpo_ddp__now/qwengene_train_onlyz3.yaml \
			                --save_steps 100  2>&1 | tee verl_demo2222222.log
	




	ACCELERATE_LOG_LEVEL=info accelerate launch \
		--config_file recipes/accelerate_configs/ddp.yaml \
		--main_process_port $PORT \
		   --num_processes=3 src/open_r1/grpo.py \
		   --per_device_train_batch_size 32 \
			  --config \
		recipes/Qwen2.5-1.5B-Instruct/grpo_train_general_benchasref_a800_full_sft_then_grpo_ddp__now/qwengene_train_formay.yaml \
		                --save_steps 100  2>&1 | tee verl_demo3333333333.log
	




done 
