"""Review views of the elevator (lift): inside the car, the ground landing, the upper landing and the strip to the control-room west door (aerial, straight-on at the door, along the strip).
usage: python cr_lift_views.py -- <in.blend> <out_dir> [--w 960 --h 540 --samples 24]   (Cycles, whole scene visible, scene frame 1 = car at the ground, door open; 400 = car at the upper level, east door open (24 s loop at 30 fps))"""
import bpy,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cam import shoot
A=sys.argv[sys.argv.index("--")+1:]; SRC,OUT=A[0],A[1]
def opt(k,d): return int(A[A.index(k)+1]) if k in A else d
W,H,S=opt("--w",960),opt("--h",540),opt("--samples",24)
os.makedirs(OUT,exist_ok=True); bpy.ops.wm.open_mainfile(filepath=SRC)
for col in bpy.data.collections: col.hide_render=False
V={"p1_anteroom_from_lift_door":((-6.72,-6.40,6.95),(-5.6,-8.2,6.1),15,400),
   "p2_anteroom_from_control_door":((-5.12,-6.80,6.95),(-7.2,-8.2,6.0),15,400),
   "p3_anteroom_overview":((-6.2,-5.85,8.25),(-6.0,-8.4,6.0),14,400),
   "p4_coffee_table_closeup":((-5.7,-7.2,6.55),(-6.35,-8.1,5.8),28,400),
   "p5_tv_wall":((-6.55,-6.95,6.75),(-4.83,-8.15,6.75),30,400),
   "p6_water_cooler_closeup":((-6.3,-7.2,6.8),(-5.45,-5.9,6.25),30,400),
   "p7_plant_and_lamp_corner":((-6.0,-7.6,6.7),(-5.3,-8.75,6.3),26,400),
   "p8_car_panel_and_dial_ground":((-8.25,-6.0,1.55),(-7.6,-7.08,1.35),24,1),
   "p9_car_camera_and_certificate":((-7.45,-5.95,1.55),(-8.5,-6.9,2.0),22,1),
   "p10_car_mid_ride_dial_needle":((-8.25,-6.0,4.25),(-7.6,-7.08,4.05),24,241),
   "p11_anteroom_floor_indicator":((-5.15,-6.4,7.0),(-6.83,-6.4,7.9),30,400),
   "p12_hall_ground_door_indicator":((-7.2,-2.4,1.9),(-7.2,-5.25,2.2),24,1),
   "p13_couch_and_print":((-5.5,-7.0,6.6),(-7.3,-8.3,6.0),22,400),
   "p14_car_mirror_and_rail":((-7.55,-6.95,1.55),(-8.62,-6.1,1.6),24,1)}
ONLY=A[A.index('--only')+1].split(',') if '--only' in A else None
for n,(l,t,ln,fr) in V.items():
    if ONLY and n not in ONLY: continue
    bpy.context.scene.frame_set(fr); shoot("cam_"+n,l,t,os.path.join(OUT,n+".png"),ln,(W,H),S)
print("all done")
