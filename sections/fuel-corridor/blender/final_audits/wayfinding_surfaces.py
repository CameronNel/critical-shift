"""Read-only evaluated glyph/backing and front-obstruction audit."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
S=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
out=Path(__file__).resolve().parents[2]/'production/evidence/final-pass'
verts=[]; faces=[]; owners=[]
for o in S.objects:
    if o.type!='MESH' or o.hide_render or o.get('surface_decal',False):continue
    ev=o.evaluated_get(dg); me=ev.to_mesh(); off=len(verts)
    verts.extend(ev.matrix_world@v.co for v in me.vertices)
    faces.extend(tuple(off+i for i in p.vertices) for p in me.polygons)
    owners.extend([o.name]*len(me.polygons));ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,faces,all_triangles=False)
rows=[]
for o in S.objects:
    is_text=o.type=='FONT'
    is_arrow=o.type=='MESH' and o.get('surface_decal') and ('chevron' in o.name or 'arrow' in o.name)
    if not(is_text or is_arrow):continue
    if is_text:normal=(o.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
    elif 'wayfinding_normal' in o:normal=Vector(o['wayfinding_normal']).normalized()
    elif o.parent and o.parent.name in ['East_reactor_route','Bypass_clean_route','Cross_service_identity','Plant_branch_identity','Delivery_reactor_identity','Clean_leg_identity']:normal=(o.parent.matrix_world.to_3x3()@Vector((0,-1,0))).normalized()
    else:continue
    ev=o.evaluated_get(dg);me=ev.to_mesh();points=[ev.matrix_world@v.co for v in me.vertices][::max(1,len(me.vertices)//180)];ev.to_mesh_clear()
    missing=[];blocked=[];backing=set()
    for p in points:
        hit,n,idx,dist=bvh.ray_cast(p+normal*.002,-normal,.082)
        if hit is None:missing.append(list(p))
        else:backing.add(owners[idx])
        hit,n,idx,dist=bvh.ray_cast(p+normal*.50,-normal,.495)
        if hit is not None:blocked.append({'point':list(p),'object':owners[idx],'depth_ahead_m':.50-dist})
    rows.append({'name':o.name,'text':o.data.body if is_text else None,'font_size':o.data.size if is_text else None,'samples':len(points),'unbacked':len(missing),'front_blocked':len(blocked),'backing':sorted(backing),'unbacked_examples':missing[:8],'blocker_examples':blocked[:8]})
report={'revision':S.get('revision'),'objects':len(S.objects),'method':'Evaluated glyph/arrow vertices; backing within80mm, physical obstruction within500mm in normal direction. Does not alone prove viewing-distance legibility.','rows':rows}
tag=S.get('revision','unknown')
(out/('wayfinding-'+tag+'.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'audited':len(rows),'issues':[{'name':r['name'],'text':r['text'],'unbacked':r['unbacked'],'blocked':r['front_blocked'],'samples':r['samples'],'blockers':sorted(set(p['object'] for p in r['blocker_examples']))} for r in rows if r['unbacked'] or r['front_blocked']]}))

