import sys
from zplot import *

ctype = 'pdf' if len(sys.argv) < 2 else sys.argv[1]
c = canvas(ctype, title='rocksdb-ycsb-load-a-throughput-kops', dimensions=['6.5in', '5in'])

t_rocksdb = table(file='./attempt3_results')
t_rocksdb_nowal = table(file='./attempt3_results_nowal')

d = drawable(canvas=c, xrange=[64, 2048], yrange=[0, 125], xscale='log2', yscale='linear',
             coord=['0.6in', '0.6in'], dimensions=['5.7in', '4in'])

axis(drawable=d, title='RocksDB YCSB Load A - Throughput and Stall Percentage', style='x', xtitle='Value size (Bytes)',
     xmanual=[['64', 64], ['128', 128], ['256', 256], ['512', 512], ['1024', 1024], ['2048', 2048]])

axis(drawable=d, ytitle='Throughput (Kops / sec)', style='y', yauto=['','',25])
axis(drawable=d, style='y', yaxisposition='2048', ytitle='Stall Percentage', linedash=[2,2], ymanual=[['10', 12.5], ['20', 25], ['30', 37.5], ['40', 50], ['50', 62.5], ['60', 75], ['70', 87.5], ['80', 100], ['90', 112.5], ['100', 125]])

p = plotter()
L = legend()

t_rocksdb.update(set='throughput_ops = throughput_ops / 1000.0')
t_rocksdb_nowal.update(set='throughput_ops = throughput_ops / 1000.0')
t_rocksdb.update(set='stall_percentage = stall_percentage * 1.25')
t_rocksdb_nowal.update(set='stall_percentage = stall_percentage * 1.25')


# operations per second
p.line(drawable=d, table=t_rocksdb, xfield='value_size', 
               yfield='throughput_ops', linecolor='red', linewidth='1.0', legend=L,
               legendtext='RocksDB')
p.line(drawable=d, table=t_rocksdb_nowal, xfield='value_size', 
               yfield='throughput_ops', linecolor='blue', linewidth='1.0', legend=L,
               legendtext='RocksDB-NoWAL')

# megabytes per second
p.line(drawable=d, table=t_rocksdb, xfield='value_size', 
       yfield='stall_percentage', linecolor='red', linewidth='1.0', linedash=[2,2], legend=L,
       legendtext='Stall\%')
p.line(drawable=d, table=t_rocksdb_nowal, xfield='value_size',  
       yfield='stall_percentage', linecolor='blue', linewidth='1.0', linedash=[2,2], legend=L,
       legendtext='Stall\%-NoWAL')


L.draw(canvas=c, coord=d.map([70,50]), down=True, width=15, height=15)

c.render()
