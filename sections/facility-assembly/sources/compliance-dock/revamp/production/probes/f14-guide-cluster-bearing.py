"""Root actual-surface check of self-touching G1 clusters; no native writes."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[3];source=R/'module_overhaul_R1.blend'
expected='6e3ee923505d393c48aeb08bdf3e73ac32bd15e3c439487e64ce685cc519a135'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)==expected
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=s
bpy.context.view_layer.update()
o=s.objects['G1 guide tower east']
tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],
                         [list(f.vertices) for f in o.data.polygons],all_triangles=False)
checks=[]
for label,y,dy in [('front shoe rear',6.8025,1),('rear shoe front',7.1975,-1)]:
    p=Vector((3.02,y,1));d=Vector((0,dy,0));h=tree.ray_cast(p,d,.10)
    checks.append(dict(label=label,query=list(p),hit=list(h[0]) if h[0] else None,
                       actual_gap_m=h[3] if h[0] else None))
assert sha(source)==expected
out=Path(__file__).with_suffix('.json')
out.write_text(json.dumps(dict(source_sha256=expected,source_unchanged=True,
                              actual_mast_surface_queries=checks,
                              interpretation='Mutually touching shoe/fixing islands are not a rooted support path. Measured F14 gap is additional root finding; independent C7 scores remain unchanged.',
                              scene_mutated=False,native_written=False),indent=2)+'\n')
print('ACTUAL_GUIDE_MAST_GAPS',json.dumps(checks),flush=True)
