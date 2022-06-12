#!/bin/bash

script=$1
wal=$2

for i in $(seq 5 5 80)
do
    echo "Running ${script} with ${i} threads"
    eval "./${script} ${i} ${wal} > ${script}_${i}.log"
    eval "rm /mydata/local/*"
done
