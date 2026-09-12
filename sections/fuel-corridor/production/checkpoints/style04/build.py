"""Original Fuel Corridor. Blender 5.2, factory-empty, metres. No imported geometry.

Build: blender -b --factory-startup --python build.py -- --stage slice --revision slice01
Render only through the shared GPU gate. See run.ps1.
"""
import argparse, bpy, math, json, sys, random, hashlib, os
from pathlib import Path
from mathutils import Vector
ROOT=Path(os.environ.get('FUEL_CORRIDOR_ROOT',str(Path(__file__).resolve().parents[1])))
P=argparse.ArgumentParser(); P.add_argument('--stage',choices=['slice','full'],default='full'); P.add_argument('--revision',default='r01'); P.add_argument('--render',default=''); P.add_argument('--samples',type=int,default=32); P.add_argument('--width',type=int,default=1200)
A=P.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene; S.unit_settings.system='METRIC'; S.unit_settings.scale_length=1
random.seed(71)
COL=None; PAR=None
def collection(name):
    global COL
    COL=bpy.data.collections.new(name);S.collection.children.link(COL)
def add(o):
    for c in list(o.users_collection):c.objects.unlink(o)
    COL.objects.link(o)
    if PAR:o.parent=PAR
    return o
def root(name,role='architecture',anchors=None,direction=(0,0,-1)):
    global PAR
    o=bpy.data.objects.new(name,None);COL.objects.link(o);o['assembly_role']=role
    if anchors is not None:o['support_anchors']=json.dumps(anchors);o['support_direction']=list(direction);o['support_max_gap']=.005;o['support_max_penetration']=.002
    PAR=o;return o
M={}
def mat(name,color,rough=.6,metal=0,variation=.05,bump=.02,emission=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    p.inputs['Specular IOR Level'].default_value=.32
    if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
    if variation:
        tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=2.3;tex.inputs['Detail'].default_value=2
        coord=n.new('ShaderNodeTexCoord');l.new(coord.outputs['Object'],tex.inputs['Vector'])
        mix=n.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[1].default_value=(*[v*(1-variation) for v in color],1);mix.inputs[2].default_value=(*[min(1,v*(1+variation)) for v in color],1);l.new(tex.outputs['Fac'],mix.inputs[0]);l.new(mix.outputs[0],p.inputs['Base Color'])
        rr=n.new('ShaderNodeMapRange');rr.inputs['From Min'].default_value=0;rr.inputs['From Max'].default_value=1;rr.inputs['To Min'].default_value=rough-.045;rr.inputs['To Max'].default_value=rough+.045;l.new(tex.outputs['Fac'],rr.inputs[0]);l.new(rr.outputs[0],p.inputs['Roughness'])
        if bump:
            grain=n.new('ShaderNodeTexNoise');grain.inputs['Scale'].default_value=54;grain.inputs['Detail'].default_value=2;l.new(coord.outputs['Object'],grain.inputs['Vector']);bn=n.new('ShaderNodeBump');bn.inputs['Strength'].default_value=.17;bn.inputs['Distance'].default_value=bump;l.new(grain.outputs['Fac'],bn.inputs['Height']);l.new(bn.outputs['Normal'],p.inputs['Normal'])
    M[name]=m;return m
mat('mineral',(.56,.575,.59),.82,variation=.025,bump=.0015)
mat('floor',(.30,.32,.35),.78,variation=.025,bump=.002)
mat('repair',(.345,.36,.38),.84,variation=.018,bump=.001)
# Historical material keys retained for source replay; colors now follow reactor A05.
mat('teal',(.065,.083,.11),.52,.25,.035,.0004)
mat('teal_light',(.145,.17,.205),.60,.12,.025,.0006)
mat('steel',(.30,.33,.37),.34,.80,.025,.0004)
mat('darksteel',(.048,.061,.080),.59,.38,.025,.0008)
mat('rubber',(.025,.03,.029),.93,.0,.04,.008)
mat('ochre',(.94,.225,.022),.53,.10,.025,.0004)
mat('ivory',(.69,.71,.72),.57,.08,.018,.0004)
mat('ink',(.075,.083,.075),.86,variation=0,bump=0)
mat('paper',(.67,.63,.48),.94,variation=.04,bump=.003)
mat('cloth',(.30,.32,.34),.98,variation=.035,bump=.0007)
mat('red',(.42,.075,.035),.56,.15,.05,.003)
mat('glass',(.24,.33,.31),.22,.18,0,0)
mat('lamp',(1,.82,.57),.45,0,0,0,4)
mat('cool_lamp',(.70,.86,1),.4,0,0,0,3)
mat('chip',(.21,.22,.195),.8,.2,0,0)
mat('primer',(.37,.265,.14),.9,.05,.05,.004)
mat('old_teal',(.12,.145,.175),.67,.12,.035,.0007)
mat('wall_patch',(.505,.53,.55),.84,variation=.015,bump=.0003)
mat('wall_light',(.61,.63,.65),.81,variation=.015,bump=.0003)
mat('brass',(.43,.27,.09),.35,.72,.025,.0004)
def finish(o,name,material):
    o.name=name;add(o)
    if material:o.data.materials.append(M[material])
    return o
def box(name,loc,dim,material='teal',bevel=.005):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=finish(bpy.context.object,name,material);o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        b=o.modifiers.new('Manufactured edge','BEVEL');b.width=bevel;b.segments=2
        n=o.modifiers.new('Face normals','WEIGHTED_NORMAL');n.keep_sharp=True
    return o
def mesh(name,verts,faces,material):
    d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update();o=bpy.data.objects.new(name,d);COL.objects.link(o)
    if PAR:o.parent=PAR
    d.materials.append(M[material]);return o
def prism(name,outline,z0,z1,material,bevel=0):
    n=len(outline);verts=[(x,y,z) for z in [z0,z1] for x,y in outline];faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];o=mesh(name,verts,faces,material)
    if bevel:b=o.modifiers.new('Rolled edges','BEVEL');b.width=bevel;b.segments=2
    return o
def rod(name,a,b,r,material='steel',verts=32):
    a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d.length,location=(a+b)/2);o=finish(bpy.context.object,name,material);o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    be=o.modifiers.new('Machined rim','BEVEL');be.width=min(.004,r*.1,d.length*.2);be.segments=2
    for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
    return o
def tube(name,points,r,material):
    d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=2;d.bevel_depth=r;d.bevel_resolution=3;s=d.splines.new('POLY');s.points.add(len(points)-1)
    for p,co in zip(s.points,points):p.co=(*co,1)
    o=bpy.data.objects.new(name,d);COL.objects.link(o);d.materials.append(M[material]);o.parent=PAR;return o
def torus(name,loc,major,minor,material='steel',rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=48,minor_segments=10,location=loc,rotation=rot);o=finish(bpy.context.object,name,material)
    for p in o.data.polygons:p.use_smooth=True
    return o
def text_obj(name,body,loc,size=.15,material='ivory',rot=(math.pi/2,0,0),align='CENTER'):
    d=bpy.data.curves.new(name,'FONT');d.body=body;d.size=size;d.align_x=align;d.extrude=.0002;d.space_character=1.05;o=bpy.data.objects.new(name,d);COL.objects.link(o);d.materials.append(M[material]);o.location=loc;o.rotation_euler=rot;o.parent=PAR;return o
def area(name,loc,target,power=300,color=(1,.88,.7),size=2,size_y=None):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='RECTANGLE';d.size=size;d.size_y=size_y or size;o=bpy.data.objects.new(name,d);COL.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
def bolt(name,loc,axis=(0,-1,0),r=.014):
    v=Vector(axis)*.01;rod(name,Vector(loc)-v,Vector(loc)+v,r,'steel',6)
def beam(name,a,b,width,depth,material='darksteel'):
    a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(width,depth,(b-a).length),material,.003);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def lathe_x(name,profile,y,z,material,n=64):
    verts=[(x,y+math.cos(a*math.tau/n)*r,z+math.sin(a*math.tau/n)*r) for x,r in profile for a in range(n)]
    faces=[tuple(reversed(range(n))),tuple(range((len(profile)-1)*n,len(profile)*n))]
    for j in range(len(profile)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    o=mesh(name,verts,faces,material)
    for p in o.data.polygons[2:]:p.use_smooth=True
    return o

def wall(name,a,b,h=4.4):
    """Wall outside the walkable contour (right side of oriented edge)."""
    a,b=Vector((*a,0)),Vector((*b,0));d=(b-a).normalized();out=Vector((d.y,-d.x,0));L=(b-a).length;mid=(a+b)/2
    root(name)
    def slab(suffix,off,z,th,height,matl):
        o=box(name+suffix,mid+out*off+Vector((0,0,z)),(L,th,height),matl,.003);o.rotation_euler.z=math.atan2(d.y,d.x);return o
    slab('_concrete',.15,h/2,.30,h,'mineral')
    slab('_washable_lower',-.014,.64,.028,1.28,'mineral')
    slab('_skirt',-.031,.10,.062,.20,'darksteel')
    slab('_capping',-.027,1.29,.045,.035,'steel')
    # Full-height panel construction with steel uprights and a restrained route band.
    if L>.35:
        slab('_upper_rail',-.045,h-.24,.09,.18,'darksteel')
        slab('_utility_band',-.006,h-.46,.012,.045,'ochre')
    divisions=max(1,math.ceil(L/2.25))
    for i in range(divisions+1):
        along=max(.045,min(L-.045,L*i/divisions));p=a+d*along
        o=box(name+'_vertical_channel',p-out*.055+Vector((0,0,h/2)),(.095,.11,h),'darksteel',.004);o.rotation_euler.z=math.atan2(d.y,d.x)
        if L>.45:
            for zz in [.20,1.42,h-.30]:
                q=p-out*.12+Vector((0,0,zz));rod(name+'_frame_anchor',q+out*.012,q-out*.007,.011,'steel',6)
    if L>1.3:
        slab('_panel_cross_seam',-.001,h*.61,.005,.008,'darksteel')
        # Broad painterly patches are individually composed, low contrast and planar.
        for i in range(divisions):
            left=L*i/divisions+.17;right=L*(i+1)/divisions-.17
            if right-left<.25:continue
            z0=1.44+random.random()*.4;z1=min(h-.55,z0+.5+random.random()*.7)
            coords=[(left,z0),(left+(right-left)*.28,z0+.16),(right,z1-.17),(right-.13,z1),(left+.11,z1-.11)]
            vv=[tuple(a+d*t-out*.0008+Vector((0,0,z))) for t,z in coords]
            patch=mesh(name+'_paint_field',vv,[tuple(range(5))],'wall_light' if i%2 else 'wall_patch');patch['surface_decal']=True
    # Construction seams stay wide and quiet.
    for i in range(1,int(L/2.5)+1):
        p=a+d*(L*i/(int(L/2.5)+1));o=box(name+'_panel_joint',p+Vector((0,0,(h+1.3)/2)),(.012,.016,h-1.3),'darksteel',0);o.rotation_euler.z=math.atan2(d.y,d.x)
    # Bumper brackets make the protection rail visibly load-bearing.
    if L>1.8:
        z=.57
        rail_a=a+d*.12-out*.11+Vector((0,0,z));rail_b=b-d*.12-out*.11+Vector((0,0,z));beam(name+'_impact_rail',rail_a,rail_b,.115,.075,'rubber')
        for t in [.12,.5,.88]:
            p=a+(b-a)*t;beam(name+'_rail_standoff',p-out*.028+Vector((0,0,z)),p-out*.11+Vector((0,0,z)),.09,.08,'steel')

def door(name,center,w,h,heading=0,closed=False):
    """Local X width, Y depth. Hinges/sliding leaves separated and travel recorded."""
    global PAR
    parent=root(name);cx,cy=center
    def pos(x,y,z):return(cx+x*math.cos(heading)-y*math.sin(heading),cy+x*math.sin(heading)+y*math.cos(heading),z)
    def bx(n,p,d,ma,bev=.004):o=box(name+n,pos(*p),d,ma,bev);o.rotation_euler.z=heading;return o
    for s in [-1,1]:
        bx('_channel_jamb',(s*(w/2+.09),0,h/2),(.18,.26,h),'darksteel')
        bx('_track_wear',(s*(w/2+.013),-.06,h/2),(.025,.11,h),'steel')
        bx('_compression_seal',(s*(w/2+.024),-.13,h/2),(.036,.025,h),'rubber')
        bx('_impact_boot',(s*(w/2+.115),-.035,.45),(.19,.33,.90),'ochre',.015)
        for z in [.17,.77,1.6,h-.15]:bolt(name+'_anchor',pos(s*(w/2+.11),-.18,z),axis=(math.sin(heading),-math.cos(heading),0))
    bx('_lintel',(0,0,h+.13),(w+.40,.32,.26),'darksteel')
    bx('_upper_motor_cover',(0,.05,h+.41),(w+.46,.47,.28),'teal')
    bx('_drive_access',(w*.28,-.191,h+.41),(.63,.026,.22),'old_teal')
    for u in [-.26,.26]:
        for z in [h+.34,h+.48]:bolt(name+'_drive_cover_bolt',pos(w*.28+u,-.21,z),(math.sin(heading),-math.cos(heading),0),.012)
    for s in [-1,1]:
        x=s*(w/4 if closed else w/2+w/4+.15)
        old_names=set(o.name for o in COL.objects)
        leaf=bx('_sliding_leaf',(x,.12,h/2),(w/2-.025,.10,h-.06),'teal_light',.006);leaf['animation_axis']='local X';leaf['travel_m']=w/2+.16;leaf['closed_state']=closed
        # Recessed rigidifying channels, a kick panel and seam tell sheet-metal construction.
        for zz in [.23,h*.45,h-.29]:bx('_leaf_stiffener',(x,.057,zz),(w/2-.19,.025,.055),'teal')
        for edge in [-1,1]:bx('_folded_return',(x+edge*(w/4-.068),.055,h/2),(.045,.036,h-.16),'teal')
        bx('_kick_plate',(x,.049,.40),(w/2-.22,.016,.42),'steel')
        # Pressed corner gussets, seams and localized pallet impact wear.
        for e in [-1,1]:
            bx('_leaf_panel_seam',(x+e*(w/4-.18),.049,h*.69),(.008,.008,h*.45),'darksteel',0)
            for zz in [.18,h-.18]:
                bx('_leaf_gusset',(x+e*(w/4-.16),.03,zz),(.18,.04,.17),'teal',.002)
                bolt(name+'_gusset_rivet',pos(x+e*(w/4-.16),-.006,zz),(math.sin(heading),-math.cos(heading),0),.012)
        # A worn edge on the brushed impact plate follows actual pallet-height contact.
        for i in range(7):
            xx=x+random.uniform(-w/4+.16,w/4-.16)
            bx('_localized_kick_scuff',(xx,.039,random.uniform(.24,.48)),(random.uniform(.035,.11),.002,.006),'darksteel',0)
        if name in ['REFINERY_BOUNDARY','REACTOR_BOUNDARY']:
            for member in COL.objects:
                if member.name not in old_names:member['external_presentation_cap']=True
    bx('_flush_sill',(0,0,-.018),(w,.40,.036),'steel',0)
    bx('_direction_panel',(0,-.19,h+.16),(min(w,2.4),.018,.30),'teal')
    label={'FREIGHT_GATE':'FUEL TRANSFER  /  04','PLANT_PORT':'PLANT SERVICES','CLEAN_PORT':'MEDICAL  /  DOCK','WASTE_PORT':'WASTE TRANSFER','REACTOR_BOUNDARY':'REACTOR APPROACH','REFINERY_BOUNDARY':'REFINERY'}.get(name,name)
    text_obj(name+'_type',label,pos(0,-.207,h+.07),.115,'ivory',(math.pi/2,0,heading))
    PAR=parent

def practical(name,x,y,z=4.4,power=320,cool=False,rotate=0):
    root(name,'ceiling',[(x-.5*math.cos(rotate),y-.5*math.sin(rotate),z),(x+.5*math.cos(rotate),y+.5*math.sin(rotate),z)],(0,0,1))
    for s in [-1,1]:
        xx=x+s*.5*math.cos(rotate);yy=y+s*.5*math.sin(rotate);rod(name+'_drop',(xx,yy,z),(xx,yy,z-.22),.014,'darksteel')
    o=box(name+'_folded_pan',(x,y,z-.27),(1.52,.28,.10),'darksteel');o.rotation_euler.z=rotate
    o=box(name+'_opal_diffuser',(x,y,z-.326),(1.40,.19,.015),'cool_lamp' if cool else 'lamp',.007);o.rotation_euler.z=rotate
    for s in [-1,1]:
        xx=x+s*.73*math.cos(rotate);yy=y+s*.73*math.sin(rotate);o=box(name+'_end_clip',(xx,yy,z-.30),(.045,.3,.08),'steel');o.rotation_euler.z=rotate
    area(name+'_light',(x,y,z-.35),(x,y,0),power,(.78,.88,1) if cool else (1,.84,.64),1.35,.22)

def pipework():
    root('Slice_utility_header','wall',[(1.7,13.2,3.24),(3.1,13.2,3.24)],(0,1,0))
    # Intentional single pressure-air service with flanges and isolator, entering a wall sleeve.
    tube('Air_header',[(-2.26,12.85,3.22),(-1.5,12.85,3.22),(-.9,12.85,3.22),(3.35,12.85,3.22),(3.65,12.85,2.92),(3.65,12.85,2.17)],.067,'teal')
    for x in [-1.35,2.8]:
        rod('Flange',(x-.025,12.85,3.22),(x+.025,12.85,3.22),.11,'steel')
        for t in range(6):
            a=t*math.tau/6;rod('Flange_bolt',(x-.036,12.85+math.cos(a)*.091,3.22+math.sin(a)*.091),(x+.036,12.85+math.cos(a)*.091,3.22+math.sin(a)*.091),.009,'darksteel',6)
    for x in [1.7,3.1]:
        box('Pipe_wall_bracket',(x,13.04,3.15),(.09,.30,.045),'darksteel');box('Pipe_backplate',(x,13.185,3.24),(.12,.03,.30),'steel')
        torus('Pipe_clamp',(x,12.85,3.22),.071,.009,'steel',(0,math.pi/2,0))
    rod('Valve_body',(.1,12.85,3.22),(.50,12.85,3.22),.092,'teal_light')
    rod('Valve_stem',(.3,12.83,3.22),(.3,12.55,3.22),.02)
    torus('Isolator_wheel',(.3,12.55,3.22),.14,.014,'ochre',(math.pi/2,0,0))
    for a in [0,math.tau/3,2*math.tau/3]:rod('Wheel_spoke',(.3,12.55,3.22),(.3+.132*math.cos(a),12.55,3.22+.132*math.sin(a)),.009,'ochre')
    # Wall-mounted regulator terminates the utility drop and remains repairable.
    box('Regulator_backplate',(3.65,13.17,2.23),(.32,.06,.56),'darksteel')
    rod('Regulator_body',(3.65,12.85,2.05),(3.65,12.85,2.34),.085,'teal_light')
    rod('Gauge_standoff',(3.65,13.16,2.28),(3.65,12.73,2.28),.028,'steel')
    rod('Gauge_bezel',(3.65,12.73,2.28),(3.65,12.68,2.28),.105,'darksteel')
    rod('Gauge_face',(3.65,12.676,2.28),(3.65,12.672,2.28),.093,'ivory')
    rod('Gauge_needle',(3.65,12.668,2.28),(3.604,12.668,2.32),.003,'ink')
    for a in [math.pi*.2+i*math.pi*.13 for i in range(11)]:
        rod('Gauge_tick',(3.65+math.cos(a)*.071,12.667,2.28+math.sin(a)*.071),(3.65+math.cos(a)*.081,12.667,2.28+math.sin(a)*.081),.002,'ink',8)
    rod('Regulator_drain',(3.65,12.85,2.05),(3.65,12.85,1.88),.018,'steel')
    box('Regulator_drain_knob',(3.65,12.85,1.92),(.07,.035,.03),'ochre')

def trolley(x=2.65,y=12.32):
    root('Long_cask_carrier','floor',[(x+sx*.79,y+sy*.32,0) for sx in [-1,1] for sy in [-1,1]])
    # 2.20 x .90 m original chassis. Four rubber tyres, forks and swivelling caster plates.
    for sx in [-1,1]:
        for sy in [-1,1]:
            xx=x+sx*.79;yy=y+sy*.32
            rod('Rubber_tyre',(xx,yy-.047,.12),(xx,yy+.047,.12),.12,'rubber',48)
            rod('Wheel_hub',(xx,yy-.052,.12),(xx,yy+.052,.12),.052,'steel')
            rod('Wheel_axle',(xx,yy-.075,.12),(xx,yy+.075,.12),.017,'darksteel')
            for e in [-1,1]:beam('Caster_fork',(xx,yy+e*.067,.12),(xx+.038,yy+e*.067,.29),.035,.029,'steel')
            box('Caster_fork_bridge',(xx+.038,yy,.284),(.08,.17,.024),'steel')
            rod('Caster_swivel',(xx+.038,yy,.27),(xx+.038,yy,.33),.043,'darksteel')
            box('Caster_plate',(xx+.038,yy,.337),(.18,.16,.018),'steel')
    for sy in [-1,1]:
        box('Folded_chassis_web',(x,y+sy*.40,.405),(2.16,.045,.12),'teal')
        for zz in [.35,.46]:box('Chassis_channel_flange',(x,y+sy*.365,zz),(2.16,.11,.025),'teal')
    for xx in [-.97,-.45,.45,.97]:box('Chassis_crossmember',(x+xx,y,.413),(.065,.84,.095),'darksteel')
    box('Carrier_tool_ledge',(x,y-.305,.478),(1.94,.28,.012),'teal')
    for sy in [-1,1]:box('Rubber_bumper',(x,y+sy*.437,.41),(2.2,.026,.09),'rubber',.01)
    # Profile-cut curved saddles on welded open trestles: real load contact at r.245.
    for sx in [-1,1]:
        xx=x+sx*.61
        outline=[(y+math.cos(a)*r,.88+math.sin(a)*r) for r,angles in [(.245,[math.pi*1.09+i*math.pi*.82/20 for i in range(21)]),(.30,[math.pi*1.91-i*math.pi*.82/20 for i in range(21)])] for a in angles]
        verts=[(xx+d,yy,z) for d in [-.045,.045] for yy,z in outline];n=len(outline)
        mesh('Cut_plate_saddle',verts,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'teal_light')
        box('Saddle_foot',(xx,y,.484),(.24,.73,.027),'teal')
        for sy in [-1,1]:
            beam('Saddle_welded_leg',(xx,y+sy*.29,.49),(xx,y+sy*.20,.69),.075,.075,'teal')
            bolt('Saddle_fastener',(xx-.10,y+sy*.29,.505),(0,0,1),.014)
            # Short fillet-weld beads confined to this load-bearing joint.
            rod('Saddle_weld',(xx-.039,y+sy*.28,.505),(xx+.039,y+sy*.28,.505),.005,'steel',12)
    z=.88
    lathe_x('Cartridge_outer_sleeve',[(x-.908,.215),(x-.885,.23),(x+.885,.23),(x+.908,.215)],y,z,'ivory')
    rod('Center_splice_seal',(x-.007,y,z),(x+.007,y,z),.232,'rubber',64)
    for xx in [-.022,.022]:rod('Center_splice_lip',(x+xx-.009,y,z),(x+xx+.009,y,z),.235,'teal',64)
    for xx in [-.93,.93]:rod('Cartridge_end_flange',(x+xx-.022,y,z),(x+xx+.022,y,z),.26,'steel',48)
    for xx in [-.965,.965]:
        rod('Cartridge_end_cap',(x+xx-.01,y,z),(x+xx+.01,y,z),.22,'teal')
        torus('Endplate_gasket',(x+xx,y,z),.217,.006,'rubber',(0,math.pi/2,0))
        for a in [i*math.tau/8 for i in range(8)]:
            sign=1 if xx>0 else -1
            rod('Cap_retention_bolt',(x+xx+sign*.006,y+math.cos(a)*.196,z+math.sin(a)*.196),(x+xx+sign*.010,y+math.cos(a)*.196,z+math.sin(a)*.196),.012,'steel',6)
        rod('Endplate_recess',(x+xx-.009,y,z),(x+xx+.009,y,z),.12,'darksteel')
        rod('Endplate_lock',(x+xx-.010,y,z),(x+xx+.010,y,z),.054,'steel',8)
        sign=1 if xx>0 else -1
        rod('Closure_compression_gasket',(x+xx-sign*.010,y,z),(x+xx-sign*.013,y,z),.225,'rubber')
    for xx in [-.63,.63]:
        rod('Retaining_band',(x+xx-.034,y,z),(x+xx+.034,y,z),.245,'ochre',48)
        box('Overcentre_latch',(x+xx,y-.262,z),(.10,.038,.15),'darksteel',.004)
        for e in [-1,1]:box('Latch_cheek',(x+xx+e*.037,y-.29,z),(.013,.028,.14),'steel')
        rod('Latch_pivot',(x+xx-.048,y-.287,z+.051),(x+xx+.048,y-.287,z+.051),.011,'steel')
        rod('Latch_handle',(x+xx,y-.305,z-.04),(x+xx,y-.305,z+.06),.009,'ochre')
        # Folded lifting ears and a retained pin provide an authored handling silhouette.
        box('Band_lifting_foot',(x+xx,y,z+.247),(.15,.12,.014),'teal')
        torus('Band_lifting_eye',(x+xx,y,z+.289),.045,.012,'steel',(math.pi/2,0,0))
        rod('Retained_pin',(x+xx-.044,y-.30,z-.036),(x+xx+.044,y-.30,z-.036),.007,'steel')
        torus('Pin_pullring',(x+xx+.053,y-.30,z-.036),.018,.003,'steel',(math.pi/2,0,0))
    # Sparse replaced paint and exposed handling wear on flange edges, never global grunge.
    for xx in [-.93,.93]:
        for i in range(6):
            a=3.30+i*.19;da=.075 if i%2 else .12
            verts=[(x+xx-.026,y+math.cos(aa)*rr,z+math.sin(aa)*rr) for aa,rr in [(a,.247),(a+da,.247),(a+da*.81,.258),(a+.02,.258)]]
            mesh('Flange_handling_scuff',verts,[(0,1,2,3)],'chip')
    # A small identity stencil follows the curved casing near its center.
    text_obj('Cartridge_identity','07',(x-.28,y-.231,z+.007),.115,'ink',(math.pi/2,0,0))
    for i,(xx,aa,span) in enumerate([(-.77,3.05,.035),(-.71,3.10,.022),(.73,3.4,.055),(.76,3.43,.029),(.29,3.5,.023)]):
        coords=[(xx,aa), (xx+.018,aa+.07),(xx+span,aa+.12),(xx+span*.9,aa+.06),(xx+.008,aa-.013)]
        mesh('Local_barrel_rub',[(x+u,y+math.cos(v)*.2307,z+math.sin(v)*.2307) for u,v in coords],[(0,1,2,3,4)],'repair' if i%2 else 'chip')
    # Longitudinal protection strips create a specific freight silhouette.
    for a in [math.pi*.18,math.pi*.82,math.pi*1.18,math.pi*1.82]:
        yy=y+math.cos(a)*.23;zz=z+math.sin(a)*.23;rod('Cask_longitudinal_wear_strip',(x-.83,yy,zz),(x+.83,yy,zz),.012,'teal')
    for sy in [-1,1]:
        tube('Push_handle',[(x-1.05,y+sy*.33,.43),(x-1.05,y+sy*.33,1.17),(x-1.03,y+sy*.29,1.21)],.025,'ochre')
    rod('Grip',(x-1.03,y-.29,1.21),(x-1.03,y+.29,1.21),.031,'rubber')
    for sy in [-1,1]:
        xx=x-.79;yy=y+sy*.32
        rod('Brake_hinge',(xx-.045,yy-.070,.21),(xx-.045,yy+.070,.21),.016,'steel')
        o=box('Foot_brake_pedal',(xx-.12,yy,.20),(.15,.10,.025),'ochre',.009);o.rotation_euler.y=.18
        box('Brake_shoe',(xx-.055,yy,.222),(.08,.075,.04),'darksteel',.007)
    # Load card, wedge, rag and handled flask: four purposeful human details.
    box('Docket_board',(x-.33,y-.33,.492),(.36,.23,.016),'darksteel')
    box('Docket',(x-.33,y-.33,.502),(.29,.18,.004),'paper',0)
    text_obj('Docket_type','LOT 07 / RECEIVED',(x-.33,y-.399,.505),.022,'ink',(0,0,0))
    for i in range(4):box('Docket_rule',(x-.34,y-.375+i*.025,.505),(.22,.003,.001),'ink',0)
    # Flattened broad folds on the folded wiping rag.
    verts=[];faces=[]
    for j in range(7):
        for i in range(10):verts.append((x+.48+i*.031,y-.42+j*.031,.495+.009*math.sin(i*1.1+j*.38)))
    for j in range(6):
        for i in range(9):a=j*10+i;faces.append((a,a+1,a+11,a+10))
    rag=mesh('Folded_wiping_cloth',verts,faces,'cloth');so=rag.modifiers.new('Fabric thickness','SOLIDIFY');so.thickness=.004
    box('Wrench_shank',(x+.06,y-.40,.4925),(.23,.028,.017),'steel')
    torus('Wrench_ring',(x-.072,y-.40,.494),.030,.01,'steel')
    # Local scuffs on chassis contact edges only.
    for i in range(16):
        xx=x+random.uniform(-1,.9);box('Chassis_contact_chip',(xx,y-.425,.455),(random.uniform(.01,.055),.004,.004),'chip',0)
    # A substantial wiping cloth draped over the rubber push grip has visible broad folds.
    root('Handle_wiping_cloth','prop',[(x-1.03,y-.12,1.244)],(0,0,-1))
    vv=[];ff=[]
    profile=[(-.087,.81),(-.089,.94),(-.070,1.08),(-.041,1.21),(-.017,1.239),(0,1.244),(.017,1.239),(.041,1.21),(.07,1.08),(.086,.99),(.088,.93)]
    for i,(xx,zz) in enumerate(profile):
        for j in range(13):
            hang=abs(i-5)/5;off=.025*math.sin(j*.85)*hang;vv.append((x-1.03+xx+off,y-.24+j*.022,zz+.032*math.sin(j*.59+.4)*hang))
    for i in range(len(profile)-1):
        for j in range(12):q=i*13+j;ff.append((q,q+1,q+14,q+13))
    ob=mesh('Draped_wiping_cloth',vv,ff,'cloth');so=ob.modifiers.new('Woven cloth thickness','SOLIDIFY');so.thickness=.004;so.offset=0
    for p in ob.data.polygons:p.use_smooth=True

def wall_station():
    station=root('Dispatch_paperwork_station','wall',[(3.1,13.172,1.22)],(0,1,0));station.location.y=-.028
    box('Station_backplate',(3.1,13.18,1.55),(.66,.04,.82),'darksteel')
    box('Stamped_document_pocket',(3.1,13.11,1.36),(.52,.10,.27),'teal')
    box('Pocket_front',(3.1,13.047,1.35),(.55,.024,.23),'teal_light')
    box('Protruding_manifest',(3.04,13.095,1.53),(.33,.004,.38),'paper',0)
    text_obj('Manifest_heading','TRANSFER',(3.04,13.090,1.65),.041,'ink')
    for i in range(5):box('Manifest_lines',(3.04,13.089,1.59-i*.031),(.24,.002,.002),'ink',0)
    box('Keyhook_base',(3.29,13.142,1.79),(.075,.04,.045),'steel')
    tube('Keyhook',[(3.29,13.12,1.79),(3.29,13.03,1.79),(3.29,13.03,1.82)],.007,'steel')
    torus('Keyring',(3.29,13.04,1.765),.022,.004,'steel',(math.pi/2,0,0))
    box('Key_tag',(3.29,13.037,1.713),(.036,.008,.064),'ochre')
    for xx in [2.82,3.38]:
        for zz in [1.20,1.90]:bolt('Station_fixing',(xx,13.151,zz))
    shelf=root('Vacuum_flask_shelf','wall',[(2.28,13.172,1.02)],(0,1,0));shelf.location.y=-.028
    box('Shelf_back',(2.28,13.18,1.08),(.46,.04,.27),'teal')
    box('Folded_shelf',(2.28,13.015,1.00),(.46,.36,.035),'teal')
    for xx in [2.09,2.47]:beam('Shelf_knee',(xx,13.17,.96),(xx,12.89,.98),.025,.05,'darksteel')
    rod('Vacuum_flask',(2.30,13.03,1.018),(2.30,13.03,1.25),.056,'steel')
    rod('Flask_cup',(2.30,13.03,1.25),(2.30,13.03,1.31),.059,'teal')
    tube('Flask_handle',[(2.351,13.03,1.25),(2.403,13.03,1.23),(2.403,13.03,1.09),(2.351,13.03,1.07)],.009,'rubber')

def task_light():
    root('Dispatch_task_sconce','wall',[(2.55,13.2,2.38)],(0,1,0))
    box('Sconce_backplate',(2.55,13.178,2.38),(.22,.044,.36),'darksteel')
    rod('Sconce_arm',(2.55,13.17,2.47),(2.55,12.89,2.47),.025,'steel')
    box('Sconce_internal_lamp_clip',(2.55,12.925,2.439),(.11,.14,.055),'steel')
    # Formed sheet-metal hood with a broad rectangular cutoff and thickened rolled edge.
    verts=[(2.35,12.84,2.51),(2.75,12.84,2.51),(2.71,13.06,2.59),(2.39,13.06,2.59),(2.35,12.84,2.36),(2.75,12.84,2.36)]
    hood=mesh('Task_hood',verts,[(0,1,2,3),(0,4,5,1)],'teal');so=hood.modifiers.new('Folded sheet','SOLIDIFY');so.thickness=.014
    box('Task_diffuser',(2.55,12.925,2.415),(.30,.17,.012),'lamp')
    area('Task_light_pool',(2.55,12.9,2.40),(2.1,11.8,.65),95,(1,.71,.41),.30,.13)

def floor_detail():
    root('Bay_floor_finish')
    # One constrained replacement patch with intentionally quiet surface fields.
    prism('Repaired_slab',[(1.5,11.55),(2.70,11.57),(2.72,12.35),(1.62,12.36)],0,.001,'repair')
    for yy in [11.76,12.92]:
        for xx in [-1.45,-.55,.35,1.25]:box('Parking_mark',(xx,yy,.001),(.53,.035,.002),'ochre',0)
    # A flush drainage grate is a solid surround and actual recessed bars.
    box('Drain_recess',(3.42,12.42,.002),(.44,.58,.003),'darksteel',0)
    for i in range(9):box('Drain_bridge',(3.42,12.17+i*.063,.009),(.39,.017,.014),'steel',.002)
    for xx in [3.20,3.64]:box('Drain_rim',(xx,12.42,.005),(.018,.60,.01),'steel',0)
    for yy in [12.12,12.72]:box('Drain_rim',(3.42,yy,.005),(.46,.018,.01),'steel',0)
    for i in range(7):
        x=-.9+i*.25;prism('Authored_wheel_scuff',[(x,11.65),(x+.14,11.67),(x+.35,11.74),(x+.19,11.72)],.001,.0015,'chip')

CAMERAS=[
 ('C01_ENTRY',(.0,1.4,1.70),(.25,9.9,1.65),25,'entry / freight readability'),
 ('C02_PRIMARY_ROUTE',(3.0,9.0,1.70),(13.0,10.4,1.70),27,'cross passage and gate'),
 ('C03_HERO',(-1.60,7.20,1.70),(2.0,11.4,2.0),23,'cask staging / style slice'),
 ('C04_REVERSE',(1.0,10.5,1.70),(-.15,1.0,1.60),26,'reverse approach'),
 ('C05_EAST_TURN',(11.15,8.45,1.70),(14.2,17.0,1.65),25,'freight ninety-degree turn'),
 ('C06_REACTOR_THRESHOLD',(13.5,19.4,1.70),(14.3,24.0,2.10),26,'outlet / transition'),
 ('C07_BYPASS',(.45,14.0,1.70),(-.2,19.7,1.65),25,'narrow service passage'),
 ('C08_SERVICE_JUNCTION',(1.7,19.85,1.70),(7.6,20.0,1.6),25,'clean services connection'),
 ('C09_MATERIALS',(3.7,9.9,1.60),(2.65,12.32,.85),42,'trolley material and support detail; rebaseline after bypass clearance correction'),
 ('C10_PLANT_HEADER',(-.7,17.2,1.70),(-5.4,17.4,1.45),25,'plant branch dead-end / concealed problem areas')]

def shell(stage):
    collection('01_Architecture')
    cells=json.loads((ROOT/'interface.json').read_text())['floor_cells']
    if stage=='slice':cells=[{'id':'entry','bounds':[-2.2,2.2,1.2,7],'height':4.4},{'id':'west_turn','bounds':[-2.2,4.4,7,13.2],'height':4.4},{'id':'crossing','bounds':[4.4,8.4,7.8,12.2],'height':4.4},{'id':'bypass_west','bounds':[-1.2,1.2,13.2,15.6],'height':3.0}]
    # Exact union boundary by compressed coordinate grid; adjacent floors have no overlap.
    xs=sorted(set(v for c in cells for v in c['bounds'][:2]));ys=sorted(set(v for c in cells for v in c['bounds'][2:]));occupied={}
    for i in range(len(xs)-1):
        for j in range(len(ys)-1):
            x=(xs[i]+xs[i+1])/2;y=(ys[j]+ys[j+1])/2
            for c in cells:
                a,b,d,e=c['bounds']
                if a<x<b and d<y<e:occupied[(i,j)]=c['height'];break
    # Floors are one per source cell (cells deliberately partitioned without overlap).
    for c in cells:
        x0,x1,y0,y1=c['bounds'];h=c['height'];root('Structure_'+c['id'])
        floor=box('Floor_'+c['id'],((x0+x1)/2,(y0+y1)/2,-.12),(x1-x0,y1-y0,.24),'floor',0);floor['support_surface']=True
        ceil=box('Ceiling_'+c['id'],((x0+x1)/2,(y0+y1)/2,h+.1),(x1-x0+.02,y1-y0+.02,.2),'mineral',0);ceil['support_surface']=True
        # Quiet modular floor joints and ceiling coffers provide scale over long runs.
        for axis,lo,hi,other0,other1 in [('X',x0,x1,y0,y1),('Y',y0,y1,x0,x1)]:
            count=max(1,math.ceil((hi-lo)/1.65))
            for ii in range(1,count):
                q=lo+(hi-lo)*ii/count
                box('Slab_joint', (q,(other0+other1)/2,.0006) if axis=='X' else ((other0+other1)/2,q,.0006),(.010,other1-other0,.0012) if axis=='X' else (other1-other0,.010,.0012),'darksteel',0)
        if x1-x0>y1-y0:
            for xx in [x0+.16+i*2.0 for i in range(max(1,math.ceil((x1-x0-.32)/2.0)))]:box('Ceiling_crossmember',(xx,(y0+y1)/2,h-.11),(.12,y1-y0,.22),'darksteel')
        else:
            for yy in [y0+.16+i*2.0 for i in range(max(1,math.ceil((y1-y0-.32)/2.0)))]:box('Ceiling_crossmember',((x0+x1)/2,yy,h-.11),(x1-x0,.12,.22),'darksteel')
    # Close vertical step faces between differing ceiling heights; no open shell gaps.
    for (i,j),h in occupied.items():
        for neighbour,axis,line in [((i+1,j),'X',xs[i+1]),((i,j+1),'Y',ys[j+1])]:
            if neighbour not in occupied or abs(occupied[neighbour]-h)<.001:continue
            low,high=sorted([h,occupied[neighbour]]);root('Ceiling_height_transition')
            if axis=='X':box('Height_step_masonry',(line,(ys[j]+ys[j+1])/2,(low+high)/2),(.20,ys[j+1]-ys[j],high-low),'mineral',0)
            else:box('Height_step_masonry',((xs[i]+xs[i+1])/2,line,(low+high)/2),(xs[i+1]-xs[i],.20,high-low),'mineral',0)
    # Merge collinear boundary segments by facing and line before creating walls.
    edges={}
    for (i,j),h in occupied.items():
        x0,x1,y0,y1=xs[i],xs[i+1],ys[j],ys[j+1]
        for key,neigh,ab in [('S',(i,j-1),(x0,x1,y0)),('E',(i+1,j),(y0,y1,x1)),('N',(i,j+1),(x0,x1,y1)),('W',(i-1,j),(y0,y1,x0))]:
            if neigh not in occupied:edges.setdefault((key,ab[2],h),[]).append(ab[:2])
    for (side,line,h),segs in edges.items():
        segs.sort();merged=[]
        for aa,bb in segs:
            if merged and abs(merged[-1][1]-aa)<1e-5:merged[-1][1]=bb
            else:merged.append([aa,bb])
        for k,(aa,bb) in enumerate(merged):
            # Ports cut the actual union shell; closed operable leaves modeled separately.
            cuts=[]
            if stage=='full':
                for port in json.loads((ROOT/'interface.json').read_text())['ports']:
                    px,py,_=port['center'];dx,dy,_=port['outward'];match=(side=='S' and dy==-1 and abs(py-line)<1e-4)or(side=='N' and dy==1 and abs(py-line)<1e-4)or(side=='W' and dx==-1 and abs(px-line)<1e-4)or(side=='E' and dx==1 and abs(px-line)<1e-4)
                    if match:
                        c=px if side in 'SN' else py;cuts.append((c-port['clear_width']/2,c+port['clear_width']/2,port['clear_height']))
            # Style slice proves a door at the same eventual gate orientation.
            intervals=[(aa,bb)]
            for ca,cb,ch in cuts:
                if cb<=aa or ca>=bb:continue
                nxt=[]
                for p,q in intervals:
                    if ca>p:nxt.append((p,min(ca,q)))
                    if cb<q:nxt.append((max(cb,p),q))
                intervals=[(p,q) for p,q in nxt if q-p>.001]
                if h>ch:
                    root('Port_header_structure');cc=(max(aa,ca)+min(bb,cb))/2;wd=min(bb,cb)-max(aa,ca)
                    box('Port_upper_masonry',(cc,line,(h+ch)/2) if side in 'SN' else (line,cc,(h+ch)/2),(wd,.30,h-ch) if side in 'SN' else (.30,wd,h-ch),'mineral',0)
            for u,v in intervals:
                a,b=((u,line),(v,line)) if side=='S' else ((line,u),(line,v)) if side=='E' else ((v,line),(u,line)) if side=='N' else ((line,v),(line,u))
                wall('Wall_'+side+str(line)+'_'+str(k)+'_'+str(u),a,b,h)
    # Every solid architecture face may support a prop; validator still raycasts actual geometry.
    for o in COL.objects:
        if o.type=='MESH':o['support_surface']=True
    collection('02_Structure_and_services')
    root('Bay_steelwork','wall',[(-2.2,7.25,3.64),(-2.2,12.95,3.64)],(-1,0,0))
    # Specific I-section girder, flange/web construction with bolted corbels.
    for yy in [7.25,12.95]:
        for zz in [4.04,4.28]:box('Girder_flange',(1.1,yy,zz),(6.54,.22,.045),'darksteel')
        box('Girder_web',(1.1,yy,4.16),(6.54,.07,.24),'darksteel')
        for xx in [-2.13,4.33]:
            beam('Girder_knee',(xx,yy,3.5),(xx+(.4 if xx<0 else -.4),yy,4.04),.10,.11,'teal')
            box('Bearing_plate',(xx,yy,3.64),(.14,.35,.5),'steel')
    pipework()
    if stage=='full':
        root('Longitudinal_tray','ceiling',[(xx,8.14,4.4) for xx in [5.3,8.5,11.8,15.1]],(0,0,1))
        for yy in [8.0,8.28]:
            box('Cable_tray_rail',(9.9,yy,3.78),(11.8,.035,.12),'darksteel')
        for xx in [4.6+i*.5 for i in range(23)]:box('Cable_tray_rung',(xx,8.14,3.73),(.024,.28,.026),'steel')
        for i in range(3):tube('Power_cable',[(4,8.04+i*.055,3.77),(15.3,8.04+i*.055,3.77),(15.85,8.6+i*.055,3.77),(15.85,20.6,3.77)],.021,'rubber')
        for xx in [5.3,8.5,11.8,15.1]:
            rod('Tray_suspension',(xx,8.14,4.4),(xx,8.14,3.69),.012,'steel')
            box('Tray_hanger_saddle',(xx,8.14,3.704),(.09,.34,.035),'steel')
        root('Service_pipework','ceiling',[(xx,19.45,3) for xx in [2,5,8,11]],(0,0,1))
        tube('Service_air_loop',[(.91,13.2,2.67),(.91,19.2,2.67),(1.35,19.45,2.67),(11.9,19.45,2.67)],.052,'teal')
        for yy in [14.1,16.3,18.4]:box('Pipe_support_standoff',(1.05,yy,2.67),(.30,.045,.08),'steel')
        for xx in [2,5,8,11]:rod('Pipe_hanger',(xx,19.45,3),(xx,19.45,2.61),.012,'darksteel')

DETAIL_SOURCE=Path(__file__).resolve().with_name('valorant_details.py')
exec(compile(DETAIL_SOURCE.read_text(encoding='utf-8'),str(DETAIL_SOURCE),'exec'))
shell(A.stage)
collection('03_Thresholds')
door('FREIGHT_GATE',(6.35,10),3.4,3.4,-math.pi/2,False)
gate_drive_detail()
if A.stage=='full':
    # Main gate closure needs an architectural bulkhead around its track.
    root('Freight_bulkhead')
    for yy in [7.93,12.07]:box('Gate_steel_return',(6.35,yy,1.7),(.34,.26,3.4),'teal')
    box('Gate_crown',(6.35,10,4.10),(.45,4.4,.60),'mineral')
    door('PLANT_PORT',(-5.4,17.4),2.0,2.5,-math.pi/2,True)
    door('CLEAN_PORT',(6.6,21),2.0,2.5,0,True)
    door('WASTE_PORT',(16.4,16),2.4,3.0,-math.pi/2,True)
    # Presentation caps are section-owned removable integration leaves, never edits to neighbors.
    door('REACTOR_BOUNDARY',(14.2,24),5.0,5.0,0,True)
    door('REFINERY_BOUNDARY',(0,0),2.6,3.0,math.pi,True)
collection('04_Freight_and_dressing');trolley();wall_station();floor_detail();task_light();detail_dressing(A.stage)
collection('05_Practical_lighting')
practical('Staging_warm_key',.15,11.78,4.4,270)
practical('Gate_cool_fill',3.32,8.45,4.4,170,True,math.pi/2)
if A.stage=='full':
    for n,x,y,h,p,co,r in [('Entry',.0,4.0,4.4,270,False,0),('Cross',8.2,10,4.4,310,False,math.pi/2),('East',14.5,10.8,4.4,330,True,0),('Delivery',14.2,17,4.4,310,False,0),('Reactor',14.2,22.8,5,480,True,0),('Bypass',0,16.5,3,155,False,0),('North_service',4.6,19.8,3,155,True,math.pi/2),('North_service_2',10,19.8,3,130,False,math.pi/2),('Plant',-3.6,17.4,3,135,False,math.pi/2)]:practical(n,x,y,h,p,co,r)
else:
    practical('Slice_entry',0,4,4.4,220)
    practical('Slice_cross',7.5,10,4.4,240,False,math.pi/2)
    practical('Slice_service',0,14.5,3,90)
    area('Slice_low_fill',(-1.8,7.5,2.6),(2.65,12,1),90,(.83,.88,1),2)

collection('06_Cameras_and_metadata');PAR=None
for name,loc,target,lens,role in CAMERAS:
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);COL.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.04;d.clip_end=150;o['evaluation_role']=role
S.camera=bpy.data.objects['C03_HERO']
S.world=bpy.data.worlds.new('Restrained ambient');S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.16,.2,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.18
S.render.engine='CYCLES';S.cycles.samples=A.samples;S.cycles.use_denoising=True;S.cycles.seed=71;S.cycles.max_bounces=8
S.render.resolution_x=A.width;S.render.resolution_y=round(A.width*.6666667);S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=.10
S['section']='fuel-corridor';S['revision']=A.revision;S['stage']=A.stage;S['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();S['original_geometry']=True
S['fixed_camera_spec']=json.dumps(CAMERAS)
S['detail_source_sha256']=hashlib.sha256(DETAIL_SOURCE.read_bytes()).hexdigest()
# Resolve and record exact intended support targets from authored anchors. The independent
# validator checks both anchor-to-support and anchor-to-assembly mesh, rather than trusting this.
bpy.context.view_layer.update()
from mathutils.bvhtree import BVHTree
deps=bpy.context.evaluated_depsgraph_get();surfaces=[]
for o in S.objects:
    if o.type not in ['MESH','CURVE','FONT']:continue
    if o.type=='CURVE' and o.data.bevel_depth==0:continue
    ev=o.evaluated_get(deps);me=ev.to_mesh()
    if me and len(me.polygons):
        vv=[o.matrix_world@v.co for v in me.vertices];ff=[list(p.vertices) for p in me.polygons];surfaces.append((o,BVHTree.FromPolygons(vv,ff)))
    ev.to_mesh_clear()
for o in list(S.objects):
    if 'support_anchors' not in o:continue
    targets=[];direction=Vector(o['support_direction'])
    for anchor in json.loads(o['support_anchors']):
        start=Vector(anchor)-direction*.012;hits=[]
        for surface,bvh in surfaces:
            ancestor=surface
            while ancestor.parent:ancestor=ancestor.parent
            if ancestor==o:continue
            co,n,index,distance=bvh.ray_cast(start,direction,.040)
            if co is not None:hits.append((abs(distance-.012),surface.name))
        targets.append(min(hits)[1] if hits else 'UNRESOLVED_SUPPORT')
    o['support_targets']=json.dumps(targets);o['support_angle_tolerance']=12.
out=ROOT/'production/renders/review'/A.revision;out.mkdir(parents=True,exist_ok=True)
blend=ROOT/'blender/Fuel_Corridor.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
(out/'build_manifest.json').write_text(json.dumps({'revision':A.revision,'stage':A.stage,'source_sha256':S['source_sha256'],'objects':len(S.objects),'cameras':CAMERAS,'blend':str(blend),'samples':A.samples,'width':A.width},indent=2))
if A.render:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='HIP';prefs.get_devices()
    for dev in prefs.devices:dev.use=dev.type=='HIP'
    S.cycles.device='GPU'
    names=[c[0] for c in CAMERAS] if A.render=='all' else A.render.split(',')
    for name in names:S.camera=bpy.data.objects[name];S.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
print('FUEL_BUILD_COMPLETE',A.revision,len(S.objects),str(blend))
