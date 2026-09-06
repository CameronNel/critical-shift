"""Eighth comparison: measured light balance, foliage surfaces and display legibility."""
import bpy, random
from math import pi
from mathutils import Vector, Quaternion
import grounded_kit as k
import worn_surfaces as wear

def tint(material, value):
    n=material.node_tree.nodes; l=material.node_tree.links; p=n['Principled BSDF']
    mix=n.new('ShaderNodeMixRGB');mix.name='Reference palette balance';mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1
    mix.inputs[2].default_value=(*value,1)
    if p.inputs['Base Color'].is_linked:l.new(p.inputs['Base Color'].links[0].from_socket,mix.inputs[1])
    else:mix.inputs[1].default_value=p.inputs['Base Color'].default_value
    l.new(mix.outputs[0],p.inputs['Base Color'])

def run():
    assert not bpy.context.scene.get('valorant_balance_pass')
    k.M={m.name:m for m in bpy.data.materials};k.STAGE=3
    # The diagnostic measured over-bright ceilings: reduce indirect intensity,
    # retain directional fixture pools, and keep local recess fills neutral.
    for room,intensity,bounce in [('BRIEFING',.55,20),('HALL',.65,18),('LOCKER',.62,38)]:
        bpy.data.objects['BOUNCE_'+room].data.intensity=intensity
        d=bpy.data.objects['EEVEE_floor_bounce_'+room].data;d.energy=bounce;d.color=(.80,.85,.90)
    for o in bpy.data.objects:
        if o.type!='LIGHT' or '_photometric' not in o.name:continue
        if o.name.startswith('BRIEFING'):o.data.energy*=1.20;o.data.color=(1,.78,.57)
        elif o.name.startswith('HALL'):o.data.energy*=1.20;o.data.color=(1,.84,.67)
        elif o.name.startswith('LOCKER'):o.data.energy*=.85;o.data.color=(1,.84,.68)
    for name,power in [('BRIEF_ceiling',0),('BRIEF_wall',35),('HALL_staff',70),('HALL_info',35),('LOCKER_bays',40),('LOCKER_front_fill',55),('LOCKER_pod_fill',45)]:
        d=bpy.data.objects['V_LIGHT_'+name].data;d.energy=power
        d.color=(.80,.88,1) if name.endswith(('front_fill','pod_fill')) else (1,.79,.60)
    ceiling=k.M['wall'].copy();ceiling.name='V_ceiling_mineral';tint(ceiling,(.60,.61,.63))
    for o in bpy.data.objects:
        if o.type=='MESH' and 'ceiling' in o.name.lower() and not o.name.startswith('SERVICE'):
            for s in o.material_slots:
                if s.material==k.M['wall']:s.material=ceiling
    tint(k.M['wall'],(.87,.89,.92));tint(k.M['dado'],(.84,.95,1.14))
    for i in range(5):
        tint(k.M['floor%d'%i],(.97,1.06,1.25))
        m=k.M['floor_timber_%d'%i];n=m.node_tree.nodes;l=m.node_tree.links;p=n['Principled BSDF']
        hue=n.new('ShaderNodeHueSaturation');hue.name='Faded matte timber palette';hue.inputs['Saturation'].default_value=.62;hue.inputs['Value'].default_value=1.4
        l.new(p.inputs['Base Color'].links[0].from_socket,hue.inputs['Color']);l.new(hue.outputs[0],p.inputs['Base Color'])
    for i in range(6):tint(k.M['V_tile%d'%i],(.88,.90,.93))
    # Rotate the actual broad surfaces of trailing leaves and their midribs.
    # The petiole bases stay attached; each leaf receives a different natural roll.
    for o in list(bpy.data.objects):
        if o.type!='MESH' or not any(t in o.name for t in ['_crown_leaf','_pothos']) or '_midrib' in o.name:continue
        rng=random.Random(wear.seed(o.name));base=o.data.vertices[0].co.copy();tip=o.data.vertices[-1].co.copy();axis=(tip-base).normalized()
        raised=Vector((axis.x,axis.y,axis.z+.18)).normalized()
        q=Quaternion(raised,rng.uniform(.70,1.25))@axis.rotation_difference(raised)
        for vert in o.data.vertices:vert.co=base+(q@(vert.co-base))*1.30
        stem,suffix=(o.name.rsplit('.',1) if o.name.rsplit('.',1)[-1].isdigit() else (o.name,None))
        rib=bpy.data.objects.get(stem+'_midrib'+('.'+suffix if suffix else ''))
        if rib:
            for spline in rib.data.splines:
                for pt in spline.points:pt.co=(*tuple(base+(q@(Vector(pt.co[:3])-base))*1.30),1)
        o.data.update()
    p=bpy.data.objects['V_BRIEF_corner_ficus'];p.scale.x*=.91;p.scale.y*=.91;p.scale.z*=1.13
    p=bpy.data.objects['V_HALL_staff_ficus'];p.scale.x*=.93;p.scale.y*=.93;p.scale.z*=1.12
    # Display centers are lifted to the eye-height band in the fixed concept.
    bpy.data.objects['BRIEFING_TV'].location.z+=.20
    board=bpy.data.objects['LIFE_whiteboard'];board.location.z+=.18;board.scale=(1.2,1,1.2)
    for o in bpy.data.objects:
        if o.type=='FONT' and o.name.startswith('LIFE_whiteboard_marker'):
            o.data.offset=.00055
            if o.name!='LIFE_whiteboard_marker':o.data.size*=1.2
    poster=bpy.data.objects['V_HALL_culture_poster'];poster.location.y=7.82;poster.location.z=1.88;poster.scale=(.74,1,.62)
    board=bpy.data.objects['V_HALL_shift_board'];board.location.y=6.0;board.scale=(1.30,1,1.10)
    # The narrow pressure bottle retains its physical mount and valve details.
    ext=bpy.data.objects['V_HALL_extinguisher'];ext.scale.x*=.82;ext.scale.y*=.93
    b=k.start()
    for j in range(13):
        z=-.001-j*.007
        k.box('V_EXT_service_rule',(-.003,-.2655,z),(.085 if j%4 else .065,.0005,.0013),'ink',0)
    k.label('V_EXT_service_heading','SERVICE / 04',(-.05,-.266,-.112),.012,'ink')
    for ob in set(bpy.data.objects)-b:ob.parent=ext
    # A closer lens fills the locker frame without moving its banks or the pod.
    bpy.data.objects['REFERENCE_LOCKER'].data.lens*=1.065
    bpy.context.scene['valorant_balance_pass']=8
