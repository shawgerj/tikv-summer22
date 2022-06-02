# Write-ahead Log and things

On a Write operation, how many times does a piece of data get persisted
before completing the operation? Hypothesis: it will be persisted in
both the Raft write-ahead log, and also the RocksDB write-ahead log.

## RPCs

Message types are defined in `kvproto/proto/kvrpcpb.proto`{.verbatim}.
RPCs are defined in `kvproto/proto/tikvpb.proto`{.verbatim}.

There are two interfaces for `Put`{.verbatim} requests.
Non-transactional and transactional.

Non-transactional:

-   `RawPut`{.verbatim}
-   `RawBatchPut`{.verbatim}

Transactional:

-   `KvPrewrite`{.verbatim}
-   `KvCommit`{.verbatim}
-   `KvTxnHeartBeat`{.verbatim}
-   `KvGC`{.verbatim}

These interfaces are all handled in
`tikv/src/server/service/kv.rs`{.verbatim}. Using `raw_put`{.verbatim}
as an example, the `RawPut`{.verbatim} rpc maps to
`raw_put()`{.verbatim} and the actual work is done in
`future_raw_put()`{.verbatim}. At this point, an Engine, LockManager,
and KvFormat are defined.

## Engines

From `storage/mod.rs`{.verbatim} -- \"When a TiKV server is running, a
RaftKV will be the underlying Engine of Storage. The other two types of
engine are for test purpose.\" So when `raw_put()`{.verbatim} is
executed in `storage/mod.rs`{.verbatim} and it calls
`engine.async_write()`{.verbatim}, need to look in
`src/server/raftkv.rs`{.verbatim} to find the correct
`async_write()`{.verbatim}.

Eventually commands are sent through the Raft router
`RaftStoreRouter`{.verbatim}. (In particular, a
`ServerRaftStoreRouter`{.verbatim}). At this point there isn\'t a
difference between executing raw or transactional commands. It will go
through the same control flow of raft protocol and persisting to
RocksDB.

`tikv/components/engine_traits/`{.verbatim}. Notice in
`options.rs`{.verbatim} there is a `WriteOptions`{.verbatim} struct,
which has `sync`{.verbatim} and `no_slowdown`{.verbatim} fields. It
looks like both are set to false on construction.

### Setting options in `raftstore`{.verbatim}

In raftstore, `src/store/peer.rs`{.verbatim} `set_sync`{.verbatim} is
set to `true`{.verbatim}. Same in
`src/store/async_io/write.rs`{.verbatim}. Also `true`{.verbatim} in
`src/store/fsm/store.rs`{.verbatim}. (Note: yes, but these are dealing
with destroy and recovery, not normal operation).

In `components/raftstore/src/store/fsm/apply.rs`{.verbatim},
`should_sync_log()`{.verbatim} appears to return `false`{.verbatim} if
it is an ordinary command. This is referring to the Raft log I believe.

In consume~andshrink~, sync~log~ is *always* passed as true. What are
the situations it could be false? `sync-log`{.verbatim} was removed as
an option in 5.0 and defaults to always true now.

I guess it makes sense raft apply wouldn\'t be syncing? I should be
looking at propose and commit. In `apply.rs`{.verbatim}, look at
`commit()`{.verbatim} and `commit_opt()`{.verbatim}. This will always
commit an entry persistently, using `write_to_db()`{.verbatim}.

## Transactions

<https://pingcap.com/blog/how-tikv-reads-and-writes#percolator> An
operation on a single region will be consistent due to Raft. But a
single operation on multiple regions needs transactions to ensure
consistency.

The timestamp oracle will provide the prewrite and commit timestamps.

### PreWrite

-   Write to the lock column
-   Write `key_prewriteTs = value`{.verbatim} to the data column

1.  Code

    There is a macro `txn_command_future`{.verbatim} in
    `src/server/service/kv.rs`{.verbatim}. It handles all the
    transaction commands

    -   prewrite
    -   acquire~pessimisticlock~
    -   pessimistic~rollback~
    -   batch~rollback~
    -   resolve~lock~
    -   commit
    -   cleanup
    -   txn~heartbeat~
    -   check~txnstatus~
    -   check~secondarylocks~
    -   mvcc~getbykey~
    -   mvcc~getbystartts~

    The key line is `storage.sched_txn_command()`{.verbatim}. It will
    match the command type to `Prewrite`{.verbatim},
    `PrewritePessimistic`{.verbatim}, or
    `AcquirePessimisticLock`{.verbatim}. Eventually,
    `self.sched.run_cmd()`{.verbatim}. `sched`{.verbatim} is a
    `TxnScheduler`{.verbatim}, which can be found in
    `tikv/src/storage/txn/scheduler.rs`{.verbatim}. Comments at the top
    of this file are good.

    The scheduler is always on the the region leader\'s store. (I wonder
    how follower reads are handled then...). Remember a region is
    replicated to many stores (here a \'store\' is just a single node
    and the regions it holds, all stored in an instance of RocksDB).

    The scheduler runs in a loop, but commands are executed by worker
    threads in a thread pool. Functions: `run_cmd`{.verbatim},
    `schedule_command`{.verbatim}, `execute`{.verbatim}. Notice in
    `schedule_command`{.verbatim} we acquire the latches for this
    transaction.

    The `execute`{.verbatim} function uses the snapshot and calls
    `process`{.verbatim} with both the snapshot and task. It will call
    `process_write`{.verbatim}. There is a variable here that signals
    whether or not the task can be pipelined. Look in
    `commands/`{.verbatim} to see all the types of commands and code for
    each of them. In this case, there is a `process_write`{.verbatim}
    function for Prewrite commands. Eventually we call
    `prewrite()`{.verbatim} in this file.

    The Raft part of this happens in `async_snapshot`{.verbatim} in
    `raftkv.rs`{.verbatim}. I need to learn more about Rust concurrency
    to understand exactly how this is being called, but the scheduler is
    generating a snapshot at the same time that it is processing the
    command.

    Once in `raftkv.rs`{.verbatim} the command will be executed using
    `RaftStoreRouter`{.verbatim}.

### Commit

-   Delete from the lock column
-   Write to the write column, `key_commitTs = prewriteTs`{.verbatim} (a
    pointer to the value written in the prewrite stage).

### Reads

-   Read the key. If a lock exists on the key, abort the read (another
    transaction in progress).
-   Find latest commit version in the write column
-   That column will have a pointer to the data for the key
    (`prewriteTs`{.verbatim}, as above). Search for
    `key_prewriteTs`{.verbatim} in the data column and read the value.

## Raft

### Helpful links

-   <https://developpaper.com/tikv-source-code-analysis-series-17-overview-of-raft-store/>
-   <https://dzone.com/articles/dive-deep-into-tikv-transactions-the-life-story-of>
-   <https://docs.pingcap.com/tidb/dev/tune-tikv-thread-performance#performance-tuning-for-tikv-thread-pools>

### Batch system

The batch system is used for multi-raft. There are two threads in the
batch system -- raftstore and apply. There are three phases:

1.  Collect messages Each member of the raft group is called a peer.
    Each peer has a mailbox, where incoming messages are stored. Since
    each peer is likely part of several raft groups, it will receive
    messages from all of them. Good functions to look at are
    `poll()`{.verbatim} in `batch-system/src/batch.rs`{.verbatim} and
    `handle_normal()`{.verbatim} in
    `raftstore/src/store/fsm/store.rs`{.verbatim}.
2.  Handle messages
3.  Process I/O For the apply thread, most of this is in
    `raftstore/src/store/fsm/apply.rs`{.verbatim}. Especially
    `handle_raft_committed_entries`{.verbatim}, fill up a WriteBatch,
    and `commit`{.verbatim} it to the RocksDB is a good code path to
    follow.

## Notes and changes

-   `tikv/components/raftstore/src/store/async_io/write.rs`{.verbatim}
    line 526 change true to false. Do not sync raft entries to disk.
    Call to `consume_and_shrink()`{.verbatim}.
-   `tikv/components/raftstore/src/store/fsm/apply.rs`{.verbatim} line
    506 change to false. Sync to RocksDB. `write_to_db()`{.verbatim}

Effects of the above changes: changing raft persistence makes a big
difference. Changing RocksDB persistence does not.

My hypothesis is that there are typically multiple entries to the raft
log for each WriteBatch of kv-pairs that gets persisted to RocksDB.
Considering the way messages are fetched from the mailbox and handled,
the system will read many committed messages at a time and persist them
all in a single batch. On the other hand, incoming write requests to the
primary have to be persisted much more frequently.

## Config options

<https://docs.pingcap.com/tidb/dev/tikv-configuration-file>

Further experimentation could involve changing some of the configuration
operations and seeing how the system behaves. For example
`cmd-batch`{.verbatim} turns batching on (default) and off. Turning it
off, or adjusting the size of batches could make it easier to reason
about how frequently data is persisted to disk.
