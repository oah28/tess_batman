#!/bin/bash
#SBATCH --job-name=TESS_Convolve
#SBATCH --workdir=/common/contrib/classroom/ast520/tess_batman/code/Convolve/
#SBATCH --output=/common/contrib/classroom/ast520/tess_batman/data/log/tconvolve%A-%a.log
#SBATCH --time=80:00:00
#SBATCH --mem=6000
#SBATCH --account=ast520-spr19
#SBATCH --array=0-97

# Array must be 0-(7n-1), each setor is split into n chunks

# 127850 files in Sectors 1-7
# each tess file takes ~6 seconds on batmanCurves_small (2560 curves)
# distributing to 7*5 = 35 tasks
# each task needs 21900 seconds or 6 hours
# round up to 8 hours

# Big:
# New code is ~2secs per tess file (2560 curves)
# Each tess file should take ~100x2s = 200 secs
# 200*127850 = 25.6 Msecs
# 196 tasks = 36 hrs
# 98 tasks = 72 hrs

TBP=/common/contrib/classroom/ast520/tess_batman
echo Starting

nprocs=5
convolvechunk=100

batmansuffix=${1:-_small}
nchunks=$(($SLURM_ARRAY_TASK_COUNT/7))
mychunk=$(($SLURM_ARRAY_TASK_ID/7))
S=$(($SLURM_ARRAY_TASK_ID%7+1))
echo Working on sector $S

#source activate /home/cjt347/.conda/envs/tconvolve
module load anaconda
source activate tconvolve

N=$(ls -1q $TBP/data/TESS/Sector$S | wc -l)
echo found $N files in sector $S

let start="$mychunk * $N / $nchunks"
let end="($mychunk+1) * $N / $nchunks"
pcmd="python $TBP/code/Convolve/convolve.py $TBP/data/TESS/ $TBP/data/ $S $start $end $TBP/data/tmp/s$S/ $batmansuffix $nprocs $convolvechunk"
echo running command: $pcmd
srun $pcmd

echo Finished
