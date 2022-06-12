#!/bin/bash

ycsb_path="/users/shawgerj/go-ycsb"
records=1000000
threads=$1
wal=$2

${ycsb_path}/bin/go-ycsb load rocksdb -P "${ycsb_path}/workloads/workloada" \
            -p rocksdb.dir="/mydata/local" -p rocksdb.write_buffer_size=2097152 \
            -p rocksdb.bytes_per_sync=1048576 -p rocksdb.wal_bytes_per_sync=524288 \
            -p rocksdb.disable_wal=${wal} \
            -p operationcount=${records} -p recordcount=${records} \
            -p threadcount=${threads}
