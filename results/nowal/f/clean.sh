#!/bin/bash

for i in $(seq 5 5 120)
do
    eval "tail -n 5 ycsb-f.sh_${i}.log | head -n 3 > ${i}.log"
done
