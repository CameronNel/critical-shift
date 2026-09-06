"""Fifth comparison: oblique presentation, storage construction and reflected light."""
import bpy
from math import pi,cos,sin
from mathutils import Quaternion
import grounded_kit as k
import valorant_polish as v

def run():
    assert not bpy.context.scene.get('valorant_detail_pass'), 'Detail pass already applied'
    k.M={m.name:m for m in bpy.data.materials};k.STAGE=3
    for name,angle in [('BRIEFING',.085),('HALL',-.055),('LOCKER',-.082)]:
        cam=bpy.data.objects['REFERENCE_'+name];cam.rotation_euler=(Quaternion((0,0,1),angle)@cam.rotation_euler.to_quaternion()).to_euler()
    plant=bpy.data.objects['V_BRIEF_corner_ficus'];plant.scale.x*=.86;plant.scale.y*=.86
    poster=bpy.data.objects['V_HALL_culture_poster'];poster.scale=(.94,1,.80);poster.location.z=1.75
    for name in ['V_HALL_first_aid','V_HALL_extinguisher','V_EXT_location']:bpy.data.objects[name].location.y=7.10
    bpy.data.objects['V_HALL_extinguisher'].scale=(1.10,1.10,1.10)
    # Construct lids, folded edges, catches and inventory faces in both travel directions.
    for name,w,d,h,mat in [('V_CART_lower',.44,.58,.31,'V_graphite'),('V_CART_upper',.44,.48,.32,'V_cardboard')]:
        root=bpy.data.objects[name];b=k.start()
        k.box(name+'_lid',(0,0,h-.018),(w+.016,d+.016,.040),mat,.005)
        for side in [-1,1]:
            y=side*(d/2+.012)
            k.box(name+'_rim',(0,y,h-.057),(w+.012,.012,.012),'V_brushed',.002)
            for x in [-w*.45,w*.45]:k.box(name+'_edge_guard',(x,y,h/2),(.024,.012,h-.06),'V_graphite',.003)
            k.box(name+'_latch',(w*.24,y+side*.008,h-.075),(.045,.016,.055),'V_brushed',.003)
        k.box(name+'_near_inventory',(-.06,d/2+.013,h*.52),(.20,.003,.115),'V_paper',.001)
        k.label(name+'_near_inventory_type','FILTER KITS' if name.endswith('lower') else 'CLEAN STOCK',(.023,d/2+.015,h*.52+.026),.017,'ink',rot=(pi/2,0,pi))
        for j in range(4):k.box(name+'_near_inventory_rule',(-.06,d/2+.015,h*.52+.005-j*.010),(.14,.001,.0018),'ink',0)
        k.tube(name+'_pull',[(-.09,d/2+.018,h*.36),(-.09,d/2+.045,h*.36),(.04,d/2+.045,h*.36),(.04,d/2+.018,h*.36)],.007,'V_graphite')
        for ob in set(bpy.data.objects)-b:ob.parent=root
    # Mechanical rather than a featureless red bottle: gauge, pin and foot ring.
    b=k.start()
    k.rod('V_EXT_gauge_rim',(-.025,-.168,.320),(-.025,-.201,.320),.028,'V_brushed',32)
    k.rod('V_EXT_gauge_face',(-.025,-.202,.320),(-.025,-.204,.320),.023,'V_paper',32)
    k.tube('V_EXT_gauge_needle',[(-.025,-.205,.320),(-.013,-.205,.330)],.0018,'V_rustred')
    k.tube('V_EXT_safety_pin',[(.053+.016*cos(i*pi/12),-.173,.328+.016*sin(i*pi/12)) for i in range(25)],.002,'V_brushed')
    k.lathe('V_EXT_foot_ring',[(.115,-.25),(.124,-.25),(.126,-.235),(.126,-.215),(.121,-.210)],'V_graphite',48).location.y=-.14
    for ob in set(bpy.data.objects)-b:ob.parent=bpy.data.objects['V_HALL_extinguisher']
    for name in ['V_EXT_location_type','V_AID_title','V_AID_subtitle']:bpy.data.objects[name].data.offset=.0004
    root=bpy.data.objects['V_EXT_location'];b=k.start()
    k.tube('V_EXT_pictogram',[(0,-.005,-.055),(-.031,-.005,-.055),(-.031,-.005,.025),(0,-.005,.042),(.031,-.005,.025),(.031,-.005,-.055),(0,-.005,-.055)],.003,'paper')
    k.tube('V_EXT_pictogram_hose',[(.005,-.005,.040),(.030,-.005,.064),(.045,-.005,.032)],.003,'paper')
    for ob in set(bpy.data.objects)-b:ob.parent=root
    bpy.data.objects['V_EXT_location_type'].data.body=''
    for ob in bpy.data.objects:
        if ob.name.startswith('V_BRIEF_plan_line') and ob.type=='CURVE':ob.data.materials.clear();ob.data.materials.append(k.M['dry_marker'])
    # All eight matching door backs receive the same real folded return channels.
    for i in range(1,5):
        for side,suffix in [(-1,'L'),(1,'R')]:
            root=bpy.data.objects['BELONG_%02d_door_%s'%(i,suffix)];cx=-side*.25;b=k.start()
            for z in [.23,1.05,2.09]:k.box('V_LOCKER_inner_channel',(cx,.021,z),(.45,.017,.035),'V_locker_steel',.004)
            for x in [cx-.233,cx+.233]:k.box('V_LOCKER_inner_return',(x,.019,1.145),(.014,.018,2.06),'V_locker_steel',.002)
            for ob in set(bpy.data.objects)-b:ob.parent=root
    for name,power in [('BRIEFING',60),('HALL',55),('LOCKER',106)]:
        d=bpy.data.objects['EEVEE_floor_bounce_'+name].data;d.energy=power;d.color=(.93,.85,.73)
    for name,power in [('V_LIGHT_BRIEF_wall',55),('V_LIGHT_BRIEF_ceiling',34),('V_LIGHT_HALL_staff',63),('V_LIGHT_LOCKER_front_fill',45),('V_LIGHT_LOCKER_pod_fill',32)]:bpy.data.objects[name].data.energy=power
    new=v.surf('V_reference_charcoal',(.09,.105,.10),.79,.28,.15,.0006)
    for ob in bpy.data.objects:
        if ob.type=='MESH' and ob.name.startswith(('V_REAR_solid_leaf','V_BRIEF_crown','V_AID_wall_mount')):
            for slot in ob.material_slots:slot.material=new
    for i in range(6):
        m=k.M['V_tile%d'%i];n=m.node_tree.nodes;l=m.node_tree.links;p=n['Principled BSDF']
        mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.84,.85,.84,1)
        l.new(p.inputs['Base Color'].links[0].from_socket,mix.inputs[1]);l.new(mix.outputs[0],p.inputs['Base Color'])
    bpy.context.scene['valorant_detail_pass']=5
