"""Root read-only dimensional inspection; no geometry changes or native writes."""
import bpy, json, hashlib
from pathlib import Path

ROOM=Path(__file__).resolve().parents[3]
SOURCE=ROOM/'module_overhaul_R1.blend'
EXPECTED='22176ab474d914156cdf5a083571c19b04c6e6e11cfa50ab8ba681013bc124a6'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)==EXPECTED
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False)
scene=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL']
bpy.context.window.scene=scene
bpy.context.view_layer.update()
records=[]
for o in scene.objects:
    if o.type!='MESH' or not o.name.startswith(('G1 ', 'Transit drum', 'Transformer box', 'Main breaker', 'CD | Utility', 'P1 ', 'Entry portal', 'Room entry')):
        continue
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    records.append(dict(name=o.name,parent=o.parent.name if o.parent else None,
                        matrix_world=[list(row) for row in o.matrix_world],
                        bounds_min=[min(v[i] for v in vs) for i in range(3)],
                        bounds_max=[max(v[i] for v in vs) for i in range(3)],
                        materials=[m.name if m else None for m in o.data.materials],
                        vertices_world=[list(v) for v in vs],
                        polygons=[list(f.vertices) for f in o.data.polygons]))
assert sha(SOURCE)==EXPECTED
out=Path(__file__).with_suffix('.json')
out.write_text(json.dumps(dict(source_sha256=EXPECTED,source_unchanged=True,
                              scope='Read-only source dimensions; no modeling or acceptance',
                              objects=records),indent=2)+'\n')
print('ROOT_READONLY_DIMENSIONS',len(records),flush=True)
