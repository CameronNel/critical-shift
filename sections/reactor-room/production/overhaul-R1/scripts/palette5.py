"""Reactor room 'dead shift' palette: dark, gloomy, weathered. Tint + value control on existing material paths."""
import bpy, colorsys
def C(h,s,v): return colorsys.hsv_to_rgb(h,s,v)
# (target rgb for hue/sat, value multiplier applied after the tint)
WALL   =(C(.80,.42,.62),0.36)   # dusty aubergine plum
MID    =(C(.62,.45,.55),0.32)   # midnight blue-violet (structure panels)
IRON   =(C(.06,.35,.50),0.50)   # soot / oxidised iron
ENAMEL =(C(.995,.78,.60),0.85)  # oxblood machine paint
OLIVE  =(C(.22,.35,.55),0.70)   # filthy olive drab
FLOOR  =(C(.02,.30,.50),0.28)   # wet dark burnt clay
FLOOR_L=(C(.03,.28,.58),0.40)
RUST   =(C(.05,.85,.80),0.95)   # weathered rust-orange trim
BLOOD  =(C(.0,.90,.60),0.55)
LAG    =(C(.78,.10,.55),0.62)   # ash-lavender lagging / pipes
POOLT  =(C(.30,.30,.45),0.20)
MAP={}
def put(names,t):
    for n in names.split("|"): MAP[n]=t
put("hall_white|white|CF white|AW white mineral|WP white mineral|H01 white mineral|hall_mineral|mineral|AW light mineral|H01 light mineral|WP light mineral|hall_mineral_light|hall_rim_stone|RF white|hall_paint_chip",WALL)
put("hall_steel_light|steel_light|CF edge",MID)
put("hall_steel|AW steel|steel|H01 folded steel|WP fine gunmetal frame|H01 gunmetal paint|AW gunmetal|CF gunmetal|CF black|RF gunmetal|RF dark|RF edge",IRON)
put("hall_teal|hall_teal_dark|hall_cast_iron|hall_vessel_enamel|AW stair protection paint",ENAMEL)
put("hall_teal_light|hall_teal_service",OLIVE)
put("hall_floor|hall_floor_wear|CF floor|CF floor joint|hall_floor_yellow",FLOOR)
put("hall_floor_light|floor_light|tread_wear|stair_tread",FLOOR_L)
put("hall_yellow|yellow|hall_orange|H01 vivid orange|CF orange|RF orange|Poster orange anodized",RUST)
put("red",BLOOD)
put("hall_pipe|pipe|hall_insulation_jacket|hall_insulation_return|hall_pipe_shadow|hall_shaft|shaft|hall_reactor_drive|CF desk",LAG)
put("hall_pool_tile",POOLT)
def tint(mat,rgb,vm):
    nt=mat.node_tree; b=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'); sock=b.inputs['Base Color']
    if not sock.is_linked:
        sock.default_value=(rgb[0]*vm,rgb[1]*vm,rgb[2]*vm,1)
    else:
        mix=nt.nodes.get("PAL_TINT")
        if mix is None:
            l=sock.links[0]; mix=nt.nodes.new("ShaderNodeMix"); mix.name="PAL_TINT"; mix.data_type='RGBA'; mix.blend_type='COLOR'
            mix.inputs[0].default_value=1.0; nt.links.new(l.from_socket,mix.inputs[6]); mix.location=(b.location.x-450,b.location.y)
        mix.inputs[7].default_value=(*rgb,1)
        hv=nt.nodes.get("PAL_VAL")
        if hv is None:
            hv=nt.nodes.new("ShaderNodeHueSaturation"); hv.name="PAL_VAL"; hv.location=(b.location.x-250,b.location.y)
            nt.links.new(mix.outputs[2],hv.inputs['Color']); nt.links.new(hv.outputs['Color'],sock)
        hv.inputs['Value'].default_value=vm
    # wet look for floors
    if base_is_floor(mat.name) and not b.inputs['Roughness'].is_linked: b.inputs['Roughness'].default_value=0.28
def base_is_floor(n): return n.split(".MCP Backup")[0] in ("hall_floor","hall_floor_wear","hall_floor_light","floor_light","CF floor")
def apply():
    n=0
    for m in bpy.data.materials:
        base=m.name.split(".MCP Backup")[0]
        if base in MAP and m.use_nodes: rgb,vm=MAP[base]; tint(m,rgb,vm); n+=1
    return n
