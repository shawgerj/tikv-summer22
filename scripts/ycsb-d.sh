#!/bin/bash

ycsb_path="/users/shawgerj/go-ycsb"
pd_addr="10.10.1.4"
pd_port="2379"
records=1000000
threads=$1

${ycsb_path}/bin/go-ycsb run tikv -P "${ycsb_path}/workloads/workloadd" \
            -p verbose=false -p debug.pprof=":6060" \
            -p tikv.pd="${pd_addr}:${pd_port}" -p tikv.type="raw" \
            -p tikv.conncount=128 -p tikv.batchsize=128 \
            -p operationcount=${records} -p recordcount=${records} \
            -p threadcount=${threads}
