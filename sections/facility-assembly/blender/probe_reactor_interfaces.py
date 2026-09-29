"""Read-only exact triangle screen of SY services against source east annex."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[3];r=root/'sections/facility-assembly';out=root/'runtime/out/spawn-integration'
src=Path(bpy.data.filepath);before=hashlib.sha256(src.read_bytes()).hexdigest()
names=['Vestibule floor','Vestibule roof','Vestibule north closure','Vestibule south closure','Vestibule east return','Stair east enclosure','Stair west lower south','Stair west lower north','Stair west upper','Stair north enclosure','Stair south lower enclosure','Stair south upper east','Stair core roof','D01 open door','D02 open door']
with bpy.data.libraries.load(str(r/'sources/reactor-room/module.blend'),link=True) as (a,b):b.objects=list(names)
tmp=bpy.data.collections.new('TEMP_INTERFACE_PROBE');bpy.context.scene.collection.children.link(tmp)
for o in b.objects:tmp.objects.link(o)
bpy.context.view_layer.update()
pose=Matrix.Translation(Vector((14.2,46.5,0)))@Matrix.Rotation(math.pi,4,'Z')
def tree(o,m):return BVHTree.FromPolygons([m@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
targets=[(o.name,tree(o,pose@o.matrix_world)) for o in b.objects]
target_points=[pose@o.matrix_world@Vector(p) for o in b.objects for p in o.bound_box]
target_low=[min(p[i] for p in target_points) for i in range(3)]
target_high=[max(p[i] for p in target_points) for i in range(3)]
rows=[]
for o in bpy.data.collections['ART | Spawn and medical courtyard'].objects:
    if o.type!='MESH':continue
    pts=[o.matrix_world@Vector(p) for p in o.bound_box]
    if any(max(p[i] for p in pts)<target_low[i]-.1 or min(p[i] for p in pts)>target_high[i]+.1 for i in range(3)):continue
    t=tree(o,o.matrix_world);hits=[]
    for name,targ in targets:
        overlap=t.overlap(targ)
        if overlap:hits.append(dict(object=name,triangle_pairs=len(overlap)))
    rows.append(dict(name=o.name,intersections=hits))
assert hashlib.sha256(src.read_bytes()).hexdigest()==before
(out/'reactor-interfaces.json').write_text(json.dumps(dict(source_sha256=before,targets=names,objects=rows),indent=2));print('REACTOR_INTERFACE_HITS',[a for a in rows if a['intersections']],flush=True)
