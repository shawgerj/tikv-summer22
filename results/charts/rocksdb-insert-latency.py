import sys
from zplot import *

ctype = 'pdf' if len(sys.argv) < 2 else sys.argv[1]
c = canvas(ctype, title='rocksdb-insert-latency', dimensions=['6.5in', '5in'])

t_rocksdb = table(file='../rocksdb_load/default/insert_latency.txt')
t_rocksdb_nowal = table(file='../rocksdb_load/disabled_wal/insert_latency.txt')

d = drawable(canvas=c, xrange=[5, 80], yrange=[0, 2200], yscale='linear',
             coord=['0.7in', '0.6in'], dimensions=['5.7in', '4in'])

axis(drawable=d, title='YCSB LOAD A 100% Insertion - RocksDB Latency',
     xtitle='Num. Threads', ytitle='Latency (us)', xauto=['','',5], yauto=['','',200])

p = plotter()
L = legend()

p.line(drawable=d, table=t_rocksdb, xfield='threads', 
               yfield='latency_us', linecolor='blue', linewidth='1.0', legend=L,
               legendtext='RocksDB')
p.line(drawable=d, table=t_rocksdb_nowal, xfield='threads', 
               yfield='latency_us', linecolor='red', linewidth='1.0', legend=L,
               legendtext='RocksDB-NoWAL')


L.draw(canvas=c, coord=d.map([60,300]), down=True, width=15, height=15)

c.render()
