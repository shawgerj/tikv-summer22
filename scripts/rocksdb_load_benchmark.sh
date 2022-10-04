#!/bin/bash

function run_workload {
    ycsb_path="/users/shawgerj/go-ycsb"
    records=30000000
    wal=$1
    value_size=$2

    ${ycsb_path}/bin/go-ycsb load rocksdb -P "${ycsb_path}/workloads/workloada${value_size}" \
                -p rocksdb.dir="/mydata2" \
                -p rocksdb.write_buffer_size=67108864 \
                -p rocksdb.level0_file_num_compaction_trigger=8 \
                -p rocksdb.level0_slowdown_writes_trigger=20 \
                -p rocksdb.stop_writes_trigger=40 \
                -p rocksdb.target_file_size_base=67108864 \
                -p rocksdb.max_bytes_for_level_base=536870912 \
                -p rocksdb.max_bytes_for_level_multiplier=8 \
                -p rocksdb.allow_concurrent_memtable_writes=false \
                -p rocksdb.disable_wal=${wal}
}

function do_benchmarks {
    wal=0
    for wal in $(seq 0 1 1)
    do
        for i in $(seq 1 1 6)
        do
            value_size=$(((2 ** i) * 32))
            echo "Running go-ycsb against rocksdb with disable_wal ${wal} and loading workload workloada${value_size}\n"
            eval "rm -r /mydata2/*"
            run_workload $wal $value_size
        done
    done
}

do_benchmarks
