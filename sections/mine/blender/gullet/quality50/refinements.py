"""Corrections identified in actual first, second and fifty-camera renders."""
import bpy,math,random
import geometry
from geometry import curve,planar_patch,box,cylinder
from materials import basic,rgba,noise,ramp
from geology_repairs import fractured_shape,settle,tree

def refine(scene,m):
    result={'cart_floor_joints':0,'cart_load_fragments':0,'cloth_wrinkled':False}
    for ci,key in enumerate(['CSM_Dispatch_cart','CSM_Loaded_haulage_cart']):
        root=scene.objects[key]
        for o in list(root.children):
            if 'Cart_floor_plank' in o.name:
                for v in o.data.vertices:v.co.x*=1.54/1.48
                o.data.update();result['cart_floor_joints']+=1
            if 'Cart_residual_ore' in o.name:bpy.data.objects.remove(o,do_unlink=True)
        for i in range(5 if ci else 3):
            o=fractured_shape('Cart_rock_residue',(.15+.018*(i%3),.21,.11),m['rock'],1813+i+ci*20)
            o.parent=root;o.location=([-.30,0,.30][i%3],-.42+(i//3)*.37,.599-min(v.co.z for v in o.data.vertices));o.rotation_euler.z=i*.61;o['csm_ore_chunk']=True
            result['cart_load_fragments']+=1
    duct=scene.objects.get('CSM_Ventilation_fabric_trunk')
    if duct:
        duct.data=duct.data.copy()
        for v in duct.data.vertices:
            x,y,z=v.co;cx=1.65+math.sin(y*.12)*.045;cz=-.025*max(y,0)+3.42-.03*math.sin(y*.5)
            dx,dz=x-cx,z-cz;r=math.hypot(dx,dz)
            if r<.1:continue
            phase=abs(((y-1+.4)%.8)-.4);fade=min(1,phase/.09)
            change=fade*(.009*math.sin(y*10.7+math.atan2(dz,dx)*3)+.005*math.sin(y*19.3))
            v.co.x=cx+dx*(r+change)/r;v.co.z=cz+dz*(r+change)/r
        duct.data.update();duct['q50_wrinkled_canvas']=True;result['cloth_wrinkled']=True
        line=[]
        for j in range(177):
            y=.8+j*.20;cx=1.65+math.sin(y*.12)*.045;cz=-.025*y+3.42-.03*math.sin(y*.5)
            line.append((cx-.190,y,cz-.218))
        curve('Canvas_longitudinal_seam',[line],.0028,m['dirt'])
    z=-.025*21.55
    for side in [-1,1]:
        for j in range(9):
            x=9.45+side*1.047;y=20.25+j*.31
            planar_patch('Sump_waterline_crust',(x,y,z-.226),(0,1,0),(0,0,1),(.19,.035),m['mineral'],seed=662+j)
    concrete=scene.objects['CSM_Apron_concrete_slab'].material_slots[0].material
    for side in [-1,1]:
        box('Facility_rear_retaining_wall',(side*5.135,-14.10,2.30),(5.02,.40,4.60),concrete,bevel=.012)
    box('Facility_rear_lintel',(0,-14.10,4.28),(5.25,.40,.64),concrete,bevel=.009)
    sign=scene.objects.get('CSM_Return_route')
    if sign:sign.location.y=-13.78;sign.location.z=3.58;sign.rotation_euler.z=math.pi
    result['facility_connection_framed']=True
    removed=[]
    for o in list(scene.objects):
        if o.get('csm_component')=='traversal_blocker':removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
        elif o.get('q50_fractured_block'):o['csm_collision_type']='convex_hull';o['q50_rubble_collision_follows_visible_mesh']=True
    result['removed_oversized_collision_boxes']=removed
    floor=scene.objects['CSM_Excavated_floor'];placed=[]
    for o in sorted([o for o in scene.objects if o.get('q50_material')=='rotted wood'],key=lambda o:o.name):
        settle(o,tree([floor]+placed));placed.append(o)
    result['decay_boards_resettled']=len(placed)
    for o in list(scene.objects):
        if o.name.startswith('Q50_Sump_floating_scum'):bpy.data.objects.remove(o,do_unlink=True)
    silt,bs=basic('water_edge_silt','34402D',.98);bs.inputs['Alpha'].default_value=.42;rng=random.Random(1487)
    for i in range(15):
        y=20.27+i*.182+rng.uniform(-.075,.065)
        planar_patch('Irregular_water_edge_silt',(8.48+rng.uniform(-.02,.06),y,z-.234),(1,0,0),(0,1,0),(rng.uniform(.02,.06),rng.uniform(.045,.16)),silt,seed=422+i)
    stain=m['stain'];n=stain.node_tree.nodes;l=stain.node_tree.links
    bs=next(a for a in n if a.type=='BSDF_PRINCIPLED');co=n.new('ShaderNodeTexCoord');v=noise(n,l,co.outputs['Object'],12,3)
    alpha=ramp(n,l,v,[(.25,(.045,.045,.045,1)),(.68,(.48,.48,.48,1))]);l.new(alpha,bs.inputs['Alpha'])
    result['water_edge_stamps_replaced']=True;result['runoff_softened_to_staining']=True
    lens,bs=basic('gate_bulkhead_lens','CDA875',.86)
    bs.inputs['Emission Color'].default_value=rgba('FFD49B');bs.inputs['Emission Strength'].default_value=1.5
    for side in [-1,1]:
        box('Inner_gate_bulkhead_back',(side*2.911,1.3,2.68),(.058,.25,.41),m['iron'],bevel=.008)
        box('Inner_gate_bulkhead_glass',(side*2.868,1.3,2.68),(.024,.18,.32),lens,bevel=.015)
        for zz in [2.57,2.68,2.79]:cylinder('Inner_gate_lamp_guard',(side*2.849,1.2,zz),(side*2.849,1.4,zz),.004,m['iron'])
        d=bpy.data.lights.new('Q50_Inner_gate_bulkhead','POINT');d.energy=65;d.color=(1.,.62,.31);d.shadow_soft_size=.20
        o=bpy.data.objects.new('Q50_Inner_gate_bulkhead',d);geometry.COLLECTION.objects.link(o);o.location=(side*2.72,1.3,2.68)
    result['inner_gate_practicals']=2
    return result
