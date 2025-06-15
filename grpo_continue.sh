##
##
##
##
##PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
##accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
##         --num_processes 3 \
##        --main_process_port $PORT \
##                  src/open_r1/grpo.py \
##        --config recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback/sft_then_grpo_type3_5k.yaml \
##    --per_device_train_batch_size 16  2>&1 | tee ddp_grpo_1111.log
##
##
##
##
##
##
#
#
#recipes/Qwen2.5-1.5B-Instruct/grpo_sat_test_5k/sft_then_grpo_onlyz3.yaml
#recipes/Qwen2.5-1.5B-Instruct/grpo_sat_test_5k/sft_then_grpo_type3.yaml
#
#
#
#
#PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
#accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
#         --num_processes 3 \
#        --main_process_port $PORT \
#                  src/open_r1/grpo.py \
#        --config recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback/sft_then_grpo_type3.yaml \
#    --per_device_train_batch_size 32  2>&1 | tee ddp_grpo_2222.log
##
##
##
##
#
#
#
#PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
#accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
#         --num_processes 3 \
#        --main_process_port $PORT \
#                  src/open_r1/grpo.py \
#        --config recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback/sft_then_grpo_onlyz3.yaml \
#    --per_device_train_batch_size 32  2>&1 | tee ddp_grpo_444.log
#
##
##
##
##
##
##
#PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
#accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
#         --num_processes 3 \
#        --main_process_port $PORT \
#                  src/open_r1/grpo.py \
#        --config recipes/Qwen2.5-1.5B-Instruct/grpo_sat_test_5k/sft_then_grpo_onlyz3.yaml  \
#    --per_device_train_batch_size 32  2>&1 | tee ddp_grpo_2222.log
#
#
#
#



#PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
#accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
#         --num_processes 3 \
#        --main_process_port $PORT \
#                  src/open_r1/grpo.py \
#        --config recipes/Qwen2.5-1.5B-Instruct/grpo_sat_test_5k/sft_then_grpo_type3.yaml \
#    --per_device_train_batch_size 32  2>&1 | tee ddp_grpo_444.log

#
#
#
#
#
#
