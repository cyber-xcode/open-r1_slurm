
rsync -avz -e 'ssh -p 8870'    --exclude "runs" --exclude "*pt" --exclude "*pth"  /common/home/users/j/jwang/scratchDirectory/wj_code/dl_loop/vanilla_direct/save_dir/   wjd_cuda122@146.190.90.3:/home/wjd_cuda122/wj_code/dl_loop/vanilla_direct/save_dir_slurm
