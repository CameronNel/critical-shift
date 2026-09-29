"""Final bounded surface cleanup: original boulder copies, continuous dirt blending."""
import bpy, math, json, hashlib, ctypes, random
from pathlib import Path
from mathutils import Vector,Matrix
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/courtyard';SRC=Path(bpy.data.filepath)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();report=json.loads((OUT/'build-verification.json').read_text());before=sha(SRC)
assert before==report['saved_sha256']
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();coll=bpy.data.collections['ART | Courtyard mine-to-refinery'];rng=random.Random(2909)
def node(nt,frame,kind,x,y):
    n=nt.nodes.new(kind);n.parent=frame;n.location=(x,y);return n
rockmat=bpy.data.materials.new('CY | Matte dark slate boulder');rockmat.use_nodes=True;nt=rockmat.node_tree;nt.nodes.clear();fr=nt.nodes.new('NodeFrame');fr.label='Slate geology broad colour and shallow relief'
n=node(nt,fr,'ShaderNodeTexNoise',0,0);n.inputs['Scale'].default_value=1.8;n.inputs['Detail'].default_value=1.2
cr=node(nt,fr,'ShaderNodeValToRGB',230,0);cr.color_ramp.elements[0].color=(.045,.05,.057,1);cr.color_ramp.elements[1].color=(.125,.126,.123,1)
bs=node(nt,fr,'ShaderNodeBsdfPrincipled',690,0);bs.inputs['Roughness'].default_value=.91;bs.inputs['Specular IOR Level'].default_value=.22
out=node(nt,fr,'ShaderNodeOutputMaterial',960,0)
fine=node(nt,fr,'ShaderNodeTexNoise',0,-220);fine.inputs['Scale'].default_value=12;fine.inputs['Detail'].default_value=1
bump=node(nt,fr,'ShaderNodeBump',460,-220);bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.009
nt.links.new(n.outputs['Fac'],cr.inputs[0]);nt.links.new(cr.outputs[0],bs.inputs['Base Color']);nt.links.new(fine.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],bs.inputs['Normal']);nt.links.new(bs.outputs[0],out.inputs[0]);rockmat.diffuse_color=(.085,.09,.095,1)
sources=[bpy.data.objects['R38 CC0 source | '+n] for n in ('namaqualand_boulder_05','namaqualand_boulder_02','boulder_01')]
for i,rec in enumerate(report['rocks']):
    o=bpy.data.objects[rec['name']];source=sources[i%3];o.data=source.data
    dx,dy,dz=rec['dimensions'];x,y=rec['position'];bb=[Vector(c) for c in source.bound_box]
    lo=Vector(tuple(min(v[a] for v in bb) for a in range(3)));hi=Vector(tuple(max(v[a] for v in bb) for a in range(3)))
    o.scale=(dx/(hi.x-lo.x),dy/(hi.y-lo.y),dz/(hi.z-lo.z));o.rotation_euler=(0,0,rng.uniform(-.33,.33))
    cen=o.rotation_euler.to_matrix()@Vector(((lo.x+hi.x)*.5*o.scale.x,(lo.y+hi.y)*.5*o.scale.y,lo.z*o.scale.z));o.location=Vector((x,y,-.16))-cen
    for slot in o.material_slots:slot.link='OBJECT';slot.material=rockmat
    o['courtyard_source']=source.name;rec.update(source=source.name,mesh=source.data.name,material_override=rockmat.name)
for o in list(coll.objects):
    if o.name.startswith('CY | Edge fieldstone'):
        for slot in o.material_slots:slot.link='OBJECT';slot.material=rockmat
    if o.name.startswith(('CY | Silt at rough apron edge','CY | Localized worn dust')):
        bpy.data.objects.remove(o,do_unlink=True)

# Blend actual surface colour continuously, avoiding opaque deposit polygons.
for i in range(4):
    m=bpy.data.materials['CY | Patched mineral concrete '+str(i)];nt=m.node_tree;nt.nodes.clear();fr=nt.nodes.new('NodeFrame');fr.label='Worn apron concrete with graded tracked soil'
    geo=node(nt,fr,'ShaderNodeNewGeometry',0,0);xyz=node(nt,fr,'ShaderNodeSeparateXYZ',220,0)
    mp=node(nt,fr,'ShaderNodeMapRange',430,0);mp.inputs['From Min'].default_value=-19.7;mp.inputs['From Max'].default_value=-13.9
    ns=node(nt,fr,'ShaderNodeTexNoise',220,-220);ns.inputs['Scale'].default_value=.67;ns.inputs['Detail'].default_value=1.5
    mul=node(nt,fr,'ShaderNodeMath',440,-220);mul.operation='MULTIPLY';mul.inputs[1].default_value=.55
    sub=node(nt,fr,'ShaderNodeMath',660,0);sub.operation='SUBTRACT'
    mask=node(nt,fr,'ShaderNodeMapRange',880,0);mask.inputs['From Min'].default_value=-.12;mask.inputs['From Max'].default_value=.48
    col=node(nt,fr,'ShaderNodeMixRGB',1100,0);col.inputs[1].default_value=(.055,.046,.035,1);col.inputs[2].default_value=(.177+i*.003,.164+i*.002,.140+i*.002,1)
    bs=node(nt,fr,'ShaderNodeBsdfPrincipled',1350,0);bs.inputs['Roughness'].default_value=.88;bs.inputs['Specular IOR Level'].default_value=.22
    out=node(nt,fr,'ShaderNodeOutputMaterial',1620,0)
    fine=node(nt,fr,'ShaderNodeTexNoise',660,-240);fine.inputs['Scale'].default_value=9;fine.inputs['Detail'].default_value=1.4
    bump=node(nt,fr,'ShaderNodeBump',1100,-240);bump.inputs['Strength'].default_value=.19;bump.inputs['Distance'].default_value=.012
    links=[(geo.outputs['Position'],xyz.inputs[0]),(geo.outputs['Position'],ns.inputs[0]),(xyz.outputs['X'],mp.inputs[0]),(ns.outputs['Fac'],mul.inputs[0]),(mp.outputs[0],sub.inputs[0]),(mul.outputs[0],sub.inputs[1]),(sub.outputs[0],mask.inputs[0]),(mask.outputs[0],col.inputs[0]),(col.outputs[0],bs.inputs['Base Color']),(geo.outputs['Position'],fine.inputs[0]),(fine.outputs['Fac'],bump.inputs['Height']),(bump.outputs[0],bs.inputs['Normal']),(bs.outputs[0],out.inputs[0])]
    for a,b in links:nt.links.new(a,b)

# Align skip wheel contact to the parking pad, including its rigid assembly.
for o in coll.objects:
    if o.name.startswith(('CY | Ore skip underframe','CY | Skip axle','CY | Skip wheel','CY | Skip hub','CY | Skip bottom','CY | Tapered skip panel','CY | Skip rolled rim','CY | Skip corner rib','CY | Skip reinforcing rib','CY | Contained ore')):o.location.z+=.08
bpy.context.view_layer.update()
for rec in report['rocks']:
    o=bpy.data.objects[rec['name']];bb=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(v[i] for v in bb) for i in range(3)];hi=[max(v[i] for v in bb) for i in range(3)];rec['bounds']=[lo,hi]
    if rec['position'][1]<-40:assert hi[1]<-41.3
assert sha(SRC)==before
s.camera=bpy.data.objects['CY CAMERA | 01_CONCEPT'];bpy.ops.wm.save_as_mainfile(filepath=str(SRC),check_existing=False)
report['surface_cleanup']={'previous_sha256':before,'changes':'Source boulder meshes reused with local matte slate material; opaque dirt patch overlays removed in favour of shader blending; ore skip wheels aligned to parking plinth.'};report['saved_sha256']=sha(SRC);(OUT/'build-verification.json').write_text(json.dumps(report,indent=2));print('COURTYARD_SURFACES_SAVED',report['saved_sha256'],flush=True)
manifest=dict(source=str(SRC),source_sha256=report['saved_sha256'],settings=report['settings'],views=[],complete=False)
for name in ('02_LEFT_EDGE','03_APPROACH','04_REVERSE','01_CONCEPT'):
    s.camera=bpy.data.objects['CY CAMERA | '+name];p=OUT/(name+'.png');s.render.filepath=str(p);bpy.ops.render.render(write_still=True)
    manifest['views'].append(dict(name=name,path=str(p),sha256=sha(p),saved_camera=s.camera.name));(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print('COURTYARD_RENDER',name,flush=True)
manifest['complete']=True;manifest['source_unchanged']=sha(SRC)==report['saved_sha256'];(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
