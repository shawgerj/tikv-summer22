# Informed Prefetching and Caching

## Reactive vs proactive disk and buffer management

Typically, disk accesses are initiated in response to requests for data
(reactive). Proactive disk accesses can dramatically improve
performance.

Why proactive?

-   Take advantage of storage parallelism
-   File access performance is important
-   I/O intensive applications can provide hints about their future
    demands

### Storage parallelism

Some I/O workloads are parallel, and benefit from using multiple disks
(striping, etc.). To parallelize a typically sequential workload (e.g.
read a large file), prefetching is needed.

### File access and performance

CPUs are getting faster, but hard drive performance doesn\'t improve at
the same rate (this was in 1995... arguably a different situation now,
but the argument makes sense). The goal should be to decrease cache
misses, but this isn\'t always so easy because files grow along with the
size of the cache.

1.  Problems with asynchronous read? (Explicit prefetching)

    -   Amount to prefetch depends on the throughput of the application,
        which can change as system demands change
    -   Might eject useful data from file cache
    -   Might cost more in paging memory
    -   Even if one could carefully manage the above drawbacks, it would
        then be difficult to port the application to a different system.

### I/O Hints

Applications should provide hints about their future file accesses, and
the file system can use that information to exploit parallelism, manage
caches, and distribute buffers amongst different applications.

## Def: hints

*Disclosure*: a hint based on advance knowledge. For example, a file is
going to be read sequentially four times. Does not require any
understanding of system implementation, only program behavior.

*Advice*: for example, a file should be cached with a particular policy.
Requires some understanding of system implementation.

Advantages of disclosure:

-   No specific knowledge of system implementation. This also means that
    disclosure hints maintain correctness on different systems.
-   Evidence for policy decision, but not the policy decision itself.
-   Modularity (refer to file descriptors, not inodes, for example).
    Implied from first point.

Interface: there are four different forms of hints (choose one from each
list).

  File Specifier    Pattern Specifier
  ----------------- ----------------------------
  file name         sequential whole file
  file descriptor   list of \<offset, length\>

## Cost-benefit analysis

### Consumers and suppliers

Problem: how to allocate cache buffers. There are two buffer consumers:
demands which result in cache misses, and prefetches of hinted blocks.
There are two buffer suppliers: the LRU cache, and the cache of hinted
blocks.

The benefit/cost is decrease/increase in I/O service time. Thus, there
is a benefit in giving a buffer to a consumer, and a cost in taking a
buffer from a supplier. How should buffers be reallocated from suppliers
to consumers?

# References

\"Informed prefetching and caching\", CMU, SOSP 95
