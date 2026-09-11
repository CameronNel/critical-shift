"""Bounded integration corrections, callable during build or on the owned live scene."""
import bpy

def apply():
    targets=['Structural floor','TRAIN foundation','TRAIN grout bed','LP exhaust pit flange','LP exhaust downhood']
    assert all(n in bpy.data.objects for n in targets)
    if 'U04 exact opening cutter' in bpy.data.objects:return
    hood=bpy.data.objects['LP exhaust downhood']
    # Original cube local lower face .35 ->0 while keeping the upper seam at1.55.
    for v in hood.data.vertices:
        worldz=v.co.z+hood.location.z
        if worldz<.6:v.co.z-=.35
    bevel=hood.modifiers.get('Manufactured edge radius')
    if bevel:bevel.width=.025
    bpy.ops.mesh.primitive_cube_add(size=1,location=(4.6,11.45,0))
    cutter=bpy.context.object;cutter.name='U04 exact opening cutter';cutter.dimensions=(2.5,1.5,4)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    cutter.hide_render=True;cutter.hide_set(True);cutter.display_type='WIRE'
    cutter['purpose']='Non-rendered Boolean operand; clear handoff aperture2.5x1.5m centered at U04'
    for name in targets:
        o=bpy.data.objects[name];m=o.modifiers.new('U04 physical exhaust penetration','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter
    bpy.context.scene['U04_opening']='Evaluated through-opening x3.35..5.85/y10.7..12.2 through foundation/floor at z0; condenser remains unassigned'
