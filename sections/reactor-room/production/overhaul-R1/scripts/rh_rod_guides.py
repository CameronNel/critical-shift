"""Bored drive housings and fixed guide seats, preserving the rod contract."""
import bpy,bmesh,math,json
from mathutils import Vector
import rh_stlib as S
import rh_support_registry as SUPPORT
OWNER='rod guide correction'

def tighten_central_grids():
    for tag,x in (('A',-1.4),('B',1.4)):
        o=next(o for o in bpy.data.objects if o.name.startswith('R2 bank '+tag+' ') and 'rod band TRIM' in o.name)
        inverse=o.matrix_world.inverted();changed=0
        for v in o.data.vertices:
            p=o.matrix_world@v.co;r=math.hypot(p.x-x,p.y)
            if abs(r-.14)<.000005:
                p.x=x+(p.x-x)*(.1125/.14);p.y*=.1125/.14;v.co=inverse@p;changed+=1
        assert changed,'Missing retained central sleeve inner walls'
        o.data.update()
        print('CENTRAL_GRID_BORE_TIGHTENED',tag,changed,flush=True)

def build(K,M):
    SUPPORT.reset(OWNER);sc=bpy.context.scene;sc.frame_set(1);rows=[]
    tighten_central_grids()
    for tag,x in (('A',-1.4),('B',1.4)):
        housing=bpy.data.objects['BANK_'+tag+'_FIXED_HOUSING']
        original=tuple(housing.matrix_world);parent=housing.parent
        bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.345,depth=3.10,end_fill_type='NGON',location=(x,0,11.16))
        cutter=bpy.context.object;cutter.name='RH TEMP rod guide bore '+tag
        mod=housing.modifiers.new('owned coaxial drive cavity','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
        bpy.context.view_layer.objects.active=housing;bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cutter,do_unlink=True)
        assert tuple(housing.matrix_world)==original and housing.parent==parent
        group='bank guide '+tag
        # Lower bush guides the nominal .240m-radius shaft; the .300m cap
        # remains above the9.94m guide top throughout the retained1.4m stroke.
        S.lathe(K,(group,'STEEL'),x,0,[(.2475,9.682),(.480,9.682),(.480,9.700),(.345,9.700),(.345,9.940),(.2475,9.940),(.2475,9.682)],64)
        bm=K.get((group,'STEEL'));bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0000001);bm.normal_update()
        for i in range(4):
            a=math.pi/4+i*math.pi/2;xx=x+.43*math.cos(a);yy=.43*math.sin(a)
            S.disc(K,group+' bolts','GALV',(xx,yy,9.682),(0,0,-1),.014,.012,seg=6)
            SUPPORT.register(OWNER,'bank '+tag+' guide flange seat','RH refine '+group+' STEEL',housing.name,[(xx,yy,9.700)],(0,0,1),'bearing')
        rows.append(dict(bank=tag,axis=[x,0],bore_radius=.345,guide_inner_radius=.2475,guide_outer_radius=.345,guide_z=[9.682,9.940]))
    sc['rh_rod_guide_correction']=json.dumps(rows);bpy.context.view_layer.update()
    print('ROD_GUIDE_CAVITIES_BUILT',json.dumps(rows),flush=True)
