#!/usr/bin/python

import subprocess
import time
from fabric import Connection

pd_node = "10.10.1.2"
tikv_nodes = ["10.10.1.3", "10.10.1.4", "10.10.1.5"]

DB_SIZE = (32 * 1024 * 1024 * 1024) # 32GB
executable = '/mydata2/go-ycsb/bin/go-ycsb'
workload = '/mydata2/go-ycsb/workloads/workloada'

run_pd_cmd = f'/mydata2/pd/bin/pd-server --name=\"pd\" --data-dir=\"/users/shawgerj/pd\" --client-urls=\"http://{pd_node}:2379\" --peer-urls=\"http://{pd_node}:2380\" --log-file=\"/users/shawgerj/pd.log\"'

run_tikv_cmds = list(map(lambda n:
                         f'/mydata2/tikv2/target/release/tikv-server --pd-endpoints=\"{pd_node}:2379\" --addr=\"{n}:20160\" --status-addr=\"{n}:20180\" --data-dir=\"/mydata2/tikv-data\" --log-file=\"/mydata2/tikv.log\"',
                         tikv_nodes))

# setup connections
pd_cxn = Connection(host=pd_node, user='shawgerj', port=22)
tikv_cxns = list(map(lambda c: Connection(host=c,
                                          user='shawgerj',
                                          port=22),
                     tikv_nodes))

# for values 1K through 32K
# database size 32GB
for i in range(7, 13):

    # ssh to pd node, run pd
    print("starting pd...")
    pd_cxn.run("screen -d -m %s" % run_pd_cmd, warn=True, hide=True)
    time.sleep(3)
    
    # ssh to each server, start tikv
    print("starting tikv...")
    for (c, cmd) in zip(tikv_cxns, run_tikv_cmds):
        print(f'running cmd {cmd}')
        c.run("screen -d -m %s" % cmd, warn=True, hide=True)
    time.sleep(3)
    
    # setup go-ycsb cmd
    fieldcount = 8
    fieldlength = pow(2, i)
    size = fieldcount * fieldlength
    recordcount = int(DB_SIZE / size)
    operationcount = 2000000

    print(f'running benchmark for values of size {size} and {recordcount} records')

    cmd = [executable, 'load', 'tikv', '-P', workload]
    opts = ['tikv.pd=10.10.1.2:2379', 'tikv.type=raw', 'threadcount=200',
            f'fieldcount={fieldcount}', f'fieldlength={fieldlength}',
            f'operationcount={operationcount}', f'recordcount={recordcount}']

    for o in opts:
        cmd.extend(['-p', o])
        
    name_pre = 'load_a_'
    print(cmd)
    with open(f'{name_pre}{size}', 'w') as outfile:
        # run cmd
        subprocess.run(cmd, stdout=outfile)

    # shutdown tikv processes, clear dbs
    print("closing tikv servers...")
    for c in tikv_cxns:
        c.run('killall tikv-server')
        time.sleep(2)
        c.run('rm /mydata2/tikv.log')
        c.run('rm -r /mydata2/tikv-data')


    time.sleep(1)
    print("closing pd server...")
    # shutdown pd, clear pd state
    pd_cxn.run('killall pd-server')
    time.sleep(2)
    pd_cxn.run('rm /users/shawgerj/pd.log')
    pd_cxn.run('rm -r /users/shawgerj/pd')
    time.sleep(2)

print("finished running benchmarks")
