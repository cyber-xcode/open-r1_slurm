
accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
	 --num_processes=4 \
	 src/open_r1/sft.py \
    --config recipes/Qwen2.5-1.5B-Instruct/sft/config_demo.yaml

accelerate launch --config_file recipes/accelerate_configs/ddp.yaml \
	 --num_processes=4 \
	 src/open_r1/sft.py \
    --config recipes/Qwen2.5-1.5B-Instruct/sft/config_demo_typenothink.yaml




bash x_continue.sh 
