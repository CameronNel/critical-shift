"""Bounded f08 -> f09 finish repair, using the canonical construction recipe.

Run only after f08 has saved and every source consumer has released it. This
does not rebuild meshes or act as a competing room builder. Fresh full builds
already include the same active-paint repair in full_repairs.py.
"""
import array, ast, bpy, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PROD=ROOT/'revamp/production'
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
state=json.loads((PROD/'build-state.json').read_text())
source=ROOT/'module_overhaul_R1.blend'
if state['revision']!='f08' or sha(source)!=state['source_sha256']:
    raise RuntimeError('Expected exact saved f08; refuse an unknown or already repaired native')
before_source=sha(source)
protected=json.loads((PROD/'protected-inputs.json').read_text())
for rel,expected in protected.items():
    if sha(ROOT.parents[3]/rel)!=expected:raise RuntimeError('Changed protected input '+rel)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=S

def geometry_digest():
    h=hashlib.sha256()
    for o in sorted(S.objects,key=lambda x:x.name):
        h.update(json.dumps([o.name,o.type,o.parent.name if o.parent else None,[list(r) for r in o.matrix_world]],sort_keys=True).encode())
        if o.type=='MESH':
            for collection,field,arity,kind in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'loop_start',1,'i'),(o.data.polygons,'loop_total',1,'i')]:
                values=array.array(kind,[0])*(len(collection)*arity);collection.foreach_get(field,values);h.update(values.tobytes())
            for layer in o.data.uv_layers:
                h.update(layer.name.encode());values=array.array('f',[0])*(len(layer.data)*2);layer.data.foreach_get('uv',values);h.update(values.tobytes())
        elif o.type=='FONT':
            h.update(json.dumps([o.data.body,o.data.size,o.data.extrude,o.data.bevel_depth,o.data.resolution_u]).encode())
    return h.hexdigest()

before_geometry=geometry_digest()
tree=ast.parse((ROOT/'full_repairs.py').read_text())
defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'material_patch','repair_working_surfaces'}]
exec(compile(ast.Module(body=defs,type_ignores=[]),str(ROOT/'full_repairs.py'),'exec'),globals())
changed=[]
for name in ['CD | coral','CD | coral | text object metres']:
    material=bpy.data.materials[name]
    MATERIALS={'coral':material}
    repair_working_surfaces(crate_only=True)
    changed.append(name)
after_geometry=geometry_digest()
if before_geometry!=after_geometry:raise RuntimeError('Bounded finish repair changed geometry, UVs, original poses or object membership')
recipes={name:sha(ROOT/name) for name in ['overhaul_dock.py','full_detail.py','full_repairs.py','render_dock.py','repair_contact_wear.py']}
lineage={'base_revision':'f08','base_sha256':before_source,'geometry_digest_before':before_geometry,'geometry_digest_after':after_geometry,'changed_material_graphs':changed,'recipe':'repair_contact_wear.py calls full_repairs.repair_working_surfaces(crate_only=True)'}
S['revision']='f09';S['recipe_sha256']=json.dumps(recipes,sort_keys=True);S['finish_repair_lineage']=json.dumps(lineage,sort_keys=True)
bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
state.update(revision='f09',source_sha256=sha(source),recipe_sha256=recipes,finish_repair_lineage=lineage)
(PROD/'build-state.json').write_text(json.dumps(state,indent=2)+'\n')
(PROD/'finish-repair-f09.json').write_text(json.dumps(lineage,indent=2)+'\n')
for rel,expected in protected.items():
    if sha(ROOT.parents[3]/rel)!=expected:raise RuntimeError('Changed protected input '+rel)
print('DOCK_FINISH_REPAIR_SAVED',state['source_sha256'],'GEOMETRY_UNCHANGED',before_geometry,flush=True)
