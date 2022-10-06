#!/bin/bash


for sz in {9..14}
do
    echo -e "#\tops\tthroughput\tlatency\tlatency_99.99" > load_a_results_$((2**sz)).out
    for i in {0..7}
    do
	tail -n 3 load_a_$((2**sz))_${i} | head -n 1 | awk -F', |: ' -v OFS='\t' '{print $4, $6, $8, $18}' >> load_a_results_$((2**sz)).out
    done
done

