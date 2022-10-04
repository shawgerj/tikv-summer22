import sys
from zplot import *

ctype = 'pdf' if len(sys.argv) < 2 else sys.argv[1]
c = canvas(ctype, title='tikv-ycsb-load-a-latency', dimensions=['6.5in', '5in'])

t_tikv_default = table(file='./tikv_load_default')
t_tikv_nowal = table(file='./tikv_load_nowal_noflush')

d = drawable(canvas=c, xrange=[64, 512], yrange=[0, 54], xscale='log10',
             yscale='linear', coord=['0.6in', '0.6in'], dimensions=['5.7in', '4in'])

axis(drawable=d, title='TiKV YCSB Load A - Write Latency Avg. and 99%', style='x',
     xtitle='Value Size', xmanual=[['64', 64], ['128', 128], ['256', 256], ['512', 512]])

axis(drawable=d, ytitle='Write latency (ms)', style='y', yauto=['','',6])

p = plotter()
L = legend()

t_tikv_default.update(set='avg_write_us = avg_write_us / 1000.0')
t_tikv_nowal.update(set='avg_write_us = avg_write_us / 1000.0')
t_tikv_default.update(set='p99_write_us = p99_write_us / 1000.0')
t_tikv_nowal.update(set='p99_write_us = p99_write_us / 1000.0')

p.line(drawable=d, table=t_tikv_default, xfield='value_size', 
               yfield='avg_write_us', linecolor='red', legend=L, legendtext='TiKV')
p.line(drawable=d, table=t_tikv_nowal, xfield='value_size', 
               yfield='avg_write_us', linecolor='blue', legend=L, legendtext='TiKV-NoWAL')
p.line(drawable=d, table=t_tikv_default, xfield='value_size', linedash=[2,2],
               yfield='p99_write_us', linecolor='red', legend=L, legendtext='TiKV 99%')
p.line(drawable=d, table=t_tikv_nowal, xfield='value_size', linedash=[2,2],
               yfield='p99_write_us', linecolor='blue', legend=L, legendtext='TiKV-NoWAL 99%')

L.draw(canvas=c, coord=d.map([75, 50]), down=True, width=15, height=15)

c.render()
