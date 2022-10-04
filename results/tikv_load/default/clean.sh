#!/bin/bash

for i in $(seq 5 60 785)
do
    eval "tail -n 3 ycsb-load.sh_${i}.log | head -n 1 > ${i}.log"
done
