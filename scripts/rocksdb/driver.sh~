#!/bin/bash

script=$1

for i in $(seq 5 5 120)
do
    echo "Running ${script} with ${i} threads"
    eval "./${script} ${i} > ${script}_${i}.log"
done
