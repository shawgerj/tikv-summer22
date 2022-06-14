import sys
from zplot import *

ctype = 'pdf' if len(sys.argv) < 2 else sys.argv[1]
c = canvas(ctype, title='ycsb-A-9999-latency', dimensions=['6.5in', '5in'])

t_tikv = table(file='../default/a/9999_latency.txt')
t_tikv_nowal = table(file='../nowal/a/9999_latency.txt')

d = drawable(canvas=c, xrange=[5, 120], yrange=[0, 200000], yscale='linear',
             coord=['0.7in', '0.6in'], dimensions=['5.7in', '4in'])

axis(drawable=d, title='YCSB Workload A - 99.99% Update Latency',
     xtitle='Num. Threads', ytitle='Latency (us)')

p = plotter()
L = legend()

p.line(drawable=d, table=t_tikv, xfield='threads', 
               yfield='latency_us', linecolor='blue', linewidth='1.0', legend=L,
               legendtext='TiKV')
p.line(drawable=d, table=t_tikv_nowal, xfield='threads', 
               yfield='latency_us', linecolor='red', linewidth='1.0', legend=L,
               legendtext='TiKV-NoWAL')


L.draw(canvas=c, coord=d.map([95,25716]), down=True, width=15, height=15)

c.render()
