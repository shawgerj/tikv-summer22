#!/bin/bash

ycsb_path="/mydata2/go-ycsb"

${ycsb_path}/bin/go-ycsb load tikv -P "${ycsb_path}/workloads/workloada512" \
                -p tikv.pd="10.10.1.2:2379" \
                -p tikv.type="raw" \
                -p threadcount=160

