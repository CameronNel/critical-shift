"""Fast continuous exterior ground, preserving lower-level room footprints."""
import bpy,json
from pathlib import Path
ROOT=Path(r'C:/Users/Camer/Games/critical-shift/worktrees/facility-assembly-astra/sections/facility-assembly')
name='08_WHOLE_MAP_FLOOR'
assert name not in bpy.data.collections,'Floor already exists'
col=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(col)
# Footprints containing below-grade geometry retain their own floors and openings.
holes=[(-101,-10.49,-58,0),(-4.51,28.7,32,59.5),(40.54,66.3,36.25,51.02),(45.74,57.98,35.02,47)]
xs=sorted(set([-111,83]+[v for h in holes for v in h[:2]]));ys=sorted(set([-68,87]+[v for h in holes for v in h[2:]]))
verts=[];faces=[];idx={}
def vi(p):
 if p not in idx:idx[p]=len(verts);verts.append(p)
 return idx[p]
for x1,x2 in zip(xs,xs[1:]):
 for y1,y2 in zip(ys,ys[1:]):
  x=(x1+x2)/2;y=(y1+y2)/2
  if any(a<x<b and c<y<d for a,b,c,d in holes):continue
  faces.append(tuple(vi(p) for p in [(x1,y1,-.065),(x2,y1,-.065),(x2,y2,-.065),(x1,y2,-.065)]))
mesh=bpy.data.meshes.new('Whole map concrete ground mesh');mesh.from_pydata(verts,[],faces);mesh.update()
o=bpy.data.objects.new('Whole map continuous concrete floor',mesh);col.objects.link(o)
m=bpy.data.materials.new('Map ground warm concrete');m.diffuse_color=(.29,.28,.245,1);m.roughness=.88;mesh.materials.append(m)
o['scope']='Continuous exterior floor. Existing below-grade rooms and mine retain their own floors.'
o['bounds_m']=[-111,83,-68,87]
bpy.context.preferences.inputs.walk_navigation.use_gravity=False
bpy.data.libraries.write(str(ROOT/'blender/whole_map_floor.blend'),{col},path_remap='RELATIVE',compress=True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
report={'bounds_m':[-111,83,-68,87],'size_m':[194,155],'z_m':-.065,'mesh_objects':1,'faces':len(mesh.polygons),'lower_room_exclusions':holes,'walkthrough_saved':bpy.data.filepath,'gravity':False}
(ROOT/'production/WHOLE_MAP_FLOOR.json').write_text(json.dumps(report,indent=2));print(report)
