"""W20: measured joint/sweep clearances and readable booth glazing."""
ob=bpy.data.objects['Filter inlet drop'];ob.location.x=-5.38
ob=bpy.data.objects['Filter inlet upper offset'];ob.location.x=-5.43;ob.dimensions.x=.50
ob=bpy.data.objects['Filter inlet welded neck'];ob.location.x=-1.03
for ob in [o for o in SC.objects if o.name.startswith('Inlet neck flange bolt')]:ob.location.x-=.13
bpy.data.objects['DR01'].location.y=6.285;bpy.data.objects['DR02'].location.y=7.315
# A jamb hinge leaf is stationary; only the door-side barrel/leaf moves.
for ob in [o for o in SC.objects if o.name.startswith('Personnel jamb hinge leaf')]:
    mat=ob.matrix_world.copy();ob.parent=None;ob.matrix_world=mat
current='Monitoring'
box('Isolator branch support bridge',(-3.42,16.675,3.27),(.08,2.65,.045),'bus',bevel=.003)
# The booth is glazed, not opaque smoked sheet. Neutral glass retains warm
# reflections without introducing teal and reveals the actual desk beyond.
m=M['glass'];bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*srgb('E8E5DC'),1);bs.inputs['Transmission Weight'].default_value=1;bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=.08;bs.inputs['IOR'].default_value=1.45
for shader_link in list(bs.inputs['Base Color'].links)+list(bs.inputs['Roughness'].links):m.node_tree.links.remove(shader_link)
