"""Disposable, actual source diffuse-radiance bake of the shed boards.
Not a beauty bake: diffuse direct + indirect + authored colour only; native
specular, moving shadows/actors and full-map acceptance remain separate gates.
"""
import bpy,json,hashlib,sys,math
from pathlib import Path
root=Path('/workspace/critical-shift-spawn-runtime');sys.path.insert(0,str(root/'runtime/tools'));from mine_delivery_uv import unwrap,surface_density
out=Path('/tmp/cs-mine-source-diffuse-prototype-final11');out.mkdir(exist_ok=True)
if any((out/name).exists() for name in ['SourceDiffuseRadiance-0.exr','SourceDiffuseShedBoards.fbx','SourceContextShed.exr']):raise ValueError('Source prototype output already exists; archive previous evidence before retry')
scene=bpy.context.scene
suppressed=[]
for material in bpy.data.materials:
 if not material.use_nodes:continue
 for node in material.node_tree.nodes:
  if node.type=='OUTPUT_MATERIAL' and node.is_active_output and node.inputs['Volume'].is_linked:
   for link in list(node.inputs['Volume'].links):material.node_tree.links.remove(link)
   suppressed.append(material.name)
source=next(o for o in bpy.data.objects if o.name=='R39 | Shed boards');dg=bpy.context.evaluated_depsgraph_get();instances=[i.matrix_world.copy() for i in dg.object_instances if i.object.original==source];assert len(instances)==1
world=instances[0];original_visibility=source.hide_render
mesh=bpy.data.meshes.new_from_object(source.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);target=bpy.data.objects.new('DIAGNOSTIC source diffuse shed boards',mesh);scene.collection.objects.link(target);target.matrix_world=world
# Copy node trees only for selecting the bake image. Geometry, materials and
# other original map instances continue to illuminate/occlude this actual target.
materials={}
for index,m in enumerate(mesh.materials):
 if m not in materials:materials[m]=m.copy()
 mesh.materials[index]=materials[m]
if len(mesh.uv_layers)!=1:raise ValueError('Prototype requires one existing source UV; do not assume FBX UV1')
source_uv=next((u for u in mesh.uv_layers if u.active_render),None)
if source_uv is None:raise ValueError('Prototype source UV missing')
for material in materials.values():
 nt=material.node_tree;uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map=source_uv.name
 for node in list(nt.nodes):
  if node.type=='NORMAL_MAP' and node.space=='TANGENT' and not node.uv_map:node.uv_map=source_uv.name
  if node.type=='TEX_IMAGE' and not node.inputs['Vector'].is_linked:nt.links.new(uv.outputs['UV'],node.inputs['Vector'])
  if node.type=='TEX_COORD':
   for link in list(node.outputs['UV'].links):nt.links.new(uv.outputs['UV'],link.to_socket)
# Conservative target-only visibility: a face occluded by another object may
# still count here, so any back-facing result needs a full scene follow-up.
from mathutils import Vector
from mathutils.bvhtree import BVHTree
mesh.calc_loop_triangles();verts=[world@v.co for v in mesh.vertices];tris=[tuple(t.vertices) for t in mesh.loop_triangles];bvh=BVHTree.FromPolygons(verts,tris,all_triangles=True)
eye=Vector(json.loads((root/'runtime/out/mine-bake-audit/blender-views.json').read_text())['views']['R39_04_SHED_FRONT'][0]);facing={'frontTriangles':0,'backTriangles':0,'scope':'Target-only first-hit visibility at triangle centroids; conservative for other-object occlusion'}
for index,tri in enumerate(tris):
 center=sum((verts[i] for i in tri),Vector())/3;direction=center-eye;distance=direction.length
 if distance<.0001:continue
 hit=bvh.ray_cast(eye,direction.normalized(),distance+.001)
 if hit[2]!=index:continue
 normal=(verts[tri[1]]-verts[tri[0]]).cross(verts[tri[2]]-verts[tri[0]])
 facing['frontTriangles' if normal.dot(eye-center)>0 else 'backTriangles']+=1
(out/'visible-face-direction.json').write_text(json.dumps(facing,indent=2)+'\n')
if not facing['frontTriangles']:raise ValueError('Empty target visibility audit')
if facing['backTriangles']:raise ValueError('Visible back faces require explicit two-sided radiance transfer')
# Split the actual evaluated board geometry; preserve source coordinates and
# named attributes. Every original polygon belongs to exactly one chunk.
import bmesh,numpy as np,gc
mesh.calc_loop_triangles()
local=np.array([tuple(v.co) for v in mesh.vertices],dtype=np.float32)
low=local.min(0);extent=np.maximum(local.max(0)-low,1e-8)
coordinates={'DIAG_original_Generated':(local-low)/extent}
for material in materials.values():
 nt=material.node_tree
 if any(n.type=='GROUP' for n in nt.nodes):raise ValueError('Nested source shader groups require explicit coordinate preservation')
 for node in list(nt.nodes):
  if node.type in {'TEX_NOISE','TEX_VORONOI','TEX_WAVE','TEX_MAGIC','TEX_GRADIENT','TEX_BRICK','TEX_CHECKER','TEX_WHITE_NOISE'} and not node.inputs['Vector'].is_linked:
   attr=nt.nodes.new('ShaderNodeAttribute');attr.attribute_name='DIAG_original_Generated';nt.links.new(attr.outputs['Vector'],node.inputs['Vector'])
  if node.type=='TEX_COORD':
   for socket in ['Generated','Object']:
    if not node.outputs[socket].is_linked:continue
    frame=node.object if socket=='Object' else None
    name='DIAG_original_Generated' if socket=='Generated' else 'DIAG_original_Object_'+(frame.name if frame else 'Self')
    if name not in coordinates:
     transform=frame.matrix_world.inverted()@world if frame else None
     coordinates[name]=np.array([tuple(transform@v.co) for v in mesh.vertices],dtype=np.float32) if transform else local
    attr=nt.nodes.new('ShaderNodeAttribute');attr.attribute_name=name
    for link in list(node.outputs[socket].links):nt.links.new(attr.outputs['Vector'],link.to_socket)
for name,values in coordinates.items():
 if mesh.attributes.get(name):raise ValueError('Diagnostic coordinate name collision')
 attr=mesh.attributes.new(name=name,type='FLOAT_VECTOR',domain='POINT');attr.data.foreach_set('vector',values.ravel())
source_normals=mesh.attributes.new(name='DIAG_original_corner_normal',type='FLOAT_VECTOR',domain='CORNER')
normal_values=np.empty(len(mesh.loops)*3,dtype=np.float32);mesh.corner_normals.foreach_get('vector',normal_values);source_normals.data.foreach_set('vector',normal_values)
source_ids=mesh.attributes.new(name='DIAG_original_polygon_id',type='INT',domain='FACE');source_ids.data.foreach_set('value',np.arange(len(mesh.polygons),dtype=np.int32))
axis=int(np.argmax(np.ptp(local,axis=0)));areas=np.zeros(len(mesh.polygons))
for triangle in mesh.loop_triangles:
 points=[world@mesh.vertices[i].co for i in triangle.vertices];areas[triangle.polygon_index]+=(points[1]-points[0]).cross(points[2]-points[0]).length/2
order=sorted(range(len(mesh.polygons)),key=lambda i:float(mesh.polygons[i].center[axis]));total_area=float(areas.sum());groups=[[],[],[],[]];accumulated=0
for index in order:
 group=min(int((accumulated+areas[index]/2)/total_area*4),3);groups[group].append(index);accumulated+=areas[index]
if any(not g for g in groups) or len(set(i for g in groups for i in g))!=len(mesh.polygons):raise ValueError('Incomplete or empty geometry partition')
targets=[];density_records=[];source_polygon_count=len(mesh.polygons);source_loop_count=len(mesh.loops)
for group,indices in enumerate(groups):
 part=mesh.copy();part.name=f'DIAGNOSTIC_source_diffuse_chunk_{group}'
 bm=bmesh.new();bm.from_mesh(part);bm.faces.ensure_lookup_table();keep=set(indices);bmesh.ops.delete(bm,geom=[face for i,face in enumerate(bm.faces) if i not in keep],context='FACES_ONLY');bm.to_mesh(part);bm.free();part.update()
 normals=np.empty(len(part.loops)*3,dtype=np.float32);part.attributes['DIAG_original_corner_normal'].data.foreach_get('vector',normals);part.normals_split_custom_set(normals.reshape((-1,3)))
 node=bpy.data.objects.new(f'DIAGNOSTIC_source_diffuse_chunk_{group}',part);scene.collection.objects.link(node);node.matrix_world=world
 # Source UV0 remains active for source shading; generated UV1 is bake-only.
 original_uv=next(u for u in part.uv_layers if u.active_render);layer=part.uv_layers.new(name='DIAGNOSTIC_SourceDiffuseUV',do_init=False);original_uv.active_render=True;unwrap([node],layer.name,4/4096)
 density=surface_density(node,layer.name,4096);density['chunk']=group;density['sourcePolygons']=len(part.polygons);density_records.append(density)
 if not math.isfinite(density['pixelsPerMetre']) or density['pixelsPerMetre']<128:raise ValueError('Chunk diffuse density below128px/m: '+repr(density))
 # Distinct material copies permit one atlas buffer live at a time.
 for index,material in enumerate(part.materials):part.materials[index]=material.copy()
 targets.append(node)
if sum(len(o.data.polygons) for o in targets)!=source_polygon_count or sum(len(o.data.loops) for o in targets)!=source_loop_count:raise ValueError('Chunking changed source face/corner inventory')
inventory={'sourcePolygons':source_polygon_count,'sourceCorners':source_loop_count,'chunkPolygons':[len(o.data.polygons) for o in targets],'chunkCorners':[len(o.data.loops) for o in targets],'allSourcePolygonsAssignedOnce':True,'sourceNamedAttributesPreserved':True,'sourceCornerNormalsPreserved':True,'sourceGeneratedAndObjectCoordinatesFrozen':list(coordinates),'sourceWorldMatrixUnchanged':True,'sourceUv0Preserved':True,'maxLiveBakeImages':1}
(out/'chunk-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n');(out/'density.json').write_text(json.dumps(density_records,indent=2)+'\n');print('CS_SOURCE_DIFFUSE_CHUNK_DENSITIES',density_records,flush=True)
# The temporary unsplit evaluated copy is no longer a renderable duplicate.
bpy.data.objects.remove(target,do_unlink=True);bpy.data.meshes.remove(mesh)
materials={m:m for o in targets for m in o.data.materials};density=density_records

source.hide_render=True;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.cycles.use_denoising=False
scene.render.bake.use_clear=True;scene.render.bake.margin=4;scene.render.bake.use_selected_to_active=False
scene.render.bake.use_pass_direct=True;scene.render.bake.use_pass_indirect=True;scene.render.bake.use_pass_color=True
radiance_files=[]
for group,target in enumerate(targets):
 image=bpy.data.images.new(f'DIAGNOSTIC source diffuse chunk{group}',4096,4096,alpha=True,float_buffer=True);image.colorspace_settings.name='Non-Color';bake_nodes=[]
 for material in target.data.materials:
  if not material.use_nodes:raise ValueError('Unsupported prototype BSDF')
  node=material.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;material.node_tree.nodes.active=node;bake_nodes.append((material,node))
  for other in material.node_tree.nodes:other.select=other==node
 bpy.ops.object.select_all(action='DESELECT');target.select_set(True);bpy.context.view_layer.objects.active=target
 print('CS_SOURCE_DIFFUSE_PROTOTYPE_CHUNK_BAKE_START',group,density_records[group],flush=True)
 bpy.ops.object.bake(type='DIFFUSE',uv_layer='DIAGNOSTIC_SourceDiffuseUV')
 scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='16';scene.render.image_settings.exr_codec='ZIP'
 file=out/f'SourceDiffuseRadiance-{group}.exr';image.save_render(str(file),scene=scene);radiance_files.append(file)
 for material,node in bake_nodes:material.node_tree.nodes.remove(node)
 bpy.data.images.remove(image);gc.collect();print('CS_SOURCE_DIFFUSE_PROTOTYPE_CHUNK_BAKE_DONE',group,flush=True)
# Exact target-visible reference mask and diffuse passes. This diagnoses only
# this copied, source-shaded board geometry, with the same source camera/context.
view=scene.view_layers[0];aov=view.aovs.add();aov.name='SourceShedBoard';aov.type='COLOR'
for material in materials.values():
 node=material.node_tree.nodes.new('ShaderNodeOutputAOV');node.aov_name='SourceShedBoard';node.inputs['Color'].default_value=(1,1,1,1)
aov=view.aovs.add();aov.name='SourceBoardBaseColor';aov.type='COLOR'
for material in materials.values():
 nodes=material.node_tree.nodes;principled=[n for n in nodes if n.type=='BSDF_PRINCIPLED']
 if len(principled)!=1:raise ValueError('Unsupported source board BaseColor AOV')
 node=nodes.new('ShaderNodeOutputAOV');node.aov_name='SourceBoardBaseColor';socket=principled[0].inputs['Base Color']
 if socket.is_linked:material.node_tree.links.new(socket.links[0].from_socket,node.inputs['Color'])
 else:node.inputs['Color'].default_value=socket.default_value
view.use_pass_diffuse_color=True;view.use_pass_diffuse_direct=True;view.use_pass_diffuse_indirect=True
camera=bpy.data.objects.new('Diagnostic source board camera',bpy.data.cameras.new('Diagnostic source board camera'));scene.collection.objects.link(camera)
sourceEye,sourceAim,lens=json.loads((root/'runtime/out/mine-bake-audit/blender-views.json').read_text())['views']['R39_04_SHED_FRONT'];camera.location=sourceEye;camera.rotation_euler=(Vector(sourceAim)-Vector(sourceEye)).to_track_quat('-Z','Y').to_euler();camera.data.lens=lens;camera.data.clip_start=.05;camera.data.clip_end=800;scene.camera=camera
scene.render.resolution_x=640;scene.render.resolution_y=360;scene.render.resolution_percentage=100
scene.render.image_settings.media_type='MULTI_LAYER_IMAGE';scene.render.image_settings.file_format='OPEN_EXR_MULTILAYER';scene.render.image_settings.color_depth='32';scene.render.filepath=str(out/'SourceContextShed.exr');bpy.ops.render.render(write_still=True)
print('CS_SOURCE_DIFFUSE_PROTOTYPE_EXACT_MASK_AND_PASSES_OK',flush=True)
# The layer is FBX UV1. Source UV0 remains intact; material images are bound
# explicitly by the temporary native diagnostic, not embedded into a beauty map.
for material in materials.values():
 for node in list(material.node_tree.nodes):
  if node.type=='TEX_IMAGE':material.node_tree.nodes.remove(node)
bpy.ops.object.select_all(action='DESELECT')
for node in targets:node.select_set(True)
bpy.context.view_layer.objects.active=targets[0]
bpy.ops.export_scene.fbx(filepath=str(out/'SourceDiffuseShedBoards.fbx'),use_selection=True,object_types={'MESH'},bake_anim=False,axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',path_mode='AUTO',use_triangles=True)
source.hide_render=original_visibility
proof={'status':'PrototypeBakeOnly','sourceBlenderSha256':hashlib.sha256((root/'runtime/out/spawn-export-source/combined-runtime-source.blend').read_bytes()).hexdigest(),'sourceObject':source.name,'worldMatrix':[list(row) for row in world],'bake':'DIFFUSE','included':['authored diffuse BSDF colour','direct diffuse lighting','indirect diffuse lighting'],'excluded':['view-dependent specular','emission','camera beauty/composite'],'visibleFaceDirection':facing,'fbxSourceDiffuseUVIndex':1,'size':4096,'chunks':4,'chunkInventory':inventory,'samples':32,'density':density,'diagnosticVolumesDisabledInMemory':suppressed,'canonicalSourceSaved':False,'nativeValidation':'Pending; dynamic shadows and actors are not certified','files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in radiance_files+[out/'SourceDiffuseShedBoards.fbx',out/'SourceContextShed.exr',out/'density.json',out/'chunk-inventory.json',out/'visible-face-direction.json']}}
(out/'provenance.json').write_text(json.dumps(proof,indent=2)+'\n');print('CS_SOURCE_DIFFUSE_PROTOTYPE_BAKE_OK',flush=True)
