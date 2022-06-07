#!/bin/bash

for i in $(seq 5 5 120)
do
    eval "tail -n 3 ycsb-c.sh_${i}.log | head -n 1 > ${i}.log"
done
