"""Raycast-mount gate lights and retain the original gate motion envelope."""
import bpy,json
from mathutils import Vector
import geometry
from geometry import box,cylinder,curve

def repair_gate_practicals(scene,m):
    collar=scene.objects['CSM_Shotcrete_portal_collar'];records=[]
    for o in list(scene.objects):
        if o.name.startswith('Q50_Inner_gate_bulkhead') or o.name.startswith('Q50_Inner_gate_lamp_guard'):bpy.data.objects.remove(o,do_unlink=True)
    lens=bpy.data.materials['Q50_gate_bulkhead_lens']
    for side in [-1,1]:
        start=Vector((0,1.3,2.68));direction=Vector((side,0,0));inv=collar.matrix_world.inverted()
        hit=collar.ray_cast(inv@start,(inv.to_3x3()@direction).normalized())
        if not hit[0]:raise RuntimeError('Cannot find the real portal-collar surface')
        surface=collar.matrix_world@hit[1];normal=(collar.matrix_world.to_3x3().inverted().transposed()@hit[2]).normalized()
        if normal.dot(start-surface)<0:normal=-normal
        root=bpy.data.objects.new('Q50_Surface_mounted_gate_lamp',None);geometry.COLLECTION.objects.link(root);root.location=surface;root.rotation_euler=normal.to_track_quat('Z','Y').to_euler()
        box('Gate_bulkhead_mount',(0,0,.034),(.26,.42,.064),m['iron'],root,bevel=.012)
        box('Gate_bulkhead_lens',(0,0,.080),(.19,.33,.026),lens,root,bevel=.010)
        for y in [-.115,0,.115]:cylinder('Gate_bulkhead_cage',(-.12,y,.105),(.12,y,.105),.004,m['iron'],root)
        light=bpy.data.lights.new('Q50_Gate_inner_practical','POINT');light.energy=85;light.color=(1.,.65,.38);light.shadow_soft_size=.20
        obj=bpy.data.objects.new('Q50_Gate_inner_practical',light);geometry.COLLECTION.objects.link(obj);obj.location=surface+normal*.25
        records.append({'surface':list(surface),'air_normal':list(normal),'light_position':list(obj.location),'power_w':85})
    for key in ['CSM_Blast_leaf_L','CSM_Blast_leaf_R']:
        root=scene.objects[key]
        for child in root.children:
            if child.type=='MESH' and 'Leaf_solid_core' in child.name:
                child.data=child.data.copy()
                for vertex in child.data.vertices:
                    if vertex.co.y>0:vertex.co.y*=.60
                child.data.update()
        for x in [-.98,.98]:box('Gate_rear_vertical_rib',(x,.133,2.38),(.09,.060,3.90),m['iron'],root,bevel=.006)
        for z in [.63,2.38,4.12]:box('Gate_rear_cross_rib',(0,.133,z),(1.87,.060,.09),m['iron'],root,bevel=.005)
        curve('Gate_rear_manual_grip',[[(-.19,.105,1.34),(-.19,.15,1.34),(.19,.15,1.34),(.19,.105,1.34)]],.012,m['iron'],root)
    for o in scene.objects:
        if o.type=='MESH' and o.name.startswith('CSM_Pocket_guard_'):
            center=sum((o.matrix_world@v.co).x for v in o.data.vertices)/len(o.data.vertices)
            transform=o.matrix_world.copy();transform.translation.x+=(.22 if center>0 else -.22);o.matrix_world=transform
    bpy.context.view_layer.update()
    return {'reason':'The closed-gate view exposed lamps inside the collar. New lamps use measured surface attachment. Rear detailing stays within the original leaf envelope; pocket guards are moved clear.','surface_mounts':records,'pocket_guard_outward_shift_m':.22}
