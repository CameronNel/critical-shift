"""W17: access every container face, not merely the cell centerline."""
for name,y in [('RA01',5.5),('RA02',6.8),('RA03',8.1)]:bpy.data.objects[name].location=(-4.55,y,0)
# Tool/filter dry crates use a shallower 0.70m body. Preserve circular hardware
# and text proportions: move mount positions; reshape only spanning panels.
ratio=.70/.95
span_prefix=('Forklift box section','Tub lower pan','Tub floor','Sealed end panel','Folded lid','End lid gasket')
for name,y,rot in [('DR01',6.25,0),('DR02',7.35,math.pi)]:
    root=bpy.data.objects[name];members=[]
    for ob in SC.objects:
        a=ob.parent
        while a is not None and a!=root:a=a.parent
        if a==root:members.append(ob)
    for ob in members:
        ob.location.y*=ratio
        if ob.type=='MESH' and ob.name.startswith(span_prefix):
            for v in ob.data.vertices:v.co.y*=ratio
        if ob.type=='MESH' and ob.name.startswith('Wear at repeatedly handled edge'):
            for v in ob.data.vertices:v.co.y*=ratio
        if ob.type=='CURVE':
            for sp in ob.data.splines:
                if sp.type=='BEZIER':
                    for v in sp.bezier_points:v.co.y*=ratio;v.handle_left.y*=ratio;v.handle_right.y*=ratio
    root.location.y=y;root.rotation_euler.z=rot;root['body_dimensions_m']='2.15x0.70x1.10';root['access']='DR01 south face / DR02 north face; opposed service strips'
