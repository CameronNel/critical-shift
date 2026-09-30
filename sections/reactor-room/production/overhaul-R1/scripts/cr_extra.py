"""Second pass on the control room: door leaf, grime and floor work, emergency beacons, personal desk items, dirty hall-side glass with notices,
wall lettering and floor markings, collision proxies, haze.  Each function is independent and idempotent with cr_build.py."""
import bpy,math,random
import numpy as np
import crk,crt
from crk import text,new_image,decal_mat,tex_mat
from cr_props1 import wall_quad
FZ=5.40; CZ=8.50
def quad_xy(A,key,cx,cy,w,h,z,ang=0.0,up=True):
    """flat decal on a horizontal surface at height z (up = faces +z); w along local x, h along local y, rotated by ang about z"""
    c,s=math.cos(ang),math.sin(ang)
    def P(u,v): return (cx+u*c-v*s,cy+u*s+v*c,z)
    pts=[P(-w/2,-h/2),P(w/2,-h/2),P(w/2,h/2),P(-w/2,h/2)]
    if not up: pts=[pts[0],pts[3],pts[2],pts[1]]; uv=((0,0),(0,1),(1,1),(1,0))
    else: uv=((0,0),(1,0),(1,1),(0,1))
    A.plane(key,*pts,uv=uv)
# ---------------------------------------------------------------- 5. door
def door(c):
    """steel door leaf hinged on the north jamb, standing open 90 degrees into the room; badge reader on the wall beside the opening"""
    A,M=c.A,c.M; g="door"; X0=-4.80; yh=-6.34                       # hinge line y (north jamb inner edge)
    x0,x1=X0+0.062,X0+0.062+0.90; y0,y1=yh-0.046,yh-0.002; z0,z1=FZ+0.012,FZ+2.14
    A.bx((g,"LOCKER"),x0,x1,y0,y1,z0,z1,0.004)                                                       # leaf
    A.bx((g,"TRIM"),x0,x1,y0-0.002,y0,z0,z1,0.002) if False else None
    A.bx((g,"YELLOW"),x0+0.01,x1-0.01,y0-0.003,y0,z0+0.0,z0+0.26,0.001)                                # hazard kick plate (room side)
    for k in range(9): A.box((g,"BLACK"),x0+0.055+k*0.095,y0-0.0035,z0+0.13,z0+0.131,0.022,0.0015,0.9,0.0) if False else None
    A.bx((g,"GLASS"),x0+0.40,x0+0.66,y0-0.002,y1+0.001,z1-0.55,z1-0.18,0.0)                          # vision panel
    for (a,b,zz0,zz1) in ((x0+0.385,x0+0.675,z1-0.565,z1-0.550),(x0+0.385,x0+0.675,z1-0.180,z1-0.165)): A.bx((g,"STEEL"),a,b,y0-0.004,y1+0.002,zz0,zz1,0.002)
    for (a,b) in ((x0+0.385,x0+0.400),(x0+0.660,x0+0.675)): A.bx((g,"STEEL"),a,b,y0-0.004,y1+0.002,z1-0.565,z1-0.165,0.002)
    A.bx((g,"STEEL_L"),x1-0.14,x1-0.03,y0-0.030,y0-0.004,z0+1.00,z0+1.05,0.006); A.bx((g,"STEEL_L"),x1-0.085,x1-0.066,y0-0.030,y0,z0+0.96,z0+1.08,0.004)   # lever handle + rose
    A.bx((g,"BLACK"),x1-0.11,x1-0.05,y0-0.008,y0-0.002,z0+1.17,z0+1.28,0.003)                          # deadbolt escutcheon
    for zz in (z0+0.25,z0+1.05,z0+1.85):                                                              # hinge barrels on the hinge edge
        A.cyl((g,"STEEL_L"),x0+0.0,yh-0.02,zz,zz+0.11,0.013,14)
    A.bx((g,"STEEL"),x0+0.02,x0+0.30,y0-0.020,y0-0.004,z1-0.05,z1,0.004); A.tube((g,"STEEL_L"),[(x0+0.06,y0-0.015,z1-0.03),(x0+0.22,y0-0.025,z1-0.12),(x0+0.30,y0-0.035,z1-0.17)],0.006,8)   # door closer arm
    A.bx((g,"BRASS"),x1-0.20,x1-0.04,y0-0.004,y0,z0+1.62,z0+1.70,0.002)                               # number plate
    text(c.coll,"CONTROL 04",(x1-0.12),y0-0.0045,z0+1.66,'-y',0.030,M["BLACK"],'CENTER',"CR door number")
    # badge reader beside the opening (south side, west wall inner face)
    by=-7.46; bz=FZ+1.12
    A.fb((g,"BLACK"),'+x',X0+0.027,by-0.05,by+0.05,bz-0.09,bz+0.09,0.018,0.004)
    A.fb((g,"GREY"),'+x',X0+0.045,by-0.035,by+0.035,bz+0.01,bz+0.06,0.002,0.001); A.fb((g,"BLACK"),'+x',X0+0.045,by-0.03,by+0.03,bz-0.065,bz-0.012,0.002,0.0008)
    A.fb((g,"LED_RON"),'+x',X0+0.045,by-0.012,by+0.012,bz-0.078,bz-0.068,0.002,0.0)
    c.BADGE_LED=(X0+0.05,by,bz-0.073)
# ---------------------------------------------------------------- 6. grime, rubber mat, taped cable run
def _decal_mats(c):
    M=c.M
    if "D_STAIN" in M: return
    M["D_STAIN"]=decal_mat("CR decal water stain",new_image("CR decal water stain",crt.water_stain()),0.9)
    M["D_WEAR"]=decal_mat("CR decal floor wear",new_image("CR decal floor wear",crt.floor_wear()),0.9)
    M["D_RING"]=decal_mat("CR decal coffee ring",new_image("CR decal coffee ring",crt.coffee_ring()),0.6)
    M["D_SPILL"]=decal_mat("CR decal spill",new_image("CR decal spill",crt.coffee_ring(spill=True,seed=31)),0.5)
def grime(c):
    A,M,R=c.A,c.M,c.R; _decal_mats(c); g="grime"
    wall_quad(c,'+y',-11.91,-2.48,7.78,0.56,1.40,"D_STAIN",frame=False,off=0.0235,g=g,paper=False)                   # water stain down the back wall beside the TV
    for (x,y,w,ang) in ((-1.5,-9.46,0.95,0.4),(0.3,-8.26,0.85,1.1)):                                       # stained ceiling tiles
        quad_xy(A,(g,"D_STAIN"),x,y,w,w,CZ+0.0115,ang,up=False)
    for (x,y,w,h,ang) in ((-1.6,-8.75,5.6,1.25,0.02),(-3.0,-10.9,1.4,3.0,1.5708),(0.25,-9.75,1.0,3.0,1.5708),(-2.3,-7.0,4.2,0.7,0.0)):    # walkway scuffing
        quad_xy(A,(g,"D_WEAR"),x,y,w,h,FZ+0.0012,ang)
    quad_xy(A,(g,"D_SPILL"),-0.15,-10.85,0.62,0.62,FZ+0.0016,0.4); quad_xy(A,(g,"D_SPILL"),1.05,-9.0,0.45,0.45,FZ+0.0016,2.0)    # spills by the break counter and the copier
    quad_xy(A,(g,"D_RING"),-3.2,-9.95,0.14,0.14,FZ+0.79+0.0005,0.0) if False else None
    # rubber mat under the operator chairs (the yellow operator line stays visible along its front edge)
    A.bx((g,"RUBBER"),-3.72,1.62,-7.72,-6.62,FZ,FZ+0.008,0.002)
    for k in range(40): A.bx((g,"BLACK"),-3.70+k*0.1335,-3.70+k*0.1335+0.004,-7.70,-6.64,FZ+0.008,FZ+0.0095,0.0)     # moulded ribs
    # taped floor cable run: black/yellow cover strip with ramps, cables out of the rack, gaffer tape
    x=0.92; y0,y1=-9.85,-7.80; n=int((y1-y0)/0.07)
    for k in range(n):
        ya=y0+k*0.07; A.bx((g,"YELLOW" if k%2==0 else "BLACK"),x-0.065,x+0.065,ya,ya+0.068,FZ,FZ+0.022,0.004)
    A.hull((g,"BLACK"),[(x-0.065,y0,FZ),(x+0.065,y0,FZ),(x-0.065,y0-0.08,FZ),(x+0.065,y0-0.08,FZ),(x-0.065,y0,FZ+0.022),(x+0.065,y0,FZ+0.022)],0.002)
    A.hull((g,"BLACK"),[(x-0.065,y1+0.0,FZ),(x+0.065,y1,FZ),(x-0.065,y1+0.08,FZ),(x+0.065,y1+0.08,FZ),(x-0.065,y1,FZ+0.022),(x+0.065,y1,FZ+0.022)],0.002)
    for k,dx in enumerate((-0.03,0.0,0.03)):                                                                      # cables from the rack plinth to the cover
        A.tube((g,"CABLE" if k!=1 else "CABLE_G"),[(1.04,-10.32+dx*2,FZ+0.012),(0.98,-10.10+dx,FZ+0.010),(x+dx,y0-0.05,FZ+0.010)],0.0065,8)
        A.tube((g,"CABLE" if k!=1 else "CABLE_G"),[(x+dx,y1+0.06,FZ+0.010),(x+dx*1.5,y1-0.06,FZ+0.010),(x+dx*2,y1-0.18,FZ+0.012)],0.0065,8)
    for yy in (-10.05,-9.98,-7.72,-7.66): A.bx((g,"CABLE_G"),x-0.055,x+0.055,yy,yy+0.028,FZ+0.0205,FZ+0.0225,0.001) if False else A.bx((g,"CABLE_G"),0.88,0.97,yy,yy+0.03,FZ+0.0105,FZ+0.0125,0.001)   # gaffer tape
# ---------------------------------------------------------------- 8. defaced poster (see cr_mats: P_questions_def, used by cr_props2.wall_decor)
# ---------------------------------------------------------------- 9. personal desk items
def _misc_mats(c):
    M=c.M
    if "PHOTO" in M: return
    M["PHOTO"]=tex_mat("CR family photo",new_image("CR family photo tex",crt.photo()),rough=0.35)
    for k in "abcd": M["STICKY_"+k]=tex_mat("CR sticky "+k,new_image("CR sticky tex "+k,crt.sticky(k)),rough=0.85)
def desk_personal(c):
    A,M=c.A,c.M; _decal_mats(c); _misc_mats(c); g="personal"; ZT=6.17
    # family photo in a black frame on an easel back (bay 1, window side)
    fx,fy=-3.42,-6.80
    A.bx((g,"BLACK"),fx-0.065,fx+0.065,fy-0.008,fy+0.004,ZT,ZT+0.175,0.004); A.bx((g,"BLACK"),fx-0.02,fx+0.02,fy+0.004,fy+0.07,ZT,ZT+0.006,0.002)
    A.tube((g,"BLACK"),[(fx,fy+0.004,ZT+0.14),(fx,fy+0.07,ZT+0.006)],0.004,6)
    A.plane((g,"PHOTO"),(fx-0.052,fy-0.0085,ZT+0.012),(fx+0.052,fy-0.0085,ZT+0.012),(fx+0.052,fy-0.0085,ZT+0.163),(fx-0.052,fy-0.0085,ZT+0.163))
    # sticky notes on the CRT bezels (front, bottom centre): bay 1, bay 2, bay 3
    for (cx,zb,k) in ((-2.75,6.33,"a"),(-1.05,6.225,"b"),(0.65,6.33,"c")):
        A.plane((g,"STICKY_"+k),(cx+0.0,-6.9035,zb+0.004),(cx+0.05,-6.9035,zb+0.004),(cx+0.05,-6.9035,zb+0.052),(cx+0.0,-6.9035,zb+0.052))
    A.plane((g,"STICKY_d"),(-3.30,-7.40,ZT+0.002),(-3.22,-7.40,ZT+0.002),(-3.22,-7.32,ZT+0.002),(-3.30,-7.32,ZT+0.002))                      # a note left on the desk
    # cup rings and a coffee spill that reaches a sheet of paper
    for (x,y,w) in ((-3.46,-7.02,0.11),(0.95,-7.45,0.10),(-2.30,-6.75,0.10)): quad_xy(A,(g,"D_RING"),x,y,w,w,ZT+0.0008,0.0)
    quad_xy(A,(g,"D_SPILL"),-0.45,-7.30,0.22,0.22,ZT+0.0016,0.7)
    # thermos (bay 1)
    A.cyl((g,"STEEL_L"),-3.12,-6.62,ZT,ZT+0.27,0.04,24,0.004); A.cyl((g,"RED"),-3.12,-6.62,ZT+0.27,ZT+0.31,0.042,24,0.004); A.bx((g,"RED"),-3.085,-3.07 if False else -3.065,-6.632,-6.608,ZT+0.20,ZT+0.27,0.004) if False else None
    # cold tea and an untouched sandwich on a plate (bay 3)
    px,py=0.12,-7.30
    A.cyl((g,"PORC"),px,py,ZT,ZT+0.012,0.115,28,0.003)
    for k,(dy,mk) in enumerate(((0.0,"CARD"),(0.0,"PAPER"),(0.0,"CARD"))): A.bx((g,mk),px-0.07,px+0.07,py-0.05,py+0.05,ZT+0.012+k*0.012,ZT+0.012+(k+1)*0.012-0.001,0.003)
    A.prism((g,"PORC_O"),(px-0.20,py+0.05,ZT),(px-0.20,py+0.05,ZT+0.085),0.04,0.046,22,0,True,0.002); A.cyl((g,"BLACK"),px-0.20,py+0.05,ZT+0.078,ZT+0.0795,0.036,22)
    A.bx((g,"PORC_O"),px-0.242,px-0.218,py+0.044,py+0.056,ZT+0.03,ZT+0.07,0.003); A.cyl((g,"PORC"),px-0.20,py+0.05,ZT,ZT+0.004,0.075,24,0.002)
# ---------------------------------------------------------------- 10. dirty hall-side glass and taped notices
def window_dressing(c):
    A,M=c.A,c.M; _misc_mats(c); g="glassnote"
    gl=bpy.data.objects.get("MZ window glass")
    if gl:
        m=crk._new("CR window glass dirty"); nt=m.node_tree
        out=crk._n(nt,"ShaderNodeOutputMaterial",900,0); b=crk._n(nt,"ShaderNodeBsdfPrincipled",600,0); nt.links.new(b.outputs['BSDF'],out.inputs['Surface'])
        b.inputs['Base Color'].default_value=(0.55,0.58,0.57,1); b.inputs['IOR'].default_value=1.45
        geo=crk._n(nt,"ShaderNodeNewGeometry",-900,0); mp=crk._n(nt,"ShaderNodeMapping",-700,0); mp.inputs['Scale'].default_value=(9.0,9.0,0.55); nt.links.new(geo.outputs['Position'],mp.inputs['Vector'])   # vertical run streaks
        n1=crk._n(nt,"ShaderNodeTexNoise",-500,100); n1.inputs['Scale'].default_value=2.2; n1.inputs['Detail'].default_value=4.0; nt.links.new(mp.outputs['Vector'],n1.inputs['Vector'])
        n2=crk._n(nt,"ShaderNodeTexNoise",-500,-150); n2.inputs['Scale'].default_value=1.3; n2.inputs['Detail'].default_value=2.0; nt.links.new(geo.outputs['Position'],n2.inputs['Vector'])
        r1=crk._n(nt,"ShaderNodeMapRange",-250,100); r1.inputs['From Min'].default_value=0.42; r1.inputs['From Max'].default_value=0.72; r1.inputs['To Min'].default_value=0.03; r1.inputs['To Max'].default_value=0.50; nt.links.new(n1.outputs['Fac'],r1.inputs['Value'])
        r2=crk._n(nt,"ShaderNodeMapRange",-250,-150); r2.inputs['From Min'].default_value=0.40; r2.inputs['From Max'].default_value=0.70; r2.inputs['To Min'].default_value=0.06; r2.inputs['To Max'].default_value=0.16; nt.links.new(n2.outputs['Fac'],r2.inputs['Value'])
        ad=crk._n(nt,"ShaderNodeMath",0,-100); ad.operation='MAXIMUM'; nt.links.new(r1.outputs['Result'],ad.inputs[0]); nt.links.new(r2.outputs['Result'],ad.inputs[1])
        r3=crk._n(nt,"ShaderNodeMath",200,-100); r3.operation='MULTIPLY'; r3.inputs[1].default_value=0.38; nt.links.new(ad.outputs['Value'],r3.inputs[0]); ad=r3          # dirt film, not a curtain
        nt.links.new(r1.outputs['Result'],b.inputs['Roughness']); nt.links.new(ad.outputs['Value'],b.inputs['Alpha'])
        gl.data.materials.clear(); gl.data.materials.append(m)
    for (k,x,z,w,h) in (("form",-3.55,7.12,0.21,0.30),("safety",-2.30,6.98,0.21,0.29),("rules",-0.72,7.22,0.23,0.31),("roster",1.05,7.04,0.21,0.29)):
        wall_quad(c,'+y',-5.99,x,z,w,h,"N_"+k,frame=False,off=0.0015,g=g,paper=False)
        for sx in (-1,1): A.fb((g,"PAPER"),'+y',-5.99,x+sx*w/2-0.014,x+sx*w/2+0.014,z+h/2-0.012,z+h/2+0.014,0.0012,0.0) if False else A.fb((g,"CABLE_B"),'+y',-5.99,x+sx*(w/2-0.012)-0.018,x+sx*(w/2-0.012)+0.018,z+h/2-0.022,z+h/2+0.006,0.0016,0.0)   # masking tape on the top corners
# ---------------------------------------------------------------- 11. wall lettering and floor markings
def markings(c):
    A,M=c.A,c.M; g="marks"
    M["D_STENCIL"]=decal_mat("CR stencil shift",new_image("CR stencil shift",crt.stencil("SHIFT 04  -  CONTROL",1600,220,170,seed=41)),0.9)
    M["D_ARROW"]=decal_mat("CR floor arrow",new_image("CR floor arrow",crt.floor_arrow(text="EXIT")),0.6)
    M["D_OP"]=decal_mat("CR floor operator",new_image("CR floor operator",crt.stencil("OPERATOR",640,120,96,col=(0.86,0.63,0.10),wear=0.55,seed=42)),0.6)
    wall_quad(c,'+y',-11.91,-1.50,8.14,1.60,0.22,"D_STENCIL",frame=False,off=0.0235,g=g,paper=False)
    quad_xy(A,(g,"D_ARROW"),-4.22,-6.88,0.85,0.32,FZ+0.0018,0.0)
    for cx in (-2.75,-1.05,0.65): quad_xy(A,(g,"D_OP"),cx,-8.03,0.50,0.094,FZ+0.0018,0.0)

# ---------------------------------------------------------------- 13. faint haze (beams in the warm pools)
def haze(c):
    coll=c.coll
    me=bpy.data.meshes.new("CR haze volume"); x0,x1,y0,y1,z0,z1=-4.77,1.97,-11.88,-6.19,5.43,8.47
    v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    f=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]; me.from_pydata(v,[],f); me.update()
    o=bpy.data.objects.new("CR haze volume",me); coll.objects.link(o)
    m=crk._new("CR haze"); nt=m.node_tree; out=crk._n(nt,"ShaderNodeOutputMaterial",400,0); pv=crk._n(nt,"ShaderNodeVolumePrincipled",100,0)
    pv.inputs['Color'].default_value=(0.86,0.87,0.88,1); pv.inputs['Density'].default_value=0.016; pv.inputs['Anisotropy'].default_value=0.45
    nt.links.new(pv.outputs['Volume'],out.inputs['Volume']); me.materials.append(m)
    o.visible_shadow=False
# ---------------------------------------------------------------- 14. collision proxies (axis-aligned boxes, engine-side player / physics collision)
PROXIES=[
 ("desk_bay1",-3.60,-1.90,-7.60,-6.40,5.40,6.20),("desk_bay2",-1.90,-0.20,-7.60,-6.40,5.40,6.20),("desk_bay3",-0.20,1.50,-7.60,-6.40,5.40,6.20),
 ("chair_bay1",-3.05,-2.45,-7.72,-7.10,5.40,6.60),("chair_bay2",-1.35,-0.75,-7.72,-7.10,5.40,6.60),("chair_bay3",0.35,0.95,-7.72,-7.10,5.40,6.60),
 ("cot",-4.72,-3.98,-11.86,-10.08,5.40,5.86),("shelving",-4.80,-4.40,-9.90,-8.30,5.40,7.70),("lockers",1.55,2.00,-11.86,-11.02,5.40,7.40),
 ("rack",1.05,1.95,-10.65,-10.05,5.40,7.45),("rack_server_drawer",0.83,1.05,-10.60,-10.10,5.96,6.10),
 ("copier",1.30,2.00,-8.85,-7.95,5.40,6.40),("printer_stand",1.52,2.00,-9.55,-8.97,5.40,6.40),
 ("tv_credenza",-2.37,-0.63,-11.91,-11.43,5.40,6.27),("break_counter",-0.46,0.43,-11.91,-11.32,5.40,6.30),("fridge",0.45,0.93,-11.91,-11.40,5.40,6.50),
 ("work_table",-3.40,-1.80,-10.30,-9.50,5.40,6.22),("work_table_chair",-2.92,-2.28,-9.46,-8.74,5.40,6.60),
 ("door_leaf",-4.74,-3.84,-6.39,-6.33,5.40,7.55),("waste_bin",1.65,1.91,-7.08,-6.82,5.40,5.72),
 ("wall_west_south",-4.83,-4.80,-11.91,-7.26,5.40,8.80),("wall_west_north",-4.83,-4.80,-6.34,-6.16,5.40,8.80),("wall_east",2.00,2.03,-11.91,-6.16,5.40,8.80),
 ("wall_back",-4.80,2.00,-11.94,-11.91,5.40,8.80),("wall_front",-4.80,2.00,-6.16,-6.13,5.40,8.80)]
def collision(c,json_path=None):
    import json,bmesh
    coll=bpy.data.collections.get("32 CR COLLISION")
    if coll:
        for o in list(coll.objects): bpy.data.objects.remove(o,do_unlink=True)
    else:
        coll=bpy.data.collections.new("32 CR COLLISION"); bpy.context.scene.collection.children.link(coll)
    for (n,x0,x1,y0,y1,z0,z1) in PROXIES:
        me=bpy.data.meshes.new("COL "+n); bm=bmesh.new(); bmesh.ops.create_cube(bm,size=1.0)
        for v in bm.verts: v.co=((x0+x1)/2+v.co.x*(x1-x0),(y0+y1)/2+v.co.y*(y1-y0),(z0+z1)/2+v.co.z*(z1-z0))
        bm.to_mesh(me); bm.free(); o=bpy.data.objects.new("COL "+n,me); o.display_type='WIRE'; o.hide_render=True; coll.objects.link(o)
    coll.hide_render=True
    if json_path:
        json.dump({"note":"control-room collision proxies, axis-aligned boxes, Blender world space, metres, Z up; walls are thin boxes with the west door opening left free (y -7.26..-6.34)",
                   "boxes":[{"name":n,"min":[x0,y0,z0],"max":[x1,y1,z1]} for (n,x0,x1,y0,y1,z0,z1) in PROXIES]},open(json_path,"w"),indent=1)
