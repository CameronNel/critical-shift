"""Eleventh comparison: wall light falloff, varied foliage and corner viewpoints."""
import bpy,random
from mathutils import Vector,Quaternion
import worn_surfaces as wear
import revise_spawn as rev

def run():
    assert not bpy.context.scene.get('valorant_local_balance_pass')
    # Local corrections to the prior incremental pass, also safe in a full build.
    rev.remove_prefix('LIFE_whiteboard_marker.001','LIFE_whiteboard_marker.002','LIFE_whiteboard_marker.003')
    m=bpy.data.materials['wall'];p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].links[0].from_node.inputs[0].default_value=.10
    for name,power in [('BRIEFING_light_01_photometric',42),('V_LIGHT_BRIEF_wall',25),('EEVEE_floor_bounce_BRIEFING',25),('V_LIGHT_BRIEF_ceiling',14),('EEVEE_floor_bounce_HALL',40),('LOCKER_light_01_photometric',75)]:bpy.data.objects[name].data.energy=power
    bpy.data.objects['V_LIGHT_BRIEF_ceiling'].data.color=(1,.78,.58)
    # Natural leaf aspect and varied lengths, preserving each attached base.
    for o in list(bpy.data.objects):
        if o.type!='MESH' or '_broad_leaf' not in o.name or '_midrib' in o.name:continue
        rng=random.Random(wear.seed(o.name)+11);base=o.data.vertices[0].co.copy();axis=(o.data.vertices[-1].co-base).normalized();long=rng.uniform(.92,1.21);width=rng.uniform(.65,.84)
        def change(pt):
            d=pt-base;along=axis*d.dot(axis);return base+along*long+(d-along)*width
        for vert in o.data.vertices:vert.co=change(vert.co)
        stem,suffix=(o.name.rsplit('.',1) if o.name.rsplit('.',1)[-1].isdigit() else (o.name,None))
        rib=bpy.data.objects.get(stem+'_midrib'+('.'+suffix if suffix else ''))
        if rib:
            rib.data.bevel_depth*=.55
            for spline in rib.data.splines:
                for pt in spline.points:pt.co=(*tuple(change(Vector(pt.co[:3]))),1)
    # Small standing-position changes expose the near return wall and locker face.
    specs=[('BRIEFING',(-2.62,1.40,1.62),(-5.25,4.4,1.3),.035,22),('HALL',(.8,8.95,1.65),(0,1.3,1.42),-.055,23.1),('LOCKER',(7.80,1.32,1.67),(3.65,4.6,1.3),-.057,22.365)]
    for name,eye,target,yaw,lens in specs:
        c=bpy.data.objects['REFERENCE_'+name];c.location=eye;q=(Vector(target)-c.location).to_track_quat('-Z','Y');c.rotation_euler=(Quaternion((0,0,1),yaw)@q).to_euler();c.data.lens=lens
    bpy.context.scene['valorant_local_balance_pass']=11
