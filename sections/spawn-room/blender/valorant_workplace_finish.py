"""Twelfth comparison: service trolley, laundry print and stable room framing."""
import bpy
from math import pi,sin
from mathutils import Quaternion
import grounded_kit as k
from valorant_readability import slashes

def run():
    assert not bpy.context.scene.get('valorant_workplace_finish_pass')
    k.M={m.name:m for m in bpy.data.materials};k.STAGE=3
    bpy.data.objects['V_HALL_culture_poster'].location.y=7.59
    c=bpy.data.objects['REFERENCE_LOCKER'];c.data.lens=20.6;c.rotation_euler=(Quaternion((0,0,1),.025)@c.rotation_euler.to_quaternion()).to_euler()
    # Supplies sit side by side rather than the cleaning bottle behind the towels.
    for i in range(3):
        o=bpy.data.objects['V_CART_towel_%d'%i];o.location.x=.063;o.location.y=.07;o.scale.x=.82
    spray=bpy.data.objects['V_CART_spray'];spray.location.x=-.20;spray.location.y=.25
    b=k.start()
    k.lathe('V_CART_bottle_collar',[(.018,.245),(.022,.245),(.022,.263),(.018,.263)],'V_graphite',32)
    k.box('V_CART_bottle_label',(0,.040,.135),(.045,.001,.074),'V_paper',.002)
    k.label('V_CART_bottle_label_type','SURFACE\nCARE',(.019,.041,.152),.010,'ink',rot=(pi/2,0,pi))
    for i in range(4):k.box('V_CART_bottle_label_rule',(0,.041,.122-i*.005),(.029,.0004,.0007),'ink',0)
    for o in set(bpy.data.objects)-b:o.parent=spray
    # Front-facing storage marks are native print on the container faces.
    for name,d,h in [('V_CART_upper',.48,.32),('V_CART_lower',.58,.31)]:
        root=bpy.data.objects[name];b=k.start()
        for i in range(2):
            x=.10+i*.032
            o=k.mesh('V_CART_inventory_mark',[(x,d/2+.014,.075),(x+.020,d/2+.014,.075),(x+.042,d/2+.014,.14),(x+.022,d/2+.014,.14)],[(0,1,2,3)],'canvas_rust' if name.endswith('lower') else 'V_graphite')
        for o in set(bpy.data.objects)-b:o.parent=root
    # The laundry emblem follows the sagged canvas rather than a floating panel.
    b=k.start();vs=[];fs=[]
    for side in [-1,1]:
        for j in range(12):
            t0=j/12;t1=(j+1)/12
            for t in [t0,t1]:
                x=side*(.035+.10*t);z=.335+.15*t
                for dx in [-.014,.014]:
                    xx=x+dx;y=-.184-.018*sin(pi*(xx+.25)/.50)*sin(pi*(z-.17)/.56)-.0006;vs.append((xx,y,z))
            q=len(vs)-4;fs.append((q,q+1,q+3,q+2))
    o=k.mesh('V_LAUNDRY_canvas_print',vs,fs,'rug_border');o.parent=bpy.data.objects['V_LOCKER_laundry_cart']
    bpy.context.scene['valorant_workplace_finish_pass']=12
