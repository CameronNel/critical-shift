import bpy,json,math,hashlib,collections
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock'); OUT=R/'revamp/production/critics/full-c06-technical'
def v(x): return [float(a) for a in x]
def props(x): return {k: str(x[k]) for k in x.keys()}
bpy.ops.wm.open_mainfile(filepath=str(R/'module.blend'),load_ui=False)
base={o.name:[[float(x) for x in row] for row in o.matrix_world] for o in bpy.context.scene.objects}
baseline={'objects':len(base),'triangles':0,'submeshes':0,'materials':set()}
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.context.scene.objects:
 if o.type not in {'MESH','FONT','CURVE','SURFACE','META'}:continue
 e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();baseline['triangles']+=len(m.loop_triangles);baseline['submeshes']+=len(set(p.material_index for p in m.polygons));baseline['materials'].update(s.material.name for s in o.material_slots if s.material);e.to_mesh_clear()
baseline['materials']=sorted(baseline['materials'])
bpy.ops.wm.open_mainfile(filepath=str(R/'module_overhaul_R1.blend'),load_ui=False)
s=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=s;dg=bpy.context.evaluated_depsgraph_get()
report={'blender':bpy.app.version_string,'source_sha256':hashlib.sha256((R/'module_overhaul_R1.blend').read_bytes()).hexdigest(),'baseline':baseline,'scene':s.name,'units':s.unit_settings.scale_length,'scene_properties':props(s),'object_count':len(s.objects),'protected_matrix_count':len(base),'missing_inherited':[],'matrix_changes':[],'objects':{},'materials':{},'images':[],'fonts':[],'libraries':[],'contacts':[]}
for n,m in base.items():
 o=s.objects.get(n)
 if o is None:report['missing_inherited'].append(n);continue
 delta=max(abs(float(o.matrix_world[i][j])-m[i][j]) for i in range(4) for j in range(4))
 if delta>1e-6:report['matrix_changes'].append({'object':n,'max_abs_delta':delta})
geo={};tris=0;submesh=0;usedmat=set();dups=collections.defaultdict(list)
for o in s.objects:
 row={'type':o.type,'parent':o.parent.name if o.parent else None,'hide_render':o.hide_render,'properties':props(o),'matrix': [v(r) for r in o.matrix_world],'materials':[slot.material.name if slot.material else None for slot in o.material_slots],'modifiers': [{'type':m.type,'name':m.name,'render':m.show_render} for m in o.modifiers]}
 report['objects'][o.name]=row
 if o.type not in {'MESH','FONT','CURVE','SURFACE','META'}:continue
 e=o.evaluated_get(dg);mesh=e.to_mesh(preserve_all_data_layers=True,depsgraph=dg);mesh.calc_loop_triangles();pts=[o.matrix_world@x.co for x in mesh.vertices];polys=[list(p.vertices) for p in mesh.polygons];t=[list(x.vertices) for x in mesh.loop_triangles]
 row.update({'evaluated_vertices':len(pts),'triangles':len(t),'polygons':len(polys),'bounds':[[min((p[i] for p in pts),default=0) for i in range(3)],[max((p[i] for p in pts),default=0) for i in range(3)]],'uv_layers':[x.name for x in mesh.uv_layers]})
 edgecounts=collections.Counter(tuple(sorted((p[i],p[(i+1)%len(p)]))) for p in polys for i in range(len(p)));row['boundary_edges']=sum(x==1 for x in edgecounts.values());row['nonmanifold_edges']=sum(x>2 for x in edgecounts.values())
 row['negative_determinant']=o.matrix_world.determinant()<0
 usedslots=set(p.material_index for p in mesh.polygons);row['used_slots']=sorted(usedslots)
 if not o.hide_render:
  tris+=len(t);submesh+=len(usedslots);usedmat.update(o.material_slots[i].material.name for i in usedslots if i<len(o.material_slots) and o.material_slots[i].material)
 # UV stretch via triangle singular value approximation: ratio area-normalized edge extrema.
 if mesh.uv_layers.active:
  uv=mesh.uv_layers.active.data;ratios=[];zero=[]
  for tri in mesh.loop_triangles:
   ps=[pts[i] for i in tri.vertices];us=[Vector(uv[i].uv) for i in tri.loops]; wa=(ps[1]-ps[0]).cross(ps[2]-ps[0]).length*.5;ua=abs((us[1].x-us[0].x)*(us[2].y-us[0].y)-(us[1].y-us[0].y)*(us[2].x-us[0].x))*.5
   if wa>1e-10 and ua<1e-12:zero.append(tri.polygon_index)
   if wa>1e-10 and ua>1e-12:ratios.append(math.sqrt(ua/wa))
  row['uv_zero_area_faces']=sorted(set(zero));row['uv_density_minmax']=[min(ratios,default=0),max(ratios,default=0)]
 bvh=BVHTree.FromPolygons(pts,t,all_triangles=True) if t else None;geo[o.name]={'obj':o,'pts':pts,'tris':t,'polys':polys,'bvh':bvh}
 fingerprint=hashlib.sha256(json.dumps(sorted(tuple(round(float(x),6) for p in [pts[i] for i in tri] for x in p) for tri in t)).encode()).hexdigest();dups[fingerprint].append(o.name)
 e.to_mesh_clear()
report['planning']={'visible_evaluated_triangles':tris,'visible_material_submeshes':submesh,'used_material_names':sorted(usedmat),'used_material_count':len(usedmat),'families': sorted({str(bpy.data.materials[n].get('family',bpy.data.materials[n].get('material_family',n))) for n in usedmat})}
report['exact_duplicate_world_meshes']=[x for x in dups.values() if len(x)>1]
for mat in bpy.data.materials:
 if mat.name not in usedmat:continue
 report['materials'][mat.name]={'properties':props(mat),'nodes':[{'name':n.name,'type':n.type,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None,'inputs':{i.name:(v(i.default_value) if hasattr(i.default_value,'__len__') and not isinstance(i.default_value,str) else i.default_value) for i in n.inputs if hasattr(i,'default_value') and isinstance(i.default_value,(float,int,str,Vector))}} for n in mat.node_tree.nodes] if mat.node_tree else []}
for lib in bpy.data.libraries:
 path=Path(bpy.path.abspath(lib.filepath,library=lib.parent));report['libraries'].append({'name':lib.name,'path':str(path),'exists':path.is_file(),'relative':lib.filepath.startswith('//')})
for im in bpy.data.images:
 path=Path(bpy.path.abspath(im.filepath,library=im.library));report['images'].append({'name':im.name,'path':str(path),'source':im.source,'packed':bool(im.packed_file),'exists':path.is_file(),'size':list(im.size),'colorspace':im.colorspace_settings.name,'used':im.users})
for f in bpy.data.fonts:
 path=Path(bpy.path.abspath(f.filepath,library=f.library));report['fonts'].append({'name':f.name,'path':str(path),'packed':bool(f.packed_file),'exists':path.is_file()})
def root(o):
 while o:
  if o.get('support_class')=='supported_assembly':return o
  o=o.parent
for anchor in [o for o in s.objects if o.get('contact_anchor')]:
 r=root(anchor);p=anchor.matrix_world.translation;row={'anchor':anchor.name,'assembly':r.name if r else None,'point':v(p)}
 if not r:report['contacts'].append(row);continue
 d=(r.matrix_world.to_3x3()@Vector(r['support_direction'])).normalized();target=geo.get(r.get('support_target'));row['target']=r.get('support_target');row['direction']=v(d)
 if target:
  loc,n,idx,dist=target['bvh'].ray_cast(p-d*.25,d,.5)
  row['support_hit']=v(loc) if loc is not None else None
  if loc is not None:row['support_signed_gap']=(loc-p).dot(d);row['angle_deg']=math.degrees(math.acos(max(-1,min(1,n.dot(-d)))))
 comps=[x for x in geo.values() if root(x['obj'])==r];nearest=[]
 for x in comps:
  loc,n,idx,dist=x['bvh'].find_nearest(p)
  if loc is not None:nearest.append((dist,x['obj'].name,v(loc)))
 row['nearest_components']=sorted(nearest)[:3];report['contacts'].append(row)
(OUT/'native-independent.json').write_text(json.dumps(report,indent=2))
# evaluated surface inventory for focused independent ray/contact analysis
(OUT/'evaluated-surfaces.json').write_text(json.dumps({n:{'points':[v(p) for p in x['pts']],'triangles':x['tris'],'polygons':x['polys']} for n,x in geo.items()}))
print('INDEPENDENT_NATIVE_DONE',report['planning'], 'contacts',len(report['contacts']),'matrix changes',report['matrix_changes'])
