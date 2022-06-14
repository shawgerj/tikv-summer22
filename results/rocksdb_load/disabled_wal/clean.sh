#!/bin/bash

for i in $(seq 5 5 80)
do
    eval "tail -n 1 ycsb-rocks-load.sh_${i}.log | head -n 2 > ${i}.log"
done
