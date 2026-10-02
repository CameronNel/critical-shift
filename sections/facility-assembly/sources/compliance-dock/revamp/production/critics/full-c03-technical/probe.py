import bpy, sys, json, math, hashlib, importlib.util
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
root=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock')
out=root/'revamp/production/critics/full-c03-technical'
native=Path(bpy.data.filepath)
hash_before=hashlib.sha256(native.read_bytes()).hexdigest()
scene=bpy.context.scene
dg=bpy.context.evaluated_depsgraph_get()
baseline=json.loads((root/'revamp/production/baseline.json').read_text())
base={o['name']:o for o in baseline['objects']}
report={'native':str(native),'hash_before':hash_before,'scene':scene.name,'blender':bpy.app.version_string,'inventory':[],'consumed_uv':[],'images':[],'libraries':[],'pose_deltas':[],'dimension_deltas':[],'missing_originals':[],'planning':{},'material_nodes':[]}
used=set();triangles=0;submeshes=0;shapes=[]
spec=importlib.util.spec_from_file_location('v',root/'validate_dock.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
for o in scene.objects:
    if o.name in base:
        b=base[o.name];dm=max(abs(o.matrix_world[i][j]-b['matrix'][i][j]) for i in range(4) for j in range(4))
        if dm>1e-6:report['pose_deltas'].append({'object':o.name,'max_matrix_delta':dm})
        dd=max(abs(o.dimensions[i]-b['dimensions'][i]) for i in range(3))
        if dd>.005001:report['dimension_deltas'].append({'object':o.name,'original':b['dimensions'],'current':list(o.dimensions),'max_delta_m':dd})
    if o.type not in v.GEOMETRY_TYPES:continue
    ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();triangles+=len(me.loop_triangles)
    indices={f.material_index for f in me.polygons};submeshes+=len(indices)
    mats={me.materials[i] for i in indices if i<len(me.materials) and me.materials[i]};used.update(mats)
    report['inventory'].append({'name':o.name,'type':o.type,'triangles':len(me.loop_triangles),'material_submeshes':len(indices),'materials':sorted(m.name for m in mats),'parent':o.parent.name if o.parent else None,'props':{k:str(x) for k,x in o.items()},'uv_layers':[x.name for x in me.uv_layers]})
    consumed=set();active_uv=me.uv_layers.active.name if me.uv_layers.active else None
    for m in mats:
        if not m.use_nodes:continue
        reachable=set();todo=[n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output]
        while todo:
            n=todo.pop()
            if n in reachable:continue
            reachable.add(n)
            for sock in n.inputs:
                todo.extend(link.from_node for link in sock.links)
        for n in reachable:
            if n.type=='UVMAP':consumed.add(n.uv_map or active_uv)
            if n.type=='TEX_COORD' and n.outputs['UV'].is_linked:consumed.add(active_uv)
            if n.type=='TEX_IMAGE' and not n.inputs['Vector'].is_linked:consumed.add(active_uv)
    for uv_name in sorted(consumed,key=str):
        layer=me.uv_layers.get(uv_name or '')
        row={'object':o.name,'uv':uv_name,'present':layer is not None,'triangles':len(me.loop_triangles),'zero_uv_triangles':0,'nonfinite':0,'min_edge_ratio':None,'max_edge_ratio':None,'bad_metric_edges':0,'witnesses':[]}
        ratios=[]
        if layer:
            for t in me.loop_triangles:
                p=[ev.matrix_world@me.vertices[i].co for i in t.vertices];q=[layer.data[i].uv.copy() for i in t.loops]
                if not all(math.isfinite(x) for y in q for x in y):row['nonfinite']+=1;continue
                uvarea=abs((q[1].x-q[0].x)*(q[2].y-q[0].y)-(q[1].y-q[0].y)*(q[2].x-q[0].x))*.5
                geoarea=(p[1]-p[0]).cross(p[2]-p[0]).length*.5
                if geoarea>1e-14 and uvarea<1e-14:row['zero_uv_triangles']+=1
                for i in range(3):
                    d=(p[(i+1)%3]-p[i]).length
                    if d>.0001:
                        ratio=(q[(i+1)%3]-q[i]).length/d;ratios.append(ratio)
                        if abs(ratio-1)>.01:
                            row['bad_metric_edges']+=1
                            if len(row['witnesses'])<3:row['witnesses'].append({'triangle':t.index,'edge_m':d,'ratio':ratio})
            if ratios:row['min_edge_ratio']=min(ratios);row['max_edge_ratio']=max(ratios)
        report['consumed_uv'].append(row)
    ev.to_mesh_clear();shapes.append(v.Shape(o,dg))
report['missing_originals']=sorted(set(base)-set(o.name for o in scene.objects))
report['planning']={'evaluated_triangles':triangles,'material_submeshes':submeshes,'used_material_datablocks':len(used),'used_materials':sorted(m.name for m in used),'baseline':{'evaluated_triangles':baseline['evaluated_triangles'],'material_submeshes':baseline['authoring_material_submeshes'],'material_datablocks':len(baseline['materials'])}}
for m in used:
    row={'name':m.name,'nodes':[]}
    if m.use_nodes:
        for n in m.node_tree.nodes:
            x={'name':n.name,'type':n.type,'links':[(i.name,l.from_node.name,l.from_socket.name) for i in n.inputs for l in i.links]}
            if n.type=='UVMAP':x['uv_map']=n.uv_map
            if n.type=='TEX_IMAGE':x['image']=n.image.name if n.image else None
            if n.type=='BSDF_PRINCIPLED':x['unlinked_defaults']={i.name: list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value for i in n.inputs if not i.is_linked and hasattr(i,'default_value')}
            row['nodes'].append(x)
    report['material_nodes'].append(row)
for im in bpy.data.images:
    packed=bool(im.packed_file) or bool(getattr(im,'packed_files',()))
    report['images'].append({'name':im.name,'packed':packed,'size':list(im.size),'filepath':im.filepath,'resolved':bpy.path.abspath(im.filepath,library=im.library),'colorspace':im.colorspace_settings.name})
for lib in bpy.data.libraries:
    actual=Path(bpy.path.abspath(lib.filepath))
    report['libraries'].append({'filepath':lib.filepath,'parent':lib.parent.filepath if lib.parent else None,'exists':actual.exists(),'missing':lib.is_missing,'resolved':str(actual)})
# Independent component-to-component surface contacts. Bounding boxes are only broad phase.
by_owner=defaultdict(list)
for s in shapes:
    if s.owner:by_owner[s.owner.name].append(s)
contacts=[];isolated=[]
for owner,parts in by_owner.items():
    touched=set();pairs=[]
    for i,a in enumerate(parts):
        for b in parts[i+1:]:
            if not a.bvh or not b.bvh or not v.overlaps(a.bounds,b.bounds,.005):continue
            overlaps=a.bvh.overlap(b.bvh)
            best=None
            if overlaps:best=0.
            else:
                for sa,sb in ((a,b),(b,a)):
                    for vertex in sa.vertices:
                        hit=sb.bvh.find_nearest(vertex,.005001)
                        if hit[0] is not None and (best is None or hit[3]<best):best=float(hit[3])
            if best is not None:
                touched.update((a.name,b.name));pairs.append({'a':a.name,'b':b.name,'min_surface_gap_m':best,'intersecting_triangles':len(overlaps)})
    contacts.append({'assembly':owner,'components':len(parts),'contact_pairs':pairs})
    for a in parts:
        if a.name not in touched:isolated.append({'assembly':owner,'object':a.name,'bounds':[list(x) for x in a.bounds]})
report['internal_surface_contacts']=contacts;report['isolated_component_candidates']=isolated
report['hash_after']=hashlib.sha256(native.read_bytes()).hexdigest();report['saved_native']=False
(out/'probe.json').write_text(json.dumps(report,indent=2))
print('PROBE_COMPLETE',report['planning'], 'pose',len(report['pose_deltas']), 'dimension',len(report['dimension_deltas']), 'isolated',len(isolated),'libs',len(report['libraries']))
