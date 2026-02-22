

md=$1


sbatch --constraint='a100|a40|l40|l40s'  slurm/eval_a40_allone.slurm $md

#sbatch --constraint='a100|a40|l40|l40s'  slurm/eval_a40_allone_08.slurm $md


