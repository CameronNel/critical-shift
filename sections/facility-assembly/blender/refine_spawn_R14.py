"""R13 -> R14: simplify only upper exterior rock, protecting lower interface and boundaries."""
import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'production/spawn-exterior-review'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_spawn_concept02_R13.blend'),load_ui=False)
records=[]
for name in ['S01 exterior quarried front material override','S01 exterior upper mountain material override']:
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table();protected=[v.index for v in bm.verts if v.co.z<5 or v.is_boundary];bm.free()
 group=ob.vertex_groups.new(name='Protected lower interface and boundary');group.add(protected,1,'REPLACE')
 mod=ob.modifiers.new('Upper exterior rock planes','DECIMATE');mod.decimate_type='COLLAPSE';mod.ratio=.24;mod.use_collapse_triangulate=True;mod.vertex_group=group.name;mod.vertex_group_factor=1000;mod.invert_vertex_group=True
 records.append({'object':name,'protected_vertices':len(protected),'source_faces':len(ob.data.polygons),'ratio':.24,'scope':'Derived exterior surface only. Boundary and all vertices below local Z=5m protected. Source library geometry untouched.'})
s=bpy.context.scene;s.view_settings.exposure=-.25;s.name='FACILITY_SPAWN_CONCEPT02_R14';dest=R/'blender/facility_spawn_concept02_R14.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
b=json.loads((O/'BUILD_R13.json').read_text());b.update(revision='R14',file=str(dest),exterior_rock_simplification=records,exposure=-.25);(O/'BUILD_R14.json').write_text(json.dumps(b,indent=2));print('R14_SAVED',records,flush=True)
