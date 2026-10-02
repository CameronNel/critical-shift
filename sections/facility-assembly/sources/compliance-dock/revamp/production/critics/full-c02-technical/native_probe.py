"""Independent read-only technical critic probe. Writes JSON only; never saves Blender."""
import bpy, sys, json, math, hashlib, collections
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path('/workspace/critical-shift')
ROOM=ROOT/'sections/facility-assembly/sources/compliance-dock'
OUT=ROOM/'revamp/production/critics/full-c02-technical'
SOURCE=ROOM/'module_overhaul_R1.blend'
OUT.mkdir(parents=True,exist_ok=True)

def v(a): return [round(float(x),8) for x in a]
def safe(a):
    if isinstance(a,dict): return {str(k):safe(x) for k,x in a.items()}
    if isinstance(a,(list,tuple)): return [safe(x) for x in a]
    if isinstance(a,float) and not math.isfinite(a): return None
    if hasattr(a,'to_list'): return safe(a.to_list())
    return a
def props(o):
    r={}
    for k in o.keys():
        try:r[k]=safe(o[k])
        except: r[k]=str(o[k])
    return r
def lineage(o):
    a=[]
    while o is not None:
        a.append(o.name);o=o.parent
    return a
def bounds(vertices):
    if not vertices:return None
    return [[min(p[k] for p in vertices) for k in range(3)],[max(p[k] for p in vertices) for k in range(3)]]
def intersects(a,b,skin=0):
    return all(a[0][k]<=b[1][k]+skin and b[0][k]<=a[1][k]+skin for k in range(3))
def upstream(mat):
    if not mat.use_nodes:return []
    outs=[n for n in mat.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output]
    seen=set();pending=list(outs)
    while pending:
        n=pending.pop()
        if n in seen:continue
        seen.add(n)
        for inp in n.inputs:
            for l in inp.links:pending.append(l.from_node)
    return list(seen)
def percentile(a,p):
    if not a:return None
    a.sort();return a[min(len(a)-1,int((len(a)-1)*p))]

bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False)
scene=bpy.data.scenes.get('COMPLIANCE_EDIT_LOCAL') or bpy.context.scene
bpy.context.window.scene=scene
dep=bpy.context.evaluated_depsgraph_get()
result={'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'blender_version':bpy.app.version_string,'scene':scene.name,'scene_properties':props(scene),
        'unit_system':scene.unit_settings.system,'metres_per_unit':scene.unit_settings.scale_length,
        'saved':False,'objects':[],'materials':[],'libraries':[],'images':[],'anchors':[],
        'world_triangle_duplicate_groups':[]}
used_materials={m for o in scene.objects if hasattr(o.data,'materials') for m in o.data.materials if m}
mat_uv={}
for m in sorted(used_materials,key=lambda x:x.name):
    nodes=upstream(m)
    uvs=sorted({n.uv_map for n in nodes if n.type=='UVMAP'})
    mat_uv[m.name]=uvs
    result['materials'].append({'name':m.name,'local':m.library is None,'properties':props(m),
        'consumed_uv_maps':uvs,'consumed_node_types':sorted({n.type for n in nodes}),
        'consumed_image_nodes':[{'node':n.name,'image':n.image.name if n.image else None} for n in nodes if n.type in {'TEX_IMAGE','TEX_ENVIRONMENT'}],
        'active_output_exists':any(n.type=='OUTPUT_MATERIAL' for n in nodes)})

shapes={};world_triangles=collections.defaultdict(list);geometry_types={'MESH','CURVE','FONT','SURFACE','META'}
for o in sorted(scene.objects,key=lambda x:x.name):
    r={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'lineage':lineage(o),
       'matrix_world':[v(row) for row in o.matrix_world],'scale':v(o.scale),'properties':props(o),
       'hide_render':o.hide_render,'library':o.library.filepath if o.library else None,
       'data_library':o.data.library.filepath if o.data and o.data.library else None,
       'collections':[c.name for c in o.users_collection],'modifiers':[{'name':m.name,'type':m.type,'show_render':m.show_render} for m in o.modifiers]}
    if o.type=='CAMERA':r.update(lens=o.data.lens,clip_start=o.data.clip_start,clip_end=o.data.clip_end)
    if o.get('contact_anchor'):result['anchors'].append({'name':o.name,'point':v(o.matrix_world.translation),'properties':props(o),'lineage':lineage(o)})
    if o.type in geometry_types:
        ev=o.evaluated_get(dep);me=ev.to_mesh();me.calc_loop_triangles()
        vertices=[o.matrix_world@p.co for p in me.vertices]
        triangles=[tuple(t.vertices) for t in me.loop_triangles]
        normals=[];areas=[];edge_use=collections.Counter();volume=0;zero=[];nonfinite=[]
        normal_matrix=o.matrix_world.to_3x3().inverted().transposed()
        uv_rows=[];missing=set();mnames=[m.name if m else None for m in me.materials]
        consumed_indices=collections.defaultdict(list)
        for t in me.loop_triangles:
            pts=[vertices[i] for i in t.vertices];cross=(pts[1]-pts[0]).cross(pts[2]-pts[0]);area=cross.length*.5
            areas.append(area);normals.append((normal_matrix@t.normal).normalized())
            if area==0:zero.append(t.index)
            if not all(math.isfinite(x) for p in pts for x in p):nonfinite.append(t.index)
            volume+=pts[0].dot(pts[1].cross(pts[2]))/6
            for a,b in zip(t.vertices,t.vertices[1:]+t.vertices[:1]):edge_use[tuple(sorted((a,b)))]+=1
            if t.material_index<len(mnames) and mnames[t.material_index]:
                for uv_name in mat_uv.get(mnames[t.material_index],[]):consumed_indices[uv_name].append(t)
            key=tuple(sorted(tuple(round(float(x),6) for x in p) for p in pts))
            if area>0:world_triangles[key].append((o.name,t.index))
        for uv_name,tris in consumed_indices.items():
            layer=me.uv_layers.get(uv_name)
            if not layer:missing.add(uv_name);continue
            ratios=[];uv_zero=[];uv_nonfinite=[];uv_areas=0;world_areas=0
            for t in tris:
                pts=[vertices[i] for i in t.vertices];uvs=[layer.data[i].uv.copy() for i in t.loops]
                ua=abs((uvs[1]-uvs[0]).cross(uvs[2]-uvs[0]))*.5
                if ua==0 and areas[t.index]>0:uv_zero.append(t.index)
                if not all(math.isfinite(x) for uv in uvs for x in uv):uv_nonfinite.append(t.index)
                uv_areas+=ua;world_areas+=areas[t.index]
                for k in range(3):
                    d=(pts[(k+1)%3]-pts[k]).length
                    if d>.0001:ratios.append((uvs[(k+1)%3]-uvs[k]).length/d)
            uv_rows.append({'name':uv_name,'actual_material_triangle_count':len(tris),'zero_uv_area_triangles':uv_zero[:100],
                'zero_uv_area_count':len(uv_zero),'nonfinite_uv_count':len(uv_nonfinite),
                'uv_area':uv_areas,'world_surface_area_m2':world_areas,
                'uv_edge_per_world_m':{'min':min(ratios) if ratios else None,'p01':percentile(ratios,.01),'median':percentile(ratios,.5),'p99':percentile(ratios,.99),'max':max(ratios) if ratios else None}})
        r.update(bounds=safe(bounds(vertices)),triangles=len(triangles),polygons=len(me.polygons),vertices=len(vertices),
            material_names=mnames,material_submeshes=len({p.material_index for p in me.polygons}),
            consumed_uv_charts=uv_rows,missing_consumed_uv_maps=sorted(missing),uv_layers=[u.name for u in me.uv_layers],
            topology={'boundary_triangle_edges':sum(x==1 for x in edge_use.values()),'nonmanifold_triangle_edges':sum(x>2 for x in edge_use.values()),
                      'zero_area_triangles':zero[:100],'zero_area_count':len(zero),'nonfinite_count':len(nonfinite),
                      'signed_world_volume_m3':volume,'min_triangle_area_m2':min(areas) if areas else None})
        shapes[o.name]={'obj':o,'vertices':vertices,'triangles':triangles,'normals':normals,'areas':areas,'bounds':bounds(vertices),
                        'bvh':BVHTree.FromPolygons(vertices,triangles,all_triangles=True,epsilon=1e-7) if triangles else None}
        ev.to_mesh_clear()
    result['objects'].append(r)

def nearest(origin,direction,distance,exclude=()):
    hit=None
    for name,s in shapes.items():
        if name in exclude or not s['bvh']:continue
        p,n,i,d=s['bvh'].ray_cast(origin,direction,distance if hit is None else hit['distance'])
        if p is not None:hit={'object':name,'point':v(p),'normal':v(s['normals'][i]),'triangle':i,'distance':d}
    return hit

# Exact triangle coincidences are screened for exposure rather than called errors by count.
dup_groups=collections.defaultdict(list)
for key,values in world_triangles.items():
    if len(values)>1:
        names=tuple(sorted({x[0] for x in values}))
        dup_groups[names].append(values)
for names,rows in dup_groups.items():
    witnesses=[]
    for row in rows[:8]:
        name,i=row[0];s=shapes[name];pts=[s['vertices'][k] for k in s['triangles'][i]]
        centre=sum(pts,Vector())/3;normal=s['normals'][i]
        front=nearest(centre+normal*.0001,normal,.05,exclude=names)
        back=nearest(centre-normal*.0001,-normal,.05,exclude=names)
        witnesses.append({'objects_and_triangles':row,'centroid':v(centre),'normal':v(normal),
                          'front_other_surface_50mm':front,'back_other_surface_50mm':back})
    result['world_triangle_duplicate_groups'].append({'objects':names,'coincident_triangle_groups':len(rows),'witnesses':witnesses})

# Real oriented anchor target surfaces plus nearby physical component surfaces.
for a in result['anchors']:
    o=scene.objects[a['name']]
    roots=[scene.objects[n] for n in a['lineage'][1:] if scene.objects[n].get('support_class')=='supported_assembly']
    if not roots:continue
    root=roots[0];target=shapes.get(root.get('support_target'));direction=root.matrix_world.to_3x3()@Vector(root.get('support_direction',(0,0,-1)))
    direction.normalize();point=o.matrix_world.translation.copy()
    a.update(root=root.name,target=root.get('support_target'),direction_world=v(direction))
    if target and target['bvh']:
        p,n,i,d=target['bvh'].ray_cast(point-direction*.25,direction,.5)
        if p is not None:a.update(target_ray_point=v(p),signed_gap_m=(p-point).dot(direction),target_normal=v(target['normals'][i]),target_triangle=i)
    component_hits=[]
    for name,s in shapes.items():
        if root.name not in lineage(s['obj'])[1:] or not s['bvh']:continue
        p,n,i,d=s['bvh'].find_nearest(point)
        if p is not None and d<.01:component_hits.append({'object':name,'point':v(p),'normal':v(s['normals'][i]),'triangle':i,'distance_m':d})
    a['actual_component_surfaces_within_10mm']=sorted(component_hits,key=lambda x:x['distance_m'])[:10]

for l in bpy.data.libraries:
    p=Path(bpy.path.abspath(l.filepath));result['libraries'].append({'name':l.name,'stored_path':l.filepath,'absolute_path':str(p),'exists':p.is_file(),'missing':l.is_missing})
for im in bpy.data.images:
    packed=bool(im.packed_file) or bool(getattr(im,'packed_files',()))
    p=Path(bpy.path.abspath(im.filepath,library=im.library)) if im.filepath else None
    result['images'].append({'name':im.name,'source':im.source,'packed':packed,'path':str(p) if p else None,'exists':p.is_file() if p else None,'size':list(im.size),'colorspace':im.colorspace_settings.name})
result['summary']={'evaluated_triangles':sum(o.get('triangles',0) for o in result['objects']),
    'authoring_material_submeshes':sum(o.get('material_submeshes',0) for o in result['objects']),
    'used_local_material_families':sum(m.library is None for m in used_materials),'scene_objects':len(scene.objects),
    'zero_area_triangle_count':sum(o.get('topology',{}).get('zero_area_count',0) for o in result['objects']),
    'negative_closed_volume_objects':[o['name'] for o in result['objects'] if o.get('topology',{}).get('signed_world_volume_m3',0)<-1e-8 and o.get('topology',{}).get('boundary_triangle_edges',1)==0],
    'objects_with_missing_consumed_uv':[o['name'] for o in result['objects'] if o.get('missing_consumed_uv_maps')],
    'collapsed_consumed_uv_objects':[o['name'] for o in result['objects'] if any(u['zero_uv_area_count'] for u in o.get('consumed_uv_charts',[]))]}
# Preserve candidate world matrices before opening the immutable selected module.
candidate={o['name']:o['matrix_world'] for o in result['objects']}
bpy.ops.wm.open_mainfile(filepath=str(ROOM/'module.blend'),load_ui=False)
baseline=bpy.context.scene
changes=[];missing=[];deltas=[]
for o in baseline.objects:
    if o.name not in candidate:missing.append(o.name);continue
    delta=max(abs(float(o.matrix_world[i][j])-candidate[o.name][i][j]) for i in range(4) for j in range(4))
    deltas.append(delta)
    if delta>1e-6:changes.append({'object':o.name,'maximum_matrix_element_delta':delta})
result['preserved_world_pose_comparison']={'baseline_scene':baseline.name,'baseline_objects':len(baseline.objects),'missing_objects':missing,
    'changed_world_matrices':changes,'maximum_matrix_element_delta':max(deltas) if deltas else None}
(OUT/'native-independent.json').write_text(json.dumps(safe(result),indent=2)+'\n')
print('INDEPENDENT_NATIVE_SUMMARY',json.dumps(result['summary']),flush=True)
print('INDEPENDENT_WORLD_POSES',json.dumps(result['preserved_world_pose_comparison']),flush=True)
print('FROZEN_SOURCE_RELEASED: process will exit without saving',flush=True)
