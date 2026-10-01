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
        # Local metre units; planar seams at manufactured corners. Repeats are
        # intentional for physical repeating materials, not a bake/lightmap UV.
        axis=max(range(3),key=lambda i:abs(f.normal[i]));axes=[i for i in range(3) if i!=axis]
        for li in f.loop_indices:
            q=o.data.vertices[o.data.loops[li].vertex_index].co
            layer.data[li].uv=(q[axes[0]],q[axes[1]])
    o['overhaul_surface']=True;o['uv_contract']='CD_Physical_1m; one UV unit per metre; intentional repeat overlaps'

spawn=json.loads((PROD/'spawn-input.json').read_text());colors={}
for m in spawn['materials']:
    if m['name'].startswith('COZY'):colors[m['name'].split('_')[1]]=m['Base Color'][:3]
def surface(key,color,rough,metal=0,variation=.025,bump=.00015):
    m=bpy.data.materials.new('CD | '+key);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
    bs.inputs['Specular IOR Level'].default_value=.3 if metal<.5 else .45
    n=m.node_tree.nodes;l=m.node_tree.links
    t=n.new('ShaderNodeUVMap');t.uv_map='CD_Physical_1m'
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=22;noise.inputs['Detail'].default_value=1.5;l.new(t.outputs[0],noise.inputs['Vector'])
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

surface('plaster',(.51,.47,.39),.88,variation=.025,bump=.0005)
surface('navy',colors['navy'],.71,bump=.0002)
surface('blue',colors['denim'],.62,.12,bump=.00012)
surface('charcoal',colors['charcoal'],.64,.15,bump=.00012)
surface('coral',[c*.65 for c in colors['coral']],.61,.08)
surface('ivory',(.67,.63,.52),.68,.05)
surface('steel',colors['steel'],.39,.82,bump=.00006)
surface('brass',colors['brass'],.43,.82,bump=.00006)
surface('yellow',[c*.72 for c in colors['mustard']],.7,.05)
surface('rubber',(.018,.021,.025),.92,variation=.06,bump=.0005)
surface('paper',(.78,.72,.58),.96,variation=.015,bump=.00003)
surface('ink',colors['ink'],.94,bump=0)
surface('wood',[c*.65 for c in colors['walnut']],.76,variation=.08,bump=.0002)
surface('fabric',(.077,.097,.13),.95,variation=.055,bump=.00035)
surface('concrete',(.18,.19,.205),.88,variation=.07,bump=.0007)
surface('wear',(.22,.245,.265),.74,.18,bump=0)
surface('ceramic',(.56,.52,.41),.28,variation=.01,bump=0)
surface('lens',(.07,.09,.08),.17,.12,bump=0)
surface('glass',(.94,.97,.99),.045,variation=0,bump=0)
g=MATERIALS['glass'].node_tree.nodes.get('Principled BSDF');g.inputs['Transmission Weight'].default_value=1;g.inputs['IOR'].default_value=1.45
for key,col,power in [('warm_lamp',(1,.65,.30),2.5),('amber_lamp',(1,.38,.025),1.4),('red_lamp',(.45,.018,.01),.6),('green_lamp',(.05,.20,.10),.3),('screen',(.095,.17,.13),.4)]:
    m=surface(key,col,.5,variation=0,bump=0);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(*col,1);bs.inputs['Emission Strength'].default_value=power

def assign(o,key):
    o.data.materials.clear();o.data.materials.append(MATERIALS[key]);uv(o)
def replace(name,new,reason):
    old=S.objects[name];world=old.matrix_world.copy();inv=world.inverted()
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
            key={'burgundy_authority':'coral','steel_frame':'charcoal','steel_machined':'steel','steel_gunmetal':'charcoal','paper_sheet':'paper','wood_laminate':'wood','brass_plate':'brass','glass_clean':'glass','ink_black':'ink','rubber_black':'rubber','emissive_green':'green_lamp'}.get(oldmat,'charcoal')
            assign(o,key)
    use_root('D1 Staff Front Door')
    for z,h in [(.6,.37),(1.6,.65)]:panel('D1 die-pressed leaf',-5.4,3.594,z,.79,h,'coral')
    for x in [-5.919,-4.881]:box('CD | D1 labyrinth seal',(x,3.597,1.1),(.016,.014,2.12),'rubber',.002)
    for z in [.32,1.12,1.96]:
        cyl('CD | D1 captive hinge',(-5.918,3.591,z),.024,.12,'steel',vertices=12,w=.001)
        box('CD | D1 hinge strap',(-5.86,3.594,z),(.095,.01,.07),'steel',.002)
    fixings('D1 kickplate',-5.4,3.583,.22,.96,.4)
    box('CD | D1 ID enamel',(-5.4,3.578,1.92),(.36,.007,.09),'ivory',.001)
    txt('CD | D1 ID','STAFF / 01',(-5.4,3.573,1.895),.045,'ink',align='CENTER')
    box('CD | D1 key cylinder',(-4.95,3.573,1.11),(.041,.006,.042),'charcoal',.006)
    txt('CD | D1 access caption','CLEARANCE 3',(-4.7,3.486,1.218),.014,'ivory',align='CENTER')
    use_root('Checkin Counter Hatch')
    # Real folded section, rather than the source's flat slab and chrome strip.
    cross=[(-.35,-.02),(.35,-.02),(.35,.02),(-.33,.02),(-.35,0)]
    replace('Transaction counter slab',profile('TEMP folded worktop',cross,1.68,0,(-3.51,3.6,1.02),'steel',.002),'Folded worktop cross-section; same footprint/top datum')
    box('CD | Counter linoleum inset',(-3.51,3.6,1.041),(1.51,.56,.002),'charcoal',0)
    for x in [-4.25,-2.75]:
        profile('CD | Counter gusset',[(0,0),(.19,0),(0,-.24)],.035,0,(x,3.57,1.0),'charcoal',.002)
        bolt('CD | Counter underside fixing',(x,3.525,.97),r=.006)
    # Replace incorrectly oriented source ring with angular cast speaking grille.
    shell=profile('TEMP speaking grille',[(-.10,-.085),(.10,-.085),(.115,-.07),(.115,.07),(.10,.085),(-.10,.085),(-.115,.07),(-.115,-.07)],.021,1,(-3.51,3.575,1.4),'charcoal',.002)
    replace('Speaking baffle ring',shell,'Cast octagonal speaking grille, physically oriented toward customer')
    box('CD | Speaking grille isolation pad',(-3.51,3.589,1.4),(.18,.007,.125),'rubber',0)
    for z in [1.352,1.37,1.388,1.406,1.424,1.442]:box('CD | Speaking grille slit',(-3.51,3.562,z),(.154,.002,.005),'ink',.001)
    fixings('Speaking grille',-3.51,3.56,1.4,.23,.17)
    for x in [-3.715,-3.305]:
        box('CD | Speaking glazing clamp',(x,3.586,1.4),(.016,.02,.23),'steel',.001)
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
    light('CD | Check-in practical',(-3.51,3.38,2.399),(-3.51,3.47,1.05),65,(1,.71,.43),.55,.09)
    asset_root('D1 service junction','Office front wall mid',[(-4.6125,3.52,2.0)],(0,1,0))
    box('CD | D1 service mounting back',(-4.6125,3.507,2.0),(.14,.026,.16),'charcoal',.001)
    panel('D1 service lid',-4.6125,3.485,2.0,.15,.17,'blue');fixings('D1 service box',-4.6125,3.472,2.0,.15,.17)
    line('CD | Door armored conduit',[(-4.6125,3.48,1.98),(-4.6125,3.48,1.51),(-4.7,3.48,1.51),(-4.7,3.52,1.35)],.009,'charcoal')
    # Each independent wall/floor/table prop must own a measured support root.
    ASM=None

slice_work()
if a.stage=='full':
    raise RuntimeError('Full expansion is locked until independent style-slice acceptance is recorded.')

# Global lighting mood is a preview. All out-of-slice meshes stay untouched.
for o in S.objects:
    if o.type!='LIGHT' or o.name.startswith('CD |'):continue
    o.data.energy*=.18 if o.data.type=='AREA' else .04
    if o.data.type=='AREA':o.data.color=(1,.87,.68)
S.world=S.world.copy();bg=S.world.node_tree.nodes.get('Background')
if bg:bg.inputs[0].default_value=(.11,.14,.20,1);bg.inputs[1].default_value=.16
S['stage']=a.stage;S['revision']=a.revision;S['contact_assemblies']=json.dumps(CONTACTS)
S['overhaul_map_reference']=True;S['map_context']='Read-only linked canonical map; original module remains selected in assembly.'
S['author']='root';S['overhaul_status']='STYLE SLICE / NOT ACCEPTED'
for o in S.objects:
    if o.name not in ORIGINAL and o.type=='MESH':uv(o)
    elif o.name not in ORIGINAL and o.type=='CURVE':o.data.resolution_u=min(o.data.resolution_u,6);o.data.bevel_resolution=min(o.data.bevel_resolution,2)
    if o.type=='FONT' and o.name not in ORIGINAL:o.data.resolution_u=min(o.data.resolution_u,4)
# Keep actual inherited camera count; additional evidence cameras are disposable.
S.camera=S.objects['C01_ENTRY'];S.render.resolution_x=1067;S.render.resolution_y=600;S.render.resolution_percentage=100
bpy.context.view_layer.update()
for name,rec in BASE.items():
    o=S.objects[name]
    delta=max(abs(o.matrix_world[i][j]-rec['matrix'][i][j]) for i in range(4) for j in range(4))
    if delta>1e-6:raise RuntimeError('Moved inherited object '+name)
    if o.get('support_class')=='architectural' and max(abs(o.dimensions[i]-rec['dimensions'][i]) for i in range(3))>1e-5:raise RuntimeError('Resized room architecture '+name)
map_path=ROOT.parents[1]/'blender/facility_environment.blend'
with bpy.data.libraries.load(str(map_path),link=True) as (lib,loaded):loaded.scenes=list(lib.scenes)
for lib in bpy.data.libraries:
    if lib.parent is None:lib.filepath=bpy.path.relpath(bpy.path.abspath(lib.filepath),start=str(ROOT))
bpy.context.window.scene=S
out=ROOT/'module_overhaul_R1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
deps=bpy.context.evaluated_depsgraph_get();triangles=0
for o in S.objects:
    if o.type not in {'MESH','CURVE','FONT'}:continue
    ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();triangles+=len(me.loop_triangles);ev.to_mesh_clear()
state={'stage':a.stage,'revision':a.revision,'source_sha256':sha(out),'source_saved':str(out),'editable_scene':S.name,'original_objects':len(ORIGINAL),'objects':len(S.objects),'evaluated_triangles':triangles,'authoring_material_submeshes':sum(len({p.material_index for p in o.data.polygons}) if o.type=='MESH' else 1 for o in S.objects if o.type in {'MESH','CURVE','FONT'}),'used_local_material_families':sorted({m.name for o in S.objects if o.type in {'MESH','CURVE','FONT'} for m in o.data.materials if m}),'intentional_construction_repairs':EXCEPTIONS,'inherited_matrices_unchanged':True,'architectural_dimensions_unchanged':True,'approved_spawn_source_sha256':spawn['source_sha256'],'map_reference':str(map_path),'source_author':'root','runtime_performance_measured':False}
(PROD/'build-state.json').write_text(json.dumps(state,indent=2)+'\n')
for rel,expected in protected.items():
    if sha(ROOT.parents[3]/rel)!=expected:raise RuntimeError('Changed protected input '+rel)
print('DOCK_OVERHAUL_SAVED',a.stage,a.revision,len(S.objects),triangles,flush=True)
