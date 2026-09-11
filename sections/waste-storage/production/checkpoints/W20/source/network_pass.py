"""W19: connected internal service paths to the owned capped boundary sockets."""
current='Ventilation'
for x in [-5.45,5.45]:
    for y in [6.6,11.2]:box('Extract drop sealed coupling',(x,y,3.80),(.38,.41,.06),'metal',bevel=.003)
current='Monitoring'
tube('Boundary power feeder',[(6.28,16.8,3.6),(5.9,16.8,3.6),(5.9,17.85,3.30),(-5.9,17.85,3.30)],.018,'rubber')
tube('Vent isolator branch',[(-3.42,17.85,3.30),(-3.42,15.50,3.30),(-3.42,15.50,1.05),(-3.42,15.65,.82)],.018,'rubber')
for x in [-5.5,-3.5,-1.5,.5,2.5,4.5]:box('Rear feeder wall clip',(x,17.925,3.30),(.06,.15,.085),'metal',bevel=.003)
for z in [1.1,2.2,3.2]:
    box('Isolator conduit clamp',(-3.42,15.53,z),(.07,.07,.05),'metal',bevel=.003)
# Upright branch carrier reaches the skid and supports the conduit clamps.
box('Isolator cable support upright',(-3.42,15.565,1.79),(.055,.025,3.05),'bus',bevel=.003)
box('Isolator upright skid cleat',(-3.42,15.64,.28),(.16,.20,.06),'metal',bevel=.004)
for side in [-1,1]:
    box('Cell monitoring feed junction',(side*5.92,17.60,3.43),(.16,.32,.25),'bus',bevel=.01)
    tube('Monitoring feed tap',[(side*5.90,17.85,3.30),(side*5.9,17.70,3.38)],.016,'rubber')
    box('Cell service termination',(side*5.92,3.60,3.43),(.16,.18,.25),'bus',bevel=.008)
tube('Inventory boundary data conduit',[(-6.28,1.2,2.8),(-5.94,1.2,2.8),(-5.94,1.2,.20),(-4.40,1.2,.20),(-4.40,1.2,.75),(-4.40,1.65,.75)],.014,'metal')
for z in [.6,1.5,2.5]:box('Data riser wall clip',(-5.97,1.2,z),(.06,.055,.05),'darkpaint',bevel=.003)
for x in [-5.4,-4.8,-4.4]:
    box('Under-desk conduit foot',(x,1.2,.015),(.12,.12,.03),'darkpaint',bevel=.003)
    beam('Under-desk conduit saddle',(x,1.2,.03),(x,1.2,.20),.025,'metal')
