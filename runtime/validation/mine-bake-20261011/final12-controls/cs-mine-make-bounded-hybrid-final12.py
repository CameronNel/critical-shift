from pathlib import Path
p=Path('/tmp/cs-mine-source-diffuse-prototype-final11.py');code=p.read_text().replace('/tmp/cs-mine-source-diffuse-prototype-final11','/tmp/cs-mine-source-hybrid-board-final12')
start=code.index('axis=int(np.argmax');end=code.index('targets=[];density_records=[]',start)
code=code[:start]+'''# One actual connected board, selected by a documented camera ray.
sourceEye,sourceAim,lens=json.loads((root/'runtime/out/mine-bake-audit/blender-views.json').read_text())['views']['R39_04_SHED_FRONT']
rotation=(Vector(sourceAim)-Vector(sourceEye)).to_track_quat('-Z','Y');px,py=540,340;vfov=math.radians(39.760704040527344)
ray=rotation@Vector(((2*px/1440-1)*math.tan(vfov/2)*1440/810,(1-2*py/810)*math.tan(vfov/2),-1));ray.normalize();hit=bvh.ray_cast(Vector(sourceEye),ray,300)
if hit[2] is None:raise ValueError('Documented board selection ray misses')
seed=mesh.loop_triangles[hit[2]].polygon_index;vertex_faces={}
for face in mesh.polygons:
 for v in face.vertices:vertex_faces.setdefault(v,[]).append(face.index)
component={seed};queue=[seed]
while queue:
 face=mesh.polygons[queue.pop()]
 for vertex in face.vertices:
  for adjacent in vertex_faces[vertex]:
   if adjacent not in component:component.add(adjacent);queue.append(adjacent)
if len(component)>256 or len(component)<2:raise ValueError('Selection is not one bounded loose board: '+str(len(component)))
groups=[sorted(component),[i for i in range(len(mesh.polygons)) if i not in component]]
vertices=sorted({v for i in component for v in mesh.polygons[i].vertices});selected=np.array([tuple(mesh.vertices[v].co) for v in vertices]);selection={'pixel':[px,py],'sourceFace':seed,'sourceFaces':sorted(component),'faces':len(component),'sourceWorldMatrix':[list(row) for row in world],'sourceLocalMin':selected.min(0).tolist(),'sourceLocalMax':selected.max(0).tolist(),'nativePrototypeExplicitLights':'All63 minePOINTs plus3 SUNs, enabled only in disposable native prototype','sourceNamedAttributesPreserved':True}
(out/'selection.json').write_text(json.dumps(selection,indent=2)+'\\n')
''' +code[end:]
code=code.replace("original_uv=next(u for u in part.uv_layers if u.active_render);layer=part.uv_layers.new(name='DIAGNOSTIC_SourceDiffuseUV',do_init=False);original_uv.active_render=True;unwrap([node],layer.name,4/4096)","original_uv=next(u for u in part.uv_layers if u.active_render);layer=part.uv_layers.new(name='DIAGNOSTIC_SourceDiffuseUV',do_init=False);original_uv.active_render=True\n if group==0:unwrap([node],layer.name,4/512)")
code=code.replace("density=surface_density(node,layer.name,4096)","density=surface_density(node,layer.name,512) if group==0 else {'pixelsPerMetre':None,'scope':'Source remainder only; not baked or exported'}")
code=code.replace("if not math.isfinite(density['pixelsPerMetre']) or density['pixelsPerMetre']<128:","if group==0 and (not math.isfinite(density['pixelsPerMetre']) or density['pixelsPerMetre']<128):")
start=code.index('radiance_files=[]');end=code.index('# Exact target-visible reference mask',start)
code=code[:start]+'''radiance_files=[];target=targets[0];source_explicit={l['name'] for r in json.loads((root/'runtime/unity/Assets/CriticalShift/Generated/Spawn/map-bindings.json').read_text())['rooms'] if r['key']=='mine' for l in r['lights']}|{'COMBINED moon','FE_MOON'}
light_data={}
for instance in dg.object_instances:
 if instance.object.type=='LIGHT' and instance.object.name in source_explicit:
  light_data[instance.object.data]=instance.object.data.energy
if len(light_data)!=66:raise ValueError('Explicit source light inventory differs: '+str(len(light_data)))
for material in target.data.materials:
 if any(n.type=='OBJECT_INFO' and any(s.is_linked for s in n.outputs) for n in material.node_tree.nodes):raise ValueError('Source ObjectInfo identity requires an explicit matching control')
roots={m:next(n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output).inputs['Surface'].links[0].from_socket for m in target.data.materials}
def bake(name,kind,direct=False,indirect=False,channel=None):
 image=bpy.data.images.new('DIAGNOSTIC '+name,512,512,alpha=True,float_buffer=True);image.colorspace_settings.name='Non-Color';temporary=[]
 if kind=='NORMAL':image.generated_color=(.5,.5,1,1)
 for material in target.data.materials:
  nt=material.node_tree;node=nt.nodes.new('ShaderNodeTexImage');node.image=image;nt.nodes.active=node;temporary.append((nt,node))
  for other in nt.nodes:other.select=other==node
  if channel:
   bsdf=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');socket=bsdf.inputs[channel];emission=nt.nodes.new('ShaderNodeEmission');temporary.append((nt,emission))
   if socket.is_linked:nt.links.new(socket.links[0].from_socket,emission.inputs['Color'])
   else:
    value=socket.default_value;emission.inputs['Color'].default_value=value if hasattr(value,'__len__') else (value,value,value,1)
   output=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output);nt.links.new(emission.outputs[0],output.inputs['Surface'])
 target.data.uv_layers['DIAGNOSTIC_SourceDiffuseUV'].active_render=True
 scene.render.bake.use_pass_direct=direct;scene.render.bake.use_pass_indirect=indirect;scene.render.bake.use_pass_color=True
 bpy.ops.object.select_all(action='DESELECT');target.select_set(True);bpy.context.view_layer.objects.active=target;print('CS_BOUNDED_SOURCE_BAKE_START',name,flush=True);bpy.ops.object.bake(type=kind,uv_layer='DIAGNOSTIC_SourceDiffuseUV')
 scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='32';scene.render.image_settings.exr_codec='ZIP';file=out/(name+'.exr');image.save_render(str(file),scene=scene);radiance_files.append(file)
 for material,root_socket in roots.items():
  nt=material.node_tree;output=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output);nt.links.new(root_socket,output.inputs['Surface'])
 for nt,node in temporary:nt.nodes.remove(node)
 bpy.data.images.remove(image);gc.collect();print('CS_BOUNDED_SOURCE_BAKE_DONE',name,flush=True)
bake('SourceAllIndirect','DIFFUSE',indirect=True)
bake('SourceAllDirect','DIFFUSE',direct=True)
try:
 for data in light_data:data.energy=0
 bake('SourceNonExplicitDirect','DIFFUSE',direct=True)
finally:
 for data,value in light_data.items():data.energy=value
bake('SourceBaseColor','EMIT',channel='Base Color');bake('SourceNormal','NORMAL');bake('SourceRoughness','EMIT',channel='Roughness');bake('SourceMetallic','EMIT',channel='Metallic')
# AOV shading must use the original UV by name, and only the selected component gets the mask.
materials={m:m for m in target.data.materials}
''' +code[end:]
code=code.replace('for node in targets:node.select_set(True)','targets[0].select_set(True)').replace("'size':4096,'chunks':4","'size':512,'chunks':1")
code=code.replace("'included':['authored diffuse BSDF colour','direct diffuse lighting','indirect diffuse lighting']","'included':['separate colour-included all-indirect','separate colour-included all-direct reference','separate colour-included non-explicit direct(world/emission/other sources)']")
code=code.replace("'nativeValidation':'Pending; dynamic shadows and actors are not certified'","'sourceExplicitLightDataCount':len(light_data),'selection':selection,'nativeValidation':'Pending; dynamic shadows, actors, source probe field and full-map not certified'")
code=code.replace("if any((out/name).exists() for name in ['SourceDiffuseRadiance-0.exr','SourceDiffuseShedBoards.fbx','SourceContextShed.exr'])","if any((out/name).exists() for name in ['SourceAllIndirect.exr','SourceDiffuseShedBoards.fbx','SourceContextShed.exr'])")
Path('/tmp/cs-mine-source-hybrid-board-final12.py').write_text(code);compile(code,'source-hybrid-board','exec');print('CS_BOUNDED_HYBRID_HELPER_PREPARED')
