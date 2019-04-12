#!/bin/bash
#SBATCH --job-name=TESS_Download
#SBATCH --workdir=/scratch/cw997/TESS/
#SBATCH --output=/scratch/cw997/TESS/log/TESS_Download%A-%a.log
#SBATCH --time=12:00:00
#SBATCH --mem=1000
#SBATCH --array=1-7

ID=$SLURM_ARRAY_TASK_ID

echo id is $ID
mkdir -p Sector$ID
cp ./tesscurl_sector_${ID}_lc.sh ./Sector$ID
cd Sector$ID
chmod u+x tesscurl_sector_${ID}_lc.sh
./tesscurl_sector_${ID}_lc.sh
rm tesscurl_sector_${ID}_lc.sh
