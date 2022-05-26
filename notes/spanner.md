# Spanner

Scalable, globally distributed database. Data is spread out in shards
all over the world. Use Paxos for replication. Reshard data across
machines as amount of data or number of machines changes. Also to
balance load handle failures.

Why replicate?

-   Global availability
-   Geographic locality

## Why not Bigtable?

-   Weak for complex, evolving schemas
-   Need strong consistency with wide-area replication

Desire for semirelational model (Megastore).

## Key features

-   Applications can control replication configurations for data
    -   Which datacenters contain data
    -   How far is data from users (read latency)
    -   How far are replicas from each other (write latency)
    -   How many replicas? (Availability, durability, read performance)
-   \"Externally consistent\" reads and writes
-   Globally consistent reads using a timestamp

Transactions have global timestamps, which determine the order of
serialization.

# Structure

## Universe

There are only a few of these. Test/playground, development/production,
and production.

## Zone

A universe is a set of zones. The zones are a set of locations across
which data can be replicated. Zones can be added or removed from a
running system.

-   Universemaster: console, status information
-   Placement driver: Automates movement of data across zones. Handles
    replication constraints, balance load, communicates with spanservers
    to do all of this.
-   Zonemaster. One master. Assigns data to spanservers.
-   Location proxy. Clients use the location proxies to find the right
    spanserver with their data.
-   Spanserver. 100s-1000s.

``` example
                 ┌──────────────────┐     ┌───────────────────┐
                 │  Universemaster  │     │ Placement driver  │
                 └──────────────────┘     └───────────────────┘
┌──────────────────┐    ┌──────────────────┐          ┌──────────────────┐
│Zone 1            │    │Zone 2            │          │Zone N            │
│                  │    │                  │          │                  │
│                  │    │                  │          │                  │
│  ┌──────────┐    │    │  ┌──────────┐    │          │  ┌──────────┐    │
│  │Zonemaster│    │    │  │Zonemaster│    │          │  │Zonemaster│    │
│  └──────────┘    │    │  └──────────┘    │          │  └──────────┘    │
│  ┌──────────┐    │    │  ┌──────────┐    │          │  ┌──────────┐    │
│  │ Location │    │    │  │ Location │    │          │  │ Location │    │
│  │  proxy   │    │    │  │  proxy   │    │  *****   │  │  proxy   │    │
│  └──────────┘    │    │  └──────────┘    │          │  └──────────┘    │
│                  │    │                  │          │                  │
│  ┌──────────┐    │    │  ┌──────────┐    │          │  ┌──────────┐    │
│  │┌─────────┴┐   │    │  │┌─────────┴┐   │          │  │┌─────────┴┐   │
│  └┤┌─────────┴┐  │    │  └┤┌─────────┴┐  │          │  └┤┌─────────┴┐  │
│   └┤spanserver│  │    │   └┤spanserver│  │          │   └┤spanserver│  │
│    └──────────┘  │    │    └──────────┘  │          │    └──────────┘  │
└──────────────────┘    └──────────────────┘          └──────────────────┘
```

## Paxos Group

``` example
      Other                                                         Other
      group ◀─────────────────Participant leader─────────────────▶  group
     leaders                 ┌───────┐ ┌───────┐                   leaders
                             │ Lock  │ │Tx     │
                             │ Table │ │Manager│
                             └───────┘ └───────┘
                                   Leader - 10sec lease
┌───────────────────┐       ┌───────────────────┐       ┌───────────────────┐
│Replica - Data     │       │Replica - Data     │       │Replica - Data     │
│Center A           │       │Center B           │       │Center C           │
│                   │       │                   │       │                   │
│ ┌────────────┐    │       │ ┌────────────┐    │       │ ┌────────────┐    │
│ │            │    │       │ │            │    │       │ │            │    │
│ │   Paxos    │    │       │ │   Paxos    │    │       │ │   Paxos    │    │
│ │            │    │       │ │            │    │       │ │            │    │
│ └────────────┘    │       │ └────────────┘    │       │ └────────────┘    │
│ ┌───────────┐     │◀─────▶│ ┌───────────┐     │◀─────▶│ ┌───────────┐     │
│ │┌──────────┴┐    │       │ │┌──────────┴┐    │       │ │┌──────────┴┐    │
│ └┤┌──────────┴┐   │       │ └┤┌──────────┴┐   │       │ └┤┌──────────┴┐   │
│  └┤Tablets    │   │       │  └┤Tablets    │   │       │  └┤Tablets    │   │
│   └───────────┘   │       │   └───────────┘   │       │   └───────────┘   │
│  ┌─────────────┐  │       │  ┌─────────────┐  │       │  ┌─────────────┐  │
│  │  Colossus   │  │       │  │  Colossus   │  │       │  │  Colossus   │  │
│  └─────────────┘  │       │  └─────────────┘  │       │  └─────────────┘  │
└───────────────────┘       └───────────────────┘       └───────────────────┘
```

## Spanserver

Each spanserver has 100-1000 tablets (similar to Bigtable tablet). A
tablet is a bag of (\<key,timestamp\> -\> string) mappings. Different
than bigtable - using timestamp as well as key.

Tablets are stored on Colossus.

Tablets are consistently replicated using Paxos state machines. There is
a Paxos state machine for each tablet. Writes are logged in *both* Paxos
log and tablet log (paper says this will be fixed in later version).
They use a leader system, with leader leases. Writes are initiated at
the leader, reads may be performed from any up-to-date replica.

### Paxos leader

There is a lock table which is used for concurrency control. Maps range
of keys to lock states.

Transactions involving only one group do not need to use the transaction
manager. The transaction manager which is used for implementing
transactions involving more than one Paxos group. Each group has a
\"participant leader\", and leaders from each gropu coordinate with
two-phase commit.

## Directories (Buckets)

A paxos group may manage multiple directories, in order to co-locate
groups of keys that tend to be accessed together. Locality.

An operation called **movedir** moves directories between Paxos groups.
It can also be used to add or remove replicas from a Paxos group. Load
balancing. It is a background process, does not block reads/writes. In
the background, move all but the last bit of data. After background work
completed, move the last data as a transaction.

### Control knobs

Replicas -- number, type, geographic placement

## TrueTime

Api:

``` example
TT.now()     -> TT interval
TT.after(t)  -> bool
TT.before(t) -> bool
```

Use GPS and atomic clocks to get a bound on *global* time, which may be
used to implement transactions, even between datacenters.

Each data center has several time master servers. Some are equipped with
GPS, and some are equipped with atomic clocks. Periodically, they
synchronize their clocks with each other (how?). Time daemons
synchronize with other daemons in other datacenters, both near and far.
Between synchronization, there is a drift rate assumed to be 200
usec/sec. Sync happens every 30 secs. Therefore uncertainty gradually
increases from 0 to 6ms between sync. Add 1ms for communication delay,
and the time uncertainty interval is generally between 1ms-7ms.

They show some evaluation results later in the paper with 90, 99, and
99.9 percentiles of the epsilon value. 99th percentile is less than 1ms.

Uncertainty can increase beyond the goal:

-   overloaded machine
-   network link issues
-   time-master availability.

These increases don\'t affect the correctness of spanner, but they will
slow the system down.

## Differences between Spanner and BigTable

-   Bigtable has single-row transactions. Spanner has multi-row
    transactions.
-   Bigtable is eventually consistent, spanner is externally consistent

## Transactions

Complex, read later.

# References

\"Spanner: Google\'s Globally-Distributed Database\", OSDI 2012
\"Bigtable: A Distributed Storage System for Structured Data\", OSDI
2006 \"Spanner, TrueTime, and the CAP Theorem\", Eric Brewer
