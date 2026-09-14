import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'connections/access'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_walkthrough_A08_access.blend'),load_ui=False)
inst=bpy.data.objects['condenser-bay'];excluded={'D01 local blanking frame','D01 local blanking panel','D01 stub end wall'}
def clone(c):
 n=bpy.data.collections.new('A08_OPEN_'+c.name)
 for o in c.objects:
  if o.name not in excluded:n.objects.link(o)
 for ch in c.children:n.children.link(clone(ch))
 return n
assert excluded<={o.name for o in inst.instance_collection.all_objects}
inst.instance_collection=clone(inst.instance_collection)
p=bpy.data.objects['WALK_PROXY_condenser-bay'];bm=bmesh.new();bm.from_mesh(p.data);inv=inst.matrix_basis.inverted()@p.matrix_basis
vs={v for v in bm.verts if -1.47<(inv@v.co).x<1.47 and -2.58<(inv@v.co).y<-2.23 and -.02<(inv@v.co).z<2.72}
fs=[f for f in bm.faces if all(v in vs for v in f.verts)];count=len(fs);bmesh.ops.delete(bm,geom=fs,context='FACES');bm.to_mesh(p.data);bm.free()
# Reuse actual open portal return meshes, sized to the condenser service aperture.
ext=bpy.data.collections['11_ACCESS_ARCHITECTURE'];template=bpy.data.objects['Compliance open portal wall return']
for x in [-1.25,1.25]:
 o=template.copy();o.data=template.data.copy();ext.objects.link(o);o.name='Condenser open D01 return';o.location=inst.matrix_basis@Vector((x,-2.45,1.35));o.rotation_euler.z=inst.rotation_euler.z;o.dimensions=(.5,.22,2.7)
o=template.copy();o.data=template.data.copy();ext.objects.link(o);o.name='Condenser open D01 lintel';o.location=inst.matrix_basis@Vector((0,-2.45,2.55));o.rotation_euler.z=inst.rotation_euler.z;o.dimensions=(2,.22,.3)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_walkthrough_A08_access.blend'),compress=True)
for name in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE']:bpy.data.collections[name].hide_viewport=True
for name in ['01_LINKED_ROOMS','06_LINKED_EXTERIORS','09_FINISHED_HORIZONTAL_CONNECTIONS','CONNECTION_C01_RESCUE_COURTYARD']:
 c=bpy.data.collections.get(name)
 if c:c.hide_viewport=False
bpy.context.scene.name='FACILITY_A08_ACCESS_MASTER'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_master_A08_access.blend'),compress=True)
(O/'CONDENSER_OPEN.json').write_text(json.dumps({'removed_D01_caps':sorted(excluded),'display_faces_removed':count,'U02_untouched':True},indent=2));print('CONDENSER_ACCESS_OPEN',flush=True)
