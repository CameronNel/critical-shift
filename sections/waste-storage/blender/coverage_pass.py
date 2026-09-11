"""W18: final approach cameras for individually accessible container faces."""
current='Cameras'
for name,loc,target,lens in [('C06_Dry',(2.65,8.25,1.68),(4.25,7.35,1.0),24),('W09_DrySouth',(2.65,5.35,1.68),(4.25,6.25,.9),24),('W10_ResidueService',(-3.0,6.6,1.68),(-4.55,6.8,1.0),20)]:
    o=SC.objects.get(name)
    if o is None:
        d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);COL[current].objects.link(o);d.clip_start=.04;d.clip_end=120
    o.location=loc;o.data.lens=lens;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
SC['interface_json']=(ROOT/'interface.json').read_text()
