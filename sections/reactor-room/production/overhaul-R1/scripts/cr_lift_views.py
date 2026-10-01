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
V={"new_1_hall_ground_door":((-7.9,-2.2,1.65),(-7.95,-5.25,1.3),20,1),
   "new_2_inside_car_upper_looking_east":((-8.30,-6.40,6.95),(-6.0,-6.4,6.85),16,400),
   "new_3_anteroom_from_lift_door":((-6.55,-6.40,6.95),(-4.8,-6.8,6.75),16,400),
   "new_4_anteroom_from_control_door":((-5.15,-6.80,6.95),(-6.8,-6.2,6.7),16,400),
   "new_5_anteroom_overview":((-5.0,-5.95,8.15),(-6.2,-7.0,6.0),14,400),
   "new_6_control_room_looking_at_door":((-3.3,-6.80,6.95),(-4.8,-6.8,6.85),18,400),
   "new_7_hall_overview":((-3.0,0.5,3.4),(-6.6,-6.0,5.8),22,1)}
ONLY=A[A.index('--only')+1].split(',') if '--only' in A else None
for n,(l,t,ln,fr) in V.items():
    if ONLY and n not in ONLY: continue
    bpy.context.scene.frame_set(fr); shoot("cam_"+n,l,t,os.path.join(OUT,n+".png"),ln,(W,H),S)
print("all done")
