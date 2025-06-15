

PORT=$(( ((RANDOM<<15)|RANDOM) % 63001 + 2000 ))
accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
         --num_processes=4 \
        --main_process_port $PORT \
         src/open_r1/sft_raw.py \
         --per_device_train_batch_size=128 \
    --config  recipes/Qwen2.5-1.5B-Instruct/sft_1b5_feedback_diff/feedback_gt_msg_rerun_4096.yaml  2>&1 | tee ddp_grpo_4096_type3_100000_rerun.log
