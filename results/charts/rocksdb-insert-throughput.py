import sys
from zplot import *

ctype = 'pdf' if len(sys.argv) < 2 else sys.argv[1]
c = canvas(ctype, title='rocksdb-insert-throughput', dimensions=['6.5in', '5in'])

t_rocksdb = table(file='../rocksdb_load/default/throughput.txt')
t_rocksdb_nowal = table(file='../rocksdb_load/disabled_wal/throughput.txt')

d = drawable(canvas=c, xrange=[5, 80], yrange=[24000, 44000], yscale='linear',
             coord=['0.7in', '0.6in'], dimensions=['5.7in', '4in'])

axis(drawable=d, title='YCSB LOAD A 100% Insertion - RocksDB Throughput',
     xtitle='Num. Threads', ytitle='Throughput (ops / sec)', xauto=['','',5], yauto=['','',2000])

p = plotter()
L = legend()

p.line(drawable=d, table=t_rocksdb, xfield='threads', 
               yfield='ops_sec', linecolor='blue', linewidth='1.0', legend=L,
               legendtext='RocksDB')
p.line(drawable=d, table=t_rocksdb_nowal, xfield='threads', 
               yfield='ops_sec', linecolor='red', linewidth='1.0', legend=L,
               legendtext='RocksDB-NoWAL')


L.draw(canvas=c, coord=d.map([60,28000]), down=True, width=15, height=15)

c.render()
