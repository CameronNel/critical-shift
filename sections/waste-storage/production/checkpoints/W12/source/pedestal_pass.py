"""W10: fixed pedestal remains aligned while the jib is parked at 45 degrees."""
p=bpy.data.objects['HJ01_HANDLING_JIB']
for o in p.children:
    if o.name.startswith('Anchored pedestal'):o.rotation_euler.z=-math.pi/4
    if o.name.startswith('Foundation stud'):
        x,y=o.location.x,o.location.y;o.location.x=(x+y)/math.sqrt(2);o.location.y=(-x+y)/math.sqrt(2)
