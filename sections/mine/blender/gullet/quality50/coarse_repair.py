"""Render-driven coarse surface repair, separate from fine roughness noise."""
import bpy
from materials import noise,ramp

def gameplay_scale_surface_repair(scene,m):
    records=[]
    for material in list(bpy.data.materials):
        if not material.use_nodes or not material.get('q50_weathered'):continue
        name=material.name.lower();n=material.node_tree.nodes;l=material.node_tree.links;p=next((x for x in n if x.type=='BSDF_PRINCIPLED'),None)
        if p is None:continue
        if 'concrete' not in name and not any(x in name for x in ['slate','enamel','ochre']):continue
        co=n.new('ShaderNodeTexCoord');fac=noise(n,l,co.outputs['Object'],17 if 'concrete' in name else 24,4)
        old=p.inputs['Normal'].links[0].from_socket if p.inputs['Normal'].is_linked else None
        b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.8;b.inputs['Distance'].default_value=.012 if 'concrete' in name else .003
        l.new(fac,b.inputs['Height'])
        if old:l.new(old,b.inputs['Normal'])
        l.new(b.outputs['Normal'],p.inputs['Normal'])
        if 'concrete' in name:
            old=p.inputs['Base Color'].links[0].from_socket;mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.48
            grain=ramp(n,l,fac,[(.25,(.28,.26,.22,1)),(.65,(1,1,1,1))]);l.new(old,mix.inputs[1]);l.new(grain,mix.inputs[2]);l.new(mix.outputs[0],p.inputs['Base Color'])
        records.append(material.name)
    for o in scene.objects:
        if o.type=='MESH' and 'Walkway_panel' in o.name:
            for slot in o.material_slots:slot.link='OBJECT';slot.material=m['iron']
    return records
