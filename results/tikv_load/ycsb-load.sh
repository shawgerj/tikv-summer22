#!/bin/bash

ycsb_path="/users/shawgerj/go-ycsb"
pd_addr="10.10.1.4"
pd_port="2379"
records=10000000
threads=120

${ycsb_path}/bin/go-ycsb load tikv -P "${ycsb_path}/workloads/workloada" \
            -p dropdata=false -p verbose=false -p debug.pprof=":6060" \
            -p tikv.pd="${pd_addr}:${pd_port}" -p tikv.type="raw" \
            -p tikv.conncount=128 -p tikv.batchsize=128 \
            -p operationcount=${records} -p recordcount=${records} \
            -p threadcount=${threads}
