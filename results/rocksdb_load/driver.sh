#!/bin/bash

script=$1
wal=$2

for i in $(seq 1 1 5)
do
    echo "Running ${script} with 1 threads"
    eval "./${script} 1 ${wal} > ${script}_${i}.log"
    eval "rm /mydata/local/*"
done
