#!/bin/bash
head -1 ./tmp/header.csv > candidates.csv; tail -n +2 -q ./tmp/candidates*.csv >> candidates.csv
