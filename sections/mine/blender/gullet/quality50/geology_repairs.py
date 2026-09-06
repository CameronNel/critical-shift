"""Contact-settled ore and physically baked, independently removable rubble."""
import bpy,bmesh,math,random,json
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from geometry import mesh

def tree(objects):
    vv=[];ff=[]
    for o in objects:
        start=len(vv);vv.extend(o.matrix_world@v.co for v in o.data.vertices)
        ff.extend(tuple(start+i for i in p.vertices) for p in o.data.polygons)
    return BVHTree.FromPolygons(vv,ff,all_triangles=False) if ff else None

def footprint_samples(o):
    verts=[o.matrix_world@v.co for v in o.data.vertices]
    own=tree([o]);lo=Vector([min(v[i] for v in verts) for i in range(3)]);hi=Vector([max(v[i] for v in verts) for i in range(3)])
    points=[]
    for i in range(11):
        for j in range(11):
            x=lo.x+(hi.x-lo.x)*i/10;y=lo.y+(hi.y-lo.y)*j/10
            h=own.ray_cast(Vector((x,y,lo.z-.2)),Vector((0,0,1)),hi.z-lo.z+.4)
            if h[0] is not None:points.append(h[0])
    points.extend(verts)
    return points

def settle(o,support):
    if not support:return 0.
    points=footprint_samples(o);deltas=[]
    for p in points:
        hit=support.ray_cast(Vector((p.x,p.y,8)),Vector((0,0,-1)),15)
        if hit[0] is not None:deltas.append(hit[0].z-p.z)
    if not deltas:return 0.
    dz=max(deltas)+.0015;mat=o.matrix_world.copy();mat.translation.z+=dz;o.matrix_world=mat;bpy.context.view_layer.update()
    return dz

def fractured_shape(name,size,mat,seed):
    rng=random.Random(seed);L,W,H=size;vv=[]
    for z,r in [(-.45,1.),(-.08,1.05),(.48,.72)]:
        for i in range(7):
            a=i*math.tau/7+rng.uniform(-.08,.08)
            vv.append((math.cos(a)*L*.5*r*rng.uniform(.83,1.08),math.sin(a)*W*.5*r*rng.uniform(.83,1.08),H*(z+rng.uniform(-.06,.06))))
    bm=bmesh.new()
    for v in vv:bm.verts.new(v)
    bm.verts.ensure_lookup_table();bmesh.ops.convex_hull(bm,input=bm.verts[:],use_existing_faces=False)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);bm.verts.index_update()
    verts=[tuple(v.co) for v in bm.verts];faces=[tuple(v.index for v in f.verts) for f in bm.faces];bm.free()
    return mesh(name,verts,faces,mat)

def settle_resources(scene):
    floor=scene.objects.get('CSM_Excavated_floor');support=tree([floor]);report=[]
    config={'A':((-3.9,17.8),(-1,0),(0,3.6,7.,12.7)),'B':((3.9,33),(1,0),(0,3.7,7.1,12.4)),'C':((0,39.2),(0,1),(0,4.5,8.8,16.3))}
    for sec,(entry,axis,depths) in config.items():
        ax=Vector((*axis,0));side=Vector((-axis[1],axis[0],0))
        for stage in [1,2,3]:
            objects=sorted([o for o in scene.objects if o.type=='MESH' and o.get('csm_sector')==sec and o.get('csm_component')=='mineable_resource' and o.get('csm_min_stage')==stage],key=lambda o:o.name)
            for j,o in enumerate(objects):
                rows=math.ceil(len(objects)/2);dep=depths[stage-1]+.38+(depths[stage]-depths[stage-1]-.78)*(j//2)/max(rows-1,1)
                u=(-1 if j%2 else 1)*(.75+.12*stage)
                p=Vector((*entry,0))+ax*dep+side*u;p.z=-.025*max(p.y,0)+.35
                mat=o.matrix_world.copy();mat.translation=p;o.matrix_world=mat;bpy.context.view_layer.update();dz=settle(o,support)
                report.append({'object':o.name,'settled':True,'movement_z':dz})
    removed=[]
    for o in list(scene.objects):
        if o.type=='MESH' and '_Seam_shoulder' in o.name:
            removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
    return {'resources_settled':len(report),'details':report,'removed_intersecting_shoulder_dressing':removed}

def rebuild_collapse(scene,m):
    """A real 200-frame convex-body bake replaces the rejected hand-stacked pile."""
    config={'A':((-3.9,17.8),(-1,0),3,.77),'B':((3.9,33),(1,0),3,.80),'C':((0,39.2),(0,1),4,.91)}
    rocks=[];records=[];original_frame=scene.frame_current
    for o in bpy.context.selected_objects:o.select_set(False)
    scene.frame_set(1)
    def body(o,active):
        bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.rigidbody.object_add();o.select_set(False)
        rb=o.rigid_body;rb.type='ACTIVE' if active else 'PASSIVE';rb.collision_shape='CONVEX_HULL' if active else 'MESH'
        rb.friction=.91;rb.restitution=.015;rb.use_margin=True;rb.collision_margin=.0015
        if active:rb.mass=20;rb.linear_damping=.55;rb.angular_damping=.65
    supports=[scene.objects['CSM_Excavated_floor'],scene.objects['CSM_Continuous_stratified_mine_skin']]
    for o in supports:body(o,False)
    for sec,(entry,axis,nx,spacing) in config.items():
        ax=Vector((*axis,0));side=Vector((-axis[1],axis[0],0))
        roots=sorted([o for o in scene.objects if o.type=='EMPTY' and o.name.startswith(f'CSM_{sec}_Rubble_')],key=lambda o:o['csm_rubble_index'])
        assert len(roots)==22
        for i,root in enumerate(roots):
            for child in list(root.children_recursive):bpy.data.objects.remove(child,do_unlink=True)
            root.matrix_world=Matrix.Identity(4)
            if i<nx*3:
                col=i%nx;row=i//nx;u=(col-(nx-1)/2)*spacing;dep=.65+row*.80;zdrop=.63
            else:
                j=i-nx*3;columns=max(2,nx-1);u=(j%columns-(columns-1)/2)*spacing*.86;dep=.95+(j//columns)*.57;zdrop=1.48+(j//(columns*2))*.75
            center=Vector((*entry,0))+side*u+ax*dep;center.z=-.025*max(center.y,0)+zdrop
            rng=random.Random(9001+ord(sec)*100+i)
            shard=fractured_shape(f'{sec}_Removable_fracture_{i:02}',(rng.uniform(.80,1.22),rng.uniform(.70,1.02),rng.uniform(.37,.64)),m['rock'],9190+i+ord(sec)*10)
            shard.parent=root;shard.matrix_world=Matrix.Translation(center)@Matrix.Rotation(rng.uniform(-.70,.70),4,'Z')@Matrix.Rotation(rng.uniform(-.20,.20),4,'Y')
            shard['csm_meta']=root['csm_meta'];shard['csm_sector']=sec;shard['csm_collapse_only']=True;shard['csm_rubble_index']=i;shard['csm_component']='removable_rubble';shard['q50_fractured_block']=True
            bpy.context.view_layer.update();body(shard,True);rocks.append(shard)
    rw=scene.rigidbody_world;rw.substeps_per_frame=8;rw.solver_iterations=30;rw.point_cache.frame_start=1;rw.point_cache.frame_end=220
    scene.gravity=(0,0,-9.81)
    for frame in range(1,201):
        scene.frame_set(frame)
        if frame in [50,100,150,200]:print('RUBBLE_PHYSICS_FRAME',frame,flush=True)
    graph=bpy.context.evaluated_depsgraph_get();transforms={o.name:o.evaluated_get(graph).matrix_world.copy() for o in rocks}
    for o in rocks+supports:
        bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.rigidbody.object_remove();o.select_set(False)
    scene.frame_set(original_frame)
    for o in rocks:
        o.matrix_world=transforms[o.name];o['q50_contact_method']='200-frame Bullet convex-body settlement; baked pose'
        records.append({'object':o.name,'sector':o['csm_sector'],'index':o['csm_rubble_index'],'world_origin':list(o.matrix_world.translation),'method':'Blender Bullet convex-body settlement','frames':200,'collision_margin_m':.0015})
    bpy.context.view_layer.update()
    return records
