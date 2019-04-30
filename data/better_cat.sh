#!/bin/bash
head -1 ./tmp/header.csv > partial_candidates.csv; tail -n +2 -q ./tmp/s1/candidates*.csv >> partial_candidates.csv
