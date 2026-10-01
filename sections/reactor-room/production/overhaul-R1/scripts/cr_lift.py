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
from crk import pm,drv
FZ=5.40; CZ=8.50
SX0,SX1,SY0,SY1=-8.95,-6.95,-7.40,-5.40         # shaft interior
AX0,AX1,AY0,AY1=-6.83,-4.83,-7.70,-5.70         # anteroom interior
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
    M["JUG"]=pm("CR jug blue",(0.045,0.17,0.40),0.22,scale=2.0,bump=0.0,var=(0.92,1.05),coat=0.4)
    M["PLANT"]=pm("CR plant leaf",(0.045,0.16,0.04),0.55,scale=4.0,bump=0.05,var=(0.85,1.10))
    M["TERRA"]=pm("CR terracotta",(0.30,0.12,0.065),0.78,scale=3.0,bump=0.10,var=(0.85,1.08))
    # ---------------------------------------------------------------- control empty with the time-driven schedule
    ctl=bpy.data.objects.new("CR_LIFT",None); ctl.empty_display_type='PLAIN_AXES'; ctl.empty_display_size=0.2; coll.objects.link(ctl)
    ctl["t_s"]=0.0; drv(ctl,'["t_s"]',None,"fmod(T,%.1f)"%PERIOD,var_s=False)
    import cr_tv
    for n_ in ("car_z","dg","du"): ctl[n_]=0.0
    cr_tv.drive_ramp(ctl,"car_z",CAR_Z); cr_tv.drive_ramp(ctl,"dg",DG); cr_tv.drive_ramp(ctl,"du",DU)
    zv=[("z",ctl,'["car_z"]')]
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
    A.fb((g,"BLACK"),'+y',wy1,-7.12,-7.00,1.05,1.30,0.02,0.004); A.fb((g,"LED_AON"),'+y',wy1+0.02,-7.10,-7.02,1.14,1.20,0.004,0.0)   # call button
    # machine room at the top of the shaft: sheave, traction motor, beams (static)
    A.cylx((g,"STEEL"),-8.45,-7.55,-6.72,9.60,0.47,28,0.005); A.cylx((g,"STEEL_L"),-8.55,-7.45,-6.72,9.60,0.07,12)
    A.bx((g,"STEEL"),-7.50,-6.98,-7.20,-6.20,9.20,10.0,0.01); A.cylx((g,"BLACK"),-7.50,-7.20,-6.70,9.60,0.17,16)
    A.bx((g,"STEEL"),SX0,SX1,-7.25,-7.05,8.85,9.05,0.004); A.bx((g,"STEEL"),SX0,SX1,-6.40,-6.20,8.85,9.05,0.004)
    A.bx((g,"STEEL_L"),-8.81,-8.75,-6.55,-6.25,0.0,HZ-0.2,0.003); A.bx((g,"STEEL_L"),-8.20,-7.90,-7.28,-7.22,0.0,HZ-0.2,0.003)   # car guide rails on the two WALL sides (the north and east sides are doorways)
    for x in (-8.30,-7.60): A.bx((g,"STEEL_L"),x-0.025,x+0.025,-7.33,-7.27,0.0,HZ-0.2,0.003)         # counterweight rails
    A.bx((g,"STEEL"),-8.78,-8.70,-6.58,-6.22,-0.0,0.12,0.004)                                         # buffer (west side only, so the east doorway stays clear)
    # ---------------------------------------------------------------- anteroom base: steel frame with solid skirt panels
    g="ante"; bx0,bx1,by0,by1=SX1+0.12,-4.80,AY0-0.12,AY1+0.12       # outer block x -6.83..-4.80, y -7.82..-5.58
    A.bx((g,"WALL_BAND"),bx0,bx1,by0,AY0,0.0,FZ-0.2,0.004); A.bx((g,"WALL_BAND"),bx0,bx1,AY1,by1,0.0,FZ-0.2,0.004)   # north / south skirt panels
    A.bx((g,"WALL_BAND"),bx1-0.10,bx1,AY0,AY1,0.0,FZ-0.2,0.004)                                      # east end panel (under the control room wall)
    for (x,y0_,y1_) in ((bx0,by0,by0+0.20),(bx0,by1-0.20,by1),(bx1-0.20,by0,by0+0.20),(bx1-0.20,by1-0.20,by1)):
        A.bx((g,"STEEL"),x if x==bx0 else x,x+0.20,y0_,y1_,0.0,FZ-0.2,0.004)                         # corner posts
    for zz in (0.9,2.6,FZ-0.55):
        A.fb((g,"TRIM"),'+y',by1,bx0,bx1,zz,zz+0.05,0.012,0.003); A.fb((g,"TRIM"),'-y',by0,bx0,bx1,zz,zz+0.05,0.012,0.003)
    A.bx((g,"YELLOW"),bx0,bx1,by1,by1+0.012,0.0,0.18,0.0)
    A.bx((g,"STEEL"),bx0,bx1,by0,by1,FZ-0.2,FZ-0.02,0.004)                                           # floor slab
    A.bx((g,"FLOOR"),AX0,AX1,AY0,AY1,FZ-0.02,FZ,0.0)                                                 # floor finish (control-room tile)
    # walls: north, south (plaster with an olive dado), west (the shaft's east face), east (the control room's west wall)
    A.bx((g,"WALL_HI"),bx0,bx1,AY1,by1-0.0,FZ,CZ,0.003); A.bx((g,"WALL_HI"),bx0,bx1,by0,AY0,FZ,CZ,0.003)
    A.fb((g,"WALL_LO"),'-y',AY1,AX0,AX1,FZ,FZ+1.05,0.012,0.003); A.fb((g,"WALL_LO"),'+y',AY0,AX0,AX1,FZ,FZ+1.05,0.012,0.003)
    A.fb((g,"TRIM"),'-y',AY1,AX0,AX1,FZ+1.05,FZ+1.10,0.014,0.003); A.fb((g,"TRIM"),'+y',AY0,AX0,AX1,FZ+1.05,FZ+1.10,0.014,0.003)
    A.fb((g,"WALL_HI"),'+x',AX0,AY0,-7.00,FZ,CZ,0.02,0.003); A.fb((g,"WALL_HI"),'+x',AX0,-5.80,AY1,FZ,CZ,0.02,0.003); A.fb((g,"WALL_HI"),'+x',AX0,-7.00,-5.80,7.62,CZ,0.02,0.003)
    A.fb((g,"WALL_LO"),'+x',AX0+0.02,AY0,-7.00,FZ,FZ+1.05,0.012,0.003); A.fb((g,"WALL_LO"),'+x',AX0+0.02,-5.80,AY1,FZ,FZ+1.05,0.012,0.003)
    A.fb((g,"WALL_HI"),'-x',AX1,AY0,-7.34,FZ,CZ,0.02,0.003); A.fb((g,"WALL_HI"),'-x',AX1,-6.26,AY1,FZ,CZ,0.02,0.003); A.fb((g,"WALL_HI"),'-x',AX1,-7.34,-6.26,7.64,CZ,0.02,0.003)
    A.fb((g,"WALL_LO"),'-x',AX1,AY0,-7.34,FZ,FZ+1.05,0.012,0.003); A.fb((g,"WALL_LO"),'-x',AX1,-6.26,AY1,FZ,FZ+1.05,0.012,0.003)
    # lift door frame (anteroom side) and skirting
    A.bx((g,"STEEL"),AX0,AX0+0.05,-7.10,-7.00,FZ,7.70,0.003); A.bx((g,"STEEL"),AX0,AX0+0.05,-5.80,-5.70,FZ,7.70,0.003); A.bx((g,"STEEL"),AX0,AX0+0.05,-7.10,-5.70,7.62,7.72,0.003)
    A.bx((g,"STEEL"),AX0,AX0+0.06,-7.00,-5.80,FZ,FZ+0.012,0.002)                                      # lift sill
    A.fb((g,"BLACK"),'+x',AX0,-6.62,-6.18,7.80,7.98,0.022,0.004); A.fb((g,"LED_ON"),'+x',AX0+0.022,-6.50,-6.30,7.86,7.92,0.004,0.0)   # floor indicator over the lift door
    A.fb((g,"BLACK"),'+x',AX0,-7.30,-7.16,6.45,6.80,0.022,0.004); A.fb((g,"LED_AON"),'+x',AX0+0.022,-7.27,-7.19,6.58,6.67,0.004,0.0) # call button
    # control-room door side: sign above the doorway
    A.fb((g,"BLACK"),'-x',AX1,-7.30,-6.30,7.74,8.06,0.03,0.004)
    crk.text(coll,"CONTROL ROOM",AX1-0.032,-6.80,7.90,'-x',0.085,M["YELLOW"],'CENTER',"CR control sign")
    A.fb((g,"YELLOW"),'-x',AX1,-7.26,-6.34,FZ,FZ+0.012,0.012,0.0)                                      # threshold strip
    # ceiling, grid and lamp
    A.bx((g,"CEIL"),AX0,AX1,AY0,AY1,CZ-0.02,CZ,0.0); A.bx((g,"CEIL_GRID"),AX0,AX1,AY0,AY0+0.03,CZ-0.03,CZ,0.002); A.bx((g,"CEIL_GRID"),AX0,AX1,AY1-0.03,AY1,CZ-0.03,CZ,0.002)
    A.bx((g,"CEIL_GRID"),AX0,AX0+0.03,AY0,AY1,CZ-0.03,CZ,0.002); A.bx((g,"CEIL_GRID"),AX1-0.03,AX1,AY0,AY1,CZ-0.03,CZ,0.002); A.bx((g,"CEIL_GRID"),-5.83-0.012,-5.83+0.012,AY0,AY1,CZ-0.03,CZ,0.002)
    A.bx((g,"STEEL"),bx0,bx1,by0,by1,CZ,CZ+0.10,0.004)
    lx,ly=-5.83,-6.70
    A.bx((g,"CEIL_GRID"),lx-0.31,lx+0.31,ly-0.16,ly+0.16,CZ-0.045,CZ,0.004); A.bx((g,"LAMPFACE"),lx-0.28,lx+0.28,ly-0.13,ly+0.13,CZ-0.05,CZ-0.045,0.0)
    crk.light(coll,"CR anteroom lamp",(lx,ly,CZ-0.10),(1.0,0.68,0.38),16,'AREA',(0,0,0),size=(0.56,0.26))
    # ---------------------------------------------------------------- props
    g="anteprop"
    # water cooler on the north wall: white cabinet, drip tray, taps, blue jug, cup dispenser
    cx0,cx1,cy0,cy1=-6.28,-5.94,-6.08,AY1
    A.bx((g,"PORC"),cx0,cx1,cy0,cy1,FZ+0.05,FZ+1.15,0.012); A.bx((g,"BLACK"),cx0+0.02,cx1-0.02,cy0+0.01,cy1-0.02,FZ,FZ+0.05,0.004)
    A.bx((g,"PORC_O"),cx0-0.003,cx1+0.003,cy0-0.004,cy0+0.012,FZ+1.00,FZ+1.15,0.004)                 # top shoulder
    A.bx((g,"GREY"),cx0+0.04,cx1-0.04,cy0-0.045,cy0+0.004,FZ+0.52,FZ+0.57,0.005)                       # drip tray
    A.bx((g,"BLACK"),cx0+0.05,cx1-0.05,cy0-0.004,cy0+0.004,FZ+0.58,FZ+0.84,0.003)                      # tap panel
    A.bx((g,"JUG"),cx0+0.08,cx0+0.14,cy0-0.022,cy0-0.004,FZ+0.74,FZ+0.79,0.004); A.bx((g,"RED"),cx1-0.14,cx1-0.08,cy0-0.022,cy0-0.004,FZ+0.74,FZ+0.79,0.004)   # cold / hot taps
    A.cyl((g,"JUG"),(cx0+cx1)/2,(cy0+cy1)/2,FZ+1.15,FZ+1.60,0.135,28,0.006); A.cyl((g,"JUG"),(cx0+cx1)/2,(cy0+cy1)/2,FZ+1.60,FZ+1.67,0.060,18,0.004)   # 19 l jug + neck
    A.cyl((g,"PORC"),(cx0+cx1)/2,(cy0+cy1)/2,FZ+1.67,FZ+1.70,0.075,18,0.003)                          # cap
    A.cyl((g,"PORC"),cx1+0.045,cy1-0.075,FZ+0.55,FZ+1.05,0.035,16,0.003)                              # paper-cup tube on the side
    for k in range(4): A.cyl((g,"PORC_O"),cx1+0.045,cy1-0.075,FZ+0.55+k*0.12,FZ+0.58+k*0.12,0.032,16,0.0)
    # loveseat on the south wall: base, cushions, back, arms, legs
    sx0,sx1,sy0,sy1=-6.60,-5.45,AY0,AY0+0.78
    A.bx((g,"BLACK"),sx0,sx1,sy0+0.02,sy1-0.02,FZ+0.09,FZ+0.30,0.012)
    for xa,xb in ((sx0+0.10,(sx0+sx1)/2-0.005),((sx0+sx1)/2+0.005,sx1-0.10)): A.bx((g,"FABRIC"),xa,xb,sy0+0.18,sy1-0.03,FZ+0.30,FZ+0.46,0.03)   # seat cushions
    A.bx((g,"FABRIC"),sx0+0.10,sx1-0.10,sy0+0.03,sy0+0.26,FZ+0.46,FZ+0.92,0.04)                                                                   # back
    for xa,xb in ((sx0,sx0+0.10),(sx1-0.10,sx1)): A.bx((g,"FABRIC"),xa,xb,sy0+0.03,sy1-0.03,FZ+0.30,FZ+0.66,0.03)                               # arms
    for (x,y) in ((sx0+0.06,sy0+0.06),(sx1-0.06,sy0+0.06),(sx0+0.06,sy1-0.06),(sx1-0.06,sy1-0.06)): A.cyl((g,"BLACK"),x,y,FZ,FZ+0.09,0.022,10)
    A.bx((g,"FABRIC_O"),sx0+0.14,sx0+0.50,sy0+0.26,sy0+0.34,FZ+0.46,FZ+0.80,0.02)                                                                # orange throw cushion
    # potted plant in the north-east corner: terracotta pot, soil, stems, leaves
    px,py=-5.22,-6.02
    A.prism((g,"TERRA"),(px,py,FZ),(px,py,FZ+0.36),0.15,0.21,22,0.0,True,0.004); A.cyl((g,"SOIL"),px,py,FZ+0.36,FZ+0.385,0.185,20)
    for k in range(9):
        a=k*2*math.pi/9+0.3; ca,sa=math.cos(a),math.sin(a); nx,ny=-sa,ca; h=0.42+0.20*((k*7)%3)/2
        top=(px+0.17*ca,py+0.17*sa,FZ+0.38+h)
        A.tube((g,"PLANT"),[(px+0.02*ca,py+0.02*sa,FZ+0.38),(px+0.08*ca,py+0.08*sa,FZ+0.38+h*0.6),top],0.006,6)
        L=0.30; d=(0.80*ca,0.80*sa,0.35)                                                  # leaf direction: outward and slightly up
        pts=[top,(top[0]+0.15*L*d[0]*1.2+0.025*nx,top[1]+0.15*L*d[1]*1.2+0.025*ny,top[2]+0.15*L*d[2]),(top[0]+0.15*L*d[0]*1.2-0.025*nx,top[1]+0.15*L*d[1]*1.2-0.025*ny,top[2]+0.15*L*d[2]),
             (top[0]+0.5*L*d[0]*1.2+0.075*nx,top[1]+0.5*L*d[1]*1.2+0.075*ny,top[2]+0.5*L*d[2]+0.01),(top[0]+0.5*L*d[0]*1.2-0.075*nx,top[1]+0.5*L*d[1]*1.2-0.075*ny,top[2]+0.5*L*d[2]+0.01),
             (top[0]+L*d[0]*1.2,top[1]+L*d[1]*1.2,top[2]+L*d[2]-0.05)]
        A.hull((g,"PLANT"),pts,0.002)
    # ---------------------------------------------------------------- moving parts (car, doors, counterweight, ropes), driven by CR_LIFT in seconds
    car=bpy.data.objects.new("CR lift car",None); car.empty_display_type='PLAIN_AXES'; car.empty_display_size=0.2; coll.objects.link(car)
    drv(car,'location',2,"z",var_s=False,extra=zv)
    def mkcar(K):
        g="lift_car"; x0,x1,y0,y1=-8.70,-7.20,-7.15,-5.65
        K.bx((g,"RUBBER"),x0,x1,y0,y1,0.0,0.08,0.006)
        K.bx((g,"STEEL_L"),x0,x0+0.07,y0,y1,0.08,2.40,0.004); K.bx((g,"STEEL_L"),x0,x1,y0,y0+0.07,0.08,2.40,0.004)                 # west + south walls
        K.bx((g,"STEEL"),x0+0.07,x1-0.07,y0+0.07,y0+0.09,0.60,0.64,0.002); K.bx((g,"STEEL"),x0+0.07,x0+0.09,y0+0.07,y1-0.07,0.60,0.64,0.002)   # wainscot rails
        for (xa,ya) in ((x0,y1-0.10),(x1-0.10,y1-0.10),(x1-0.10,y0)): K.bx((g,"TRIM"),xa,xa+0.10,ya,ya+0.10,0.08,2.40,0.004)        # corner posts (north + east sides are the doorways)
        K.bx((g,"TRIM"),x0,x1,y1-0.10,y1,2.28,2.40,0.004); K.bx((g,"TRIM"),x1-0.10,x1,y0,y1,2.28,2.40,0.004)                          # door lintels
        K.bx((g,"STEEL_L"),x0,x1,y0,y1,2.40,2.48,0.004)                                                                              # roof
        K.bx((g,"CEIL_GRID"),-8.25,-7.65,-6.75,-6.45,2.36,2.40,0.004); K.bx((g,"LAMPFACE"),-8.22,-7.68,-6.72,-6.48,2.355,2.36,0.0)  # cabin light
        K.bx((g,"STEEL_L"),x0+0.07,x0+0.12,y0+0.25,y1-0.25,0.95,1.0,0.003); K.bx((g,"STEEL_L"),x0+0.25,x1-0.25,y0+0.07,y0+0.12,0.95,1.0,0.003)    # handrails
        K.bx((g,"BLACK"),x1-0.02,x1,y1-0.52,y1-0.34,1.0,1.45,0.004)                                                                  # control strip (east post)
        for k in range(4): K.bx((g,"LED_AON") if k==2 else (g,"LED_ON"),x1-0.018,x1-0.012,y1-0.50+k*0.04,y1-0.46+k*0.04,1.08+k*0.08,1.12+k*0.08,0.0)
        K.bx((g,"YELLOW"),x0+0.07,x1-0.10,y1-0.10,y1,0.08,0.09,0.0)                                                                   # sill marking
        K.bx((g,"STEEL"),x0+0.4,x1-0.4,y0+0.08,y0+0.095,1.5,1.62,0.002)                                                               # rear panel plate
    cobjs=_mover(c,"lift_car",mkcar)
    for o in cobjs: o.parent=car
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
            K.bx((g,"STEEL"),x0,x1,y0,y1,z1-0.30,z1-0.25,0.002); K.bx((g,"YELLOW"),x0+0.01,x1-0.01,y0,y1,z0,z0+0.08,0.001) if axis==0 else K.bx((g,"YELLOW"),x0,x1,y0+0.01,y1-0.01,z0,z0+0.08,0.001)
        o=_mover(c,name,fn)
        for ob in o: drv(ob,'location',axis,"%+.2f*d"%(sign*0.50),var_s=False,extra=[("d",ctl,'["%s"]'%prop)])
    wy1_=SY1+0.12
    leaf("lift_dgL",-8.55,-7.95,wy1_,wy1_+0.05,0.02,2.26,0,-1,"dg"); leaf("lift_dgR",-7.95,-7.35,wy1_,wy1_+0.05,0.02,2.26,0,+1,"dg")
    leaf("lift_duL",AX0,AX0+0.05,-7.00,-6.40,FZ+0.02,7.60,1,-1,"du"); leaf("lift_duR",AX0,AX0+0.05,-6.40,-5.80,FZ+0.02,7.60,1,+1,"du")
    print("lift: built shaft, anteroom, props, car, doors")
