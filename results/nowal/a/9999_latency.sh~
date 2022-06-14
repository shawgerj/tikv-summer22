#!/bin/bash

for i in $(seq 5 5 120)
do
    eval "tail -n 1 ${i}.log | awk -F\", |: \" '{print ${i}\"\t\"\$8}' >> update_latency.txt"
done
