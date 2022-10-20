#!/usr/bin/python

import subprocess
import time
import shutil

executable = '/mydata/rocksdb/examples/shared_log'

# for values 512 through 16K
# database size 32GB
for i in range(10, 15):
    shutil.rmtree('/mydata/rocksdb_kvdb')
    shutil.rmtree('/mydata/rocksdb_raftdb')
 # setup go-ycsb cmd
    value_size = pow(2, i)
    shared_log = True
    wal = False
    print(f'running benchmark for values of size {value_size}, shared log {shared_log} and WAL {wal}')
    
    cmd = [executable, '-v', f'{value_size}']
    
    if shared_log: 
        cmd.extend(['-s'])
    if wal:
        cmd.extend(['-w'])

    print(cmd)
    with open(f'insert_{value_size}_{shared_log}_{wal}', 'w') as outfile:
        # run cmd
        subprocess.run(cmd, stdout=outfile)
                    
    time.sleep(2)
                            
print("finished running benchmarks")
                            
