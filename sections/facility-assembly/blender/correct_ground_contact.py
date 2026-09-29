"""Pixel-review correction: actual FACE-domain rock pigment and mineral contact."""
import bpy,json,hashlib,ctypes,math
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/ground-finish';SRC=Path(bpy.data.filepath);MAIN=SRC.with_name('facility_environment.blend');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((OUT/'verification.json').read_text());assert sha(SRC)==r['candidate_sha256'] and sha(MAIN)==r['before_sha256']
s=bpy.context.scene;s.frame_set(1);count=0
for name in r['changed']:
 if not name.startswith('CY | Existing boulder'):continue
 o=bpy.data.objects[name];a=o.data.attributes.get('r38c');assert a and a.domain=='FACE' and a.data_type=='FLOAT_COLOR'
 for p,d in zip(o.data.polygons,a.data):
  c=d.color;L=.2126*c[0]+.7152*c[1]+.0722*c[2];pos=o.matrix_world@p.center;dust=max(0,min(1,(.60-pos.z)/.60))*.48
  neutral=(L*1.38+.037,L*1.30+.031,L*1.13+.021);soil=(.13,.111,.083)
  d.color=(*(neutral[j]*(1-dust)+soil[j]*dust for j in range(3)),c[3]);count+=1
ground=bpy.data.objects['R39 | Apron mud'];me=ground.data
attr=me.color_attributes.new(name='GF_MineralContact',domain='POINT',type='FLOAT_COLOR')
for v,d in zip(me.vertices,attr.data):
 p=ground.matrix_world@v.co;along=max(0,min(1,(p.x+38.3)/1.5))*max(0,min(1,(-17-p.x)/3));edge=max(0,min(1,(-42.3-p.y)/2.1))
 patch=max(0,min(1,.53+.24*math.sin(p.x*2.3+p.y*1.3)+.19*math.sin(p.x*.8-p.y*3.1)))
 d.color=(.145,.13,.103,along*edge*patch*.62)
for i,original in enumerate(list(me.materials)):
 if not original:continue
 m=original.copy();m.name='GF | Ground Contact '+str(i);nt=m.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL');link=next(l for l in nt.links if l.to_socket==bs.inputs['Base Color']);source=link.from_socket
 frame=bs.parent
 if frame is None:
  frame=nt.nodes.new('NodeFrame');frame.label='Mineral Ground Contact';bs.parent=frame;out.parent=frame
  # Only this local output region is formatted; inherited upstream graph retained.
  maxx=max((n.location.x+n.width for n in nt.nodes if n.type!='FRAME' and n not in (bs,out)),default=0);frame.location=(maxx+220,0)
  bs.location=(460,0);out.location=(700,0)
  vx,mx=0,230
 else:
  bs.location=(1710,0);out.location=(1970,0);vx,mx=1190,1450
 a=nt.nodes.new('ShaderNodeVertexColor');a.layer_name=attr.name;a.parent=frame;a.location=(vx,280);a.width=160
 mix=nt.nodes.new('ShaderNodeMixRGB');mix.parent=frame;mix.location=(mx,0);mix.width=160
 nt.links.new(a.outputs['Alpha'],mix.inputs[0]);nt.links.new(source,mix.inputs[1]);nt.links.new(a.outputs['Color'],mix.inputs[2]);nt.links.new(mix.outputs[0],bs.inputs['Base Color']);me.materials[i]=m
r['changed'].append(ground.name_full);r['contact_corrected']=dict(face_pigments=count,ground_vertices=len(me.vertices),geometry_changed=False)
assert sha(MAIN)==r['before_sha256'];bpy.ops.wm.save_as_mainfile(filepath=str(SRC),check_existing=False);r['candidate_sha256']=sha(SRC);(OUT/'verification.json').write_text(json.dumps(r,indent=2))
s.camera=bpy.data.objects['GF CAMERA | mine-cliff-yard'];s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=4;s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.filepath=str(OUT/'mine-cliff-yard.png');bpy.ops.render.render(write_still=True);print('CONTACT_CORRECTED',count,flush=True)
