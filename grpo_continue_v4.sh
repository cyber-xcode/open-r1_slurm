##PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
##accelerate launch --config_file recipes/accelerate_configs/fsdp.yaml \
##         --num_processes=4 \
##        --main_process_port $PORT \
##         src/open_r1/sft_raw.py \
##         --per_device_train_batch_size=16 \
##    --config  recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_diff/feedback_gt_msg_rerun.yaml  2>&1 | tee ddp_grpo_37337_type3_100000_rerun.log
#
#
##PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
##accelerate launch --config_file recipes/accelerate_configs/fsdp.yaml \
##         --num_processes=4 \
##        --main_process_port $PORT \
##         src/open_r1/sft_raw.py \
##         --per_device_train_batch_size=16 \
##    --config  recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_diff/feedback_gt_msg.yaml  2>&1 | tee ddp_grpo_37337_type3_100000.log
#
#
##PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
##accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
##         --num_processes 3 \
##        --main_process_port $PORT \
##                  src/open_r1/grpo.py \
##        --config recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_diff/sft_then_grpo_onlyz3_5k.yaml \
##    --per_device_train_batch_size 16  2>&1 | tee ddp_grpo_37337_type3_300000.log
#
#
#
#
#PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
#accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
#         --num_processes 3 \
#        --main_process_port $PORT \
#                  src/open_r1/grpo.py \
#        --config recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_diff/sft_then_grpo_type3_5k_ep32.yaml \
#    --per_device_train_batch_size 16  2>&1 | tee ddp_grpo_37337_type3_400000.log
#
#
#
#
#PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
#accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
#         --num_processes 3 \
#        --main_process_port $PORT \
#                  src/open_r1/grpo.py \
#        --config recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_diff/sft_then_grpo_type3_5k.yaml \
#    --per_device_train_batch_size 16  2>&1 | tee ddp_grpo_37337_type3_400001.log
#
#
#
#PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
#accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
#         --num_processes 3 \
#        --main_process_port $PORT \
#                  src/open_r1/grpo.py \
#        --config recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_diff/sft_then_grpo_onlyz3_5k_ep32.yaml \
#    --per_device_train_batch_size 16  2>&1 | tee ddp_grpo_37337_type3_400002.log
#
#
#
#
#







#PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
#accelerate launch --config_file recipes/accelerate_configs/fsdp.yaml \
#         --num_processes=4 \
#         src/open_r1/sft_raw.py \
#         --per_device_train_batch_size=4 \
#    --config recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_diff/feedback_gt_msg_7b.yaml  2>&1 | tee ddp_grpo_37337_type3_500000.log
