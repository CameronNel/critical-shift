"""Bounded one-probe diffuse-irradiance experiment, not a production probe asset."""
import bpy,json,hashlib,math,gc,numpy as np
from collections import Counter
from pathlib import Path
from mathutils import Vector
root=Path('/workspace/critical-shift-spawn-runtime');out=Path('/tmp/cs-mine-source-probe-field-final12');out.mkdir(exist_ok=True)
if any(out.glob('*.exr')):raise ValueError('Existing probe experiment outputs')
scene=bpy.context.scene;volumes=[]
for material in bpy.data.materials:
 if not material.use_nodes:continue
 for node in material.node_tree.nodes:
  if node.type=='OUTPUT_MATERIAL' and node.is_active_output and node.inputs['Volume'].is_linked:
   for link in list(node.inputs['Volume'].links):material.node_tree.links.remove(link)
   volumes.append(material.name)
centre=Vector((-41.4,-70,1.2));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();clearance=[]
for x in [-1,0,1]:
 for y in [-1,0,1]:
  for z in [-1,0,1]:
   if x==y==z==0:continue
   direction=Vector((x,y,z)).normalized();origin=centre.copy();record={'direction':list(direction),'skipped':[]}
   for attempt in range(24):
    hit,point,normal,face,obj,matrix=scene.ray_cast(dg,origin,direction,distance=50)
    if not hit:record['hit']=False;break
    if hasattr(obj.data,'materials') and any(m and m.name in volumes for m in obj.data.materials):record['skipped'].append(obj.name);origin=point+direction*.0001;continue
    distance=(point-centre).length;record.update(hit=True,object=obj.name,distance=distance,normalDotRay=normal.dot(direction))
    if distance<.012:raise ValueError('Virtualprobe intersects/approaches sourcegeometry: '+repr(record))
    if normal.dot(direction)>.001:
     mesh=obj.evaluated_get(dg).data
     if obj.type!='MESH':raise ValueError('Backfacingnonmesh needs explicitclearance classification: '+obj.name)
     edges=Counter(tuple(sorted((face.vertices[i],face.vertices[(i+1)%len(face.vertices)]))) for face in mesh.polygons for i in range(len(face.vertices)))
     watertight=bool(edges) and all(count==2 for count in edges.values())
     record.update(watertightEdgeTopology=watertight,boundaryEdges=sum(count==1 for count in edges.values()),nonManifoldEdges=sum(count>2 for count in edges.values()))
     if watertight:raise ValueError('Virtualprobe may be inside sourcegeometry: '+repr(record))
    break
   else:raise ValueError('Clearance query exhausted volume skips')
   clearance.append(record)
(out/'source-clearance.json').write_text(json.dumps({'scope':'26 documented sourcegeometry rays; radiusclearance and conservativeclosedfirsthit test only, notfullsigned-distance proof. Backfacingopen-source surfacesare recordedwithoutinferringinside-solid.','radius':.01,'rays':clearance},indent=2)+'\n')
bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=.01,location=centre);probe=bpy.context.object;probe.name='DIAGNOSTIC virtual diffuse probe';probe.visible_camera=True;probe.visible_shadow=False;probe.visible_diffuse=False;probe.visible_glossy=False;probe.visible_transmission=False;probe.visible_volume_scatter=False
for polygon in probe.data.polygons:polygon.use_smooth=True
material=bpy.data.materials.new('Diagnostic white Lambert receiver');material.use_nodes=True;nt=material.node_tree;nt.nodes.clear();diffuse=nt.nodes.new('ShaderNodeBsdfDiffuse');diffuse.inputs['Color'].default_value=(1,1,1,1);diffuse.inputs['Roughness'].default_value=0;output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(diffuse.outputs[0],output.inputs['Surface']);probe.data.materials.append(material)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=64;scene.cycles.use_denoising=False;scene.render.bake.use_clear=True;scene.render.bake.margin=0;scene.render.bake.use_selected_to_active=False;scene.render.bake.use_pass_color=False
explicit={l['name'] for r in json.loads((root/'runtime/unity/Assets/CriticalShift/Generated/Spawn/map-bindings.json').read_text())['rooms'] if r['key']=='mine' for l in r['lights']}|{'COMBINED moon','FE_MOON'}
def energies():
 bpy.context.view_layer.update();return {i.object.name:float(i.object.data.energy) for i in bpy.context.evaluated_depsgraph_get().object_instances if i.object.type=='LIGHT' and i.object.name in explicit}
original={i.object.original.data:i.object.original.data.energy for i in bpy.context.evaluated_depsgraph_get().object_instances if i.object.type=='LIGHT' and i.object.name in explicit};assert len(original)==66
files=[]
def bake(name,kind,direct=False,indirect=False):
 image=bpy.data.images.new('Diagnostic '+name,64,32,alpha=True,float_buffer=True);image.colorspace_settings.name='Non-Color';node=nt.nodes.new('ShaderNodeTexImage');node.image=image
 for n in nt.nodes:n.select=n==node
 nt.nodes.active=node;scene.render.bake.use_pass_direct=direct;scene.render.bake.use_pass_indirect=indirect;bpy.ops.object.select_all(action='DESELECT');probe.select_set(True);bpy.context.view_layer.objects.active=probe;print('CS_SOURCE_PROBE_FIELD_START',name,flush=True);bpy.ops.object.bake(type=kind)
 raw=np.empty(len(image.pixels),dtype=np.float32);image.pixels.foreach_get(raw)
 if not np.isfinite(raw).all():raise ValueError('Nonfinite probe '+name)
 scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='32';scene.render.image_settings.exr_codec='ZIP';file=out/(name+'.exr');image.save_render(str(file),scene=scene);files.append(file);nt.nodes.remove(node);bpy.data.images.remove(image);gc.collect();print('CS_SOURCE_PROBE_FIELD_DONE',name,flush=True)
bake('SourceProbeAllIndirect','DIFFUSE',indirect=True)
try:
 for data in original:data.energy=0
 disabled=energies();assert len(disabled)==66 and all(value==0 for value in disabled.values());(out/'disabled-lights.json').write_text(json.dumps(disabled,indent=2)+'\n')
 bake('SourceProbeNonExplicitDirect','DIFFUSE',direct=True)
finally:
 for data,power in original.items():data.energy=power
 restored=energies();assert len(restored)==66;(out/'restored-lights.json').write_text(json.dumps(restored,indent=2)+'\n')
 for i in bpy.context.evaluated_depsgraph_get().object_instances:
  if i.object.type=='LIGHT' and i.object.name in explicit:assert abs(i.object.data.energy-original[i.object.original.data])<1e-6
constant=nt.nodes.new('ShaderNodeEmission');constant.inputs['Color'].default_value=(1,1,1,1);nt.links.new(constant.outputs[0],output.inputs['Surface']);bake('SourceProbeValidTexels','EMIT');nt.links.new(diffuse.outputs[0],output.inputs['Surface'])
geometry=nt.nodes.new('ShaderNodeNewGeometry');scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=.5;nt.links.new(geometry.outputs['Normal'],scale.inputs[0]);add=nt.nodes.new('ShaderNodeVectorMath');add.operation='ADD';add.inputs[1].default_value=(.5,.5,.5);nt.links.new(scale.outputs[0],add.inputs[0]);emission=nt.nodes.new('ShaderNodeEmission');nt.links.new(add.outputs[0],emission.inputs['Color']);nt.links.new(emission.outputs[0],output.inputs['Surface']);bake('SourceProbeActualWorldNormals','EMIT');nt.links.new(diffuse.outputs[0],output.inputs['Surface'])
(out/'provenance.json').write_text(json.dumps({'status':'SingleVirtualProbeBakeOnly','sourceSha256':hashlib.sha256((root/'runtime/out/spawn-export-source/combined-runtime-source.blend').read_bytes()).hexdigest(),'worldCentreBlenderXYZ':list(centre),'radiusMetres':.01,'size':[64,32],'samples':64,'receiver':'White Lambert diffuse roughness0','receiverDiffuseColourRemoved':True,'quantity':'White Lambert outgoing diffuse radiance E/pi, not incident radiance or irradiance E','helperSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'receiverHiddenFromShadowDiffuseGlossyTransmissionRays':True,'receiverCameraVisibleForCyclesBakeAdmission':True,'noBeautyCameraRenderedInVirtualProbeScene':True,'allIndirectIncludesOriginalExplicitLights':True,'nonExplicitDirectDisablesOriginal66LightsOnlyDuringDirectBake':True,'volumesDisabledInMemory':volumes,'canonicalSourceSaved':False,'nativeValidation':'Pending SH fit, GPU/CPU basis check and actual static/dynamic neutral receivers; no fullprobe/actor acceptance','files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files+[out/'disabled-lights.json',out/'restored-lights.json',out/'source-clearance.json']}},indent=2)+'\n');print('CS_SOURCE_SINGLE_PROBE_FIELD_READY_FOR_BOUNDED_VALIDATION',flush=True)
