"""Original Waste Storage environment. Blender 5.2, factory-empty reproducible authoring.

blender --background --factory-startup --python build_scene.py -- --stage slice --output file.blend --revision slice-r01
This entrypoint saves only. GPU rendering belongs to the shared facility GPU gate.
"""
import bpy, math, json, argparse, sys, os, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
from math import sin, cos, pi

P=argparse.ArgumentParser(); P.add_argument('--stage',choices=['slice','full'],default='slice'); P.add_argument('--output',required=True); P.add_argument('--revision',default='slice-r01')
A=P.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene; S.unit_settings.system='METRIC'; S.unit_settings.length_unit='METERS'; S.unit_settings.scale_length=1
S['section']='waste-storage'; S['revision']=A.revision; S['build_stage']=A.stage; S['original_geometry']=True; S['build_source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
COL={}
for n in ['00_ARCHITECTURE','01_RECEIVING','02_MONITOR_BOOTH','03_TRANSFER_CASK','04_STORAGE_CELLS','05_VENTILATION','06_HUMAN_TRACES','07_LIGHTS','08_CAMERAS','09_SUPPORT_ANCHORS']:
    c=bpy.data.collections.new(n); S.collection.children.link(c); COL[n]=c
ACTIVE='00_ARCHITECTURE'

def link(o,collection=None):
    for c in list(o.users_collection): c.objects.unlink(o)
    COL[collection or ACTIVE].objects.link(o)

def mat(name,color,rough=.65,metal=0,noise=.018,bump=0,emission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    nt=m.node_tree; bs=nt.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    if noise:
        tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=3.4; tex.inputs['Detail'].default_value=1.0; tex.inputs['Roughness'].default_value=.45
        ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.12; ramp.color_ramp.elements[0].color=(*[max(0,v-noise) for v in color],1); ramp.color_ramp.elements[1].position=.88; ramp.color_ramp.elements[1].color=(*[min(1,v+noise) for v in color],1)
        nt.links.new(tex.outputs['Fac'],ramp.inputs[0]); nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
        rr=nt.nodes.new('ShaderNodeMapRange'); rr.inputs['From Min'].default_value=0; rr.inputs['From Max'].default_value=1; rr.inputs['To Min'].default_value=rough-.07; rr.inputs['To Max'].default_value=min(1,rough+.05); nt.links.new(tex.outputs['Fac'],rr.inputs[0]); nt.links.new(rr.outputs[0],bs.inputs['Roughness'])
    if bump:
        tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=95; tex.inputs['Detail'].default_value=1
        bn=nt.nodes.new('ShaderNodeBump'); bn.inputs['Strength'].default_value=.16; bn.inputs['Distance'].default_value=bump; nt.links.new(tex.outputs['Fac'],bn.inputs['Height']); nt.links.new(bn.outputs[0],bs.inputs['Normal'])
    if emission:
        bs.inputs['Emission Color'].default_value=(*color,1); bs.inputs['Emission Strength'].default_value=emission
    return m
M={
 'concrete':mat('Warm cast concrete • broad mineral tone',(.42,.40,.35),.9,noise=.025,bump=.008),
 'plaster':mat('Painted mineral wall • warm cream',(.50,.47,.40),.91,noise=.018,bump=.003),
 'floor':mat('Sealed concrete • satin dry',(.245,.26,.245),.83,noise=.017,bump=.004),
 'teal':mat('Teal baked steel • maintained',(.032,.095,.110),.48,.65,.007,.001),
 'teallight':mat('Repainted teal panel',(.05,.135,.15),.64,.4,.008),
 'dark':mat('Graphite powder coated steel',(.045,.06,.06),.62,.45,.005),
 'steel':mat('Brushed zinc steel',(.28,.32,.33),.30,.88,.020),
 'cream':mat('Ivory enamel steel',(.44,.445,.38),.65,.38,.016,.001),
 'orange':mat('Maintenance ochre enamel',(.48,.185,.035),.52,.4,.012),
 'rubber':mat('Carbon rubber • soft matte',(.019,.025,.026),.93,0,.003,.001),
 'plastic':mat('ABS instrument housing',(.10,.125,.12),.48,0,.004),
 'fabric':mat('Washed canvas',(.17,.205,.15),.98,0,.016,.003),
 'paper':mat('Inventory paper',(.71,.7,.59),.93,0,.007),
 'ink':mat('Graphite lettering',(.035,.046,.046),.85,0,0),
 'white':mat('Warm white marking',(.74,.73,.62),.81,0,.005),
 'red':mat('Emergency red paint',(.42,.048,.029),.59,.15,.006),
 'light':mat('Opal warm lamp diffuser',(.95,.81,.58),.4,0,0,emission=3),
 'screen':mat('Phosphor low output screen',(.17,.30,.21),.52,0,0,emission=.3),
 'scuff':mat('Dry wheel abrasion',(.155,.175,.163),.94,0,.008),
 'chip':mat('Oxidised exposed primer',(.24,.235,.19),.82,.25,.011),
 'woodedge':mat('Phenolic desk edge',(.19,.17,.115),.76,0,.009)
}
M['glass']=mat('Wired safety glazing',(.80,.88,.84),.065,0,0); gb=M['glass'].node_tree.nodes.get('Principled BSDF'); gb.inputs['Transmission Weight'].default_value=1.; gb.inputs['IOR'].default_value=1.46

def root(name,target='Floor',direction=(0,0,-1),anchors=(),irregular=False):
    o=bpy.data.objects.new(name,None); link(o); o.empty_display_size=.08
    o['support_required']=True; o['support_target']=target; o['support_direction']=json.dumps(direction); o['support_max_gap']=.005; o['support_max_penetration']=.002; o['support_angle_tolerance_deg']=12.; o['support_irregular']=irregular
    names=[]
    for i,co in enumerate(anchors):
        an=bpy.data.objects.new(name+'__CONTACT_%02d'%i,None); COL['09_SUPPORT_ANCHORS'].objects.link(an); an.location=co; an.parent=o; an.empty_display_size=.035; an['support_anchor']=True; names.append(an.name)
    o['support_anchors']=json.dumps(names)
    return o

def finish(o,name,material=None,parent=None,bevel=0,solid=True):
    o.name=name; link(o)
    if material: o.data.materials.append(M[material] if isinstance(material,str) else material)
    o['collision_role']='solid' if solid else 'noncolliding'
    if parent: o.parent=parent; o['support_role']='assembly_part'; o['support_root']=parent.name if parent.get('support_required') else parent['support_root']
    else: o['support_role']='architectural'
    if bevel:
        m=o.modifiers.new('Fabricated edge finish','BEVEL'); m.width=bevel; m.segments=3
        m=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL'); m.keep_sharp=True; m.weight=25
    return o

def box(name,co,dim,material,parent=None,bevel=.01,rot=None,solid=True):
    bpy.ops.mesh.primitive_cube_add(size=1,location=co); o=bpy.context.object; o.scale=dim; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if rot: o.rotation_euler=rot
    return finish(o,name,material,parent,min(bevel,min(dim)*.22),solid)

def cyl(name,co,r,depth,material,parent=None,axis='Z',vertices=48,bevel=.004):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=co); o=bpy.context.object
    if axis=='X': o.rotation_euler[1]=pi/2
    elif axis=='Y': o.rotation_euler[0]=pi/2
    for p in o.data.polygons: p.use_smooth=len(p.vertices)==4
    return finish(o,name,material,parent,bevel)

def sphere(name,co,scale,material,parent):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=co); o=bpy.context.object; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for p in o.data.polygons:p.use_smooth=True
    return finish(o,name,material,parent)

def rod(name,p1,p2,r,material,parent=None):
    a,b=Vector(p1),Vector(p2); o=cyl(name,(a+b)/2,r,(b-a).length,material,parent,bevel=.002); o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return o

def tube(name,points,r,material,parent=None):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.resolution_u=12; cu.bevel_depth=r; cu.bevel_resolution=3;cu.use_fill_caps=True
    sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(points)-1)
    for p,co in zip(sp.bezier_points,points):p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,cu); COL[ACTIVE].objects.link(o); return finish(o,name,material,parent)

def lathe(name,cx,cy,profile,material,parent,n=64):
    vv=[(cx+r*cos(2*pi*i/n),cy+r*sin(2*pi*i/n),z) for r,z in profile for i in range(n)]
    ff=[]
    for j in range(len(profile)-1):
        for i in range(n):ff.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    ff.append(tuple(reversed(range(n)))); ff.append(tuple((len(profile)-1)*n+i for i in range(n)))
    me=bpy.data.meshes.new(name); me.from_pydata(vv,[],ff); me.update(); o=bpy.data.objects.new(name,me); COL[ACTIVE].objects.link(o)
    for p in me.polygons:p.use_smooth=len(p.vertices)==4
    return finish(o,name,material,parent,.004)

def torus(name,co,major,minor,material,parent,rot=None):
    bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=12,location=co,major_radius=major,minor_radius=minor); o=bpy.context.object
    if rot:o.rotation_euler=rot
    for p in o.data.polygons:p.use_smooth=True
    return finish(o,name,material,parent)

def mesh(name,verts,faces,material,parent,bevel=0):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new(name,me); COL[ACTIVE].objects.link(o); return finish(o,name,material,parent,bevel)

def text(name,body,co,size,material,parent,rot=(pi/2,0,0),align='CENTER'):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=body; cu.size=size; cu.align_x=align; cu.align_y='CENTER'; cu.extrude=.0005; cu.resolution_u=8
    o=bpy.data.objects.new(name,cu); COL[ACTIVE].objects.link(o); o.location=co; o.rotation_euler=rot;o['open_surface_reason']='Non-collision dimensional glyph curves; font tessellation is intentionally exempt from watertight solid collision.'; return finish(o,name,material,parent,solid=False)

def bolt(name,co,parent,axis='Z',r=.023):return cyl(name,co,r,.017,'steel',parent,axis,6,.001)

def chip(name,center,u,v,w,h,parent,material='chip'):
    # Sparse hand-authored contact abrasion, deliberately unequal torn outline.
    pts=[(-.5,-.27),(-.35,-.5),(-.08,-.30),(.18,-.48),(.5,-.21),(.41,.13),(.22,.22),(.11,.5),(-.17,.35),(-.45,.47)]
    c=Vector(center);u=Vector(u);v=Vector(v)
    vv=[tuple(c+u*(x*w)+v*(y*h)) for x,y in pts]
    o=mesh(name,vv,[tuple(range(len(vv)))],material,parent)
    m=o.modifiers.new('Paint-thickness abrasion decal','SOLIDIFY');m.thickness=.0006
    o['collision_role']='noncolliding'
    return o

def gauge(x,y,z,parent):
    q=root('Dose-rate analogue instrument',target='Desk laminate worktop',anchors=[(x,y,.82)],irregular=True)
    box('Dose instrument mounting foot',(x,y,.838),(.25,.21,.036),'dark',q,.005)
    box('Dose meter enclosure',(x,y,.995),(.29,.19,.28),'teal',q,.016)
    cyl('Dose meter bezel',(x,y+.108,1.02),.102,.038,'steel',q,'Y')
    cyl('Dose meter black surround',(x,y+.13,1.02),.091,.012,'rubber',q,'Y')
    cyl('Dose dial ivory face',(x,y+.138,1.02),.085,.004,'paper',q,'Y')
    for i in range(9):
        a=pi*.10+i*pi*.10
        rod('Dose dial tick',(x+.066*cos(a),y+.142,1.02+.066*sin(a)),(x+.078*cos(a),y+.142,1.02+.078*sin(a)),.0017,'ink',q)
    rod('Dose meter needle',(x,y+.143,1.02),(x-.056,y+.143,1.055),.002,'red',q)
    text('Dose dial units','mSv/h',(x,y+.145,.992),.017,'ink',q,(pi/2,0,pi))
    cyl('Dose meter knob',(x+.082,y+.116,.904),.020,.030,'rubber',q,'Y')
    tube('Dose meter cord',[(x-.10,y-.08,.96),(x-.24,y-.09,.89),(x-.25,y+.1,.84),(x-.19,y+.13,.84)],.008,'rubber',q)

def wall_sign(name,body,co,dim,size,root_obj,material='teal',axis='Y'):
    o=box(name+' backing',co,dim,material,root_obj,.007)
    if axis=='Y':text(name+' legend',body,(co[0],co[1]-.5*dim[1]-.002,co[2]),size,'white',root_obj)
    if axis=='X':text(name+' legend',body,(co[0]-.5*dim[0]-.002,co[1],co[2]),size,'white',root_obj,(pi/2,0,-pi/2))
    return o

def floor_rect(name,x,y,w,d,material='white'):
    r=root(name,anchors=[(x,y,0)]); o=box(name+' paint',(x,y,.001),(w,d,.002),material,r,0,solid=False); o['collision_role']='route_marking'; return o

def light(name,co,target,power,size,color=(1,.81,.58),shape='DISK',size_y=None):
    d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.shape=shape; d.size=size; d.color=color
    if size_y is not None and shape=='RECTANGLE':d.size_y=size_y
    o=bpy.data.objects.new(name,d); COL['07_LIGHTS'].objects.link(o); o.location=co; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler(); return o

def ceiling_fixture(name,x,y,z=4.65,length=1.5,power=450):
    r=root(name,target='Ceiling',direction=(0,0,1),anchors=[(x,y,4.8)])
    rod(name+' drop',(x,y,4.8),(x,y,z+.045),.018,'steel',r)
    box(name+' folded reflector',(x,y,z),(.32,length,.11),'dark',r,.015)
    box(name+' opal trough',(x,y,z-.063),(.20,length-.10,.024),'light',r,.009)
    for yy in [y-length/2+.06,y+length/2-.06]:box(name+' end clip',(x,yy,z-.07),(.33,.03,.04),'steel',r,.003)
    light(name+' working pool',(x,y,z-.09),(x,y,0),power,length,(1,.85,.66),'RECTANGLE',.35)

def architecture():
    global ACTIVE; ACTIVE='00_ARCHITECTURE'
    depth=18 if A.stage=='full' else 4.6
    box('Floor',(0,depth/2,-.14),(12.4,depth+.5,.28),'floor',bevel=.015)
    box('West_Wall',(-6.16,depth/2,2.4),(.32,depth,4.8),'plaster',bevel=.006)
    # East receiving personnel portal: 1.2 m x 2.3 m.
    box('East_Wall_Front',(6.16,.9,2.4),(.32,1.8,4.8),'plaster')
    box('East_Wall_Rear',(6.16,(3+depth)/2,2.4),(.32,depth-3,4.8),'plaster')
    box('East_Wall_Lintel',(6.16,2.4,3.55),(.32,1.2,2.5),'plaster')
    box('Front_Wall_West',(-3.83,-.16,2.4),(4.66,.32,4.8),'plaster'); box('Front_Wall_East',(3.83,-.16,2.4),(4.66,.32,4.8),'plaster')
    box('Front_Wall_Lintel',(0,-.16,4),(3,.32,1.6),'plaster')
    box('Ceiling',(0,depth/2,4.92),(12.4,depth+.3,.24),'concrete')
    box('Concrete west wall plinth',(-5.95,depth/2,.14),(.1,depth,.28),'concrete',bevel=.009)
    for yy,dd in [(.9,1.8),((depth+3)/2,depth-3)]:box('Concrete east wall plinth',(5.95,yy,.14),(.1,dd,.28),'concrete',bevel=.009)
    for y in ([.25,4.45,9.1,13.9,17.75] if A.stage=='full' else [.25,4.45]):
        box('Portal frame top',(0,y,4.54),(12.05,.19,.25),'dark',bevel=.006)
        for x in [-5.89,5.89]:
            box('Portal column',(x,y,2.27),(.20,.19,4.54),'dark',bevel=.005)
            box('Column base shoe',(x,y,.1),(.30,.31,.20),'steel',bevel=.006)
    # Deliberate poured floor joints and sparse route wheel abrasion.
    for y in [1.0,4.45]+([8.95,13.8,17.1] if A.stage=='full' else []):floor_rect('Floor construction joint',0,y,12,.009,'scuff')
    for x in [-3,3]:floor_rect('Floor slab joint',x,depth/2,.009,depth,'scuff')
    for x in [-1.48,1.48]:floor_rect('Threshold guide stripe',x,.40,.045,.8)
    # Roller entry is genuinely open and coiled above the portal.
    r=root('Receiving roller assembly',target='Front_Wall_Lintel',direction=(0,-1,0),anchors=[(0,0,3.55)])
    box('Roller fixing backplate',(0,.035,3.55),(3.45,.07,.54),'dark',r,.008)
    cyl('Rolled steel curtain',(0,.35,3.59),.28,3.17,'steel',r,'X')
    for x in [-1.57,1.57]:box('Door guide channel',(x,.095,1.825),(.12,.16,3.65),'dark',r,.006)
    for x in [-1.4+i*.07 for i in range(41)]:cyl('Rolled curtain seam',(x,.35,3.59),.284,.006,'dark',r,'X',32,.001)
    box('Curtain hood',(0,.35,3.90),(3.48,.71,.10),'teal',r,.018)
    floor_rect('Receiving threshold steel',0,.02,3,.22,'steel')
    # Side exit leaf sits beyond the open interface plane, hingeable at jamb.
    r=root('Personnel exit frame',target='East_Wall_Lintel',direction=(1,0,0),anchors=[(6,2.4,2.52)])
    box('Personnel frame header',(5.94,2.4,2.40),(.12,1.46,.20),'dark',r,.006)
    for y in [1.735,3.065]:box('Personnel frame jamb',(5.94,y,1.15),(.12,.13,2.30),'dark',r,.006)
    wall_sign('Exit direction','EXIT',(5.94,2.4,2.57),(.12,.55,.20),.11,r,'teal','X')
    # Actual support connects upper mounting ear to lintel.
    box('Exit mounting ear',(5.97,2.4,2.52),(.06,.12,.12),'steel',r,.002)
    if A.stage=='full':
        box('Rear_Wall_Left',(-3.6,18.16,2.4),(4.8,.32,4.8),'plaster');box('Rear_Wall_Right',(3.6,18.16,2.4),(4.8,.32,4.8),'plaster');box('Rear_Wall_Lintel',(0,18.16,3.8),(2.4,.32,2),'plaster')

def booth():
    global ACTIVE; ACTIVE='02_MONITOR_BOOTH'
    r=root('Monitoring booth shell',anchors=[(-5.62,.52,0),(-2.45,.52,0),(-2.45,3.68,0)],irregular=True)
    # Sill walls are broad, cream, framed as prefabricated insulated panels.
    box('Booth front insulated sill',(-4.08,.49,.55),(3.28,.14,1.1),'cream',r,.013)
    box('Booth rear insulated sill',(-4.08,3.73,.55),(3.28,.14,1.1),'cream',r,.013)
    # East face broken around a 1.1 m opening y1.65..2.75.
    for y,d in [(1.055,1.19),(3.275,1.05)]:box('Booth return sill',(-2.45,y,.55),(.14,d,1.1),'teal',r,.012)
    box('Booth front kickrail',(-4.08,.396,.2),(3.28,.05,.22),'teal',r,.009)
    box('Booth rear kickrail',(-4.08,3.824,.2),(3.28,.05,.22),'teal',r,.009)
    for x in [-5.15,-3.20]:
        chip('Booth trolley scuff',(x,3.850,.22),(1,0,0),(0,0,1),.21,.024,r,'steel')
    for y in [1.08,3.31]:
        box('Booth panel inset joint',(-2.524,y,.61),(.012,.006,.81),'dark',r,.001)
    for x in [-5.50,-4.53,-3.55,-2.58]:
        for z in [.12,1.06]:bolt('Booth accessible panel screw',(x,3.806,z),r,'Y',.011)
    # Pinned glazing frames; glass remains transparent with readable edges.
    for y in [.49,3.73]:
        for x in [-5.65,-4.6,-3.55,-2.45]:box('Booth window mullion',(x,y,1.90),(.065,.14,1.6),'teal',r,.005)
        for z in [1.10,2.62]:box('Booth glazing rail',(-4.05,y,z),(3.32,.14,.07),'teal',r,.005)
        for x in [-5.125,-4.075,-3.025]:box('Booth safety glass',(x,y,1.86),(.976,.017,1.45),'glass',r,.001)
    for y,d in [(1.055,1.06),(3.29,.92)]:
        box('Booth side safety glass',(-2.45,y,1.86),(.017,d,1.44),'glass',r,.001)
        for z in [1.10,2.62]:box('Booth side glazing rail',(-2.45,y,z),(.14,d+.13,.07),'teal',r,.005)
    for i,y in enumerate([.49,1.615,2.785,3.73]):box('Booth east stile %02d'%i,(-2.45,y,1.35),(.14,.07,2.7),'teal',r,.006)
    box('Booth upper east fascia',(-2.45,2.11,2.78),(.20,3.42,.25),'teal',r,.007)
    box('Booth front upper fascia',(-4.08,.49,2.78),(3.46,.2,.25),'teal',r,.007)
    box('Booth rear upper fascia',(-4.08,3.73,2.78),(3.46,.2,.25),'teal',r,.007)
    box('Booth suspended cap',(-4.1,2.11,2.945),(3.55,3.46,.08),'cream',r,.007)
    # Door recessed and closed inside boundary. Source has real hinge origin.
    d=bpy.data.objects.new('Booth_Door_PIVOT',None); COL[ACTIVE].objects.link(d); d.parent=r; d['support_role']='assembly_part'; d['support_root']=r.name; d['interaction']='controlled_access'; d['hinge_axis']='Z'; d['opening_degrees']=95
    door_parts=[]
    door_parts.append(box('Booth door solid lower',(-2.495,2.2,.54),(.056,1.075,1.08),'teallight',r,.012))
    door_parts.append(box('Booth door glazed upper',(-2.495,2.2,1.70),(.018,.91,1.10),'glass',r,.001))
    for y in [1.676,2.724]:door_parts.append(box('Door leaf edge',(-2.495,y,1.145),(.07,.06,2.29),'teal',r,.004))
    for z in [1.13,2.27]:door_parts.append(box('Door leaf cross rail',(-2.495,2.2,z),(.07,1.08,.07),'teal',r,.004))
    for z in [.28,1.99]:cyl('Booth hinge barrel',(-2.495,2.75,z),.025,.12,'steel',r)
    door_parts.append(rod('Booth door lever',(-2.38,1.82,1.08),(-2.38,2.01,1.08),.013,'steel',r))
    door_parts.append(rod('Door lever spindle',(-2.49,1.82,1.08),(-2.38,1.82,1.08),.012,'steel',r))
    door_parts.append(box('Door lock escutcheon',(-2.447,1.82,1.075),(.025,.055,.18),'steel',r,.007))
    # Parent geometry to pivot while preserving source world transforms.
    d.location=(-2.495,2.75,0);bpy.context.view_layer.update()
    for o in door_parts:
        w=o.matrix_world.copy(); o.parent=d; o.matrix_world=w
    d.rotation_euler[2]=-pi/2
    # Short monitoring desk behind the glazing, shaped slab and steel cantilever legs.
    q=root('Monitor desk',anchors=[(-5.34,1.02,0),(-3.29,1.02,0),(-5.34,1.51,0),(-3.29,1.51,0)],irregular=True)
    box('Desk laminate worktop',(-4.30,1.3,.79),(2.35,.72,.06),'cream',q,.007)
    box('Desk exposed phenolic edge',(-4.30,1.665,.785),(2.33,.022,.038),'woodedge',q,.003)
    for x in [-5.34,-3.29]:
        box('Desk foot',(x,1.265,.032),(.11,.62,.064),'dark',q,.009)
        box('Desk tubular standard',(x,1.18,.40),(.06,.06,.74),'teal',q,.008)
        box('Desk underarm',(x,1.28,.73),(.055,.61,.06),'teal',q,.006)
    box('Desk service modesty panel',(-4.3,1.59,.49),(2.13,.045,.43),'teal',q,.008)
    # Angled late-industrial monitor enclosure, purposeful dial and small data display.
    v=root('Inventory instrument',target='Desk laminate worktop',anchors=[(-4.55,1.34,.82)],irregular=True)
    box('Instrument foot',(-4.55,1.34,.845),(.5,.32,.05),'dark',v,.008)
    rod('Instrument stalk',(-4.55,1.34,.87),(-4.55,1.39,1.04),.028,'steel',v)
    box('Inventory monitor case',(-4.55,1.39,1.25),(.62,.27,.46),'plastic',v,.037,rot=(-.10,0,0))
    box('Recessed monitor bezel',(-4.55,1.237,1.25),(.53,.026,.35),'rubber',v,.017)
    box('Inventory display',(-4.55,1.219,1.26),(.45,.006,.278),'screen',v,.009)
    text('Inventory screen primary','RECEIPT 042',(-4.55,1.212,1.34),.032,'white',v)
    text('Inventory screen state','SEALED /  03',(-4.55,1.211,1.20),.03,'white',v)
    for xx in [-4.72,-4.56,-4.40]:box('Screen low graph',(xx,1.211,1.273),(.1,.002,.006),'white',v,0)
    for xx in [-4.79,-4.31]:
        for zz in [1.09,1.41]:bolt('Monitor captive face screw',(xx,1.213,zz),v,'Y',.009)
    for xx in [-4.70,-4.58,-4.46]:cyl('Monitor physical selector',(xx,1.226,1.065),.020,.023,'dark',v,'Y')
    for i in range(8):box('Instrument cooling slot',(-4.856,1.30+i*.02,1.24),(.003,.01,.18),'rubber',v,.001)
    v.matrix_world=Matrix.Translation(Vector((-4.55,1.34,0))) @ Matrix.Rotation(pi,4,'Z') @ Matrix.Translation(Vector((4.55,-1.34,0)))
    # A grounded keyboard tray and analogue dose-rate head make the desk a monitoring station.
    h=root('Physical monitoring controls',target='Desk laminate worktop',anchors=[(-4.57,1.55,.82)])
    box('Console keyboard lower shell',(-4.57,1.53,.853),(.67,.20,.066),'teal',h,.008)
    for row in range(3):
        for col in range(11):box('Keyboard square key',(-4.86+col*.054,1.48+row*.048,.892),(.042,.034,.015),'plastic',h,.003)
    gauge(-3.30,1.37,.99,h)
    # Phone, ledger, glove and a ceramic mug are concentrated at a worked station.
    story_props(q)
    chair(-4.1,2.5)
    # Front desk task light on rear ceiling of booth, support registered against cap.
    l=root('Booth task light',target='Booth suspended cap',direction=(0,0,1),anchors=[(-4.1,2.2,2.905)])
    box('Booth lamp fixing',(-4.1,2.2,2.88),(.14,.12,.05),'steel',l,.004)
    box('Booth opal task strip',(-4.1,2.2,2.84),(1.25,.16,.035),'light',l,.008)
    light('Monitoring warm task pool',(-4.1,2.2,2.78),(-4.1,1.5,.8),75,.85,(1,.80,.52),'RECTANGLE',.2)
    # Utility route enters wall and ends at a credible device; no decorative spaghetti.
    u=root('Receiving radiation monitor',target='Booth rear insulated sill',direction=(0,-1,0),anchors=[(-2.95,3.8,.84)])
    box('Monitor bolted backplate',(-2.95,3.816,.84),(.34,.032,.42),'steel',u,.007)
    box('Portable survey dock',(-2.95,3.91,.91),(.24,.16,.37),'orange',u,.019)
    box('Survey meter rubber window',(-2.95,4.001,1.00),(.17,.02,.12),'rubber',u,.007)
    box('Survey meter LCD',(-2.95,4.013,1.00),(.134,.005,.074),'screen',u,.003)
    text('Survey reading','0.04',(-2.95,4.019,1.0),.035,'white',u,(pi/2,0,pi))
    tube('Survey probe flex',[(-2.83,3.93,.84),(-2.7,3.94,.63),(-2.61,3.94,.70),(-2.64,3.94,.97)],.013,'rubber',u)
    cyl('Survey probe',(-2.64,3.93,1.06),.025,.20,'dark',u)
    # Actual utility conduit supported by booth panel, rising to cap.
    rod('Monitor straight supply conduit',(-3.28,3.83,.72),(-3.28,3.83,2.63),.011,'steel',u)
    tube('Monitor conduit lower elbow',[(-3.07,3.825,.68),(-3.22,3.83,.68),(-3.28,3.83,.72)],.011,'steel',u)
    tube('Monitor conduit upper elbow',[(-3.28,3.83,2.63),(-3.28,3.80,2.73),(-3.28,3.65,2.8)],.011,'steel',u)
    for zz in [1.25,2.30]:box('Conduit fixing saddle',(-3.28,3.81,zz),(.065,.024,.018),'dark',u,.003)

def story_props(deskroot):
    global ACTIVE; ACTIVE='06_HUMAN_TRACES'
    q=root('Signed shift ledger',target='Desk laminate worktop',anchors=[(-3.66,1.24,.82)])
    box('Ledger cloth cover',(-3.66,1.24,.835),(.34,.28,.03),'teal',q,.005,rot=(0,0,-.12))
    box('Ledger paper block',(-3.66,1.24,.854),(.315,.26,.015),'paper',q,.002,rot=(0,0,-.12))
    text('Ledger ink heading','SHIFT / 04',(-3.66,1.26,.863),.024,'ink',q,(0,0,-.12))
    for yy in [1.17,1.20,1.23]:box('Ledger rule',(-3.66,yy,.864),(.23,.001,.0008),'ink',q,0,solid=False)
    rod('Resting pencil',(-3.78,1.15,.868),(-3.55,1.12,.868),.006,'orange',q)
    q=root('Operator enamel mug',target='Desk laminate worktop',anchors=[(-5.19,1.18,.82)],irregular=True)
    lathe('Hollow enamel cup',-5.19,1.18,[(.062,.82),(.066,.828),(.069,.95),(.062,.96),(.057,.95),(.054,.834)],'cream',q,48)
    torus('Cup lip',(-5.19,1.18,.954),.065,.004,'dark',q)
    torus('Cup handle',(-5.27,1.18,.891),.042,.009,'cream',q,(pi/2,0,0))
    q=root('Canvas wipe folded on desk',target='Desk laminate worktop',anchors=[(-3.7,1.52,.82)],irregular=True)
    vv=[]; nx=16;ny=10
    for j in range(ny):
        for i in range(nx):
            x=-3.85+i*.018;y=1.44+j*.016;z=.829+.01*sin(i*.7)+.004*cos(j*.9);vv.append((x,y,z))
    ff=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(ny-1) for i in range(nx-1)]
    o=mesh('Folded woven wiping cloth',vv,ff,'fabric',q);md=o.modifiers.new('Cloth edge thickness','SOLIDIFY');md.thickness=.006
    box('Cloth bottom folded layer',(-3.70,1.52,.823),(.29,.16,.006),'fabric',q,.003)
    ACTIVE='02_MONITOR_BOOTH'

def chair(x,y):
    q=root('Operator swivel chair',anchors=[(x+.31,y,0),(x-.251,y+.182,0)],irregular=True)
    for i in range(5):
        a=2*pi*i/5; ex=x+.31*cos(a);ey=y+.31*sin(a)
        rod('Chair star base spoke',(x,y,.19),(ex,ey,.08),.022,'dark',q)
        sphere('Chair rubber caster',(ex,ey,.035),(.041,.034,.035),'rubber',q)
    cyl('Chair gas column',(x,y,.29),.041,.32,'steel',q)
    box('Chair molded seat pan',(x,y,.465),(.47,.43,.055),'plastic',q,.055)
    box('Chair fabric seat cushion',(x,y-.005,.511),(.455,.425,.06),'fabric',q,.065)
    rod('Chair back support',(x,y+.17,.46),(x,y+.26,.84),.028,'dark',q)
    box('Chair contoured back',(x,y+.257,.885),(.43,.06,.36),'fabric',q,.065,rot=(.10,0,0))

def cask_cart(cx,cy):
    global ACTIVE; ACTIVE='03_TRANSFER_CASK'
    q=root('Transfer cart and cask',anchors=[(cx-.53,cy-.58,0),(cx+.53,cy-.58,0),(cx-.53,cy+.58,0),(cx+.53,cy+.58,0)],irregular=True)
    # Steel ladder chassis is a proper load path with bolted axle plates and four broad wheels.
    for xx in [cx-.45,cx+.45]:box('Cart channel rail',(xx,cy,.30),(.13,1.54,.13),'teal',q,.012)
    for yy in [cy-.64,cy,cy+.64]:box('Cart cross bearer',(cx,yy,.30),(1.21,.11,.13),'teal',q,.009)
    box('Cart inset deck',(cx,cy,.389),(1.15,1.35,.045),'steel',q,.01)
    for xx in [cx-.53,cx+.53]:
        for yy in [cy-.58,cy+.58]:
            box('Caster mounting pad',(xx,yy,.266),(.22,.25,.036),'steel',q,.006)
            cyl('Caster swivel bearing',(xx,yy,.235),.083,.03,'dark',q)
            for x2 in [xx-.095,xx+.095]:
                yz=[(-.108,.232),(.108,.232),(.104,.142),(.058,.085),(-.057,.085),(-.102,.139)]
                vv=[(x2+dx,yy+dy,z) for dx in [-.0125,.0125] for dy,z in yz];n=len(yz)
                ff=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
                mesh('Pressed-steel caster fork cheek',vv,ff,'teal',q,.003)
            cyl('Load rated rubber wheel',(xx,yy,.112),.112,.16,'rubber',q,'X',48,.013)
            cyl('Recessed wheel hub',(xx-.086,yy,.112),.053,.012,'steel',q,'X')
            cyl('Axle bolt',(xx-.099,yy,.112),.02,.018,'dark',q,'X',6,.002)
    # Cradle ring uses shaped pads and stops instead of a flat box plinth.
    lathe('Cask cradle seat',cx,cy,[(.50,.413),(.64,.43),(.66,.50),(.61,.545),(.51,.545)],'teal',q)
    for xx in [cx-.49,cx+.49]:
        box('Cradle rubber saddle',(xx,cy,.55),(.12,.71,.07),'rubber',q,.018)
    lathe('Cask lower impact ring',cx,cy,[(.47,.55),(.56,.58),(.59,.63),(.59,.70),(.54,.73)],'dark',q)
    lathe('Shielded cask body',cx,cy,[(.51,.70),(.54,.76),(.545,1.22),(.52,1.33),(.465,1.405)],'cream',q)
    # Circumferential shell belt and selective vertical stiffening create specific silhouette.
    lathe('Cask restraint belt',cx,cy,[(.54,.88),(.56,.90),(.56,.995),(.543,1.01)],'teal',q)
    for i in range(8):
        a=2*pi*i/8;rr=.541;u=Vector((-sin(a),cos(a),0));v=Vector((cos(a),sin(a),0));c=Vector((cx,cy,1.14))
        outline=[(-.025,-.14),(.025,-.14),(.040,-.08),(.036,.11),(.022,.14),(-.022,.14),(-.036,.11),(-.04,-.08)]
        vv=[tuple(c+u*t+v*(rr+depth)+Vector((0,0,z))) for depth in [-.004,.029] for t,z in outline];n=8
        ff=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
        mesh('Cast tapered heat rib',vv,ff,'cream',q,.002)
    lathe('Cask lid bolting flange',cx,cy,[(.466,1.36),(.585,1.39),(.59,1.45),(.46,1.46)],'steel',q)
    lathe('Cask compressible lid seal',cx,cy,[(.459,1.454),(.55,1.459),(.55,1.475),(.459,1.48)],'rubber',q)
    lid=bpy.data.objects.new('Cask_Lid_LIFT_PIVOT',None); COL[ACTIVE].objects.link(lid);lid.parent=q;lid['support_role']='assembly_part';lid['support_root']=q.name;lid['interaction']='unseal_lift';lid['axis']='Z'
    o=lathe('Shielded dished lid',cx,cy,[(.555,1.477),(.555,1.51),(.50,1.56),(.37,1.60),(.12,1.615)],'teal',q);w=o.matrix_world.copy();o.parent=lid;o.matrix_world=w
    for i in range(12):
        a=2*pi*i/12;bolt('Captive lid bolt',(cx+.521*cos(a),cy+.521*sin(a),1.525),q,r=.025)
    # Two oval lifting bails, cast feet and retention pins.
    for xx in [cx-.32,cx+.32]:
        for yy in [cy-.10,cy+.10]:box('Bail welded foot',(xx,yy,1.605),(.12,.10,.035),'teal',q,.009)
        tube('Cask lifting bail',[(xx,cy-.10,1.62),(xx,cy-.10,1.77),(xx,cy,1.81),(xx,cy+.10,1.77),(xx,cy+.10,1.62)],.027,'orange',q)
    cyl('Lid test coupling',(cx,cy,1.638),.047,.048,'steel',q)
    cyl('Test coupling tethered cap',(cx,cy,1.67),.049,.019,'orange',q,vertices=12)
    # Four clamps connect shell to body shoulder; authored purposeful latch silhouette.
    for i in range(4):
        a=pi/4+i*pi/2;xx=cx+.545*cos(a);yy=cy+.545*sin(a)
        box('Cask latch bracket',(xx,yy,1.345),(.11,.045,.18),'teal',q,.004,rot=(0,0,a-pi/2))
        radial=Vector((cos(a),sin(a),0));tan=Vector((-sin(a),cos(a),0));c=Vector((cx,cy,0))
        p1=c+radial*.578+Vector((0,0,1.36));p2=c+radial*.620+Vector((0,0,1.235))
        rod('Toggle forged lever',p1,p2,.014,'orange',q)
        rod('Toggle transverse pivot',p1-tan*.050,p1+tan*.050,.020,'steel',q)
        for side in [-1,1]:
            points=[tuple(c+radial*.567+tan*.036*side+Vector((0,0,1.36))),tuple(c+radial*.61+tan*.036*side+Vector((0,0,1.47))),tuple(c+radial*.545+tan*.036*side+Vector((0,0,1.53)))]
            tube('Toggle flange draw-hook',points,.009,'steel',q)
    # Cart restraint hooks and a low U-shaped push bar clear the cask body.
    tube('Transport cradle push handle',[(cx-.48,cy+.72,.33),(cx-.48,cy+.84,1.01),(cx-.35,cy+.85,1.11),(cx+.35,cy+.85,1.11),(cx+.48,cy+.84,1.01),(cx+.48,cy+.72,.33)],.029,'teal',q)
    rod('Push bar soft grip',(cx-.30,cy+.85,1.11),(cx+.30,cy+.85,1.11),.036,'rubber',q)
    # Retention strap follows diameter across lower body, selective woven insert.
    for xx in [cx-.59,cx+.59]:box('Retention buckle',(xx,cy-.12,.925),(.075,.16,.12),'steel',q,.008)
    # Sparse front marking, one physical tag on tamper seal and abraded bumper edge.
    wall_sign('Cask registry','W–042',(cx,cy-.553,1.12),(.29,.026,.12),.057,q,'teal')
    for xx in [cx-.39,cx+.29]:chip('Cask bumper contact wear',(xx,cy-.44,.704),(1,0,0),(0,1,0),.13,.018,q,'steel')
    box('Cask latch lead seal',(cx+.405,cy-.424,1.36),(.038,.018,.048),'orange',q,.005)
    for yy in [cy-.59,cy+.58]:
        for xx in [cx-.44,cx+.44]:bolt('Cart deck screw',(xx,yy,.421),q,r=.014)
    # Contact wear is concentrated on leading chassis and handled lid, with clean fields around it.
    for dx,w in [(-.42,.16),(-.18,.075),(.31,.13)]:chip('Leading chassis chipped enamel',(cx+dx,cy-.696,.33),(1,0,0),(0,0,1),w,.025,q,'steel')
    for a in [3.8,4.1,5.15]:
        chip('Handled lid rim primer',(cx+.542*cos(a),cy+.542*sin(a),1.518),(-sin(a),cos(a),0),(0,0,1),.047,.013,q,'chip')
    # One wired paper seal records chain of custody; there is no decorative screen on the cask.
    tag=box('Paper custody tag',(cx-.415,cy-.40,1.29),(.075,.006,.12),'paper',q,.002,rot=(0,0,-pi/4))
    tube('Custody tag seal wire',[(cx-.41,cy-.39,1.35),(cx-.44,cy-.43,1.44),(cx-.45,cy-.45,1.46)],.002,'steel',q)
    text('Custody tag number','042',(cx-.415,cy-.405,1.29),.020,'ink',q,(pi/2,0,-pi/4))

def receiving_details():
    global ACTIVE; ACTIVE='01_RECEIVING'
    # Low receiving bollard defines staging without narrowing entry clear opening.
    for x in [-2.11]:
        r=root('Booth corner guard',anchors=[(x,3.92,0)])
        cyl('Guard base',(x,3.92,.045),.135,.09,'dark',r)
        lathe('Guard formed post',x,3.92,[(.067,.09),(.076,.13),(.076,.73),(.06,.78),(.01,.79)],'orange',r,32)
        for z in [.24,.52]:cyl('Guard rubber band',(x,3.92,z),.078,.09,'rubber',r)
    # Concise label and shallow service switch by the booth door.
    r=root('Monitoring access plate',target='Booth east stile 01',direction=(-1,0,0),anchors=[(-2.38,1.62,1.45)])
    box('Card reader bracket',(-2.365,1.62,1.45),(.03,.055,.20),'steel',r,.003)
    box('Access card reader',(-2.327,1.62,1.45),(.05,.095,.16),'plastic',r,.012)
    box('Reader status slot',(-2.296,1.62,1.49),(.007,.052,.013),'screen',r,.002)
    # Small receiving floor staging corners only, no giant chevrons.
    for xx in [-.49,1.09]:
        for yy in [2.04,3.93]:
            floor_rect('Staging corner longitudinal',xx,yy,.032,.28,'orange');floor_rect('Staging corner transverse',xx+(.12 if xx<0 else -.12),yy,.27,.032,'orange')
    for xx in [-.21,.80]:
        floor_rect('Localized wheel scuff',xx,2.19,.047,.52,'scuff')
    ceiling_fixture('Receiving practical',.10,2.55,power=420,length=1.7)
    ceiling_fixture('Booth exterior practical',-3.3,3.99,power=185,length=1.25)
    light('Entry soft bounced fill',(1.3,-.6,2.3),(0,2,1),65,3,(.68,.78,1))

CAMERAS=[
 ('C01_ENTRY',(0,.28,1.65),(0,8,1.45),24),
 ('C02_HERO',(3.85,4.30,1.65),(-1.42,2.19,1.23),27),
 ('C03_REVERSE',(.30,16.8,1.65),(0,2,1.5),25),
 ('C04_ROUTE',(0,5.1,1.65),(0,15.8,1.5),28),
 ('C05_CELL_ACCESS',(.3,8.8,1.65),(-4.0,7.0,1.25),30),
 ('C06_CASK',(.3,6.0,1.65),(-4,6.75,1.23),40),
 ('C07_MONITORING',(-2.91,3.2,1.65),(-4.32,1.25,1.07),28),
 ('C08_VENTILATION',(3,14.6,1.65),(-3.1,16.6,1.55),29),
 ('C09_RECEIVING',(4.7,.79,1.65),(-2.3,2.45,1.35),26),
 ('C10_MATERIALS',(1.58,1.28,1.32),(.20,3.10,1.19),49)
]
def setup():
    for n,co,target,lens in CAMERAS:
        d=bpy.data.cameras.new(n);d.lens=lens;d.sensor_width=36;d.clip_start=.06;d.clip_end=100
        o=bpy.data.objects.new(n,d);COL['08_CAMERAS'].objects.link(o);o.location=co;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    S.camera=bpy.data.objects['C02_HERO']; S.render.engine='CYCLES';S.cycles.samples=64; S.cycles.use_denoising=True;S.cycles.max_bounces=8
    S.cycles.seed=4217;S.cycles.use_animated_seed=False;S.cycles.diffuse_bounces=4;S.cycles.glossy_bounces=4;S.cycles.transmission_bounces=6;S.cycles.transparent_max_bounces=8
    S.render.resolution_x=1280;S.render.resolution_y=800;S.render.resolution_percentage=100
    S.render.image_settings.file_format='PNG';S.render.film_transparent=False
    S.world=bpy.data.worlds.new('Muted industrial ambient');S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.27,.34,.37,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.065
    S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=.1
    S['camera_manifest']=json.dumps([{'name':n,'position':co,'target':ta,'lens':le,'stage':'slice/full' if n in ['C02_HERO','C07_MONITORING','C09_RECEIVING','C10_MATERIALS'] else 'full'} for n,co,ta,le in CAMERAS])
    S['route_clearances']=json.dumps([{'name':'Entry threshold','min':[-1.5,0,0.015],'max':[1.5,.8,3.2]},{'name':'Main transfer route','min':[-1.8,4.5,.015],'max':[1.8,14.5,2.4]},{'name':'Personnel exit','min':[5.65,1.8,.015],'max':[6.3,3.0,2.3]}])

architecture();booth();cask_cart(.30,3.0);receiving_details()
if A.stage=='full':
    raise RuntimeError('Full expansion gated on independent slice pixel acceptance. Request author expansion after slice pass.')
setup()
# Report all support relations as a portable source-side manifest.
os.makedirs(os.path.dirname(os.path.abspath(A.output)),exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(A.output),compress=True)
manifest={'stage':A.stage,'revision':A.revision,'build_source_sha256':S['build_source_sha256'],'camera_manifest':json.loads(S['camera_manifest']),'assemblies':[{'name':o.name,'target':o.get('support_target'),'direction':json.loads(o['support_direction']),'anchors':json.loads(o['support_anchors'])} for o in bpy.data.objects if o.get('support_required')]}
with open(os.path.join(os.path.dirname(__file__),'scene_manifest.json'),'w',encoding='utf-8') as f:json.dump(manifest,f,indent=2)
print('WASTE_BUILD_SAVED '+json.dumps({'stage':A.stage,'revision':A.revision,'output':A.output,'objects':len(bpy.data.objects),'cameras':len(CAMERAS),'assemblies':len(manifest['assemblies'])}))
