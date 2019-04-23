#!/bin/bash
#SBATCH --job-name=TESS_Convolve
#SBATCH --workdir=/common/contrib/classroom/ast520/tess_batman/code/Convolve/
#SBATCH --output=/common/contrib/classroom/ast520/tess_batman/data/log/tconvolve%A-%a.log
#SBATCH --time=08:00:00
#SBATCH --mem=2000
#SBATCH --account=ast520-spr19
#SBATCH --array=1-7

# 127850 files in Sectors 1-7
# each tess file takes ~6 seconds on batmanCurves_small (2560 curves)
# distributing to 7*5 = 35 tasks
# each task needs 21900 seconds or 6 hours
# round up to 8 hours

TBP=/common/contrib/classroom/ast520/tess_batman
echo Starting
i=$1
nchunks=$2
S=$SLURM_ARRAY_TASK_ID
echo Working on sector $S

#source activate /home/cjt347/.conda/envs/tconvolve
source activate tconvolve

N=$(ls -1q $TBP/data/TESS/Sector$S | wc -l)
echo found $N files in sector $S

let start="$i * $N / $nchunks"
let end="($i+1) * $N / $nchunks"
pcmd="python $TBP/code/Convolve/convolve.py $TBP/data/TESS/ $TBP/data/ $S $start $end $TBP/data/tmp/s$S/"
echo running command: $pcmd
srun $pcmd
echo Finished

