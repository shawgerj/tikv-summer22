import sys
from zplot import *

ctype = 'pdf' if len(sys.argv) < 2 else sys.argv[1]
c = canvas(ctype, title='ycsb-A-throughput', dimensions=['6.5in', '5in'])

t_tikv = table(file='../default/a/throughput.txt')

d = drawable(canvas=c, xrange=[5, 120], yrange=[0, 12000], yscale='linear',
             coord=['0.7in', '0.6in'], dimensions=['5.7in', '4in'])

axis(drawable=d, title='YCSB Workload A - Throughput',
     xtitle='Num. Threads', ytitle='Throughput (ops / sec)')

p = plotter()
L = legend()

p.line(drawable=d, table=t_tikv, xfield='threads', 
               yfield='ops_sec', linecolor='black', linewidth='1.0', legend=L,
               legendtext='TiKV')


L.draw(canvas=c, coord=d.map([11,11000]), down=True, width=15, height=15)

c.render()