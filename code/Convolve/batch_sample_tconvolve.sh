#!/bin/bash
#SBATCH --job-name=sample_Convolve
#SBATCH --workdir=/common/contrib/classroom/ast520/tess_batman/code/Convolve/
#SBATCH --output=/common/contrib/classroom/ast520/tess_batman/sampleData/log/sample_convolve%A.log
#SBATCH --time=02:00:00
#SBATCH --mem=4000
#SBATCH --account=cs599-spr19


python /common/contrib/classroom/ast520/tess_batman/code/Convolve/convolve.py /common/contrib/classroom/ast520/tess_batman/sampleData/ /common/contrib/classroom/ast520/tess_batman/data/ 0 0 6 /common/contrib/classroom/ast520/tess_batman/sampleData/ _big 0 100
