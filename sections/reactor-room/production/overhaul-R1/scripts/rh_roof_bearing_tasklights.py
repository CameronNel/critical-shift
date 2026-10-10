"""Mount restrained maintenance uplights beneath the twelve structural bearing heads."""
import bpy,json
from mathutils import Vector
import crk
import rh_support_registry as SUPPORT
KEY='rh_roof_bearing_tasklights'
OWNER='roof bearing maintenance lights'
HOUSING='RH roof bearing maintenance housings'
LENS='RH roof bearing maintenance lenses'
def apply(scene,objects,materials):
 if KEY in scene:return json.loads(scene[KEY])
 rows=[r for r in json.loads(scene[SUPPORT.KEY]) if r['owner']=='wall roof bearings' and r['name'].startswith('column head ')]
 assert len(rows)==12
 coll=objects['RH walls roof posts STEEL'].users_collection[0]
 steel=materials['RH roof girder Audi grey coating']
 practical=objects['RH hoist anchor tasklight lens'].data.materials[0]
 k=crk.Kit();records=[]
 for i,r in enumerate(sorted(rows,key=lambda r:r['name'])):
  x,y,z=[sum(p[a]for p in r['anchors'])/len(r['anchors']) for a in range(3)]
  # The post head plate underside lies 20mm below the registered packer interface.
  seat=z-.02
  k.bx(('body','METAL'),x+.075,x+.125,y-.04,y+.04,seat-.14,seat,.002)
  k.bx(('body','METAL'),x+.095,x+.385,y-.05,y+.05,seat-.165,seat-.14,.002)
  k.bx(('lens','EMIT'),x+.245,x+.370,y-.038,y+.038,seat-.14,seat-.138,.0004)
  SUPPORT.register(OWNER,'bearing uplight seat '+str(i),HOUSING,'RH walls roof posts STEEL',[(x+dx,y+dy,seat)for dx in (.08,.12)for dy in (-.03,.03)],(0,0,1),'suspension')
  lamp=bpy.data.lights.new('RH roof bearing maintenance LED '+str(i),'AREA');lamp.energy=2.0;lamp.color=(.96,.97,.96);lamp.shape='RECTANGLE';lamp.size=.12;lamp.size_y=.075;lamp.spread=1.7453292519943295
  light=bpy.data.objects.new(lamp.name,lamp);coll.objects.link(light);light.location=(x+.31,y,seat-.136)
  target=Vector((x+.14,y,z+.015));light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
  records.append({'light':light.name,'bearing_center':[x,y,z],'mount_seat_z':seat,'location':list(light.location),'target':list(target),'power_w':lamp.energy,'color':list(lamp.color)})
 built=k.build(coll,'RH roof bearing maintenance',{'METAL':steel,'EMIT':practical})
 for o in built:o.name=HOUSING if o.name.endswith(' METAL') else LENS
 assert {o.name for o in built}=={HOUSING,LENS},[o.name for o in built]
 report={'added_objects':[HOUSING,LENS]+[r['light']for r in records],'records':records,'fixture_count':12,'power_w_each':2.0,'total_power_w':24.0,'scope':'Twelve mounted bearing-head maintenance fixtures; existing scene objects, material graphs, retained lights, exposures, cameras and state drivers unchanged. Full technical and visual verification required.'}
 scene[KEY]=json.dumps(report,sort_keys=True);return json.loads(scene[KEY])
