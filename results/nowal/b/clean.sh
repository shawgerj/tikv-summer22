#!/bin/bash

for i in $(seq 5 5 120)
do
    eval "tail -n 4 ycsb-b.sh_${i}.log | head -n 2 > ${i}.log"
done
