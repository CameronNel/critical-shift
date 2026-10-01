import bpy, bmesh, json, hashlib, math
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('/workspace/critical-shift')
DOCK=ROOT/'sections/facility-assembly/sources/compliance-dock'
OUT=DOCK/'revamp/production/critics/slice-s03-technical-probe.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
protected=json.loads((DOCK/'revamp/production/protected-inputs.json').read_text())
report={'scope':'fresh read-only native source probe; no Blender save','source_sha256':sha(DOCK/'module_overhaul_R1.blend'),'protected_inputs':{p:{'expected':h,'actual':sha(ROOT/p),'match':sha(ROOT/p)==h} for p,h in protected.items()}}
bpy.ops.wm.open_mainfile(filepath=str(DOCK/'module.blend'),load_ui=False)
base={o.name:{'matrix':[list(r) for r in o.matrix_world],'dimensions':list(o.dimensions),'class':o.get('support_class')} for o in bpy.context.scene.objects}
bpy.ops.wm.open_mainfile(filepath=str(DOCK/'module_overhaul_R1.blend'),load_ui=False)
S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=S;bpy.context.view_layer.update()
report['scene']={'name':S.name,'objects':len(S.objects),'version':bpy.app.version_string,'stage':S.get('stage'),'revision':S.get('revision')}
report['retained']={'baseline_objects':len(base),'missing':[],'matrix_changes':[],'architectural_dimension_changes':[],'other_dimension_changes':[]}
for name,v in base.items():
 o=S.objects.get(name)
 if not o:report['retained']['missing'].append(name);continue
 dm=max(abs(o.matrix_world[i][j]-v['matrix'][i][j]) for i in range(4) for j in range(4))
 dd=max(abs(o.dimensions[i]-v['dimensions'][i]) for i in range(3))
 if dm>1e-6:report['retained']['matrix_changes'].append({'object':name,'max_delta':dm})
 if dd>1e-5:report['retained']['architectural_dimension_changes' if v['class']=='architectural' else 'other_dimension_changes'].append({'object':name,'baseline_dimensions':v['dimensions'],'current_dimensions':list(o.dimensions),'max_delta':dd})
report['libraries']=[]
for lib in bpy.data.libraries:
 path=Path(bpy.path.abspath(lib.filepath))
 report['libraries'].append({'name':lib.name,'raw':lib.filepath,'parent':lib.parent.name if lib.parent else None,'resolved':str(path),'exists':path.exists()})
report['images']=[{'name':im.name,'source':im.source,'packed':bool(im.packed_file),'raw':im.filepath,'exists':bool(im.packed_file) or im.source not in {'FILE','MOVIE','SEQUENCE','TILED'} or Path(bpy.path.abspath(im.filepath,library=im.library)).is_file()} for im in bpy.data.images]
report['fonts']=[{'name':f.name,'raw':f.filepath,'packed':bool(f.packed_file),'exists':f.filepath=='<builtin>' or bool(f.packed_file) or Path(bpy.path.abspath(f.filepath,library=f.library)).exists()} for f in bpy.data.fonts]
local=[o for o in S.objects if o.type=='MESH' and o.get('overhaul_surface')]
report['mesh_checks']=[];dg=bpy.context.evaluated_depsgraph_get();shape={}
for o in [o for o in S.objects if o.type in {'MESH','CURVE'} and (o.get('overhaul_surface') or o.parent and o.parent.name in {'D1 Staff Front Door','Checkin Counter Hatch'} or o.name.startswith('CD |'))]:
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();wv=[o.matrix_world@v.co for v in me.vertices]
 shape[o.name]={'verts':wv,'triangles':[tuple(t.vertices) for t in me.loop_triangles],'bvh':BVHTree.FromPolygons(wv,[tuple(t.vertices) for t in me.loop_triangles],all_triangles=True) if me.loop_triangles else None,'bounds':([min(v[i] for v in wv) for i in range(3)],[max(v[i] for v in wv) for i in range(3)]) if wv else None,'owner':o.parent.name if o.parent else None}
 if o.type!='MESH':ev.to_mesh_clear();continue
 bm=bmesh.new();bm.from_mesh(o.data)
 shared_bad=[]
 for e in bm.edges:
  if len(e.link_faces)==2:
   ends=[]
   for f in e.link_faces:
    for l in f.loops:
     if l.edge==e:ends.append((l.vert.index,l.link_loop_next.vert.index))
   if len(ends)==2 and ends[0]==ends[1]:shared_bad.append(e.index)
 bm.free()
 centre=sum(wv,Vector())/len(wv) if wv else Vector()
 volume=sum((wv[t.vertices[0]]-centre).dot((wv[t.vertices[1]]-centre).cross(wv[t.vertices[2]]-centre))/6 for t in me.loop_triangles)
 rawuv=o.data.uv_layers.get('CD_Physical_1m');evuv=me.uv_layers.get('CD_Physical_1m');uvrec={'named_layer':bool(rawuv),'active_layer':o.data.uv_layers.active.name if o.data.uv_layers.active else None,'source_faces':len(o.data.polygons),'source_degenerate_faces':[],'source_nonfinite':0,'evaluated_triangles':len(me.loop_triangles),'evaluated_degenerate_triangles':[],'world_area':0,'uv_area':0,'singular_values_min':None,'singular_values_max':None,'anisotropy_max':None,'distortion_examples':[]}
 if rawuv:
  for f in o.data.polygons:
   coords=[rawuv.data[i].uv for i in f.loop_indices];area=abs(sum(coords[i].x*coords[(i+1)%len(coords)].y-coords[(i+1)%len(coords)].x*coords[i].y for i in range(len(coords)))/2)
   if area<1e-12:uvrec['source_degenerate_faces'].append(f.index)
   uvrec['source_nonfinite']+=sum(not all(math.isfinite(x) for x in v) for v in coords)
 ratios=[];dist=[]
 if evuv:
  for t in me.loop_triangles:
   p=[wv[i] for i in t.vertices];u=[evuv.data[i].uv for i in t.loops];e1=p[1]-p[0];e2=p[2]-p[0];a=e1.length
   if a<1e-12:continue
   bx=e1.dot(e2)/a;by=math.sqrt(max(0,e2.length_squared-bx*bx));wa=a*by/2;ua=abs((u[1]-u[0]).cross(u[2]-u[0]))/2
   uvrec['world_area']+=wa;uvrec['uv_area']+=ua
   if wa<1e-12:continue
   if ua<1e-12:uvrec['evaluated_degenerate_triangles'].append(t.index);continue
   d1=u[1]-u[0];d2=u[2]-u[0];j11=d1.x/a;j21=d1.y/a;j12=(d2.x-j11*bx)/by;j22=(d2.y-j21*bx)/by
   aa=j11*j11+j21*j21;bb=j12*j12+j22*j22;ab=j11*j12+j21*j22;dis=math.sqrt((aa-bb)**2+4*ab*ab);l1=max(0,(aa+bb+dis)/2);l2=max(0,(aa+bb-dis)/2);smax=math.sqrt(l1);smin=math.sqrt(l2);an=smax/smin if smin>1e-10 else 1e20
   ratios.append((smin,smax,an))
   if wa>.00001 and (smin<.85 or smax>1.15 or an>1.2):dist.append({'triangle':t.index,'polygon':t.polygon_index,'world_area':wa,'uv_area':ua,'sv_min':smin,'sv_max':smax,'anisotropy':an})
 if ratios:
  uvrec.update(singular_values_min=min(x[0] for x in ratios),singular_values_max=max(x[1] for x in ratios),anisotropy_max=max(x[2] for x in ratios))
 uvrec['distortion_examples']=sorted(dist,key=lambda x:x['world_area'],reverse=True)[:10];uvrec['distorted_area']=sum(x['world_area'] for x in dist)
 rec={'object':o.name,'new':o.name not in base,'materials':[m.name for m in o.data.materials],'owner':o.parent.name if o.parent else None,'bounds':shape[o.name]['bounds'],'raw_faces':len(o.data.polygons),'eval_triangles':len(me.loop_triangles),'raw_shared_edge_winding_failures':shared_bad,'eval_signed_volume_m3':volume,'uv':uvrec,'modifiers':[{'type':m.type,'name':m.name} for m in o.modifiers]}
 report['mesh_checks'].append(rec);ev.to_mesh_clear()
# Detailed AABB geometry gaps for authored support-bearing parts. This is a witness,
# not a complete structural solver; ray/nearest data supplements authored ancestry.
pairs=[('Hatch speaking aperture plate','Hatch security grille bottom'),('CD | Speaking glazing clamp','Hatch security grille bottom'),('Hatch speaking aperture plate','Transaction counter slab'),('CD | Counter handling scar','Transaction counter slab'),('Authority stamp rubber base','CD | Counter linoleum inset'),('Ink pad tin base','CD | Counter linoleum inset'),('Counter pen holder base','CD | Counter linoleum inset'),('CD | Counter gusset','Hatch wall sill base'),('CD | Counter gusset.001','Hatch wall sill base'),('CD | Counter gusset','Transaction counter slab'),('CD | Counter gusset.001','Transaction counter slab'),('CD | Task folded shade','CD | Task wall bracket'),('CD | Task frosted lens','CD | Task folded shade'),('CD | Speaking glazing clamp','Hatch speaking aperture plate'),('CD | Speaking instruction decal','Hatch speaking aperture plate'),('Speaking baffle ring','Hatch speaking aperture plate'),('CD | D1 service lid','CD | D1 service mounting back')]
# Capture exact scene names and bounds for support roots and likely parts.
report['support_inventory']=[{'object':o.name,'parent':o.parent.name if o.parent else None,'class':o.get('support_class'),'target':o.get('support_target'),'anchor':list(o.matrix_world.translation) if o.get('contact_anchor') else None,'bounds':shape[o.name]['bounds'] if o.name in shape else None} for o in S.objects if o.name.startswith('CD |') or o.name in {'Hatch wall sill base','Transaction counter slab','Hatch speaking aperture plate','Speaking baffle ring','Office front wall mid','Office front head lintel'}]
report['pair_probes']=[]
# Architecture targets must also be evaluated.
for name in {v for pair in pairs for v in pair}:
 o=S.objects.get(name)
 if not o or name in shape:continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();wv=[o.matrix_world@v.co for v in me.vertices]
 shape[name]={'verts':wv,'triangles':[tuple(t.vertices) for t in me.loop_triangles],'bvh':BVHTree.FromPolygons(wv,[tuple(t.vertices) for t in me.loop_triangles],all_triangles=True),'bounds':([min(v[i] for v in wv) for i in range(3)],[max(v[i] for v in wv) for i in range(3)])};ev.to_mesh_clear()
for n1,n2 in pairs:
 if n1 not in shape or n2 not in shape:
  report['pair_probes'].append({'a':n1,'b':n2,'missing':True});continue
 s1,s2=shape[n1],shape[n2];g=[max(0,s2['bounds'][0][i]-s1['bounds'][1][i],s1['bounds'][0][i]-s2['bounds'][1][i]) for i in range(3)];md=math.inf
 for src,dst in [(s1,s2),(s2,s1)]:
  for p in src['verts']:
   h=dst['bvh'].find_nearest(p)
   if h[0] is not None:md=min(md,h[3])
 report['pair_probes'].append({'a':n1,'b':n2,'aabb_axis_gaps_m':g,'aabb_min_gap_m':Vector(g).length,'nearest_vertex_to_surface_m':md,'surface_triangle_overlap_pairs':len(s1['bvh'].overlap(s2['bvh']))})
report['speaking_cluster_nearest_external']=[]
cluster={'Hatch speaking aperture plate','Speaking baffle ring'}|{n for n in shape if 'Speaking' in n or 'Speak instruction' in n}
for name in cluster:
 if name not in shape:continue
 near=[]
 for other,sh in shape.items():
  if other in cluster:continue
  a1,a2=shape[name]['bounds'],sh['bounds'];g=[max(0,a2[0][i]-a1[1][i],a1[0][i]-a2[1][i]) for i in range(3)]
  near.append({'object':other,'aabb_axis_gaps_m':g,'aabb_min_gap_m':Vector(g).length})
 report['speaking_cluster_nearest_external'].append({'object':name,'nearest_external':sorted(near,key=lambda x:x['aabb_min_gap_m'])[:6]})

report['wall_coplanar_rays']=[]
for x in [-4.6125,-2.535]:
 row={'x':x,'z':2.7,'hits':[]}
 for name in ['Office front wall mid','Office front wall east','Office front head lintel']:
  sh=shape.get(name)
  if sh:
   hit=sh['bvh'].ray_cast(Vector((x,3.0,2.7)),Vector((0,1,0)),1)
   if hit[0] is not None:row['hits'].append({'object':name,'point':list(hit[0]),'normal':list(hit[1]),'distance':hit[3]})
 report['wall_coplanar_rays'].append(row)
report['wall_volume_overlaps']=[]
for name in ['Office front wall mid','Office front wall east']:
 a=shape[name]['bounds'];b=shape['Office front head lintel']['bounds'];lo=[max(a[0][i],b[0][i]) for i in range(3)];hi=[min(a[1][i],b[1][i]) for i in range(3)]
 report['wall_volume_overlaps'].append({'object':name,'with':'Office front head lintel','overlap_bounds':[lo,hi],'overlap_volume_m3':math.prod(max(0,hi[i]-lo[i]) for i in range(3)),'coincident_front_y':a[0][1]==b[0][1]})
report['probe_method_notes']=['Library.filepath is relative to current loaded file; image.filepath resolves in owning library context.','Signed volume uses recentered world vertices to avoid floating-point cancellation on tiny fasteners.','AABB gaps are rigorous lower bounds for separation; nearest-vertex distances alone are not exact mesh-mesh separation.']
report['source_unchanged_after_probe']=sha(DOCK/'module_overhaul_R1.blend')==report['source_sha256']
OUT.write_text(json.dumps(report,indent=2));print('TECHNICAL_PROBE_WRITTEN',OUT)
print('RETAINED',json.dumps(report['retained']))
print('MESHES',len(report['mesh_checks']),'UV_DEGENERATE_SOURCE',sum(len(r['uv']['source_degenerate_faces']) for r in report['mesh_checks']),'UV_DEGENERATE_EVAL',sum(len(r['uv']['evaluated_degenerate_triangles']) for r in report['mesh_checks']))
print('PAIR_PROBES',json.dumps(report['pair_probes']))
