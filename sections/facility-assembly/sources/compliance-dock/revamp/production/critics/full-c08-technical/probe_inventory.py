import bpy, hashlib, json, math, collections
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock')
OUT=R/'revamp/production/critics/full-c08-technical'
SRC=R/'module_overhaul_R1.blend'
EXPECTED='d2514e668ea2b24e8b4ede6bde870e12f10c1afd6d6e1892b12c016266bd7b35'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC)==EXPECTED
bpy.ops.wm.open_mainfile(filepath=str(R/'module.blend'),load_ui=False)
base={o.name:[float(v) for row in o.matrix_world for v in row] for o in bpy.context.scene.objects}
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False)
scene=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=scene
deps=bpy.context.evaluated_depsgraph_get()
report={'source_sha256':EXPECTED,'blender':bpy.app.version_string,'baseline_objects':len(base),'scene':scene.name,'scene_objects':len(scene.objects),'scenes':list(bpy.data.scenes.keys()),'baseline_matrix_differences':[],'objects':[],'images':[],'libraries':[],'fonts':[],'materials':[],'totals':{}}
for name,m in base.items():
 o=scene.objects.get(name)
 if o is None:report['baseline_matrix_differences'].append({'object':name,'missing':True});continue
 delta=max(abs(a-b) for a,b in zip(m,[float(v) for row in o.matrix_world for v in row]))
 if delta>1e-8:report['baseline_matrix_differences'].append({'object':name,'max_delta':delta})
tri=slots=0;deg=[];missing=[];usedm=set();uvmetric=[];uvcloth=[];dup=collections.defaultdict(list)
for o in scene.objects:
 row={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'library':o.library.filepath if o.library else None,'hidden_render':o.hide_render,'scale':list(o.scale),'origin':list(o.matrix_world.translation),'props':{k:str(v) for k,v in o.items()},'modifiers':[{'name':m.name,'type':m.type,'show_render':m.show_render,'show_viewport':m.show_viewport} for m in o.modifiers]}
 if o.type in {'MESH','CURVE','FONT','SURFACE','META'}:
  ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();vs=[o.matrix_world@v.co for v in me.vertices]
  row.update(vertices=len(me.vertices),polygons=len(me.polygons),triangles=len(me.loop_triangles),material_slots=[m.name if m else None for m in me.materials],uv_layers=list(me.uv_layers.keys()),bbox=[[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]] if vs else None)
  row['origin_in_bounds']=bool(vs) and all(row['bbox'][0][k]-.1<=o.matrix_world.translation[k]<=row['bbox'][1][k]+.1 for k in range(3))
  tri+=len(me.loop_triangles);slots+=len({p.material_index for p in me.polygons});usedm.update(m.name for m in me.materials if m)
  if not me.materials or any(m is None for m in me.materials):missing.append(o.name)
  degcount=sum(1 for t in me.loop_triangles if (vs[t.vertices[1]]-vs[t.vertices[0]]).cross(vs[t.vertices[2]]-vs[t.vertices[0]]).length<1e-12)
  if degcount:deg.append({'object':o.name,'count':degcount})
  edges=collections.Counter(tuple(sorted((p.vertices[i],p.vertices[(i+1)%len(p.vertices)]))) for p in me.polygons for i in range(len(p.vertices)))
  row['edge_users']=dict(collections.Counter(edges.values()));row['signed_volume']=sum(vs[t.vertices[0]].dot(vs[t.vertices[1]].cross(vs[t.vertices[2]]))/6 for t in me.loop_triangles)
  signature=hashlib.sha256(json.dumps({'v':[tuple(round(c,7) for c in v) for v in vs],'p':[list(p.vertices) for p in me.polygons]},separators=(',',':')).encode()).hexdigest();dup[signature].append(o.name)
  for lname in ['CD_Physical_1m','CD_Fabric_Cut_1m']:
   layer=me.uv_layers.get(lname)
   if not layer:continue
   ratios=[];anis=[];bad=0;area3=area2=0
   for t in me.loop_triangles:
    verts=[vs[i] for i in t.vertices];uv=[layer.data[i].uv.copy() for i in t.loops]
    a=(verts[1]-verts[0]).cross(verts[2]-verts[0]).length*.5;b=abs((uv[1]-uv[0]).cross(uv[2]-uv[0]))*.5;area3+=a;area2+=b
    rs=[]
    for i in range(3):
     d=(verts[(i+1)%3]-verts[i]).length
     if d>1e-4:rs.append((uv[(i+1)%3]-uv[i]).length/d)
    if rs:
     ratios.extend(rs);anis.append(max(rs)/max(min(rs),1e-20))
     if any(abs(r-1)>.01 for r in rs):bad+=1
   def percent(vals,p):return sorted(vals)[min(len(vals)-1,int((len(vals)-1)*p))] if vals else None
   ur={'object':o.name,'layer':lname,'triangles':len(me.loop_triangles),'bad_triangles_1percent_metric':bad,'ratio_min':min(ratios) if ratios else None,'ratio_max':max(ratios) if ratios else None,'ratio_p50':percent(ratios,.5),'ratio_p95':percent(ratios,.95),'edge_anisotropy_max':max(anis) if anis else None,'surface_area_m2':area3,'uv_area':area2}
   (uvmetric if lname=='CD_Physical_1m' else uvcloth).append(ur)
  ev.to_mesh_clear()
 report['objects'].append(row)
for im in bpy.data.images:
 report['images'].append({'name':im.name,'filepath':im.filepath,'size':list(im.size),'source':im.source,'packed':bool(im.packed_file),'users':im.users,'colorspace':im.colorspace_settings.name,'props':{k:str(v) for k,v in im.items()}})
for lib in bpy.data.libraries:report['libraries'].append({'name':lib.name,'filepath':lib.filepath,'exists':Path(bpy.path.abspath(lib.filepath)).exists()})
for f in bpy.data.fonts:report['fonts'].append({'name':f.name,'filepath':f.filepath,'packed':bool(f.packed_file),'users':f.users})
for m in bpy.data.materials:
 if m.name not in usedm:continue
 report['materials'].append({'name':m.name,'users':m.users,'library':m.library.filepath if m.library else None,'nodes':[{'name':n.name,'type':n.type,'uv_map':getattr(n,'uv_map',None),'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None} for n in m.node_tree.nodes] if m.node_tree else [],'links':[{'from':l.from_node.name+'.'+l.from_socket.name,'to':l.to_node.name+'.'+l.to_socket.name} for l in m.node_tree.links] if m.node_tree else []})
report['totals']={'evaluated_triangles':tri,'used_material_submeshes':slots,'used_materials':len(usedm),'local_material_families':len([n for n in usedm if bpy.data.materials[n].library is None]),'degenerate_objects':deg,'missing_material_objects':missing,'duplicate_world_geometry_groups':[v for v in dup.values() if len(v)>1]}
report['physical_uv']=uvmetric;report['cloth_uv']=uvcloth
assert sha(SRC)==EXPECTED
(OUT/'inventory.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:report[k] for k in ['baseline_objects','scene_objects','baseline_matrix_differences','totals','images','libraries','fonts']},indent=2))
