#!/usr/bin/env bash
# shawgerj
# Purpose of these benchmarks is to do a random fill workload on rocksdb
# (100% write) and measure performance with and without WAL.
#
# Much inspiration taken from tools/benchmark.sh
# Config values altered to be similar to TiKV default RocksDB config. 

if [ -z $DB_DIR ]; then
  echo "DB_DIR is not defined"
  exit 0
fi

if [ -z $WAL_DIR ]; then
  echo "WAL_DIR is not defined"
  exit 0
fi

output_dir=${OUTPUT_DIR:-/tmp/}
if [ ! -d $output_dir ]; then
  mkdir -p $output_dir
fi

# size constants
K=1024
M=$((1024 * K))
G=$((1024 * M))
T=$((1024 * T))

num_threads=${NUM_THREADS:-64}
mb_written_per_sec=${MB_WRITE_PER_SEC:-0}
num_keys=${NUM_KEYS:-30000000}
cache_size=${CACHE_SIZE:-$((17179869184))}
compression_max_dict_bytes=${COMPRESSION_MAX_DICT_BYTES:-0}
compression_type=${COMPRESSION_TYPE:-zstd}

function summarize_result {
  test_out=$1
  test_name=$2
  bench_name=$3

  # Note that this function assumes that the benchmark executes long enough so
  # that "Compaction Stats" is written to stdout at least once. If it won't
  # happen then empty output from grep when searching for "Sum" will cause
  # syntax errors.
  uptime=$( grep ^Uptime\(secs $test_out | tail -1 | awk '{ printf "%.0f", $2 }' )
  stall_time=$( grep "^Cumulative stall" $test_out | tail -1  | awk '{  print $3 }' )
  stall_pct=$( grep "^Cumulative stall" $test_out| tail -1  | awk '{  print $5 }' )
  ops_sec=$( grep ^${bench_name} $test_out | awk '{ print $5 }' )
  mb_sec=$( grep ^${bench_name} $test_out | awk '{ print $7 }' )
  lo_wgb=$( grep "^  L0" $test_out | tail -1 | awk '{ print $9 }' )
  sum_wgb=$( grep "^ Sum" $test_out | tail -1 | awk '{ print $9 }' )
  sum_size=$( grep "^ Sum" $test_out | tail -1 | awk '{ printf "%.1f", $3 / 1024.0 }' )
  wamp=$( echo "scale=1; $sum_wgb / $lo_wgb" | bc )
  wmb_ps=$( echo "scale=1; ( $sum_wgb * 1024.0 ) / $uptime" | bc )
  usecs_op=$( grep ^${bench_name} $test_out | awk '{ printf "%.1f", $3 }' )
  p50=$( grep "^Percentiles:" $test_out | tail -1 | awk '{ printf "%.1f", $3 }' )
  p75=$( grep "^Percentiles:" $test_out | tail -1 | awk '{ printf "%.1f", $5 }' )
  p99=$( grep "^Percentiles:" $test_out | tail -1 | awk '{ printf "%.0f", $7 }' )
  p999=$( grep "^Percentiles:" $test_out | tail -1 | awk '{ printf "%.0f", $9 }' )
  p9999=$( grep "^Percentiles:" $test_out | tail -1 | awk '{ printf "%.0f", $11 }' )
  echo -e "$ops_sec\t$mb_sec\t$sum_size\t$lo_wgb\t$sum_wgb\t$wamp\t$wmb_ps\t$usecs_op\t$p50\t$p75\t$p99\t$p999\t$p9999\t$uptime\t$stall_time\t$stall_pct\t$test_name" \
    >> $output_dir/report.txt
}

function run_bulkload {
    wal=$1
    key_size=$2
    value_size=$3

    params="
  --db=$DB_DIR \
  --wal_dir=$WAL_DIR \
  \
  --num=$num_keys \
  --num_levels=6 \
  --key_size=$key_size \
  --value_size=$value_size \
  --block_size=$((64 * K)) \
  --cache_size=$cache_size \
  --cache_numshardbits=6 \
  --compression_max_dict_bytes=$compression_max_dict_bytes \
  --compression_ratio=0.5 \
  --compression_type=$compression_type \
  --level_compaction_dynamic_level_bytes=true \
  --bytes_per_sync=$((1 * M)) \
  --wal_bytes_per_sync=$((512 * K)) \ 
  --cache_index_and_filter_blocks=0 \
  --pin_l0_filter_and_index_blocks_in_cache=1 \
  --benchmark_write_rate_limit=$(( 1024 * 1024 * $mb_written_per_sec )) \
  \
  --hard_rate_limit=3 \
  --rate_limit_delay_max_milliseconds=1000000 \
  --write_buffer_size=$((64 * M)) \
  --target_file_size_base=$((64 * M)) \
  --max_bytes_for_level_base=$((512 * M)) \
  \
  --verify_checksum=1 \
  --delete_obsolete_files_period_micros=$((60 * M)) \
  --max_bytes_for_level_multiplier=8 \
  \
  --statistics=0 \
  --stats_per_interval=1 \
  --stats_interval_seconds=60 \
  --histogram=1 \
  \
  --memtablerep=skip_list \
  --bloom_bits=10 \
  --open_files=-1 \
  \
  --compaction_readahead_size=$((2 * M)) \ 
  --new_table_reader_for_compaction_inputs=true \
  --max_background_compactions=4 \
  --max_write_buffer_number=3 \
  --allow_concurrent_memtable_write=false \
  --max_background_flushes=4 \
  --level0_file_num_compaction_trigger=8 \
  --level0_slowdown_writes_trigger=20 \
  --level0_stop_writes_trigger=40"

      cmd="./db_bench --benchmarks=fillrandom \
       --use_existing_db=0 \
       --disable_auto_compactions=0 \
       --sync=0 \
       $params \
       --threads=1 \
       --memtablerep=skip_list \
       --allow_concurrent_memtable_write=false \
       --disable_wal=$wal \
       --seed=$( date +%s ) \
       2>&1 | tee -a $output_dir/benchmark_bulkload_fillrandom.log"
  echo $cmd | tee $output_dir/benchmark_bulkload_fillrandom.log
  eval $cmd
  summarize_result $output_dir/benchmark_bulkload_fillrandom.log bulkload fillrandom
}

function do_benchmarks {
    wal=0
    key_size=20
    for wal in $(seq 0 1 1)
    do    
        for i in $(seq 1 1 6)
        do
            value_size=$(((2 ** i) * 32))
            echo "Running benchmark with disable_wal ${wal} and ${value_size} values"
            eval "rm -r /mydata/*"
            run_bulkload $wal $key_size $value_size
        done
    done    
}

do_benchmarks
