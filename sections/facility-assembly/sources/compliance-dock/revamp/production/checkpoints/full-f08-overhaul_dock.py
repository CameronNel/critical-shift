"""Additive dock authoring. Root owns geometry; critics never author the room.

Extends recovered original construction helpers without executing their builder.
Always starts from current selected module. Frozen map/room/spawn bytes asserted.
"""
import argparse, ast, bmesh, bpy, hashlib, json, math, random, sys
from math import sin, cos, pi
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
PROD=ROOT/'revamp/production'
p=argparse.ArgumentParser();p.add_argument('--stage',choices=['slice','full'],default='slice');p.add_argument('--revision',default='s01')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);random.seed(8217)
protected=json.loads((PROD/'protected-inputs.json').read_text())
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
for rel,expected in protected.items():
    if sha(ROOT.parents[3]/rel)!=expected:raise RuntimeError('Changed protected input '+rel)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'module.blend'),load_ui=False)
S=bpy.context.scene;S.name='COMPLIANCE_EDIT_LOCAL'
BASE={o.name:{'matrix':[list(r) for r in o.matrix_world],'dimensions':list(o.dimensions)} for o in S.objects}
ORIGINAL=set(BASE);EXCEPTIONS={};COL=None;ASM=None;MATERIALS={};CONTACTS=[]
RECIPE_HASHES={name:sha(ROOT/name) for name in ['overhaul_dock.py','full_detail.py','full_repairs.py','render_dock.py'] if (ROOT/name).exists()}
old=ROOT/'revamp/reference-tooling/original_build_dock.py'
tree=ast.parse(old.read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef)]
exec(compile(ast.Module(body=defs,type_ignores=[]),str(old),'exec'),globals())
CONTACTS=json.loads(S['contact_assemblies'])
collection('09 Overhaul | '+a.stage)

def profile(name,pts,depth,axis,offset,mat,w=.003,block=False):
    other=[i for i in range(3) if i!=axis];verts=[]
    for d in [-depth/2,depth/2]:
        for q in pts:
            v=list(offset);v[axis]+=d;v[other[0]]+=q[0];v[other[1]]+=q[1];verts.append(v)
    n=len(pts);faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    o=mesh(name,verts,faces,mat,w,block)
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    return o

def uv(o):
    if o.type!='MESH':return
    layer=o.data.uv_layers.get('CD_Physical_1m') or o.data.uv_layers.new(name='CD_Physical_1m')
    for f in o.data.polygons:
        # Orthonormal chart in the actual face plane, including sloped caps.
        # Every edge has its real metric length. Seams/repeat overlaps are
        # intentional and this is not a bake/lightmap atlas.
        normal=f.normal.normalized();ref=Vector((0,0,1)) if abs(normal.z)<.95 else Vector((1,0,0))
        tangent=(ref-normal*ref.dot(normal)).normalized();bitangent=normal.cross(tangent).normalized()
        for li in f.loop_indices:
            q=o.data.vertices[o.data.loops[li].vertex_index].co
            layer.data[li].uv=(q.dot(tangent),q.dot(bitangent))
    o['overhaul_surface']=True;o['uv_contract']='CD_Physical_1m; metric orthonormal face charts; intentional seams/repeats; not a lightmap'

spawn=json.loads((PROD/'spawn-input.json').read_text());colors={}
for m in spawn['materials']:
    if m['name'].startswith('COZY'):colors[m['name'].split('_')[1]]=m['Base Color'][:3]
def surface(key,color,rough,metal=0,variation=.025,bump=.00015):
    m=bpy.data.materials.new('CD | '+key);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
    bs.inputs['Specular IOR Level'].default_value=.3 if metal<.5 else .45
    n=m.node_tree.nodes;l=m.node_tree.links
    t=n.new('ShaderNodeUVMap');t.uv_map='CD_Physical_1m'
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1.7;noise.inputs['Detail'].default_value=2;l.new(t.outputs[0],noise.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color=(*(c*(1-variation) for c in color),1)
    ramp.color_ramp.elements[1].color=(*(min(1,c*(1+variation)) for c in color),1)
    l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],bs.inputs['Base Color'])
    rr=n.new('ShaderNodeMapRange');rr.inputs['To Min'].default_value=max(.02,rough-.045);rr.inputs['To Max'].default_value=min(1,rough+.045)
    l.new(noise.outputs['Fac'],rr.inputs[0]);l.new(rr.outputs[0],bs.inputs['Roughness'])
    if bump:
        fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=180;fine.inputs['Detail'].default_value=1
        l.new(t.outputs[0],fine.inputs['Vector']);b=n.new('ShaderNodeBump');b.inputs['Distance'].default_value=bump;b.inputs['Strength'].default_value=.25
        l.new(fine.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],bs.inputs['Normal'])
    MATERIALS[key]=m;m.diffuse_color=(*color,1);return m

surface('plaster',(.45,.42,.37),.9,variation=.10,bump=.0013)
surface('navy',colors['navy'],.71,bump=.0002)
surface('blue',colors['denim'],.62,.12,bump=.00012)
surface('charcoal',colors['charcoal'],.64,.15,bump=.00012)
surface('coral',[c*.58 for c in colors['coral']],.67,.08,variation=.075,bump=.00022)
surface('rubbed_coral',(.24,.13,.075),.57,.08,variation=.06,bump=.00012)
surface('plastic',(.046,.055,.066),.45,variation=.035,bump=.00005)
surface('linoleum',(.051,.058,.058),.85,variation=.07,bump=.00018)
surface('coffee',(.035,.018,.009),.55,variation=.03,bump=0)
surface('ivory',(.67,.63,.52),.68,.05)
surface('steel',colors['steel'],.39,.82,bump=.00006)
surface('brass',colors['brass'],.43,.82,bump=.00006)
surface('yellow',[c*.72 for c in colors['mustard']],.7,.05)
surface('rubber',(.018,.021,.025),.92,variation=.06,bump=.0005)
surface('paper',(.78,.72,.58),.96,variation=.015,bump=.00003)
surface('ink',colors['ink'],.94,bump=0)
surface('wood',[c*.65 for c in colors['walnut']],.76,variation=.08,bump=.0002)
surface('fabric',(.077,.097,.13),.95,variation=.055,bump=.00035)
surface('cotton',(.073,.095,.115),.97,variation=.09,bump=.0008)
surface('concrete',(.215,.205,.18),.88,variation=.08,bump=.0007)
surface('wear',(.22,.245,.265),.74,.18,bump=0)
surface('ceramic',(.56,.52,.41),.28,variation=.01,bump=0)
surface('lens',(.07,.09,.08),.17,.12,bump=0)
surface('glass',(.94,.97,.99),.045,variation=0,bump=0)
g=MATERIALS['glass'].node_tree.nodes.get('Principled BSDF');g.inputs['Transmission Weight'].default_value=1;g.inputs['IOR'].default_value=1.45
for key,col,power in [('warm_lamp',(1,.65,.30),2.5),('amber_lamp',(1,.38,.025),1.4),('red_lamp',(.45,.018,.01),.6),('green_lamp',(.05,.20,.10),.3),('screen',(.095,.17,.13),.4)]:
    m=surface(key,col,.5,variation=0,bump=0);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(*col,1);bs.inputs['Emission Strength'].default_value=power

def assign(o,key):
    o.data.materials.clear();o.data.materials.append(MATERIALS[key]);uv(o)
def handling_wear(o,key,center,radii,color,strength=.6):
    # Local paint/linoleum response belongs to the handled surface, rather
    # than a detached opaque polygon. Geometry.Position is world space.
    base=o.data.materials[0];m=base.copy();m.name='CD | '+key
    n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF')
    pos=n.new('ShaderNodeNewGeometry');delta=n.new('ShaderNodeVectorMath');delta.operation='SUBTRACT';delta.inputs[1].default_value=center;l.new(pos.outputs['Position'],delta.inputs[0])
    scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=tuple(0 if r==0 else 1/r for r in radii);l.new(delta.outputs[0],scale.inputs[0])
    dist=n.new('ShaderNodeVectorMath');dist.operation='LENGTH';l.new(scale.outputs[0],dist.inputs[0])
    irregular=n.new('ShaderNodeTexNoise');irregular.inputs['Scale'].default_value=47;irregular.inputs['Detail'].default_value=1;l.new(pos.outputs['Position'],irregular.inputs['Vector'])
    varied=n.new('ShaderNodeMath');varied.operation='MULTIPLY_ADD';varied.inputs[1].default_value=.28;varied.inputs[2].default_value=-.14;l.new(irregular.outputs['Fac'],varied.inputs[0])
    boundary=n.new('ShaderNodeMath');boundary.operation='ADD';l.new(dist.outputs['Value'],boundary.inputs[0]);l.new(varied.outputs[0],boundary.inputs[1])
    falloff=n.new('ShaderNodeMapRange');falloff.interpolation_type='SMOOTHSTEP';falloff.inputs['From Min'].default_value=.35;falloff.inputs['From Max'].default_value=1.05;falloff.inputs['To Min'].default_value=strength;falloff.inputs['To Max'].default_value=0;l.new(boundary.outputs[0],falloff.inputs['Value'])
    mix=n.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[2].default_value=(*color,1);l.new(falloff.outputs[0],mix.inputs[0])
    old=bs.inputs['Base Color'].links[0].from_socket;l.new(old,mix.inputs[1]);l.new(mix.outputs[0],bs.inputs['Base Color'])
    drop=n.new('ShaderNodeMath');drop.operation='MULTIPLY';drop.inputs[1].default_value=.18;l.new(falloff.outputs[0],drop.inputs[0])
    rough=n.new('ShaderNodeMath');rough.operation='SUBTRACT';old=bs.inputs['Roughness'].links[0].from_socket;l.new(old,rough.inputs[0]);l.new(drop.outputs[0],rough.inputs[1]);l.new(rough.outputs[0],bs.inputs['Roughness'])
    MATERIALS[key]=m;o.data.materials[0]=m
def replace(name,new,reason):
    # Rotation setters on freshly generated cylinders/toruses do not eagerly
    # update matrix_world. Resolve evaluated transforms before copying geometry.
    bpy.context.view_layer.update()
    old=S.objects[name];world=old.matrix_world.copy();inv=world.inverted()
    if old.type!='MESH':
        for selected in list(bpy.context.selected_objects):selected.select_set(False)
        old.select_set(True);bpy.context.view_layer.objects.active=old
        bpy.ops.object.convert(target='MESH');old=bpy.context.object;old.select_set(False)
    bm=bmesh.new();bm.from_mesh(new.data);bm.transform(inv@new.matrix_world);bm.to_mesh(new.data);bm.free()
    old.data=new.data;old.modifiers.clear()
    for mod in new.modifiers:
        copy=old.modifiers.new(mod.name,mod.type)
        if mod.type=='BEVEL':copy.width=mod.width;copy.segments=mod.segments;copy.limit_method=mod.limit_method
        elif mod.type=='WEIGHTED_NORMAL':copy.keep_sharp=True;copy.weight=40
    bpy.data.objects.remove(new,do_unlink=True);uv(old);EXCEPTIONS[name]=reason;return old

def asset_root(name,target,anchors,direction=(0,0,-1)):
    return assembly('CD | '+name,target,anchors,direction)
def use_root(name):
    global ASM
    ASM=S.objects[name]
def panel(name,x,y,z,w,h,key='blue'):
    # Authored three-step closed pressed-metal section with chamfered corners.
    cut=min(.055,w*.12,h*.12)
    pts=[(-w/2+cut,-h/2),(w/2-cut,-h/2),(w/2,-h/2+cut),(w/2,h/2-cut),(w/2-cut,h/2),(-w/2+cut,h/2),(-w/2,h/2-cut),(-w/2,-h/2+cut)]
    o=profile('CD | '+name,pts,.012,1,(x,y,z),key,.0015)
    inner=profile('CD | '+name+' recessed stamping',[(u*.88,v*.84) for u,v in pts],.006,1,(x,y-.009,z),key,.001)
    return o,inner
def fixings(name,x,y,z,w,h):
    for sx in [-1,1]:
        for sz in [-1,1]:bolt('CD | '+name,(x+sx*(w/2-.028),y,z+sz*(h/2-.028)),r=.007)

def slice_work():
    global ASM
    for o in S.objects:
        if o.type not in {'MESH','CURVE','FONT'}:continue
        n=o.name
        if n.startswith('Office front') or n=='Hatch wall sill base':
            assign(o,'navy' if 'wainscot' in n or 'sill' in n else 'charcoal' if 'dado' in n else 'plaster')
        elif o.parent and o.parent.name in {'D1 Staff Front Door','Checkin Counter Hatch'}:
            oldmat=o.data.materials[0].name
            key={'burgundy_authority':'coral','steel_frame':'charcoal','steel_machined':'steel','steel_gunmetal':'charcoal','paper_sheet':'paper','wood_laminate':'wood','brass_plate':'brass','glass_clean':'glass','ink_black':'ink','rubber_dark':'rubber','rubber_black':'rubber','emissive_green':'green_lamp'}.get(oldmat,'charcoal')
            assign(o,key)
    # Remove actual overlapping architecture, rather than offsetting faces to
    # conceal z-fighting. These piers now butt into the retained lintel at 2.35m.
    # Combined wall envelope, thickness, hatch/door openings and all poses stay.
    for name in ['Office front wall mid','Office front wall east']:
        o=S.objects[name];inv=o.matrix_world.inverted()
        for v in o.data.vertices:
            q=o.matrix_world@v.co
            if q.z>2.35:q.z=2.35;v.co=inv@q
        o.data.update();uv(o)
        EXCEPTIONS[name]='Trim redundant pier above lintel underside z=2.35; remove measured coplanar overlap; combined architectural envelope/apertures unchanged'
    # Frame pocket: wall and protective lining butt into the outer jamb, not
    # through it. West upper return retains its original exterior envelope.
    ASM=None
    replace('Office front wall west',profile('TEMP west frame pocket',[(-6.8,0),(-6.025,0),(-6.025,2.35),(-5.925,2.35),(-5.925,3.05),(-6.8,3.05)],.16,1,(0,3.6,0),'plaster',.002),'Real stepped jamb pocket; outer envelope and net door opening unchanged')
    for name,edge,side in [('Office front wall mid',-4.775,'min'),('Office front wainscot west',-6.025,'max'),('Office front dado west',-6.025,'max'),('Office front wainscot mid',-4.775,'min'),('Office front dado mid',-4.775,'min')]:
        o=S.objects[name];inv=o.matrix_world.inverted()
        for v in o.data.vertices:
            q=o.matrix_world@v.co
            if (side=='max' and q.x>edge) or (side=='min' and q.x<edge):q.x=edge;v.co=inv@q
        o.data.update();uv(o);EXCEPTIONS[name]='Butt wall/lining into outer D1 jamb edge; remove exposed coincident faces, combined door/wall envelope unchanged'
    # A real protective trim caps the lining rather than overlapping its
    # exposed return. Its back now reaches the same structural wall datum.
    for side in ['west','mid']:
        for name,axis,edge in [('Office front wainscot '+side,2,.99),('Office front dado '+side,1,3.52)]:
            o=S.objects[name];inv=o.matrix_world.inverted()
            for v in o.data.vertices:
                q=o.matrix_world@v.co
                if axis==2 and q.z>.99:q.z=.99;v.co=inv@q
                elif axis==1 and q.y>3.50:q.y=3.52;v.co=inv@q
            o.data.update();uv(o)
            EXCEPTIONS[name]=EXCEPTIONS.get(name,'')+'; true trim/lining butt at z=.99 and backing-wall contact Y3.52, exposed combined profile retained'
    use_root('D1 Staff Front Door')
    for z,h in [(.6,.37),(1.6,.65)]:panel('D1 die-pressed leaf',-5.4,3.594,z,.79,h,'coral')
    for x in [-5.919,-4.881]:box('CD | D1 labyrinth seal',(x,3.597,1.1),(.016,.014,2.12),'rubber',.002)
    for z in [.32,1.12,1.96]:
        cyl('CD | D1 captive hinge',(-5.918,3.591,z),.024,.12,'steel',vertices=12,w=.001)
        box('CD | D1 hinge strap',(-5.86,3.594,z),(.095,.01,.07),'steel',.002)
    fixings('D1 kickplate',-5.4,3.583,.22,.96,.4)
    # Handling wear stays around the lock and foot zone, not every perimeter.
    handling_wear(S.objects['D1 door leaf'],'D1 handled paint',(-5.08,3.6,.98),(.09,.012,.115),(.28,.15,.075),.7)
    for i in range(10):
        x=-5.4+random.uniform(-.32,.32);z=.19+random.uniform(-.05,.05)
        profile('CD | D1 foot contact scuff',[(-.045,-.001),(.031,.001),(.046,.005),(-.028,.004)],.0006,1,(x,3.5852,z),'wear',0)
    for x,z in [(-5.8,.086),(-5.755,.062),(-5.73,.073)]:
        profile('CD | D1 paint loss at foot edge',[(-.012,0),(.017,.002),(.02,.007),(.004,.011),(-.011,.006)],.0006,1,(x,3.5997,z),'steel',0)
    box('CD | D1 transom closure',(-5.4,3.6,2.325),(1.25,.20,.05),'charcoal',.001)
    asset_root('D1 identity plate','D1 door leaf',[(-5.545,3.6,1.95),(-5.255,3.6,1.95)],(0,1,0))
    box('CD | D1 ID enamel',(-5.4,3.578,1.92),(.36,.007,.09),'ivory',.001)
    txt('CD | D1 ID','STAFF / 01',(-5.4,3.573,1.895),.045,'ink',align='CENTER')
    verts=[];faces=[]
    for x in [-5.545,-5.255]:
        for z,support_y in [(1.89,3.588),(1.95,3.6)]:
            # Captive stand-offs bridge the measured stepped skin/leaf gap.
            for front,back,radius in [(3.5815,support_y,.0035),(3.5725,3.5745,.0045)]:
                first=len(verts);count=6
                for y in [front,back]:verts.extend((x+radius*cos(2*pi*j/count),y,z+radius*sin(2*pi*j/count)) for j in range(count))
                faces.extend([tuple(first+j for j in range(count-1,-1,-1)),tuple(first+count+j for j in range(count))])
                faces.extend((first+j,first+(j+1)%count,first+(j+1)%count+count,first+j+count) for j in range(count))
    mounts=mesh('CD | D1 ID captive stand-offs',verts,faces,'steel',.00015)
    bm=bmesh.new();bm.from_mesh(mounts.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mounts.data);bm.free()
    mounts['construction_contract']='Four spacers bear on stepped pressed leaf/door skin and enamel back; four captive heads clamp the enamel front. Internal screw threads are not modeled.'
    use_root('D1 Staff Front Door')
    box('CD | D1 key cylinder',(-4.95,3.573,1.11),(.041,.006,.042),'charcoal',.006)
    # Molded reader shell, separate cap seam and lens seating.
    asset_root('D1 wall-mounted reader','Office front wall mid',[(-4.7,3.52,1.23)],(0,1,0))
    reader=replace('D1 keycard reader',profile('TEMP molded reader',[(-.055,-.10),(.055,-.10),(.06,-.095),(.06,.092),(.047,.10),(-.047,.10),(-.06,.092),(-.06,-.095)],.032,1,(-4.7,3.504,1.25),'plastic',.001),'Molded ABS reader with actual back-plane Y3.52 bearing; inherited matrix retained, measured 20mm wall penetration removed')
    world=reader.matrix_world.copy();reader.parent=ASM;reader.matrix_world=world;reader['assembly']=ASM.name
    # Four pressed cap regions leave a genuine rectangular lens aperture.
    caps=[
        [(-.0395,-.0875),(.0395,-.0875),(.0515,-.0755),(.0515,.035),(-.0515,.035),(-.0515,-.0755)],
        [(-.0515,.065),(.0515,.065),(.0515,.0755),(.0395,.0875),(-.0395,.0875),(-.0515,.0755)],
        [(-.0515,.035),(-.0225,.035),(-.0225,.065),(-.0515,.065)],
        [(.0225,.035),(.0515,.035),(.0515,.065),(.0225,.065)]]
    for pts in caps:profile('CD | Reader aperture cap',pts,.0025,1,(-4.7,3.48675,1.25),'plastic',0)
    lens=replace('D1 keycard light green',profile('TEMP reader lens',[(-.02,-.0095),(.02,-.0095),(.02,.0095),(-.02,.0095)],.005,1,(-4.7,3.4855,1.30),'green_lamp',.0003),'Indicator lens seated on actual housing front through a real cap aperture; inherited matrix retained')
    world=lens.matrix_world.copy();lens.parent=ASM;lens.matrix_world=world;lens['assembly']=ASM.name
    txt('CD | D1 access caption','CLEARANCE 3',(-4.7,3.4845,1.218),.014,'ivory',align='CENTER')
    use_root('Checkin Counter Hatch')
    # The inherited steel posts were buried in an identical continuous sill
    # volume, leaving exposed coincident faces. Real infill butts between them.
    ASM=None;verts=[];faces=[]
    for left,right in [(-4.35,-4.29),(-4.21,-2.79),(-2.71,-2.67)]:
        start=len(verts)
        verts.extend((x,y,z) for z in [0,1] for y in [3.52,3.68] for x in [left,right])
        faces.extend(tuple(start+i for i in f) for f in [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)])
    infill=mesh('TEMP sill post pockets',verts,faces,'navy',.0008)
    replace('Hatch wall sill base',infill,'Three real infill sections butt into inherited steel posts; remove exposed duplicate front/back surfaces; combined sill envelope retained')
    use_root('Checkin Counter Hatch')
    # Real folded section, rather than the source's flat slab and chrome strip.
    cross=[(-.35,-.02),(.35,-.02),(.35,.02),(-.33,.02),(-.35,0)]
    replace('Transaction counter slab',profile('TEMP folded worktop',cross,1.68,0,(-3.51,3.6,1.02),'steel',.002),'Folded worktop cross-section; same footprint/top datum')
    inset=box('CD | Counter linoleum inset',(-3.51,3.6,1.041),(1.51,.56,.002),'linoleum',0)
    handling_wear(inset,'Handled linoleum',(-3.77,3.365,1.042),(.145,.038,.003),(.11,.12,.115),.7)
    handling_wear(S.objects['Transaction counter slab'],'Worktop lip wear',(-3.80,3.255,1.024),(.16,.025,.017),(.16,.175,.18),.6)
    for x in [-4.25,-2.75]:
        profile('CD | Counter gusset',[(0,0),(.17,0),(0,-.24)],.035,0,(x,3.68,1.0),'charcoal',.002)
        bolt('CD | Counter underside fixing',(x,3.525,.97),r=.006)
    # Replace incorrectly oriented source ring with angular cast speaking grille.
    shell=profile('TEMP speaking grille',[(-.10,-.085),(.10,-.085),(.115,-.07),(.115,.07),(.10,.085),(-.10,.085),(-.115,.07),(-.115,-.07)],.021,1,(-3.51,3.575,1.4),'charcoal',.002)
    replace('Speaking baffle ring',shell,'Cast octagonal speaking grille, physically oriented toward customer')
    box('CD | Speaking grille isolation pad',(-3.51,3.589,1.4),(.18,.007,.125),'rubber',0)
    for z in [1.352,1.37,1.388,1.406,1.424,1.442]:box('CD | Speaking grille slit',(-3.51,3.562,z),(.154,.002,.005),'ink',.001)
    fixings('Speaking grille',-3.51,3.56,1.4,.23,.17)
    for x in [-3.715,-3.305]:
        box('CD | Speaking glazing clamp',(x,3.586,1.4),(.016,.02,.23),'steel',.001)
        box('CD | Speaking stanchion foot',(x,3.594,1.045),(.055,.075,.006),'steel',.001)
        box('CD | Speaking load-bearing stanchion',(x,3.599,1.282),(.021,.024,.468),'charcoal',.001)
        for y in [3.568,3.62]:cyl('CD | Stanchion foot fixing',(x,y,1.05),.004,.004,'steel',vertices=6,w=.0005)
    box('CD | Speaking instruction decal',(-3.51,3.592,1.545),(.35,.001,.035),'ivory',0)
    txt('CD | Speak instruction','STATE YOUR NUMBER',(-3.51,3.5909,1.538),.021,'ink',align='CENTER')
    box('CD | Document tray lip',(-3.51,3.42,1.043),(.44,.012,.012),'steel',.001)
    box('CD | Counter docket tray',(-4.045,3.6,1.052),(.24,.29,.018),'charcoal',.002)
    for x in [-4.158,-3.932]:box('CD | Docket folded rail',(x,3.6,1.083),(.008,.29,.05),'charcoal',.001)
    for i in range(4):box('CD | Unprocessed forms',(-4.045+i*.003,3.6-i*.002,1.063+i*.0015),(.20,.25,.001),'paper',0)
    txt('CD | Forms title','UNPROCESSED',(-4.135,3.56,1.069),.017,'ink',rot=(0,0,0))
    box('CD | Stamp maker plate',(-2.95,3.394,1.083),(.052,.002,.01),'ivory',0)
    txt('CD | Stamp identity','07',(-2.95,3.3925,1.0805),.008,'ink',align='CENTER')
    for i in range(7):
        x=-3.68+random.uniform(-.12,.19);y=3.3+random.uniform(-.006,.008)
        scar=box('CD | Counter handling scar',(x,y,1.043),(.012+random.uniform(0,.04),.001,.0005),'wear',0);scar.rotation_euler[2]=random.uniform(-.16,.16)
    # Anti-slip stamping pad gives rubber a purposeful silhouette and response.
    asset_root('Stamping rubber pad','CD | Counter linoleum inset',[(-3.045,3.38,1.042),(-2.8,3.48,1.042)])
    profile('CD | Molded stamping pad',[(-.145,-.085),(.145,-.085),(.165,-.065),(.165,.065),(.145,.085),(-.145,.085),(-.165,.065),(-.165,-.065)],.006,2,(-2.915,3.43,1.045),'rubber',.001)
    verts=[];faces=[]
    for i in range(12):
        x=-3.045+i*.024;start=len(verts)
        verts.extend((xx,yy,zz) for zz in [1.048,1.049] for yy in [3.357,3.369] for xx in [x-.002,x+.002])
        faces.extend(tuple(start+j for j in f) for f in [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)])
    mesh('CD | Pad molded grip ribs',verts,faces,'rubber',.0003)
    use_root('Checkin Counter Hatch')
    # Retained small-item poses/top connections stay; extend the defective base
    # construction to the actual worktop, instead of leaving inherited gaps.
    for name in ['Authority stamp rubber base','Ink pad tin base','Counter pen holder base']:
        o=S.objects[name];inv=o.matrix_world.inverted()
        for v in o.data.vertices:
            q=o.matrix_world@v.co
            if q.z<o.matrix_world.translation.z:q.z=1.048 if name!='Counter pen holder base' else 1.042;v.co=inv@q
        o.data.update();uv(o);EXCEPTIONS[name]='Extend base to actual support (stamping pad 1.048 or linoleum 1.042), retaining matrix and upper interface'
    # Hollow molded ink-pad case, inset felt seat, lip, open lid and pin hinges.
    def ring(w,d,cut,z):return [(-2.8+x,3.42+y,z) for x,y in [(-w/2+cut,-d/2),(w/2-cut,-d/2),(w/2,-d/2+cut),(w/2,d/2-cut),(w/2-cut,d/2),(-w/2+cut,d/2),(-w/2,d/2-cut),(-w/2,-d/2+cut)]]
    verts=ring(.096,.076,.005,1.048)+ring(.10,.08,.005,1.076)+ring(.09,.068,.003,1.076)+ring(.087,.066,.003,1.0695)
    faces=[tuple(range(7,-1,-1)),tuple(range(24,32))]
    for j in range(3):faces.extend((j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i) for i in range(8))
    case=mesh('TEMP molded ink-pad case',verts,faces,'plastic',.0005)
    bm=bmesh.new();bm.from_mesh(case.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(case.data);bm.free()
    replace('Ink pad tin base',case,'Historical name retained; new hollow molded bakelite case, actual felt seat and stamping-pad bearing')
    replace('Ink pad lid open',profile('TEMP molded lid',[(-.045,-.03),(.045,-.03),(.05,-.025),(.05,.025),(.045,.03),(-.045,.03),(-.05,.025),(-.05,-.025)],.009,1,(-2.8,3.475,1.095),'plastic',.0005),'Molded lid with clipped corners and physical pin hinges')
    box('CD | Ink pad lid inner lip',(-2.8,3.4698,1.095),(.084,.002,.044),'plastic',.001)
    for x in [-2.838,-2.762]:cyl('CD | Ink pad pin hinge',(x,3.466,1.073),.007,.023,'plastic','X',vertices=12,w=.0005)
    assign(S.objects['Ink pad felt cushion'],'ink')
    # A shallow rag left during counter cleaning demonstrates woven fabric.
    asset_root('Counter cleaning cloth','CD | Counter linoleum inset',[(-4.23,3.35,1.042),(-4.035,3.425,1.042)])
    profile('CD | Folded wipe lower ply',[(-.13,-.056),(.105,-.06),(.13,-.038),(.118,.054),(-.10,.058),(-.13,.034)],.011,2,(-4.11,3.39,1.0475),'cotton',.002)
    profile('CD | Folded wipe middle ply',[(-.125,-.055),(.11,-.052),(.125,-.03),(.115,.049),(-.108,.05),(-.127,.031)],.009,2,(-4.112,3.386,1.0575),'cotton',.0015)
    verts=[];nx=16;ny=10
    for j in range(ny+1):
        for i in range(nx+1):
            u=i/nx;v=j/ny
            x=-4.234+.252*u+.004*u*sin(2*pi*v)
            y=3.335+.104*v+.003*sin(pi*u)*cos(2*pi*v)
            fold=.030*max(0,1-abs(v-.40-.16*u)/.26)*sin(pi*u)
            # A lifted near corner and broad crease read at gameplay distance.
            corner=.017*max(0,(u-.72)/.28)*max(0,1-v/.42)
            verts.append((x,y,1.062+fold+corner))
    faces=[(j*(nx+1)+i,j*(nx+1)+i+1,(j+1)*(nx+1)+i+1,(j+1)*(nx+1)+i) for j in range(ny) for i in range(nx)]
    rag=mesh('CD | Used cotton wipe',verts,faces,'cotton')
    for f in rag.data.polygons:f.use_smooth=True
    solid=rag.modifiers.new('Woven cloth thickness','SOLIDIFY');solid.thickness=.0024;solid.offset=1
    for row in [3.334,3.443]:
        points=[]
        for i in range(nx+1):
            u=i/nx;points.append((-4.234+.252*u,row+.003*sin(pi*u),1.0644+(.017*max(0,(u-.72)/.28) if row<3.4 else 0)))
        line('CD | Wipe rolled hem',points,.0011,'cotton')
    use_root('Checkin Counter Hatch')
    # Coffee traces mark one exact worker resting spot; no general grunge.
    for i in range(19):
        t=pi*.15+i*pi*1.5/18;r=.045
        box('CD | Faded cup contact',(-3.89+r*cos(t),3.61+r*sin(t),1.0423),(.004,.002,.0006),'coffee',0)
    # Curl only an unwritten corner, preserving the existing readable form face.
    o=S.objects['Counter manifest paper'];inv=o.matrix_world.inverted()
    for v in o.data.vertices:
        q=o.matrix_world@v.co
        if q.x>-3.30 and q.y>3.52:q.z+=.004;v.co=inv@q
    o.data.update();uv(o);EXCEPTIONS[o.name]='Used form corner curl outside text, retained main writing plane'
    for mod in o.modifiers:
        if mod.type=='BEVEL':mod.width=min(mod.width,.0004)
    # Three different worker traces, restricted to this one cluster.
    box('CD | Rejected docket',(-3.0,3.75,1.043),(.19,.12,.001),'paper',0)
    txt('CD | Docket warning','RETURN TO DUTY',(-3.08,3.73,1.044),.018,'coral',rot=(0,0,0))
    txt('CD | Docket secondary','INCIDENT 731 / NO LEAVE',(-3.08,3.71,1.044),.009,'ink',rot=(0,0,0))
    # Label plaque physically bears against front-office lintel.
    asset_root('Counter authority plaque','Office front head lintel',[(-3.75,3.52,2.68),(-3.27,3.52,2.68)],(0,1,0))
    box('CD | Plaque wall back',(-3.51,3.509,2.7),(1.42,.022,.35),'charcoal',.004)
    box('CD | Plaque enamel inset',(-3.51,3.493,2.7),(1.34,.008,.275),'ivory',.002)
    txt('CD | Plaque headline','WE VALUE YOUR TIME',(-3.51,3.487,2.735),.088,'ink',align='CENTER')
    txt('CD | Plaque coercion','ALL DELAYS ARE YOUR RESPONSIBILITY',(-3.51,3.486,2.653),.034,'ink',align='CENTER')
    # Concrete practical fixture, plugged into a surface-mounted utility route.
    asset_root('Check-in task fixture','Office front head lintel',[(-3.72,3.52,2.43),(-3.30,3.52,2.43)],(0,1,0))
    for x in [-3.72,-3.30]:box('CD | Task wall bracket',(x,3.475,2.43),(.035,.09,.075),'charcoal',.002)
    profile('CD | Task folded shade',[(-.05,-.018),(.05,-.018),(.08,.02),(-.08,.02)],.65,0,(-3.51,3.41,2.43),'charcoal',.002)
    box('CD | Task frosted lens',(-3.51,3.413,2.410),(.55,.08,.006),'warm_lamp',.001)
    light('CD | Check-in practical',(-3.51,3.38,2.399),(-3.51,3.47,1.05),40,(1,.71,.43),.55,.09)
    asset_root('D1 service junction','Office front wall mid',[(-4.6125,3.52,2.0)],(0,1,0))
    box('CD | D1 service mounting back',(-4.6125,3.507,2.0),(.14,.026,.16),'charcoal',.001)
    panel('D1 service lid',-4.6125,3.485,2.0,.15,.17,'blue');fixings('D1 service box',-4.6125,3.472,2.0,.15,.17)
    path=[(-4.6125,3.48,1.98),(-4.6125,3.48,1.555)]
    path.extend((-4.6575+.045*cos(-pi*i/10),3.48,1.555+.045*sin(-pi*i/10)) for i in range(1,6))
    path.extend([(-4.7,3.48,1.51),(-4.7,3.52,1.35)])
    line('CD | Door armored conduit',path,.009,'charcoal')
    for z in [1.75,1.92]:
        box('CD | Service saddle fixing',(-4.6125,3.5045,z),(.03,.031,.018),'steel',.001)
        bolt('CD | Saddle captive fixing',(-4.6125,3.488,z),r=.005)
    # Each independent wall/floor/table prop must own a measured support root.
    ASM=None

slice_work()
if a.stage=='full':
    gate=json.loads((PROD/'STYLE_SLICE_ACCEPTANCE.json').read_text())
    for rel,digest in gate['files'].items():
        if sha(PROD/rel)!=digest:raise RuntimeError('Style gate evidence changed: '+rel)
    for role in ['visual_report','technical_report']:
        if json.loads((PROD/gate[role]).read_text())['verdict']!='LOCAL PASS':raise RuntimeError('Style expansion gate failed: '+role)
    exec(compile((ROOT/'full_detail.py').read_text(),str(ROOT/'full_detail.py'),'exec'),globals())
    full_work()

# Global lighting mood is a preview. All out-of-slice meshes stay untouched.
for o in S.objects:
    if o.type!='LIGHT' or o.name.startswith('CD |'):continue
    o.data.energy*=.10 if o.data.type=='AREA' else .025
    if o.data.type=='AREA':o.data.color=(.68,.77,1)
for mat in list(bpy.data.materials):
    if not mat.name.startswith('emissive_'):continue
    bs=mat.node_tree.nodes.get('Principled BSDF') if mat.use_nodes else None
    if bs:bs.inputs['Emission Strength'].default_value*=.18
if a.stage=='full':full_lighting()
S.world=S.world.copy();bg=S.world.node_tree.nodes.get('Background')
if bg:bg.inputs[0].default_value=(.11,.14,.20,1);bg.inputs[1].default_value=.16
S['stage']=a.stage;S['revision']=a.revision;S['contact_assemblies']=json.dumps(CONTACTS)
S['overhaul_map_reference']=True;S['map_context']='Read-only linked canonical map; original module remains selected in assembly.'
S['author']='root';S['overhaul_status']='FULL ROOM / REVIEW PENDING' if a.stage=='full' else 'STYLE SLICE / LOCAL ACCEPTED s10' if a.revision=='s10' else 'STYLE SLICE / NOT ACCEPTED'
for o in S.objects:
    if o.name not in ORIGINAL and o.type=='MESH':uv(o)
    elif o.name not in ORIGINAL and o.type=='CURVE':o.data.resolution_u=min(o.data.resolution_u,6);o.data.bevel_resolution=min(o.data.bevel_resolution,2)
    if o.type=='FONT' and o.name not in ORIGINAL:o.data.resolution_u=min(o.data.resolution_u,4)
# Curve geometry becomes an editable mesh with the same name/pose and metric
# face charts. Text stays editable; its shared family uses explicit 1m object
# coordinates rather than claiming an absent named UV layer.
text_materials={}
for o in list(S.objects):
    if o.type not in {'CURVE','FONT'} or not any(m and m.name.startswith('CD |') for m in o.data.materials):continue
    if o.type=='CURVE':
        name=o.name
        for selected in bpy.context.selected_objects:selected.select_set(False)
        o.select_set(True);bpy.context.view_layer.objects.active=o
        bpy.ops.object.convert(target='MESH');o=S.objects[name];uv(o);o.select_set(False)
        o['editable_curve_recipe']='overhaul_dock.py or reference-tooling/original_build_dock.py; converted render geometry with metric UV'
    else:
        for i,base in enumerate(list(o.data.materials)):
            if not base or not base.name.startswith('CD |'):continue
            if base.name not in text_materials:
                m=base.copy();m.name=base.name+' | text object metres';n=m.node_tree.nodes;l=m.node_tree.links
                coords=n.new('ShaderNodeTexCoord')
                for node in list(n):
                    if node.type!='UVMAP':continue
                    destinations=[link.to_socket for link in node.outputs[0].links]
                    for socket in destinations:l.new(coords.outputs['Object'],socket)
                    n.remove(node)
                m['mapping_contract']='Editable FONT: local object metres (object scale retained), no absent UV layer claim'
                text_materials[base.name]=m
            o.data.materials[i]=text_materials[base.name]
for o in S.objects:
    if o.type!='MESH' or not o.get('overhaul_surface'):continue
    # UV after true manufactured edge/thickness geometry, not interpolated
    # bevel UV strips. Editable meshes and procedural source remain delivered.
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    for mod in list(o.modifiers):
        if mod.type=='BEVEL':
            if o.name not in ORIGINAL and mod.width<=.002:mod.segments=min(mod.segments,2)
            # Measured full-width edge collapse on thin slit/rib/lip parts:
            # retain a positive central face rather than beveling to zero.
            positive=[d for d in o.dimensions if d>1e-7]
            if positive:mod.width=min(mod.width,min(positive)*.35)
        if mod.type in {'BEVEL','SOLIDIFY'}:bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(o.data)
    warped=[]
    for f in bm.faces:
        if len(f.verts)>3 and max(abs((v.co-f.verts[0].co).dot(f.normal)) for v in f.verts)>1e-6:warped.append(f)
    if warped:bmesh.ops.triangulate(bm,faces=warped)
    bm.to_mesh(o.data);bm.free();o.data.update();uv(o);o.select_set(False)
if a.stage=='full':
    finish_full_repairs()
    consolidate_new_details()
# Keep actual inherited camera count; additional evidence cameras are disposable.
S.camera=S.objects['C01_ENTRY'];S.render.resolution_x=1067;S.render.resolution_y=600;S.render.resolution_percentage=100
bpy.context.view_layer.update()
for name,rec in BASE.items():
    o=S.objects[name]
    delta=max(abs(o.matrix_world[i][j]-rec['matrix'][i][j]) for i in range(4) for j in range(4))
    if delta>1e-6:raise RuntimeError('Moved inherited object '+name)
    if o.get('support_class')=='architectural' and name not in EXCEPTIONS and max(abs(o.dimensions[i]-rec['dimensions'][i]) for i in range(3))>1e-5:raise RuntimeError('Resized room architecture '+name)
map_path=ROOT.parents[1]/'blender/facility_environment.blend'
with bpy.data.libraries.load(str(map_path),link=True) as (lib,loaded):loaded.scenes=list(lib.scenes)
for lib in bpy.data.libraries:
    if lib.parent is None:lib.filepath=bpy.path.relpath(bpy.path.abspath(lib.filepath),start=str(ROOT))
bpy.context.window.scene=S
for name,expected in RECIPE_HASHES.items():
    if sha(ROOT/name)!=expected:raise RuntimeError('Recipe changed during build: '+name)
S['recipe_sha256']=json.dumps(RECIPE_HASHES,sort_keys=True)
out=ROOT/'module_overhaul_R1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
deps=bpy.context.evaluated_depsgraph_get();triangles=0
for o in S.objects:
    if o.type not in {'MESH','CURVE','FONT'}:continue
    ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();triangles+=len(me.loop_triangles);ev.to_mesh_clear()
state={'stage':a.stage,'revision':a.revision,'source_sha256':sha(out),'source_saved':str(out),'editable_scene':S.name,'original_objects':len(ORIGINAL),'objects':len(S.objects),'evaluated_triangles':triangles,'authoring_material_submeshes':sum(len({p.material_index for p in o.data.polygons}) if o.type=='MESH' else 1 for o in S.objects if o.type in {'MESH','CURVE','FONT'}),'used_local_material_families':sorted({m.name for o in S.objects if o.type in {'MESH','CURVE','FONT'} for m in o.data.materials if m}),'intentional_construction_repairs':EXCEPTIONS,'inherited_matrices_unchanged':True,'combined_room_envelope_and_apertures_unchanged':True,'architectural_geometry_repairs':[n for n in EXCEPTIONS if S.objects[n].get('support_class')=='architectural'],'architectural_dimension_repairs':[n for n in EXCEPTIONS if S.objects[n].get('support_class')=='architectural' and max(abs(S.objects[n].dimensions[i]-BASE[n]['dimensions'][i]) for i in range(3))>1e-5],'approved_spawn_source_sha256':spawn['source_sha256'],'map_reference':str(map_path),'source_author':'root','runtime_performance_measured':False}
(PROD/'build-state.json').write_text(json.dumps(state,indent=2)+'\n')
state['recipe_sha256']=RECIPE_HASHES
(PROD/'build-state.json').write_text(json.dumps(state,indent=2)+'\n')
for rel,expected in protected.items():
    if sha(ROOT.parents[3]/rel)!=expected:raise RuntimeError('Changed protected input '+rel)
print('DOCK_OVERHAUL_SAVED',a.stage,a.revision,len(S.objects),triangles,flush=True)
