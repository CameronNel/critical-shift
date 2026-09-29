"""Bounded courtyard pass from approved concept. Single worker, CPU only.

Never executes a historical scene generator. Existing mine, cliff and buildings
are protected; only explicitly named exterior ground/track datablocks may change.
"""
import bpy, bmesh, math, random, json, hashlib, ctypes, shutil, sys
import numpy as np
from pathlib import Path
from mathutils import Vector, Matrix

ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runtime/out/environment/courtyard'; OUT.mkdir(parents=True,exist_ok=True)
SRC=Path(bpy.data.filepath); sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
initial_sha=sha(SRC)
expected=json.loads((OUT/'inventory.json').read_text())['sha256']
assert initial_sha==expected, 'Source changed after inspection; stop for reconciliation'
BACKUP=SRC.with_name('facility_environment.courtyard-before.blend')
if BACKUP.exists():assert sha(BACKUP)==initial_sha, 'Different checkpoint exists; do not overwrite it'
else:shutil.copy2(SRC,BACKUP)
s=bpy.context.scene;s.frame_set(s.frame_current);bpy.context.view_layer.update()
rng=random.Random(927)

def fingerprint(o):
    h=hashlib.sha256();h.update(np.asarray(o.matrix_world,dtype=np.float64).tobytes())
    h.update(str((o.hide_render,o.hide_viewport,o.hide_get(),o.type)).encode())
    if o.type=='MESH':
        a=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',a);h.update(a.tobytes())
        a=np.empty(len(o.data.loops),np.int32);o.data.loops.foreach_get('vertex_index',a);h.update(a.tobytes())
        a=np.empty(len(o.data.polygons),np.int32);o.data.polygons.foreach_get('material_index',a);h.update(a.tobytes())
        h.update(str([m.name_full if m else None for m in o.data.materials]).encode())
        for uv in o.data.uv_layers:
            a=np.empty(len(uv.data)*2,np.float32);uv.data.foreach_get('uv',a);h.update(a.tobytes())
    elif o.type=='LIGHT':h.update(str((o.data.energy,tuple(o.data.color),o.data.type)).encode())
    elif o.type=='FONT':h.update(str((o.data.body,o.data.size)).encode())
    return h.hexdigest()

original_objects={o.name_full:o for o in s.objects}
before={n:fingerprint(o) for n,o in original_objects.items()}
libraries={bpy.path.abspath(l.filepath):sha(bpy.path.abspath(l.filepath)) for l in bpy.data.libraries}
original_materials={m.name_full:m for m in bpy.data.materials}
def material_sig(m):
    data=[list(m.diffuse_color),m.use_nodes]
    if m.use_nodes:
        for n in m.node_tree.nodes:
            vals=[]
            for v in n.inputs:
                if hasattr(v,'default_value'):
                    q=v.default_value
                    try:q=list(q)
                    except TypeError:pass
                    vals.append((v.identifier,q))
            data.append((n.name,n.bl_idname,vals,n.image.filepath if n.type=='TEX_IMAGE' and n.image else None))
        data.append([(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links])
    return hashlib.sha256(repr(data).encode()).hexdigest()
mat_before={n:material_sig(m) for n,m in original_materials.items()}
print('PRESERVATION_BASELINE',len(before),'objects',flush=True)

coll=bpy.data.collections.new('ART | Courtyard mine-to-refinery');s.collection.children.link(coll)
changed=set();rock_records=[];slabs=[]
def mesh_obj(name,vs,fs,mat):
    me=bpy.data.meshes.new('CY | '+name);me.from_pydata(vs,[],fs);me.update()
    ob=bpy.data.objects.new(me.name,me);coll.objects.link(ob)
    if mat:me.materials.append(mat)
    return ob
def box(name,p,dim,mat,bevel=0,angle=0):
    bm=bmesh.new();bmesh.ops.create_cube(bm,size=1)
    for v in bm.verts:v.co=Vector((v.co.x*dim[0],v.co.y*dim[1],v.co.z*dim[2]))
    if bevel:bmesh.ops.bevel(bm,geom=list(bm.edges),offset=bevel,segments=2,affect='EDGES',clamp_overlap=True)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    me=bpy.data.meshes.new('CY | '+name);bm.to_mesh(me);bm.free();me.materials.append(mat)
    ob=bpy.data.objects.new(me.name,me);coll.objects.link(ob);ob.location=p;ob.rotation_euler.z=angle
    return ob
def beam(name,a,b,w,d,mat):
    a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(w,d,(b-a).length),mat,.006);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def cylinder(name,p,r,depth,mat,axis='Z',vertices=16):
    bm=bmesh.new();bmesh.ops.create_cone(bm,cap_ends=True,cap_tris=False,segments=vertices,radius1=r,radius2=r,depth=depth)
    me=bpy.data.meshes.new('CY | '+name);bm.to_mesh(me);bm.free();me.materials.append(mat)
    ob=bpy.data.objects.new(me.name,me);coll.objects.link(ob);ob.location=p
    if axis=='Y':ob.rotation_euler.x=math.pi/2
    if axis=='X':ob.rotation_euler.y=math.pi/2
    return ob

def material(name,col,rough=.8,metal=0,variation=.12,scale=.55):
    m=bpy.data.materials.new('CY | '+name);m.diffuse_color=(*col,1);m.use_nodes=True
    nt=m.node_tree;nt.nodes.clear();fr=nt.nodes.new('NodeFrame');fr.label='Broad authored material variation'
    ns=[]
    for typ in ('ShaderNodeTexNoise','ShaderNodeValToRGB','ShaderNodeBsdfPrincipled','ShaderNodeOutputMaterial'):
        n=nt.nodes.new(typ);n.parent=fr;n.location=(len(ns)*240,0);ns.append(n)
    noise,ramp,bs,out=ns;noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=1.0
    for e,k in zip(ramp.color_ramp.elements,(1-variation,1+variation)):e.color=(*(v*k for v in col),1)
    bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
    nt.links.new(noise.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color']);nt.links.new(bs.outputs[0],out.inputs[0])
    return m
concrete=[material('Patched mineral concrete '+str(i),c,.87,variation=.065,scale=.8) for i,c in enumerate(((.29,.275,.245),(.32,.30,.26),(.265,.257,.237),(.35,.323,.28)))]
steel=material('Graphite structural steel',(.047,.054,.056),.69,.48,.09)
ochre=material('Worn ochre enamel',(.43,.265,.071),.78,.1,.15)
olive=material('Old olive utility enamel',(.12,.14,.10),.81,.1,.13)
soil=material('Dark compacted verge',(.084,.075,.064),.94,variation=.19,scale=.8)
aggregate=material('Charcoal ballast',(.09,.086,.081),.94,variation=.22,scale=1.4)
rust=material('Oxidised seams',(.19,.091,.043),.87,.1,.12)
timber=bpy.data.materials['R39 | Creosote sleepers']
railmat=bpy.data.materials['R39 | Rail steel']

# Local ground colour transition. The shed footprint keeps its original slot.
ground=material('Mine earth to dusty yard',(.14,.123,.103),.94,variation=.16,scale=.7)
nt=ground.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');fr=next(n for n in nt.nodes if n.type=='FRAME')
geo=nt.nodes.new('ShaderNodeNewGeometry');geo.parent=fr;geo.location=(-720,-260)
xyz=nt.nodes.new('ShaderNodeSeparateXYZ');xyz.parent=fr;xyz.location=(-490,-260)
mp=nt.nodes.new('ShaderNodeMapRange');mp.parent=fr;mp.location=(-240,-260);mp.inputs['From Min'].default_value=-30;mp.inputs['From Max'].default_value=-11
cr=nt.nodes.new('ShaderNodeValToRGB');cr.parent=fr;cr.location=(10,-260)
cr.color_ramp.elements[0].color=(.072,.065,.059,1);cr.color_ramp.elements[1].color=(.245,.214,.167,1)
nt.links.new(geo.outputs['Position'],xyz.inputs[0]);nt.links.new(xyz.outputs['X'],mp.inputs[0]);nt.links.new(mp.outputs[0],cr.inputs[0]);nt.links.new(cr.outputs[0],bs.inputs['Base Color'])

def in_mine(x,y):return x<-22.0 and -38.1<y<-19.5
def paved(x,y):return -19.0<x<-10.95 and -44.0<y<-10.0 and abs(y+29)>1.22
for name in ('R39 | Apron mud','R39 | Gravel yard','R39 | Loose rocks yard'):
    o=bpy.data.objects[name];o.data=o.data.copy();changed.add(o.name_full)
    o.data.materials.append(ground if name.endswith('mud') else aggregate);idx=len(o.data.materials)-1
    for p in o.data.polygons:
        c=o.matrix_world@p.center
        if not in_mine(c.x,c.y):p.material_index=idx

# Paving: broad patchwork slabs with irregular cut western edge, narrow joints.
ys=[(-43.8,-40.8),(-40.8,-37.8),(-37.8,-34.8),(-34.8,-31.0),(-27.5,-24.4),(-24.4,-21.3),(-21.3,-18.2),(-18.2,-15.1),(-15.1,-11.2)]
for j,(ya,yb) in enumerate(ys):
    west=(-18.8,-17.7,-19.1,-18.3,-19.0,-18.5,-17.9,-18.6,-17.6)[j]
    # Deliberate varied panels, not identical floor tiles.
    edges=(west,-14.9,-10.95)
    for i in range(2):
        xa,xb=edges[i]+.018,edges[i+1]-.018;cy=(ya+yb)/2
        o=box('Patched yard slab %02d-%d'%(j,i),((xa+xb)/2,cy,.055),(xb-xa,yb-ya-.036,.19),concrete[(i+j)%4],.014)
        slabs.append((xa,xb,ya+.018,yb-.018,.15))
    # Drain located on the eastern half of paving; concrete collar and dark grate.
    if j in (1,3,6,8):
        gx,gy=-13.1,cy
        box('Drain collar',(gx,gy,.154),(.91,.68,.06),concrete[2],.015)
        box('Drain recess',(gx,gy,.188),(.73,.5,.018),steel,.008)
        for k in range(9):box('Drain grating bar',(gx-.31+k*.078,gy,.205),(.028,.47,.025),steel,.004)
    # Sparse chipped wayfinding at route shoulder.
    for k in range(3):
        box('Faded route shoulder',(-11.4,ya+.3+k*.7,.154),(.12,.49,.007),ochre,.001)

# Flush cross-track bridge: keep flangeways and rail heads exposed.
for yy,ww in ((-30.35,.8),(-29.0,.87),(-27.65,.8)):
    box('Level crossing infill',(-12.6,yy,.085),(2.7,ww,.13),concrete[2],.012)

# Carry mine rail and sleeper materials to the existing refinery connection.
for o in list(s.objects):
    if not o.name.startswith('MTRACK | ') or o.hide_render or not o.visible_get():continue
    if 'mine approach' in o.name.lower():continue
    if any(t in o.name for t in ('Continuous rail','Cast tie','Continuous supported track bed','Rail chair','Rail foot keeper','Keeper bolt')):
        o.data=o.data.copy();changed.add(o.name_full)
        mat=railmat if 'Continuous rail' in o.name else timber if 'Cast tie' in o.name else aggregate if 'track bed' in o.name else bpy.data.materials['R39 | Rusted iron']
        o.data.materials.clear();o.data.materials.append(mat)
        if 'Cast tie' in o.name:
            for v in o.data.vertices:
                v.co.x*=1.22;v.co.y*=1.11;v.co.z=v.co.z*1.45-.012
            uv=o.data.uv_layers.get('UVMap') or o.data.uv_layers.new(name='UVMap')
            for p in o.data.polygons:
                for li in p.loop_indices:
                    co=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(co.x*2,co.y)
        for an in ('r39v','r39w','r39j','r38e','r39t'):
            at=o.data.attributes.get(an) or o.data.attributes.new(an,'FLOAT','FACE')
            for p in o.data.polygons:at.data[p.index].value=(1 if an=='r39t' and p.normal.z>.7 else .35 if an=='r38e' else .15)

# Existing boulders: shared meshes/materials, grounded varied copies inside fence.
rock_sources=[bpy.data.objects['R38 CC0 source | '+n] for n in ('namaqualand_boulder_05','namaqualand_boulder_02','boulder_01')]
def rock(i,x,y,dx,dy,dz,angle):
    source=rock_sources[i%3];o=source.copy();o.data=source.data;o.name='CY | Existing boulder %02d'%i;coll.objects.link(o)
    o.hide_render=False;o.hide_viewport=False;o.hide_set(False);o.parent=None;o.matrix_world=Matrix.Identity(4)
    bb=[Vector(c) for c in source.bound_box];lo=Vector(tuple(min(v[a] for v in bb) for a in range(3)));hi=Vector(tuple(max(v[a] for v in bb) for a in range(3)))
    o.scale=(dx/(hi.x-lo.x),dy/(hi.y-lo.y),dz/(hi.z-lo.z));o.rotation_euler=(0,0,angle)
    R=o.rotation_euler.to_matrix();cen=R@Vector(((lo.x+hi.x)*.5*o.scale.x,(lo.y+hi.y)*.5*o.scale.y,lo.z*o.scale.z))
    o.location=Vector((x,y,-.10))-cen
    o['courtyard_source']=source.name;o['purpose']='Left fence screen' if y<-40 else 'Northern service edge'
    rock_records.append(dict(name=o.name,source=source.name,mesh=source.data.name,position=[x,y],dimensions=[dx,dy,dz]))
    return o
placements=[(-36.4,-46.4,4.7,3.1,2.7),(-32.9,-46.1,4.6,3.1,3.0),(-29.3,-46.6,4.7,3.0,2.5),(-25.9,-46.5,4.1,2.9,2.3),(-22.8,-46.9,4.4,2.6,2.6),(-19.4,-46.6,4.0,2.8,2.0),(-16.2,-46.8,3.9,2.8,1.8),(-12.9,-47.1,3.5,2.5,1.6),(-35.1,-44.3,3.6,2.4,1.6),(-30.9,-44.4,3.4,2.2,1.8),(-26.5,-44.4,3.0,2.2,1.3),(-21.2,-45.1,3.1,2.0,1.4),(-17.8,-45,2.6,1.8,1.1),(-35.2,-12.0,4.5,3.4,2.2),(-31.1,-11.7,4.0,3.0,1.9)]
for i,p in enumerate(placements):rock(i,*p,rng.uniform(-.33,.33))

# Grounded low retaining bay at northern edge; it occupies non-route space.
for j in range(4):
    x=-29.5+j*2.5
    box('Retaining foundation',(x,-12.55,.02),(2.5,.9,.28),concrete[2],.035)
    box('Retaining panel',(x,-12.55,.67),(2.47,.43,1.28),concrete[(j+1)%4],.028)
    box('Retaining coping',(x,-12.55,1.34),(2.49,.55,.13),concrete[0],.025)
    box('Retaining footing stain',(x,-12.785,.22),(2.28,.015,.21),soil,.003)
    if j in (0,3):box('Retaining end warning',(x,-12.794,.89),(.12,.012,.47),ochre,.002)
box('Retaining return',(-19.6,-11.45,.67),(.44,2.6,1.28),concrete[1],.026)

# Sleeper storage: rested on bearers, banded as a purposeful working cluster.
for xx in (-28.1,-26.5):box('Stack bearer',(xx,-15.0,.18),(.23,2.45,.24),timber,.013)
for level in range(3):
    for j in range(6):
        ob=box('Stored sleeper',(-27.3,-16.0+j*.37,.40+level*.19),(2.8,.30,.18),timber,.018,angle=.006*(j-2))
        uv=ob.data.uv_layers.new(name='UVMap')
        for lp in ob.data.loops:
            v=ob.data.vertices[lp.vertex_index].co;uv.data[lp.index].uv=(v.y,v.x)
for xx in (-28.25,-26.35):
    box('Stack retaining band top',(xx,-15.06,.88),(.045,2.22,.014),steel,.002)
    for yy in (-16.17,-13.95):box('Stack retaining band side',(xx,yy,.58),(.045,.014,.61),steel,.002)

# Ore skip: tapered folded vessel, rim, ribs, underframe, wheels and contained ore.
cx,cy=-22.8,-16.1
box('Skip parking plinth',(cx,cy,.09),(3.4,2.7,.18),concrete[2],.02)
box('Ore skip underframe',(cx,cy,.47),(2.65,1.8,.22),steel,.025)
for xx in (cx-.91,cx+.91):
    cylinder('Skip axle',(xx,cy,.40),.07,2.1,steel,'Y')
    for yy in (cy-1.0,cy+1.0):
        cylinder('Skip wheel',(xx,yy,.40),.30,.15,steel,'Y',20)
        cylinder('Skip hub',(xx,yy+(.09 if yy>cy else -.09),.40),.11,.03,rust,'Y')
# Vessel has separate thick trapezoid panels, not a solid box.
bottom=[(cx-1.13,cy-.68,.62),(cx+1.13,cy-.68,.62),(cx+1.13,cy+.68,.62),(cx-1.13,cy+.68,.62)]
top=[(cx-1.48,cy-.96,1.70),(cx+1.48,cy-.96,1.70),(cx+1.48,cy+.96,1.70),(cx-1.48,cy+.96,1.70)]
box('Skip bottom',(cx,cy,.63),(2.30,1.38,.065),olive,.006)
for i in range(4):
    j=(i+1)%4;outer=[bottom[i],bottom[j],top[j],top[i]]
    inner=[(x+(cx-x)*.021,y+(cy-y)*.028,z) for x,y,z in outer]
    o=mesh_obj('Tapered skip panel',outer+inner,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],olive)
    beam('Skip rolled rim',top[i],top[j],.09,.09,rust)
    beam('Skip corner rib',bottom[i],top[i],.07,.07,steel)
for xx in (cx-.65,cx+.65):
    for side in (-1,1):beam('Skip reinforcing rib',(xx,cy+side*.69,.64),(xx,cy+side*.965,1.68),.065,.055,steel)
for i in range(9):
    bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=1,radius=1)
    for v in bm.verts:v.co=Vector((v.co.x*rng.uniform(.25,.4),v.co.y*.27,v.co.z*.24))
    me=bpy.data.meshes.new('CY | Contained ore');bm.to_mesh(me);bm.free();me.materials.append(aggregate)
    ob=bpy.data.objects.new(me.name,me);coll.objects.link(ob);ob.location=(cx-.95+(i%3)*.87,cy-.48+(i//3)*.45,1.39+rng.uniform(-.05,.09))

# A compact disconnected pump assembly on the south storage edge.
px,py=-21.0,-42.0
box('Pump skid',(px,py,.20),(2.25,1.0,.20),steel,.018)
for xx in (px-.8,px+.8):box('Skid bearer',(xx,py,.08),(.2,1.25,.17),concrete[2],.012)
cylinder('Pump motor',(px-.38,py,.60),.32,.87,olive,'X',24)
for xx in np.linspace(px-.79,px+.01,8):cylinder('Motor cooling rib',(float(xx),py,.60),.345,.035,steel,'X',24)
cylinder('Volute housing',(px+.52,py,.60),.39,.30,olive,'X',20)
cylinder('Capped discharge',(px+.52,py,1.05),.105,.38,steel)
cylinder('Discharge blank flange',(px+.52,py,1.25),.16,.045,rust)
box('Motor junction box',(px-.38,py,.95),(.31,.29,.15),olive,.018)

# Small ballast shoulder patches extend the existing bed; centre stays clear.
for side in (-1,1):
    for j in range(6):box('Track ballast shoulder',(-23.1+j*2.0,-29+side*1.01,.002),(1.98,.28,.10),aggregate,.025)

# Saved reproducible review cameras. Main oblique includes the fence-side extension.
views={
 '01_CONCEPT':((14,-64,33),(-22,-26,1),43),
 '02_LEFT_EDGE':((-12,-43,1.85),(-34,-43,1.55),25),
 '03_APPROACH':((-9,-32.8,1.85),(-27,-29,1.8),24),
 '04_REVERSE':((-22,-25,1.8),(-11,-16,1.3),24),
}
for name,(pos,target,lens) in views.items():
    cd=bpy.data.cameras.new('CY CAMERA | '+name);cam=bpy.data.objects.new(cd.name,cd);coll.objects.link(cam)
    cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;cd.clip_start=.08;cd.clip_end=2000
s.camera=bpy.data.objects['CY CAMERA | 01_CONCEPT']
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=12;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.cycles.seed=73
s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.frame_set(1)
bpy.context.view_layer.update()

# Geometry and preservation gates before saving.
def bounds(o):
    bb=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [min(v[i] for v in bb) for i in range(3)],[max(v[i] for v in bb) for i in range(3)]
for rec in rock_records:
    lo,hi=bounds(bpy.data.objects[rec['name']]);rec['bounds']=[lo,hi]
    assert abs(lo[2]+.10)<1e-4
    if rec['position'][1]<-40:assert hi[1]<-41.3, ('South route blocked',rec)
protected_changes=[n for n,h in before.items() if n not in changed and fingerprint(original_objects[n])!=h]
assert not protected_changes,protected_changes
assert all(material_sig(m)==mat_before[n] for n,m in original_materials.items()), 'Original material changed'
assert all(sha(p)==h for p,h in libraries.items()),'Library changed concurrently'
mesh_errors=[]
for o in coll.objects:
    if o.type!='MESH' or o.name.startswith('CY | Existing boulder'):continue
    bm=bmesh.new();bm.from_mesh(o.data)
    bad=sum(1 for e in bm.edges if not e.is_manifold);deg=sum(1 for f in bm.faces if f.calc_area()<1e-10)
    bm.free()
    if bad or deg:mesh_errors.append((o.name,bad,deg))
assert not mesh_errors,mesh_errors
# Route probes against NEW raised obstacles; existing rail infrastructure retained.
obstacles=[]
for o in coll.objects:
    if o.type=='MESH':
        lo,hi=bounds(o)
        if hi[2]>.35:obstacles.append((o,lo,hi))
paths={
 'rail-side south':[(-22+i*.5,-32.5) for i in range(24)],
 'south mine service':[(-35+i*.5,-39.65) for i in range(46)],
 'north mine service':[(-35+i*.5,-18.15) for i in range(44)],
 'north-south courtyard':[(-17.1,-40+i*.5) for i in range(47)],
}
route_failures=[];route_samples=[]
for name,pts in paths.items():
    for x,y in pts:
        blockers=[o.name for o,lo,hi in obstacles if lo[0]-.45<x<hi[0]+.45 and lo[1]-.45<y<hi[1]+.45 and hi[2]>.35 and lo[2]<2.0]
        if blockers:route_failures.append((name,[x,y],blockers))
        route_samples.append(dict(route=name,xy=[x,y],new_obstacles=blockers))
assert not route_failures,route_failures
assert sha(SRC)==initial_sha,'Source changed concurrently; refuse overwrite'
report=dict(source=str(SRC),before_sha256=initial_sha,backup=str(BACKUP),changed_original_objects=sorted(changed),protected_objects=len(before)-len(changed),protected_changes=protected_changes,original_materials_unchanged=True,libraries=libraries,rocks=rock_records,manufactured_mesh_errors=mesh_errors,route_samples=route_samples,route_probe_radius=.45,route_probe_height=1.8,limitations='New-obstacle AABB clearance only; runtime collision/navmesh not tested.',concept=str(ROOT/'sections/facility-assembly/concepts/mine-refinery-transition-valorant-fidelity-v3.png'),settings=dict(engine='CYCLES',device='CPU',threads=1,width=1280,height=720,samples=12,seed=73,denoiser='OPENIMAGEDENOISE',denoising_use_gpu=False),views=views)
bpy.ops.wm.save_as_mainfile(filepath=str(SRC),check_existing=False)
report['saved_sha256']=sha(SRC);report['protected_fingerprints']={n:h for n,h in before.items() if n not in changed}
(OUT/'build-verification.json').write_text(json.dumps(report,indent=2))
print('COURTYARD_SAVED',report['saved_sha256'],len(coll.objects),'new objects',flush=True)
manifest=dict(source=str(SRC),source_sha256=report['saved_sha256'],settings=report['settings'],views=[],complete=False)
for name in views:
    s.camera=bpy.data.objects['CY CAMERA | '+name];p=OUT/(name+'.png');s.render.filepath=str(p)
    bpy.ops.render.render(write_still=True)
    manifest['views'].append(dict(name=name,path=str(p),sha256=sha(p),saved_camera=s.camera.name))
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print('COURTYARD_RENDER',name,flush=True)
manifest['complete']=True;manifest['source_unchanged']=sha(SRC)==report['saved_sha256'];(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
