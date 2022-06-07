#!/bin/bash

./tikv/pd/bin/pd-server --name=pd1 \
--data-dir=pd1 \
--client-urls="http://10.10.1.4:2379" \
--peer-urls="http://10.10.1.4:2380" \
--initial-cluster="pd1=http://10.10.1.4:2380" \
--log-file=pd1.log
