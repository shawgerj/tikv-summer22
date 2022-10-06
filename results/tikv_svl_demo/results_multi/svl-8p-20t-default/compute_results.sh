#!/bin/bash

echo -e "#\tvalue_size\ttotal_ops\tthroughput_opssec\tlatency_us\tlatency_99.99" > results.out
for sz in {9..14}
do
    awk -v size=$((2**sz)) 'BEGIN{FS=OFS="\t"} NR>1{for (i=1;i<=NF;i++) a[i]+=$i} END{printf size OFS; for (i=1;i<=NF;i++) if(i<3){printf a[i] OFS} else { printf a[i]/(NR-1) OFS}; printf "\n"}' load_a_results_$((2**sz)).out >> results.out
done
