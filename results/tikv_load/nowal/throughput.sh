#!/bin/bash

for i in $(seq 5 60 785)
do
    eval "awk -F\", |: \" '{sum+=\$6;}END{print ${i}\"\t\"sum;}' ${i}.log >> throughput.txt"
done
