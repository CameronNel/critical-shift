"""Root-authored F18 repair functions recovered from this session after execution transport loss.
Pending: selected duct/pallet/UV studies passed in memory, but no full F18 native/build/render/review exists.
Append only through apply_pending_f18.py after reading the repo skills and current failure evidence.
Do not treat this file as visual acceptance or overwrite the original module/map.
"""

def tenth_clearance_cutter(subject, clearance=.008):
    """Actual evaluated solid plus a conservative world-space clearance hull."""
    dg=bpy.context.evaluated_depsgraph_get();ev=subject.evaluated_get(dg)
    me=ev.to_mesh();bm=bmesh.new()
    for v in me.vertices:
        p=ev.matrix_world@v.co
        for x in [-clearance,clearance]:
            for y in [-clearance,clearance]:
                for z in [-clearance,clearance]:bm.verts.new(p+Vector((x,y,z)))
    ev.to_mesh_clear()
    result=bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
    unused=[v for v in bm.verts if not v.link_faces]
    if unused:bmesh.ops.delete(bm,geom=unused,context='VERTS')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.verts.ensure_lookup_table();bm.verts.index_update()
    out=mesh('TEMP actual evaluated clearance hull',[tuple(v.co) for v in bm.verts],
             [tuple(v.index for v in f.verts) for f in bm.faces],'steel',0)
    bm.free();return out


def tenth_difference(o, cutter, reason):
    bpy.context.view_layer.objects.active=o
    for mod in list(o.modifiers):
        if mod.type=='BEVEL':bpy.ops.object.modifier_apply(modifier=mod.name)
        elif mod.type=='WEIGHTED_NORMAL':o.modifiers.remove(mod)
    mod=o.modifiers.new(reason,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
    bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.dissolve_limit(bm,angle_limit=1e-6,verts=list(bm.verts),edges=list(bm.edges),use_dissolve_boundaries=False,delimit={'MATERIAL'})
    bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='FIXED',ngon_method='EAR_CLIP')
    bmesh.ops.dissolve_degenerate(bm,dist=1e-6,edges=list(bm.edges))
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    o.data.update();uv(o)
    wn=o.modifiers.new('Manufactured relief return normals','WEIGHTED_NORMAL');wn.keep_sharp=True;wn.weight=40
    if o.name in ORIGINAL:EXCEPTIONS[o.name]=reason
    else:o['construction_repair']=reason


def tenth_review_repairs():
    use_root('CD | Main ventilation supply trunk suspension')
    duct=S.objects['Main ventilation supply trunk'];passages=[]
    for y in [2.2,5.2,8.2,11.2,13.9]:
        brace=S.objects['Truss diag B '+str(y)+'_0.8']
        tenth_difference(duct,tenth_clearance_cutter(brace,.008),
            'Actual sealed diagonal brace-passage returns;8mm conservative clearance, original duct envelope/pose and suspension retained')
        passages.append({'brace':brace.name,'clearance_m':.008})
    duct['actual_brace_passages']=json.dumps(passages)
    root=S.objects['CD | Warm Fluorescent SW suspended fixture']
    for o in list(S.objects):
        if o.parent==root and (o.name.startswith(('CD | Fixture suspension rod','CD | Fixture roof plate')) or o.get('contact_anchor')):
            p=o.matrix_world.translation.copy();p.x=-4.11
            world=o.matrix_world.copy();world.translation=p;o.matrix_world=world
    root['construction_repair']='New hangers/roof plates use reflector top atX-4.11, clear of return duct; original fixture/light poses retained'
    tenth_pallet_notch()
    use_root('Person Scanner Arch')
    for side in [-1,1]:
        column=S.objects['Scanner portal column '+str(side)]
        cut=profile('TEMP scanner formed service recess',octagon(.13,1.74,.045),.024,1,(side*.73,6.827,1.35),'steel',0)
        tenth_difference(column,cut,'Actual deep angular service-channel returns; retained optical pockets, crown, feet and inner aperture')
        plate=profile('CD | Scanner captive service shoe',octagon(.115,.34,.035),.003,1,(side*.73,6.8375,.70),'charcoal',0)
        plate['construction_contract']='Back bears on actual new service recess atY6.839; small access shoe inside original column envelope'
    use_root('G1 Cart Bypass Gate')
    for j in [1,2,3]:
        o=S.objects[f'G1 leaf {j} panel'];c=o.matrix_world.translation
        tenth_difference(o,profile('TEMP enlarged gate observation',octagon(.47,.18,.027),.12,1,(c.x,c.y,c.z+.585),'steel',0),
            'Clipped180mm observation opening with65mm+ retained top band; original panel pose/envelope/bay lands unchanged')
    use_root('CD | Check-in projecting locator')
    heading=S.objects['CD | Locator heading'];heading.data.body='01 / CHECK-IN';heading.data.size=.048
    heading.location=(-2.3515,3.018,2.638)
    txt('CD | Locator reverse heading','01 / CHECK-IN',(-2.380,3.505,2.638),.048,'ivory',rot=(pi/2,0,-pi/2))
    use_root('G1 Cart Bypass Gate')
    txt('CD | Cart mast operation','CARTS', (3.02,6.821,1.90),.063,'ivory',align='CENTER')
    txt('CD | Cart mast clearance','02 / HOLD', (3.02,6.821,1.84),.027,'ivory',align='CENTER')
    use_root('Checkin Counter Hatch')
    lip=profile('CD | Counter folded document handoff',
        [(-.32,0),(.32,0),(.32,.036),(.29,.058),(.26,.058),(.26,.013),(-.26,.013),(-.26,.058),(-.29,.058),(-.32,.036)],
        .035,1,(-3.51,2.9925,1.040),'steel',0)
    lip['construction_contract']='Folded handoff rail bottom bears on actual counter topZ1.040 inside existing reservation; original writing plane remains clear'
    txt('CD | Visitor document instruction','01 / DUTY CLEARANCE',(-3.51,2.9748,1.065),.033,'ink',align='CENTER')
    status=S.objects['CD | Transfer custody match'];status.data.body='HOLD';status.data.size=.058
    status.location=(-5.456,12.205,.558)
    secondary=S.objects['CD | Poster coercive line'];secondary.data.body='NO RELIEF\nNO RELEASE';secondary.data.size=.058
    S.objects['CD | Reassurance qualification'].data.body='RELIEF CANCELLED';S.objects['CD | Reassurance qualification'].data.size=.025
    warn=S.objects['CD | Docket warning'];warn.data.body='RELIEF CANCELLED';warn.data.size=.024
    S['tenth_review_repairs']='Actual brace-passage duct returns, rerouted new hanger bearings, notched pallet, deep scanner channels, observation windows, functional route identification, formed handoff rail and explicit interrupted custody'
    tenth_review_materials()


def tenth_pallet_notch():
    use_root('Transit Storage Stacks')
    pts=[(5.975,11.375),(6.604,11.375),(6.604,11.686),
         (6.725,11.686),(6.725,12.425),(5.975,12.425)]
    return replace('Transit pallet base 1',profile('TEMP notched transit pallet',pts,.12,2,(0,0,.06),'wood',0),
        'Actual closed6mm-clear pilaster/flange corner notch; original outside bounds, pose and floor bearing retained')


def tenth_review_materials():
    for key in ['cotton','fabric','seat canvas']:
        if key not in MATERIALS:continue
        m=MATERIALS[key]
        for node in m.node_tree.nodes:
            if node.type=='TEX_WAVE':node.inputs['Scale'].default_value=42 if node.bands_direction=='X' else 47
            if node.type=='BUMP':node.inputs['Distance'].default_value=.00035;node.inputs['Strength'].default_value=.20
    repaint_family('plaster',(.45,.39,.305),.92,.09)
    m=MATERIALS['glass'];n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF')
    geo=n.new('ShaderNodeNewGeometry');z=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],z.inputs[0])
    rough=n.new('ShaderNodeMapRange');rough.inputs['From Min'].default_value=.8;rough.inputs['From Max'].default_value=2.9
    rough.inputs['To Min'].default_value=.13;rough.inputs['To Max'].default_value=.035;l.new(z.outputs['Z'],rough.inputs['Value'])
    for link in list(bs.inputs['Roughness'].links):l.remove(link)
    l.new(rough.outputs[0],bs.inputs['Roughness']);m['finish_contract']='More handled lower glazing, clear upper transmission, original thickness/refraction retained'
    material_patch(MATERIALS['yellow'],(0,14.65,0),(3.8,1.0,.008),(.29,.23,.11),.40,False)


def tenth_review_lighting():
    for name,power in [('Office Task Fluorescent',17),('Office Rear Fluorescent',13),('Support Concealed Accent',19),
                       ('CD | Custody transfer practical',18),('CD | Custody floor reflected fill',7),
                       ('CD | Cargo inspection low bounce',8),('CD | Cargo practical roof bounce',41),('CD | Scanner practical roof bounce',45)]:
        lamp=S.objects[name];lamp.data.energy=power
    for name in ['Office Task Fluorescent','Office Rear Fluorescent','Support Concealed Accent']:
        lamp=S.objects[name];lamp.data.spread=1.12;lamp.data.size=.50;lamp.data.size_y=1.15;lamp.data.color=(.87,.85,.81)
    lamp=S.objects['CD | Custody floor reflected fill'];lamp.data.color=(.74,.81,.91);lamp.data.size=.85;lamp.data.size_y=.4
    lamp=S.objects['CD | Cargo inspection low bounce'];lamp.data.color=(.80,.85,.90);lamp.data.size=1.1;lamp.data.size_y=.55
    use_root('Arrival Gate P2')
    lamp=light('CD | Arrival reveal reflected fill',(-1.9,15.48,2.7),(0,15.7,1.3),10,(.80,.86,.94),.65,.22)
    reposition_parent(lamp,ASM)
    S['tenth_lighting_contract']='Restrained secondary warm pools; cool reflected cargo/custody separation and selective roof/reveal depth; global exposure/original light poses fixed'


def finish_tenth_review_uv():
    for o in S.objects:
        if o.type!='MESH' or o.name in {'Covered Trolley Draped Tarp','Chair seat cushion','Chair back lumbar','Chair back upper'}:continue
        cut=o.data.uv_layers.get('CD_Fabric_Cut_1m');physical=o.data.uv_layers.get('CD_Physical_1m')
        if cut is None or physical is None:continue
        changed=0
        for f in o.data.polygons:
            if abs(f.normal.z)<.90 or ('welt' in o.name.lower() or 'hem' in o.name.lower()):
                for li in f.loop_indices:cut.data[li].uv=physical.data[li].uv
                changed+=1
        if changed:o['narrow_fabric_return_charts']=changed
