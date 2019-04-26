#!/bin/bash
#SBATCH --job-name=TESS_Convolve
#SBATCH --workdir=/common/contrib/classroom/ast520/tess_batman/code/Batman/
#SBATCH --output=/common/contrib/classroom/ast520/tess_batman/data/log/batman%A.log
#SBATCH --time=04:00:00
#SBATCH --mem=4000
#SBATCH --account=ast520-spr19

# 2500 curves ran in 2 minutes
# 100x(2500) curves in about 2 hours (gave it 4 because monsoon cores slower)

TBP=/common/contrib/classroom/ast520/tess_batman
echo Starting

source activate batman

pcmd="python $TBP/code/Batman/batman.py $TBP/code/Batman/param.txt $TBP/data/ $S $start $end $TBP/data/tmp/s$S/"
echo running command: $pcmd
srun $pcmd
echo Finished

