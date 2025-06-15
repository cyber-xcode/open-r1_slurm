#
#
#accelerate launch --config_file recipes/accelerate_configs/fsdp.yaml \
#         --num_processes=4 \
#         src/open_r1/sft_raw.py \
#         --per_device_train_batch_size=16 \
#    --config recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_32768/feedback_gt_msg.yaml 
#
#
#
#accelerate launch --config_file recipes/accelerate_configs/fsdp.yaml \
#         --num_processes=4 \
#         src/open_r1/sft_raw.py \
#         --per_device_train_batch_size=16 \
#    --config recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_32768/feedback_only.yaml 
#
#
#
#
#accelerate launch --config_file recipes/accelerate_configs/fsdp.yaml \
#         --num_processes=4 \
#         src/open_r1/sft_raw.py \
#         --per_device_train_batch_size=16 \
#    --config  recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_32768/gt_msg_only.yaml 
#
#
#
#
#
#
#
#
#
#accelerate launch --config_file recipes/accelerate_configs/fsdp.yaml \
#         --num_processes=4 \
#         src/open_r1/sft_raw.py \
#         --per_device_train_batch_size=16 \
#    --config recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback/feedback_gt_msg.yaml 
#
#
#
#accelerate launch --config_file recipes/accelerate_configs/fsdp.yaml \
#         --num_processes=4 \
#         src/open_r1/sft_raw.py \
#         --per_device_train_batch_size=16 \
#    --config recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback/feedback_only.yaml 
#
#
#
#
#accelerate launch --config_file recipes/accelerate_configs/fsdp.yaml \
#         --num_processes=4 \
#         src/open_r1/sft_raw.py \
#         --per_device_train_batch_size=16 \
#    --config  recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback/gt_msg_only.yaml 
#
#
#
#
#
#
#
#
#
#
#
#bash grpo_continue.sh 
#
#
#
#
#accelerate launch --config_file recipes/accelerate_configs/fsdp.yaml \
#         --num_processes=4 \
#         src/open_r1/sft_raw.py \
#         --per_device_train_batch_size=8 \
#    --config recipes/Qwen2.5-7B-Instruct/sft_7b_feedback/feedback_gt_msg.yaml  2>&1 | tee ddp_grpo_37337_feedback_gt_msg.log 
#
#
#
#accelerate launch --config_file recipes/accelerate_configs/fsdp.yaml \
#         --num_processes=4 \
#         src/open_r1/sft_raw.py \
#         --per_device_train_batch_size=8 \
#    --config recipes/Qwen2.5-7B-Instruct/sft_7b_feedback/feedback_only.yaml  2>&1 | tee ddp_grpo_37337_type3_feedback_only.log
#
#
#
#
#accelerate launch --config_file recipes/accelerate_configs/fsdp.yaml \
#         --num_processes=4 \
#         src/open_r1/sft_raw.py \
#         --per_device_train_batch_size=8 \
#    --config  recipes/Qwen2.5-7B-Instruct/sft_7b_feedback/gt_msg_only.yaml  2>&1 | tee ddp_grpo_37337_gt_msg_only.log
#
#
#
#
