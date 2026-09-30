"""Control-room material library (names 'CR ...').  Palette: charcoal / graphite steel / olive-grey / mineral plaster,
warm tungsten light, hazard orange + yellow accents.  No purple, no teal, no navy."""
import bpy,math,random,zlib
import numpy as np
import crk,crt
from crk import pm,tex_mat,emit_mat,glass_mat,new_image
def make(R):
    M={}
    # ---- architecture
    M["WALL_LO"]=pm("CR wall dado olive",(0.078,0.094,0.056),0.52,edge=(0.17,0.19,0.11),grime=0.55,scale=1.6,var=(0.84,1.07),coat=0.05)
    M["WALL_HI"]=pm("CR wall mineral plaster",(0.215,0.20,0.165),0.82,scale=1.1,var=(0.86,1.05),bump=0.12,grime=0.30,grain=0.05)
    M["WALL_BAND"]=pm("CR wall band graphite",(0.030,0.034,0.033),0.5,edge=(0.14,0.15,0.14),scale=2.0)
    M["TRIM"]=pm("CR trim charcoal steel",(0.040,0.044,0.044),0.42,metal=0.55,edge=(0.22,0.23,0.22),scale=2.0,bump=0.0)
    M["STEEL"]=pm("CR graphite steel",(0.058,0.066,0.068),0.38,metal=0.75,edge=(0.27,0.28,0.28),scale=2.2,bump=0.0)
    M["STEEL_L"]=pm("CR galvanised steel",(0.36,0.37,0.37),0.30,metal=0.85,edge=(0.55,0.55,0.53),scale=3.0,bump=0.0,var=(0.85,1.05))
    M["BLACK"]=pm("CR black plastic",(0.016,0.017,0.019),0.48,edge=(0.10,0.10,0.10),scale=3.0,bump=0.02)
    M["RUBBER"]=pm("CR rubber",(0.020,0.022,0.020),0.85,scale=3.0,bump=0.10)
    M["CEIL"]=pm("CR ceiling tile",(0.25,0.235,0.195),0.95,scale=2.0,var=(0.88,1.03),bump=0.22,grain=0.06)
    M["CEIL_GRID"]=pm("CR ceiling grid",(0.47,0.46,0.43),0.42,metal=0.35,edge=(0.6,0.6,0.56),scale=3.0,bump=0.0)
    M["PLENUM"]=pm("CR plenum dark",(0.012,0.013,0.013),0.9,scale=2.0)
    ft=new_image("CR floor tile",crt.floor_tile(1024,3)); M["FLOOR"]=_floor(ft)
    # ---- furniture / plastics
    M["WOOD"]=pm("CR laminate walnut",(0.105,0.068,0.042),0.36,scale=1.5,var=(0.80,1.10),aniso=(1.0,14.0,1.0),coat=0.12,bump=0.02,edge=(0.22,0.14,0.07),edge_w=0.003)
    M["EDGE"]=pm("CR desk edge",(0.022,0.024,0.024),0.5,scale=3.0)
    M["BEIGE"]=pm("CR platinum plastic",(0.37,0.345,0.27),0.44,edge=(0.50,0.47,0.38),grime=0.25,var=(0.90,1.04),bump=0.02,scale=1.8)
    M["BEIGE_D"]=pm("CR platinum plastic dark",(0.20,0.19,0.15),0.46,edge=(0.28,0.26,0.20),var=(0.9,1.05),bump=0.02,scale=1.8)
    M["GREY"]=pm("CR grey plastic",(0.10,0.105,0.10),0.46,edge=(0.20,0.20,0.19),bump=0.02,scale=1.8)
    M["KEY"]=pm("CR keycap",(0.24,0.225,0.18),0.5,edge=(0.34,0.32,0.26),bump=0.0,scale=6.0,var=(0.92,1.04))
    M["KEY_D"]=pm("CR keycap dark",(0.10,0.10,0.095),0.5,edge=(0.18,0.18,0.17),bump=0.0,scale=6.0)
    M["FABRIC"]=pm("CR chair fabric",(0.030,0.033,0.029),0.92,scale=4.0,var=(0.80,1.15),bump=0.28,grain=0.10)
    M["FABRIC_O"]=pm("CR fabric rust",(0.28,0.085,0.028),0.95,scale=4.0,var=(0.85,1.1),bump=0.28,grain=0.08)
    M["PAPER"]=pm("CR paper",(0.60,0.59,0.53),0.86,scale=2.0,bump=0.03,var=(0.94,1.03))
    M["CARD"]=pm("CR cardboard",(0.36,0.25,0.14),0.9,scale=2.0,bump=0.10,var=(0.85,1.08))
    M["ORANGE"]=pm("CR hazard orange",(0.52,0.14,0.018),0.48,edge=(0.72,0.28,0.06),scale=2.0,bump=0.02)
    M["YELLOW"]=pm("CR hazard yellow",(0.58,0.40,0.03),0.5,edge=(0.80,0.58,0.08),scale=2.0,bump=0.02)
    M["RED"]=pm("CR signal red",(0.32,0.022,0.015),0.42,edge=(0.55,0.08,0.05),scale=2.0,bump=0.02)
    M["LOCKER"]=pm("CR locker olive",(0.088,0.103,0.064),0.46,metal=0.35,edge=(0.20,0.22,0.13),grime=0.4,scale=1.4,var=(0.86,1.06),bump=0.0)
    M["CANVAS"]=pm("CR canvas olive",(0.100,0.112,0.070),0.92,scale=3.0,bump=0.22,grain=0.08)
    M["BLANKET"]=pm("CR blanket rust",(0.30,0.095,0.032),0.96,scale=3.0,bump=0.25,var=(0.86,1.1),grain=0.08)
    M["PILLOW"]=pm("CR pillow grey",(0.42,0.42,0.38),0.92,scale=3.0,bump=0.12)
    M["AC"]=pm("CR aircon casing",(0.40,0.38,0.31),0.42,edge=(0.52,0.50,0.42),grime=0.15,bump=0.02,scale=1.6)
    M["FRIDGE"]=pm("CR fridge enamel",(0.30,0.33,0.27),0.28,edge=(0.42,0.45,0.37),bump=0.0,scale=1.5,coat=0.2)
    M["CORK"]=pm("CR cork",(0.30,0.17,0.075),0.95,scale=5.0,bump=0.35,var=(0.75,1.2),grain=0.12)
    M["CABLE"]=pm("CR cable black",(0.016,0.016,0.017),0.55,scale=3.0,bump=0.0,grain=0)
    M["CABLE_G"]=pm("CR cable grey",(0.16,0.16,0.15),0.55,scale=3.0,bump=0.0,grain=0)
    M["CABLE_B"]=pm("CR cable beige",(0.30,0.28,0.22),0.55,scale=3.0,bump=0.0,grain=0)
    M["PORC"]=pm("CR mug ceramic",(0.34,0.33,0.29),0.22,scale=2.0,bump=0.0,coat=0.3)
    M["PORC_O"]=pm("CR mug orange",(0.46,0.13,0.02),0.22,scale=2.0,bump=0.0,coat=0.3)
    M["BRASS"]=pm("CR brass",(0.42,0.30,0.10),0.32,metal=0.9,scale=3.0,bump=0.0,var=(0.85,1.1))
    M["GLASS"]=bpy.data.materials.get("observation_glass") or glass_mat("CR glass")
    M["SOIL"]=pm("CR dry soil",(0.07,0.05,0.035),0.95,scale=6,bump=0.3)
    M["LEAF"]=pm("CR dead leaf",(0.20,0.17,0.06),0.9,scale=5,bump=0.1)
    # ---- printed / painted-image materials
    for k in ("machine","shift","comply","questions","report","hydrate"):
        M["P_"+k]=tex_mat("CR poster "+k,new_image("CR poster tex "+k,crt.poster(k,seed=zlib.crc32(k.encode())%1000)),rough=0.62)
    for k,rgb in (("form",None),("roster",None),("rules",None),("log",None),("safety",None),("passcard",None)):
        M["N_"+k]=tex_mat("CR notice "+k,new_image("CR notice tex "+k,crt.notice(k,seed=zlib.crc32(k.encode())%1000)),rough=0.8)
    M["HAZARD"]=tex_mat("CR hazard stripes",new_image("CR hazard tex",_hazard()),rough=0.5)
    # ---- emissive
    M["LED_G"]=[emit_mat(f"CR led green {k}",(0.12,1.0,0.16),4.5,_blink(R)) for k in range(4)]
    M["LED_A"]=[emit_mat(f"CR led amber {k}",(1.0,0.50,0.04),4.5,_blink(R)) for k in range(4)]
    M["LED_R"]=[emit_mat(f"CR led red {k}",(1.0,0.06,0.04),4.5,_blink(R)) for k in range(3)]
    M["LED_ON"]=emit_mat("CR led steady green",(0.12,1.0,0.16),3.0)
    M["LED_AON"]=emit_mat("CR led steady amber",(1.0,0.50,0.04),3.0)
    M["LED_RON"]=emit_mat("CR led steady red",(1.0,0.06,0.04),3.0)
    M["TUBE"]=emit_mat("CR tungsten tube",(1.0,0.66,0.34),7.0)
    M["TUBE_F"]=emit_mat("CR tungsten tube flicker",(1.0,0.66,0.34),7.0,FLICKER)
    M["TUBE_OFF"]=pm("CR tube dead",(0.30,0.28,0.22),0.4,scale=2.0,bump=0.0)
    M["BULB"]=emit_mat("CR bulb",(1.0,0.66,0.32),9.0)
    M["LAMPFACE"]=emit_mat("CR panel light",(1.0,0.72,0.44),1.6)
    return M
FLICKER="7.0*(1-0.85*max(0,sin(frame*2.7)*sin(frame*0.53)*sin(frame*0.19+1)-0.42)*3.0)"
def _blink(R):
    a,b,p,q=R.uniform(0.35,1.6),R.uniform(0.11,0.6),R.uniform(0,6.3),R.uniform(0,6.3)
    return f"4.5*max(0.03,min(1.0,(sin(frame*{a:.3f}+{p:.2f})+sin(frame*{b:.3f}+{q:.2f}))*3.2-1.6))"
def _hazard(N=256):
    X,Y=crt.XY(N,N); a=crt.canvas(N,N,(0.10,0.10,0.09)); s=((X+Y)/(N/4))%2
    crt.over(a,(s<1).astype(np.float32),(0.86,0.62,0.06)); return a
def _floor(img):
    m=crk._new("CR floor tile"); nt=m.node_tree
    out=crk._n(nt,"ShaderNodeOutputMaterial",900,0); b=crk._n(nt,"ShaderNodeBsdfPrincipled",600,0); nt.links.new(b.outputs['BSDF'],out.inputs['Surface'])
    b.inputs['Roughness'].default_value=0.42; b.inputs['Coat Weight'].default_value=0.12; b.inputs['Coat Roughness'].default_value=0.25
    g=crk._n(nt,"ShaderNodeNewGeometry",-700,0); mp=crk._n(nt,"ShaderNodeMapping",-450,0); mp.inputs['Scale'].default_value=(1/1.2,1/1.2,1/1.2); nt.links.new(g.outputs['Position'],mp.inputs['Vector'])
    tx=crk._n(nt,"ShaderNodeTexImage",-150,0); tx.image=img; tx.extension='REPEAT'; nt.links.new(mp.outputs['Vector'],tx.inputs[0]); nt.links.new(tx.outputs['Color'],b.inputs['Base Color'])
    nz=crk._n(nt,"ShaderNodeTexNoise",-150,-300); nz.inputs['Scale'].default_value=200; nt.links.new(g.outputs['Position'],nz.inputs['Vector'])
    bp=crk._n(nt,"ShaderNodeBump",300,-300); bp.inputs['Strength'].default_value=0.04; nt.links.new(nz.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],b.inputs['Normal'])
    return m
