#!/bin/bash

# Number of sbatch scripts you want
num_sbatch_scripts=10

for i in $(seq 1 1 $num_sbatch_scripts)
do
  sbatch -A euler -c 11 <<EOF
#!/bin/bash
#SBATCH --job-name=GFM
#SBATCH --gres=gpu:1
#SBATCH --time=100:59:59
#SBATCH --partition=euler

# env
export TRITON_CACHE_DIR=/tmp/triton_cache_$SLURM_JOB_ID
source ~/miniconda3/etc/profile.d/conda.sh
conda activate graphany

# Run the main.py script with the parameter set for this sbatch script
while IFS= read -r line
do
  python -u /home/benfin/GraphAny/run_and_record.py.py \$line
done < /home/benfin/GraphAny/scripts_euler/grid/batch_${i}.txt
EOF
done