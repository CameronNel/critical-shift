"""Original Fuel Corridor. Blender 5.2, factory-empty, metres. No imported geometry.

Build: blender -b --factory-startup --python build.py -- --stage slice --revision slice01
Render only through the shared GPU gate. See run.ps1.
"""
import argparse, bpy, math, json, sys, random, hashlib, os
from pathlib import Path
from mathutils import Vector
ROOT=Path(os.environ.get('FUEL_CORRIDOR_ROOT',str(Path(__file__).resolve().parents[1])))
INTERFACE_PATH=Path(__file__).resolve().with_name('interface.json')
if not INTERFACE_PATH.exists():INTERFACE_PATH=ROOT/'interface.json'
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
        tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=19;tex.inputs['Detail'].default_value=3;tex.inputs['Roughness'].default_value=.72
        coord=n.new('ShaderNodeTexCoord');l.new(coord.outputs['Object'],tex.inputs['Vector'])
        ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='LINEAR'
        ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
        for i,(pos,v) in enumerate([(.30,-1),(.40,-.5),(.475,0),(.55,.5),(.65,1)]):
            e=ramp.color_ramp.elements[0] if i==0 else ramp.color_ramp.elements.new(pos);e.position=pos;e.color=(*[min(1,max(0,c*(1+variation*v*.40))) for c in color],1)
        l.new(tex.outputs['Fac'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],p.inputs['Base Color'])
        rr=n.new('ShaderNodeMapRange');rr.inputs['From Min'].default_value=.32;rr.inputs['From Max'].default_value=.68;rr.inputs['To Min'].default_value=max(.1,rough-.05);rr.inputs['To Max'].default_value=min(1,rough+.04);l.new(tex.outputs['Fac'],rr.inputs[0]);l.new(rr.outputs[0],p.inputs['Roughness'])
        if bump:
            grain=n.new('ShaderNodeTexNoise');grain.inputs['Scale'].default_value=54;grain.inputs['Detail'].default_value=2;l.new(coord.outputs['Object'],grain.inputs['Vector']);bn=n.new('ShaderNodeBump');bn.inputs['Strength'].default_value=.17;bn.inputs['Distance'].default_value=bump;l.new(grain.outputs['Fac'],bn.inputs['Height']);l.new(bn.outputs['Normal'],p.inputs['Normal'])
    M[name]=m;return m
mat('mineral',(.32,.345,.375),.85,variation=.10,bump=.0015)
mat('floor',(.18,.20,.23),.76,variation=.10,bump=.002)
mat('repair',(.16,.18,.21),.86,variation=.04,bump=.001)
# Historical material keys retained for source replay; colors now follow reactor A05.
mat('teal',(.060,.069,.087),.49,.28,.07,.0007)
mat('teal_light',(.08,.105,.14),.60,.18,.055,.0008)
mat('steel',(.21,.255,.31),.32,.87,.055,.0005)
M['steel'].node_tree.nodes.get('Principled BSDF').inputs['Anisotropic'].default_value=.58
mat('darksteel',(.064,.079,.103),.43,.54,.075,.0008)
mat('structural_coat',(.12,.15,.19),.62,.08,.045,.0004)
mat('rubber',(.025,.03,.029),.93,.0,.04,.008)
mat('ochre',(.70,.125,.009),.62,.08,.055,.0005)
mat('ivory',(.46,.49,.53),.70,.06,.09,.0009)
mat('ink',(.075,.083,.075),.86,variation=0,bump=0)
mat('paper',(.67,.63,.48),.94,variation=.04,bump=.003)
mat('cloth',(.30,.32,.34),.98,variation=.035,bump=.0007)
mat('glove',(.022,.03,.043),.97,variation=.06,bump=.0009)
mat('cotton',(.025,.049,.075),.98,variation=.055,bump=.0005)
mat('glove_leather',(.034,.033,.029),.88,variation=.065,bump=.00025)
M['cotton'].node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value=.09
M['glove'].node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value=.05
mat('red',(.42,.075,.035),.56,.15,.05,.003)
mat('glass',(.24,.33,.31),.22,.18,0,0)
gp=M['glass'].node_tree.nodes.get('Principled BSDF');gp.inputs['Base Color'].default_value=(.96,.985,1,1);gp.inputs['Metallic'].default_value=0;gp.inputs['Transmission Weight'].default_value=1;gp.inputs['IOR'].default_value=1.46;gp.inputs['Roughness'].default_value=.075
mat('lamp',(1,.55,.18),.45,0,0,0,4)
mat('cool_lamp',(.70,.86,1),.4,0,0,0,3)
mat('chip',(.21,.22,.195),.8,.2,0,0)
mat('primer',(.37,.265,.14),.9,.05,.05,.004)
mat('old_teal',(.12,.145,.175),.67,.12,.035,.0007)
mat('wall_patch',(.30,.325,.355),.86,variation=.025,bump=.0003)
mat('wall_light',(.345,.37,.40),.83,variation=.025,bump=.0003)
mat('brass',(.43,.27,.09),.35,.72,.025,.0004)
mat('floor_stroke',(.192,.211,.240),.82,variation=.04,bump=.001)
mat('floor_scuff',(.135,.15,.175),.87,variation=.03,bump=.001)
mat('wall_protection',(.085,.105,.135),.76,.08,.035,.0006)
FLOOR_ALBEDO=ROOT/'art/materials/T01-floor-albedo-r01.png'
floor_image=bpy.data.images.load(str(FLOOR_ALBEDO),check_existing=True);floor_image.pack();floor_image.filepath='//../art/materials/T01-floor-albedo-r01.png'
fm=M['floor'];nn=fm.node_tree.nodes;ll=fm.node_tree.links;pb=nn.get('Principled BSDF')
co=nn.new('ShaderNodeNewGeometry');sc=nn.new('ShaderNodeVectorMath');sc.operation='SCALE';sc.inputs[3].default_value=.25;ll.new(co.outputs['Position'],sc.inputs[0])
it=nn.new('ShaderNodeTexImage');it.image=floor_image;it.extension='REPEAT';ll.new(sc.outputs[0],it.inputs['Vector']);ll.new(it.outputs['Color'],pb.inputs['Base Color'])
ft=nn.new('ShaderNodeMixRGB');ft.blend_type='MULTIPLY';ft.inputs[0].default_value=1;ft.inputs[2].default_value=(.43,.52,.67,1);ll.new(it.outputs['Color'],ft.inputs[1]);ll.new(ft.outputs[0],pb.inputs['Base Color'])
rough=nn.new('ShaderNodeMapRange');rough.inputs['From Min'].default_value=.10;rough.inputs['From Max'].default_value=.36;rough.inputs['To Min'].default_value=.43 if A.stage=='full' else .48;rough.inputs['To Max'].default_value=.58 if A.stage=='full' else .66;ll.new(it.outputs['Color'],rough.inputs[0]);ll.new(rough.outputs[0],pb.inputs['Roughness'])
WALL_ALBEDO=ROOT/'art/materials/T02-wall-albedo-r01.png'
wall_image=bpy.data.images.load(str(WALL_ALBEDO),check_existing=True);wall_image.pack();wall_image.filepath='//../art/materials/T02-wall-albedo-r01.png'
wm=M['mineral'];wn=wm.node_tree.nodes;wl=wm.node_tree.links;wp=wn.get('Principled BSDF')
wc=wn.new('ShaderNodeTexCoord')
wi=wn.new('ShaderNodeTexImage');wi.image=wall_image;wi.projection='FLAT';wl.new(wc.outputs['UV'],wi.inputs['Vector'])
wt=wn.new('ShaderNodeMixRGB');wt.blend_type='MULTIPLY';wt.inputs[0].default_value=1;wt.inputs[2].default_value=(.78,.84,.94,1);wl.new(wi.outputs['Color'],wt.inputs[1]);wl.new(wt.outputs[0],wp.inputs['Base Color'])
M['cartridge_paint']=M['ivory'].copy();M['cartridge_paint'].name='Closed_cartridge_enamel'
cn=M['cartridge_paint'].node_tree.nodes;cl=M['cartridge_paint'].node_tree.links;cp=cn.get('Principled BSDF')
ct=cn.new('ShaderNodeTexImage');ct.image=wall_image;cu=cn.new('ShaderNodeTexCoord');cl.new(cu.outputs['UV'],ct.inputs['Vector'])
cm=cn.new('ShaderNodeMixRGB');cm.blend_type='MIX';cm.inputs[0].default_value=.40;cm.inputs[1].default_value=(.46,.49,.53,1);cl.new(ct.outputs['Color'],cm.inputs[2]);cl.new(cm.outputs[0],cp.inputs['Base Color'])
CLOTH_ALBEDO=ROOT/'art/materials/T03-cloth-albedo-r01.png'
cloth_image=bpy.data.images.load(str(CLOTH_ALBEDO),check_existing=True);cloth_image.pack();cloth_image.filepath='//../art/materials/T03-cloth-albedo-r01.png'
for name in ['cotton','glove']:
    mm=M[name];nodes=mm.node_tree.nodes;links=mm.node_tree.links;pp=nodes.get('Principled BSDF')
    tx=nodes.new('ShaderNodeTexImage');tx.image=cloth_image;coord=nodes.new('ShaderNodeTexCoord');links.new(coord.outputs['UV'],tx.inputs['Vector']);links.new(tx.outputs['Color'],pp.inputs['Base Color'])
    bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.00035;links.new(tx.outputs['Color'],bump.inputs['Height']);links.new(bump.outputs['Normal'],pp.inputs['Normal'])
    pp.inputs['Specular IOR Level'].default_value=.18;pp.inputs['Diffuse Roughness'].default_value=.35
def finish(o,name,material):
    o.name=name;add(o)
    if material:o.data.materials.append(M[material])
    return o
def box(name,loc,dim,material='teal',bevel=.005):
    xx,yy,zz=[v*.5 for v in dim]
    vv=[(x,y,z) for x in [-xx,xx] for y in [-yy,yy] for z in [-zz,zz]]
    o=mesh(name,vv,[(0,2,6,4),(1,5,7,3),(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6)],material);o.location=loc
    if bevel:
        b=o.modifiers.new('Manufactured edge','BEVEL');b.width=min(bevel,min(abs(v) for v in dim)*.24);b.segments=2
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
    a,b=Vector(a),Vector(b);d=b-a
    vv=[(r*math.cos(i*math.tau/verts),r*math.sin(i*math.tau/verts),z) for z in [-d.length/2,d.length/2] for i in range(verts)]
    ff=[tuple(reversed(range(verts))),tuple(range(verts,2*verts))]+[(i,(i+1)%verts,(i+1)%verts+verts,i+verts) for i in range(verts)]
    o=mesh(name,vv,ff,material);o.location=(a+b)/2;o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    be=o.modifiers.new('Machined rim','BEVEL');be.width=min(.004,r*.1,d.length*.2);be.segments=2
    for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
    return o
def tube(name,points,r,material):
    d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=2;d.bevel_depth=r;d.bevel_resolution=3;s=d.splines.new('POLY');s.points.add(len(points)-1)
    for p,co in zip(s.points,points):p.co=(*co,1)
    o=bpy.data.objects.new(name,d);COL.objects.link(o);d.materials.append(M[material]);o.parent=PAR;return o
def torus(name,loc,major,minor,material='steel',rot=(0,0,0)):
    nn,mm=48,10
    vv=[((major+minor*math.cos(j*math.tau/mm))*math.cos(i*math.tau/nn),(major+minor*math.cos(j*math.tau/mm))*math.sin(i*math.tau/nn),minor*math.sin(j*math.tau/mm)) for i in range(nn) for j in range(mm)]
    ff=[(i*mm+j,((i+1)%nn)*mm+j,((i+1)%nn)*mm+(j+1)%mm,i*mm+(j+1)%mm) for i in range(nn) for j in range(mm)]
    o=mesh(name,vv,ff,material);o.location=loc;o.rotation_euler=rot
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
        o=box(name+suffix,mid+out*off+Vector((0,0,z)),(L,th,height),matl,0 if height<.02 or th<.012 else .003);o.rotation_euler.z=math.atan2(d.y,d.x);return o
    slab('_concrete',.19,h/2,.30,h,'mineral')
    shield=(abs(a.y-13.2)<.0001 and abs(b.y-13.2)<.0001 and min(a.x,b.x)>=1.199 and max(a.x,b.x)<=4.401)
    slab('_washable_lower',-.014,.64,.028,1.28,'wall_protection' if shield else 'mineral')
    slab('_skirt',-.031,.10,.062,.20,'darksteel')
    slab('_capping',-.027,1.29,.045,.035,'steel')
    # Full-height panel construction with steel uprights and a restrained route band.
    if L>.35:
        slab('_upper_rail',-.045,h-.24,.09,.18,'structural_coat')
        slab('_utility_band',-.006,h-.46,.012,.045,'ochre')
    divisions=max(1,math.ceil(L/2.25))
    for pi in range(divisions):
        pa=L*pi/divisions+.115;pb=L*(pi+1)/divisions-.115
        if pb-pa<.12:continue
        for za,zb in [(1.325,h*.61-.008),(h*.61+.008,h-.35)]:
            if zb<=za:continue
            loc=a+d*((pa+pb)/2)+out*.02+Vector((0,0,(za+zb)/2))
            ob=box(name+'_formed_infill_panel',loc,(pb-pa,.04,zb-za),'mineral',.0015);ob.rotation_euler.z=math.atan2(d.y,d.x)
            for t in [pa+.055,pb-.055]:
                for zz in [za+.055,zb-.055]:
                    q=a+d*t-out*.004+Vector((0,0,zz));rod(name+'_panel_fastener',q+out*.007,q-out*.002,.009,'steel',6)
    for i in range(1 if A.stage=='full' and L<.27 else divisions+1):
        end_margin=min(.13,L/2) if A.stage=='full' else .045
        along=max(end_margin,min(L-end_margin,L*i/divisions));p=a+d*along
        o=box(name+'_vertical_web',p-out*.080+Vector((0,0,h/2)),(.07,.16,h),'structural_coat',.003);o.rotation_euler.z=math.atan2(d.y,d.x)
        for off in [.014,.146]:
            o=box(name+'_vertical_flange',p-out*off+Vector((0,0,h/2)),(.21,.028,h),'teal_light' if off>.1 else 'teal',.004);o.rotation_euler.z=math.atan2(d.y,d.x)
        if L>.45:
            for zz in [.20,1.42,h-.30]:
                for t in [-.071,.071]:
                    q=p+d*t-out*.167+Vector((0,0,zz));rod(name+'_frame_anchor',q+out*.012,q-out*.007,.011,'steel',6)
            for sign in [-1,1]:
                if along+sign*.34<.03 or along+sign*.34>L-.03:continue
                profile=[(along,h-.22),(along+sign*.34,h-.22),(along,h-.58)]
                vv=[tuple(a+d*t-out*off+Vector((0,0,z))) for off in [.149,.179] for t,z in profile]
                mesh(name+'_knee_gusset',vv,[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],'teal_light')
                for t,z in [(along+sign*.065,h-.28),(along+sign*.19,h-.28),(along+sign*.060,h-.44)]:
                    q=a+d*t-out*.184+Vector((0,0,z));rod(name+'_gusset_bolt',q+out*.006,q-out*.005,.013,'steel',6)
            # Manufactured splices and bearing shoes give the frame a construction scale.
            for z,hh in [(.18,.30),(h-.72,.20)]:
                o=box(name+'_splice_plate',p-out*.166+Vector((0,0,z)),(.225,.016,hh),'teal_light',.002);o.rotation_euler.z=math.atan2(d.y,d.x)
                for side2 in [-1,1]:
                    for vz in [-.065,.065]:
                        q=p+d*side2*.071-out*.178+Vector((0,0,z+vz));rod(name+'_splice_bolt',q+out*.006,q-out*.008,.010,'steel',6)
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
        # Sparse edge abrasion follows upright edges at cart/hand contact height.
        for i in range(divisions+1):
            t=max(.045,min(L-.045,L*i/divisions))
            for s in [-1,1]:
                for zz,length in [(.48,.04),(.73,.075),(1.17,.06),(1.86,.025)]:
                    tt=t+s*.098
                    if tt<.008 or tt>L-.008:continue
                    points=[(tt,zz),(tt-s*.006,zz+.015),(tt-s*.004,zz+length),(tt,zz+length+.008)]
                    ob=mesh(name+'_edge_handling_wear',[tuple(a+d*u-out*.161+Vector((0,0,z))) for u,z in points],[(0,1,2,3)],'steel');ob['surface_decal']=True
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
    parent['port_id']={'REFINERY_BOUNDARY':'F01_REFINERY','REACTOR_BOUNDARY':'F02_REACTOR','PLANT_PORT':'S01_PLANT','CLEAN_PORT':'S02_CLEAN','WASTE_PORT':'S03_WASTE'}.get(name,'INTERNAL_FREIGHT_GATE')
    parent['geometry_owner']='fuel-corridor'
    parent['presentation_cap']=name in ['REFINERY_BOUNDARY','REACTOR_BOUNDARY']
    external=A.stage=='full' and name!='FREIGHT_GATE'
    manual=name in ['PLANT_PORT','CLEAN_PORT']
    if external:
        cx+=math.sin(heading)*.50;cy-=math.cos(heading)*.50
        parent['interface_threshold']=list(center)+[0];parent['inboard_frame_offset_m']=.50
    def pos(x,y,z):return(cx+x*math.cos(heading)-y*math.sin(heading),cy+x*math.sin(heading)+y*math.cos(heading),z)
    def bx(n,p,d,ma,bev=.004):o=box(name+n,pos(*p),d,ma,bev);o.rotation_euler.z=heading;return o
    for s in [-1,1]:
        if A.stage=='full':
            bx('_channel_jamb',(s*(w/2+.09),-.09,h/2),(.18,.08,h),'darksteel')
            bx('_rear_jamb',(s*(w/2+.09),.22,h/2),(.18,.08,h),'darksteel')
        else:bx('_channel_jamb',(s*(w/2+.09),0,h/2),(.18,.26,h),'darksteel')
        bx('_track_wear',(s*(w/2+.013),-.06,h/2),(.025,.11,h),'steel')
        bx('_compression_seal',(s*(w/2+.024),-.13,h/2),(.036,.025,h),'rubber')
        bx('_impact_boot',(s*(w/2+.115),-.12 if A.stage=='full' else -.035,.45),(.19,.17 if A.stage=='full' else .33,.90),'ochre',.015)
        if external:
            foundation=bx('_frame_foundation',(s*(w/2+.09),0,-.12),(.24,.66,.24),'floor',0)
            foundation.parent=None;COL.objects.unlink(foundation);bpy.data.collections['01_Architecture'].objects.link(foundation);foundation['support_surface']=True
        for z in [.17,.77,1.6,h-.15]:bolt(name+'_anchor',pos(s*(w/2+.11),-.205 if z<.9 else -.135,z),axis=(math.sin(heading),-math.cos(heading),0))
    if A.stage=='full':
        # Built-up sliding track with a real open carriage slot and supported rollers.
        for yy,dd in [(-.075,.27),(.245,.13)]:bx('_lintel_cheek',(0,yy,h+.13),(w+.72,dd,.26),'darksteel')
        bx('_lintel_roof',(0,.05,h+.235),(w+.72,.52,.05),'darksteel')
        for yy in [.075,.165]:bx('_running_rail',(0,yy,h+.06),(w+.72,.03,.04),'steel',.001)
    else:bx('_lintel',(0,0,h+.13),(w+.40,.32,.26),'darksteel')
    if not manual:bx('_upper_motor_cover',(0,.05,h+.41),(w+.46,.47,.28),'teal')
    for xx in [-w*.38,w*.38]:bx('_drive_bearing_shim',(xx,0,h+.264),(.18,.26,.018),'steel')
    if not manual:
        bx('_drive_access',(w*.28,-.191,h+.41),(.63,.026,.22),'old_teal')
        for u in [-.26,.26]:
            for z in [h+.34,h+.48]:bolt(name+'_drive_cover_bolt',pos(w*.28+u,-.21,z),(math.sin(heading),-math.cos(heading),0),.012)
    for s in [-1,1]:
        x=s*(w/4 if closed else w/2+w/4+.15)
        old_names=set(o.name for o in COL.objects)
        leaf=bx('_sliding_leaf',(x,.12,h/2),(w/2-.025,.10,h-.06),'teal_light',.006);leaf['animation_axis']='carriage vector';leaf['travel_m']=w/2+.15;leaf['closed_state']=closed
        # Recessed rigidifying channels, a kick panel and seam tell sheet-metal construction.
        for zz in [.23,h*.45,h-.29]:bx('_leaf_stiffener',(x,.057,zz),(w/2-.19,.025,.055),'teal')
        for edge in [-1,1]:bx('_folded_return',(x+edge*(w/4-.068),.055,h/2),(.045,.036,h-.16),'teal')
        bx('_kick_plate',(x,.049,.40),(w/2-.22,.016,.42),'steel')
        # Pressed corner gussets, seams and localized pallet impact wear.
        for e in [-1,1]:
            bx('_leaf_panel_seam',(x+e*(w/4-.18),.066 if A.stage=='full' else .049,h*.69),(.008,.008,h*.45),'darksteel',0)
            for zz in [.18,h-.18]:
                bx('_leaf_gusset',(x+e*(w/4-.16),.03,zz),(.18,.04,.17),'teal',.002)
                bolt(name+'_gusset_rivet',pos(x+e*(w/4-.16),.005,zz),(math.sin(heading),-math.cos(heading),0),.012)
        # A worn edge on the brushed impact plate follows actual pallet-height contact.
        for i in range(7):
            xx=x+random.uniform(-w/4+.16,w/4-.16)
            bx('_localized_kick_scuff',(xx,.039,random.uniform(.24,.48)),(random.uniform(.035,.11),.002,.006),'darksteel',0)
        if external:
            # C09: manufactured identity inserts, human-height pulls and discrete access covers.
            field_w=w/2-.18;field_z=1.75 if h>4 else .91;field_h=.85 if h>4 else .50
            bx('_leaf_identity_field',(x,.058,field_z),(field_w,.024,field_h),'mineral',.009)
            words={'REFINERY_BOUNDARY':('FUEL','REFINERY'),'REACTOR_BOUNDARY':('FUEL','REACTOR'),'PLANT_PORT':('PLANT','SERVICES'),'CLEAN_PORT':('CLEAN','MEDICAL'),'WASTE_PORT':('WASTE','TRANSFER')}[name]
            word=words[0 if s<0 else 1];font=min(.33,field_w/(len(word)*.69))
            text_obj(name+'_leaf_identity_text',word,pos(x,.0455,field_z+.01),font,'teal',(math.pi/2,0,heading))
            sub='TRANSFER' if name in ['REFINERY_BOUNDARY','REACTOR_BOUNDARY'] else 'AUTHORIZED ACCESS'
            text_obj(name+'_leaf_identity_text',sub,pos(x,.0455,field_z-.16),min(.095,field_w/13), 'teal',(math.pi/2,0,heading))
            for edge in [-1,1]:
                for zz in [field_z-field_h/2+.048,field_z+field_h/2-.048]:bolt(name+'_leaf_identity_fastener',pos(x+edge*(field_w/2-.044),.042,zz),(math.sin(heading),-math.cos(heading),0),.009)
                bx('_leaf_orange_strip',(x+edge*(w/4-.11),.067,h*.56),(.030,.006,h*.68),'ochre',0)
            access_z=3.28 if h>4 else 1.89;access_w=min(.72,field_w*.65);access_h=.62 if h>4 else .49
            bx('_leaf_access_panel',(x,.055,access_z),(access_w,.030,access_h),'teal',.006)
            for edge in [-1,1]:
                for zz in [access_z-access_h/2+.05,access_z+access_h/2-.05]:bolt(name+'_leaf_access_fastener',pos(x+edge*(access_w/2-.05),.032,zz),(math.sin(heading),-math.cos(heading),0),.012)
            text_obj(name+'_leaf_access_type','R-01' if name=='REACTOR_BOUNDARY' else 'FC / 04',pos(x,.039,access_z+.05),.079,'ivory',(math.pi/2,0,heading))
            text_obj(name+'_leaf_access_type','STAND CLEAR',pos(x,.039,access_z-.085),.037,'paper',(math.pi/2,0,heading))
            pull_x=x-s*(w/4-.16)
            bx('_leaf_pull_back',(pull_x,.061,1.16),(.076,.018,.225),'teal',.008)
            bx('_leaf_pull_shadow',(pull_x,.050,1.16),(.039,.004,.159),'rubber',.005)
            for edge in [-1,1]:bx('_leaf_pull_rail',(pull_x+edge*.029,.044,1.16),(.013,.030,.177),'steel',.004)
            for zz in [1.071,1.249]:bx('_leaf_pull_end',(pull_x,.044,zz),(.070,.030,.014),'steel',.004)
            bx('_leaf_serial_plate',(x-s*field_w*.25,.037,.48),(.21,.008,.105),'paper',.002)
            text_obj(name+'_leaf_serial_type','FC-04 / '+('L' if s<0 else 'R')+'\nINSPECT 07-B',pos(x-s*field_w*.25,.032,.47),.023,'ink',(math.pi/2,0,heading))
        if name in ['REFINERY_BOUNDARY','REACTOR_BOUNDARY']:
            for member in COL.objects:
                if member.name not in old_names:member['external_presentation_cap']=True
        hx=x-s*(w/4-(.14 if A.stage=='full' else .05))
        bx('_leaf_carriage_hanger',(hx,.12,h if A.stage=='full' else h-.01),(.085,.04 if A.stage=='full' else .08,.32 if A.stage=='full' else .22),'steel')
        if A.stage=='full':
            for yy in [.075,.165]:rod(name+'_leaf_carriage_roller',pos(hx,yy-.007,h+.14),pos(hx,yy+.007,h+.14),.06,'steel',32)
            rod(name+'_leaf_carriage_axle',pos(hx,.062,h+.14),pos(hx,.178,h+.14),.016,'steel',16)
        members=[o for o in COL.objects if o.name not in old_names]
        if name in ['REFINERY_BOUNDARY','REACTOR_BOUNDARY']:
            for member in members:member['external_presentation_cap']=True
        pivot=bpy.data.objects.new(name+('_LEFT_CARRIAGE' if s<0 else '_RIGHT_CARRIAGE'),None);COL.objects.link(pivot);pivot.parent=parent;pivot.location=pos(x,0,0);pivot.rotation_euler.z=heading
        pivot['component_role']='sliding_leaf_carriage';pivot['current_pose']='CLOSED' if closed else 'OPEN';pivot['closed_to_open_translation_m']=[s*(w/2+.15)*math.cos(heading),s*(w/2+.15)*math.sin(heading),0];pivot['controller_status']='Editable rigid assembly; engine trigger/controller and moving collision sweep unverified'
        pivot['translation_coordinate_space']='section metres; parent root has identity transform'
        bpy.context.view_layer.update()
        for member in members:member.parent=pivot;member.matrix_parent_inverse=pivot.matrix_world.inverted()
    bx('_flush_sill',(0,0,-.018),(w,.40,.036),'steel',0)
    bx('_direction_panel',(0,-.23 if A.stage=='full' else -.178,h+.13 if A.stage=='full' else h+.16),(min(w,2.4),.040,.20 if A.stage=='full' else .30),'teal')
    label={'FREIGHT_GATE':'FUEL TRANSFER  /  04','PLANT_PORT':'PLANT SERVICES','CLEAN_PORT':'MEDICAL  /  DOCK','WASTE_PORT':'WASTE TRANSFER','REACTOR_BOUNDARY':'REACTOR APPROACH','REFINERY_BOUNDARY':'REFINERY'}.get(name,name)
    text_obj(name+'_type',label,pos(0,-.251 if A.stage=='full' else -.199,h+.065 if A.stage=='full' else h+.07),.115,'ivory',(math.pi/2,0,heading))
    PAR=parent
    if name=='FREIGHT_GATE' or external:
        parent['assembly_role']='floor';parent['support_anchors']=json.dumps([pos(s*(w/2+.09),-.12 if A.stage=='full' else 0,0) for s in [-1,1]]);parent['support_direction']=[0,0,-1]

def practical(name,x,y,z=4.4,power=320,cool=False,rotate=0):
    root(name,'ceiling',[(x-.5*math.cos(rotate),y-.5*math.sin(rotate),z),(x+.5*math.cos(rotate),y+.5*math.sin(rotate),z)],(0,0,1))
    for s in [-1,1]:
        xx=x+s*.5*math.cos(rotate);yy=y+s*.5*math.sin(rotate);rod(name+'_drop',(xx,yy,z),(xx,yy,z-.22),.014,'darksteel')
    o=box(name+'_folded_pan',(x,y,z-.27),(1.52,.28,.10),'darksteel');o.rotation_euler.z=rotate
    o=box(name+'_opal_diffuser',(x,y,z-.326),(1.40,.19,.015),'cool_lamp' if cool else 'lamp',.007);o.rotation_euler.z=rotate
    o=box(name+'_upper_opal_window',(x,y,z-.216),(1.10,.16,.008),'cool_lamp' if cool else 'lamp',.001);o.rotation_euler.z=rotate
    for s in [-1,1]:
        xx=x+s*.73*math.cos(rotate);yy=y+s*.73*math.sin(rotate);o=box(name+'_end_clip',(xx,yy,z-.30),(.045,.3,.08),'steel');o.rotation_euler.z=rotate
    area(name+'_light',(x,y,z-.35),(x,y,0),power*.68,(.78,.88,1) if cool else (1,.84,.68),1.35,.22)
    area(name+'_ceiling_bounce',(x,y,z-.210),(x,y,z+.1),power*.035,(.78,.88,1) if cool else (1,.86,.72),1.10,.16)

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
 ('C03_HERO',(-1.45,6.0,1.70),(1.10,11.5,1.8),22,'whole staging junction / workbench and freight gate; corrected cropped baseline'),
 ('C04_REVERSE',(1.0,10.5,1.70),(-.15,1.0,1.60),26,'reverse approach'),
 ('C05_EAST_TURN',(11.15,8.45,1.70),(14.2,17.0,1.65),25,'freight ninety-degree turn'),
 ('C06_REACTOR_THRESHOLD',(13.5,19.4,1.70),(14.3,24.0,2.10),26,'outlet / transition'),
 ('C07_BYPASS',(.45,14.0,1.70),(-.2,19.7,1.65),25,'narrow service passage'),
 ('C08_SERVICE_JUNCTION',(1.7,19.85,1.70),(7.6,20.0,1.6),25,'clean services connection'),
 ('C09_MATERIALS',(3.7,9.9,1.60),(2.65,12.32,.85),42,'trolley material and support detail; rebaseline after bypass clearance correction'),
 ('C10_PLANT_HEADER',(-.7,17.2,1.70),(-5.4,17.4,1.45),25,'plant branch dead-end / concealed problem areas')]
EXTRA_CAMERAS=[
 ('D01_CARRIER_OPERATION',(1.17,10.2,1.24),(2.38,12.32,.63),42,'supplement: brake and restraint operation'),
 ('D02_WORKBENCH',(-.20,8.75,1.65),(-1.80,10.58,1.26),40,'supplement: worker equipment and purposeful dressing'),
 ('D03_UTILITY',(3.80,11.0,1.72),(3.80,13.15,1.72),46,'supplement: isolator, regulator, gauge, hose and support'),
 ('D04_REACTOR_WIDE',(13.5,17.1,1.7),(14.2,23.5,2.45),19,'supplement: complete five-metre reactor threshold and head'),
 ('D05_GATE_MECHANISM',(4.65,9.5,2.75),(6.35,10,3.5),24,'supplement: freight track, motor, leaf support and services'),
 ('D06_SERVICE_RECESS',(.70,15.2,1.72),(-1.49,15.08,1.72),32,'supplement: recessed air station feed and wall construction')]

def shell(stage):
    collection('01_Architecture')
    cells=json.loads(INTERFACE_PATH.read_text())['floor_cells']
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
        roof_y0=max(0,y0-.01);roof_y1=min(24,y1+.01)
        ceil=box('Ceiling_'+c['id'],((x0+x1)/2,(roof_y0+roof_y1)/2,h+.118),(x1-x0+.02,roof_y1-roof_y0,.2),'darksteel',0);ceil['support_surface']=True
        # Quiet modular floor joints and ceiling coffers provide scale over long runs.
        for axis,lo,hi,other0,other1 in [('X',x0,x1,y0,y1),('Y',y0,y1,x0,x1)]:
            count=max(1,math.ceil((hi-lo)/1.65))
            for ii in range(1,count):
                q=lo+(hi-lo)*ii/count
                box('Slab_joint', (q,(other0+other1)/2,.0006) if axis=='X' else ((other0+other1)/2,q,.0006),(.010,other1-other0,.0012) if axis=='X' else (other1-other0,.010,.0012),'darksteel',0)
        if x1-x0>y1-y0:
            for xx in [x0+.16+i*2.0 for i in range(max(1,math.ceil((x1-x0-.32)/2.0)))]:box('Ceiling_crossmember',(xx,(y0+y1)/2,h-.11),(.12,y1-y0,.22),'structural_coat')
        else:
            for yy in [y0+.16+i*2.0 for i in range(max(1,math.ceil((y1-y0-.32)/2.0)))]:box('Ceiling_crossmember',((x0+x1)/2,yy,h-.11),(x1-x0,.12,.22),'structural_coat')
        nx=max(1,math.ceil((x1-x0)/1.65));ny=max(1,math.ceil((y1-y0)/1.65))
        for ix in range(nx):
            for iy in range(ny):
                xa=x0+(x1-x0)*ix/nx+.06;xb=x0+(x1-x0)*(ix+1)/nx-.06
                ya=y0+(y1-y0)*iy/ny+.06;yb=y0+(y1-y0)*(iy+1)/ny-.06
                if xb-xa<.3 or yb-ya<.3:continue
                box('Recessed_ceiling_panel',((xa+xb)/2,(ya+yb)/2,h+.015),(xb-xa+.102,yb-ya+.102,.030),'mineral',.002)
                # Visible panel fixings at the ceiling, not floating decorative dots.
                for xx in [xa,xb]:
                    for yy in [ya,yb]:rod('Ceiling_panel_fixing',(xx,yy,h-.006),(xx,yy,h+.006),.008,'steel',6)
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
                for port in json.loads(INTERFACE_PATH.read_text())['ports']:
                    px,py,_=port['center'];dx,dy,_=port['outward'];match=(side=='S' and dy==-1 and abs(py-line)<1e-4)or(side=='N' and dy==1 and abs(py-line)<1e-4)or(side=='W' and dx==-1 and abs(px-line)<1e-4)or(side=='E' and dx==1 and abs(px-line)<1e-4)
                    if match:
                        c=px if side in 'SN' else py;cuts.append((c-port['clear_width']/2-.12,c+port['clear_width']/2+.12,port['clear_height']))
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
                    masonry_plane=line+(.15 if side in ['S','W'] else -.15)
                    box('Port_upper_masonry',(cc,masonry_plane,(h+ch)/2) if side in 'SN' else (masonry_plane,cc,(h+ch)/2),(wd,.30,h-ch) if side in 'SN' else (.30,wd,h-ch),'mineral',0)
            for u,v in intervals:
                a,b=((u,line),(v,line)) if side=='S' else ((line,u),(line,v)) if side=='E' else ((v,line),(u,line)) if side=='N' else ((line,v),(line,u))
                if stage=='full' and side in ['S','N'] and (abs(line)<1e-6 or abs(line-24)<1e-6):
                    inward=.34 if side=='S' else -.34
                    a=(a[0],a[1]+inward);b=(b[0],b[1]+inward)
                wall('Wall_'+side+str(line)+'_'+str(k)+'_'+str(u),a,b,h)
    # Every solid architecture face may support a prop; validator still raycasts actual geometry.
    for o in COL.objects:
        if o.type=='MESH':o['support_surface']=True
    collection('02_Structure_and_services')
    root('Bay_steelwork','wall',[(-2.026,7.25,3.64),(-2.2,12.95,3.64)],(-1,0,0))
    # Specific I-section girder, flange/web construction with bolted corbels.
    for yy in [7.25,12.95]:
        for zz in [4.04,4.28]:box('Girder_flange',(1.1,yy,zz),(6.54,.22,.045),'structural_coat')
        box('Girder_web',(1.1,yy,4.16),(6.54,.07,.24),'structural_coat')
        for xx in [-2.13,4.33]:
            beam('Girder_knee',(xx,yy,3.5),(xx+(.4 if xx<0 else -.4),yy,4.04),.10,.11,'teal')
            box('Bearing_plate',(xx+(.174 if yy==7.25 and xx<0 else 0),yy,3.64),(.14,.35,.5),'steel')
    pipework()
    if stage=='full':
        root('Longitudinal_tray','ceiling',[(xx,8.14,4.4) for xx in [5.3,8.8,11.8,15.1]]+[(15.85,yy,4.4) for yy in [14.5,18.5]],(0,0,1))
        for yy in [8.0,8.28]:
            box('Cable_tray_rail',(9.9,yy,4.12),(11.8,.035,.12),'darksteel')
        for xx in [4.6+i*.5 for i in range(23)]:box('Cable_tray_rung',(xx,8.14,4.07),(.024,.28,.026),'steel')
        for i in range(3):tube('Power_cable',[(4,8.04+i*.055,4.102)]+[(4.6+j*.5,8.04+i*.055,4.102) for j in range(22)]+[(15.3,8.04+i*.055,4.102),(15.80+i*.055,8.6,4.102)]+[(15.80+i*.055,8.9+j*.5,4.102) for j in range(24)],.021,'rubber')
        for xx in [5.3,8.8,11.8,15.1]:
            rod('Tray_suspension',(xx,8.14,4.4),(xx,8.14,4.03),.012,'steel')
            box('Tray_hanger_saddle',(xx,8.14,4.044),(.09,.34,.035),'steel')
        for xx in [15.71,15.99]:box('Delivery_tray_rail',(xx,14.39,4.12),(.035,12.5,.12),'darksteel')
        for i in range(26):box('Delivery_tray_rung',(15.85,8.14+i*.48,4.07),(.28,.024,.026),'steel')
        for yy in [14.5,18.5]:
            rod('Delivery_tray_drop',(15.85,yy,4.4),(15.85,yy,4.03),.012,'steel')
            box('Delivery_tray_saddle',(15.85,yy,4.044),(.34,.09,.035),'steel')
        root('Service_pipework','ceiling',[(xx,19.45,3) for xx in [2,5,8,11]],(0,0,1))
        tube('Service_air_loop',[(.91,13.2,2.67),(.91,19.2,2.67),(1.35,19.45,2.67),(11.9,19.45,2.67)],.052,'teal')
        rod('Air_supply_reserved_cap',(.91,13.185,2.67),(.91,13.23,2.67),.064,'steel',16)
        rod('Air_supply_reserved_end',(11.87,19.45,2.67),(11.915,19.45,2.67),.064,'steel',16)
        for yy in [14.1,16.3,18.4]:box('Pipe_support_standoff',(1.05,yy,2.67),(.30,.045,.08),'steel')
        for xx in [2,5,8,11]:rod('Pipe_hanger',(xx,19.45,3),(xx,19.45,2.61),.012,'darksteel')
        tube('Recess_air_branch',[(.91,14.8,2.67),(-1.06,14.8,2.67),(-1.06,14.8,2.16),(-1.49,14.8,2.14)],.025,'steel')
        rod('Service_branch_union',(-1.38,14.8,2.146),(-1.45,14.8,2.142),.046,'steel')

DETAIL_SOURCE=Path(__file__).resolve().with_name('valorant_details.py')
exec(compile(DETAIL_SOURCE.read_text(encoding='utf-8'),str(DETAIL_SOURCE),'exec'))
shell(A.stage)
collection('03_Thresholds')
door('FREIGHT_GATE',(6.35,10),3.4,3.4,-math.pi/2,False)
gate_drive_detail()
if A.stage=='full':
    # Main gate closure needs an architectural bulkhead around its track.
    root('Freight_bulkhead')
    for yy in [7.93,12.07]:
        for xx in [6.16,6.61]:box('Gate_steel_return',(xx,yy,1.7),(.08,.26,3.4),'teal')
    box('Gate_crown_beam',(6.35,10,4.345),(.45,4.4,.11),'darksteel')
    box('Gate_crown_infill',(6.35,10.32,4.13),(.26,3.76,.30),'mineral')
    box('Tray_penetration_lower_ledge',(6.35,8.12,3.985),(.45,.64,.03),'steel')
    door('PLANT_PORT',(-5.4,17.4),2.0,2.5,math.pi/2,True)
    door('CLEAN_PORT',(6.6,21),2.0,2.5,0,True)
    door('WASTE_PORT',(16.4,16),2.4,3.0,-math.pi/2,True)
    # Presentation caps are section-owned removable integration leaves, never edits to neighbors.
    door('REACTOR_BOUNDARY',(14.2,24),5.0,5.0,0,True)
    door('REFINERY_BOUNDARY',(0,0),2.6,3.0,math.pi,True)
collection('04_Freight_and_dressing');trolley();wall_station();floor_detail();task_light();detail_dressing(A.stage)
collection('05_Practical_lighting')
practical('Staging_warm_key',.15,11.78,4.4,180)
practical('Gate_cool_fill',3.32,8.45,4.4,140,True,math.pi/2)
practical('Staging_front_practical',1.10,7.65,4.4,110)
if A.stage=='full':
    for n,x,y,h,p,co,r in [('Entry',.0,4.0,4.4,270,False,0),('Cross',8.2,10,4.4,310,False,math.pi/2),('East',14.5,10.8,4.4,330,False,0),('Delivery',14.2,17,4.4,310,False,0),('Reactor',14.2,22.8,5.9,550,False,0),('Bypass',0,16.5,3,155,False,0),('North_service',4.6,19.8,3,155,False,math.pi/2),('North_service_2',10,19.8,3,130,False,math.pi/2),('Plant',-3.6,17.4,3,135,False,math.pi/2)]:practical(n,x,y,h,p,co,r)
else:
    practical('Slice_entry',0,4,4.4,100)
    practical('Slice_cross',7.5,10,4.4,110,False,math.pi/2)
    practical('Slice_service',0,14.5,3,65)

collection('06_Cameras_and_metadata');PAR=None
for name,loc,target,lens,role in CAMERAS+EXTRA_CAMERAS:
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);COL.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.04;d.clip_end=150;o['evaluation_role']=role
if A.stage=='full':
    contract=json.loads(INTERFACE_PATH.read_text(encoding='utf-8'))
    collection('07_Runtime_handoff');PAR=None
    handoff={'schema':'critical-shift-engine-handoff/1','section':'fuel-corridor','revision':A.revision,'units':'metres','space':'section-local +Y inward, +Z up','integration_state':'Authored Blender handoff; engine import/runtime not verified','interface_sha256':hashlib.sha256(INTERFACE_PATH.read_bytes()).hexdigest()}
    def marker(name,kind,loc,details,dimensions=None):
        obj=bpy.data.objects.new(name,None);COL.objects.link(obj);obj.location=loc;obj.empty_display_type='CUBE' if dimensions else 'ARROWS';obj.empty_display_size=1 if dimensions else .22
        if dimensions:obj.scale=Vector(dimensions)/2
        obj['handoff_kind']=kind;obj['handoff_data']=json.dumps(details);return {'id':name,'kind':kind,'position':list(loc),**details}
    handoff['spawn_markers']=[marker(name,'spawn',position,{'role':role,'engine_spawn_logic':'pending','feet_z':0}) for name,position,role in [('FC_ENTRY_START',(0,2.1,0),'section approach'),('FC_EAST_REENTRY',(13.8,12.0,0),'section reentry'),('FC_SERVICE_RESCUE',(0,16.6,0),'rescue staging')]]
    handoff['incident_hooks']=[marker(name,'incident',position,{'event':event,'target_assembly':target,'runtime_handler':'pending'}) for name,position,event,target in [('FC_HOOK_AIR_LEAK',(-1.49,14.8,2.14),'air_leak','Service_air_station'),('FC_HOOK_GATE_JAM',(6.35,10,3.7),'freight_gate_jam','FREIGHT_GATE'),('FC_HOOK_RESTRAINT',(2.65,12.32,.76),'carrier_restraint_fault','Long_cask_carrier')]]
    handoff['audio_zones']=[];handoff['network_boundaries']=[]
    for cell in contract['floor_cells']:
        x0,x1,y0,y1=cell['bounds'];h=cell['height'];dims=[x1-x0,y1-y0,h];loc=[(x0+x1)/2,(y0+y1)/2,h/2]
        desc={'bounds_min':[x0,y0,0],'bounds_max':[x1,y1,h],'cell':cell['id']}
        handoff['audio_zones'].append(marker('FC_AUDIO_'+cell['id'],'audio_zone',loc,{**desc,'ambience_intent':'ventilation and distant industrial structure','audio_assets_and_mix':'pending'},dims))
        handoff['network_boundaries'].append(marker('FC_NET_'+cell['id'],'network_boundary',loc,{**desc,'section_owner':'fuel-corridor','relevance_padding_m':2.0,'engine_replication':'pending'},dims))
    handoff['navigation']={'route_centerlines':contract['route_centerlines'],'freight_test_envelope_m':[2.4,2.2],'bypass_test_envelope_m':[2.0,2.2],'navmesh_bake':'pending engine integration','branch_approaches':[{'port':port['id'],'threshold':port['center'],'outward':port['outward'],'state':'closed termination; owner opening required'} for port in contract['ports'] if port['id'].startswith('S')],'neighbor_and_runtime_passage':'unverified'}
    handoff['doors']=[]
    for obj in S.objects:
        if obj.get('component_role')=='sliding_leaf_carriage':handoff['doors'].append({'carriage':obj.name,'assembly':obj.parent.name,'port_id':obj.parent['port_id'],'geometry_owner':'fuel-corridor','section_presentation_cap':bool(obj.parent['presentation_cap']),'cap_removal_scope':'Only listed moving members; retain fixed frame/sill/rails. Neighbor closure unchanged.' if obj.parent['presentation_cap'] else 'Not a presentation cap','translation_space':'section-local metres','pose':obj['current_pose'],'closed_to_open_section_vector_m':list(obj['closed_to_open_translation_m']),'members':sorted(c.name for c in obj.children),'controller_and_motion_validation':'see technical evidence; engine controller pending'})
    registry=[]
    for obj in S.objects:
        if obj.type not in ['MESH','CURVE']:continue
        if obj.type=='CURVE' and obj.data.bevel_depth<=0:continue
        chain=[];ancestor=obj
        while ancestor:chain.append(ancestor);ancestor=ancestor.parent
        if obj.get('surface_decal') or any(q in obj.name.lower() for q in ['scuff','paint_field','painted_rub','wear','label','type','rule','stitch','stripe','floor_arrow','white_line','joint']):policy='visual_only'
        elif any(p.get('component_role')=='sliding_leaf_carriage' for p in chain):policy='kinematic_geometry'
        elif any(p.name=='Long_cask_carrier' for p in chain):policy='carrier_convex_proxy_required'
        else:policy='static_evaluated_geometry'
        obj['collision_handoff']=policy;registry.append({'object':obj.name,'policy':policy})
    handoff['collision']={'geometry_registry':registry,'engine_collider_cooking':'pending; static evaluated meshes are source geometry, carrier needs a measured convex proxy','runtime_physics':'not simulated'}
    encoded=json.dumps(handoff,indent=2);S['engine_handoff_json']=encoded
    (ROOT/'scenery/handoff.json').write_text(encoded+'\n',encoding='utf-8')
S.camera=bpy.data.objects['C03_HERO']
S.world=bpy.data.worlds.new('Restrained ambient');S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.16,.2,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.18
S.render.engine='CYCLES';S.cycles.samples=A.samples;S.cycles.use_denoising=True;S.cycles.seed=71;S.cycles.max_bounces=8
S.render.resolution_x=A.width;S.render.resolution_y=round(A.width*.6666667);S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=.10
S['section']='fuel-corridor';S['revision']=A.revision;S['stage']=A.stage;S['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();S['original_geometry']=True
S['fixed_camera_spec']=json.dumps(CAMERAS)
S['detail_source_sha256']=hashlib.sha256(DETAIL_SOURCE.read_bytes()).hexdigest()
S['interface_sha256']=hashlib.sha256(INTERFACE_PATH.read_bytes()).hexdigest()
S['floor_albedo_sha256']=hashlib.sha256(FLOOR_ALBEDO.read_bytes()).hexdigest()
S['wall_albedo_sha256']=hashlib.sha256(WALL_ALBEDO.read_bytes()).hexdigest()
S['cloth_albedo_sha256']=hashlib.sha256(CLOTH_ALBEDO.read_bytes()).hexdigest()
# Resolve and record exact intended support targets from authored anchors. The independent
# validator checks both anchor-to-support and anchor-to-assembly mesh, rather than trusting this.
bpy.context.view_layer.update()
for ob in S.objects:
    if ob.type=='MESH' and any(ma in [M['cotton'],M['glove']] for ma in ob.data.materials):
        uv=ob.data.uv_layers.new(name='Textile_0p28m')
        for poly in ob.data.polygons:
            for li in poly.loop_indices:
                vv=ob.matrix_world@ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(vv.x/.28,vv.y/.28)
    if ob.type!='MESH' or not any(ma==M['mineral'] for ma in ob.data.materials):continue
    uv=ob.data.uv_layers.new(name='Planar_metres')
    normal_matrix=ob.matrix_world.to_3x3().inverted().transposed()
    for poly in ob.data.polygons:
        normal=normal_matrix@poly.normal
        axis=max(range(3),key=lambda i:abs(normal[i]))
        axes=(1,2) if axis==0 else (0,2) if axis==1 else (0,1)
        for li in poly.loop_indices:
            position=ob.matrix_world@ob.data.vertices[ob.data.loops[li].vertex_index].co
            uv.data[li].uv=(position[axes[0]]*.4,position[axes[1]]*.4)
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
manifest={'revision':A.revision,'stage':A.stage,'source_sha256':S['source_sha256'],'detail_source_sha256':S['detail_source_sha256'],'interface_sha256':S['interface_sha256'],'blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'objects':len(S.objects),'cameras':CAMERAS,'diagnostic_cameras':EXTRA_CAMERAS,'blend':str(blend),'samples':A.samples,'width':A.width,'material_sha256':{n:S[n+'_albedo_sha256'] for n in ['floor','wall','cloth']}}
if A.stage=='full':manifest['authored_handoff_sha256']=hashlib.sha256(S['engine_handoff_json'].encode('utf-8')).hexdigest()
(out/'build_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
if A.render:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='HIP';prefs.get_devices()
    for dev in prefs.devices:dev.use=dev.type=='HIP'
    assert any(dev.use for dev in prefs.devices),'No HIP device available for shared-gate render'
    S.cycles.device='GPU'
    names=[c[0] for c in CAMERAS] if A.render=='all' else A.render.split(',')
    for name in names:S.camera=bpy.data.objects[name];S.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    manifest['completed_render_sha256']={name:hashlib.sha256((out/(name+'.png')).read_bytes()).hexdigest() for name in names}
    manifest['render_batch_complete']=True
    (out/'build_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print('FUEL_BUILD_COMPLETE',A.revision,len(S.objects),str(blend))
