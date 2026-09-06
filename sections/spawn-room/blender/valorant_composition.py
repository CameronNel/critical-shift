"""Sixth comparison: physically complete locker sides and reference dressing placement."""
import bpy
from math import pi,sin,cos
from mathutils import Quaternion
import grounded_kit as k
import grounded_room as room
import inhabit_spawn as life
import revise_spawn as rev
import valorant_polish as v

def run():
    assert not bpy.context.scene.get('valorant_composition_pass')
    k.M={m.name:m for m in bpy.data.materials};k.STAGE=3
    cam=bpy.data.objects['REFERENCE_BRIEFING'];cam.rotation_euler=(Quaternion((0,0,1),-.050)@cam.rotation_euler.to_quaternion()).to_euler();cam.data.sensor_width=60
    bpy.data.objects['V_HALL_culture_poster'].location.z=1.69
    # Position useful objects in the open bay beside the rear lockers.
    plant=bpy.data.objects['V_LOCKER_corner_ficus'];plant.location=(2.35,5.85,.006);plant.scale=(.90,.90,1.04)
    for name in ['V_LOCKER_pegboard','V_LOCKER_peg_shelf','V_LOCKER_laundry_cart']:bpy.data.objects[name].location.x=5.72
    # Exterior metal sidework repeats on every identical cabinet.
    for i in range(1,5):
        root=bpy.data.objects['PPE_%02d'%i]
        for side in [-1,1]:
            b=k.start()
            for y in [-.276,.276]:k.box('V_PPE_side_fold',(side*.534,y,1.145),(.014,.025,2.14),'V_locker_steel',.002)
            for z in [.09,2.205]:k.box('V_PPE_side_fold',(side*.534,0,z),(.014,.56,.025),'V_locker_steel',.002)
            for j in range(5):
                z=1.84+j*.045
                k.box('V_PPE_side_vent_shadow',(side*.536,0,z),(.005,.34,.018),'darksteel',.002)
                slat=k.box('V_PPE_side_vent_fold',(side*.546,0,z+.012),(.018,.354,.014),'V_locker_steel',.003);slat.rotation_euler.y=side*.22
            for ob in set(bpy.data.objects)-b:ob.parent=root
    # A real mounted hook carries the foreground towel; its cotton has a woven stripe.
    h=life.wall_hook('V_PPE_side_towel_hook',(-.528,0,1.64),-pi/2,'PPE_04_folded_side');h.parent=bpy.data.objects['PPE_04']
    towel=life.hanging_towel('V_PPE_hung_towel',(0,-.043,.026),'cotton_grey',width=.30,length=.68);towel.parent=h
    mesh=bpy.data.objects['V_PPE_hung_towel_cloth'].data;mesh.materials.append(k.M['cotton_cream'])
    for p in mesh.polygons:
        if 21<=p.index//20<=23:p.material_index=1
    # Cloth lies on the bench and rolls over the front edge with an uneven soft hem.
    rev.remove_prefix('V_LOCKER_bench_towel_0','V_LOCKER_bench_towel_1')
    b=k.start();vs=[];nx=25;ny=41
    for j in range(ny):
        t=j/(ny-1)
        if t<.4:y=.14-.27*t/.4;z=.003
        elif t<.58:
            a=(t-.4)/.18*pi/2;y=-.13-.035*sin(a);z=.003-.035*(1-cos(a))
        else:y=-.165-.008*sin((t-.58)*10);z=-.032-(t-.58)/.42*.24
        for i in range(nx):
            x=(i/(nx-1)-.5)*.40
            zz=z+.0025*cos(x*61)*(1 if t<.5 else .2)
            yy=y-(.010*cos(x*55)+.004*sin(x*22))*max(0,(t-.4)/.6)
            vs.append((x,yy,zz))
    ob=k.mesh('V_LOCKER_draped_cotton',vs,[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(ny-1) for i in range(nx-1)],'cotton_cream',True)
    ob.data.materials.append(k.M['cotton_grey'])
    for p in ob.data.polygons:
        if 33<=p.index//(nx-1)<=35:p.material_index=1
    sol=ob.modifiers.new('Woven cotton edge','SOLIDIFY');sol.thickness=.002
    for edge in [-.2,.2]:k.tube('V_LOCKER_towel_hem',[(edge,vs[j*nx][1],vs[j*nx][2]) for j in range(ny)],.0015,'cotton_cream')
    root=k.group('V_LOCKER_draped_towel',b,(3.60,2.85,.454));life.supported(root,'LOCKER_changing_bench_01_laminate_slat.001',[(0,.005,.0055)])
    # Recover the metal's actual teal paint, while retaining its low-sheen finish.
    m=k.M['V_locker_steel'];n=m.node_tree.nodes;l=m.node_tree.links;p=n['Principled BSDF']
    tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(1.55,1.55,1.52,1)
    l.new(p.inputs['Base Color'].links[0].from_socket,tint.inputs[1]);l.new(tint.outputs[0],p.inputs['Base Color'])
    metal=v.surf('V_pod_satin_metal',(.12,.155,.15),.58,.72,.12,.00045)
    for ob in bpy.data.objects['INTEGRITY_POD'].children_recursive:
        if ob.type=='MESH':
            for slot in ob.material_slots:
                if slot.material and slot.material.name=='pressure_metal':slot.material=metal
    room.cam('DETAIL_FourLockers',(6.12,4,1.77),(3.6,4,1.45),21).data.sensor_width=60
    bpy.context.scene['valorant_composition_pass']=6
