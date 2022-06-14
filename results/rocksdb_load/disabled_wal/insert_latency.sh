#!/bin/bash

for i in $(seq 5 5 80)
do
    eval "tail -n 1 ${i}.log | awk -F\", |: \" '{print ${i}\"\t\"\$8}' >> insert_latency.txt"
done
