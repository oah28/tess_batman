#!/bin/bash
#SBATCH --job-name=TESS_Convolve
#SBATCH --workdir=/common/contrib/classroom/ast520/tess_batman/code/Convolve/
#SBATCH --output=/common/contrib/classroom/ast520/tess_batman/code/TESS_Convolve.log
#SBATCH --time=24:00:00
#SBATCH --mem=2000
#SBATCH --account=ast520-spr19

python ./TESS_Convolve_Monsoon.py
