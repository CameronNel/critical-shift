"""Reactor room palette pass: tints existing material colour paths, keeping texture detail."""
import bpy, colorsys

def C(h,s,v): return colorsys.hsv_to_rgb(h,s,v)
# target: (rgb, value_multiplier)
PUTTY   =(C(.105,.42,.80),1.0)
SAGE    =(C(.47,.42,.55),1.0)
PETROL  =(C(.53,.62,.30),1.0)
INK     =(C(.58,.55,.14),1.0)
ENAMEL  =(C(.54,.70,.42),1.0)
CLAY    =(C(.075,.30,.50),1.0)
CLAY_L  =(C(.09,.22,.68),1.0)
MUSTARD =(C(.12,.85,.90),1.0)
CORAL   =(C(.015,.80,.82),1.0)
IVORY   =(C(.11,.16,.90),1.0)

MAP={}
def put(names,t):
    for n in names.split("|"): MAP[n]=t
put("hall_white|white|CF white|AW white mineral|WP white mineral|H01 white mineral|hall_mineral|mineral|AW light mineral|H01 light mineral|WP light mineral|hall_mineral_light|hall_rim_stone|RF white|hall_paint_chip",PUTTY)
put("hall_steel_light|steel_light|CF edge",SAGE)
put("hall_steel|AW steel|steel|H01 folded steel|WP fine gunmetal frame|H01 gunmetal paint|AW gunmetal|CF gunmetal|CF black|RF gunmetal|RF dark|RF edge",INK)
put("hall_teal|hall_teal_dark|hall_teal_light|hall_teal_service|hall_cast_iron|hall_vessel_enamel|AW stair protection paint",ENAMEL)
put("hall_floor|hall_floor_wear|CF floor|CF floor joint|hall_floor_yellow",CLAY)
put("hall_floor_light|floor_light|tread_wear|stair_tread",CLAY_L)
put("hall_yellow|yellow|hall_orange|H01 vivid orange|CF orange|RF orange|Poster orange anodized",MUSTARD)
put("red",CORAL)
put("hall_pipe|pipe|hall_insulation_jacket|hall_insulation_return|hall_pipe_shadow|hall_shaft|shaft|hall_reactor_drive|CF desk",IVORY)
put("hall_pool_tile",(C(.51,.55,.55),1.0))

def tint(mat,rgb,vm):
    nt=mat.node_tree; b=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
    sock=b.inputs['Base Color']
    if not sock.is_linked:
        sock.default_value=(*rgb,1); return
    if any(n.name=="PAL_TINT" for n in nt.nodes): nt.nodes["PAL_TINT"].inputs[7].default_value=(*rgb,1); return
    l=sock.links[0]; src,srcs=l.from_socket.node,l.from_socket
    mix=nt.nodes.new("ShaderNodeMix"); mix.name="PAL_TINT"; mix.data_type='RGBA'; mix.blend_type='COLOR'
    mix.inputs[0].default_value=1.0; mix.inputs[7].default_value=(*rgb,1)
    nt.links.new(srcs,mix.inputs[6]); nt.links.new(mix.outputs[2],sock)
    mix.location=(b.location.x-250,b.location.y)

def apply():
    n=0
    for m in bpy.data.materials:
        base=m.name.split(".MCP Backup")[0]
        if base in MAP and m.use_nodes:
            rgb,vm=MAP[base]; tint(m,rgb,vm); n+=1
    # pool: restore cyan hero
    for m in bpy.data.materials:
        base=m.name.split(".MCP Backup")[0]
        if base in("pool_glow","hall_cyan_indicator","hall_screen_line"):
            b=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
            b.inputs['Base Color'].default_value=(.02,.49,.59,1); 
            if 'Emission Color' in b.inputs: b.inputs['Emission Color'].default_value=(.05,.75,.95,1)
    return n
