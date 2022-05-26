# TiKV system overview

## Client

The client caches the routing information from the [*routing
table*]{.spurious-link target="*Routing table"}. If a client tried to
contact a leader but it is not the current leader, it will ask the PD
for the new leader and update its cache.

### RawKV

### TransactionKV

## Placement driver

### Scheduler

<https://tikv.org/docs/5.1/reference/architecture/scheduling/>

The placement driver is responsible for adjusting which regions are on
which nodes to balance load.

When a region splits, the node notifies the placement driver. The
placement driver does not command nodes to split.

Merge is apparently not implemented yet.

### Routing table

The routing table maps ranges of keys to regions and their leader nodes.

``` example
<startkey1, endkey1> -> <region1, nodeA>
<startkey2, endkey2> -> <region2, nodeB>
<startkey3, endkey3> -> <region3, nodeC>
```

The routing table is stored in etcd. Nodes maintain heartbeats with the
PD, which contain region information. PD uses this information to keep
the routing table up-to-date. If the PD fails and a new one takes over,
the routing table might be out-of-date briefly, but it will be updated
within a few heartbeats.

Use epochs to guard against out-of-date info caused by network
partitions. Every time there is a configuration change (like a region
splitting), increase the epoch number. If the PD gets conflicting
information from two nodes, it checks the epoch number and uses the
highest of the two.

### Timestamp oracle

TiKV depends on a timestamp oracle to implement transactions. Timestamps
should be return in monotonically-increasing order. There should be more
than one PD to avoid a single point of failure here.

To scale well, the timestamp oracle periodically allocates a range of
timestamp by writing the highest allocated timestamp to persistent
storage (etcd) and then serving timestamps from memory.

Production environments typically have a raft group of PD nodes (I
think?), but even in that setting the timestamp oracle can be
problematic. If the raft leader fails, the system cannot allocate new
timestamps until there is a new leader

<https://pingcap.com/blog/Time-in-Distributed-Systems>

Alternatives:

-   Google TrueTime
-   Amazon Time Sync (EC2)
-   Hybrid Logical Clocks (I have not read about them yet)

## Consensus

### Raft

Reference links:

-   <https://pingcap.com/blog/implement-raft-in-rust>
-   <https://pingcap.com/blog/raft-in-tikv>
-   <https://pingcap.com/blog/design-and-implementation-of-multi-raft>
-   <https://github.com/tikv/tikv/tree/master/components/raftstore/src/store>

Multi-raft: data is sharded (each shard is a region) and replicated.
Each node is responsible for multiple data regions. Consensus for each
region is achieved by using the Raft protocol. Since each node is
hosting multiple regions, multi-raft is needed to support multiple
regions.

Raft metadata, raft log, and data in the state machine are stored in a
RocksDB instance. Use key prefixes to differentiate data types.

*Do key prefixes in RocksDB affect locality? They do in Spanner...*

### Optimizations

Reference links:

-   <https://pingcap.com/blog/optimizing-raft-in-tikv>
-   <https://pingcap.com/blog/lease-read>
-   <https://pingcap.com/blog/doubling-system-read-throughput-with-only-26-lines-of-code>

1.  Follower read

    In traditional Raft, all reads and writes are handled by the leader.
    This can present a scalability issue. Follower read allows reads to
    be serviced by up-to-date replicas.

    When the client sends a read request to a follower, the follower
    gets the latest committed log index from the leader. This involves
    an RPC, so latency to service the read request isn\'t terrific, but
    load is reduced on the server and throughput is increased.

    I wonder how the client knows to contact a follower? The routing
    table only contains leaders for each region.

2.  Batch

3.  Pipeline

4.  Asynchronous Apply

## TiKV node

Each TiKV node hosts a number of regions of the distributed key-value
store. Data is stored in RocksDB. A node actually has two RocksDB stores
-- one which stores all of the regions, and another for the Raft log.

In a given raft group, one node is designated as the leader. For
transactions involving multiple groups, there is a distributed
transaction layer above the raft group layer.

### Special features of RocksDB and their uses

1.  Prefix Bloom Filter

    Bloom filters are used for set membership. Does a key exist in a
    particular table?

    Prefix bloom filters are used to see if another key with the same
    prefix exists in a table. This is useful for multi-version
    concurrency control. In MVCC, the key is a concatenation of the row
    key and the timestamp. Thus, the row key can be used as a prefix for
    the prefix bloom filter.

2.  Table Properties

    Used for a few optimizations. Store the size of a table in its
    TableProperties -- this is useful for determining if a table needs
    to be split without scanning the entire table. Store MVCC statistics
    to help with garbage collection.

    If a region contains a lot of deleted entries (tombstones), do
    CompactRange on it.

3.  EventListener

    Listen to some special events, for example table compaction. Events
    trigger callbacks, and KvDB can update size information after a
    compaction.

4.  IngestExternalFile

    Generate an SST file and store it in RocksDB directly. When adding a
    new server, generate a snapshot file from another server and import
    it directly.

    Also useful for ingesting large amounts of data into TiKV without
    manually Put-ing it all.

5.  DeleteFilesInRange

    Delete tombstone regions and garbage collected tables. Apparently
    this breaks snapshots and should be used with caution.

## Regions

The goal is to provide the illusion of a single key-value store to the
client. Regions should be divided equitably amongst the available nodes.
By default, each region is replicated three times, to form a raft group.
Each node hosts multiple regions.

Consider how easy it is to add or remove nodes, given a sharding
strategy. It should be elastic.

### Sharding strategies

1.  Range

    Advantages:

    -   Split and merge are easy
    -   Range scan is easy
    -   LSM trees naturally store keys in-order

    Disadvantages:

    -   Sequential writes always write to the last node
    -   Hotspots potentially.

2.  Hash

    Advantages:

    -   Keys distributed randomly, so this results in an even load

    Disadvantages:

    -   Difficult to split, must re-hash (unless, consistent hashing?
        See Dynamo?)
    -   Range scan very hard since sequential keys are not stored next
        to each other

# References

<https://tikv.org/blog/building-distributed-storage-system-on-raft/>
<https://tikv.org/deep-dive/introduction/>
