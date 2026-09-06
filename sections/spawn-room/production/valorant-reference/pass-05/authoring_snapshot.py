"""Reference-led maintained facility polish, authored over the live-state checkpoint.

Targets are the three ChatGPT browser concepts in production/valorant-reference.
Never consumes an earlier unrelated .blend or overwrites the inhabited source.
"""
import bpy, sys, math, random, json, argparse, time, hashlib
from pathlib import Path
from mathutils import Vector
from math import pi, sin, cos
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import grounded_kit as k
import grounded_room as room
import inhabit_spawn as life
import revise_spawn as rev
import validate_contacts as contacts
import worn_surfaces as wear
R=random.Random(61129)
EVIDENCE=HERE.parent/'production/valorant-reference'

def surf(name,col,rough=.85,metal=0,variation=.13,relief=.0008):
    m=k.material(name,col,rough,metal,variation,relief,4)
    n=m.node_tree.nodes;l=m.node_tree.links;p=n['Principled BSDF']
    p.inputs['Specular IOR Level'].default_value=.22 if metal else .17
    coord=n.new('ShaderNodeTexCoord')
    for node in list(n):
        if node.type=='TEX_NOISE':l.new(coord.outputs['Object'],node.inputs['Vector'])
    return m

def materials():
    k.STAGE=3;k.M={m.name:m for m in bpy.data.materials}
    for i in range(5):
        m=k.M['floor_timber_%d'%i];n=m.node_tree.nodes;p=n['Principled BSDF']
        p.inputs['Coat Weight'].default_value=0;p.inputs['Specular IOR Level'].default_value=.12
        for a in n:
            if a.type=='MAP_RANGE':a.inputs['To Min'].default_value=.90;a.inputs['To Max'].default_value=.98
            if a.type=='BUMP':a.inputs['Distance'].default_value=.0025
        tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(.66,.77,.88,1)
        m.node_tree.links.new(p.inputs['Base Color'].links[0].from_socket,tint.inputs[1]);m.node_tree.links.new(tint.outputs[0],p.inputs['Base Color'])
        m['finish']='Matte oiled, no varnish; roughness 0.90-0.98'
    for name in ['wall','dado']:
        m=k.M[name]
        # Preserve the packed trowel/paint maps while reducing high-frequency relief.
        for n in m.node_tree.nodes:
            if n.type=='BUMP':n.inputs['Distance'].default_value*=.87
    for name,c,rough,metal in [
        ('V_locker_steel',(.047,.075,.071),.80,.35),('V_graphite',(.043,.051,.049),.76,.5),
        ('V_brushed',(.29,.32,.30),.54,.8),('V_ceramic',(.46,.44,.36),.9,0),
        ('V_terracotta',(.34,.14,.069),.93,0),('V_ochre',(.37,.255,.105),.9,0),
        ('V_potstone',(.36,.35,.30),.95,0),('V_soil',(.042,.035,.022),.98,0),
        ('V_leaf0',(.042,.095,.031),.86,0),('V_leaf1',(.081,.146,.041),.84,0),
        ('V_leaf2',(.115,.188,.057),.84,0),('V_leaf3',(.17,.20,.07),.9,0),
        ('V_stem',(.070,.10,.033),.9,0),('V_bark',(.085,.061,.032),.93,0),('V_paper',(.57,.51,.38),.95,0),
        ('V_cardboard',(.25,.19,.108),.94,0),('V_rustred',(.20,.022,.012),.61,.65),
        ('V_tilegrout',(.21,.24,.22),.98,0)]:surf(name,c,rough,metal)
    wear.mineral(k.M['V_potstone'],'plastered_wall',(.29,.28,.24),.004)
    wear.mineral(k.M['V_terracotta'],'plastered_wall',(.32,.12,.056),.003)
    wear.mineral(k.M['V_ochre'],'plastered_wall',(.24,.14,.065),.002)
    bm=k.M['bench_worn_timber'];bp=bm.node_tree.nodes['Principled BSDF']
    bp.inputs['Coat Weight'].default_value=0;bp.inputs['Specular IOR Level'].default_value=.17
    for node in bm.node_tree.nodes:
        if node.type=='MAP_RANGE':node.inputs['To Min'].default_value=.78;node.inputs['To Max'].default_value=.94
    for root in bpy.data.objects:
        if root.type=='EMPTY' and ('bench' in root.name and not root.get('cs_support_anchor')):
            for ob in root.children_recursive:
                if ob.type=='MESH':
                    for slot in ob.material_slots:
                        if slot.material and slot.material.name=='steel':slot.material=k.M['V_graphite']
    for i in range(6):surf('V_tile%d'%i,[(.46,.49,.45),(.49,.50,.46),(.42,.46,.42),(.48,.49,.44),(.44,.475,.435),(.47,.48,.43)][i],.85,0,.07,.00025)
    # Aged utility metal has broad colour, avoiding the old stretched generated grain.
    for key in ['pale','paint']:
        m=k.M[key]
        replacement=surf('V_utility_'+key,(.35,.36,.31) if key=='pale' else (.16,.215,.19),.82,.12)
        for o in bpy.data.objects:
            if o.type=='MESH' and not o.name.startswith('PPE_'):
                for slot in o.material_slots:
                    if slot.material==m:slot.material=replacement

def floor_contact(o,target='FACILITY_floor',anchors=[(0,0,0)]):
    return life.supported(o,target,anchors)

def bathroom_floor():
    rev.remove_prefix('TRAFFIC_1','TRAFFIC_2','TRAFFIC_3','FLOOR_replacement_1')
    # Single joined tile mesh; shallow real bevel and grout, no coplanar surfaces.
    vs=[];fs=[];idx=[]
    x0,x1,y0,y1=1.86,8.1,.7,7.3;pitch=.10;top=.006
    for ix in range(63):
        a=x0+ix*pitch;b=min(x1,a+pitch)
        if b-a<.015:continue
        for iy in range(66):
            c=y0+iy*pitch;d=min(y1,c+pitch)
            a1,b1,c1,d1=a+.0013,b-.0013,c+.0013,d-.0013
            start=len(vs);vs.extend([(x,y,z) for z in [.001,top] for x,y in [(a1,c1),(b1,c1),(b1,d1),(a1,d1)]])
            mi=R.choices(range(6),[4,3,1,3,2,3])[0]
            for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:fs.append(tuple(start+j for j in f));idx.append(mi)
    start=len(vs);vs.extend([(x0,y0,.004),(x1,y0,.004),(x1,y1,.004),(x0,y1,.004)]);fs.append(tuple(range(start,start+4)));idx.append(6)
    o=k.mesh('V_LOCKER_porcelain_tiles',vs,fs,'V_tile0')
    o.data.materials.clear()
    for i in range(6):o.data.materials.append(k.M['V_tile%d'%i])
    o.data.materials.append(k.M['V_tilegrout'])
    for p,mi in zip(o.data.polygons,idx):p.material_index=mi
    k.bevel(o,.0006,2);o['asset_role']='locker_small_porcelain_tiles';o['tile_pitch_m']=pitch
    # Raise only existing floor-supported locker assemblies by the new 6 mm finish.
    bpy.context.view_layer.update()
    for ob in list(bpy.data.objects):
        if ob.get('cs_support_target')!='FACILITY_floor':continue
        loc=ob.matrix_world.translation
        is_locker=(ob.name.startswith(('PPE_','LOCKER_','INTEGRITY_','LIFE_laundry','LIFE_bench_boot')) or (1.9<loc.x<8.1 and .7<loc.y<7.3))
        if not is_locker:continue
        ob.location.z+=top;ob['cs_support_target']=o.name
    for ob in bpy.data.objects:
        if ob.name.startswith('TRAFFIC_') and ob.matrix_world.translation.x>1.85:ob.hide_render=True;ob.hide_viewport=True
    k.mesh('V_LOCKER_tile_transition',[(1.70,2.60,.001),(1.94,2.60,top),(1.94,4.8,top),(1.70,4.8,.001)],[(0,1,2,3)],'V_brushed')

def lockers():
    rev.remove_prefix('LOCKER_personal_north','LOCKER_personal_south')
    for idx in range(1,5):
        name='PPE_%02d'%idx;root=bpy.data.objects[name]
        for o in root.children_recursive:
            if o.type=='MESH':
                for slot in o.material_slots:
                    if slot.material and slot.material.name in ['locker_paint','locker_pale','paint','pale']:
                        slot.material=k.M['V_locker_steel']
        for side,suffix in [(-1,'L'),(1,'R')]:
            door=bpy.data.objects['BELONG_%02d_door_%s'%(idx,suffix)]
            door.rotation_euler.z=side*math.radians(108)
            for o in door.children_recursive:
                if o.type=='MESH':
                    for slot in o.material_slots:
                        if slot.material and slot.material.name in ['locker_paint','locker_pale']:slot.material=k.M['V_locker_steel']
        root['construction']='Identical 1.05m folded-steel locker body, 2.2425m height, matching paired 108-degree open doors'
        root['finish']='Low sheen graphite-teal powder coat'

def modern_door():
    rev.remove_prefix('HALL_rear_door');b=k.start()
    k.box('V_REAR_solid_leaf',(0,0,1.097),(1.23,.070,2.184),'V_graphite',.009)
    k.frame('V_REAR_flush_reveal',(0,-.037,1.10),1.12,2.045,.008,.003,'V_brushed',.009)
    for x in [-.666,.666]:k.box('V_REAR_jamb',(x,-.012,1.115),(.078,.145,2.23),'V_graphite',.005)
    k.box('V_REAR_lintel',(0,-.012,2.244),(1.41,.145,.085),'V_graphite',.005)
    for z in [.79,1.29]:k.rod('V_REAR_pull_standoff',(.45,-.04,z),(.45,-.10,z),.012,'V_brushed')
    k.box('V_REAR_vertical_pull',(.45,-.101,1.04),(.028,.036,.54),'V_brushed',.005)
    k.box('V_REAR_threshold',(0,-.026,.004),(1.30,.16,.008),'V_brushed',.002)
    k.label('V_REAR_staff_label','STAFF ACCESS',(-.22,-.038,1.91),.035,'paper')
    root=k.group('V_REAR_staff_door',b,(0,-.35,0),pi);root['asset_role']='modern_inaccessible_staff_door'
    b=k.start();k.box('V_REAR_reader_mount',(0,-.008,0),(.092,.016,.19),'V_graphite',.01)
    k.panel('V_REAR_reader_face',(0,-.023,0),.077,.175,.018,.009,'darksteel')
    k.box('V_REAR_reader_green',(0,-.034,.054),(.028,.002,.010),'ready',.002)
    k.label('V_REAR_reader_icon','|||',(-.016,-.034,-.023),.022,'pale')
    o=k.group('V_REAR_card_reader',b,(-.82,-.339,1.15),pi);life.supported(o,'HALL_rear_left',direction='LOCAL_+Y',kind='WALL')

def leaf(name,base,direction,length,width,mi=0):
    axis=Vector(direction).normalized();side=axis.cross(Vector((0,0,1)))
    if side.length<.01:side=Vector((1,0,0))
    side.normalize();normal=side.cross(axis).normalized();v=[]
    for i in range(13):
        t=i/12;center=Vector(base)+axis*(t*length)+Vector((0,0,-.23*length*t*t))
        w=width*(sin(pi*t)**.72)*(1+.07*sin(t*15+mi))
        for s in [-1,-.5,0,.5,1]:v.append(tuple(center+side*s*w+normal*(.095*length*sin(pi*t)*(1-abs(s))+.035*length*s*sin(t*5+mi))))
    f=[]
    for i in range(12):
        for j in range(4):a=i*5+j;f.append((a,a+1,a+6,a+5))
    ob=k.mesh(name,v,f,'V_leaf%d'%mi,True)
    ob.data.materials.append(k.M['V_leaf%d'%((mi+1)%3)])
    for p in ob.data.polygons:p.material_index=1 if p.index%4>1 else 0
    sol=ob.modifiers.new('Leaf edge thickness','SOLIDIFY');sol.thickness=.0012
    rib=[v[i*5+2] for i in range(1,12)]
    k.tube(name+'_midrib',rib,.0015,'V_stem')
    return ob

def plant(name,p,size=1,kind='ficus',pot='V_potstone',target='FACILITY_floor'):
    b=k.start();height=.47;radius=.215
    # Thick rolled rim, slight taper, dark soil and a contrasting worn foot band.
    vessel=k.lathe(name+'_pot',[(0,0),(.167,0),(.176,.025),(.220,.435),(.222,.468),(.217,.478),(.201,.478),(.199,.445),(.17,.055),(0,.055)],pot,64)
    for v in vessel.data.vertices:
        a=math.atan2(v.co.y,v.co.x);v.co.x*=1+.008*sin(a*5+v.co.z*11);v.co.y*=1+.006*cos(a*7-v.co.z*13)
    k.lathe(name+'_base_band',[(.172,.035),(.186,.035),(.193,.115),(.183,.115),(.172,.035)],'V_ochre',48)
    k.rod(name+'_soil',(0,0,.427),(0,0,.430),.197,'V_soil',40)
    if kind=='snake':
        for j in range(17):
            a=j*2.399;base=(.09*cos(a),.09*sin(a),.427);length=R.uniform(.55,1.10)
            leaf(name+'_blade',base,(.28*cos(a),.28*sin(a),1),length,.035+(j%3)*.010,j%3)
    elif kind=='trailing':
        for j in range(13):
            a=j*2.399;leaf(name+'_crown_leaf',(.05*cos(a),.05*sin(a),.44),(cos(a),sin(a),.9),.28,.10,j%3)
        for j in range(5):
            a=pi+j*pi/4;pts=[]
            for i in range(8):
                t=i/7;pt=(cos(a)*(.08+.28*t),sin(a)*(.08+.28*t),.44+.08*sin(t*pi)-.65*t*t);pts.append(pt)
                if i>0:leaf(name+'_pothos',pt,(cos(a+(-1)**i),sin(a+(-1)**i),.25),.18,.07,(i+j)%3)
            k.tube(name+'_vine',pts,.006,'V_stem')
    else:
        bounds=(-7.29,-1.91,1.03,6.06) if target=='BRIEFING_wood_floor' else (1.9,8.05,.74,7.26) if target=='V_LOCKER_porcelain_tiles' else (-1.66,1.66,-.31,9.2) if target=='FACILITY_floor' else None
        for j in range(6):
            a=j*2.399+R.uniform(-.4,.4);h=[1.40,1.14,1.56,.88,1.28,1.02][j]
            pts=[(0,0,.43),(.06*cos(a),.06*sin(a),.83),(.10*cos(a),.10*sin(a),h+.12)]
            k.tube(name+'_branch',pts,.010 if j else .017,'V_bark')
            for i in range(6+j%3):
                z=.56+(i+R.uniform(.1,.55))*(h-.49)/(6+j%3);theta=a+i*2.3+R.uniform(-.5,.5)
                start=(.07*cos(a),.07*sin(a),z)
                end=Vector(start)+Vector((.08*cos(theta),.08*sin(theta),.04))
                k.rod(name+'_petiole',start,end,.004,'V_stem',10)
                direction=Vector((cos(theta),sin(theta),R.uniform(.23,.72)));length=R.uniform(.28,.45);width=R.uniform(.065,.108)
                tip=Vector(p)+(end+direction.normalized()*length)*size
                if bounds:
                    if tip.x<bounds[0]:direction.x=abs(direction.x)
                    if tip.x>bounds[1]:direction.x=-abs(direction.x)
                    if tip.y<bounds[2]:direction.y=abs(direction.y)
                    if tip.y>bounds[3]:direction.y=-abs(direction.y)
                leaf(name+'_broad_leaf',end,direction,length,width,R.choices([0,1,2,3],[3,5,3,1])[0])
    root=k.group(name,b,p);root.scale=(size,size,size);root['asset_role']='potted_plant'
    floor_contact(root,target);return root

def wall_shelf(name,p,angle,target,width=.72):
    b=k.start();deck=k.box(name+'_deck',(0,-.165,0),(width,.33,.034),'bench_worn_timber',.005)
    for x in [-width*.35,width*.35]:
        k.tube(name+'_bracket',[(x,0,-.22),(x,-.29,-.025),(x,0,-.025)],.012,'V_graphite')
    root=k.group(name,b,p,angle);life.supported(root,target,[(x,0,-.22) for x in [-width*.35,width*.35]],'LOCAL_+Y','WALL')
    return root,deck

def wall_notice(name,p,angle,target,w=.3,h=.40,body='SAFETY\nBUILDS\nTOMORROW',col='V_paper'):
    b=k.start();k.box(name+'_paper',(0,-.001,0),(w,.002,h),col,.001)
    for x in [-w*.43,w*.43]:
        for z in [-h*.43,h*.43]:k.rod(name+'_pin',(x,-.002,z),(x,-.004,z),.004,'steel',10)
    k.label(name+'_type',body,(0,-.0025,h*.28),min(w*.11,.051),'ink',align='CENTER')
    root=k.group(name,b,p,angle);life.supported(root,target,direction='LOCAL_+Y',kind='WALL');return root

def box_supply(name,p,size=(.35,.26,.25),mat='V_cardboard'):
    b=k.start();w,d,h=size
    k.box(name+'_carton',(0,0,h/2),size,mat,.008)
    k.box(name+'_tape',(0,0,h+.0007),(.044,d,.0014),'paper_board',.0005)
    k.label(name+'_stamp','// SUPPLIES',(-w*.4,-d/2-.001,h*.27),min(w*.065,.025),'ink')
    return k.group(name,b,p)

def briefing_dressing():
    plant('V_BRIEF_corner_ficus',(-2.38,5.67,.022),.98,target='BRIEFING_wood_floor')
    # The original sideboard stays in place. Existing mug/clipboard remain useful.
    plant('V_BRIEF_table_pothos',(-6.17,1.30,.798),.48,'trailing','V_terracotta','BRIEFING_sideboard_laminate_top')
    b=k.start();k.box('V_BRIEF_tea_tray',(0,0,.008),(.42,.24,.016),'bench_worn_timber',.007)
    for x in [-.20,.20]:k.box('V_BRIEF_tray_lip',(x,0,.021),(.012,.24,.028),'bench_worn_timber',.004)
    root=k.group('V_BRIEF_refreshment_tray',b,(-5.80,1.34,.798));floor_contact(root,'BRIEFING_sideboard_laminate_top')
    tray=bpy.data.objects['V_BRIEF_tea_tray']
    b=k.start();k.lathe('V_BRIEF_coffee_flask',[(0,0),(.063,0),(.073,.035),(.063,.22),(.050,.25),(.047,.28)],'V_brushed',48)
    k.lathe('V_BRIEF_flask_lid',[(0,.277),(.053,.277),(.053,.305),(0,.305)],'V_graphite',48)
    k.tube('V_BRIEF_flask_handle',[(.05,0,.26),(.105,0,.24),(.11,0,.09),(.070,0,.065)],.012,'V_graphite')
    flask=k.group('V_BRIEF_thermal_coffee',b,(-5.90,1.33,.814));floor_contact(flask,tray)
    for j,loc in enumerate([(-5.67,1.29,.814),(-5.60,1.43,.798)]):
        mug=k.mug('V_BRIEF_mug_%d'%j,loc);floor_contact(mug,tray if j==0 else 'BRIEFING_sideboard_laminate_top')
    # Stacked manuals on the sideboard end, folded jacket hanging from its edge.
    for i in range(3):
        b=k.start();k.box('V_BRIEF_manual_pages',(0,0,.018),(.22,.31,.032),'V_paper',.002)
        for z in [.002,.035]:k.box('V_BRIEF_manual_cover',(0,0,z),(.23,.32,.004),'rug_border' if i%2 else 'canvas_rust',.001)
        k.box('V_BRIEF_manual_spine',(0,-.158,.019),(.23,.014,.037),'rug_border' if i%2 else 'V_graphite',.002)
        k.label('V_BRIEF_manual_title',['OPERATIONS','PEOPLE','A SAFER TOMORROW'][i],(-.102,-.167,.010),.016,'paper')
        root=k.group('V_BRIEF_manual_%d'%i,b,(-5.31,1.39,.798+i*.037),.02*(-1)**i)
    coat=life.jacket('V_BRIEF_draped_jacket',(-5.45,1.647,.84),'cotton_grey');coat.rotation_euler.z=pi
    # Narrow waste basket with real open wire diamonds and crumpled paper.
    b=k.start();k.rod('V_BRIEF_bin_base',(0,0,.008),(0,0,.024),.132,'V_graphite',32)
    for z,r in [(.028,.134),(.35,.167)]:k.tube('V_BRIEF_bin_ring',[(r*cos(t*2*pi/48),r*sin(t*2*pi/48),z) for t in range(48)],.004,'V_graphite',True)
    for i in range(24):
        for sign in [-1,1]:
            pts=[]
            for j in range(10):
                t=j/9;r=.134+t*.033;a=2*pi*i/24+sign*t*.60;pts.append((r*cos(a),r*sin(a),.029+t*.315))
            k.tube('V_BRIEF_bin_mesh',pts,.0013,'V_graphite')
    for i in range(4):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.063,location=(R.uniform(-.07,.07),R.uniform(-.07,.07),.065+i*.036));ob=bpy.context.object;k.finish(ob,'V_BRIEF_crumpled_paper','V_paper');ob.scale=(1,.8,.6)
    root=k.group('V_BRIEF_wastebasket',b,(-6.55,1.23,.022));floor_contact(root,'BRIEFING_wood_floor')
    for name,x,z,w,h,body in [('safety',-3.50,1.99,.31,.41,'SAFETY\nBUILDS\nTOMORROW'),('rota',-3.10,1.62,.25,.33,'SHIFT 04\n\n08:00   16:00\n16:00   00:00'),('map',-2.90,2.08,.45,.34,'FACILITY / 08\n\nCHECK YOUR ROUTE')]:wall_notice('V_BRIEF_'+name,(x,6.1,z),0,'BRIEFING_north',w,h,body)
    # Move the entire refreshment cluster against the focal wall, as in the target.
    from mathutils import Matrix
    old=bpy.data.objects['BRIEFING_sideboard'];bpy.context.view_layer.update();previous=old.matrix_world.copy()
    old.location=(-7.035,1.72,.022);old.rotation_euler.z=pi/2;bpy.context.view_layer.update();delta=old.matrix_world@previous.inverted()
    for ob in list(bpy.data.objects):
        if ob.parent or ob==old:continue
        if ob.name in ['BRIEFING_mug','BRIEFING_notes','LIFE_remote'] or ob.name.startswith(('V_BRIEF_table_','V_BRIEF_refreshment_','V_BRIEF_thermal_','V_BRIEF_mug_','V_BRIEF_manual_','V_BRIEF_draped_')):ob.matrix_world=delta@ob.matrix_world
    b=k.start();k.box('V_BRIEF_discipline_back',(0,-.007,0),(.57,.014,.96),'V_graphite',.003)
    k.box('V_BRIEF_discipline_paper',(0,-.016,0),(.53,.002,.91),'rug_border',.001)
    for side in [-1,1]:k.mesh('V_BRIEF_discipline_emblem',[(side*.19,-.018,.29),(side*.08,-.018,.04),(0,-.018,-.04),(side*.065,-.018,.24)],[(0,1,2,3)],'V_ochre')
    k.label('V_BRIEF_discipline_type','DISCIPLINE\nPEOPLE\nPROCESS',(0,-.019,-.18),.049,'paper',align='CENTER')
    root=k.group('V_BRIEF_discipline_poster',b,(-7.3,1.69,2.08),pi/2);life.supported(root,'BRIEFING_focal_wall',direction='LOCAL_+Y',kind='WALL')
    # Fine native vector route plan and pinned running notes, with separated surfaces.
    maproot=bpy.data.objects['V_BRIEF_map']
    for j in range(6):
        z=.02-j*.022;ob=k.tube('V_BRIEF_plan_line',[(-.16,-.003,z),(-.035,-.003,z),(-.035,-.003,z-.017),(.13,-.003,z-.017)],.0016,'erased_marker');ob.parent=maproot
    for idx,(x,z) in enumerate([(-3.60,1.57),(-3.36,1.51)]):
        note=wall_notice('V_BRIEF_pinned_note_%d'%idx,(x,6.1,z),0,'BRIEFING_north',.16,.20,'HANDOVER\nCHECKED')

def hallway_dressing():
    bpy.data.objects['LIFE_cleaning_bucket'].location=(1.40,.82,0)
    plant('V_HALL_staff_ficus',(1.14,-.05,0),.96)
    plant('V_HALL_staff_snake',(-1.09,-.03,0),.93,'snake')
    shelf,deck=wall_shelf('V_HALL_plant_shelf',(-2.15,2.04,2.52),pi/2,'HALL_briefing_infill',.78)
    plantroot=plant('V_HALL_trailing_plant',(0,-.17,.017),.60,'trailing','V_terracotta',deck);plantroot.parent=shelf
    # Grouped information board in the large blank wall opposite briefing.
    b=k.start();back=k.box('V_HALL_shift_board_back',(0,-.014,0),(1.18,.028,1.22),'V_graphite',.006)
    k.frame('V_HALL_shift_board_trim',(0,-.031,0),1.20,1.24,.029,.026,'bench_worn_timber',.008)
    k.label('V_HALL_shift_board_header','SHIFT UPDATES',(-.52,-.032,.49),.061,'paper')
    root=k.group('V_HALL_shift_board',b,(1.7,5.54,1.82),-pi/2);life.supported(root,'HALL_right_ops',direction='LOCAL_+Y',kind='WALL')
    for i,(x,z,w,h,txt,col) in enumerate([(-.31,.10,.38,.52,'SAME\nTEAM\nA BRIGHTER\nTOMORROW','V_paper'),(.16,.19,.38,.36,'DAILY CHECKS\n\n01  TOOLS\n02  EQUIPMENT\n03  RETURN','paper'),(-.31,-.37,.38,.31,'SHIFT ROTA\n\n04 / 09 / 26','paper'),(.23,-.30,.45,.43,'SAFETY\nBUILDS\nCONFIDENCE','canvas_rust')]):
        o=wall_notice('V_HALL_notice_%d'%i,(x,-.029,z),0,back,w,h,txt,col);o.parent=root
    # Bold original facility poster replaces empty plaster; all native text/geometry.
    b=k.start();k.box('V_HALL_poster_back',(0,-.009,0),(.77,.018,1.25),'V_graphite',.005)
    k.box('V_HALL_poster_paper',(0,-.020,0),(.70,.002,1.18),'V_paper',.001)
    k.label('V_HALL_poster_type','PEOPLE\nKEEP\nOPERATIONS\nMOVING',(-.29,-.024,.43),.096,'ink')
    for j,col in enumerate(['rug_border','cotton_grey','V_ochre']):
        vs=[(-.35,-.022,-.24-j*.08),(-.19,-.022,-.22-j*.07),(-.03,-.022,-.29-j*.06),(.13,-.022,-.18-j*.06),(.35,-.022,-.10-j*.07),(.35,-.022,-.44),(-.35,-.022,-.44)];k.mesh('V_HALL_poster_landscape',vs,[tuple(range(7))],col)
    k.label('V_HALL_poster_footer','CRITICAL SHIFT',(-.27,-.023,-.53),.038,'ink')
    root=k.group('V_HALL_culture_poster',b,(1.7,7.60,1.93),-pi/2);root.scale=(1.17,1,1.12);life.supported(root,'HALL_right_ops',direction='LOCAL_+Y',kind='WALL')
    firstaid();trolley()

def firstaid():
    b=k.start();k.box('V_AID_wall_mount',(0,-.015,0),(.40,.03,.58),'V_graphite',.009)
    k.panel('V_AID_cabinet',(0,-.080,0),.49,.65,.14,.022,'aged_socket')
    k.frame('V_AID_door_seam',(0,-.152,0),.442,.598,.006,.003,'V_brushed',.015)
    k.box('V_AID_cross_field',(0,-.154,.12),(.15,.002,.16),'rug_border',.003)
    k.box('V_AID_cross_h',(0,-.156,.12),(.104,.002,.030),'paper',.001)
    k.box('V_AID_cross_v',(0,-.156,.12),(.030,.002,.104),'paper',.001)
    k.label('V_AID_title','FIRST AID',(0,-.156,-.047),.048,'ink',align='CENTER')
    k.label('V_AID_subtitle','FOR A SAFER\nTOMORROW',(0,-.156,-.11),.030,'ink',align='CENTER')
    root=k.group('V_HALL_first_aid',b,(-1.7,6.36,1.83),pi/2);life.supported(root,'HALL_left_ops',direction='LOCAL_+Y',kind='WALL')
    b=k.start();k.box('V_EXT_bracket',(0,-.025,.15),(.15,.05,.31),'V_graphite',.006)
    k.lathe('V_EXT_cylinder',[(0,-.28),(.09,-.28),(.118,-.25),(.122,-.20),(.122,.23),(.106,.27),(.045,.30)],'V_rustred',48).location.y=-.14
    k.rod('V_EXT_valve',(0,-.14,.29),(0,-.14,.34),.024,'V_brushed')
    k.box('V_EXT_handle',(.025,-.14,.355),(.17,.035,.023),'V_graphite',.007)
    k.tube('V_EXT_hose',[(.03,-.14,.31),(.16,-.14,.34),(.19,-.14,.21),(.15,-.14,-.22)],.013,'rubber')
    k.box('V_EXT_label',(0,-.263,.02),(.13,.002,.27),'V_paper',.001)
    k.label('V_EXT_instruction','PULL\nAIM\nSQUEEZE\nSWEEP',(-.05,-.265,.12),.023,'ink')
    root=k.group('V_HALL_extinguisher',b,(-1.692,6.34,.85),pi/2);life.supported(root,'HALL_left_ops_washable_dado',[(0,0,.15)],'LOCAL_+Y','WALL')
    wall_notice('V_EXT_location',(-1.7,6.34,1.35),pi/2,'HALL_left_ops',.16,.19,'FIRE','V_rustred')

def trolley():
    b=k.start()
    for z in [.15,.60,1.02]:
        k.box('V_CART_shelf',(0,0,z),(.57,.79,.024),'V_graphite',.008)
        for x in [-.278,.278]:k.box('V_CART_tray_lip',(x,0,z+.029),(.016,.79,.07),'V_brushed',.004)
    for x in [-.25,.25]:
        for y in [-.34,.34]:
            k.rod('V_CART_upright',(x,y,.13),(x,y,1.03),.020,'V_graphite')
            k.rod('V_CART_caster',(x-.026,y,.061),(x+.026,y,.061),.061,'rubber',24)
            k.box('V_CART_fork',(x,y,.112),(.018,.045,.06),'V_brushed',.004)
    for x in [-.25,.25]:k.tube('V_CART_handle',[(x,-.34,.96),(x,-.36,1.13),(x,.36,1.13),(x,.34,.96)],.018,'V_graphite')
    root=k.group('V_HALL_supply_trolley',b,(1.31,5.79,0));floor_contact(root,anchors=[(x,y,0) for x in [-.25,.25] for y in [-.34,.34]])
    for name,p,size in [('lower',(0,0,.162),(.44,.58,.31)),('upper',(0,.07,.612),(.44,.48,.32))]:
        ob=box_supply('V_CART_'+name,p,size);ob.parent=root
    for j in range(3):
        fold=life.fold('V_CART_towel_%d'%j,(0,.13,1.032+j*.048),'cotton_cream',.39,.29,.048,.02*j);fold.parent=root
    b2=k.start();k.lathe('V_CART_cleaner_bottle',[(0,0),(.038,0),(.041,.03),(.038,.20),(.018,.24),(.018,.28)],'aged_socket',32)
    k.box('V_CART_spray_trigger',(.02,0,.287),(.075,.03,.029),'V_graphite',.005)
    spr=k.group('V_CART_spray',b2,(-.10,-.25,1.032));spr.parent=root

def locker_dressing():
    plant('V_LOCKER_corner_ficus',(6.10,6.70,.006),1.04,target='V_LOCKER_porcelain_tiles')
    plant('V_LOCKER_corner_snake',(6.0,1.27,.006),.82,'snake','V_terracotta','V_LOCKER_porcelain_tiles')
    shelf,deck=wall_shelf('V_LOCKER_green_shelf',(1.86,5.85,2.48),pi/2,'HALL_right_ops',.93)
    p=plant('V_LOCKER_shelf_pothos',(-.20,-.17,.017),.53,'trailing','V_ochre',deck);p.parent=shelf
    for i in range(2):
        fold=life.fold('V_LOCKER_shelf_towels_%d'%i,(.22,-.16,.017+i*.05),'cotton_cream',.30,.24,.05);fold.parent=shelf
    b=k.start();k.box('V_LOCKER_dispenser_back',(0,-.014,0),(.16,.028,.28),'V_graphite',.01)
    k.panel('V_LOCKER_soap_body',(0,-.058,0),.18,.29,.09,.033,'aged_socket')
    k.panel('V_LOCKER_soap_level',(0,-.105,0),.04,.14,.003,.012,'V_graphite')
    k.box('V_LOCKER_pump',(0,-.095,-.171),(.058,.11,.03),'V_brushed',.008)
    root=k.group('V_LOCKER_wall_dispenser',b,(1.86,5.05,1.32),pi/2);life.supported(root,'HALL_right_ops',direction='LOCAL_+Y',kind='WALL')
    # Bag on the changing bench has an actual supported floor/seat contact.
    duffel()
    for j in range(2):
        o=life.fold('V_LOCKER_bench_towel_%d'%j,(3.6,2.85,.456+j*.044),'cotton_cream',.41,.30,.044,.025*j)
        floor_contact(o,'LOCKER_changing_bench_01_laminate_slat.001' if j==0 else 'V_LOCKER_bench_towel_0_soft_body') if j==0 else None
    locker_utility_cluster()

def duffel():
    b=k.start();mat='canvas_olive'
    body=k.garment_loft('V_DUFFEL_canvas',[(0,0,0,.21,.12),(.005,0,.025,.29,.17),(0,.008,.10,.32,.18),(-.012,0,.23,.30,.16),(0,0,.32,.25,.12),(0,0,.35,.19,.022)],mat,64)
    for v in body.data.vertices:
        x,y,z=v.co;v.co.y+=(.004*sin(x*70+z*18)+.003*sin(z*58-x*28))*sin(pi*z/.35)
    for y in [-.14,.14]:
        for x in [-.15,.15]:
            k.tube('V_DUFFEL_webbing',[(x,y*.5,.012),(x,y*1.24,.12),(x,y,.27),(x,y*.7,.33)],.012,'rug_border')
        k.tube('V_DUFFEL_carry_handle',[(-.15,y*.7,.32),(-.12,y*.7,.415),(-.07,y*.7,.44),(.08,y*.7,.438),(.12,y*.7,.414),(.15,y*.7,.32)],.009,'rug_border')
    k.tube('V_DUFFEL_zipper',[(-.24,0,.332),(-.12,0,.35),(.12,0,.35),(.24,0,.332)],.003,'V_brushed')
    k.panel('V_DUFFEL_side_pocket',(0,-.178,.15),.31,.17,.013,.026,mat)
    k.label('V_DUFFEL_owner','SHIFT 04',(-.09,-.187,.145),.024,'paper')
    root=k.group('V_LOCKER_floor_duffel',b,(3.80,2.51,.006),.10);floor_contact(root,'V_LOCKER_porcelain_tiles')

def locker_utility_cluster():
    b=k.start();back=k.box('V_PEG_back',(0,-.012,0),(.88,.024,.64),'V_graphite',.007)
    panel=k.box('V_PEG_board',(0,-.031,0),(.85,.014,.61),'V_cardboard',.004)
    for i in range(14):
        for j in range(9):k.rod('V_PEG_hole',(-.39+i*.06,-.038,-.24+j*.06),(-.39+i*.06,-.039,-.24+j*.06),.006,'darksteel',10)
    for x in [-.30,-.12,.10,.29]:k.tube('V_PEG_hook',[(x,-.038,.16),(x,-.105,.16),(x,-.12,.18)],.005,'V_brushed')
    for x in [-.20,.10]:
        k.tube('V_PEG_lanyard',[(x-.04,-.056,.14),(x-.08,-.06,-.13),(x,-.06,-.22),(x+.08,-.06,-.13),(x+.04,-.056,.14)],.009,'rubbed_leather')
    k.rod('V_PEG_brush_handle',(.29,-.06,.14),(.29,-.06,-.12),.014,'wood')
    k.box('V_PEG_brush_head',(.29,-.066,-.17),(.083,.045,.09),'cotton_grey',.005)
    root=k.group('V_LOCKER_pegboard',b,(7.17,7.3,1.75));life.supported(root,'LOCKER_north',direction='LOCAL_+Y',kind='WALL')
    shelf,deck=wall_shelf('V_LOCKER_peg_shelf',(7.17,7.3,2.12),0,'LOCKER_north',.98)
    p=plant('V_LOCKER_peg_plant',(-.26,-.17,.017),.48,'trailing','V_terracotta',deck);p.parent=shelf
    for i in range(2):
        o=box_supply('V_LOCKER_supply_box_%d'%i,(.18,-.14,.017+i*.10),(.24,.23,.10));o.parent=shelf
    b=k.start()
    for x in [-.28,.28]:
        for y in [-.20,.20]:
            k.rod('V_LAUNDRY_frame',(x,y,.10),(x,y,.79),.013,'V_brushed')
            k.rod('V_LAUNDRY_wheel',(x-.017,y,.046),(x+.017,y,.046),.046,'rubber',20)
    for y in [-.20,.20]:k.tube('V_LAUNDRY_top_rail',[(-.28,y,.78),(-.28,y,.82),(.28,y,.82),(.28,y,.78)],.015,'V_brushed')
    # Four soft canvas panels hang within the frame, with broad sag and seam lines.
    for side in [-1,1]:
        vs=[]
        for j in range(12):
            for i in range(17):
                x=-.25+i*.50/16;z=.17+j*.56/11;y=side*(.184+.018*sin(pi*i/16)*sin(pi*j/11));vs.append((x,y,z))
        o=k.mesh('V_LAUNDRY_canvas',vs,[(j*17+i,j*17+i+1,(j+1)*17+i+1,(j+1)*17+i) for j in range(11) for i in range(16)],'cotton_cream',True)
        sol=o.modifiers.new('Canvas thickness','SOLIDIFY');sol.thickness=.003
    for x in [-.25,.25]:k.box('V_LAUNDRY_end',(x,0,.45),(.008,.36,.56),'cotton_cream',.009)
    root=k.group('V_LOCKER_laundry_cart',b,(7.12,6.92,.006));floor_contact(root,'V_LOCKER_porcelain_tiles',[(x,y,0) for x in [-.28,.28] for y in [-.20,.20]])
    towel=life.hanging_towel('V_LOCKER_cart_towel',(0,-.212,.79),'cotton_blue',width=.28,length=.44);towel.parent=root

def lighting():
    energies={'HALL_light_00':125,'HALL_light_01':115,'HALL_light_02':140,'BRIEFING_light_00':205,'BRIEFING_light_01':160,'LOCKER_light_00':225,'LOCKER_light_01':205,'LOCKER_light_02':100}
    for ob in bpy.data.objects:
        if ob.type!='LIGHT':continue
        for pref,en in energies.items():
            if ob.name.startswith(pref):ob.data.energy=en*.66;ob.data.color=(1,.70,.43)
        if ob.name.startswith('EEVEE_floor_bounce'):
            ob.data.energy={'BRIEFING':43,'HALL':35,'LOCKER':75,'SERVICE':15}[ob.name.split('_')[-1]];ob.data.color=(.70,.77,.86)
        ob.data.shadow_filter_radius=2.5;ob.data.shadow_maximum_resolution=.006;ob.data.use_shadow_jitter=True
    for matname in ['lamp']:
        p=k.M[matname].node_tree.nodes['Principled BSDF'];p.inputs['Emission Color'].default_value=(1,.79,.51,1)
    # Spill from existing practical positions, aimed across plaster, gives readable light pools.
    for name,eye,target,power,size in [
        ('BRIEF_wall',(-5.9,3.60,3.15),(-5.3,6.1,1.6),55,1.7),
        ('BRIEF_ceiling',(-4.6,3.5,1.1),(-4.6,3.5,3.4),30,3.8),
        ('HALL_staff',(0,1.45,3.17),(0,-.50,1.8),60,1.2),
        ('HALL_info',(0,4.65,3.15),(1.7,5.3,1.5),35,1.4),
        ('LOCKER_bays',(2.7,4,3.54),(3.3,7.0,1.1),50,1.8),
        ('LOCKER_front_fill',(5.4,3.0,2.3),(4.0,1.0,1.2),25,2.5),
        ('LOCKER_pod_fill',(5.1,4.0,2.1),(6.82,4.0,.90),18,1.8)]:
        d=bpy.data.lights.new('V_LIGHT_'+name,'AREA');d.energy=power*.75;d.shape='DISK';d.size=size;d.color=(1,.70,.43)
        ob=bpy.data.objects.new('V_LIGHT_'+name,d);bpy.context.collection.objects.link(ob);ob.location=eye;ob.rotation_euler=(Vector(target)-Vector(eye)).to_track_quat('-Z','Y').to_euler()
        d.shadow_filter_radius=2.5;d.shadow_maximum_resolution=.006;d.use_shadow_jitter=True

def cameras():
    # Same standing corners as the source captures. Aspect matches generated concept frames.
    for name,eye,target,lens in [('HALL',(1.0,8.95,1.60),(0,1.3,1.42),22),('BRIEFING',(-2.75,1.10,1.55),(-5.25,4.4,1.3),22),('LOCKER',(7.8,1.02,1.60),(3.65,4.6,1.3),21)]:
        cam=room.cam('REFERENCE_'+name,eye,target,lens);cam.data.sensor_width=56 if name=='HALL' else 58

def finishing_pass():
    """Corrections from the third rendered comparison, also runnable on its saved file."""
    from mathutils import Quaternion
    assert not bpy.context.scene.get('valorant_finishing_pass'), 'Finishing pass already applied'
    k.M={m.name:m for m in bpy.data.materials};k.STAGE=3
    # Present broad leaf surfaces instead of a ladder of edge-on planes.
    for ob in list(bpy.data.objects):
        if ob.type!='MESH' or '_broad_leaf' not in ob.name or '_midrib' in ob.name:continue
        rng=random.Random(wear.seed(ob.name));base=ob.data.vertices[0].co.copy();tip=ob.data.vertices[-1].co.copy();axis=(tip-base).normalized()
        raised=Vector((axis.x,axis.y,axis.z+.65)).normalized()
        tilt=axis.rotation_difference(raised);roll=Quaternion(raised,rng.uniform(.60,1.20));q=roll@tilt
        for v in ob.data.vertices:v.co=base+q@(v.co-base)
        stem,suffix=(ob.name.rsplit('.',1) if ob.name.rsplit('.',1)[-1].isdigit() else (ob.name,None))
        rib=bpy.data.objects.get(stem+'_midrib'+('.'+suffix if suffix else ''))
        if rib:
            for sp in rib.data.splines:
                for pt in sp.points:pt.co=(*tuple(base+q@(Vector(pt.co[:3])-base)),1)
        ob.data.update()
    poster=bpy.data.objects['V_HALL_culture_poster'];poster.location.z=1.74;poster.scale.z=1
    # A compact bold headline remains readable at the corridor's oblique angle.
    headline=bpy.data.objects['V_HALL_poster_type'];headline.data.offset=.0017;headline.scale.x=.83
    bpy.data.objects['V_HALL_shift_board_header'].data.offset=.0006
    # The reference's credenza is painted steel under a worn timber worktop.
    for ob in bpy.data.objects['BRIEFING_sideboard'].children_recursive:
        if ob.type=='MESH' and ('_door' in ob.name or '_carcass' in ob.name):
            for slot in ob.material_slots:slot.material=k.M['V_locker_steel']
            wear.paint_chips(k,ob)
    for name in ['V_HALL_first_aid','V_HALL_extinguisher','V_EXT_location']:bpy.data.objects[name].location.y=6.65
    text=bpy.data.objects['V_EXT_location_type'];text.data.materials.clear();text.data.materials.append(k.M['paper'])
    for root in bpy.data.objects:
        if root.type!='EMPTY' or 'bench' not in root.name or root.get('cs_support_anchor'):continue
        for ob in root.children_recursive:
            if ob.type=='MESH' and '_laminate_slat' not in ob.name:
                for slot in ob.material_slots:
                    if slot.material and slot.material.name in ['steel','pale','paint','pressure_metal','V_utility_pale','V_utility_paint']:slot.material=k.M['V_graphite']
    for name,power,color in [('BRIEFING',45,(.92,.84,.73)),('HALL',42,(.84,.85,.81)),('LOCKER',84,(.84,.86,.85))]:
        lamp=bpy.data.objects['EEVEE_floor_bounce_'+name].data;lamp.energy=power;lamp.color=color
    # Low, sparse paint wear exposes the previous coat without making the building abandoned.
    for name,amount in [('dado',.48),('wall',.18)]:
        m=k.M[name];n=m.node_tree.nodes;l=m.node_tree.links;p=n['Principled BSDF']
        coord=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(coord.outputs['Position'],sep.inputs[0])
        grain=wear.noise(n,l,coord.outputs['Position'],19,3)
        patches=wear.noise(n,l,coord.outputs['Position'],3.4,2)
        combined=wear.mathnode(n,l,'ADD',wear.mathnode(n,l,'MULTIPLY',grain,.38),wear.mathnode(n,l,'MULTIPLY',patches,.62))
        mask=n.new('ShaderNodeMapRange');mask.inputs['From Min'].default_value=.586;mask.inputs['From Max'].default_value=.64;l.new(combined,mask.inputs[0])
        low=n.new('ShaderNodeMapRange');low.inputs['From Min'].default_value=.24;low.inputs['From Max'].default_value=1.12;low.inputs['To Min'].default_value=1;low.inputs['To Max'].default_value=.10;l.new(sep.outputs['Z'],low.inputs[0])
        strength=wear.mathnode(n,l,'MULTIPLY',wear.mathnode(n,l,'MULTIPLY',mask.outputs[0],low.outputs[0]),amount)
        tint=n.new('ShaderNodeMixRGB');tint.blend_type='MIX';l.new(strength,tint.inputs[0]);l.new(p.inputs['Base Color'].links[0].from_socket,tint.inputs[1]);tint.inputs[2].default_value=(.32,.30,.245,1);l.new(tint.outputs[0],p.inputs['Base Color'])
        m['reference_finish']='Sparse lower-wall rubs, retained packed plaster and rough paint texture'
    # Slightly faded timber retains its roughness and grain, with no varnish coat.
    for i in range(5):
        m=k.M['floor_timber_%d'%i];n=m.node_tree.nodes;l=m.node_tree.links;p=n['Principled BSDF']
        tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(1.16,1.20,1.25,1)
        l.new(p.inputs['Base Color'].links[0].from_socket,tint.inputs[1]);l.new(tint.outputs[0],p.inputs['Base Color'])
    # Two abutting crown sections create the target's strong upper wall silhouette.
    o=k.box('V_BRIEF_crown_focal',(-7.275,3.55,3.295),(.05,5.10,.13),'V_graphite',.003)
    life.supported(o,'BRIEFING_focal_wall',[(-.025,0,0)],'WORLD_-X','WALL')
    o=k.box('V_BRIEF_crown_north',(-4.565,6.075,3.295),(5.37,.05,.13),'V_graphite',.003)
    life.supported(o,'BRIEFING_north',[(0,.025,0)],'WORLD_+Y','WALL')
    # Number plates make the four identical bodies recognizable across views.
    for i in range(1,5):
        for suffix,body in [('L','%02d'%i),('R','SHIFT 04')]:
            door=bpy.data.objects['BELONG_%02d_door_%s'%(i,suffix)];side=-1 if suffix=='L' else 1
            label=k.label('V_LOCKER_identity_%02d_%s'%(i,suffix),body,(-side*.25,-.0225,1.687),.029 if suffix=='L' else .014,'ink',align='CENTER');label.parent=door
    # Local wear on the actual touch faces, plus inventory labels on the trolley.
    for ob in list(bpy.data.objects):
        if ob.type=='MESH' and len(ob.data.vertices)==8 and ob.name.startswith(('V_CART_shelf','V_CART_tray_lip','V_CART_upper_carton','V_REAR_solid_leaf')):wear.paint_chips(k,ob)
    lower=bpy.data.objects['V_CART_lower_carton'];lower.data.materials.clear();lower.data.materials.append(k.M['V_graphite'])
    for name in ['V_CART_lower','V_CART_upper']:
        root=bpy.data.objects[name];d=.58 if name.endswith('lower') else .48;h=.31 if name.endswith('lower') else .32
        before=k.start();k.box(name+'_inventory',(0,-d/2-.002,h*.55),(.16,.003,.10),'V_paper',.001)
        k.label(name+'_inventory_type','FILTER KITS' if name.endswith('lower') else 'CLEAN STOCK',(-.071,-d/2-.004,.55*h+.018),.016,'ink')
        for j in range(3):k.box(name+'_inventory_rule',(-.016,-d/2-.004,.55*h-.003-j*.01),(.105,.001,.0015),'ink',0)
        for ob in set(bpy.data.objects)-before:ob.parent=root
    bpy.context.scene['valorant_finishing_pass']=4

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--review',default='pass-01');ap.add_argument('--validate-only',action='store_true');ap.add_argument('--finish-only',action='store_true');ap.add_argument('--detail-only',action='store_true');ap.add_argument('--no-bake',action='store_true');ap.add_argument('--cameras',default='REFERENCE_HALL,REFERENCE_BRIEFING,REFERENCE_LOCKER');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    out=EVIDENCE/a.review;out.mkdir(parents=True,exist_ok=True);t=time.time();source=bpy.data.filepath;s=bpy.context.scene
    if not a.validate_only:
        if not a.finish_only and not a.detail_only:materials();lockers();bathroom_floor();modern_door();briefing_dressing();hallway_dressing();locker_dressing();lighting();cameras()
        if not a.detail_only:finishing_pass()
        import valorant_detail
        valorant_detail.run();rev.startup()
        s['user_revision']='Valorant browser reference iteration: matte timber, small porcelain tiles, matching metal lockers, modern staff door, plants and grouped workplace props.'
        s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100
        dest=HERE/'spawnroom_valorant_walk.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
        if not a.no_bake:
            print('BAKING_REFERENCE_LIGHTING',flush=True);bpy.ops.object.lightprobe_cache_bake(subset='ALL')
            bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
    else:dest=Path(source)
    report=life.validate(out)
    s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100
    for name in a.cameras.split(','):
        if not name:continue
        s.camera=bpy.data.objects[name];s.render.filepath=str(out/(name+'.png'));print('RENDER',name,flush=True);bpy.ops.render.render(write_still=True)
    (out/'provenance.json').write_text(json.dumps({'source':source,'output':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'engine':s.render.engine,'elapsed_seconds':time.time()-t},indent=2))
    print('VALORANT_PASS_COMPLETE',report['status'],flush=True)

if __name__=='__main__':main()
