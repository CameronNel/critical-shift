"""Targeted, repeatable wayfinding correction; preserves unrelated live geometry."""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector, Matrix

def apply_wayfinding():
    scene=bpy.context.scene
    specs=[
        ('East_reactor_route',(16.4,9.92),-math.pi/2,'F02','REACTOR','FUEL TRANSFER',-1),
        ('Bypass_clean_route',(.18,21),0,'S02','CLEAN','MEDICAL / COMPLIANCE',1),
        ('Plant_branch_identity',(-1.5,19.5),math.pi/2,'S01','PLANT','TURBINE / ELECTRICAL',-1),
        ('Delivery_reactor_identity',(12,16.4),math.pi/2,'F02','REACTOR','FREIGHT APPROACH',1),
        ('Clean_leg_identity',(9.65,21),0,'S02','CLEAN','MEDICAL / COMPLIANCE',-1),
        ('Waste_marker',(16.4,13.5),-math.pi/2,'S03','WASTE','WASTE TRANSFER',-1),
        ('Entry_marker',(-2.2,3),math.pi/2,'F01','REFINERY','FUEL ASSEMBLY',-1),
    ]
    # The central turn board already gives the reactor direction. A second
    # foreground board competed with it in the freight approach.
    redundant=bpy.data.objects.get('Cross_service_identity')
    if redundant:
        for ob in list(redundant.children_recursive):bpy.data.objects.remove(ob,do_unlink=True)
        bpy.data.objects.remove(redundant,do_unlink=True)
    for name,origin,heading,code,title,subtitle,direction in specs:
        old=bpy.data.objects.get(name)
        col=old.users_collection[0] if old else scene.collection
        if old:
            for obj in list(old.children_recursive):bpy.data.objects.remove(obj,do_unlink=True)
            bpy.data.objects.remove(old,do_unlink=True)
        root=bpy.data.objects.new(name,None);col.objects.link(root)
        root['wayfinding_code']=code;root['wayfinding_revision']='walk02'
        root['component_role']='wall_wayfinding_panel'
        u=Vector((math.cos(heading),math.sin(heading),0));n=Vector((math.sin(heading),-math.cos(heading),0))
        base=Vector((*origin,0))
        def point(x,d,z):return base+u*x+n*d+Vector((0,0,z))
        def mesh(suffix,vertices,faces,material,decal=False):
            me=bpy.data.meshes.new(name+suffix);me.from_pydata(vertices,[],faces);me.update()
            ob=bpy.data.objects.new(name+suffix,me);col.objects.link(ob);ob.parent=root
            me.materials.append(bpy.data.materials[material]);ob['surface_decal']=decal
            ob['collision_handoff']='visual_only' if decal else 'static_evaluated_geometry'
            ob['wayfinding_normal']=list(n)
            return ob
        def box(suffix,x,d,z,w,depth,h,material):
            vv=[point(x+sx*w/2,d+sy*depth/2,z+sz*h/2) for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
            ob=mesh(suffix,vv,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],material)
            mod=ob.modifiers.new('Pressed edge','BEVEL');mod.width=min(.003,min(w,depth,h)*.24);mod.segments=2
            return ob
        box('_backing',0,.220,1.99,1.65,.024,1.10,'ivory')
        box('_lower_trim',0,.235,1.475,1.59,.006,.035,'ochre')
        # Solid stand-offs bridge the existing recessed wall face and steel posts.
        for x in [-.65,.65]:
            for z in [1.59,2.39]:
                box('_stand_off',x,.10,z,.05,.22,.05,'steel')
                box('_mount_foot',x,.004,z,.11,.020,.11,'steel')
                box('_fastener',x,.241,z,.025,.016,.025,'darksteel')
        def text(suffix,body,x,z,size):
            cu=bpy.data.curves.new(name+suffix,'FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.offset=.0025 if suffix in ['_number','_title'] else .0005
            ob=bpy.data.objects.new(name+suffix,cu);col.objects.link(ob);ob.parent=root
            ob.location=point(x,.2335,z);ob.rotation_euler=(math.pi/2,0,heading);cu.materials.append(bpy.data.materials['teal'])
            ob['surface_decal']=True;ob['wayfinding_code']=code
            return ob
        text('_number',code,-direction*.09,2.11,.40)
        text('_title',title,0,1.85,.245)
        text('_subtitle',subtitle,0,1.65,.105)
        x=direction*.62
        pts=[(-.065,-.11),(.005,-.11),(.10,0),(.005,.11),(-.065,.11),(.025,0)]
        mesh('_chevron',[point(x+direction*dx,.2335,2.26+dz) for dx,dz in pts],[(0,1,2,3,4,5)],'ochre',True)
    codes={'REFINERY_BOUNDARY':('F01','REFINERY'),'REACTOR_BOUNDARY':('F02','REACTOR'),'PLANT_PORT':('S01','PLANT'),'CLEAN_PORT':('S02','CLEAN'),'WASTE_PORT':('S03','WASTE')}
    for ob in scene.objects:
        if ob.type!='FONT':continue
        for prefix,(code,title) in codes.items():
            if not ob.name.startswith(prefix):continue
            if '_leaf_access_type' in ob.name and ob.data.body in ['FC / 04','R-01']:ob.data.body=code
            if '_leaf_serial_type' in ob.name:
                side='L' if ' / L' in ob.data.body else 'R'
                ob.data.body=code+' / '+side+'\nINSPECT 07-B'
            if ob.name==prefix+'_type':ob.data.body=code+' / '+title
            if '_leaf_identity_text' in ob.name and ob.data.body in ['FUEL','PLANT','SERVICES','CLEAN','MEDICAL','WASTE','TRANSFER','REFINERY','REACTOR']:
                # Only primary identity labels; secondary TRANSFER remains a subtitle.
                if ob.name in [prefix+'_leaf_identity_text',prefix+'_leaf_identity_text.002']:
                    is_left=ob.parent and 'LEFT' in ob.parent.name
                    ob.data.body=code if is_left else title;ob.data.size=.245;ob.data.offset=.0035
                    if prefix!='REACTOR_BOUNDARY':
                        matrix=ob.matrix_world.copy();matrix.translation.z=.83;ob.matrix_world=matrix
        if ob.name=='Bay_identity_number':ob.data.body='BAY A';ob.data.size=.08;ob['wayfinding_note']='Staging bay A, not a destination code'
        if ob.name=='FREIGHT_GATE_type':ob.data.body='FG01 / FREIGHT'
        if ob.name=='REACTOR_BOUNDARY_type':
            ob.data.materials.clear();ob.data.materials.append(bpy.data.materials['ink']);ob.data.offset=.002
    bpy.data.objects['REACTOR_BOUNDARY_direction_panel'].data.materials[0]=bpy.data.materials['ivory']
    # Preserve the verified saved label's upright face and position explicitly.
    bpy.context.view_layer.update()
    ob=bpy.data.objects['Service_air_station_label']
    ob.matrix_world=Matrix(((0,0,1,-1.398),(1,0,0,15),(0,1,0,2.245),(0,0,0,1)))
    bpy.data.objects['Spare_parts_case_identity_plate'].matrix_world=Matrix.Translation(Vector((-1.6425,10.81,.3306)))@Matrix.Rotation(math.pi/2,4,'Z')
    bpy.data.objects['Spare_parts_case_kit_type'].matrix_world=Matrix.Translation(Vector((-1.6395,10.81,.32485)))@Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Rotation(math.pi/2,4,'X')
    for prefix,code in [('Bench_tool_case','TK-01'),('Consumables_drawer','TK-02'),('Spare_parts_case','TK-03')]:bpy.data.objects[prefix+'_kit_type'].data.body=code
    for name,body in [('Plant_blade_destination','S01 / PLANT'),('Clean_blade_destination','S02 / CLEAN')]:
        ob=bpy.data.objects[name];ob.data.body=body;ob.data.size=.115
    for prefix,code in [('East_distribution','E-01'),('Bypass_isolation','E-02'),('Clean_distribution','E-03')]:bpy.data.objects[prefix+'_identity'].data.body=code
    scene['wayfinding_revision']='walk02'
    scene['wayfinding_source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    bpy.context.view_layer.update()
    register_panel_supports()
    print(json.dumps({'wayfinding_revision':'walk02','replaced_panels':len(specs),'objects':len(scene.objects)}))

def register_panel_supports():
    """Bind every mounting foot to a measured non-panel support surface.

    Independent validation still checks signed gap, own surface contact, normals,
    architecture grounding and connectivity of all assembly members.
    """
    from mathutils.bvhtree import BVHTree
    scene=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
    panels=[o for o in scene.objects if o.get('component_role')=='wall_wayfinding_panel']
    excluded={x for p in panels for x in [p]+list(p.children_recursive)}
    vv=[];ff=[];owners=[]
    for ob in scene.objects:
        if ob.type!='MESH' or ob in excluded or ob.get('surface_decal'):continue
        ev=ob.evaluated_get(dg);me=ev.to_mesh();offset=len(vv)
        vv.extend(ev.matrix_world@v.co for v in me.vertices)
        ff.extend(tuple(offset+i for i in p.vertices) for p in me.polygons)
        owners.extend([ob.name]*len(me.polygons));ev.to_mesh_clear()
    tree=BVHTree.FromPolygons(vv,ff)
    for panel in panels:
        anchors=[];targets=[];directions=[]
        for foot in sorted((o for o in panel.children if '_mount_foot' in o.name),key=lambda o:o.name):
            center=sum((foot.matrix_world@Vector(v) for v in foot.bound_box),Vector())/8
            normal=Vector(foot['wayfinding_normal']).normalized()
            hit,_,index,distance=tree.ray_cast(center+normal*.05,-normal,.075)
            if hit is None:raise RuntimeError('No nearby physical support for '+foot.name)
            # Fit the physical foot and stand-off to the actual wall/pilaster face.
            # Old uniform feet penetrated recessed panels by 6 mm and missed
            # raised flanges by 14 mm; registration alone is insufficient.
            delta=hit+normal*.010-center
            inv=foot.matrix_world.inverted().to_3x3()
            for vertex in foot.data.vertices:vertex.co+=inv@delta
            suffix=foot.name.split('_mount_foot',1)[1]
            post=bpy.data.objects[panel.name+'_stand_off'+suffix]
            world=[post.matrix_world@v.co for v in post.data.vertices]
            low=min(v.dot(normal) for v in world)
            target=(hit+normal*.020).dot(normal)
            inverse=post.matrix_world.inverted()
            for vertex,position in zip(post.data.vertices,world):
                if position.dot(normal)<low+.001:
                    vertex.co=inverse@(position+normal*(target-position.dot(normal)))
            anchors.append(list(hit));targets.append(owners[index]);directions.append(list(-normal))
        assert len(anchors)==4,panel.name
        panel['support_required']=True;panel['assembly_role']='wall_sign'
        panel['support_anchors']=json.dumps(anchors);panel['support_targets']=json.dumps(targets)
        panel['support_direction']=directions[0];panel['support_directions']=json.dumps(directions)
        panel['support_max_gap']=.005;panel['support_max_penetration']=.002;panel['support_angle_tolerance']=12.
    bpy.context.view_layer.update()

if __name__=='__main__':apply_wayfinding()
