"""Read-only exact semantic comparison of preserved scene and source reproduction."""
import bpy, json, hashlib, sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:]
def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=path)
    rows={}
    for o in bpy.context.scene.objects:
        row={'type':o.type,'parent':o.parent.name if o.parent else None,
             'matrix':[round(v,6) for r in o.matrix_world for v in r],
             'hidden':[o.hide_render,o.hide_viewport]}
        if o.type=='MESH':
            row.pop('matrix')
            row['vertices']=[[round(v,5) for v in (o.matrix_world @ p.co)] for p in o.data.vertices]
            row['faces']=[list(p.vertices) for p in o.data.polygons]
            row['materials']=[m.name if m else None for m in o.data.materials]
            row['face_materials']=[p.material_index for p in o.data.polygons]
        elif o.type=='FONT':
            row['text']=[o.data.body,round(o.data.size,6),round(o.data.offset,6)]
        elif o.type=='LIGHT':
            row['light']=[o.data.type,o.data.energy,list(o.data.color)]
        elif o.type=='CAMERA':row['camera']=[o.data.lens,o.data.clip_start,o.data.clip_end]
        elif o.type=='EMPTY':row.pop('matrix')
        row['modifiers']=[{'name':m.name,'type':m.type,**{p:round(getattr(m,p),7) for p in ['width','segments'] if hasattr(m,p)}} for m in o.modifiers]
        rows[o.name]=row
    return rows
a=snapshot(args[0]);b=snapshot(args[1])
diff={n:[k for k in a[n] if a[n].get(k)!=b[n].get(k)] for n in a.keys()&b.keys() if a[n]!=b[n]}
report={'baseline':args[0],'reproduction':args[1],'baseline_count':len(a),'reproduction_count':len(b),
        'missing':sorted(a.keys()-b.keys()),'added':sorted(b.keys()-a.keys()),'changed':diff,
        'scope':'Object transforms, base mesh topology/material assignment, fonts, lights, cameras, bevels; material node graphs and UVs require separate verification.'}
report['matrix_differences']={n:{'baseline':a[n]['matrix'],'reproduction':b[n]['matrix']} for n,keys in diff.items() if 'matrix' in keys}
Path(args[2]).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='changed'}));print('Changed objects:',len(diff))
