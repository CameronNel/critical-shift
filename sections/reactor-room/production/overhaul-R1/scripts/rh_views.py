"""Standard review views of the reactor hall (the nine scene cameras' positions) plus optional --only names and --state stability.
usage: python rh_views.py -- <in.blend> <out_dir> [samples] [--only h01_hero,h04_turbine_aisle] [--state 0.5]"""
import bpy,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cam import shoot
A=sys.argv[sys.argv.index("--")+1:]; O=A[1]; N=int(A[2]) if len(A)>2 and A[2].isdigit() else 20
ONLY=A[A.index('--only')+1].split(',') if '--only' in A else None; STATE=float(A[A.index('--state')+1]) if '--state' in A else None
bpy.ops.wm.open_mainfile(filepath=A[0])
for col in bpy.data.collections: col.hide_render=False
if STATE is not None: bpy.data.objects['REACTOR_STATE']['stability']=STATE
bpy.context.scene.frame_set(1)
V={"h01_hero":((-7.5,8.6,8.8),(0.0,0.0,5.0),18),"h02_west_entry":((-10.1,-2.4,1.7),(0,2,2.5),21),"h03_south_gate":((-2.6,-6.3,1.7),(2,-2,1.5),24),
   "h04_turbine_aisle":((5.3,-6.2,1.8),(8,2,1.8),23),"h05_reverse_north":((3.2,7.0,1.7),(0,0,1.5),23),"h06_fuel_handling":((2.8,5.2,1.8),(2,11,2),23),
   "h07_emergency":((6.1,-5.4,1.9),(8,0,1.5),23),"h08_material":((-6.9,-4.9,1.8),(-8,-8,1.5),27),"h10_east_high":((9.4,-5.9,8.0),(0,0,2),17)}
for n,(l,t,ln) in V.items():
    if ONLY and n not in ONLY: continue
    shoot("cam_"+n,l,t,os.path.join(O,n+".png"),ln,(960,540),N)
