"""Independent C9 read-only evaluated whole-scene probe. Never saves a native file."""
import bpy, json, math, hashlib, time, collections
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent
ROOM=OUT.parents[3]
started=time.time()
S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=S
DG=bpy.context.evaluated_depsgraph_get()
def vv(v): return [round(float(x),9) for x in v]
def props(o): return {k:str(o[k]) for k in o.keys()}
def ancestor(o):
 while o:
  if o.get('support_class')=='supported_assembly':return o.name
  o=o.parent
def box(v):return [[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]]
def close(a,b,p=.005001):return all(a[0][i]<=b[1][i]+p and b[0][i]<=a[1][i]+p for i in range(3))
parts=[];objects=[];mats={};uvstats=[];duptris=collections.defaultdict(list)
for M in {m for o in S.objects if o.type in {'MESH','CURVE','FONT'} for m in o.data.materials if m}:
 reachable=set();stack=[n for n in M.node_tree.nodes if n.type=='OUTPUT_MATERIAL'] if M.node_tree else []
 while stack:
  n=stack.pop()
  if n.name in reachable:continue
  reachable.add(n.name)
  stack += [l.from_node for sock in n.inputs for l in sock.links]
 mats[M.name]={'users':M.users,'library':M.library.filepath if M.library else None,'used_uv':[n.uv_map for n in M.node_tree.nodes if n.name in reachable and n.type=='UVMAP'] if M.node_tree else [],'nodes':[{'name':n.name,'type':n.type,'active':n.name in reachable,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None} for n in M.node_tree.nodes] if M.node_tree else []}
for O in S.objects:
 rec={'name':O.name,'type':O.type,'matrix':[vv(r) for r in O.matrix_world],'dimensions':vv(O.dimensions),'parent':O.parent.name if O.parent else None,'owner':ancestor(O),'props':props(O),'hide_render':O.hide_render,'library':O.library.filepath if O.library else None}
 objects.append(rec)
 if O.type not in {'MESH','CURVE','FONT','SURFACE'}:continue
 E=O.evaluated_get(DG);me=E.to_mesh();me.calc_loop_triangles();V=[O.matrix_world@v.co for v in me.vertices];T=[tuple(t.vertices) for t in me.loop_triangles]
 rec.update(triangles=len(T),submeshes=len({p.material_index for p in me.polygons}),materials=[m.name if m else None for m in me.materials],uv_layers=[u.name for u in me.uv_layers],bounds=box(V) if V else None,modifiers=[{'type':m.type,'name':m.name,'show_render':m.show_render} for m in O.modifiers])
 # Weld coincident positions for topological connected parts, independent of UV seams.
 parent=list(range(len(V)));weld={}
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 def union(i,j):parent[find(i)]=find(j)
 for i,v in enumerate(V):
  k=tuple(round(x,7) for x in v)
  if k in weld:union(i,weld[k])
  else:weld[k]=i
 for t in T:union(t[0],t[1]);union(t[1],t[2])
 groups=collections.defaultdict(list)
 for ti,t in enumerate(T):groups[find(t[0])].append(ti)
 rec['components']=len(groups)
 for cid,ids in enumerate(groups.values()):
  inds=sorted({j for ti in ids for j in T[ti]});mapping={j:i for i,j in enumerate(inds)};pv=[V[j] for j in inds];pt=[tuple(mapping[j] for j in T[ti]) for ti in ids]
  area=0.;volume=0.;bad=[];edges=collections.defaultdict(list);samples=list(pv)
  for ti,tri in zip(ids,pt):
   a,b,c=[pv[j] for j in tri];ar=(b-a).cross(c-a).length/2;area+=ar;volume+=(a-pv[0]).dot((b-pv[0]).cross(c-pv[0]))/6
   if ar<1e-12:bad.append(ti)
   samples.append((a+b+c)/3)
   for x,y in zip(tri,tri[1:]+tri[:1]):edges[tuple(sorted((tuple(round(z,7) for z in pv[x]),tuple(round(z,7) for z in pv[y]))))].append((x,y))
   key=tuple(sorted(tuple(round(z,7) for z in p) for p in (a,b,c)))
   if ar>1e-10:duptris[key].append([O.name,cid,ti])
  row={'id':len(parts),'object':O.name,'component':cid,'owner':ancestor(O),'architectural':O.get('support_class')=='architectural','bounds':box(pv),'area_m2':area,'signed_volume_m3':volume,'triangles':len(pt),'degenerate_triangle_ids':bad,'boundary_edges':sum(len(e)==1 for e in edges.values()),'nonmanifold_edges':sum(len(e)>2 for e in edges.values()),'closed_winding':not any(len(e)!=2 for e in edges.values()),'v':pv,'t':pt,'samples':samples,'bvh':BVHTree.FromPolygons(pv,pt,all_triangles=True,epsilon=1e-8) if pt else None}
  parts.append(row)
 # Exact differential of every evaluated triangle for each actually consumed UV map.
 accum={}
 for tri in me.loop_triangles:
  mat=me.materials[tri.material_index] if tri.material_index<len(me.materials) else None
  for layername in set(mats.get(mat.name if mat else '',{}).get('used_uv',[])):
   key=(mat.name,layername);z=accum.setdefault(key,{'triangles':0,'area_m2':0,'degenerate_world':0,'degenerate_uv':0,'ratio_area_gt2':0,'ratio_area_gt5':0,'max_anisotropy':1,'max_witness':None,'density_area_sum':0})
   layer=me.uv_layers.get(layername);z['triangles']+=1
   if not layer:z['missing_layer']=True;continue
   a,b,c=[V[i] for i in tri.vertices];u,v,w=[layer.data[i].uv.copy() for i in tri.loops];e=b-a;f=c-a;ar=e.cross(f).length/2;z['area_m2']+=ar
   if ar<1e-12:z['degenerate_world']+=1;continue
   x=e.length;fx=f.dot(e)/x;fy=2*ar/x;du=v-u;dv=w-u
   j00=du.x/x;j10=du.y/x;j01=(dv.x-j00*fx)/fy;j11=(dv.y-j10*fx)/fy
   aa=j00*j00+j10*j10;bb=j00*j01+j10*j11;cc=j01*j01+j11*j11;d=math.sqrt(max(0,(aa-cc)**2+4*bb*bb));lo=max(0,(aa+cc-d)/2);hi=(aa+cc+d)/2
   ratio=math.sqrt(hi/lo) if lo>1e-18 else 1e20
   if lo<=1e-18:z['degenerate_uv']+=1
   if ratio>2:z['ratio_area_gt2']+=ar
   if ratio>5:z['ratio_area_gt5']+=ar
   z['density_area_sum']+=ar*math.sqrt(abs(j00*j11-j01*j10))
   if ratio>z['max_anisotropy']:z['max_anisotropy']=ratio;z['max_witness']={'triangle':tri.index,'centre':vv((a+b+c)/3),'area_m2':ar}
 for (mat,layer),z in accum.items():uvstats.append(dict(object=O.name,material=mat,layer=layer,**z))
 E.to_mesh_clear()
 if len(objects)%100==0:print('EXTRACT',len(objects),flush=True)
publicparts=[{k:v for k,v in p.items() if k not in {'v','t','samples','bvh'}} for p in parts]
result={'scene':S.name,'blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'objects':objects,'parts':publicparts,'materials':mats,'consumed_uv_differential':uvstats,'duplicate_world_triangles':[{'vertices':k,'users':v} for k,v in duptris.items() if len(v)>1],'counts':{'objects':len(objects),'parts':len(parts),'evaluated_triangles':sum(o.get('triangles',0) for o in objects),'material_submeshes':sum(o.get('submeshes',0) for o in objects),'local_material_families':len(mats)},'libraries':[{'name':L.name,'filepath':L.filepath,'absolute':bpy.path.abspath(L.filepath),'parent':L.parent.name if L.parent else None} for L in bpy.data.libraries],'images':[{'name':I.name,'path':I.filepath,'packed':bool(I.packed_file),'source':I.source,'users':I.users} for I in bpy.data.images],'fonts':[{'name':F.name,'path':F.filepath,'packed':bool(F.packed_file),'users':F.users} for F in bpy.data.fonts]}
(OUT/'inventory.json').write_text(json.dumps(result,indent=2))
print('INVENTORY_COMPLETE',result['counts'],flush=True)
contacts=[];intersections=[];candidates=0
for ai,a in enumerate(parts):
 if not a['bvh']:continue
 for b in parts[:ai]:
  if not b['bvh'] or not close(a['bounds'],b['bounds']):continue
  candidates+=1
  crossing=a['bvh'].overlap(b['bvh']) if close(a['bounds'],b['bounds'],0) else []
  best=.005001;witness=None
  # Nearest triangle surface queries use actual evaluated vertex and face-centre samples, never proxies.
  for p,q in [(a,b),(b,a)]:
   for v in p['samples']:
    if not all(q['bounds'][0][i]-best<=v[i]<=q['bounds'][1][i]+best for i in range(3)):continue
    co,n,face,d=q['bvh'].find_nearest(v,best)
    if co is not None and d<best:best=d;witness={'from':p['id'],'point':vv(v),'target_point':vv(co),'target_triangle':face,'distance_m':d}
    if best<1e-7:break
   if best<1e-7:break
  if crossing or witness:
   contacts.append({'a':a['id'],'b':b['id'],'distance_upper_bound_m':best if witness else None,'witness':witness,'crossing_triangle_pairs':len(crossing)})
  if crossing:intersections.append({'a':a['id'],'b':b['id'],'pairs':len(crossing),'pair_examples':crossing[:6]})
 if ai%100==0:print('CONTACT',ai,'/',len(parts),'candidates',candidates,flush=True)
graph=collections.defaultdict(set)
for c in contacts:graph[c['a']].add(c['b']);graph[c['b']].add(c['a'])
floor={p['id'] for p in parts if p['object']=='Floor slab'};seen=set(floor);queue=list(floor);path={i:[i] for i in floor}
while queue:
 i=queue.pop(0)
 for j in graph[i]-seen:seen.add(j);queue.append(j);path[j]=path[i]+[j]
missing=[]
for i in range(len(parts)):
 if i in seen:continue
 a=parts[i];best=1.;witness=None
 for b in parts:
  if b['id']==i or not close(a['bounds'],b['bounds'],best):continue
  for p,q in [(a,b),(b,a)]:
   for v in p['samples']:
    if not all(q['bounds'][0][j]-best<=v[j]<=q['bounds'][1][j]+best for j in range(3)):continue
    co,n,face,d=q['bvh'].find_nearest(v,best)
    if co is not None and d<best:best=d;witness={'from_component':p['id'],'target_component':q['id'],'target_object':q['object'],'point':vv(v),'target_point':vv(co),'triangle':face,'distance_m':d}
 missing.append({**publicparts[i],'nearest_surface':witness})
(OUT/'contacts.json').write_text(json.dumps({'tolerance_m':.005,'method':'Actual evaluated triangle BVH overlaps plus nearest-surface queries of all component vertices and face centres; distances are upper bounds; possible unsampled edge-edge contacts are limitations. Contacts prove touching/penetrating geometry only, not engineering load capacity.','candidates':candidates,'contacts':contacts,'intersections':intersections,'floor_graph_reachable':len(seen),'floor_graph_unreachable':missing,'chains':path,'elapsed_s':time.time()-started},indent=2))
current={o['name']:o for o in objects}
# Fresh actual immutable selected module, not an author baseline report.
bpy.ops.wm.open_mainfile(filepath=str(ROOM/'module.blend'),load_ui=False)
original=[];missingnames=[];changed=[]
for O in bpy.context.scene.objects:
 original.append(O.name)
 if O.name not in current:missingnames.append(O.name);continue
 delta=max(abs(float(O.matrix_world[r][c])-current[O.name]['matrix'][r][c]) for r in range(4) for c in range(4))
 if delta>1e-7:changed.append({'object':O.name,'max_matrix_difference':delta})
(OUT/'original-matrices.json').write_text(json.dumps({'original_count':len(original),'missing':missingnames,'changed_world_matrices':changed,'threshold':1e-7},indent=2))
print('PROBE_COMPLETE',time.time()-started,flush=True)
