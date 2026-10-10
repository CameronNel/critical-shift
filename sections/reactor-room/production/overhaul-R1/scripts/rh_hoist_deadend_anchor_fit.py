"""Fit positive drum-end restraints and an inspectable hood aperture."""
import bpy,bmesh,json,math
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
import crk
import rh_support_registry as SUPPORT

KEY='rh_hoist_deadend_anchor_fit'
BODY='R2 crane trolley crane IRON'
HOOD='R2 crane trolley crane OLIVE'
ROPE='RH refine crane hoist rope rope CRANE_ROPE'

def apply(scene,objects,materials):
    if KEY in scene:return json.loads(scene[KEY])
    scene.frame_set(1);bpy.context.view_layer.update()
    body=objects[BODY];hood=objects[HOOD];rope=objects[ROPE]
    graph=bpy.context.evaluated_depsgraph_get()
    coll=bpy.data.collections.get('RH HOIST ANCHOR CORRECTION')
    assert coll is None,'Untracked previous anchor assembly'
    coll=bpy.data.collections.new('RH HOIST ANCHOR CORRECTION');scene.collection.children.link(coll)
    steel=objects['RH roof crossings washers GALV'].data.materials[0]
    temporary=[];created=[]

    def world_operand(original,label):
        evaluated=original.evaluated_get(graph)
        mesh=bpy.data.meshes.new_from_object(evaluated,depsgraph=graph)
        mesh.transform(original.matrix_world)
        obj=bpy.data.objects.new(label,mesh);coll.objects.link(obj);temporary.append(obj)
        return obj
    def box(name,x0,x1,y0,y1,z0,z1,ch=0):
        kit=crk.Kit();kit.bx(('part','METAL'),x0,x1,y0,y1,z0,z1,ch)
        obj=kit.build(coll,name,{'METAL':steel})[0];obj.name=name
        return obj
    def cylinder(name,x,y,z0,z1,r,segments=32):
        kit=crk.Kit();kit.cyl(('part','METAL'),x,y,z0,z1,r,segments,0)
        obj=kit.build(coll,name,{'METAL':steel})[0];obj.name=name
        return obj
    def difference(obj,cutter,label):
        bpy.context.view_layer.objects.active=obj;obj.select_set(True)
        modifier=obj.modifiers.new(label,'BOOLEAN');modifier.operation='DIFFERENCE'
        modifier.solver='EXACT';modifier.object=cutter
        modifier.use_self=False
        before=[obj.matrix_world@v.co for v in obj.data.vertices]
        bounds=[(min(p[i] for p in before),max(p[i] for p in before)) for i in range(3)]
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        obj.select_set(False)
        after=[obj.matrix_world@v.co for v in obj.data.vertices]
        assert after and all(lo-2e-5<=p[i]<=hi+2e-5 for p in after for i,(lo,hi) in enumerate(bounds)),(obj.name,label,'Boolean difference escaped original solid bounds')
    def remove(obj):
        mesh=obj.data;bpy.data.objects.remove(obj,do_unlink=True)
        if mesh.users==0:bpy.data.meshes.remove(mesh)
    def closed(obj):
        bm=bmesh.new();bm.from_mesh(obj.data)
        report={'object':obj.name,'vertices':len(bm.verts),'faces':len(bm.faces),
                'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
                'degenerate_faces':sum(f.calc_area()<1e-12 for f in bm.faces),
                'signed_volume_m3':bm.calc_volume(signed=True)}
        bm.free()
        assert not report['nonmanifold_edges'] and not report['degenerate_faces'] and report['signed_volume_m3']>0,report
        return report
    def attach(obj):
        obj.parent=body;obj.matrix_parent_inverse=body.matrix_world.inverted();created.append(obj)
    body_operand=world_operand(body,'TMP hoist drum fitting operand')
    # Each drum is built from separate closed primitive islands. Boolean
    # subtraction of the overlapping aggregate is not a valid solid operand.
    # Use its exact closed islands separately, preserving the authored seat.
    bm=bmesh.new();bm.from_mesh(body_operand.data)
    remaining=set(bm.verts);drum_parts=[]
    while remaining:
        seed=remaining.pop();component={seed};stack=[seed]
        while stack:
            v=stack.pop()
            for e in v.link_edges:
                w=e.other_vert(v)
                if w in remaining:remaining.remove(w);component.add(w);stack.append(w)
        low=[min(v.co[i] for v in component) for i in range(3)]
        high=[max(v.co[i] for v in component) for i in range(3)]
        if high[2]<16.070 or low[2]>16.118 or high[1]<4.744 or low[1]>4.816:continue
        vs=list(component);index={v:i for i,v in enumerate(vs)}
        faces={f for v in vs for f in v.link_faces}
        mesh=bpy.data.meshes.new('TMP exact drum island')
        mesh.from_pydata([tuple(v.co) for v in vs],[],[[index[v] for v in f.verts] for f in faces])
        local=bmesh.new();local.from_mesh(mesh);bmesh.ops.recalc_face_normals(local,faces=list(local.faces));local.to_mesh(mesh);local.free()
        part=bpy.data.objects.new('TMP exact drum island',mesh);coll.objects.link(part);temporary.append(part)
        closed(part);drum_parts.append((part,low,high))
    bm.free()
    vertices=[v.co.copy() for v in body_operand.data.vertices]
    tree=BVHTree.FromPolygons(vertices,[list(p.vertices) for p in body_operand.data.polygons],all_triangles=False)
    def drum_seat(x,y):
        point,normal,index,distance=tree.ray_cast(Vector((x,y,16.40)),Vector((0,0,-1)),.55)
        assert point is not None and 16.06<point.z<16.12,(x,y,point)
        return tuple(point)

    # The existing hood is retained with its rig and material. Only a bounded
    # lid aperture is cut; side guards, rim, mount points and controls stay.
    center=body.matrix_world.translation.x
    aperture=(center-.29,center+.29,4.69,4.91)
    cut=box('TMP hoist inspection aperture',*aperture,16.124,16.18)
    temporary.append(cut);difference(hood,cut,'Actual inspection aperture')
    topology=[closed(hood)]
    frame=box('RH hoist inspection aperture frame',aperture[0]-.012,aperture[1]+.012,
              aperture[2]-.012,aperture[3]+.012,16.160,16.164,.0005)
    difference(frame,cut,'Open inspection frame');topology.append(closed(frame));attach(frame)
    frame_anchors=[(x,y,16.160) for x in (aperture[0]-.006,aperture[1]+.006)
                   for y in (aperture[2]-.006,aperture[3]+.006)]
    SUPPORT.register('refinement props','hoist inspection rim',frame.name,hood.name,frame_anchors)
    units=[]
    for index,dx in enumerate((-.126,.114)):
        x=center+dx;y=4.780
        clamp=box('RH hoist drum end clamp '+str(index+1),x-.052,x+.052,4.744,4.816,16.070,16.118,.001)
        for part,low,high in drum_parts:
            if high[0]<x-.052 or low[0]>x+.052:continue
            difference(clamp,part,'Conformal exact drum island seat')
        # A clean 24 mm cylindrical rope saddle follows the terminal tangent;
        # the existing stranded cable is retained inside this relief.
        kit=crk.Kit();kit.cyly(('part','METAL'),x,4.72,4.84,16.092,.012,48)
        groove=kit.build(coll,'TMP wire rope terminal saddle',{'METAL':steel})[0]
        temporary.append(groove);closed(groove)
        difference(clamp,groove,'Wire-rope terminal saddle')
        bolt_rows=[]
        for side in (-1,1):
            bx=x+side*.033;by=y
            bore=cylinder('TMP hoist clamp bolt bore',bx,by,16.055,16.13,.0045)
            temporary.append(bore);difference(clamp,bore,'M8 clamp bolt clearance')
            seat=drum_seat(bx,by)
            shaft=cylinder('RH hoist anchor bolt shank '+str(index+1)+' '+str(side),bx,by,seat[2]-.008,16.120,.004,24)
            washer=cylinder('RH hoist anchor washer '+str(index+1)+' '+str(side),bx,by,16.118,16.120,.009)
            difference(washer,bore,'Washer clearance')
            head=cylinder('RH hoist anchor hex head '+str(index+1)+' '+str(side),bx,by,16.120,16.126,.0075,6)
            for obj in (shaft,washer,head):topology.append(closed(obj));attach(obj)
            SUPPORT.register('refinement props','hoist clamp washer '+str(index)+' '+str(side),washer.name,clamp.name,[(bx,by+.006,16.118)])
            SUPPORT.register('refinement props','hoist clamp head '+str(index)+' '+str(side),head.name,washer.name,[(bx,by+.006,16.120)])
            bolt_rows.append({'center_xy':[bx,by],'drum_seat':list(seat),'shaft_insertion_m':.008,'clearance_radius_m':.0045,'shaft_radius_m':.004})
        topology.append(closed(clamp));attach(clamp)
        anchors=[drum_seat(x+s*.044,yy) for s in (-1,1) for yy in (4.753,4.807)]
        for seat_index,anchor in enumerate(anchors):
            origin=Vector((anchor[0],anchor[1],16.40));point,normal,face,distance=tree.ray_cast(origin,Vector((0,0,-1)),.55)
            SUPPORT.register('refinement props','hoist rope dead-end clamp '+str(index+1)+' seat '+str(seat_index),clamp.name,body.name,[anchor],tuple(-normal))
        units.append({'clamp':clamp.name,'rope_cap_xyz':[x,4.8,16.092],'drum_contact_anchors':anchors,'bolts':bolt_rows})
    for obj in temporary:remove(obj)
    bpy.context.view_layer.update()
    report={'inspection_aperture_xy':list(aperture),'units':units,'topology':topology,
            'added_objects':sorted(o.name for o in created),'changed_retained_objects':[HOOD],
            'scope':'Two exact drum-island subtraction-fitted retaining blocks with tangent wire-rope saddles, four M8 bolt shanks/clearance bores/washers/hex heads, and a framed real hood-lid inspection opening. Eight-millimetre shank insertion represents intentional threaded attachment. Drum, rope, rig transforms/drivers, lights and camera data are retained. All new parts follow the retained trolley body; temporary Boolean operands are removed. Full technical and independent rendered acceptance remain required.',
            'art_acceptance':False}
    scene[KEY]=json.dumps(report,sort_keys=True)
    return json.loads(scene[KEY])
