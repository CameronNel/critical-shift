"""W08: repair unset incremental graphics material and restrain concrete texture."""
for ob in SC.objects:
    if ob.type=='MESH' and ob.name.startswith(('Divider oxide lower band','Wall bay underline')):
        ob.data.materials.clear();ob.data.materials.append(M['orange'])
for key,variation,scale in [('wall',.13,35),('floor',.15,55),('pale',.12,18)]:
    m=M[key];base=m.diffuse_color[:3]
    for n in m.node_tree.nodes:
        if n.type=='VALTORGB':
            n.color_ramp.elements[0].position=.15;n.color_ramp.elements[1].position=.85
            n.color_ramp.elements[0].color=(*(c*(1-variation) for c in base),1)
            n.color_ramp.elements[1].color=(*(min(1,c*(1+variation)) for c in base),1)
        if n.type=='TEX_NOISE' and n.inputs['Scale'].default_value<60:n.inputs['Scale'].default_value=scale;n.inputs['Detail'].default_value=1.2
# Camera evidence outside owned openings looks into the real room. No false
# neighboring corridor is invented to fill the unassembled boundary void.
current='Cameras'
for name,loc,target,lens in [('W05_ReceivingExterior',(0,-1.20,1.68),(0,5,1.65),22),('W06_PersonnelExterior',(7.0,2.2,1.68),(2.5,2.4,1.65),20),('W07_DispatchExterior',(0,19.0,1.68),(0,12,1.65),22),('W08_BoothDoor',(-1.2,2.15,1.68),(-3.5,2.2,1.5),24)]:
    d=bpy.data.cameras.new(name);d.lens=lens;d.clip_start=.04;d.clip_end=120;o=bpy.data.objects.new(name,d);COL[current].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
