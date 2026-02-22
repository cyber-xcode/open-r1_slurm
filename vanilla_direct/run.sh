



#export CUDA_VISIBLE_DEVICES=0
#nohup cat mmmmmmaa |xargs -I {} sh -c "bash vllm_msg.sh {} " 2>&1 >/dev/null & 



#export CUDA_VISIBLE_DEVICES=1
#nohup cat mmmmmmab |xargs -I {} sh -c "bash vllm_msg.sh {} " 2>&1 >/dev/null & 


#export CUDA_VISIBLE_DEVICES=2
#nohup cat mmmmmmac |xargs -I {} sh -c "bash vllm_msg.sh {} " 2>&1 >/dev/null & 



export CUDA_VISIBLE_DEVICES=3
nohup cat mmmmmmad |xargs -I {} sh -c "bash vllm_msg.sh {} " 2>&1 >/dev/null & 
