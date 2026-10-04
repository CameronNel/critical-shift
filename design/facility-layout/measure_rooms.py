"""Measures the world-space bounding box of a Blender file (mesh, curve and text objects) and writes JSON.

Run:  blender -b --factory-startup <file.blend> --python measure_rooms.py -- <out.json>
"""
import bpy, sys, json, re
from mathutils import Vector
out=sys.argv[sys.argv.index('--')+1]
dg=bpy.context.evaluated_depsgraph_get()
def bbox(objs):
    mn=Vector((1e9,)*3); mx=Vector((-1e9,)*3); n=0
    for o in objs:
        if o.type not in ('MESH','CURVE','FONT','SURFACE','META'): continue
        if o.hide_render and o.hide_viewport: continue
        try:
            ev=o.evaluated_get(dg)
            corners=[ev.matrix_world@Vector(c) for c in ev.bound_box]
        except Exception: continue
        if not corners: continue
        for c in corners:
            for i in range(3):
                mn[i]=min(mn[i],c[i]); mx[i]=max(mx[i],c[i])
        n+=1
    if n==0: return None
    return {'min':[round(v,2) for v in mn],'max':[round(v,2) for v in mx],'size':[round(mx[i]-mn[i],2) for i in range(3)],'n':n}
res={'file':bpy.data.filepath.split('/')[-1],'scenes':[s.name for s in bpy.data.scenes],'objects':len(bpy.data.objects),'libraries':[l.filepath for l in bpy.data.libraries]}
allm=[o for o in bpy.context.scene.objects]
res['overall']=bbox(allm)
cols=[]
def walk(c,depth=0):
    objs=list(c.objects)
    b=bbox(objs) if objs else None
    cols.append({'name':c.name,'depth':depth,'direct_objs':len(objs),'bbox':b})
    for ch in c.children: walk(ch,depth+1)
walk(bpy.context.scene.collection)
res['collections']=[c for c in cols if c['bbox'] or c['depth']<2]
pat=re.compile(r'door|portal|^IF_|threshold|entry|exit|airlock|gate|floor|ceiling|roof|shell|slab',re.I)
named=[]
for o in allm:
    if pat.search(o.name) and o.type in('MESH','EMPTY','CURVE'):
        b=bbox([o]) if o.type!='EMPTY' else None
        named.append({'name':o.name,'type':o.type,'loc':[round(v,2) for v in o.matrix_world.translation],'size':b['size'] if b else None,'min':b['min'] if b else None,'max':b['max'] if b else None})
res['named']=named[:250]
json.dump(res,open(out,'w'),indent=1)
print('MEASURED',res['file'],res['objects'],res['overall'])
