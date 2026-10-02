"""Remodel the parked leaves and vision trim around actual through apertures."""
import bmesh
k.collection('Door construction')
glass=k.material('Wired vision glass',(.78,.85,.82),.14,0,.000006)
bs=glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=.96;bs.inputs['IOR'].default_value=1.47
bs.inputs['Coat Weight'].default_value=.16;bs.inputs['Coat Roughness'].default_value=.11
def worldbounds(o):
    vs=[o.matrix_world@Vector(v) for v in o.bound_box]
    return Vector(tuple(min(p[i] for p in vs) for i in range(3))),Vector(tuple(max(p[i] for p in vs) for i in range(3)))
def aperture(o,inner):
    lo,hi=worldbounds(o);x0,x1,z0,z1=inner;rows=[];bm=bmesh.new()
    for y in [lo.y,hi.y]:
        for corners in [[(lo.x,lo.z),(hi.x,lo.z),(hi.x,hi.z),(lo.x,hi.z)],[(x0,z0),(x1,z0),(x1,z1),(x0,z1)]]:
            rows.append([bm.verts.new((x,y,z)) for x,z in corners])
    for i in range(4):
        j=(i+1)%4
        for ra,rb in [(0,1),(2,3),(0,2),(1,3)]:bm.faces.new((rows[ra][i],rows[ra][j],rows[rb][j],rows[rb][i]))
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bmesh.ops.bevel(bm,geom=list(bm.edges),offset=.0015,segments=2,affect='EDGES',clamp_overlap=True)
    inverse=o.matrix_world.inverted()
    for v in bm.verts:v.co=inverse@v.co
    me=bpy.data.meshes.new(o.data.name+' actual vision opening');bm.to_mesh(me);bm.free()
    for mat in o.data.materials:me.materials.append(mat)
    o.data=me;o['electrical_remodelled']='Vision aperture; original matrix and outside bounds preserved'
for leaf in [o for o in bpy.data.objects if o.name.startswith('Parked sliding leaf')]:
    lo,hi=worldbounds(leaf);cx=(lo.x+hi.x)/2;cy=(lo.y+hi.y)/2
    aperture(leaf,[cx-.232,cx+.232,1.823,2.077])
    member=leaf.get('assembly_member');target='Sliding door rail hood' if 'D01' in member else 'Sliding door rail hood.001'
    # Explicit suspension from the existing track, no floor-based floating exemption.
    k.root('Suspended door '+leaf.name,target,[[cx-.22,cy,2.85],[cx+.22,cy,2.85]],'WORLD_+Z')
    leaf['cs_assembly']=k.ASSEMBLY.name
    for dx in [-.22,.22]:
        hanger=k.box('Door track suspension strap',(cx+dx,cy,2.755),(.05,.026,.19),m['steel'],.002)
        matrix=hanger.matrix_world.copy();hanger.parent=leaf;hanger.matrix_world=matrix
        sign=1 if cy<1 else -1
        k.bolt('Door suspension fixing',(cx+dx,hi.y+.014 if sign>0 else lo.y-.014,2.625),(0,sign,0),m['steel'],.010)
    for trim in [o for o in bpy.data.objects if o.name.startswith('Door recessed vision trim')]:
        tlo,thi=worldbounds(trim);c=(tlo+thi)/2
        if abs(c.x-cx)<.02 and abs(c.y-cy)<.10:
            aperture(trim,[cx-.23,cx+.23,1.825,2.075]);trim['cs_assembly']=k.ASSEMBLY.name
    for pane in [o for o in bpy.data.objects if o.name.startswith('Door wired vision glass')]:
        plo,phi=worldbounds(pane);c=(plo+phi)/2
        if abs(c.x-cx)<.02 and abs(c.y-cy)<.12:
            pane.data.materials.clear();pane.data.materials.append(glass);pane['cs_assembly']=k.ASSEMBLY.name
            for slot in pane.material_slots:slot.material=glass
            for face in pane.data.polygons:face.use_smooth=False
            # Wire is embedded at mid-thickness, never proud of the pane surface.
            y=c.y;sign=1 if cy<1 else -1
            for wire in [o for o in bpy.data.objects if o.name.startswith('Vision glass wire')]:
                wlo,whi=worldbounds(wire);wc=(wlo+whi)/2
                if abs(wc.x-cx)<.23 and abs(wc.y-c.y)<.02:
                    # Only a measured7mm depth shift. All other wire dimensions,
                    # the object matrix and the contracted outside leaf stay fixed.
                    shift=Vector((0,-sign*.007,0))
                    local=wire.matrix_world.to_3x3().inverted()@shift
                    wire.data=wire.data.copy();wire.data.transform(Matrix.Translation(local))
                    wire['electrical_embedded_wire']=pane.name;wire['cs_assembly']=k.ASSEMBLY.name
            for z in [1.86,1.92,1.98,2.04]:k.cyl('Vision embedded transverse wire',(cx-.225,y+.0003,z),(cx+.225,y+.0003,z),.0007,m['steel'],8)
            sign=1 if cy<1 else -1
            for dx in [-.246,.246]:
                k.box('Vision glazing seated bead',(cx+dx,c.y+sign*.0055,1.95),(.012,.005,.276),m['zinc'],.001)
                for z in [1.84,2.06]:k.bolt('Vision bead captive fixing',(cx+dx,c.y+sign*.008,z),(0,sign,0),m['steel'],.004)
    sign=1 if cy<1 else -1
    for x in [lo.x+.065,hi.x-.065]:
        k.box('Door face folded vertical return',(x,hi.y+.007 if sign>0 else lo.y-.007,1.34),(.045,.014,2.55),m['slate'],.003)
    k.box('Door lower folded seam',(cx,hi.y+.009 if sign>0 else lo.y-.009,.55),(1.13,.018,.022),m['zinc'],.003)
