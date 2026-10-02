"""Lift, anteroom and the passage to the control room (owner brief 2026-10-01).
Old layout: a glazed shaft looking into the reactor hall, a railed catwalk deck and a 0.8 m strip to the control room's west door.  New layout:
  * the shaft is a SOLID enclosed box; its car has two doors: NORTH at ground level (the only opening onto the hall) and EAST at the control-room level;
  * the east door opens into a 2 x 2 m anteroom (water cooler with a blue jug, a loveseat, a potted plant) whose far door is the control room's west door;
  * the anteroom stands on a steel frame with solid skirt panels (control-room floor level, z 5.4); no catwalk, no glass looking into the reactor hall.
Everything the car does is driven by SCENE TIME IN SECONDS (24 s loop: ground, ride up, upper, ride down), never by frames.
Coordinates (m): shaft interior x -8.95..-6.95, y -7.40..-5.40; anteroom interior x -6.83..-4.83, y -7.70..-5.70; floor z 5.4, ceiling z 8.5."""
import bpy,bmesh,math
from mathutils import Vector
import crk,crt
import math
from crk import pm,drv
FZ=5.40; CZ=8.50
SX0,SX1,SY0,SY1=-8.95,-6.95,-7.40,-5.40         # shaft interior
AX0,AX1,AY0,AY1=-6.83,-4.83,-8.95,-5.70         # anteroom interior: 2.0 m wide, 3.25 m deep (back wall pushed 1.25 m south on request: it was 2 x 2 m and cramped)
AXE=-5.00                                       # the control room's west cladding slab (mezzanine CF gunmetal, x -5.0..-4.8) is the anteroom's real east wall face; the dressing is mounted on it
AXW=-7.70                                       # south-west alcove: the couch wall is 0.87 m wider (x -7.70..-6.83, y -8.95..-7.52, tucked south of the shaft)
PERIOD=24.0
CAR_Z=[(0,0),(5,0),(11,5.4),(17,5.4),(23,0),(24,0)]
DG=[(0,1),(4.2,1),(5.0,0),(23.0,0),(23.8,1),(24,1)]            # ground (north) landing door open fraction
DU=[(0,0),(11.0,0),(11.8,1),(16.2,1),(17.0,0),(24,0)]          # upper (east) landing door open fraction
def remove_old():
    """the old shaft, glass front, doors, landing deck and strip, their steel columns/rails and lamps"""
    gone=0
    el=bpy.data.collections.get("21 ELEVATOR")
    if el:
        for o in list(el.all_objects): bpy.data.objects.remove(o,do_unlink=True); gone+=1
    for n in ("LP elevator car lamp","LP elevator shaft lamp","MZ landing deck","MZ landing strip"):
        o=bpy.data.objects.get(n)
        if o: bpy.data.objects.remove(o,do_unlink=True); gone+=1
    for o in list(bpy.data.objects):                                  # elevator call panels / indicators / frame on the old hall-side face, and the floor drain that now sits under the anteroom base
        if o.name.startswith("R2 detail el ") or o.name=="R2 floor drain IRON": bpy.data.objects.remove(o,do_unlink=True); gone+=1
    mz=bpy.data.collections.get("20 CONTROL MEZZANINE")
    if mz:
        for o in list(mz.all_objects):
            if "hall_steel -2_-1_" in o.name or "hall_steel -1_-1_" in o.name: bpy.data.objects.remove(o,do_unlink=True); gone+=1
    print("lift: removed old objects",gone)
def _mover(c,name,fn,parent=None,pivot=None):
    """build one moving object with its own kit; returns the object (named 'CR <name> <mat>' by the kit, joined if the kit made several)"""
    A2=crk.Kit(); fn(A2)
    mats=dict(c.M); objs=A2.build(c.coll,"CR",mats)
    for o in objs:
        o.name=f"CR {name} {o.name.split(' ')[-1]}" if len(objs)>1 else f"CR {name}"
    return objs
def build(c):
    A,M=c.A,c.M; coll=c.coll; R=c.R
    remove_old()
    M["JUG"]=pm("CR jug blue",(0.05,0.24,0.56),0.18,scale=2.0,bump=0.0,var=(0.92,1.05),coat=0.5)
    M["CARWALL"]=pm("CR lift wall panel",(0.30,0.31,0.29),0.40,edge=(0.55,0.55,0.50),scale=2.5,bump=0.0,var=(0.90,1.04),coat=0.1)      # satin painted car walls: a closed metal box with only specular reads black
    M["PLANT"]=pm("CR plant leaf",(0.045,0.16,0.04),0.55,scale=4.0,bump=0.05,var=(0.85,1.10))
    M["TERRA"]=pm("CR terracotta",(0.30,0.12,0.065),0.78,scale=3.0,bump=0.10,var=(0.85,1.08))
    # ---------------------------------------------------------------- control empty with the time-driven schedule
    ctl=bpy.data.objects.new("CR_LIFT",None); ctl.empty_display_type='PLAIN_AXES'; ctl.empty_display_size=0.2; coll.objects.link(ctl)
    ctl["t_s"]=0.0; drv(ctl,'["t_s"]',None,"fmod(T,%.1f)"%PERIOD,var_s=False)
    import cr_tv
    for n_ in ("car_z","dg","du"): ctl[n_]=0.0
    cr_tv.drive_ramp(ctl,"car_z",CAR_Z); cr_tv.drive_ramp(ctl,"dg",DG); cr_tv.drive_ramp(ctl,"du",DU)
    zv=[("z",ctl,'["car_z"]')]
    import cr_ante; cr_ante.lamp_mats(c,ctl)
    # ---------------------------------------------------------------- shaft: solid enclosure, ground door in the north wall, car-level door in the east wall
    g="lift"; T=0.12
    wx0,wx1=SX0-T,SX1+T; wy0,wy1=SY0-T,SY1+T                 # outer faces x -9.07..-6.83, y -7.52..-5.28
    HZ=10.8
    A.bx((g,"WALL_BAND"),wx0,SX0,wy0,wy1,-0.3,HZ,0.004)                                            # west wall
    A.bx((g,"WALL_BAND"),wx0,wx1,wy0,SY0,-0.3,HZ,0.004)                                            # south wall
    A.bx((g,"WALL_BAND"),wx0,-8.55,SY1,wy1,-0.3,HZ,0.004); A.bx((g,"WALL_BAND"),-7.35,wx1,SY1,wy1,-0.3,HZ,0.004)    # north wall around the ground door
    A.bx((g,"WALL_BAND"),-8.55,-7.35,SY1,wy1,2.30,HZ,0.004)                                        # above the ground door
    A.bx((g,"WALL_BAND"),SX1,wx1,wy0,-7.00,-0.3,HZ,0.004); A.bx((g,"WALL_BAND"),SX1,wx1,-5.80,wy1,-0.3,HZ,0.004)  # east wall beside the upper door
    A.bx((g,"WALL_BAND"),SX1,wx1,-7.00,-5.80,-0.3,FZ,0.004); A.bx((g,"WALL_BAND"),SX1,wx1,-7.00,-5.80,7.62,HZ,0.004)   # east wall below / above the upper door
    A.bx((g,"WALL_BAND"),wx0,wx1,wy0,wy1,HZ,HZ+0.15,0.004)                                         # roof
    A.bx((g,"STEEL"),SX0,SX1,SY0,SY1,-0.3,0.0,0.004)                                               # pit floor
    # hall-side dressing of the shaft: olive dado, trim bands, hazard sill and sign
    A.fb((g,"WALL_LO"),'+y',wy1,wx0,-8.55,0.0,1.1,0.012,0.003); A.fb((g,"WALL_LO"),'+y',wy1,-7.35,wx1,0.0,1.1,0.012,0.003)
    A.fb((g,"WALL_LO"),'-x',wx0,wy0,wy1,0.0,1.1,0.012,0.003); A.fb((g,"WALL_LO"),'-y',wy0,wx0,wx1,0.0,1.1,0.012,0.003)
    for zz in (1.1,3.0,FZ-0.35):
        A.fb((g,"TRIM"),'+y',wy1,wx0,wx1,zz,zz+0.05,0.014,0.003); A.fb((g,"TRIM"),'-x',wx0,wy0,wy1,zz,zz+0.05,0.014,0.003)
    A.bx((g,"STEEL"),-8.67,-8.55,SY1,wy1+0.05,0.0,2.36,0.004); A.bx((g,"STEEL"),-7.35,-7.23,SY1,wy1+0.05,0.0,2.36,0.004); A.bx((g,"STEEL"),-8.67,-7.23,SY1,wy1+0.05,2.30,2.42,0.004)   # ground door frame
    A.bx((g,"YELLOW"),-8.67,-7.23,wy1+0.05,wy1+0.30,0.0,0.01,0.0)                                    # hazard sill in front of the door
    for k in range(7): A.bx((g,"BLACK"),-8.64+k*0.2,-8.56+k*0.2,wy1+0.05,wy1+0.30,0.0,0.012,0.0)
    A.fb((g,"BLACK"),'+y',wy1,-8.40,-7.50,2.47,2.78,0.03,0.004)                                      # LIFT sign box
    crk.text(coll,"LIFT",-7.95,wy1+0.032,2.625,'+y',0.15,M["YELLOW"],'CENTER',"CR lift sign")
    A.pillow((g,"BRUSH"),-7.15,-6.97,wy1,wy1+0.016,1.00,1.32,0.004,1); A.cyly((g,"BLACK"),-7.06,wy1+0.016,wy1+0.026,1.22,0.020,16,0.0); A.cyly((g,"LED_AON"),-7.06,wy1+0.026,wy1+0.029,1.22,0.012,14)
    A.cyly((g,"BLACK"),-7.06,wy1+0.016,wy1+0.026,1.10,0.020,16,0.0); A.cyly((g,"LED_AON"),-7.06,wy1+0.026,wy1+0.029,1.10,0.012,14)   # call buttons (up / down)
    # machine room at the top of the shaft: sheave, traction motor, beams (static)
    A.cylx((g,"STEEL"),-8.45,-7.55,-6.72,9.60,0.47,28,0.005); A.cylx((g,"STEEL_L"),-8.55,-7.45,-6.72,9.60,0.07,12)
    A.bx((g,"STEEL"),-7.50,-6.98,-7.20,-6.20,9.20,10.0,0.01); A.cylx((g,"BLACK"),-7.50,-7.20,-6.70,9.60,0.17,16)
    A.bx((g,"STEEL"),SX0,SX1,-7.25,-7.05,8.85,9.05,0.004); A.bx((g,"STEEL"),SX0,SX1,-6.40,-6.20,8.85,9.05,0.004)
    A.bx((g,"STEEL_L"),-8.81,-8.75,-6.55,-6.25,0.0,HZ-0.2,0.003); A.bx((g,"STEEL_L"),-8.20,-7.90,-7.28,-7.22,0.0,HZ-0.2,0.003)   # car guide rails on the two WALL sides (the north and east sides are doorways)
    for x in (-8.30,-7.60): A.bx((g,"STEEL_L"),x-0.025,x+0.025,-7.33,-7.27,0.0,HZ-0.2,0.003)         # counterweight rails
    A.bx((g,"STEEL"),-8.78,-8.70,-6.58,-6.22,-0.0,0.12,0.004)                                         # buffer (west side only, so the east doorway stays clear)
    # ---------------------------------------------------------------- anteroom base: steel frame with solid skirt panels
    g="ante"; bx0,bx1,by0,by1=SX1+0.12,-4.80,AY0-0.12,AY1+0.12       # outer block x -6.83..-4.80, y -8.95-0.12..-5.58
    ax0=AXW-0.12; yn=wy0                                                # alcove outer west face x -7.82; its north boundary is the shaft's south face y -7.52
    A.bx((g,"WALL_BAND"),ax0,bx1,by0,AY0,0.0,FZ-0.2,0.004); A.bx((g,"WALL_BAND"),bx0,bx1,AY1,by1,0.0,FZ-0.2,0.004)   # south (spans the alcove) / north skirt panels
    A.bx((g,"WALL_BAND"),ax0,AXW,AY0,yn,0.0,FZ-0.2,0.004)                                            # alcove west skirt panel
    A.bx((g,"WALL_BAND"),bx1-0.10,bx1,AY0,AY1,0.0,FZ-0.2,0.004)                                      # east end panel (under the control room wall)
    for (xa,xb,ya,yb) in ((ax0,ax0+0.20,by0,by0+0.20),(ax0,ax0+0.20,yn-0.20,yn),(bx0,bx0+0.20,by1-0.20,by1),(bx1-0.20,bx1,by0,by0+0.20),(bx1-0.20,bx1,by1-0.20,by1)):
        A.bx((g,"STEEL"),xa,xb,ya,yb,0.0,FZ-0.2,0.004)                                                  # corner posts
    for zz in (0.9,2.6,FZ-0.55):
        A.fb((g,"TRIM"),'+y',by1,bx0,bx1,zz,zz+0.05,0.012,0.003); A.fb((g,"TRIM"),'-y',by0,ax0,bx1,zz,zz+0.05,0.012,0.003); A.fb((g,"TRIM"),'-x',ax0,by0,yn,zz,zz+0.05,0.012,0.003)
    A.bx((g,"YELLOW"),bx0,bx1,by1,by1+0.012,0.0,0.18,0.0)
    A.bx((g,"WALL_BAND"),ax0,AXW,by0,yn,FZ-0.2,CZ+0.10,0.004)                                         # alcove west wall (full height)
    A.bx((g,"STEEL"),bx0,bx1,by0,by1,FZ-0.2,FZ-0.02,0.004); A.bx((g,"STEEL"),ax0,bx0,by0,yn,FZ-0.2,FZ-0.02,0.004)   # floor slab (+ alcove)
    A.bx((g,"FLOOR"),AX0,AX1,AY0,AY1,FZ-0.02,FZ,0.0); A.bx((g,"FLOOR"),AXW,AX0,AY0,yn,FZ-0.02,FZ,0.0)               # floor finish (control-room tile)
    # walls: north, south (plaster with an olive dado, spans the alcove), alcove west + north (the shaft's south face), shaft east face, control room west wall
    A.bx((g,"WALL_HI"),bx0,bx1,AY1,by1,FZ,CZ,0.003); A.bx((g,"WALL_HI"),ax0,bx1,by0,AY0,FZ,CZ,0.003)
    A.fb((g,"WALL_LO"),'-y',AY1,AX0,AX1,FZ,FZ+1.05,0.012,0.003); A.fb((g,"WALL_LO"),'+y',AY0,AXW,AX1,FZ,FZ+1.05,0.012,0.003)
    A.fb((g,"TRIM"),'-y',AY1,AX0,AX1,FZ+1.05,FZ+1.10,0.014,0.003); A.fb((g,"TRIM"),'+y',AY0,AXW,AX1,FZ+1.05,FZ+1.10,0.014,0.003)
    A.fb((g,"WALL_HI"),'+x',AXW,AY0,yn,FZ,CZ,0.02,0.003); A.fb((g,"WALL_LO"),'+x',AXW+0.02,AY0,yn,FZ,FZ+1.05,0.012,0.003); A.fb((g,"TRIM"),'+x',AXW+0.02,AY0,yn,FZ+1.05,FZ+1.10,0.014,0.003)
    A.fb((g,"WALL_HI"),'-y',yn,AXW,AX0,FZ,CZ,0.02,0.003); A.fb((g,"WALL_LO"),'-y',yn-0.02,AXW,AX0,FZ,FZ+1.05,0.012,0.003); A.fb((g,"TRIM"),'-y',yn-0.02,AXW,AX0,FZ+1.05,FZ+1.10,0.014,0.003)
    A.fb((g,"WALL_HI"),'+x',AX0,yn,-7.00,FZ,CZ,0.02,0.003); A.fb((g,"WALL_HI"),'+x',AX0,-5.80,AY1,FZ,CZ,0.02,0.003); A.fb((g,"WALL_HI"),'+x',AX0,-7.00,-5.80,7.62,CZ,0.02,0.003)
    A.fb((g,"WALL_LO"),'+x',AX0+0.02,yn,-7.00,FZ,FZ+1.05,0.012,0.003); A.fb((g,"WALL_LO"),'+x',AX0+0.02,-5.80,AY1,FZ,FZ+1.05,0.012,0.003)
    A.fb((g,"WALL_HI"),'-x',AXE,AY0,-7.34,FZ,CZ,0.02,0.003); A.fb((g,"WALL_HI"),'-x',AXE,-6.26,AY1,FZ,CZ,0.02,0.003); A.fb((g,"WALL_HI"),'-x',AXE,-7.34,-6.26,7.64,CZ,0.02,0.003)
    A.fb((g,"WALL_LO"),'-x',AXE,AY0,-7.34,FZ,FZ+1.05,0.012,0.003); A.fb((g,"WALL_LO"),'-x',AXE,-6.26,AY1,FZ,FZ+1.05,0.012,0.003)
    cr_ante.trim(c,wy0)
    # lift door frame (anteroom side) and skirting
    A.bx((g,"STEEL"),AX0,AX0+0.05,-7.10,-7.00,FZ,7.70,0.003); A.bx((g,"STEEL"),AX0,AX0+0.05,-5.80,-5.70,FZ,7.70,0.003); A.bx((g,"STEEL"),AX0,AX0+0.05,-7.10,-5.70,7.62,7.72,0.003)
    A.bx((g,"STEEL"),AX0,AX0+0.06,-7.00,-5.80,FZ,FZ+0.012,0.002)                                      # lift sill
    A.fb((g,"BLACK"),'+x',AX0,-7.30,-7.16,6.45,6.80,0.022,0.004); A.fb((g,"LED_AON"),'+x',AX0+0.022,-7.27,-7.19,6.58,6.67,0.004,0.0) # call button
    # control-room door side: sign above the doorway
    A.fb((g,"BLACK"),'-x',AXE,-7.30,-6.30,7.74,8.06,0.03,0.004)
    crk.text(coll,"CONTROL ROOM",AXE-0.032,-6.80,7.90,'-x',0.085,M["YELLOW"],'CENTER',"CR control sign")
    A.fb((g,"YELLOW"),'-x',AXE,-7.26,-6.34,FZ,FZ+0.012,0.012,0.0)                                      # threshold strip
    # ceiling, grid and lamp
    A.bx((g,"CEIL"),AX0,AX1,AY0,AY1,CZ-0.02,CZ,0.0); A.bx((g,"CEIL"),AXW,AX0,AY0,wy0,CZ-0.02,CZ,0.0)
    A.bx((g,"CEIL_GRID"),AXW,AX1,AY0,AY0+0.03,CZ-0.03,CZ,0.002); A.bx((g,"CEIL_GRID"),AX0,AX1,AY1-0.03,AY1,CZ-0.03,CZ,0.002)
    A.bx((g,"CEIL_GRID"),AXW,AXW+0.03,AY0,wy0,CZ-0.03,CZ,0.002); A.bx((g,"CEIL_GRID"),AX1-0.03,AX1,AY0,AY1,CZ-0.03,CZ,0.002)
    A.bx((g,"CEIL_GRID"),AXW,AX0,wy0-0.03,wy0,CZ-0.03,CZ,0.002); A.bx((g,"CEIL_GRID"),AX0,AX0+0.03,wy0,AY1,CZ-0.03,CZ,0.002)
    A.bx((g,"CEIL_GRID"),-5.83-0.012,-5.83+0.012,AY0,AY1,CZ-0.03,CZ,0.002); A.bx((g,"CEIL_GRID"),AXW,AX0,-8.23,-8.21,CZ-0.03,CZ,0.002)
    A.bx((g,"STEEL"),bx0,bx1,by0,by1,CZ,CZ+0.10,0.004); A.bx((g,"STEEL"),ax0,bx0,by0,yn,CZ,CZ+0.10,0.004)
    lx,ly=-6.30,-7.70
    A.bx((g,"CEIL_GRID"),lx-0.33,lx+0.33,ly-0.17,ly+0.17,CZ-0.045,CZ,0.004); A.bx((g,"LAMPFACE"),lx-0.30,lx+0.30,ly-0.14,ly+0.14,CZ-0.05,CZ-0.045,0.0)
    crk.light(coll,"CR anteroom lamp",(lx,ly,CZ-0.10),(1.0,0.70,0.42),34,'AREA',(0,0,0),size=(0.60,0.28))
    # ---------------------------------------------------------------- props and floor indicators (cr_ante.py)
    cr_ante.props(c); cr_ante.indicators(c,ctl)
    # ---------------------------------------------------------------- moving parts (car, doors, counterweight, ropes), driven by CR_LIFT in seconds
    car=bpy.data.objects.new("CR lift car",None); car.empty_display_type='PLAIN_AXES'; car.empty_display_size=0.2; coll.objects.link(car)
    drv(car,'location',2,"z",var_s=False,extra=zv)
    def mkcar(K):
        g="lift_car"; x0,x1,y0,y1=-8.70,-7.20,-7.15,-5.65
        K.bx((g,"RUBBER"),x0,x1,y0,y1,0.0,0.08,0.006)
        K.bx((g,"CARWALL"),x0,x0+0.07,y0,y1,0.08,2.40,0.004); K.bx((g,"CARWALL"),x0,x1,y0,y0+0.07,0.08,2.40,0.004)                 # west + south walls
        K.bx((g,"STEEL"),x0+0.07,x1-0.07,y0+0.07,y0+0.09,0.60,0.64,0.002); K.bx((g,"STEEL"),x0+0.07,x0+0.09,y0+0.07,y1-0.07,0.60,0.64,0.002)   # wainscot rails
        for (xa,ya) in ((x0,y1-0.10),(x1-0.10,y1-0.10),(x1-0.10,y0)): K.bx((g,"TRIM"),xa,xa+0.10,ya,ya+0.10,0.08,2.40,0.004)        # corner posts (north + east sides are the doorways)
        K.bx((g,"TRIM"),x0,x1,y1-0.10,y1,2.28,2.40,0.004); K.bx((g,"TRIM"),x1-0.10,x1,y0,y1,2.28,2.40,0.004)                          # door lintels
        K.bx((g,"CARWALL"),x0,x1,y0,y1,2.40,2.48,0.004)                                                                              # roof
        K.bx((g,"CEIL_GRID"),-8.25,-7.65,-6.75,-6.45,2.36,2.40,0.004); K.bx((g,"CAB_LIGHT"),-8.22,-7.68,-6.72,-6.48,2.355,2.36,0.0)  # cabin light (flickers)
        # round handrails on small brackets (west wall full length; south wall stops short of the control panel)
        for (ya,yb,xx) in ((y0+0.25,y1-0.25,x0+0.07+0.045),):
            K.prism((g,"BRUSH"),(xx,ya,0.97),(xx,yb,0.97),0.0125,0.0125,14,0.0,True,0.0)
            for yy in (ya+0.02,(ya+yb)/2,yb-0.02): K.bx((g,"BRUSH"),x0+0.07,xx,yy-0.012,yy+0.012,0.955,0.985,0.003)
        K.prism((g,"BRUSH"),(x0+0.25,y0+0.07+0.045,0.97),(-7.66,y0+0.07+0.045,0.97),0.0125,0.0125,14,0.0,True,0.0)
        for xx in (x0+0.27,-7.68): K.bx((g,"BRUSH"),xx-0.012,xx+0.012,y0+0.07,y0+0.07+0.045,0.955,0.985,0.003)
        # brushed kick plates, ribbed rubber floor with a steel border, threshold nosings, ceiling frame with vents / speaker
        K.bx((g,"BRUSH"),x0+0.07,x0+0.077,y0+0.07,y1-0.10,0.09,0.58,0.002); K.bx((g,"BRUSH"),x0+0.07,x1-0.10,y0+0.07,y0+0.077,0.09,0.58,0.002)
        K.bx((g,"STEEL"),x0+0.07,x1-0.07,y0+0.07,y1-0.07,0.078,0.086,0.002)
        for k in range(15): K.bx((g,"RUBBER"),x0+0.10+k*0.0925,x0+0.10+k*0.0925+0.035,y0+0.10,y1-0.10,0.086,0.096,0.0015)
        K.bx((g,"BRUSH"),x0,x1,y1-0.02,y1,0.075,0.09,0.002); K.bx((g,"BRUSH"),x1-0.02,x1,y0,y1,0.075,0.09,0.002)
        for k in range(5): K.bx((g,"BLACK"),-8.50+k*0.05,-8.50+k*0.05+0.025,-5.95,-5.78,2.395,2.402,0.0005)                                 # ceiling vent slots
        K.lathe((g,"BRUSH"),-7.50,-6.12,[(0.052,2.40),(0.052,2.386),(0.046,2.384),(0.0,2.384)],seg=18)
        for k in range(3): K.cyl((g,"BLACK"),-7.50+0.022*math.cos(k*2.094),-6.12+0.022*math.sin(k*2.094),2.384,2.387,0.006,6)                    # speaker grille holes
        K.bx((g,"BRUSH"),-8.29,-7.61,-6.79,-6.41,2.396,2.403,0.002)                                                                                # cabin light frame
        K.bx((g,"YELLOW"),x0+0.07,x1-0.10,y1-0.10,y1,0.08,0.09,0.0)                                                                   # sill marking
        K.bx((g,"STEEL"),x0+0.4,x1-0.4,y0+0.08,y0+0.095,1.5,1.62,0.002)                                                               # rear panel plate
    cobjs=_mover(c,"lift_car",mkcar)
    for o in cobjs: o.parent=car
    cr_ante.car_interior(c,ctl,car,zv,_mover)
    # counterweight and ropes (z = 7.1 - car z)
    cw=bpy.data.objects.new("CR lift cw",None); cw.empty_display_type='PLAIN_AXES'; cw.empty_display_size=0.2; coll.objects.link(cw); drv(cw,'location',2,"-z",var_s=False,extra=zv)
    def mkcw(K):
        g="lift_cw"; K.bx((g,"STEEL"),-8.40,-7.50,-7.24,-7.12,7.10,9.00,0.006)
        for k in range(8): K.bx((g,"STEEL_L"),-8.36,-7.54,-7.255,-7.24,7.18+k*0.22,7.24+k*0.22,0.002)
    for o in _mover(c,"lift_cw",mkcw): o.parent=cw
    def rope(name,x,y,top,expr_len):
        K=crk.Kit(); K.bx(("lift_rope","STEEL"),x-0.008,x+0.008,y-0.008,y+0.008,top-1.0,top,0.0)
        o=K.build(coll,"CR",dict(M))[0]; o.name=name
        o.data.transform(__import__("mathutils").Matrix.Translation((0,0,-top))); o.location=(0,0,top)
        drv(o,'scale',2,expr_len,var_s=False,extra=zv); return o
    for x in (-8.05,-7.85): rope("CR lift rope car %.2f"%x,x,-6.25,9.60,"7.12-z")
    for x in (-8.05,-7.85): rope("CR lift rope cw %.2f"%x,x,-7.18,9.60,"0.6+z")
    # landing door leaves: north (ground) slides along x, east (upper) slides along y; each opens with its schedule fraction
    def leaf(name,x0,x1,y0,y1,z0,z1,axis,sign,prop):
        def fn(K):
            g=name.replace(" ","_"); K.bx((g,"STEEL_L"),x0,x1,y0,y1,z0,z1,0.004); K.bx((g,"STEEL"),x0,x1,y0,y1,z0+0.55,z0+0.60,0.002)
            for k in range(4):                                                                                             # vertical grooves + a brushed centre plate
                f=(k+1)/5
                if axis==0: K.bx((g,"BLACK"),x0+(x1-x0)*f-0.004,x0+(x1-x0)*f+0.004,y0-0.003,y1+0.003,z0+0.62,z1-0.32,0.0005)
                else: K.bx((g,"BLACK"),x0-0.003,x1+0.003,y0+(y1-y0)*f-0.004,y0+(y1-y0)*f+0.004,z0+0.62,z1-0.32,0.0005)
            K.bx((g,"STEEL"),x0,x1,y0,y1,z1-0.30,z1-0.25,0.002); K.bx((g,"YELLOW"),x0+0.01,x1-0.01,y0,y1,z0,z0+0.08,0.001) if axis==0 else K.bx((g,"YELLOW"),x0,x1,y0+0.01,y1-0.01,z0,z0+0.08,0.001)
        o=_mover(c,name,fn)
        for ob in o: drv(ob,'location',axis,"%+.2f*d"%(sign*0.50),var_s=False,extra=[("d",ctl,'["%s"]'%prop)])
    wy1_=SY1+0.12
    leaf("lift_dgL",-8.55,-7.95,wy1_,wy1_+0.05,0.02,2.26,0,-1,"dg"); leaf("lift_dgR",-7.95,-7.35,wy1_,wy1_+0.05,0.02,2.26,0,+1,"dg")
    leaf("lift_duL",AX0,AX0+0.05,-7.00,-6.40,FZ+0.02,7.60,1,-1,"du"); leaf("lift_duR",AX0,AX0+0.05,-6.40,-5.80,FZ+0.02,7.60,1,+1,"du")
    print("lift: built shaft, anteroom, props, car, doors")
