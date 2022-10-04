import sys
from zplot import *

ctype = 'pdf' if len(sys.argv) < 2 else sys.argv[1]
c = canvas(ctype, title='tikv-ycsb-load-a-throughput-kops', dimensions=['6.5in', '5in'])

t_tikv_default = table(file='./tikv_load_default')
t_tikv_nowal = table(file='./tikv_load_nowal_noflush')


d = drawable(canvas=c, xrange=[64, 512], yrange=[0, 45], xscale='log2',
             yscale='linear', coord=['0.6in', '0.6in'], dimensions=['5.7in', '4in'])

axis(drawable=d, title='TiKV YCSB Load A - Throughput Kops/Sec', style='x',
     xtitle='Value Size (Bytes)',
     xmanual=[['64', 64], ['128', 128], ['256', 256], ['512', 512]])

axis(drawable=d, ytitle='Throughput (Kops / sec)', style='y', yauto=['','',5])

p = plotter()
L = legend()

t_tikv_default.update(set='throughput_ops = throughput_ops / 1000.0')
t_tikv_nowal.update(set='throughput_ops = throughput_ops / 1000.0')


# operations per second
p.line(drawable=d, table=t_tikv_default, xfield='value_size', yfield='throughput_ops',
       linecolor='red', legend=L, legendtext='TiKV')
p.line(drawable=d, table=t_tikv_nowal, xfield='value_size', yfield='throughput_ops',
       linecolor='blue', legend=L, legendtext='TiKV-NoWAL')

L.draw(canvas=c, coord=d.map([70,15]), down=True, width=15, height=15)

c.render()
