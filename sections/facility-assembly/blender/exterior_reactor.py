"""Skins follow original faceted panel geometry; no reconstructed room envelope."""
import re
from mathutils import Matrix
with bpy.data.libraries.load(str(source),link=True) as (rs,rd):rd.collections=['MODULE_'+SID]
# Linked collection objects require evaluation before reading their world matrices.
scene.collection.children.link(rd.collections[0]);bpy.context.view_layer.update()
for original in rd.collections[0].all_objects:
 if original.type!='MESH' or not re.match(r'^Shell [1-8] field(?:\.\d+)?$',original.name):continue
 coords=[v.co for v in original.data.vertices]
 lo=[min(v[i] for v in coords) for i in range(3)];hi=[max(v[i] for v in coords) for i in range(3)]
 # The source panel's local +Y is the exterior, including recessed fields.
 center=Vector(((lo[0]+hi[0])/2,hi[1]+.014,(lo[2]+hi[2])/2))
 skin=box('Reactor exterior '+original.name,center,(hi[0]-lo[0]-.004,.028,hi[2]-lo[2]-.004),accent if center.z>13.4 else cream,.004)
 skin.matrix_world=original.matrix_world@Matrix.Translation(center)
 skin['source_panel']=original.name
 if hi[2]>15.95:
  cap=box('Reactor individual panel weather cap',((lo[0]+hi[0])/2,hi[1]+.005,hi[2]-.04),(hi[0]-lo[0],.13,.08),steel,.004)
  cap.matrix_world=original.matrix_world@Matrix.Translation(Vector(((lo[0]+hi[0])/2,hi[1]+.005,hi[2]-.04)))
scene.collection.children.unlink(rd.collections[0])
# Large identification remains on the unbroken south facet, clear of every portal.
text('Reactor external identification','REACTOR',(0,-11.111,7.8),1.0)
ob=bpy.data.objects['Reactor external identification'];ob.rotation_euler.z=0;ob.data.materials.clear();ob.data.materials.append(steel)
camera_specs=[('FRONT',(2,-46,10),(2,0,7)),('OBLIQUE',(-36,-40,25),(0,0,7)),('REVERSE',(38,40,25),(0,0,7)),('DETAIL',(-3,-19,8),(0,-10.8,8))]
