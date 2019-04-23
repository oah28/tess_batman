#!/bin/bash
nchunks=${1:-5} # set chunks on cmd line, defaults to 5
for i in $(seq 0 $((nchunks-1)))
do
    sbatch ./array_batch_tconvolve.sh $i $nchunks &
done
echo Jobs submitted

