# Running local cluster

<https://tikv.org/docs/5.1/concepts/tikv-in-5-minutes/>

## My setup

`tiup -v`{.verbatim}

-   1.9.6 tiup
-   Go Version: go1.17.10
-   Git Ref: v1.9.6
-   GitHash: 28965259aecd0a10ae72b69fc59121f6b4edd276

Run: `tiup playground --mode tikv-slim`{.verbatim} to start default
cluster.

## Dashboard

Open your browser, access <http://127.0.0.1:3000>, and then log in to
the Grafana Dashboard. Password is admin/admin.

## Python

`pip install tikv-client`{.verbatim} (slight departure from published
docs)

Hello world script

``` python
from tikv_client import RawClient

client = RawClient.connect(["127.0.0.1:2379"])

# put
client.put(b"k1", b"Hello")
client.put(b"k2", b",")
client.put(b"k3", b"World")
client.put(b"k4", b"!")
client.put(b"k5", b"Raw KV")

# get
print(client.get(b"k1"))
# batch get
print(client.batch_get([b"k1", b"k3"]))
# scan
print(client.scan(b"k1", end=b"k5", limit=10, include_start=True))

```

Output:

``` example
[summer22/tikv] $ python test_raw.py
May 23 14:33:03.437 INFO connect to tikv endpoint: "127.0.0.1:20160"
b'Hello'
[(b'k1', b'Hello'), (b'k3', b'World')]
[(b'k1', b'Hello'), (b'k2', b','), (b'k3', b'World'), (b'k4', b'!')]
```

Using the transactional client

``` python
from tikv_client import TransactionClient

client = TransactionClient.connect(["127.0.0.1:2379"])

# put
txn = client.begin(pessimistic=True)
txn.put(b"k1", b"Hello")
txn.put(b"k2", b",")
txn.put(b"k3", b"World")
txn.put(b"k4", b"!")
txn.put(b"k5", b"Raw KV")
txn.commit()

snapshot = client.snapshot(client.current_timestamp(), True)

# get
print(snapshot.get(b"k1"))
# batch get
print(snapshot.batch_get([b"k1", b"k3"]))
# scan
print(snapshot.scan(b"k1", end=b"k5", limit=10, include_start=True))
```

Output

``` example
[summer22/tikv] $ python test_txn.py
May 23 14:38:17.138 INFO connect to tikv endpoint: "127.0.0.1:20160"
b'Hello'
[(b'k1', b'Hello'), (b'k3', b'World')]
[(b'k1', b'Hello'), (b'k2', b','), (b'k3', b'World'), (b'k4', b'!')]
```

Looks like the Python client is still experimental, as the getting
started guide had some minor syntax errors.

# Scale out - simple experiment

<https://tikv.org/docs/5.1/concepts/explore-tikv-features/replication-and-rebalancing/>

# Simulate simple failures

<https://tikv.org/docs/5.1/concepts/explore-tikv-features/fault-tolerance/>
