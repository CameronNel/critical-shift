"""Mount a restrained maintenance LED over the positive rope-end anchors."""
import bpy,json
from mathutils import Vector
import crk
import rh_support_registry as SUPPORT
KEY='rh_hoist_aperture_tasklight'
def apply(scene,objects,materials):
    if KEY in scene:return json.loads(scene[KEY])
    body=objects['R2 crane trolley crane IRON'];frame=objects['RH hoist inspection aperture frame'];x=body.matrix_world.translation.x
    coll=frame.users_collection[0];steel=objects['RH roof crossings washers GALV'].data.materials[0]
    practical=next(m for m in objects['RH refine main hoist lamp diffuser PRACTICAL'].data.materials if m)
    kit=crk.Kit();kit.bx(('part','METAL'),x-.21,x+.21,4.894,4.918,16.164,16.182,.001)
    housing=kit.build(coll,'RH hoist anchor tasklight housing',{'METAL':steel})[0];housing.name='RH hoist anchor tasklight housing'
    kit=crk.Kit();kit.bx(('part','EMIT'),x-.194,x+.194,4.895,4.908,16.162,16.164,.0003)
    lens=kit.build(coll,'RH hoist anchor tasklight lens',{'EMIT':practical})[0];lens.name='RH hoist anchor tasklight lens'
    lamp=bpy.data.lights.new('RH hoist anchor maintenance LED','AREA');lamp.energy=1.2;lamp.color=(1,.94,.86);lamp.shape='RECTANGLE';lamp.size=.38;lamp.size_y=.010
    light=bpy.data.objects.new('RH hoist anchor maintenance LED',lamp);coll.objects.link(light)
    light.location=(x,4.901,16.161);direction=(Vector((x,4.780,16.10))-light.location).normalized();light.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    for o in (housing,lens,light):o.parent=body;o.matrix_parent_inverse=body.matrix_world.inverted()
    SUPPORT.register('refinement props','hoist tasklight rim seat',housing.name,frame.name,[(x+dx,4.916,16.164) for dx in (-.16,.16)])
    SUPPORT.register('refinement props','hoist tasklight lens seat',lens.name,housing.name,[(x+dx,4.903,16.164) for dx in (-.16,.16)],(0,0,1),'suspension')
    report={'added_objects':[housing.name,lens.name,light.name],'power_w':lamp.energy,'color':list(lamp.color),'aim':list(direction),'scope':'Mounted aperture-edge LED housing, retained practical lens material, and 1.2W narrowly local rectangular light; no changes to retained lights, cameras, rig, materials or geometry. Full technical and rendered acceptance required.'}
    scene[KEY]=json.dumps(report,sort_keys=True);return json.loads(scene[KEY])
