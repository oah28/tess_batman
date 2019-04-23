#!/bin/bash
#SBATCH --job-name=TESS_Convolve
#SBATCH --workdir=/common/contrib/classroom/ast520/tess_batman/code/Convolve/
#SBATCH --output=/common/contrib/classroom/ast520/tess_batman/data/log/tconvolve%A-%a.log
#SBATCH --time=00:05:00
#SBATCH --mem=2000
#SBATCH --account=ast520-spr19


python /common/contrib/classroom/ast520/tess_batman/code/Convolve/convolve.py /common/contrib/classroom/ast520/tess_batman/data/TESS/ /common/contrib/classroom/ast520/tess_batman/data/ 1 0 10 /common/contrib/classroom/ast520/tess_batman/data/tmp/
