import bpy, sys, json, math
from mathutils import Vector
sys.path.insert(0, sys.argv[sys.argv.index('--')+1])
import design_layout as D
from design_data import *
out=sys.argv[sys.argv.index('--')+2]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=28; sc.view_settings.exposure=0.5; sc.cycles.use_denoising=True
sc.render.resolution_x=1120; sc.render.resolution_y=630
# colours (cat/color -> rgb)
PAL=dict(wall=(.78,.76,.72),floorc=(.86,.78,.64),floorh=(.74,.78,.82),yard=(.62,.60,.55),roof=(.35,.37,.4),cliff=(.55,.48,.38),
 kitchen=(.85,.78,.62),counter=(.65,.5,.3),table=(.72,.55,.32),chair=(.45,.4,.3),booth=(.55,.4,.28),vending=(.75,.18,.15),appliance=(.5,.55,.6),screen=(.05,.05,.07),couch=(.62,.30,.20),
 plant=(.25,.5,.22),sign=(.3,.3,.3),bench=(.55,.4,.25),desk=(.45,.5,.55),safety=(.15,.5,.2),gantry=(.55,.25,.65),portal=(.28,.22,.15),rail=(.3,.3,.32),cart=(.5,.33,.16),crate=(.7,.52,.3),pallet=(.6,.45,.25),
 barrel=(.25,.4,.55),drum=(.4,.4,.4),scrap=(.45,.32,.25),tarp=(.3,.5,.3),machine=(.45,.45,.45),canopy=(.55,.55,.58),planter=(.6,.6,.6),tree=(.22,.45,.22),pole=(.1,.1,.1),door=(.8,.2,.1),blast=(.85,.55,.1))
mats={}
def mat(name,rgb,emit=0):
    if name in mats: return mats[name]
    m=bpy.data.materials.new(name); m.use_nodes=True
    b=m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(*rgb,1); b.inputs['Roughness'].default_value=0.85
    if emit:
        b.inputs['Emission Color'].default_value=(*rgb,1); b.inputs['Emission Strength'].default_value=emit
    mats[name]=m; return m
roofs=[]
def add_box(name,x0,x1,y0,y1,z0,z1,col,emit=0,roof=False):
    bpy.ops.mesh.primitive_cube_add(size=1,location=((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
    o=bpy.context.object; o.scale=(abs(x1-x0),abs(y1-y0),abs(z1-z0)); o.name=name
    o.data.materials.append(mat(name if emit else str(col),col,emit))
    if roof: roofs.append(o)
    return o
def add_cyl(name,x,y,r,z0,z1,col):
    bpy.ops.mesh.primitive_cylinder_add(radius=r,depth=z1-z0,location=(x,y,(z0+z1)/2),vertices=16)
    o=bpy.context.object; o.name=name; o.data.materials.append(mat(str(col),col)); return o
# furniture/props from the shared layout
for i,o in enumerate(D.objs):
    c=PAL.get(o['cat'],PAL.get(o['color'],(.6,.6,.6)))
    if o['kind']=='box':
        if o['cat']=='cliff':
            add_box('cliff',-70,-48,-90,-54,0,o['z1']+2,c)
        else: add_box(f"{o['cat']}{i}",o['x0'],o['x1'],o['y0'],o['y1'],o['z0'],o['z1'],c, emit=3.0 if o['cat']=='tv' else 0)
    else: add_cyl(f"{o['cat']}{i}",o['x'],o['y'],o['r'],o['z0'],o['z1'],c)
# floors
def floor(rc,col,name,z=0): add_box(name,rc[0],rc[1],rc[2],rc[3],-0.2,z,col)
floor((-70,45,-100,-45),PAL['yard'],'ground')
floor(CAF,PAL['floorc'],'caf_floor',0.02); floor(HALL,PAL['floorh'],'hall_floor',0.02); floor(SPAWN,(.8,.8,.8),'spawn_floor',0.02)
# wall helper with openings
def wall_h(x0,x1,y,h,col,gaps,t=0.3,name='wall',gh=2.7):
    pts=[x0]+[v for g in sorted(gaps) for v in (g[0]-g[1]/2,g[0]+g[1]/2)]+[x1]
    for a,b in zip(pts[::2],pts[1::2]):
        if b-a>0.01: add_box(name,a,b,y-t/2,y+t/2,0,h,col)
    for gx,gw in gaps: add_box(name+'_hdr',gx-gw/2,gx+gw/2,y-t/2,y+t/2,gh,h,col)
def wall_v(y0,y1,x,h,col,gaps,t=0.3,name='wall',gh=2.7):
    pts=[y0]+[v for g in sorted(gaps) for v in (g[0]-g[1]/2,g[0]+g[1]/2)]+[y1]
    for a,b in zip(pts[::2],pts[1::2]):
        if b-a>0.01: add_box(name,x-t/2,x+t/2,a,b,0,h,col)
    for gy,gw in gaps: add_box(name+'_hdr',x-t/2,x+t/2,gy-gw/2,gy+gw/2,gh,h,col)
W=PAL['wall']
# cafeteria
wall_h(CAF[0],CAF[1],CAF[2],H_CAF,W,[(8,2.6)],name='caf_S')
wall_v(CAF[2],CAF[3],CAF[0],H_CAF,W,[(-70,3)],name='caf_W'); wall_v(CAF[2],CAF[3],CAF[1],H_CAF,W,[(-70,2.2)],name='caf_E')
# high windows on the yard side
add_box('win_strip',CAF[0]-0.2,CAF[0]+0.2,-78,-72,3.0,4.4,(.5,.7,.85),emit=0.6) if False else None
# hall
wall_h(HALL[0],HALL[1],HALL[2],H_HALL,W,[(8,6)],name='hall_S',gh=3.4)
wall_h(HALL[0],HALL[1],HALL[3],H_HALL,W,[(8,3.6)],name='hall_N',gh=3.2)
wall_v(HALL[2],HALL[3],HALL[0],H_HALL,W,[(-54,2.4)],name='hall_W'); wall_v(HALL[2],HALL[3],HALL[1],H_HALL,W,[(-54,2.4)],name='hall_E')
# blast door (in the spine opening, drawn open as a frame) + door frames
add_box('blast_frame',6.0,6.3,-48.15,-47.85,0,3.6,PAL['blast']); add_box('blast_frame',9.7,10.0,-48.15,-47.85,0,3.6,PAL['blast']); add_box('blast_frame',6.0,10.0,-48.15,-47.85,3.2,3.6,PAL['blast'])
# spine corridor to reactor door
add_box('spine_wallW',5.9,6.1,-48,-14,0,4.2,W); add_box('spine_wallE',9.9,10.1,-48,-14,0,4.2,W); add_box('spine_roof',5.9,10.1,-48,-14,4.1,4.3,PAL['roof'],roof=False)
add_box('reactor_door',6,10,-14.4,-14,0,3.4,PAL['door'],emit=1.2)
for yy in range(-44,-16,6): add_box('spine_light',7.5,8.5,yy,yy+0.8,4.0,4.1,(1,.9,.7),emit=8)
# spawn walls (hallway end visible)
wall_h(SPAWN[0],SPAWN[1],SPAWN[2],4.0,W,[]); wall_v(SPAWN[2],SPAWN[3],SPAWN[0],4.0,W,[]); wall_v(SPAWN[2],SPAWN[3],SPAWN[1],4.0,W,[])
# medical block
wall_h(MEDICAL[0],MEDICAL[1],MEDICAL[2],3.6,W,[]); wall_h(MEDICAL[0],MEDICAL[1],MEDICAL[3],3.6,W,[]); wall_v(MEDICAL[2],MEDICAL[3],MEDICAL[1],3.6,W,[])
# yard north / south fences, evacuation gate, refinery wall (backdrop)
add_box('fenceS',-48,-31,-84.1,-83.9,0,2.4,PAL['canopy']); add_box('fenceS',-25,-8,-84.1,-83.9,0,2.4,PAL['canopy'])
add_box('refinery_face',-33.7,-18.9,-57.6,-56.6,0,7.5,(.6,.58,.55)); add_box('freight_gate',-23.7,-20.7,-57.7,-57.5,0,3.6,PAL['blast'])
add_box('fenceN',-48,-24,-60.1,-59.9,0,2.4,PAL['canopy']); add_box('fenceN',-20.4,-12,-60.1,-59.9,0,2.4,PAL['canopy'])
# west colonnade
add_box('colonnade_roof',-18.9,-4,-55.5,-52.5,3.2,3.4,PAL['canopy'])
for cx in (-18,-14,-10,-6): add_box('col',cx-0.1,cx+0.1,-55.4,-55.2,0,3.2,PAL['canopy'])
# roofs (cafeteria + hall) with skylights as emissive strips
add_box('caf_roof',CAF[0],CAF[1],CAF[2],CAF[3],H_CAF,H_CAF+0.3,PAL['roof'],roof=True)
add_box('hall_roof',HALL[0],HALL[1],HALL[2],HALL[3],H_HALL,H_HALL+0.3,PAL['roof'],roof=True)
# interior lights
for lx in (-3,3,13,19,25):
    for ly in (-64,-70,-76): add_box('caf_light',lx-0.6,lx+0.6,ly-0.15,ly+0.15,H_CAF-0.15,H_CAF,(1,.85,.6),emit=10)
for lx in range(0,32,6): add_box('hall_light',lx-0.9,lx+0.9,-54.2,-53.8,H_HALL-0.15,H_HALL,(.85,.92,1),emit=9)
for lx in range(0,32,10): add_box('sky',lx-1,lx+1,-52,-50,H_HALL+0.3,H_HALL+0.4,(.6,.8,1),emit=2)
# sun + sky
sun=bpy.data.lights.new('sun','SUN'); sun.energy=2.4; sun.angle=0.05
so=bpy.data.objects.new('sun',sun); so.rotation_euler=(math.radians(52),0,math.radians(-35)); sc.collection.objects.link(so)
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True
w.node_tree.nodes['Background'].inputs['Color'].default_value=(.55,.7,.9,1); w.node_tree.nodes['Background'].inputs['Strength'].default_value=1.0
bpy.context.view_layer.update()
def cam(name,loc,tgt,lens=22,roof_hidden=False):
    c=bpy.data.cameras.new(name); c.lens=lens; c.clip_start=0.05; c.clip_end=500
    o=bpy.data.objects.new(name,c); o.location=loc; sc.collection.objects.link(o)
    o.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler(); return o
views=[('V1_spawn_exit_north',(8,-80.7,1.65),(8,-30,2.4),21,False),
       ('V2_yard_door_west',(-7.6,-70,1.65),(-48,-70.3,2.4),24,False),
       ('V3_hall_east',(-3.5,-55.5,1.7),(32,-53,2.4),20,False),
       ('V4_aerial',(10,-135,62),(-4,-68,0),32,True)]
for n,loc,tgt,lens,hide in views:
    for r in roofs: r.hide_render=hide
    co=cam(n,loc,tgt,lens); sc.camera=co
    sc.render.filepath=f'{out}/{n}.png'; bpy.ops.render.render(write_still=True)
print('GREYBOX DONE')
