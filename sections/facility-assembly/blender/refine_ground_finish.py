"""Revision-guarded, roof-excluded finish. Run floor, then rest after pixel review."""
import bpy,ast,json,hashlib,ctypes,shutil,sys,math
import numpy as np
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/ground-finish';MAIN=Path(__file__).with_name('facility_environment.blend');SRC=Path(bpy.data.filepath)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
stage=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'floor'
inspection=json.loads((OUT/'inspection.json').read_text());assert sha(MAIN)==inspection['sha256'],'Concurrent edit'
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
for fn in ('fingerprint','material_sig'):
 tree=ast.parse(Path(__file__).with_name('build_transition_courtyard.py').read_text());fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==fn);exec(compile(ast.Module(body=[fun],type_ignores=[]),'<audit>','exec'))
def geom_sig(o):
 h=hashlib.sha256();h.update(np.asarray(o.matrix_world,dtype=np.float64).tobytes())
 if o.type=='MESH':
  for seq,field,dtype,n in ((o.data.vertices,'co',np.float32,3),(o.data.loops,'vertex_index',np.int32,1)):
   a=np.empty(len(seq)*n,dtype);seq.foreach_get(field,a);h.update(a.tobytes())
 return h.hexdigest()
def strongmat(m):
 return hashlib.sha256((material_sig(m)+repr([(n.name,[(e.position,tuple(e.color)) for e in n.color_ramp.elements]) for n in m.node_tree.nodes if n.type=='VALTORGB'] if m.use_nodes else [])).encode()).hexdigest()
if stage=='floor':
 backup=MAIN.with_name('facility_environment.ground-before.blend')
 if backup.exists():assert sha(backup)==sha(MAIN)
 else:shutil.copy2(MAIN,backup)
 report=dict(before_sha256=sha(MAIN),backup=str(backup),original_objects={o.name_full:fingerprint(o) for o in s.objects},geometry={o.name_full:geom_sig(o) for o in s.objects if o.type=='MESH'},materials={m.name_full:strongmat(m) for m in bpy.data.materials},libraries={bpy.path.abspath(l.filepath):sha(bpy.path.abspath(l.filepath)) for l in bpy.data.libraries},changed=[],complete=False)
 print('BASELINE_RECORDED',flush=True)
else:
 report=json.loads((OUT/'verification.json').read_text());assert sha(SRC)==report['candidate_sha256']

def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box];return np.min(p,axis=0),np.max(p,axis=0)
def camera(name,pos,target,lens):
 key='GF CAMERA | '+name;cam=bpy.data.objects.get(key)
 if not cam:
  d=bpy.data.cameras.new(key);cam=bpy.data.objects.new(key,d);s.collection.objects.link(cam)
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.clip_start=.08;cam.data.clip_end=300;return cam
cams={
 'refinery-floor':camera('refinery-floor',(7,-24,1.7),(4.8,-19,.4),35),
 'mine-cliff-yard':camera('mine-cliff-yard',(-13,-36,1.7),(-24,-39,3),32),
 'mine-canopy':camera('mine-canopy',(-28,-34,1.7),(-37,-29,2.2),24)}
def settings(width=960,samples=4):
 s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=samples;s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=width;s.render.resolution_y=width*9//16;s.render.resolution_percentage=100;s.render.use_border=False;s.render.image_settings.file_format='PNG'
def render(name):
 s.camera=cams[name];s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)

def floor_finish(prefix):
 panels=sorted([o for o in s.objects if o.name.startswith(prefix)],key=lambda o:o.name)
 pools=[o for o in s.objects if o.name.startswith('FLR | Water in shallow slab depression')]
 N=128;cols=8;rows=math.ceil(len(panels)/cols);pixels=np.zeros((rows*N,cols*N,4),np.float32);pixels[:,:,3]=1
 img=bpy.data.images.new('GF | '+prefix.split('|')[-1].strip()+' wear and damp masks',width=cols*N,height=rows*N,alpha=True);img.colorspace_settings.name='Non-Color'
 mats=[]
 for k,base in enumerate(((.22,.209,.19),(.255,.243,.221),(.196,.192,.178),(.23,.224,.206))):
  m=bpy.data.materials.new('GF | '+prefix.split('|')[-1].strip()+' mineral '+str(k));m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();f=nt.nodes.new('NodeFrame');f.label='Mineral Paving And Moisture'
  def node(kind,x,y=0):
   n=nt.nodes.new(kind);n.parent=f;n.location=(x,y);n.width=160;return n
  uv=node('ShaderNodeUVMap',0,0);uv.uv_map='GF_FloorMask'
  tex=node('ShaderNodeTexImage',220,0);tex.image=img;tex.extension='EXTEND';tex.interpolation='Linear'
  sep=node('ShaderNodeSeparateColor',460,0);nt.links.new(uv.outputs['UV'],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],sep.inputs['Color'])
  co=node('ShaderNodeNewGeometry',0,-280);noise=node('ShaderNodeTexNoise',220,-340);noise.inputs['Scale'].default_value=1.6;noise.inputs['Detail'].default_value=2
  ramp=node('ShaderNodeValToRGB',460,-260);ramp.width=210
  for e,a in zip(ramp.color_ramp.elements,(.77,1.12)):e.color=(*(c*a for c in base),1)
  nt.links.new(co.outputs['Position'],noise.inputs['Vector']);nt.links.new(noise.outputs['Fac'],ramp.inputs[0])
  wear=node('ShaderNodeMixRGB',750,0);wear.inputs[2].default_value=(.33,.315,.275,1);nt.links.new(sep.outputs['Red'],wear.inputs[0]);nt.links.new(ramp.outputs['Color'],wear.inputs[1])
  damp=node('ShaderNodeMixRGB',970,0);damp.inputs[2].default_value=(.091,.092,.081,1);nt.links.new(sep.outputs['Green'],damp.inputs[0]);nt.links.new(wear.outputs[0],damp.inputs[1])
  rough=node('ShaderNodeMapRange',970,-240);rough.inputs['To Min'].default_value=.88;rough.inputs['To Max'].default_value=.36;nt.links.new(sep.outputs['Green'],rough.inputs['Value'])
  fine=node('ShaderNodeTexNoise',460,-580);fine.inputs['Scale'].default_value=38;fine.inputs['Detail'].default_value=2;nt.links.new(co.outputs['Position'],fine.inputs['Vector'])
  bump=node('ShaderNodeBump',1190,-490);bump.inputs['Strength'].default_value=.19;bump.inputs['Distance'].default_value=.006;nt.links.new(fine.outputs['Fac'],bump.inputs['Height'])
  bs=node('ShaderNodeBsdfPrincipled',1430,0);bs.inputs['Specular IOR Level'].default_value=.28;nt.links.new(damp.outputs[0],bs.inputs['Base Color']);nt.links.new(rough.outputs['Result'],bs.inputs['Roughness']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
  output=node('ShaderNodeOutputMaterial',1680,0);nt.links.new(bs.outputs[0],output.inputs['Surface']);mats.append(m)
 for idx,o in enumerate(panels):
  lo,hi=bounds(o);w,h=hi[0]-lo[0],hi[1]-lo[1];tx,ty=idx%cols,idx//cols
  # Two texel padding, continuous world-space abrasion and capillary wet margins.
  yy,xx=np.mgrid[0:N,0:N];u=np.clip((xx-2)/(N-5),0,1);v=np.clip((yy-2)/(N-5),0,1);X=lo[0]+u*w;Y=lo[1]+v*h
  edge=np.minimum.reduce([u*w,(1-u)*w,v*h,(1-v)*h])
  grain=(np.sin(X*13.3+Y*4.7)+np.sin(X*6.1-Y*11.7)+np.sin(X*39.1+Y*25.9))/6+.5
  patch=.5+.25*np.sin(X*3.1+Y*2.2)+.18*np.sin(X*1.8-Y*4.3)
  wear=np.clip(1-edge/(.05+.06*grain),0,1)*np.clip((patch-.40)*3,0,1)*.8
  # Softly broken foot/cart abrasion, not a uniform bright outline.
  scuff=np.exp(-((u-(.42+.06*np.sin(Y*2.7)))/.17)**2)*np.clip((patch-.63)*2.8,0,.36)
  wear=np.maximum(wear,scuff)
  damp=np.clip(1-edge/.14,0,1)*np.clip((.44-patch)*2,0,.32)
  for p in pools:
   a,b=bounds(p);cx,cy=(a[:2]+b[:2])/2
   if not(lo[0]<cx<hi[0] and lo[1]<cy<hi[1]):continue
   pts=np.array([p.matrix_world@vtx.co for vtx in p.data.vertices])[:,:2];dist=np.full_like(X,1e8,dtype=float);inside=np.zeros_like(X,dtype=bool)
   for j in range(len(pts)):
    A=pts[j];B=pts[(j+1)%len(pts)];D=B-A;t=np.clip(((X-A[0])*D[0]+(Y-A[1])*D[1])/(D@D),0,1);dist=np.minimum(dist,np.hypot(X-A[0]-t*D[0],Y-A[1]-t*D[1]))
    inside^=((A[1]>Y)!=(B[1]>Y))&(X<(B[0]-A[0])*(Y-A[1])/(B[1]-A[1]+1e-15)+A[0])
   rim=np.clip(1-dist/(.17+.11*grain),0,1);rim=rim*rim*(3-2*rim);rim[inside]=1;damp=np.maximum(damp,rim*.96)
  pixels[ty*N:(ty+1)*N,tx*N:(tx+1)*N,:3]=np.stack((wear,damp,patch),axis=-1)
  uv=o.data.uv_layers.new(name='GF_FloorMask')
  for loop in o.data.loops:
   p=o.matrix_world@o.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=((tx*N+2.5+(p.x-lo[0])/w*(N-5))/(cols*N),(ty*N+2.5+(p.y-lo[1])/h*(N-5))/(rows*N))
  # Keep the cut returns; replace all face/wet/bevel slots with one continuous field.
  mat=mats[(idx*3+idx//4)%4]
  for j in (0,1,3):o.data.materials[j].use_fake_user=True;o.data.materials[j]=mat
  report['changed'].append(o.name_full)
 img.pixels.foreach_set(pixels.ravel());img.pack();report.setdefault('floor',[]).append(dict(panels=len(panels),image=img.name,resolution=list(img.size)))

def local_wood(objname,name,palette,limit=None):
 o=bpy.data.objects[objname];original=o.data.materials[0];mat=original.copy();mat.name='GF | '+name
 # Preserve Claude's grain images, mapping, wear and moisture computation.
 ramp=mat.node_tree.nodes.get('Color Ramp')
 for e,col in zip(ramp.color_ramp.elements,palette):e.color=(*col,1)
 if limit is None:o.data.materials[0]=mat
 else:
  index=len(o.data.materials);o.data.materials.append(mat)
  for p in o.data.polygons:
   if max((o.matrix_world@o.data.vertices[i].co).z for i in p.vertices)<limit:p.material_index=index
 report['changed'].append(o.name_full)
 # Existing graph was entirely unframed. Preserve native node names and wiring;
 # arrange meaningful inherited processing stages with positive dependency flow.
 nodes=[n for n in mat.node_tree.nodes if n.type!='FRAME'];remaining=set(nodes);order=[]
 while remaining:
  ready=[n for n in nodes if n in remaining and all(l.from_node not in remaining for l in mat.node_tree.links if l.to_node==n)]
  assert ready,'Unexpected cyclic shader';order.extend(ready);remaining.difference_update(ready)
 sizes=[13,13,13,len(order)-39] if len(order)>39 else [len(order)]
 if sizes[-1]<4:sizes[-2]-=4-sizes[-1];sizes[-1]=4
 offset=0
 for j,num in enumerate(sizes):
  f=mat.node_tree.nodes.new('NodeFrame');f.label=('Timber Inputs','Grain And Patina','Moisture And Abrasion','Surface Response')[j];f.location=(offset*210,0)
  for k,n in enumerate(order[offset:offset+num]):n.parent=f;n.location=(k*210,0);n.width=160
  offset+=num

def mine_finish():
 report['roof_faces']={}
 for name in ('R39 | Shed frame','R39 | Shed boards'):
  o=bpy.data.objects[name];report['roof_faces'][name]={str(p.index):o.data.materials[p.material_index].name_full for p in o.data.polygons if max((o.matrix_world@o.data.vertices[i].co).z for i in p.vertices)>=4.35}
 local_wood('R39 | Shed frame','Silvered Structural Timber',[(.085,.075,.062),(.115,.105,.090),(.078,.063,.049),(.065,.059,.050)],4.35)
 local_wood('R39 | Shed boards','Shadowed Wall Boards',[(.034,.027,.021),(.044,.039,.032),(.030,.022,.016),(.027,.025,.021)],4.35)
 local_wood('R39 | Shed floor planks','Traffic Polished Boards',[(.087,.072,.053),(.105,.093,.072),(.081,.060,.041),(.072,.063,.049)])
 local_wood('R39 | Shed signs','Dark Entrance Backboard',[(.020,.019,.016),(.027,.025,.021),(.019,.017,.014),(.021,.021,.019)])
 # Use the already framed weathered ivory paint, without emissive lettering.
 sign=bpy.data.objects['R39 | Sign text'];sign.data=sign.data.copy();sign.data.materials[0]=bpy.data.materials['MEX | Ivory Letter Paint'];report['changed'].append(sign.name_full)

def rock_finish():
 # Material copies isolate the correction from the roof, terrain plateau and other rooms.
 # Existing boulder geometry, UVs and photographed mineral texture remain intact.
 for o in s.objects:
  if not o.name.startswith('CY | Existing boulder'):continue
  lo,hi=bounds(o)
  if hi[0]>-16 or lo[1]>-40:continue
  o.data=o.data.copy()
  for attr in o.data.color_attributes:
   if attr.domain not in {'POINT','CORNER','FACE'}:continue
   for item in attr.data:
    c=item.color;lum=.2126*c[0]+.7152*c[1]+.0722*c[2]
    # Desaturate cold blue colour blocks, retain authored light/dark facet rhythm.
    item.color=(lum*1.22+.025,lum*1.17+.023,lum*1.05+.020,c[3])
  report['changed'].append(o.name_full)
 # Reduce self-lighting on the visible cliff only. Its broad form must react to light.
 cliff=bpy.data.objects['R40 | Mine cliff'];cliff.data=cliff.data.copy()
 mat=cliff.data.materials[0].copy();mat.name='GF | Shaded Cliff Foot';cliff.data.materials.append(mat);slot=len(cliff.data.materials)-1
 bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 for l in list(mat.node_tree.links):
  if l.to_socket==bs.inputs['Emission Strength']:mat.node_tree.links.remove(l)
 bs.inputs['Emission Strength'].default_value=0
 f=mat.node_tree.nodes.new('NodeFrame');f.label='Cliff Surface Response'
 for i,name in enumerate(('Bump','Mix (Legacy).015','Principled BSDF','Material Output')):
  n=mat.node_tree.nodes[name];n.parent=f;n.location=(i*260,0);n.width=160
 selected=0
 for p in cliff.data.polygons:
  c=cliff.matrix_world@p.center
  if -58<c.y<-38 and c.x>-48 and c.z<14:p.material_index=slot;selected+=1
 assert selected>100;report['cliff_faces']=selected
 report['changed'].append(cliff.name_full)
 # Copy no geometry: localized mineral dust and darker contact zones are painted
 # into the existing boulder attributes, leaving every route and root unchanged.
 report['rock_scope']='Existing southern yard boulder colour attributes; local cliff material self-lighting removed. Geometry retained.'

if stage=='floor':
 floor_finish('FLR | Refinery dimensional slab')
 # Scene-grounded identification of visible cliff facets and inherited attributes.
 deps=bpy.context.evaluated_depsgraph_get();cam=cams['mine-cliff-yard'];bpy.context.view_layer.update();hits=[]
 frame=cam.data.view_frame(scene=s)
 for u,v in ((.15,.75),(.35,.5),(.55,.5),(.30,.30),(.12,.22)):
  point=frame[2].lerp(frame[1],u).lerp(frame[3].lerp(frame[0],u),v);direction=cam.matrix_world.to_3x3()@point.normalized();origin=cam.location.copy()
  for it in range(8):
   hit,loc,norm,face,obj,matrix=s.ray_cast(deps,origin,direction,distance=200)
   if not hit:break
   if obj.type=='MESH' and 'fog' not in obj.name.lower() and 'haze' not in obj.name.lower():
    hits.append(dict(uv=[u,v],object=obj.name,point=list(loc),normal=list(norm),face=face));break
   origin=loc+direction*.002
 report['cliff_hits']=hits
 (OUT/'visible-targets.json').write_text(json.dumps(dict(hits=hits,attributes={o.name:[(a.name,a.domain,a.data_type) for a in o.data.attributes] for o in s.objects if o.name in {'Mine Ridge | Preserved entrance rock','R39 | Shed frame','R39 | Shed boards','R39 | Shed signs','R39 | Apron mud','CY | Existing boulder 00'}}),indent=2))
else:
 floor_finish('FLR | Courtyard dimensional slab')
 mine_finish();rock_finish()

assert sha(MAIN)==inspection['sha256'];settings();s.camera=cams['refinery-floor']
target=MAIN.with_name('facility_environment.ground-candidate.blend');bpy.ops.wm.save_as_mainfile(filepath=str(target),check_existing=False)
report['candidate_sha256']=sha(target);(OUT/'verification.json').write_text(json.dumps(report,indent=2));print('CANDIDATE_SAVED',flush=True)
if stage=='floor':render('refinery-floor')
else:
 for name in ('mine-canopy','mine-cliff-yard'):render(name)
