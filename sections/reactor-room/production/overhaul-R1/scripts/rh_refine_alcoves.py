"""Fitted service recesses for retained equipment outside the octagonal face.

The equipment, its ports and interactive pivots stay in place. Concrete gets
formed reveals and a bearing floor; existing steel columns remain continuous.
"""
import bpy,crk
from mathutils import Vector
from r2lib import WALLS
import rh_support_registry as SUPPORT

def box(K,key,w,u0,u1,v0,v1,z0,z1):
    p=w.pt((u0+u1)/2,(v0+v1)/2)
    K.box(key,p.x,p.y,z0,z1,u1-u0,v1-v0,w.angle,0)

def boolean(target,cutter,operation):
    before=len(target.data.polygons)
    bpy.context.view_layer.objects.active=target
    mod=target.modifiers.new('Fitted service recess','BOOLEAN')
    mod.operation=operation;mod.solver='EXACT';mod.object=cutter
    mod.use_self=True;mod.use_hole_tolerant=True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    if before and not target.data.polygons:raise RuntimeError('Local recess erased entire mesh: '+target.name)

def temporary(K,collection,material):
    return K.build(collection,'RH temporary recess',{'CONC_POUR':material})[0]

def build(K,M,collection):
    SUPPORT.reset('refinement recesses')
    # The pool-inlet support stands on the concrete coping, with a formed
    # tread recess so its base does not intersect the non-slip plate above.
    cutter=crk.Kit();cutter.bx(('cut','CONC_POUR'),-1.515,-1.285,-3.615,-3.385,.20,.24,0)
    cut=temporary(cutter,collection,M['CONC_POUR'])
    tread=bpy.data.objects.get('RH pool tread TREAD')
    if tread:boolean(tread,cut,'DIFFERENCE')
    bpy.data.objects.remove(cut,do_unlink=True)
    for name,wi,u0,u1,depth,z0,z1 in (
        ('fuel cart',5,3.62,5.68,1.10,0,2.15),
        ('vent power',3,.52,1.78,.96,1.92,2.92)):
        w=WALLS[wi];kit=crk.Kit()
        box(kit,('cut','CONC_POUR'),w,u0,u1,-depth,.60,z0,z1)
        cutter=temporary(kit,collection,M['CONC_POUR'])
        # Never remove columns, protected assemblies or wall accessories here.
        for o in list(bpy.data.objects):
            if o.type=='MESH' and o.name.startswith(('RH walls mass ','RH walls concrete ')):
                boolean(o,cutter,'DIFFERENCE')
        bpy.data.objects.remove(cutter,do_unlink=True)
        if wi==5:
            kit=crk.Kit()
            box(kit,('cut','CONC_POUR'),w,3.38,5.78,-.02,.20,.32,.54)
            cutter=temporary(kit,collection,M['CONC_POUR'])
            for o in list(bpy.data.objects):
                if o.type=='MESH' and o.name.startswith('RH walls trim '):boolean(o,cutter,'DIFFERENCE')
            bpy.data.objects.remove(cutter,do_unlink=True)
            box(K,('cart bay bumper end','STEEL'),w,3.368,3.38,.044,.116,.34,.52)
        group=name+' service recess'
        box(K,(group,'CONC_POUR'),w,u0-.10,u1+.10,-depth-.12,-depth,z0,z1+.12)
        for a,b in ((u0-.10,u0),(u1,u1+.10)):
            box(K,(group,'CONC_POUR'),w,a,b,-depth,.015,z0,z1)
        box(K,(group,'CONC_POUR'),w,u0-.10,u1+.10,-depth,.015,z1,z1+.12)
        # A visible steel frame seats in the formed jambs and lintel, leaving
        # the adjacent original I section and its load path intact.
        for a,b in ((u0-.075,u0+.025),(u1-.025,u1+.075)):
            box(K,(group,'STEEL'),w,a,b,-.05,.035,z0,z1+.075)
        box(K,(group,'STEEL'),w,u0-.075,u1+.075,-.05,.035,z1-.025,z1+.075)
        if wi==5:
            kit=crk.Kit()
            box(kit,('floor','CONC_POUR'),w,u0-.10,u1+.10,-depth-.12,.08,-.45,0)
            addition=temporary(kit,collection,M['CONC_POUR'])
            boolean(bpy.data.objects['R2 floor'],addition,'UNION')
            bpy.data.objects.remove(addition,do_unlink=True)
        else:
            # Cabinet bottom at 2.0 meets an actual shelf in the recess.
            box(K,(group,'STEEL'),w,u0,u1,-depth,.05,1.94,2.0)
            for z in (2.12,2.57):
                for y in (6.81,7.19):
                    p=Vector((10.80,y,z));v=(Vector((p.x,p.y))-w.P).dot(w.n)
                    end=p-Vector((w.n.x,w.n.y,0))*(v+depth)
                    K.prism((group,'STEEL'),p,end,.025,.025,8,0,True,0)
    # The sampling cabinet gets a fitted seat in the coping, rather than
    # passing through the raised rim and falsely claiming floor support.
    kit=crk.Kit();kit.bx(('cut','CONC_POUR'),1.11,2.09,-3.76,-3.09,0,.30,0)
    cutter=temporary(kit,collection,M['CONC_POUR'])
    for o in list(bpy.data.objects):
        if o.type=='MESH' and o.name.startswith('RH pool coping '):boolean(o,cutter,'DIFFERENCE')
    bpy.data.objects.remove(cutter,do_unlink=True)
    SUPPORT.register('refinement recesses','sampler coping seat','RH stations south','RH pool coping CONC_POUR',[(1.6,-3.425,0)])
    # Both console plinths bear on fitted concrete seats. Tread is relieved
    # around their footprints so the base plates do not intersect it by15 mm.
    for cx in (-1.025,.94):
        right=cx+.185 if cx<0 else cx+.165
        kit=crk.Kit();kit.bx(('cut','CONC_POUR'),cx-.185,right,-3.84,-3.36,.20,.23,0)
        cutter=temporary(kit,collection,M['CONC_POUR'])
        for o in list(bpy.data.objects):
            if o.type=='MESH' and o.name.startswith('RH pool tread '):boolean(o,cutter,'DIFFERENCE')
        bpy.data.objects.remove(cutter,do_unlink=True)
        kit=crk.Kit();kit.bx(('seat','CONC_POUR'),cx-.188,right+.003,-3.843,-3.357,-.30,.20,0)
        seat=temporary(kit,collection,M['CONC_POUR'])
        curb=bpy.data.objects.get('RH pool coping GALV')
        if curb:boolean(curb,seat,'DIFFERENCE')
        boolean(bpy.data.objects['RH pool coping CONC_POUR'],seat,'UNION')
        bpy.data.objects.remove(seat,do_unlink=True)
        SUPPORT.register('refinement recesses','console coping seat '+str(cx),'RH pool console STEEL',
            'RH pool coping CONC_POUR',[(cx+dx,-3.6+dy,.20) for dx in (-.12,.12) for dy in (-.10,.10)])
