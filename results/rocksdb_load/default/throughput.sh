#!/bin/bash

for i in $(seq 5 5 80)
do
    eval "awk -F\", |: \" '{sum+=\$6;}END{print ${i}\"\t\"sum;}' ${i}.log >> throughput.txt"
done
