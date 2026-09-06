"""Tenth comparison: tactile mineral floors and readable briefing information."""
import bpy
from math import pi
import grounded_kit as k
import worn_surfaces as wear
import revise_spawn as rev
from valorant_balance import tint

def run():
    assert not bpy.context.scene.get('valorant_surface_finish_pass')
    k.M={m.name:m for m in bpy.data.materials};k.STAGE=3
    # Restore larger concrete variation from the retained CC0 scan, not gloss.
    for i in range(5):
        m=k.M['floor%d'%i];n=m.node_tree.nodes
        for node in n:
            if node.type=='VALTORGB' and node.inputs[0].is_linked and node.inputs[0].links[0].from_node.type=='RGBTOBW':
                a,b=node.color_ramp.elements
                a.color=(*(c*.52 for c in a.color[:3]),1);b.color=(*(c*1.20 for c in b.color[:3]),1)
            elif node.type=='BUMP':node.inputs['Strength'].default_value=.65;node.inputs['Distance'].default_value=.020
        tint(m,(1,.94,.83))
    # Matte porcelain uses warm grey body clay with occasional sage tiles.
    for i in range(6):tint(k.M['V_tile%d'%i],(.78,.64,.49))
    tint(k.M['V_tile2'],(.77,.88,.86));tint(k.M['V_tile4'],(.89,.96,.91))
    # Local ceiling fill retains warm bounce without bleaching the concrete walls.
    for room in ['BRIEFING','HALL','LOCKER']:
        bpy.data.objects['EEVEE_floor_bounce_'+room].data.color=(1,.78,.58)
    bpy.data.objects['V_LIGHT_HALL_staff'].data.energy=55
    # Printed discipline poster occupies the near return wall in the concept.
    poster=bpy.data.objects['V_BRIEF_discipline_poster'];poster.location=(-6.60,1.0,2.08);poster.rotation_euler.z=pi
    poster['cs_support_target']='BRIEFING_south'
    # Four clear checklist rows rather than sparse tiny lines.
    rev.remove_prefix('LIFE_whiteboard_marker.001','LIFE_whiteboard_marker.002','LIFE_whiteboard_marker.003','LIFE_whiteboard_erased')
    board=bpy.data.objects['LIFE_whiteboard'];b=k.start()
    for i,body in enumerate(['Systems nominal','Check inventory','Report anomalies','Next shift notes']):
        z=.127-i*.100
        k.frame('V_BRIEF_check_box',(-.600,-.033,z+.016),.025,.025,.002,.001,'dry_marker',.003)
        t=k.label('V_BRIEF_handover_row',body,(-.558,-.033,z),.052,'dry_marker');t.data.offset=.0003
    for o in set(bpy.data.objects)-b:o.parent=board
    t=bpy.data.objects['LIFE_whiteboard_marker'];t.data.size=.066;t.data.offset=.0004
    bpy.data.objects['V_BRIEF_map'].scale=(1.20,1,1.20)
    # Broad restrained mineral patches retain the real plaster microtexture.
    m=k.M['wall'];n=m.node_tree.nodes;l=m.node_tree.links;p=n['Principled BSDF']
    geo=n.new('ShaderNodeNewGeometry');q=wear.noise(n,l,geo.outputs['Position'],7.5,1)
    wash=wear.ramp(n,l,q,[(.77,.75,.72),(1.05,1.045,1.025)],(.44,.58))
    mix=n.new('ShaderNodeMixRGB');mix.name='Mineral wash moderation';mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.10
    l.new(p.inputs['Base Color'].links[0].from_socket,mix.inputs[1]);l.new(wash,mix.inputs[2]);l.new(mix.outputs[0],p.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.003
    l.new(p.inputs['Normal'].links[0].from_socket,bump.inputs['Normal']);l.new(q,bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
    bpy.context.scene['valorant_surface_finish_pass']=10
