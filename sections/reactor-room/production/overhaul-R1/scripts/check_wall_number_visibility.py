"""Finite check: how much of each baked wall number is clear of equipment.

Blender 5.2.2: blender --background --disable-autoexec -noaudio reactorroom.blend --python-exit-code 1 --python check_wall_number_visibility.py
Casts 9 rays per stencil from 1.7 m inside each wall straight at the wall and counts
those that reach the wall concretes first (the haze volume is skipped). A sample test,
not a view test: it ignores anything nearer the viewer than 1.7 m from the wall.
"""
import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
P,W,H,Z0=4.1,2.4,0.8,3.3
walls={'N':(1,1),'S':(1,-1),'E':(0,1),'W':(0,-1)}
wall_mats={'RH refine wall concrete','RH refine cast concrete'}
rows=[]
for letter,(ax,sg) in walls.items():
    for b in range(5):
        c=(b-2)*P   # bay centre along u
        u_sign={'N':1,'S':-1,'E':-1,'W':1}[letter]
        vis=0;tot=0;blockers=set()
        for fu in (-.45,0,.45):
            for fz in (.1,.5,.9):
                u=(c+fu*W)*u_sign; z=Z0+fz*H
                o=Vector((0,0,z)); o[1-ax]=u; o[ax]=sg*9.0
                d=Vector((0,0,0)); d[ax]=sg
                ok=False
                for _ in range(6):
                    ok,loc,nrm,idx,obj,_=sc.ray_cast(dg,o,d,distance=3.0)
                    if ok and 'haze' in obj.name.lower():
                        o=loc+d*0.01; continue
                    break
                tot+=1
                if ok:
                    mats=[s.material.name for s in obj.material_slots if s.material]
                    if any(m in wall_mats for m in mats) and abs(abs(loc[ax])-10.7)<1.2: vis+=1
                    else: blockers.add(obj.name[:30])
        rows.append((f'{letter}-{b+1}',vis,tot,sorted(blockers)[:3]))
for r in rows: print("NUM",r[0],f"{r[1]}/{r[2]} samples clear",("blocked by "+", ".join(r[3])) if r[3] else "")
