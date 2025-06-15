#
#
#
#
#
#
#
##PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
##accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
##         --num_processes=4 \
##        --main_process_port $PORT \
##         src/open_r1/sft_raw.py \
##         --per_device_train_batch_size=128 \
##    --config  recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_diff/feedback_gt_msg_rerun_4096.yaml  2>&1 | tee ddp_grpo_4096_type3_100000_rerun.log
#
#
##PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
##accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
##         --num_processes=4 \
##        --main_process_port $PORT \
##         src/open_r1/sft_raw.py \
##         --per_device_train_batch_size=16 \
##    --config  recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_diff/ddp16batch_feedback_gt_msg_rerun_4096.yaml  2>&1 | tee ddp_grpo_4096_type3_100000_rerun.log
#
#
#
##PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
##accelerate launch --config_file recipes/accelerate_configs/fsdp.yaml \
##         --num_processes=4 \
##        --main_process_port $PORT \
##         src/open_r1/sft_raw.py \
##         --per_device_train_batch_size=16 \
##    --config  recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_diff/fsdp_feedback_gt_msg_rerun_4096.yaml  2>&1 | tee ddp_grpo_4096_type3_100000_rerun.log
#
#
#
#PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
#accelerate launch --config_file recipes/accelerate_configs/fsdp.yaml \
#         --num_processes=4 \
#        --main_process_port $PORT \
#         src/open_r1/sft_raw.py \
#         --per_device_train_batch_size=16 \
#    --config  recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_diff/nofeed_sft_savesteps.yaml  2>&1 | tee fsdp_nofeed_sft_savestepsrerun.log
#
#PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
#accelerate launch --config_file recipes/accelerate_configs/fsdp.yaml \
#         --num_processes=4 \
#        --main_process_port $PORT \
#         src/open_r1/sft_raw.py \
#         --per_device_train_batch_size=16 \
#    --config  recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_diff/feedback_mix.yaml  2>&1 | tee dfsdp_feedback_mix_rerun.log
#
#
#
#
#PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
#accelerate launch --config_file recipes/accelerate_configs/fsdp.yaml \
#         --num_processes=4 \
#        --main_process_port $PORT \
#         src/open_r1/sft_raw.py \
#         --per_device_train_batch_size=16 \
#    --config  recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_diff/nofeed_sft_savesteps_nopack.yaml  2>&1 | tee fsdp_nofeed_sft_savestepsrerun.log
#
#PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
#accelerate launch --config_file recipes/accelerate_configs/fsdp.yaml \
#         --num_processes=4 \
#        --main_process_port $PORT \
#         src/open_r1/sft_raw.py \
#         --per_device_train_batch_size=16 \
#    --config  recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_diff/feedback_mix_nopack.yaml  2>&1 | tee dfsdp_feedback_mix_rerun.log
#
#
#
##PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
##accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
##         --num_processes 3 \
##        --main_process_port $PORT \
##                  src/open_r1/grpo.py \
##        --config recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_diff/sft_then_grpo_onlyz3_5k_ep32_4096.yaml \
##    --per_device_train_batch_size 16  2>&1 | tee ddp_grpo_4096_type3_300000.log
#
#
##PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
##accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
##         --num_processes 3 \
##        --main_process_port $PORT \
# #                 src/open_r1/grpo.py \
# #       --config recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_diff/sft_then_grpo_type3_5k_ep32_4096.yaml \
# #   --per_device_train_batch_size 16  2>&1 | tee ddp_grpo_4096_type3_400000.log








#PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
#accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
#         --num_processes 3 \
#        --main_process_port $PORT \
#                 src/open_r1/grpo.py \
#       --config recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_mix/sft_then_grpo_type3_5k_ep32.yaml \
#   --per_device_train_batch_size 16  2>&1 | tee ddp_grpo_4096_type3_400000.log



#PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
#accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
#         --num_processes 3 \
#        --main_process_port $PORT \
 #                src/open_r1/grpo.py \
 #      --config recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_mix/sft_then_grpo_onlyz3_5k_ep32.yaml  \
 #  --per_device_train_batch_size 16  2>&1 | tee ddp_grpo_4096_type3_400000.log



#PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
#accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
#         --num_processes 3 \
#        --main_process_port $PORT \
#                 src/open_r1/grpo.py \
#       --config recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_mix/sftnofeed_then_grpo_type3_full_ep32.yaml \
#   --per_device_train_batch_size 16  2>&1 | tee ddp_grpo_4096_type3_400000_full_golden.log

#recipes/Qwen2.5-1.5B-Instruct/sft_1b5_golden_a100_p1p2/sft_then_grpo_type3_5k_ep32.yaml
#PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
#accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
#         --num_processes 3 \
#        --main_process_port $PORT \
#                 src/open_r1/grpo.py \
#       --config recipes/Qwen2.5-1.5B-Instruct/sft_1b5_golden_a100_p1p2/sft_then_grpo_type3_5k_ep32.yaml \
#   --per_device_train_batch_size 16  2>&1 | tee ddp_grpo_4096_type3_400000sft_then_grpo_type3_5k_ep32.log


#sft_then_grpo_type3_full_ep32
#PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
#accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
#         --num_processes 3 \
#        --main_process_port $PORT \
#                 src/open_r1/grpo.py \
#       --config recipes/Qwen2.5-1.5B-Instruct/sft_1b5_golden_a100_p1p2/sft_then_grpo_type3_full_ep32.yaml \
#   --per_device_train_batch_size 16  2>&1 | tee ddp_grpo_4096_type3_400000sft_then_grpo_type3_full_ep32.log


#PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
#accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
#         --num_processes 3 \
#        --main_process_port $PORT \
#                 src/open_r1/grpo.py \
#       --config recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_mix/sftnofeed_then_grpo_type3_full_ep32_treesitter.yaml \
#   --per_device_train_batch_size 16  2>&1 | tee ddp_grpo_4096_type3_400000_full_treesitter.log


