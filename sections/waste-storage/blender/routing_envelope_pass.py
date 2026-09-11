"""W21: constrain service-curve handles to their authored routing envelopes."""
for name in ['Vent isolator branch','Boundary power feeder','Inventory boundary data conduit']:
    ob=bpy.data.objects[name]
    for sp in ob.data.splines:
        if sp.type!='BEZIER':continue
        lo=[min(p.co[k] for p in sp.bezier_points) for k in range(3)];hi=[max(p.co[k] for p in sp.bezier_points) for k in range(3)]
        saved=[(p.handle_left.copy(),p.handle_right.copy()) for p in sp.bezier_points]
        for p,(left,right) in zip(sp.bezier_points,saved):
            p.handle_left_type='FREE';p.handle_right_type='FREE'
            for k in range(3):left[k]=max(lo[k],min(hi[k],left[k]));right[k]=max(lo[k],min(hi[k],right[k]))
            p.handle_left=left;p.handle_right=right
