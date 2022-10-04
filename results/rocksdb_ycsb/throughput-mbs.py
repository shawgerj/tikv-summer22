import sys
from zplot import *

ctype = 'pdf' if len(sys.argv) < 2 else sys.argv[1]
c = canvas(ctype, title='rocksdb-ycsb-load-a-throughput-mbs', dimensions=['6.5in', '5in'])

t_rocksdb = table(file='./attempt3_results')
t_rocksdb_nowal = table(file='./attempt3_results_nowal')

d = drawable(canvas=c, xrange=[64, 2048], yrange=[0, 35], xscale='log2', yscale='linear',
             coord=['0.6in', '0.6in'], dimensions=['5.7in', '4in'])

axis(drawable=d, title='RocksDB YCSB Load A - Throughput MB/sec', style='x', xtitle='Value size (Bytes)',
     xmanual=[['64', 64], ['128', 128], ['256', 256], ['512', 512], ['1024', 1024], ['2048', 2048]])

axis(drawable=d, ytitle='Throughput (MB / sec)', style='y', yauto=['','',5])

p = plotter()
L = legend()

# operations per second
p.line(drawable=d, table=t_rocksdb, xfield='value_size', 
               yfield='throughput_mbs', linecolor='red', linewidth='1.0', legend=L,
               legendtext='RocksDB')
p.line(drawable=d, table=t_rocksdb_nowal, xfield='value_size', 
               yfield='throughput_mbs', linecolor='blue', linewidth='1.0', legend=L,
               legendtext='RocksDB-NoWAL')

L.draw(canvas=c, coord=d.map([900,10]), down=True, width=15, height=15)

c.render()
