"""Review views of the elevator (lift): inside the car, the ground landing, the upper landing and the strip to the control-room west door (aerial, straight-on at the door, along the strip).
usage: python cr_lift_views.py -- <in.blend> <out_dir> [--w 960 --h 540 --samples 24]   (Cycles, whole scene visible, scene frame 1 = car at the ground, 240 = car at the upper landing)"""
import bpy,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cam import shoot
A=sys.argv[sys.argv.index("--")+1:]; SRC,OUT=A[0],A[1]
def opt(k,d): return int(A[A.index(k)+1]) if k in A else d
W,H,S=opt("--w",960),opt("--h",540),opt("--samples",24)
os.makedirs(OUT,exist_ok=True); bpy.ops.wm.open_mainfile(filepath=SRC)
for col in bpy.data.collections: col.hide_render=False
V={"lift_1_inside_car":((-6.8,-7.12,1.50),(-6.8,-5.85,1.25),16,1),
   "lift_2_ground_outside":((-6.8,-2.4,1.65),(-6.8,-5.6,1.35),20,1),
   "lift_3_overview_from_hall":((-4.2,0.8,3.2),(-6.4,-6.0,5.8),20,240),
   "lift_4_upper_landing":((-4.95,-4.68,7.1),(-6.9,-5.65,6.6),14,240),
   "lift_5_aerial_connection":((-6.6,-2.6,10.6),(-5.5,-6.6,5.5),22,240),
   "lift_6_door_straight_on":((-5.5,-6.8,7.0),(0.0,-6.8,6.9),14,240),
   "lift_7_along_strip":((-5.2,-7.7,7.0),(-5.2,-5.0,6.9),16,240)}
ONLY=A[A.index('--only')+1].split(',') if '--only' in A else None
for n,(l,t,ln,fr) in V.items():
    if ONLY and n not in ONLY: continue
    bpy.context.scene.frame_set(fr); shoot("cam_"+n,l,t,os.path.join(OUT,n+".png"),ln,(W,H),S)
print("all done")
