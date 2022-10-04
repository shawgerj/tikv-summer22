import sys
from zplot import *

ctype = 'pdf' if len(sys.argv) < 2 else sys.argv[1]
c = canvas(ctype, title='rocksdb-ycsb-load-a-latency', dimensions=['6.5in', '5in'])

t_rocksdb = table(file='./attempt3_results')
t_rocksdb_nowal = table(file='./attempt3_results_nowal')

d = drawable(canvas=c, xrange=[64, 2048], yrange=[1, 3000], xscale='log2', yscale='log2',
             coord=['0.6in', '0.6in'], dimensions=['5.7in', '4in'])

axis(drawable=d, title='RocksDB YCSB Load A - Latency Avg. and 99\%', style='x', xtitle='Value size (Bytes)',
     xmanual=[['64', 64], ['128', 128], ['256', 256], ['512', 512], ['1024', 1024], ['2048', 2048]])

axis(drawable=d, ytitle='Latency (us)', style='y',
     ymanual=[['1', 1], ['4', 4], ['16', 16], ['64', 64], ['256', 256], ['1024', 1024]])

p = plotter()
L = legend()

# operations per second
p.line(drawable=d, table=t_rocksdb, xfield='value_size', 
               yfield='avg_write_us', linecolor='red', linewidth='1.0', legend=L,
               legendtext='RocksDB')
p.line(drawable=d, table=t_rocksdb_nowal, xfield='value_size', 
               yfield='avg_write_us', linecolor='blue', linewidth='1.0', legend=L,
               legendtext='RocksDB-NoWAL')

# megabytes per second
p.line(drawable=d, table=t_rocksdb, xfield='value_size', 
       yfield='p99_write_us', linecolor='red', linewidth='1.0', linedash=[2,2],
       legend=L, legendtext="99\% latency")
p.line(drawable=d, table=t_rocksdb_nowal, xfield='value_size', 
       yfield='p99_write_us', linecolor='blue', linewidth='1.0', linedash=[2,2],
       legend=L, legendtext="99\% latency NoWAL")


L.draw(canvas=c, coord=d.map([880,256]), down=True, width=15, height=15)

c.render()
