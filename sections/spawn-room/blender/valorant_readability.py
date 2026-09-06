"""Ninth comparison: ceiling recovery, readable print and richer plant cascades."""
import bpy
from math import pi
from mathutils import Vector
import grounded_kit as k

def slashes(name,parent,y,z,height,material):
    for i in range(2):
        x=-height*.46+i*height*.45
        o=k.mesh(name,[(x,y,z),(x+height*.25,y,z),(x+height*.61,y,z+height),(x+height*.36,y,z+height)],[(0,1,2,3)],material);o.parent=parent

def run():
    assert not bpy.context.scene.get('valorant_readability_pass')
    k.M={m.name:m for m in bpy.data.materials};k.STAGE=3
    for room,power in [('BRIEFING',35),('HALL',32),('LOCKER',58)]:bpy.data.objects['EEVEE_floor_bounce_'+room].data.energy=power
    bpy.data.objects['V_LIGHT_BRIEF_ceiling'].data.energy=12
    # Retain warm practical light, without the near-black ceiling from pass08.
    for o in bpy.data.objects:
        if o.type=='LIGHT' and o.name.startswith('LOCKER') and '_photometric' in o.name:o.data.color=(1,.79,.59)
    poster=bpy.data.objects['V_HALL_culture_poster'];poster.location.z=1.71;poster.scale.x=.60
    # Separate overlapping printed landscape layers: they were coplanar.
    landscapes=sorted([o for o in bpy.data.objects if o.name.startswith('V_HALL_poster_landscape')],key=lambda o:o.name)
    for i,o in enumerate(landscapes):
        for vert in o.data.vertices:vert.co.y-=i*.00065
    slashes('V_HALL_brandmark',poster,-.025,.006,.09,'canvas_rust')
    slashes('V_AID_brandmark',bpy.data.objects['V_HALL_first_aid'],-.157,-.227,.033,'canvas_rust')
    for i,size in enumerate([.071,.056,.054,.065]):
        o=bpy.data.objects['V_HALL_notice_%d_type'%i];o.data.size=size;o.data.offset=.0002
    # Quiet graphite tube frames and dry faded timber match the worn palette.
    for root in bpy.data.objects:
        if root.type=='EMPTY' and 'bench' in root.name:
            for o in root.children_recursive:
                if o.type in {'MESH','CURVE'}:
                    for slot in o.material_slots:
                        if slot.material and slot.material.name=='darksteel':slot.material=k.M['V_graphite']
    m=k.M['bench_worn_timber'];n=m.node_tree.nodes;l=m.node_tree.links;p=n['Principled BSDF']
    hue=n.new('ShaderNodeHueSaturation');hue.inputs['Saturation'].default_value=.58;hue.inputs['Value'].default_value=1.10
    l.new(p.inputs['Base Color'].links[0].from_socket,hue.inputs['Color']);l.new(hue.outputs[0],p.inputs['Base Color'])
    # Extend the existing living vines; all leaves remain on their own vine nodes.
    for o in list(bpy.data.objects):
        if o.type=='MESH' and '_pothos' in o.name and '_midrib' not in o.name:
            base=o.data.vertices[0].co.copy();drop=max(0,.44-base.z)*.65
            for vert in o.data.vertices:vert.co.z-=drop
            stem,suffix=(o.name.rsplit('.',1) if o.name.rsplit('.',1)[-1].isdigit() else (o.name,None))
            rib=bpy.data.objects.get(stem+'_midrib'+('.'+suffix if suffix else ''))
            if rib:
                for spline in rib.data.splines:
                    for pt in spline.points:pt.co.z-=drop
        elif o.type=='CURVE' and o.name.startswith('V_') and '_vine' in o.name:
            for spline in o.data.splines:
                for pt in spline.points:pt.co.z-=max(0,.44-pt.co.z)*.65
    # Surface print is made of real small vector marks and remains on the fabric.
    slashes('V_DUFFEL_owner_mark',bpy.data.objects['V_LOCKER_floor_duffel'],-.187,.071,.039,'paper')
    bpy.context.scene['valorant_readability_pass']=9
