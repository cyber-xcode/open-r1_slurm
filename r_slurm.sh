



for x in $(find recipes/Qwen2.5-1.5B-Instruct/grpo_train_general_benchasref_a800_full_sft_then_grpo_trueddp/ -name 'sft*.yaml'); do

	filename="$(basename "$x")"
	filename_no_ext="${filename%.yaml}"
	sbatch   --job-name="open_$filename_no_ext"  --nodes=1 \
		--constraint="a40|a100|l40|l40s|h200" \
		slurm/train_a40.slurm Qwen2.5-1.5B-Instruct sft $x   ddp '--per_device_train_batch_size=8 --num_train_epochs=10 --save_only_model=true --save_steps=100000  ' 2


done 

#sbatch   --job-name=open_our_small2  --nodes=1 slurm/train_a40.slurm Qwen2.5-1.5B-Instruct sft "recipes/Qwen2.5-1.5B-Instruct/grpo_train_general_benchasref_a800_full_sft_then_grpo_trueddp/sft_l40sconfig_demo_full_4096_ddp.yaml"  ddp '--per_device_train_batch_size=8 --num_train_epochs=10  ' 2
