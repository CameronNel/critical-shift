"""Read-only cold-open survey of neighbouring saved Blender geometry. Never saves."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
files={
 'reactor':Path('C:/Users/Camer/Games/critical-shift/worktrees/reactor-valorant/sections/reactor-room/blender/reactor_scene.blend'),
 'refinery':Path('C:/Users/Camer/Games/critical-shift/worktrees/refinery-compact/sections/refinery/blender/Refinery.blend'),
 'fuel':Path('C:/Users/Camer/.codex/worktrees/3598/critical-shift/sections/fuel-corridor/blender/Fuel_Corridor.blend')}
out={'method':'Fresh CPU process opens existing saved files read-only, evaluates named connection objects, records exact world bounds. No neighbour saved or edited.','neighbours':{}}
for key,p in files.items():
    if not p.exists():out['neighbours'][key]={'missing':str(p)};continue
    before=hashlib.sha256(p.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(p))
    dg=bpy.context.evaluated_depsgraph_get();rows=[]
    for o in bpy.context.scene.objects:
        n=o.name.lower()
        wanted=('cooling plant' in n or 'fuel corridor' in n) if key=='reactor' else any(s in n for s in (('dispatch','sill','bollard','portal') if key=='refinery' else ('s01','f01','f02','threshold','plant','sill')))
        if not wanted:continue
        row={'name':o.name,'type':o.type,'location':list(o.matrix_world.translation),'rotation_degrees':[math.degrees(x) for x in o.matrix_world.to_euler()]}
        if o.type in ('MESH','CURVE','FONT'):
            ev=o.evaluated_get(dg);m=ev.to_mesh()
            if m and len(m.vertices):
                pts=[ev.matrix_world@v.co for v in m.vertices]
                row['bounds']={'min':[min(v[i] for v in pts) for i in range(3)],'max':[max(v[i] for v in pts) for i in range(3)]}
                row['object_local_bounds']={'min':[min(v.co[i] for v in m.vertices) for i in range(3)],'max':[max(v.co[i] for v in m.vertices) for i in range(3)]}
            ev.to_mesh_clear()
        rows.append(row)
    after=hashlib.sha256(p.read_bytes()).hexdigest()
    out['neighbours'][key]={'path':str(p),'sha256_before':before,'sha256_after':after,'unchanged':before==after,'objects':rows}
dest=ROOT/'production/technical/neighbour-saved-measurements.json'
dest.write_text(json.dumps(out,indent=2))
print('NEIGHBOUR_SURVEY '+json.dumps({k:len(v.get('objects',[])) for k,v in out['neighbours'].items()}))
