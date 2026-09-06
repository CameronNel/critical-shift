"""Dress the corrected Spawn room as a maintained, occupied workplace.

Latest user direction: no displayed suits; personal lockers, wood briefing floor,
woven carpet, sockets and the approved lived-in prop clusters. Separate output.
"""
import bpy, sys, math, json, random, hashlib, argparse, time
from pathlib import Path
from mathutils import Vector
from math import pi, sin, cos
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import grounded_kit as k
import grounded_room as room
import worn_surfaces as wear
import revise_spawn as rev
import validate_contacts as contact
RNG=random.Random(20260906)

def supported(root,target,anchors=[(0,0,0)],direction='WORLD_-Z',kind='FLOOR'):
    k.support(root,bpy.data.objects[target] if isinstance(target,str) else target,direction,anchors,kind)
    return root

def floor(root,anchors=[(0,0,0)]):return supported(root,'FACILITY_floor',anchors)

def textured(name,color,rough=.88,scale=(1,1,1),weave=False):
    mat=k.material(name,color,rough,0,.16,.0005,4)
    n=mat.node_tree.nodes;l=mat.node_tree.links;p=n.get('Principled BSDF')
    coord=n.new('ShaderNodeTexCoord');stretch=n.new('ShaderNodeVectorMath');stretch.operation='MULTIPLY';stretch.inputs[1].default_value=scale
    l.new(coord.outputs['Object'],stretch.inputs[0])
    for node in n:
        if node.type=='TEX_NOISE':l.new(stretch.outputs[0],node.inputs['Vector'])
    fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=110;fine.inputs['Detail'].default_value=2;l.new(stretch.outputs[0],fine.inputs['Vector'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.00065
    l.new(fine.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
    p.inputs['Specular IOR Level'].default_value=.24
    if weave:
        p.inputs['Sheen Weight'].default_value=.36
        waves=[]
        # Irregular short fibres avoid the moire of mathematically periodic bands.
        for stretch_axes in [(85,600,100),(600,85,100)] if name.startswith('rug_') else [(85,100,700),(700,100,85)]:
            rate=n.new('ShaderNodeVectorMath');rate.operation='MULTIPLY';rate.inputs[1].default_value=stretch_axes;l.new(coord.outputs['Object'],rate.inputs[0])
            wave=n.new('ShaderNodeTexNoise');wave.inputs['Scale'].default_value=1;wave.inputs['Detail'].default_value=2;l.new(rate.outputs[0],wave.inputs['Vector']);waves.append(wave.outputs['Fac'])
        weave_node=n.new('ShaderNodeMath');weave_node.operation='MULTIPLY';l.new(waves[0],weave_node.inputs[0]);l.new(waves[1],weave_node.inputs[1])
        weave_bump=n.new('ShaderNodeBump');weave_bump.inputs['Strength'].default_value=.55;weave_bump.inputs['Distance'].default_value=.0013
        l.new(weave_node.outputs[0],weave_bump.inputs['Height']);l.new(bump.outputs[0],weave_bump.inputs['Normal']);l.new(weave_bump.outputs[0],p.inputs['Normal'])
        # Millimetre yarn mottling and broad sun-fading remain visible at walking distance.
        broad=n.new('ShaderNodeTexNoise');broad.inputs['Scale'].default_value=7; broad.inputs['Detail'].default_value=3;l.new(coord.outputs['Object'],broad.inputs['Vector'])
        mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.55
        old=p.inputs['Base Color'].links[0].from_socket;l.new(old,mix.inputs[1]);l.new(broad.outputs['Color'],mix.inputs[2]);l.new(mix.outputs[0],p.inputs['Base Color'])
        yarn=n.new('ShaderNodeMixRGB');yarn.blend_type='MULTIPLY';yarn.inputs[0].default_value=.28;l.new(mix.outputs[0],yarn.inputs[1]);l.new(fine.outputs['Color'],yarn.inputs[2]);l.new(yarn.outputs[0],p.inputs['Base Color'])
    return mat

def materials():
    k.STAGE=3;k.M={m.name:m for m in bpy.data.materials}
    for name,color in [('canvas_olive',(.14,.17,.10)),('canvas_rust',(.27,.105,.05)),('cotton_blue',(.09,.15,.20)),('cotton_grey',(.28,.29,.25)),('cotton_cream',(.56,.50,.37))]:textured(name,color,.91,(1,1,2),True)
    for name,color in [('rug_field',(.23,.087,.044)),('rug_border',(.052,.087,.078)),('rug_cream',(.40,.32,.205))]:textured(name,color,.96,(1,1,1),True)
    textured('aged_socket',(.52,.51,.42),.71);textured('paper_board',(.58,.50,.33),.93)
    textured('rubbed_leather',(.14,.079,.038),.82,(2,1,1))
    for name,color in [('locker_paint',(.155,.218,.20)),('locker_pale',(.43,.44,.375))]:
        mat=textured(name,color,.76);p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Metallic'].default_value=.14
    k.material('board_enamel',(.62,.64,.55),.62,0,.035,.00015,3)
    k.material('dry_marker',(.055,.08,.073),.92,0,0,0,1)
    k.material('erased_marker',(.43,.46,.39),.9,0,.10,0,2)
    mat=k.material('amber_signal',(.70,.24,.028),.31,0,.025,0,1)
    p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Emission Color'].default_value=(1,.32,.028,1)
    for f,power in [(1,.25),(49,1.8),(97,.25),(145,.25)]:p.inputs['Emission Strength'].default_value=power;p.inputs['Emission Strength'].keyframe_insert(data_path='default_value',frame=f)
    for i in range(5):
        mat=k.material('floor_timber_%d'%i,(.22,.12,.05),.74,0,0,0,1);n=mat.node_tree.nodes;l=mat.node_tree.links;p=n['Principled BSDF']
        coord=n.new('ShaderNodeTexCoord');images={}
        for kind in ['diff','rough','disp']:
            im=bpy.data.images.get('wood_table_worn_'+kind+'_2k.jpg');assert im
            t=n.new('ShaderNodeTexImage');t.image=im;l.new(coord.outputs['UV'],t.inputs['Vector']);images[kind]=t.outputs['Color']
        tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=.38;tint.inputs[2].default_value=(.64+i*.09,.61+i*.085,.55+i*.08,1)
        l.new(images['diff'],tint.inputs[1]);l.new(tint.outputs[0],p.inputs['Base Color'])
        rough=n.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.55;rough.inputs['To Max'].default_value=.87;l.new(images['rough'],rough.inputs[0]);l.new(rough.outputs[0],p.inputs['Roughness'])
        bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.40;bump.inputs['Distance'].default_value=.004;l.new(images['disp'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
        p.inputs['Coat Weight'].default_value=.035;p.inputs['Specular IOR Level'].default_value=.32
        mat['source']='Packed CC0 Poly Haven wood_table_worn; per-plank UV, material tint, worn finish'
    bench=k.M['floor_timber_2'].copy();bench.name='bench_worn_timber';k.M[bench.name]=bench
    n=bench.node_tree.nodes;l=bench.node_tree.links;coord=next(o for o in n if o.type=='TEX_COORD')
    scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(.55,1.4,1.4);l.new(coord.outputs['Object'],scale.inputs[0])
    for node in n:
        if node.type=='TEX_IMAGE':node.projection='BOX';node.projection_blend=.15;l.new(scale.outputs[0],node.inputs['Vector'])
    for ob in bpy.data.objects:
        if ob.type=='MESH' and ('_laminate_slat' in ob.name or ob.name.startswith('BRIEFING_backrest_board')):
            ob.data.materials.clear();ob.data.materials.append(bench)
        if ob.type=='MESH' and ob.name.startswith('LOCKER_personal_'):
            for slot in ob.material_slots:
                if slot.material and slot.material.name in ['paint','pale']:slot.material=k.M['locker_paint' if slot.material.name=='paint' else 'locker_pale']

def timber_floor():
    vertices=[];faces=[];indices=[];uvs=[]
    def block(x0,x1,y0,y1,mat,offset):
        first=len(vertices);vertices.extend([(x,y,z) for z in [.006,.022] for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]])
        loops=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
        for loop in loops:
            faces.append(tuple(first+i for i in loop));indices.append(mat)
            uvs.append([((vertices[first+i][0]-x0)/1.65+offset[0],(vertices[first+i][1]-y0)/.72+offset[1]) for i in loop])
    for row in range(28):
        y0=1.0+row*(5.1/28);y1=y0+5.1/28
        xmax=-2.31 if y0<2.65 else -1.86
        x=-7.30-((row%3)*.54)
        while x<xmax:
            length=RNG.uniform(1.30,1.95);a=max(-7.3,x);b=min(xmax,x+length)
            if b-a>.03:block(a+.0015,b-.0015,y0+.0013,y1-.0013,RNG.randrange(5),(RNG.random(),RNG.random()))
            x+=length
    obj=k.mesh('BRIEFING_wood_floor',vertices,faces,'floor_timber_0')
    obj.data.materials.clear()
    for i in range(5):obj.data.materials.append(k.M['floor_timber_%d'%i])
    layer=obj.data.uv_layers.new(name='Metric staggered plank UV')
    for p,index,uv in zip(obj.data.polygons,indices,uvs):
        p.material_index=index
        for li,co in zip(p.loop_indices,uv):layer.data[li].uv=co
    k.bevel(obj,.0008,2);obj['asset_role']='timber_floor';obj['plank_count']=len(vertices)//8
    # A dark continuous underlay makes the narrow board joints read with real depth.
    k.box('BRIEFING_wood_underlay',(-4.805,3.55,.003),(4.99,5.1,.006),'darksteel',0)
    k.box('BRIEFING_wood_underlay_return',(-2.085,4.375,.003),(.45,3.45,.006),'darksteel',0)
    # Low tapered transition ends at the existing clear doorway.
    k.mesh('BRIEFING_wood_transition',[(-1.94,3.05,.022),(-1.70,3.05,.008),(-1.70,4.35,.008),(-1.94,4.35,.022)],[(0,1,2,3)],'steel')
    return obj

def carpet():
    nx,ny=61,53;width,depth=3.20,2.68;vertices=[];faces=[];indices=[]
    for j in range(ny):
        for i in range(nx):
            x=-width/2+i*width/(nx-1);y=-depth/2+j*depth/(ny-1)
            z=.030+.00035*sin(x*14+y*2)*cos(y*19)
            edge=min(width/2-abs(x),depth/2-abs(y))
            z+=.0055*math.exp(-((x-width/2)**2+(y-depth/2)**2)/.015)
            vertices.append((x,y,z))
    for j in range(ny-1):
        for i in range(nx-1):
            v=j*nx+i;faces.append((v,v+1,v+1+nx,v+nx));x,y,_=vertices[v];edge=min(width/2-abs(x),depth/2-abs(y))
            idx=1 if edge<.10 else 2 if .10<=edge<.16 or .25<edge<.28 else 0
            # A faded geometric weave occupies the center, subordinate to the furniture.
            if edge>.40 and abs((abs(x)% .70)-.35)+abs(y)<.19:idx=2
            indices.append(idx)
    o=k.mesh('BRIEFING_carpet',vertices,faces,'rug_field',True);o.location=(-4.55,3.55,0)
    o.data.materials.append(k.M['rug_border']);o.data.materials.append(k.M['rug_cream'])
    for face,i in zip(o.data.polygons,indices):face.material_index=i
    sol=o.modifiers.new('Woven backing','SOLIDIFY');sol.thickness=.006;sol.offset=-1
    o['asset_role']='woven_carpet';supported(o,'BRIEFING_wood_floor',[(.06,.045,.024)])
    for x in [-1.58,1.58]:
        for i in range(32):
            y=-1.29+i*.083;thread=k.tube('BRIEFING_rug_bound_stitch',[(x-.008,y,.030),(x,y+.012,.032),(x+.008,y+.024,.030)],.0009,'rug_cream');thread.parent=o
    for i in range(13):
        y=-1.32+i*.018;t=k.tube('BRIEFING_rug_frayed_corner',[(-1.59,y,.027),(-1.64-RNG.random()*.027,y+.009,.024)],.00065,'rug_cream');t.parent=o
    return o

def reset_support(root,target):
    root['cs_support_target']=target

def fold(name,p,mat='cotton_grey',width=.30,depth=.22,height=.065,angle=0):
    before=k.start()
    # Fabric wraps rounded folded edges and broad compression creases.
    nx,ny=19,15;vs=[]
    for j in range(ny):
        for i in range(nx):
            x=-width/2+width*i/(nx-1);y=-depth/2+depth*j/(ny-1)
            z=height-.009*(abs(x)/(width/2))**5+.003*sin(x*51+y*19)*sin(pi*i/(nx-1))
            vs.append((x,y,z))
    faces=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(ny-1) for i in range(nx-1)]
    boundary=list(range(nx))+[j*nx+nx-1 for j in range(1,ny)]+list(range((ny-1)*nx+nx-2,(ny-1)*nx-1,-1))+[j*nx for j in range(ny-2,0,-1)]
    base=len(vs);vs.extend([(vs[i][0]*.98,vs[i][1]*.98,0) for i in boundary])
    faces.append(tuple(range(base+len(boundary)-1,base-1,-1)))
    for j,i in enumerate(boundary):faces.append((i,base+j,base+(j+1)%len(boundary),boundary[(j+1)%len(boundary)]))
    o=k.mesh(name+'_folded_fabric',vs,faces,mat,True)
    for z in [height*.34,height*.69]:k.tube(name+'_fold_edge',[(-width*.46,-depth/2-.001,z),(0,-depth/2-.004,z+.002),(width*.46,-depth/2-.001,z)],.0014,mat)
    return k.group(name,before,p,angle)

def bag(name,p,mat='canvas_olive',angle=0):
    before=k.start()
    k.garment_loft(name+'_soft_canvas',[(0,0,.005,.18,.095),(-.008,0,.025,.22,.105),(.005,0,.12,.235,.105),(-.006,.008,.21,.205,.085),(0,0,.255,.16,.058),(0,0,.267,.05,.027)],mat,48)
    k.tube(name+'_zip',[(x,.0,.266+.004*cos(x*15)) for x in [-.145,-.10,-.05,0,.05,.10,.145]],.003,'darksteel')
    for y in [-.074,.074]:k.tube(name+'_webbing_handle',[(-.075,y,.23),(-.075,y,.335),(-.04,y,.365),(.04,y,.365),(.075,y,.335),(.075,y,.23)],.008,mat)
    k.panel(name+'_stitched_patch',(0,-.106,.12),.10,.055,.002,.007,'rubbed_leather')
    root=k.group(name,before,p,angle);root['asset_role']='personal_canvas_bag';return root

def thermos(name,p,angle=0):
    before=k.start()
    k.lathe(name+'_body',[(0,0),(.041,0),(.047,.015),(.047,.235),(.039,.248),(.031,.255),(0,.255)],'pressure_metal',48)
    k.lathe(name+'_grip',[(.047,.056),(.049,.06),(.049,.155),(.047,.16)],'rubbed_leather',48)
    k.lathe(name+'_cup_lid',[(0,.255),(.041,.255),(.043,.27),(.042,.312),(.035,.318),(0,.318)],'darksteel',48)
    return k.group(name,before,p,angle)

def hanger(name,x,y):
    before=k.start()
    # Twisted hook catches the rail, with a broad wooden triangular shoulder.
    pts=[(x,y,1.86),(x,y,1.945),(x,.132,1.989)]
    pts += [(x,.15+.018*cos(t),1.997+.018*sin(t)) for t in [pi+i*pi/20 for i in range(31)]]
    k.tube(name+'_hook',pts,.0025,'steel')
    k.tube(name+'_shoulders',[(x-.185,y,1.735),(x-.065,y,1.81),(x,y,1.85),(x+.065,y,1.81),(x+.185,y,1.735)],.010,'wood')
    k.rod(name+'_crossbar',(x-.185,y,1.735),(x+.185,y,1.735),.006,'wood')
    return k.group(name,before)

def jacket(name,p,mat='cotton_blue',angle=0):
    before=k.start()
    # A short work jacket: open collar, separate sleeves, no mannequin/head/gloves.
    profile=[(-.70,.195,.028),(-.68,.202,.032),(-.59,.194,.039),(-.52,.182,.037),(-.43,.190,.032),(-.34,.189,.036),(-.25,.202,.033),(-.18,.214,.036),(-.09,.23,.033),(-.018,.08,.026)]
    torso=k.garment_loft(name+'_body',[(.004*sin(z*12),0,z,w,d) for z,w,d in profile],mat,64)
    for v in torso.data.vertices:
        x,y,z=v.co;side=1 if y>0 else -1
        v.co.y+=side*(.005*sin(x*84+z*4)+.003*sin(x*39-z*9))*max(0,1-(x/.24)**2)
    for side in [-1,1]:
        sleeve=k.garment_loft(name+'_sleeve',[(side*.27,-.018,-.64,.030,.021),(side*.272,-.010,-.61,.039,.024),(side*.278,.0,-.50,.036,.030),(side*.267,0,-.42,.044,.026),(side*.261,.010,-.37,.040,.023),(side*.257,.006,-.30,.047,.031),(side*.24,.006,-.18,.057,.037),(side*.19,0,-.08,.055,.033)],mat,48)
        for v in sleeve.data.vertices:
            x,y,z=v.co;v.co.y+=(.003*sin(z*68+x*15))
        k.tube(name+'_pocket',[(side*.052,-.040,-.43),(side*.14,-.043,-.43),(side*.142,-.042,-.55),(side*.050,-.041,-.55)],.0012,mat)
        k.tube(name+'_shoulder_seam',[(side*.083,-.021,-.035),(side*.17,-.032,-.10),(side*.215,-.029,-.145)],.0014,mat)
    k.tube(name+'_zipper',[(.0,-.032,-.67),(.003,-.034,-.52),(.004,-.038,-.36),(0,-.028,-.04)],.002,'darksteel')
    k.tube(name+'_collar',[(-.08,0,-.014),(-.068,-.033,-.085),(0,-.037,-.042),(.068,-.033,-.085),(.08,0,-.014)],.007,mat)
    k.tube(name+'_hanging_loop',[(-.015,.014,-.024),(-.012,.015,.014),(.012,.015,.014),(.015,.014,-.024)],.003,mat)
    return k.group(name,before,p,angle)

def locker_leaf(name,side,opening,mat):
    before=k.start()
    k.box(name+'_sheet',(-side*.250,0,1.145),(.495,.021,2.085),mat,.003)
    for z in [.26,2.0]:
        k.rod(name+'_hinge',(0,0,z-.034),(0,0,z+.034),.012,'steel')
    k.tube(name+'_pull',[(-side*.414,-.016,1.12),(-side*.414,-.053,1.12),(-side*.414,-.053,1.28),(-side*.414,-.016,1.28)],.008,'darksteel')
    for z in [1.83,1.875,1.92]:k.box(name+'_vent',(-side*.25,-.0116,z),(.25,.0025,.011),'darksteel',.002)
    k.panel(name+'_label_holder',(-side*.25,-.015,1.70),.135,.063,.008,.004,'steel')
    k.box(name+'_label',(-side*.25,-.020,1.70),(.112,.002,.042),'paper',.001)
    root=k.group(name,before,(side*.515,-.319,0),side*math.radians(opening));root['asset_role']='personal_locker_leaf'
    wear.paint_chips(k,bpy.data.objects[name+'_sheet'])
    return root

def lockers():
    removed=[]
    for idx in range(1,5):
        name='PPE_%02d'%idx;root=bpy.data.objects[name]
        removed += rev.remove_prefix(name+'_PPE',name+'_garment_hanger',name+'_suspension',name+'_indicator')
        root['asset_role']='personal_locker';root['contents']='Hangers, shoes and individual belongings; no displayed suit'
        for ob in root.children_recursive:
            if ob.type=='MESH':
                for slot in ob.material_slots:
                    if slot.material and slot.material.name in ['pale','paint']:slot.material=k.M['locker_pale' if slot.material.name=='pale' else 'locker_paint']
        # Individual clothing and belongings have useful negative space between them.
        for j,(x,y) in enumerate([(-.23,.01),(.02,.09),(.24,.16)]):
            h=hanger('BELONG_%02d_hanger_%d'%(idx,j),x,y);h.parent=root
            supported(h,name+'_hanger_rail',[(x,.15,2.0125)],'LOCAL_-Z')
        shelf=k.box('BELONG_%02d_mid_shelf'%idx,(0,.012,.615),(1.0,.48,.020),'locker_pale',.002);shelf.parent=root
        for side,opening in [(-1,[100,20,95,105][idx-1]),(1,[105,110,20,95][idx-1])]:
            leaf=locker_leaf('BELONG_%02d_door_%s'%(idx,'L' if side<0 else 'R'),side,opening,'locker_paint' if idx%2 else 'locker_pale');leaf.parent=root
        if idx in [1,3]:
            cloth=jacket('BELONG_%02d_jacket'%idx,(-.12,-.025,1.83),'cotton_blue' if idx==1 else 'canvas_olive');cloth.parent=root
        previous=shelf
        for j in range(2 if idx in [1,4] else 1):
            cloth=fold('BELONG_%02d_fold_%d'%(idx,j),(.25,.016,.625+j*.056),['cotton_grey','cotton_cream'][j%2],width=.34,height=.055);cloth.parent=root
            supported(cloth,previous,[(0,0,0)],'LOCAL_-Z');previous=bpy.data.objects[cloth.name+'_folded_fabric']
        if idx in [2,4]:
            lunch=bag('BELONG_%02d_bag'%idx,(-.14,.0,.625),'canvas_rust' if idx==2 else 'canvas_olive');lunch.scale=(.73,.80,.80);lunch.parent=root
            supported(lunch,shelf,[(0,0,.005)],'LOCAL_-Z')
        if idx in [1,3]:
            flask=thermos('BELONG_%02d_thermos'%idx,(.34,.015,2.049));flask.parent=root;supported(flask,name+'_upper_cubby_shelf',direction='LOCAL_-Z')
        if idx==2:
            photo=room.mounted_print('BELONG_02_crew_photo',HERE.parent/'assets/portraits/commissioning_crew.png',(.31,.274,1.39),.18,.12);photo.parent=root
            supported(photo,name+'_back',direction='LOCAL_+Y',kind='WALL')
    return removed

def socket(name,p,angle,target):
    before=k.start()
    k.panel(name+'_backplate',(0,-.010,0),.14,.175,.020,.012,'aged_socket')
    k.panel(name+'_face',(0,-.022,0),.126,.157,.014,.010,'aged_socket')
    for x,z,r in [(0,.032,.010),(-.032,-.019,.008),(.032,-.019,.008)]:k.rod(name+'_recess',(x,-.028,z),(x,-.031,z),r,'darksteel',20)
    for z in [-.068,.068]:k.rod(name+'_screw',(0,-.030,z),(0,-.0315,z),.003,'steel',12)
    k.box(name+'_rocker',(.040,-.032,.045),(.022,.012,.039),'aged_socket',.003)
    root=k.group(name,before,p,angle);root['asset_role']='wall_socket';supported(root,target,direction='LOCAL_+Y',kind='WALL');return root

def wall_hook(name,p,angle,target):
    before=k.start();k.panel(name+'_plate',(0,-.008,0),.055,.105,.016,.009,'steel')
    k.tube(name+'_hook',[(0,-.015,-.03),(0,-.060,-.032),(0,-.081,-.002),(0,-.072,.026)],.008,'darksteel')
    root=k.group(name,before,p,angle);supported(root,target,direction='LOCAL_+Y',kind='WALL');return root

def clock(name,p,angle,target):
    before=k.start()
    k.rod(name+'_steel_case',(0,0,0),(0,-.045,0),.183,'darksteel',96)
    k.rod(name+'_face',(0,-.046,0),(0,-.049,0),.164,'paper',96)
    for i in range(60):
        theta=i*2*pi/60;r=.15;inner=.129 if i%5==0 else .142
        k.rod(name+'_tick',(sin(theta)*inner,-.051,cos(theta)*inner),(sin(theta)*r,-.051,cos(theta)*r),.0015 if i%5==0 else .0007,'ink',8)
    for i in [3,6,9,12]:
        theta=i*pi/6;k.label(name+'_number',str(i),(sin(theta)*.104,-.052,cos(theta)*.104-.012),.027,'ink',align='CENTER')
    hour=k.tube(name+'_hour_hand',[(0,-.054,-.014),(0,-.054,.077)],.0035,'ink');hour.rotation_euler.y=math.radians(285)
    minute=k.tube(name+'_minute_hand',[(0,-.057,-.017),(0,-.057,.120)],.0022,'ink');minute.rotation_euler.y=math.radians(110)
    second=k.tube(name+'_seconds',[(0,-.060,-.028),(0,-.060,.137)],.001,'red')
    for f,a in [(1,20),(1441,380)]:second.rotation_euler.y=math.radians(a);second.keyframe_insert(data_path='rotation_euler',frame=f)
    k.rod(name+'_pin',(0,-.060,0),(0,-.064,0),.006,'steel')
    root=k.group(name,before,p,angle);root['asset_role']='wall_clock';supported(root,target,direction='LOCAL_+Y',kind='WALL')

def paper_notice(name,p,angle,target,body='FILTER DELIVERY\nMOVED TO FRIDAY'):
    before=k.start();k.box(name+'_paper',(0,-.001,0),(.21,.002,.285),'paper',.001)
    for z in [.134,-.134]:k.box(name+'_tape',(0,-.003,z),(.065,.003,.024),'paper_board',.001)
    k.label(name+'_text',body,(-.086,-.004,.075),.024,'ink')
    root=k.group(name,before,p,angle);supported(root,target,direction='LOCAL_+Y',kind='WALL');return root

def bucket(name,p):
    before=k.start()
    o=k.lathe(name+'_dented_body',[(0,0),(.12,0),(.135,.027),(.165,.26),(.165,.28),(.151,.284),(.15,.26),(.127,.035),(0,.035)],'pale',64)
    for v in o.data.vertices:
        if v.co.x<0 and .05<v.co.z<.22:v.co.x+=.012*sin(pi*(v.co.z-.05)/.17)
    k.tube(name+'_wire_handle',[(.161*cos(t),0,.255+.19*sin(t)) for t in [i*pi/32 for i in range(33)]],.004,'steel')
    k.tube(name+'_grip',[(-.06,0,.435),(.06,0,.435)],.009,'rubber')
    root=k.group(name,before,p);floor(root)

def hanging_towel(name,p,mat='cotton_grey',angle=0,width=.32,length=.63):
    before=k.start();nx,ny=21,30;vs=[]
    for j in range(ny):
        for i in range(nx):
            x=(i/(nx-1)-.5)*width*(.17+.83*min(1,j/8));z=-length*j/(ny-1)
            y=-.029-.018*cos(x*52)*(j/(ny-1))-.015*sin(j*.22)
            vs.append((x,y,z))
    ob=k.mesh(name+'_cloth',vs,[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(ny-1) for i in range(nx-1)],mat,True)
    sol=ob.modifiers.new('Hemmed cotton thickness','SOLIDIFY');sol.thickness=.003
    k.tube(name+'_bottom_hem',[(vs[(ny-1)*nx+i][0],vs[(ny-1)*nx+i][1]-.001,-length+.008) for i in range(nx)],.002,mat)
    return k.group(name,before,p,angle)

def hallway():
    clock('LIFE_shift_clock',(1.7,.95,2.62),-pi/2,'HALL_right_spawn')
    paper_notice('LIFE_changed_shift',(1.7,1.54,1.55),-pi/2,'HALL_right_spawn')
    h=wall_hook('LIFE_hall_coat_hook',(-2.15,1.73,1.96),pi/2,'HALL_briefing_infill')
    coat=jacket('LIFE_hall_jacket',(0,-.058,-.02),'canvas_rust');coat.parent=h
    lunch=bag('LIFE_lunch_bag',(-1.89,1.36,-.005),'canvas_olive',pi/2);floor(lunch,[(0,0,.005)])
    bucket('LIFE_cleaning_bucket',(1.41,-.19,0))
    # Compact wall rack, mop stem and cotton head live at the spawn end.
    h=wall_hook('LIFE_mop_rack',(1.7,.23,1.49),-pi/2,'HALL_right_spawn')
    mop=k.rod('LIFE_mop_handle',(1.57,.21,.095),(1.63,.23,1.58),.014,'wood');mop['asset_role']='mop'
    mophead=k.start()
    k.box('LIFE_mop_head',(0,0,.042),(.22,.08,.035),'darksteel',.008)
    for i in range(25):
        x=RNG.uniform(-.12,.12);y=RNG.uniform(-.06,.06)
        k.tube('LIFE_mop_cotton',[(x,y,.057),(x*1.2,y*1.5,.017),(x*1.32,y*1.8,.006)],.004,'cotton_grey')
    root=k.group('LIFE_mop_floor_head',mophead,(1.565,.21,-.002));floor(root,[(0,0,.002)])
    # A dated repair on a quiet lower wall is intentionally limited to one patch.
    before=k.start();k.box('LIFE_paint_patch',(0,-.0008,0),(.33,.0016,.24),'pale',.0005)
    k.label('LIFE_patch_date','PATCHED  04 / 09',(-.12,-.002,-.077),.016,'ink')
    root=k.group('LIFE_repair_patch',before,(-1.7,6.52,.74),pi/2)
    # The lower finish sits 8mm toward the room; mount on its actual face.
    root.location.x=-1.692;supported(root,'HALL_left_ops_washable_dado',direction='LOCAL_+Y',kind='WALL')
    socket('LIFE_socket_hall_left',(-1.692,6.1,.43),pi/2,'HALL_left_ops_washable_dado')
    socket('LIFE_socket_hall_right',(1.692,7.65,.43),-pi/2,'HALL_right_ops_washable_dado')

def booklet(name,p,angle=0):
    before=k.start();k.box(name+'_pages',(0,0,.006),(.205,.28,.012),'paper',.003)
    vs=[(-.106,-.144,.014),(.106,-.144,.014),(.106,.144,.014),(-.100,.144,.024),(-.106,.07,.014)]
    k.mesh(name+'_bent_cover',vs,[(0,1,2,3,4)],'paper_board')
    k.label(name+'_title','SHIFT NOTES',(-.086,.05,.016),.022,'ink',rot=(0,0,0))
    k.label(name+'_chapter','PRE-ENTRY CHECK',(-.086,.011,.016),.013,'ink',rot=(0,0,0))
    k.tube(name+'_crease',[(-.095,-.14,.015),(-.095,.07,.017),(-.094,.138,.023)],.0008,'cotton_grey')
    return k.group(name,before,p,angle)

def whiteboard():
    before=k.start();k.box('LIFE_whiteboard_mount',(0,-.01,0),(1.52,.02,.84),'darksteel',.004)
    k.panel('LIFE_whiteboard_surface',(0,-.023,0),1.47,.79,.009,.012,'board_enamel')
    k.frame('LIFE_whiteboard_frame',(0,-.027,0),1.54,.86,.024,.025,'steel',.010)
    # Erased marker patches are quiet strokes, not an opaque fake decal.
    for j in range(6):k.tube('LIFE_whiteboard_erased',[(-.61,-.030,.02-j*.018),(-.21,-.030,.025-j*.019),(.03,-.030,.024-j*.019)],.0028,'erased_marker')
    for title,p,size,mat in [('SHIFT 04  /  HANDOVER',(-.64,-.032,.275),.057,'dry_marker'),('CHECK FILTER STOCK',(-.59,-.032,.135),.037,'dry_marker'),('NORTH PUMP  -  RECHECK',(-.59,-.032,-.015),.037,'dry_marker'),('Leave the spare keys here.',(-.58,-.032,-.235),.032,'dry_marker')]:
        t=k.label('LIFE_whiteboard_marker',title,p,size,mat);t.rotation_euler.y=.008
    k.tube('LIFE_whiteboard_underline',[(-.62,-.033,.248),(.61,-.033,.241)],.0018,'dry_marker')
    k.box('LIFE_whiteboard_tray',(0,-.07,-.437),(1.30,.12,.025),'steel',.004)
    k.rod('LIFE_whiteboard_pen',(.23,-.072,-.417),(.38,-.072,-.417),.005,'ink')
    k.box('LIFE_whiteboard_eraser',(-.38,-.075,-.412),(.10,.044,.022),'cotton_grey',.004)
    root=k.group('LIFE_whiteboard',before,(-6.28,6.1,1.74));supported(root,'BRIEFING_north',direction='LOCAL_+Y',kind='WALL')

def speaker(name,p,angle,target):
    before=k.start();k.box(name+'_mount',(0,-.025,0),(.15,.05,.18),'steel',.004)
    k.panel(name+'_cabinet',(0,-.102,0),.26,.33,.15,.025,'darksteel')
    k.panel(name+'_cloth_grille',(0,-.181,0),.218,.285,.003,.014,'rug_border')
    for z in [-.14,.14]:
        for x in [-.11,.11]:k.rod(name+'_screw',(x,-.177,z),(x,-.183,z),.003,'steel',8)
    root=k.group(name,before,p,angle);supported(root,target,direction='LOCAL_+Y',kind='WALL')

def briefing():
    timber_floor();carpet()
    for name in ['BRIEFING_sideboard','BRIEFING_mug','BRIEFING_notes']:bpy.data.objects[name].location.z+=.022
    reset_support(bpy.data.objects['BRIEFING_sideboard'],'BRIEFING_wood_floor')
    for name in ['BRIEFING_bench_01','BRIEFING_bench_02']:
        bpy.data.objects[name].location.z=.030;reset_support(bpy.data.objects[name],'BRIEFING_carpet')
    b=booklet('LIFE_training_booklet',(-5.25,3.10,.480),-.24)
    supported(b,'BRIEFING_bench_01_laminate_slat.001')
    before=k.start();k.panel('LIFE_remote_body',(0,0,0),.058,.18,.024,.015,'darksteel')
    for i in range(6):k.rod('LIFE_remote_button',((i%2)*.018-.009,-.014,(i//2)*.025-.04),((i%2)*.018-.009,-.018,(i//2)*.025-.04),.003,'aged_socket',12)
    remote=k.group('LIFE_remote',before,(-5.98,1.46,.812));remote.rotation_euler.x=pi/2;remote.rotation_euler.z=.12
    supported(remote,'BRIEFING_sideboard_laminate_top',[(0,-.012,0)])
    whiteboard();speaker('LIFE_briefing_speaker',(-7.3,5.13,2.57),pi/2,'BRIEFING_focal_wall')
    socket('LIFE_socket_briefing_TV',(-7.292,4.87,.40),pi/2,'BRIEFING_focal_wall_washable_dado')
    socket('LIFE_socket_briefing_side',(-3.06,6.092,.42),0,'BRIEFING_north_washable_dado')
    # TV and speaker cables follow one restrained surface conduit to the socket.
    k.tube('LIFE_TV_cable',[(-7.19,3.55,1.86),(-7.26,3.55,1.58),(-7.27,3.55,.40),(-7.27,4.84,.40)],.006,'rubber')
    k.tube('LIFE_speaker_cable',[(-7.22,5.13,2.53),(-7.27,5.13,.40),(-7.27,4.91,.40)],.004,'rubber')
    tv=bpy.data.objects['BRIEFING_TV'];before=k.start()
    # Native vector training diagram stays in the physical screen plane.
    for i,x in enumerate([-.81,0,.81]):
        k.frame('LIFE_TV_diagram',(x,-.101,-.045),.32,.27,.012,.001,'pale',.01)
        if i==0:
            for dx in [-.05,.05]:k.tube('LIFE_TV_hanger',[(x+dx-.03,-.102,-.04),(x+dx,-.102,.0),(x+dx+.03,-.102,-.04),(x+dx-.03,-.102,-.04)],.003,'paper')
        elif i==1:
            k.tube('LIFE_TV_graph',[(x-.11,-.102,-.11),(x-.045,-.102,-.02),(x+.025,-.102,-.06),(x+.11,-.102,.04)],.004,'paper')
        else:k.tube('LIFE_TV_return',[(x-.10,-.102,-.06),(x+.03,-.102,-.06),(x+.03,-.102,.04),(x-.02,-.102,.015)],.005,'paper')
    for x in [-.40,.405]:k.tube('LIFE_TV_arrow',[(x-.08,-.102,-.04),(x+.08,-.102,-.04),(x+.035,-.102,-.005)],.003,'pale')
    k.label('LIFE_TV_paused','PAUSED   02:14',(.70,-.103,-.55),.026,'paper')
    for o in set(bpy.data.objects)-before:o.parent=tv
    for o in tv.children:
        if o.name.startswith('BRIEFING_TV_step'):o.location.z=-.28

def locker_dressing():
    socket('LIFE_socket_locker_back',(8.092,5.53,.42),-pi/2,'LOCKER_far_washable_dado')
    socket('LIFE_socket_locker_south',(5.6,.708,.42),pi,'LOCKER_south_washable_dado')
    hook=wall_hook('LIFE_towel_hook',(2.22,.7,1.76),pi,'LOCKER_south')
    towel=hanging_towel('LIFE_locker_towel',(0,-.048,-.03),'cotton_cream');towel.parent=hook
    before=k.start()
    body=k.lathe('LIFE_laundry_canvas',[(0,0),(.18,0),(.22,.055),(.235,.47),(.22,.51),(.204,.506),(.214,.47),(.195,.060),(0,.060)],'canvas_olive',72)
    body.scale=(1,.82,1)
    for z in [.045,.465]:
        rim=k.lathe('LIFE_laundry_rim',[(.213,z),(.233,z),(.235,z+.015),(.213,z+.015),(.213,z)],'rubbed_leather',72);rim.scale=(1,.82,1)
    k.tube('LIFE_laundry_handle',[(-.12,-.18,.45),(-.12,-.19,.55),(.12,-.19,.55),(.12,-.18,.45)],.010,'rubbed_leather')
    root=k.group('LIFE_laundry_hamper',before,(2.19,1.22,0));floor(root)
    for i,(x,y,angle) in enumerate([(4.25,2.81,-.2),(4.08,2.91,.09)]):
        boot=k.boot('LIFE_bench_boot_%d'%i,(x,y,-.012),angle);floor(boot,[(0,-.025,.012)])
    # Supplies form a single wall shelf cluster in the far corner.
    before=k.start();shelf=k.box('LIFE_supply_shelf_deck',(0,-.15,0),(1.10,.30,.025),'pale',.003)
    for x in [-.43,.43]:k.tube('LIFE_supply_bracket',[(x,0,-.20),(x,-.27,-.01),(x,0,-.01)],.013,'steel')
    assembly=k.group('LIFE_supply_shelf',before,(8.1,6.40,1.30),-pi/2);supported(assembly,'LOCKER_far',[(x,0,-.20) for x in [-.43,.43]],'LOCAL_+Y','WALL')
    for i,x in enumerate([-.35,-.20]):
        can=k.filter_can('LIFE_spare_filter_%d'%i,(x,-.15,.0125));can.parent=assembly;supported(can,shelf,direction='LOCAL_-Z')
    for i in range(2):
        box=k.box('LIFE_sealed_gloves_%d'%i,(.25,-.14,.053+i*.08),(.29,.20,.08),'paper_board',.004);box.parent=assembly
        tag=k.label('LIFE_glove_box_label','WORK GLOVES',(.14,-.241,.045+i*.08),.016,'ink');tag.parent=assembly
        tape=k.box('LIFE_glove_box_tape',(.25,-.14,.0935+i*.08),(.033,.20,.001),'paper',.0003);tape.parent=assembly
    label=k.label('LIFE_supply_label','SPARE FILTERS',(-.34,-.306,-.006),.022,'ink');label.parent=assembly
    # A service hose connects the chamber spine to an actual wall termination.
    before=k.start()
    k.tube('LIFE_pod_service_hose',[(8.1,4,.52),(7.94,4,.52),(7.9,4,.36),(7.765,4,.36)],.026,'rubber')
    k.rod('LIFE_pod_wall_coupling',(8.045,4,.52),(8.1,4,.52),.065,'steel')
    service=k.group('LIFE_pod_service_connection',before);supported(service,'LOCKER_far',[(8.1,4,.52)],'WORLD_+X','WALL')
    log=k.clipboard('LIFE_pod_inspection_log',(8.1,5.37,1.56),-pi/2)
    # A clipboard normally lies in XY. Stand it upright and face it into the room.
    log.rotation_euler=(pi/2,0,-pi/2)
    supported(log,'LOCKER_far',[(0,0,0)],'WORLD_+X','WALL')

def airlock_life():
    before=k.start()
    k.rod('LIFE_airlock_lamp_mount',(0,0,0),(0,-.027,0),.061,'darksteel',48)
    k.rod('LIFE_airlock_amber_lens',(0,-.03,0),(0,-.063,0),.040,'amber_signal',48)
    for x in [-.032,.032]:k.tube('LIFE_airlock_lens_guard',[(x,-.023,-.043),(x,-.070,-.042),(x,-.070,.042),(x,-.023,.043)],.004,'steel')
    root=k.group('LIFE_airlock_status',before,(-.95,9.145,2.73));root['asset_role']='airlock_status_lamp';supported(root,'AIRLOCK_pressure_ring',direction='LOCAL_+Y',kind='WALL')
    # Door pressure gauge is integrated into the leaf; the removed Geiger stays absent.
    before=k.start();k.rod('LIFE_airlock_gauge_case',(0,0,0),(0,-.035,0),.105,'steel',64)
    k.rod('LIFE_airlock_gauge_dial',(0,-.036,0),(0,-.038,0),.090,'paper',64)
    for i in range(11):
        a=-2.35+i*.47;k.rod('LIFE_airlock_pressure_tick',(.068*sin(a),-.041,.068*cos(a)),(.080*sin(a),-.041,.080*cos(a)),.001,'ink',8)
    k.tube('LIFE_airlock_pressure_needle',[(0,-.044,0),(.034,-.044,.051)],.0017,'red')
    k.label('LIFE_airlock_pressure_unit','kPa',(-.024,-.044,-.050),.018,'ink')
    gauge=k.group('LIFE_airlock_pressure_gauge',before,(-.89,9.221,1.88));supported(gauge,'AIRLOCK_steel_face',direction='LOCAL_+Y',kind='WALL')
    # Narrow traffic-worn amber band in front of the threshold, outside the walkway rise.
    vs=[];fs=[]
    for a,b in [(-1.245,-.62),(-.60,.38),(.402,1.245)]:
        upper=[];lower=[]
        for i in range(28):
            x=a+(b-a)*i/27;upper.append((x,8.8725-RNG.uniform(0,.004),.0007));lower.append((x,8.8075+RNG.uniform(0,.005),.0007))
        start=len(vs);vs.extend(lower+list(reversed(upper)));fs.append(tuple(range(start,len(vs))))
    mark=k.mesh('LIFE_airlock_floor_boundary',vs,fs,'yellow');floor(mark,[(0,8.84,.0007)])

def validate(out):
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cache={};rows=[]
    for o in sorted(contact.get_collection_objects(contact.REQUIRED_COLLECTION),key=lambda o:o.name):rows.append(contact.validate_object(o,cache,dg))
    failures=[r for r in rows if r['status']!='PASS'];report={'status':'FAIL' if failures else 'PASS','objects_checked':len(rows),'failures':failures,'objects':rows}
    (out/'contacts.json').write_text(json.dumps(report,indent=2))
    blocked=[]
    for label,x,width in [('briefing',-1.78,1.30),('locker',1.78,2.20)]:
        for j in range(17):
            y=3.7-width/2+.025+(width-.05)*j/16
            for z in [.045,.45,1.1,1.63,2.16]:
                hit,loc,n,ix,obj,m=bpy.context.scene.ray_cast(dg,Vector((x-.21,y,z)),Vector((1,0,0)),distance=.42)
                if hit:blocked.append({'portal':label,'object':obj.name})
    route_hits=[];route_rays=0
    for area,paths in [
        ('hall', [((x,.55,z),(x,8.60,z)) for x in [-.60,.60] for z in [.10,1.63]]),
        ('locker_center', [((1.95,y,z),(5.60,y,z)) for y in [3.60,4.40] for z in [.10,1.63]]),
        ('briefing_north', [((-6.75,5.35,z),(-2.40,5.35,z)) for z in [.10,1.63]])]:
        for a,b in paths:
            direction=Vector(b)-Vector(a);hit,loc,n,ix,obj,m=bpy.context.scene.ray_cast(dg,Vector(a),direction.normalized(),distance=direction.length);route_rays+=1
            if hit:route_hits.append({'area':area,'object':obj.name,'point':list(loc)})
    checks={
       'no_displayed_suits':not any('continuous_coverall' in o.name or o.get('asset_role')=='primary_PPE' for o in bpy.data.objects),
       'four_personal_lockers':sum(o.get('asset_role')=='personal_locker' for o in bpy.data.objects)==4,
       'twelve_clothes_hangers':len([o for o in bpy.data.objects if o.name.startswith('BELONG_') and '_hanger_' in o.name and o.type=='EMPTY' and not o.get('cs_support_anchor')])==12,
       'shoes_retained':len([o for o in bpy.data.objects if '_work_boot' in o.name and o.type=='EMPTY' and not o.get('cs_support_anchor')])==8,
       'two_briefing_benches':sum(o.get('asset_role')=='briefing_bench' for o in bpy.data.objects)==2,
       'wood_floor':bool(bpy.data.objects.get('BRIEFING_wood_floor')),
       'woven_carpet':bool(bpy.data.objects.get('BRIEFING_carpet')),
       'six_wall_sockets':sum(o.get('asset_role')=='wall_socket' for o in bpy.data.objects)==6,
       'wall_clock':bool(bpy.data.objects.get('LIFE_shift_clock')),
       'whiteboard_and_training_booklet':bool(bpy.data.objects.get('LIFE_whiteboard')) and bool(bpy.data.objects.get('LIFE_training_booklet')),
       'cleaning_station':bool(bpy.data.objects.get('LIFE_cleaning_bucket')),
       'doorways_clear_170_rays':not blocked,
       'main_room_routes_clear':not route_hits,
       'all_support_contacts':not failures,
       'all_used_images_packed':all(im.packed_file or im.packed_files for im in bpy.data.images if im.source=='FILE' and im.users),
       'shadow_correction_retained':bpy.context.scene.eevee.use_shadows and bpy.context.scene.eevee.use_shadow_jitter_viewport,
       'no_geiger_or_room_doors':not any(bpy.data.objects.get(n) for n in ['RADIATION','BRIEFING_entry_LEAF','LOCKER_entry_LEAF']),
    }
    report={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'blocked_rays':blocked,'route_rays':route_rays,'route_hits':route_hits,'contacts':len(rows),'failed_contacts':[{'name':x['object'],'issues':x['issues']} for x in failures]}
    (out/'checks.json').write_text(json.dumps(report,indent=2));print('INHABITED_CHECKS',json.dumps(report),flush=True);return report

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--review',default='inhabited-01');ap.add_argument('--validate-only',action='store_true');ap.add_argument('--no-bake',action='store_true');ap.add_argument('--cameras',default='VALIDATE_Spawn,VALIDATE_BriefingDoor,VALIDATE_LockerDoor,VALIDATE_ExitReverse,DETAIL_LockerLife,DETAIL_BriefingFloor');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    out=HERE.parent/'production/renders/review'/a.review;out.mkdir(parents=True,exist_ok=True);s=bpy.context.scene;source=Path(bpy.data.filepath);t=time.time()
    if not a.validate_only:
        materials();removed=lockers();briefing();hallway();locker_dressing();airlock_life();rev.startup()
        room.cam('DETAIL_LockerLife',(4.9,4.9,1.63),(3.6,6.99,1.27),26)
        room.cam('DETAIL_BriefingFloor',(-2.40,2.0,1.63),(-4.65,3.8,.48),23)
        room.cam('DETAIL_HallLife',(.45,3.2,1.63),(-1.8,1.5,1.10),24)
        room.cam('DETAIL_LockerSupplies',(5.8,4.85,1.63),(8.1,6.2,1.38),27)
        s['user_revision']='Personal locker contents; no display suits. Worn wood briefing floor, woven rug, sockets and lived-in prop clusters.'
        (out/'removed_objects.json').write_text(json.dumps(removed,indent=2))
        if not a.no_bake:print('BAKE_INHABITED_INDIRECT',flush=True);bpy.ops.object.lightprobe_cache_bake(subset='ALL')
        rev.startup();destination=HERE/'spawnroom_inhabited_walk.blend';bpy.ops.wm.save_as_mainfile(filepath=str(destination),compress=True)
    else:destination=source
    report=validate(out);s.render.resolution_x=1120;s.render.resolution_y=700;s.render.resolution_percentage=100
    for name in a.cameras.split(','):
        if not name:continue
        s.camera=bpy.data.objects[name];s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    result={'source':str(source),'output':str(destination),'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'engine':s.render.engine,'blender':bpy.app.version_string,'cameras':a.cameras.split(','),'elapsed_seconds':time.time()-t}
    (out/'provenance.json').write_text(json.dumps(result,indent=2));print('INHABITED_COMPLETE',json.dumps(result),flush=True)
    assert report['status']=='PASS','Read contacts.json and checks.json'

if __name__=='__main__':main()
