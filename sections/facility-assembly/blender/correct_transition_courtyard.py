"""Reviewer-directed correction limited to the owned courtyard pass."""
import bpy,bmesh,ast,math,random,json,hashlib,ctypes
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/courtyard'
SRC=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
report=json.loads((OUT/'build-verification.json').read_text());previous=sha(SRC)
assert previous==report['saved_sha256']
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
coll=bpy.data.collections['ART | Courtyard mine-to-refinery'];rng=random.Random(1729)
tree=ast.parse(Path(__file__).with_name('build_transition_courtyard.py').read_text())
helpers={'fingerprint','bounds','mesh_obj','box','beam','material'}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in helpers],type_ignores=[]),'<courtyard helpers>','exec'))

# Reuse the existing authored fieldstone assets, retaining source materials.
sources=[bpy.data.objects[n] for n in ('R36 | Mine toe rockfall A','R36 | Mine toe rockfall N1','R36 | Mine join recess boulder')]
for i,rec in enumerate(report['rocks']):
    o=bpy.data.objects[rec['name']];source=sources[i%3];o.data=source.data
    dx,dy,dz=rec['dimensions'];dx*=.92;dy*=.94;dz*=.80
    if i in (1,4,8):dz*=1.1
    x,y=rec['position'];y+=(-.1,.05,-.25)[i%3]
    bb=[Vector(c) for c in source.bound_box];lo=Vector(tuple(min(v[a] for v in bb) for a in range(3)));hi=Vector(tuple(max(v[a] for v in bb) for a in range(3)))
    o.scale=(dx/(hi.x-lo.x),dy/(hi.y-lo.y),dz/(hi.z-lo.z));o.rotation_euler=(0,0,rng.uniform(-.48,.48))
    cen=o.rotation_euler.to_matrix()@Vector(((lo.x+hi.x)*.5*o.scale.x,(lo.y+hi.y)*.5*o.scale.y,lo.z*o.scale.z))
    o.location=Vector((x,y,-.16))-cen;o['courtyard_source']=source.name
    rec.update(source=source.name,mesh=source.data.name,position=[x,y],dimensions=[dx,dy,dz],burial=-.16)

# Preserve the original dirt shader's authored broad texture and shallow relief.
old=bpy.data.materials['CY | Mine earth to dusty yard'];dirt=bpy.data.materials['R39 | Yard mud'].copy();dirt.name='CY | Authored yard earth transition'
nt=dirt.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');original=bs.inputs['Base Color'].links[0].from_socket
frame=nt.nodes.new('NodeFrame');frame.label='Courtyard dust transition'
geo=nt.nodes.new('ShaderNodeNewGeometry');xyz=nt.nodes.new('ShaderNodeSeparateXYZ');mp=nt.nodes.new('ShaderNodeMapRange');mix=nt.nodes.new('ShaderNodeMixRGB')
for j,n in enumerate((geo,xyz,mp,mix)):n.parent=frame;n.location=(j*220,0)
mp.inputs['From Min'].default_value=-31;mp.inputs['From Max'].default_value=-11;mp.inputs['To Min'].default_value=.88;mp.inputs['To Max'].default_value=1.65
mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1
nt.links.new(geo.outputs['Position'],xyz.inputs[0]);nt.links.new(xyz.outputs['X'],mp.inputs[0]);nt.links.new(original,mix.inputs[1]);nt.links.new(mp.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],bs.inputs['Base Color'])
for name in ('R39 | Apron mud','R39 | Gravel yard','R39 | Loose rocks yard'):
    o=bpy.data.objects[name]
    for j,m in enumerate(o.data.materials):
        if m==old:o.data.materials[j]=dirt

# Tone down paving variation and soften the obvious regular seams.
for i in range(4):
    m=bpy.data.materials['CY | Patched mineral concrete '+str(i)]
    ramp=next(n for n in m.node_tree.nodes if n.type=='VALTORGB')
    c=(.178+i*.004,.169+i*.003,.148+i*.002)
    for e,k in zip(ramp.color_ramp.elements,(.89,1.08)):e.color=(*(v*k for v in c),1)
    m.diffuse_color=(*c,1)
    ns=m.node_tree.nodes;fr=next(n for n in ns if n.type=='FRAME');bs=next(n for n in ns if n.type=='BSDF_PRINCIPLED')
    fine=ns.new('ShaderNodeTexNoise');fine.parent=fr;fine.location=(-200,-220);fine.inputs['Scale'].default_value=19;fine.inputs['Detail'].default_value=1.1
    bump=ns.new('ShaderNodeBump');bump.parent=fr;bump.location=(260,-220);bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.018
    m.node_tree.links.new(fine.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs[0],bs.inputs['Normal'])
for o in list(coll.objects):
    if o.name.startswith('CY | Patched yard slab'):
        # Close the coarse gaps to construction-width seams, retain actual joints.
        for v in o.data.vertices:
            v.co.x+=math.copysign(.014,v.co.x);v.co.y+=math.copysign(.014,v.co.y)
    if o.name.startswith(('CY | Drain collar','CY | Drain recess','CY | Drain grating bar')):
        centers=(-42.3,-32.9,-19.75,-13.15);cy=min(centers,key=lambda y:abs(y-o.location.y))
        o.location.x=-13.1+(o.location.x+13.1)*.74;o.location.y=cy+(o.location.y-cy)*.74;o.scale.x*=.74;o.scale.y*=.74

soil=bpy.data.materials['CY | Dark compacted verge'];aggregate=bpy.data.materials['CY | Charcoal ballast']
steel=bpy.data.materials['CY | Graphite structural steel']
stain=material('Tracked mineral dust',(.135,.119,.094),.94,variation=.16,scale=2.2)
edge=material('Dusty broken apron aggregate',(.125,.117,.099),.94,variation=.24,scale=1.1)

# Earthen shoulder behind rock clusters makes a landform border inside the fence.
vs=[];fs=[]
for j in range(14):
    x=-38+j*2.03
    for y,z in ((-47.6,-.17),(-46.7,.35+rng.uniform(0,.3)),(-45.3,.24+rng.uniform(0,.25)),(-43.9,-.05)):
        vs.append((x,y+rng.uniform(-.16,.16),z))
for j in range(13):
    for k in range(3):a=j*4+k;fs.extend(((a,a+4,a+5),(a,a+5,a+1)))
berm=mesh_obj('Fence-side compacted earth shoulder',vs,fs,dirt);berm['terrain_open_surface']=True

def patch(name,x,y,rx,ry,z,mat):
    # Irregular low profile deposit; quiet clusters, no repeated starbursts.
    n=13;vs=[(x,y,z)]
    for k in range(n):
        a=2*math.pi*k/n;r=rng.uniform(.83,1.07);vs.append((x+rx*math.cos(a)*r,y+ry*math.sin(a)*r,z-rng.uniform(0,.003)))
    ob=mesh_obj(name,vs,[(0,1+k,1+(k+1)%n) for k in range(n)],mat);ob['surface_decal']=True
    return ob
# Wind/traffic deposits spill across the rough paving edge, bridging the material seam.
for x,y,rx,ry in ((-18.6,-42.1,1.0,1.5),(-18.3,-37.8,.8,1.2),(-18.6,-34.7,.9,1.3),(-17.8,-25.5,1.3,1.7),(-18.2,-21.4,1.1,1.0),(-17.7,-17.3,1.0,1.1),(-17.7,-12.2,.9,.7)):
    patch('Silt at rough apron edge',x,y,rx,ry,.158,edge)
for x,y,rx,ry in ((-12.9,-40.7,.6,.23),(-14.9,-36.3,.95,.3),(-14.5,-26.3,.65,.31),(-16.1,-23,.95,.3),(-13,-19,.4,.7)):
    patch('Localized worn dust',x,y,rx,ry,.159,stain)

# Intermittent ballast stones and subdued edge scree reuse the same source family.
for i in range(66):
    if i<36:
        x=rng.uniform(-24,-11.4);y=-29+(-1 if i%2 else 1)*rng.uniform(.91,1.31);sz=rng.uniform(.065,.13)
    else:
        x=rng.uniform(-36,-14);y=rng.uniform(-44.8,-43.25);sz=rng.uniform(.12,.25)
    source=sources[i%3];o=source.copy();o.data=source.data;o.name='CY | Edge fieldstone %02d'%i;coll.objects.link(o);o.parent=None;o.matrix_world=Matrix.Identity(4)
    lo,hi=bounds(source);bb=[Vector(c) for c in source.bound_box];a=Vector(tuple(min(v[k] for v in bb) for k in range(3)));b=Vector(tuple(max(v[k] for v in bb) for k in range(3)))
    o.scale=(sz*2/(b.x-a.x),sz*1.7/(b.y-a.y),sz/(b.z-a.z));o.rotation_euler.z=rng.uniform(0,6.28)
    cen=o.rotation_euler.to_matrix()@Vector(((a.x+b.x)*.5*o.scale.x,(a.y+b.y)*.5*o.scale.y,a.z*o.scale.z))
    o.location=Vector((x,y,-.015))-cen;o.hide_render=False;o.hide_viewport=False;o.hide_set(False)

# Keep the authored path open and validate the corrected protected revision.
bpy.context.view_layer.update();objects={o.name_full:o for o in s.objects}
assert all(fingerprint(objects[n])==h for n,h in report['protected_fingerprints'].items())
for rec in report['rocks']:
    lo,hi=bounds(bpy.data.objects[rec['name']]);rec['bounds']=[lo,hi]
    if rec['position'][1]<-40:assert hi[1]<-41.3,(rec['name'],hi)
obstacles=[]
for o in coll.objects:
    if o.type=='MESH' and not o.get('terrain_open_surface'):
        lo,hi=bounds(o)
        if hi[2]>.35:obstacles.append((o,lo,hi))
for p in report['route_samples']:
    x,y=p['xy'];p['new_obstacles']=[o.name for o,lo,hi in obstacles if lo[0]-.45<x<hi[0]+.45 and lo[1]-.45<y<hi[1]+.45 and hi[2]>.35 and lo[2]<2]
assert not any(p['new_obstacles'] for p in report['route_samples'])
assert sha(SRC)==previous,'Concurrent source edit'
s.camera=bpy.data.objects['CY CAMERA | 01_CONCEPT'];bpy.ops.wm.save_as_mainfile(filepath=str(SRC),check_existing=False)
report['review_correction']={'previous_sha256':previous,'reason':'Independent review rejected pale photographic rocks and pristine grid paving; use existing slate fieldstones, quieter concrete, authored dirt shoulder and edge deposits. Earlier overview pixels are overwritten by corrected captures.'}
report['saved_sha256']=sha(SRC);(OUT/'build-verification.json').write_text(json.dumps(report,indent=2));print('COURTYARD_CORRECTED',report['saved_sha256'],flush=True)
manifest=dict(source=str(SRC),source_sha256=report['saved_sha256'],settings=report['settings'],views=[],complete=False)
for name in report['views']:
    s.camera=bpy.data.objects['CY CAMERA | '+name];p=OUT/(name+'.png');s.render.filepath=str(p);bpy.ops.render.render(write_still=True)
    manifest['views'].append(dict(name=name,path=str(p),sha256=sha(p),saved_camera=s.camera.name));(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print('COURTYARD_RENDER',name,flush=True)
manifest['complete']=True;manifest['source_unchanged']=sha(SRC)==report['saved_sha256'];(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
