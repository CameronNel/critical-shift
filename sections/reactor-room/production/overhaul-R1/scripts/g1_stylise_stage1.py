"""Stage 1 stylisation: painted dado + trim line, worn bright edges, floor-up grime. Procedural nodes on the existing materials."""
import bpy,sys; sys.path.insert(0,"."); import palette2
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w16.blend")
def N(nt,t,x,y,**k):
    n=nt.nodes.new(t); n.location=(x,y)
    for a,b in k.items(): setattr(n,a,b)
    return n
def mix(nt,x,y): m=N(nt,"ShaderNodeMix",x,y); m.data_type='RGBA'; m.blend_type='MIX'; return m
def stylise(m,edge_col,grime,dado):
    nt=m.node_tree; b=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'); sock=b.inputs['Base Color']
    if not sock.is_linked or nt.nodes.get("ST_DONE"): return False
    src=sock.links[0].from_socket; x0=b.location.x-1100; y0=b.location.y-300
    N(nt,"NodeFrame",0,0,name="ST_DONE",label="stage1 stylise")
    geo=N(nt,"ShaderNodeNewGeometry",x0,y0-300)
    bev=N(nt,"ShaderNodeBevel",x0,y0); bev.inputs['Radius'].default_value=0.03; bev.samples=4
    dot=N(nt,"ShaderNodeVectorMath",x0+200,y0); dot.operation='DOT_PRODUCT'
    nt.links.new(bev.outputs['Normal'],dot.inputs[0]); nt.links.new(geo.outputs['Normal'],dot.inputs[1])
    em=N(nt,"ShaderNodeMapRange",x0+400,y0); em.inputs['From Min'].default_value=0.995; em.inputs['From Max'].default_value=0.90; em.inputs['To Min'].default_value=0.0; em.inputs['To Max'].default_value=1.0
    nt.links.new(dot.outputs['Value'],em.inputs['Value'])
    e1=mix(nt,x0+700,y0); e1.inputs[7].default_value=(*edge_col,1); nt.links.new(src,e1.inputs[6]); nt.links.new(em.outputs['Result'],e1.inputs[0])
    cur=e1.outputs[2]
    sep=N(nt,"ShaderNodeSeparateXYZ",x0+200,y0-300); nt.links.new(geo.outputs['Position'],sep.inputs['Vector'])
    if grime>0:
        gz=N(nt,"ShaderNodeMapRange",x0+400,y0-300); gz.inputs['From Min'].default_value=0.0; gz.inputs['From Max'].default_value=4.0; gz.inputs['To Min'].default_value=1.0; gz.inputs['To Max'].default_value=0.0
        nt.links.new(sep.outputs['Z'],gz.inputs['Value'])
        noi=N(nt,"ShaderNodeTexNoise",x0+400,y0-550); noi.inputs['Scale'].default_value=2.6; noi.inputs['Detail'].default_value=4
        gm=N(nt,"ShaderNodeMath",x0+650,y0-400); gm.operation='MULTIPLY'; gm.inputs[1].default_value=grime
        nt.links.new(gz.outputs['Result'],gm.inputs[0])
        gn=N(nt,"ShaderNodeMath",x0+850,y0-450); gn.operation='MULTIPLY'; nt.links.new(gm.outputs['Value'],gn.inputs[0]); nt.links.new(noi.outputs['Fac'],gn.inputs[1])
        gx=N(nt,"ShaderNodeMath",x0+1000,y0-450); gx.operation='MULTIPLY'; gx.inputs[1].default_value=2.0; nt.links.new(gn.outputs['Value'],gx.inputs[0])
        g1=mix(nt,x0+1150,y0-100); g1.inputs[7].default_value=(0.012,0.008,0.014,1); nt.links.new(cur,g1.inputs[6]); nt.links.new(gx.outputs['Value'],g1.inputs[0]); cur=g1.outputs[2]
    if dado:
        dm=N(nt,"ShaderNodeMapRange",x0+400,y0-800); dm.inputs['From Min'].default_value=1.20; dm.inputs['From Max'].default_value=1.14; dm.inputs['To Min'].default_value=0.0; dm.inputs['To Max'].default_value=1.0
        nt.links.new(sep.outputs['Z'],dm.inputs['Value'])
        d1=mix(nt,x0+1300,y0-100); d1.inputs[7].default_value=(0.020,0.030,0.090,1); nt.links.new(cur,d1.inputs[6]); nt.links.new(dm.outputs['Result'],d1.inputs[0])
        sm=N(nt,"ShaderNodeMapRange",x0+400,y0-1050); sm.inputs['From Min'].default_value=1.20; sm.inputs['From Max'].default_value=1.26; sm.inputs['To Min'].default_value=0.0; sm.inputs['To Max'].default_value=1.0
        nt.links.new(sep.outputs['Z'],sm.inputs['Value'])
        sm2=N(nt,"ShaderNodeMapRange",x0+400,y0-1250); sm2.inputs['From Min'].default_value=1.34; sm2.inputs['From Max'].default_value=1.28; sm2.inputs['To Min'].default_value=0.0; sm2.inputs['To Max'].default_value=1.0
        nt.links.new(sep.outputs['Z'],sm2.inputs['Value'])
        sx=N(nt,"ShaderNodeMath",x0+700,y0-1150); sx.operation='MULTIPLY'; nt.links.new(sm.outputs['Result'],sx.inputs[0]); nt.links.new(sm2.outputs['Result'],sx.inputs[1])
        d2=mix(nt,x0+1450,y0-100); d2.inputs[7].default_value=(0.55,0.14,0.02,1); nt.links.new(d1.outputs[2],d2.inputs[6]); nt.links.new(sx.outputs['Value'],d2.inputs[0]); cur=d2.outputs[2]
    nt.links.new(cur,sock); return True
RUSTHI=(0.85,0.30,0.04); WALLHI=(0.32,0.16,0.34); NAVYHI=(0.14,0.18,0.42); OXHI=(0.95,0.32,0.10); FLOORHI=(0.30,0.20,0.20)
groups=[("hall_white|white|CF white|AW white mineral|WP white mineral|H01 white mineral|hall_mineral|mineral|AW light mineral|H01 light mineral|WP light mineral|hall_mineral_light|hall_rim_stone|RF white|hall_paint_chip",WALLHI,0.55,True),
 ("hall_steel_light|steel_light|CF edge",NAVYHI,0.5,True),
 ("hall_steel|AW steel|steel|H01 folded steel|WP fine gunmetal frame|H01 gunmetal paint|AW gunmetal|CF gunmetal|CF black|RF gunmetal|RF dark|RF edge",RUSTHI,0.4,False),
 ("hall_teal|hall_teal_dark|hall_cast_iron|hall_vessel_enamel|hall_teal_light|hall_teal_service|AW stair protection paint",OXHI,0.5,False),
 ("hall_floor|hall_floor_wear|CF floor|CF floor joint|hall_floor_yellow|hall_floor_light|floor_light|tread_wear|stair_tread",FLOORHI,0.35,False)]
n=0
for names,ec,gr,dd in groups:
    for nm in names.split("|"):
        for m in bpy.data.materials:
            if m.use_nodes and m.name.split(".MCP Backup")[0]==nm and stylise(m,ec,gr,dd): n+=1
print("stylised materials:",n)
bpy.ops.wm.save_as_mainfile(filepath=S+"/w17.blend"); print("ok")
