#!/usr/bin/python

import subprocess
import time
from fabric import Connection

pd_node = "10.10.1.2"
tikv_nodes = ["10.10.1.3", "10.10.1.4", "10.10.1.5"]

DB_SIZE = (32 * 1024 * 1024 * 1024) # 32GB
NUM_BENCHES = 8
executable = '/mydata/go-ycsb/bin/go-ycsb'
workload = '/mydata/go-ycsb/workloads/workloada'

run_pd_cmd = f'/mydata/pd/bin/pd-server --name=\"pd\" --data-dir=\"/users/shawgerj/pd\" --client-urls=\"http://{pd_node}:2379\" --peer-urls=\"http://{pd_node}:2380\" --log-file=\"/users/shawgerj/pd.log\"'

run_tikv_cmds = list(map(lambda n:
                         f'/mydata/tikv2/target/release/tikv-server --pd-endpoints=\"{pd_node}:2379\" --addr=\"{n}:20160\" --status-addr=\"{n}:20180\" --data-dir=\"/mydata/tikv-data\" --log-file=\"/mydata/tikv.log\"',
                         tikv_nodes))

# setup connections
pd_cxn = Connection(host=pd_node, user='shawgerj', port=22)
tikv_cxns = list(map(lambda c: Connection(host=c,
                                          user='shawgerj',
                                          port=22),
                     tikv_nodes))

# for values 512 through 16K
# database size 32GB
for i in range(6, 12):

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
    recordcount = int((DB_SIZE / size) / NUM_BENCHES)
    operationcount = 2000000

    print(f'running benchmark for values of size {size} and {recordcount} records')

    cmd = [executable, 'load', 'tikv', '-P', workload]
    opts = ['tikv.pd=10.10.1.2:2379', 'tikv.type=raw', 'threadcount=20',
            f'fieldcount={fieldcount}', f'fieldlength={fieldlength}',
            f'operationcount={operationcount}', f'recordcount={recordcount}']

    for o in opts:
        cmd.extend(['-p', o])

    ps = []
    for i in range(0, NUM_BENCHES):
        print(cmd)
        with open(f'load_a_{size}_{i}', 'w') as outfile:
            # run cmd
            p = subprocess.Popen(cmd, stdout=outfile)
            ps.append(p)

    for p in ps:
        p.wait()

    # shutdown tikv processes, clear dbs
    # adding a bunch of waits because I was getting weird errors
    time.sleep(5)
    print("closing tikv servers...")
    for c in tikv_cxns:
        c.run('killall tikv-server')
        time.sleep(10)
        c.run('rm /mydata/tikv.log')
        time.sleep(10)
        c.run('rm -r /mydata/tikv-data')


    time.sleep(1)
    print("closing pd server...")
    # shutdown pd, clear pd state
    pd_cxn.run('killall pd-server')
    time.sleep(2)
    pd_cxn.run('rm /users/shawgerj/pd.log')
    pd_cxn.run('rm -r /users/shawgerj/pd')
    time.sleep(2)

print("finished running benchmarks")
