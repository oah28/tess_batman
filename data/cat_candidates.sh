#!/bin/bash
for i in {1..7}
do
    echo catting s${i}/
    cat ./tmp/s${i}/* > ./tmp/candidates_s${i}.csv
done

rm ./candidates.csv
echo catting candidates.csv
for i in {1..7}
do
    cat ./tmp/candidates_s${i}.csv >> ./candidates.csv
    echo removing candidates_s${i}.csv
    rm ./tmp/candidates_s${i}.csv
done
