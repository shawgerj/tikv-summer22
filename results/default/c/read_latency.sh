#!/bin/bash

for i in $(seq 5 5 120)
do
    eval "awk -F\", |: \" '{print ${i}\"\t\"\$8}' ${i}.log >> read_latency.txt"
done
