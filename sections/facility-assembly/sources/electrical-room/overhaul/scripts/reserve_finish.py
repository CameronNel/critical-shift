"""Mounted low-voltage service strips reveal the reserve cell recesses."""
import bpy
from mathutils import Vector

def apply(k, m):
    before=set(bpy.data.objects)
    k.COLL=bpy.data.collections[k.PREFIX+'Reserve and transfer refinements']
    diffuser=m['ceramic'].copy();diffuser.name=k.PREFIX+'Reserve service LED diffuser'
    bs=diffuser.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Emission Color'].default_value=(1,.89,.71,1)
    bs.inputs['Emission Strength'].default_value=1.8
    contacts=[];lights=[]
    for i,y in enumerate([12.18,13.20,14.22]):
        k.ASSEMBLY=bpy.data.objects[k.PREFIX+'Reserve service rack '+str(i+1)]
        # Folded vertical jamb carries the low-voltage raceway and each end shoe.
        k.box('Reserve lighting raceway',(7.447,y+.416,1.035),(.024,.019,1.51),m['slate'],.003)
        k.box('Reserve lighting raceway returned lid',(7.433,y+.416,1.035),(.006,.021,1.51),m['steel'],.001)
        k.box('Reserve lighting junction cover',(7.426,y+.416,1.82),(.022,.032,.065),m['replacement'],.004)
        for z in [.834,1.384,1.843]:
            k.box('Reserve service strip extruded housing',(7.458,y,z),(.046,.786,.024),m['zinc'],.003)
            k.box('Reserve service strip recessed diffuser',(7.435,y,z-.004),(.007,.714,.012),diffuser,.002)
            # Front return shades the lens from the aisle while leaving a downlight slot.
            k.box('Reserve service strip glare return',(7.428,y,z+.008),(.009,.738,.008),m['slate'],.001)
            for side in [-1,1]:
                yy=y+side*.401
                shoe=k.box('Reserve service strip retained end shoe',(7.458,yy,z),(.052,.024,.032),m['rubber'],.004)
                k.bolt('Reserve strip fixing',(7.430,yy,z),(-1,0,0),m['zinc'],.004)
                target='Reserve folded vertical'+('' if 2*i+(0 if side==1 else 1)==0 else '.'+str(2*i+(0 if side==1 else 1)).zfill(3))
                contacts.append({'fixture':shoe.name,'target':target,'point':[7.458,y+side*.4125,z],'direction':[0,side,0]})
            k.tube('Reserve strip retained supply lead',[(7.462,y+.365,z),(7.448,y+.385,z-.006),(7.446,y+.416,z-.014)],.003,m['rubber'])
            lamp=k.lamp('Reserve compartment service light',(7.417,y,z-.014),(7.49,y,z-.25),3.5,(1,.89,.71),.60)
            lamp.data.shape='RECTANGLE';lamp.data.size=.60;lamp.data.size_y=.018
            lights.append(lamp.name)
    bpy.context.view_layer.update()
    for c in contacts:
        target=bpy.data.objects[c['target']];inv=target.matrix_world.inverted()
        direction=Vector(c['direction']);p=Vector(c['point'])-direction*.002
        hit,loc,*_=target.ray_cast(inv@p,(inv.to_3x3()@direction).normalized(),distance=.005)
        assert hit,c
        gap=(target.matrix_world@loc-Vector(c['point'])).length
        assert gap<.00001,(c,gap)
        c['support_gap_m']=gap
    bpy.context.scene['electrical_reserve_service_lighting_revision']=1
    return {'new_supported_object_names':sorted(o.name for o in set(bpy.data.objects)-before),
            'new_material_names':[diffuser.name],'new_service_lights':lights,'watts_per_light':3.5,
            'measured_jamb_contacts':contacts,'existing_rack_support_roots_reused':3,
            'existing_objects_and_material_definitions_unchanged':True}
