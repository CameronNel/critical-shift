"""Additive cafeteria overhaul. Open the original front-end .blend before running.

Imports independently authored .blend collections; preserves hall, yard and interfaces.
Never saves over the input. Source room, combined map and runtime ownership stay separate.
"""
import sys,os,hashlib,random
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from kit import *
from support_coverage import complete_contacts

CAF=bpy.data.collections.get('CAFETERIA')
assert CAF,'Open front_end_area.blend before this script'
ROOT=HERE.parent
IMPORTED=[];SUPPORTS=[]
def local(x,y,z=0):return (x-8,y+80,z)
def remove(name):
    ob=bpy.data.objects.get(name)
    if ob:bpy.data.objects.remove(ob,do_unlink=True)
def root_at(name,c,x,y,z=0,rz=0):
    o=empty(name,c,local(x,y,z));o.rotation_euler.z=rz;return o
def supported(ob,target,anchors,direction=(0,0,-1)):
    ob['support_target']=target;ob['support_direction']=direction;ob['support_max_gap_m']=.005;ob['support_max_penetration_m']=.002
    SUPPORTS.append({'object':ob.name,'target':target,'anchors':[list(a) for a in anchors],'direction':list(direction)})

def reimport(kind,label,x,y,z=0,rz=0):
    file=HERE/'assets'/(kind+'.blend'); expected=json.loads((HERE/'assets'/(kind+'.json')).read_text())
    with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=['ASSET_'+kind.upper()]
    c=dst.collections[0];CAF.children.link(c);c.name='GAME_'+label
    root=next(o for o in c.objects if o.get('asset_kind')==kind)
    bpy.context.view_layer.update();bb=bounds(c.all_objects);tris=triangles(c.all_objects)
    assert len(c.all_objects)==expected['components'],(kind,'component loss')
    assert tris==expected['triangles'],(kind,'geometry loss')
    error=max(abs(bb[i][j]-expected['bounds_m'][i][j]) for i in range(2) for j in range(3))
    assert error<.00001,(kind,'bounds changed',error)
    for o in c.all_objects:o.name=label+'__'+o.name
    root.name=label;root.location=local(x,y,z);root.rotation_euler.z=rz
    root['reimported_from']='//cafeteria-revamp/assets/'+kind+'.blend'
    anchors=[tuple(o.location) for o in c.all_objects if 'CONTACT_' in o.name]
    supported(root,'cafhall_mid_seg0_core' if kind=='dartboard' else 'game_rug',anchors,(0,1,0) if kind=='dartboard' else (0,0,-1))
    IMPORTED.append({'instance':label,'kind':kind,'source':str(file.relative_to(ROOT)),'triangles':tris,'component_count':len(c.all_objects),'bounds_error_m':error})
    return root,c

def games(c):
    for n in ('rec_foosball','rec_basketball','rec_dartboard','rec_oche','game_beanbag_0','game_beanbag_1'):remove(n)
    reimport('foosball','FOOSBALL_A',-3.65,-64.2,.016)
    reimport('foosball','FOOSBALL_B',-3.65,-61.85,.016)
    reimport('basketball','BASKETBALL_A',-6.27,-65.15,.016,math.pi/2)
    reimport('basketball','BASKETBALL_B',-6.27,-63.66,.016,math.pi/2)
    dr,dc=reimport('dartboard','DARTBOARD',-1.13,-60.152,1.73)
    # The oche is exactly 2.37 m from the scoring face, with floor attachment at rug level.
    m=mb();m.rbox(-9.13,17.345,.018,1.06,.034,.004,.001,mi=MI['ivory']);o=finish(m,'rec_oche_regulation_2p37m',c)
    o['support']='rug';o['throw_distance_m']=2.37
    for n,p in [('game_stool_0',(-1.32,-65.6)),('game_stool_1',(-.66,-66.0)),('game_side_table',(-.46,-64.48))]:
      ob=bpy.data.objects.get(n)
      if ob:ob.location=local(*p,.016);ob['support']='rug'
    # Replace only the carpet's albedo; keep its measured thickness, bounds and UVs.
    rug=bpy.data.objects['game_rug'];temp=panel('TEMP_CARPET',(0,0,0),1,1,'game_carpet.png',c)
    rug.data=rug.data.copy();rug.data.materials[0]=temp.data.materials[0];remove('TEMP_CARPET')
    # Cabinet lights and a curved dartboard task lamp, rather than room-filling neon.
    m=mb();p=Vector(local(-1.13,-60.15,2.305))
    m.rbox(p.x,p.y-.0115,p.z,.28,.023,.041,.005,mi=MI['navy'])
    m.between(p+Vector((-.10,-.02,0)),p+Vector((-.10,-.13,.07)),.008,seg=10,mi=MI['steel'])
    m.between(p+Vector((.10,-.02,0)),p+Vector((.10,-.13,.07)),.008,seg=10,mi=MI['steel'])
    m.rbox(p.x,p.y-.15,p.z+.067,.37,.11,.048,.015,mi=MI['black'])
    m.rbox(p.x,p.y-.16,p.z+.042,.30,.058,.007,.002,mi=MI['lamp'])
    lamp=finish(m,'Game_dartboard_task_lamp',c);supported(lamp,'cafhall_mid_seg0_core',[tuple(p)],(0,1,0))
    area('R8_Dart_task',p+Vector((0,-.17,.025)),local(-1.13,-60.32,1.73),16,.22,(1,.86,.64),c)
    for label,x,y in [('A',-6.27,-65.15),('B',-6.27,-63.66)]:
      area('R8_Arcade_marquee_'+label,local(x-.8,y,2.48),local(x+.3,y,1.3),5,.38,(1,.47,.19),c)

def soft_seat(c,name,seats,pos,rz,col):
    remove(name);root=root_at(name,c,*pos,.016,rz);m=mb();w=seats*.71+.39
    m.rbox(0,0,.235,w-.1,.86,.205,.045,mi=MI[col])
    # Individually padded rear panels change the silhouette as well as the seams.
    # The structural rail joins them below; exposed upholstery has a soft belly.
    for i in range(seats):
      x=(i-(seats-1)/2)*.71;rear=p_cushion(.705,.163,.636,.052,2)
      for v in rear.verts:
        if v.co.y<0:
          v.co.y-=.025*max(0,math.cos(v.co.x/.3525*math.pi/2))*max(0,math.sin((v.co.z/.636+.5)*math.pi))
      m.add(rear,loc=(x,-.392,.612),mi=MI[col])
    m.rbox(0,-.362,.331,w-.13,.119,.07,.012,mi=MI['walnut'])
    m.rbox(0,.448,.235,w-.12,.038,.16,.009,mi=MI['walnut'])
    for s in (-1,1):
      m.cushion(s*(w/2-.089),0,.44,.18,.90,.395,r=.055,levels=2,mi=MI[col])
      for t in (-1,1):
        m.between((s*(w/2-.18),t*.30,.15),(s*(w/2-.13),t*.34,.015),.025,seg=12,r2=.017,mi=MI['walnut'])
        m.cylz(s*(w/2-.13),t*.34,0,.015,.023,seg=12,mi=MI['rubber'])
    finish(m,name+'_frame_arms_legs',c,root)
    for i in range(seats):
      x=(i-(seats-1)/2)*.71;pts=[]
      for cx,cz,start in [(.294,.260,0),(-.294,.260,90),(-.294,-.260,180),(.294,-.260,270)]:
        for k in range(7):
          a=math.radians(start+k*15);xx=cx+.033*math.cos(a);zz=cz+.033*math.sin(a)
          yy=-.476-.025*max(0,math.cos(xx/.3525*math.pi/2))*max(0,math.cos(zz/.318*math.pi/2))
          pts.append((x+xx,yy,.612+zz))
      curve(name+'_rear_panel_welt_'+str(i),pts,.0018,'stitch',c,root,True,res=1)
    for i in range(seats):
      x=(i-(seats-1)/2)*.71;m=mb()
      pb=p_cushion(.696,.677,.155,.055,2)
      for v in pb.verts:
        if v.co.z>0:v.co.z-=.017*math.exp(-((v.co.x/.25)**2+(v.co.y/.23)**2))*min(1,v.co.z/.04)
      m.add(pb,loc=(x,.052,.405),mi=MI[col])
      m.cushion(x,-.277,.686,.687,.187,.504,r=.07,levels=2,rot=(-.16,0,0),mi=MI[col])
      finish(m,f'{name}_cushion_{i}',c,root)
      # Tailored piping: rounded corners follow cushion edges at a believable scale.
      pts=[]
      for cx,cy,start in [(.298,.275,0),(-.298,.275,90),(-.298,-.275,180),(.298,-.275,270)]:
        for k in range(7):
          a=math.radians(start+k*15);pts.append((x+cx+.032*math.cos(a),.052+cy+.032*math.sin(a),.419))
      curve(f'{name}_seat_welt_{i}',pts,.0018,'stitch',c,root,True,res=1)
      pts=[(x-.278,-.386,.49),(x+.278,-.386,.49),(x+.29,-.347,.895),(x-.29,-.347,.895)]
      curve(f'{name}_back_seam_{i}',pts,.0018,'stitch',c,root,True,res=1)
    supported(root,'lounge_rug',[(s*(w/2-.13),t*.34,0) for s in (-1,1) for t in (-1,1)])
    return root

def lounge(c):
    main=soft_seat(c,'lounge_sofa_main',3,(-4.2,-75.3),math.pi,'fabric_rust')
    soft_seat(c,'lounge_sofa_side',2,(-6.95,-77.5),-math.pi/2,'fabric_rust')
    club_chair(c,'lounge_armchair_0',(-1.7,-77.9),math.pi/2+.3)
    club_chair(c,'lounge_armchair_1',(-1.7,-75.4),math.pi/2-.2)
    MI['fabric_ochre']=len(MATS);MATS.append(material('fabric_ochre',(.54,.32,.09),.96,texture='fabric',bump=.18))
    for i,(parent,x,y) in enumerate([(main,.79,.10),(main,-.79,.13),(bpy.data.objects['lounge_sofa_side'],.38,.10)]):
      remove('lounge_cushion_'+str(i));m=mb();p=p_cushion(.401,.17,.411,.071,2)
      for v in p.verts:
        v.co.y+=math.copysign(.022*max(0,math.cos(v.co.x/.201*math.pi/2))*max(0,math.cos(v.co.z/.206*math.pi/2)),v.co.y)
      m.add(p,loc=(x,y,.692),rot=(-.09,0,.035*(i-1)),mi=MI['fabric_ochre'])
      finish(m,'Lounge_soft_scatter_pillow_'+str(i),c,parent)
      pts=[]
      for cx,cz,start in [(.137,.141,0),(-.137,.141,90),(-.137,-.141,180),(.137,-.141,270)]:
        for k in range(7):
          a=math.radians(start+k*15);pts.append((x+cx+.048*math.cos(a),y+.082,.692+cz+.048*math.sin(a)))
      curve('Pillow_tailored_welt_'+str(i),pts,.0017,'stitch',c,parent,True,res=1)
    # A folded throw drapes over one arm. Topology follows the contact, edge and drop.
    me=bpy.data.meshes.new('Lounge_throw');vs=[];faces=[]
    for j in range(15):
      t=j/14
      for i in range(17):
        u=i/16;x=1.005+u*.30;y=-.18+t*.36
        z=.479 if u<.2 else .479+(u-.2)/.35*.16 if u<.55 else .639-.078*math.sin((u-.55)/.30*math.pi/2)**2 if u<.85 else .561-(u-.85)*1.85
        z+=.004*math.sin(t*math.pi*7+u*1.8);vs.append((x,y,z))
    for j in range(14):
      for i in range(16):a=j*17+i;faces.append((a,a+1,a+18,a+17))
    me.from_pydata(vs,[],faces);me.materials.append(MATS[MI['stitch']]);o=bpy.data.objects.new('Lounge_draped_throw',me);c.objects.link(o);o.parent=main
    for f in me.polygons:f.use_smooth=True
    so=o.modifiers.new('Woven thickness','SOLIDIFY');so.thickness=.003;su=o.modifiers.new('Soft textile','SUBSURF');su.levels=1
    o['support']='soft'
    # A lower, properly proportioned wall-mounted display with content and a soundbar.
    remove('lounge_tv')
    for o in list(CAF.objects):
      if o.name.startswith('tv_slat_'):remove(o.name)
    remove('caf_S_poster_l_12_0');remove('caf_S_poster_l_11_1')
    r=root_at('LOUNGE_MEDIA_WALL',c,-4.2,-79.83,0);m=mb()
    m.rbox(0,.015,1.62,5.15,.022,3.24,.002,mi=MI['black'])
    for k in range(69):
      x=-2.5+k*.073;m.rbox(x,.055,1.62,.044,.059,3.24,.004,mi=MI['walnut' if k%5 else 'oak'])
    m.rbox(0,.172,1.922,1.96,.065,1.134,.016,mi=MI['black'])
    m.rbox(0,.218,1.922,1.88,.018,1.057,.004,mi=MI['black'])
    m.rbox(0,.196,1.277,1.12,.10,.085,.025,mi=MI['navy'])
    for k in range(11):m.rbox(-.50+k*.1,.252,1.277,.056,.003,.045,.008,mi=MI['black'])
    m.rbox(.84,.23,1.402,.019,.006,.006,.002,mi=MI['redled'])
    finish(m,'Media_wall_slats_display_bezel_soundbar',c,r)
    panel('TV_local_broadcast',(0,.231,1.922),1.869,1.05,'lounge_tv.png',c,rot=(0,0,math.pi),parent=r,lit=.65)
    supported(r,'caf_S_seg0_skin',[(0,.004,1.922)],(0,-1,0))
    area('R8_Media_wall_wash',local(-4.2,-79.30,3.28),local(-4.2,-79.7,1.5),28,1.6,(1,.75,.45),c)
    # Book, reading glasses and a sculpted remote sit on the existing table, not on the floor.
    r=root_at('LOUNGE_LAST_BREAK',c,-4.47,-77.59,.436,.21);m=mb()
    m.rbox(0,0,.02,.29,.205,.031,.002,mi=MI['ivory'])
    for z in (.004,.039):m.rbox(0,0,z,.306,.221,.006,.002,mi=MI['navy'])
    for k in range(8):m.rbox(0,-.104,.008+k*.0036,.286,.002,.001,0,mi=MI['stitch'])
    for x in (-.044,.044):m.torus(x,-.01,.048,.032,.0015,ns=20,nt=4,mi=MI['steel'])
    m.between((-.012,-.01,.048),(.012,-.01,.048),.0015,seg=6,mi=MI['steel'])
    for x in (-.076,.076):m.between((x,-.01,.048),(x,.071,.06),.0015,seg=6,mi=MI['steel'])
    m.rbox(.37,.039,.016,.051,.163,.026,.010,mi=MI['black'])
    for j in range(5):
      for i in range(3):m.sphere(.353+i*.016,-.015+j*.022,.031,.004,.005,.0025,rings=4,seg=6,mi=MI['ivory' if j>0 else 'rust'])
    finish(m,'Reading_book_glasses_remote',c,r);supported(r,'lounge_coffee_table',[(0,0,.001),(.37,.039,.003)])
    # A work jacket and clipped ID left on the side sofa make this a staff break room.
    parent=bpy.data.objects['lounge_sofa_side'];m=mb()
    m.cushion(-.39,.095,.505,.408,.334,.061,r=.029,levels=2,mi=MI['fabric_blue'])
    for s in (-1,1):
      m.cushion(-.39+s*.10,.085,.545,.118,.30,.026,r=.010,levels=1,rot=(0,0,s*.14),mi=MI['fabric_blue'])
      m.rbox(-.39+s*.113,.155,.562,.103,.071,.006,.008,mi=MI['fabric_blue'])
    m.rbox(-.39,-.03,.572,.186,.038,.012,.007,mi=MI['fabric_ochre'])
    m.rbox(-.337,.019,.573,.046,.071,.004,.004,mi=MI['ivory'])
    m.rbox(-.337,.041,.577,.032,.019,.002,.001,mi=MI['navy'])
    m.between((-.39,-.05,.568),(-.39,.17,.568),.0012,seg=4,mi=MI['steel'])
    m.rbox(-.337,-.021,.577,.01,.017,.003,.001,mi=MI['steel'])
    finish(m,'Staff_folded_work_jacket_with_clipped_ID',c,parent)

def cutlery_stations(c):
    for name in ('counter_cutlery_0','counter_cutlery_1'):
      old=bpy.data.objects[name];pos=old.location.copy();remove(name);r=empty(name,c,tuple(pos));m=mb();rng=random.Random(71)
      m.rbox(0,0,.008,.38,.24,.016,.007,mi=MI['steel'])
      for y in (-.114,.114):m.rbox(0,y,.023,.372,.008,.038,.003,mi=MI['steel'])
      for x in (-.184,.184):m.rbox(x,0,.023,.008,.222,.038,.003,mi=MI['steel'])
      for j in range(3):
        x=-.115+j*.115
        m.rbox(x,0,.023,.095,.16,.012,.003,mi=MI['steel'])
        for dx in (-.046,.046):m.rbox(x+dx,0,.101,.005,.16,.15,.002,mi=MI['steel'])
        for y in (-.077,.077):m.rbox(x,y,.101,.088,.005,.15,.002,mi=MI['steel'])
        for y in (-.077,.077):m.rbox(x,y,.176,.099,.011,.008,.003,mi=MI['steel'])
        for dx in (-.046,.046):m.rbox(x+dx,0,.176,.011,.151,.008,.003,mi=MI['steel'])
        for q in range(3):
          a=Vector((x+rng.uniform(-.025,.025),rng.uniform(-.035,.035),.047));b=a+Vector((rng.uniform(-.025,.025),rng.uniform(-.025,.025),.215+q*.011))
          m.between(a,b,.0028,seg=6,mi=MI['steel'])
          if j==0:
            for k in range(4):m.between(b+Vector((-.010+k*.006,0,0)),b+Vector((-.010+k*.006,0,.028)),.0011,seg=4,mi=MI['steel'])
            m.rbox(b.x,b.y,b.z,.025,.003,.009,.001,mi=MI['steel'])
          elif j==1:m.sphere(b.x,b.y,b.z+.008,.012,.003,.021,rings=6,seg=8,mi=MI['steel'])
          else:m.rbox(b.x+.003,b.y,b.z+.017,.012,.004,.037,.002,mi=MI['steel'])
      finish(m,name+'_open_folded_bins_forks_spoons_knives',c,r)
      supported(r,'serving_counter',[(0,0,0)])

def remove_counter_placeholder_parts():
    ob=bpy.data.objects['serving_counter'];ob.data=ob.data.copy();bm=bmesh.new();bm.from_mesh(ob.data);seen=set();erase=[]
    for v in bm.verts:
      if v in seen:continue
      todo=[v];part=[];seen.add(v)
      while todo:
        u=todo.pop();part.append(u)
        for e in u.link_edges:
          n=e.other_vert(u)
          if n not in seen:seen.add(n);todo.append(n)
      zs=[u.co.z for u in part];xs=[u.co.x for u in part]
      if min(zs)>.92 and min(xs)>4.30:erase.extend(part);continue
      fs={f for u in part for f in u.link_faces}
      if min(zs)>.965 and max(zs)<1.15 and any(ob.data.materials[f.material_index].name=='props' for f in fs):erase.extend(part)
      # Food guards end before the coffee service bay. Preserve their construction,
      # and remove the final isolated upright/heat-strip rather than leave it floating.
      if min(zs)>1.08 and min(xs)<-5 and max(xs)>5:
        lo,hi=min(xs),max(xs)
        for u in part:u.co.x=lo+(u.co.x-lo)*(3.30-lo)/(hi-lo)
      elif min(zs)>.924 and min(xs)>3.3 and max(zs)>1.4:erase.extend(part)
      elif min(zs)>1.45 and max(xs)>3.3 and min(xs)>2.9:erase.extend(part)
    bmesh.ops.delete(bm,geom=erase,context='VERTS');bm.to_mesh(ob.data);bm.free()

def espresso(c):
    r=root_at('ESPRESSO_STATION',c,24.9,-65.36,.955);m=mb()
    m.rbox(0,0,.035,.66,.48,.07,.009,mi=MI['steel'])
    m.rbox(0,.118,.244,.63,.22,.42,.025,mi=MI['navy'])
    for s in (-1,1):m.rbox(s*.296,0,.215,.043,.47,.397,.008,mi=MI['steel'])
    m.rbox(0,0,.43,.65,.47,.043,.009,mi=MI['steel'])
    m.rbox(0,-.131,.289,.555,.038,.188,.010,mi=MI['steel'])
    m.rbox(0,-.108,.128,.548,.04,.097,.006,mi=MI['black'])
    for x in (-.155,.155):
      m.cylz(x,-.161,.175,.226,.030,seg=16,mi=MI['steel'])
      m.between((x,-.162,.193),(x,-.31,.2),.012,seg=12,mi=MI['black'])
      for k in range(3):m.sphere(x-.043+k*.044,-.154,.343,.008,.003,.008,rings=6,seg=10,mi=MI['black'])
      m.lathe([(0,0),(.026,0),(.037,.055),(.035,.059),(.029,.055),(.024,.013)],loc=(x,-.153,.072),seg=20,mi=MI['ceramic'])
      m.torus(x+.034,-.15,.107,.015,.003,ns=14,nt=4,rot=(math.pi/2,0,0),mi=MI['ceramic'])
    for k in range(9):m.rbox(-.23+k*.057,-.071,.073,.012,.281,.009,.003,mi=MI['black'])
    m.add(p_cyl(.023,.008,24),loc=(0,-.155,.29),rot=(math.pi/2,0,0),mi=MI['ivory'])
    m.between((0,-.161,.29),(.008,-.161,.3),.0012,seg=4,mi=MI['black'])
    m.between((.259,-.15,.28),(.259,-.24,.108),.006,seg=10,mi=MI['steel'])
    m.between((.259,-.24,.108),(.276,-.223,.07),.006,seg=10,mi=MI['steel'])
    for k in range(4):
      cup=p_lathe([(0,0),(.026,0),(.035,.051),(.035,.055),(.029,.055),(.024,.009),(0,.009)],seg=16)
      bmesh.ops.remove_doubles(cup,verts=cup.verts[:],dist=.0000001)
      bmesh.ops.recalc_face_normals(cup,faces=cup.faces[:])
      m.add(cup,loc=(-.22+k*.145,.04,.455),mi=MI['ceramic'])
    # Grinder with a translucent hopper, filled beans and a doser lever.
    m.rbox(-.49,.039,.061,.20,.244,.122,.014,mi=MI['navy'])
    m.cylz(-.49,.04,.105,.31,.071,seg=24,bevel=.008,mi=MI['steel'])
    m.lathe([(.055,.30),(.09,.44),(.095,.47),(.092,.475)],loc=(-.49,.04,0),seg=28,mi=MI['glass'])
    m.cylz(-.49,.04,.473,.486,.096,seg=24,mi=MI['black'])
    rnd=random.Random(27)
    for k in range(23):m.sphere(-.49+rnd.uniform(-.06,.06),.04+rnd.uniform(-.05,.05),.40+rnd.uniform(-.03,.012),.009,.005,.006,rings=4,seg=6,mi=MI['walnut'])
    m.between((-.49,-.055,.23),(-.49,-.108,.19),.018,seg=10,mi=MI['black'])
    finish(m,'Espresso_dual_group_machine_grinder_and_cups',c,r)
    supported(r,'serving_counter',[(-.296,0,0),(.296,0,0)])
    panel('Coffee_brand',(-.49,-.087,.086),.177,.047,'coffee_label.png',c,parent=r)
    m=mb();p=Vector(local(24.78,-64.08,2.313))
    m.rbox(*p,.47,.099,.034,.004,mi=MI['navy'])
    m.rbox(p.x,p.y,p.z-.019,.419,.072,.004,.001,mi=MI['lamp'])
    light=finish(m,'Coffee_under_hatch_task_strip',c);supported(light,'hatch_frame_head',[(p.x,p.y,2.33)],(0,0,1))
    area('R8_Coffee_worklight',p+Vector((0,0,-.025)),local(24.8,-65.37,1.2),32,.41,(.91,.95,1),c)

def serving(c):
    remove_counter_placeholder_parts();espresso(c);cutlery_stations(c)
    # Consolidated menu, with proper rails and two directed wash lights.
    for i in range(3):remove('menu_board_'+str(i))
    r=root_at('KITCHEN_MENU',c,20.1,-64.107,2.86);m=mb()
    m.rbox(0,0,0,8.62,.048,.854,.012,mi=MI['black'])
    for x in (-4.19,4.19):
      for z in (-.37,.37):screw(m,(x,-.026,z),(0,-1,0),.007)
    finish(m,'Menu_frame_fasteners',c,r)
    panel('Kitchen_menu_albedo',(0,-.028,0),8.52,.778,'menu_board.png',c,parent=r,lit=.35)
    supported(r,'kitchen_front_hi',[(0,.023,0)],(0,1,0))
    for x in (17.5,22.9):area('R8_Menu_wash_'+str(x),local(x,-65.1,3.33),local(x,-64.1,2.85),12,.55,(1,.93,.81),c)
    # Kiosk screen is a designed texture on the face in the original object's local frame.
    ko=bpy.data.objects['order_kiosk'];panel('Kiosk_food_selection',(0,.186,1.27),.397,.297,'kiosk_menu.png',c,rot=(0,0,math.pi),parent=ko,lit=.45)
    m=mb();rng=random.Random(16)
    for k in range(6):
      x=15.7+k*1.1;y=-65.30
      # Low food surfaces fit the stainless trays without hiding them beneath globes.
      m.rbox(*local(x,y,1.016),.824,.397,.018,.012,mi=MI[['food_gold','food_green','food_red','food_gold','ivory','food_green'][k]])
      for q in range(19):
        xx=x+rng.uniform(-.35,.35);yy=y+rng.uniform(-.16,.16);zz=1.052
        if k in (1,5):m.sphere(*local(xx,yy,zz),.035,.028,.025,rings=5,seg=8,mi=MI['food_green'])
        elif k==2:m.sphere(*local(xx,yy,zz),.026,.026,.018,rings=5,seg=8,mi=MI['food_red'])
        elif k==3:m.sphere(*local(xx,yy,zz),.045,.025,.025,rings=5,seg=8,mi=MI['food_gold'])
        else:m.sphere(*local(xx,yy,zz),.023,.008,.007,rings=4,seg=6,mi=MI['ivory' if k==4 else 'food_gold'])
      m.between(local(x+.25,y+.08,1.04),local(x+.38,y+.32,1.14),.007,seg=8,mi=MI['steel'])
      m.sphere(*local(x+.23,y+.06,1.041),.031,.045,.009,rings=4,seg=8,mi=MI['steel'])
    finish(m,'Hot_food_six_gastronorm_pans_and_ladles',c)
    # Pots on the visible kitchen work surface and rack details.
    r=root_at('KITCHEN_PREP',c,17.2,-61.1,.93);m=mb()
    for x in (-.65,.65):
      m.lathe([(0,0),(.158,0),(.172,.023),(.172,.233),(.166,.24),(.151,.232)],loc=(x,0,0),seg=24,mi=MI['steel'])
      m.cylz(x,0,.215,.222,.145,seg=24,mi=MI['food_red'])
      for s in (-1,1):m.between((x+s*.168,-.044,.19),(x+s*.225,-.044,.19),.008,seg=8,mi=MI['black'])
    finish(m,'Kitchen_stockpots_loop_handles',c,r)
    supported(r,'kitchen_block',[(-.65,0,0),(.65,0,0)])

def club_chair(c,name,pos,rz):
    """Curved upholstered barrel back, compressed pad and exposed timber arms."""
    remove(name);r=root_at(name,c,*pos,.016,rz)
    if 'blue_thread' not in MI:
      MI['blue_thread']=len(MATS);MATS.append(material('blue_thread',(.18,.25,.34),.94))
    m=mb();bm=bmesh.new();rows=[]
    for j in range(13):
      t=j/12;row=[];width=.329+.046*math.sin(t*math.pi/2)
      for i in range(25):
        f=2*i/24-1;x=width*f;z=.355+t*(.620-.055*f*f)
        y=-.310+.155*f*f+.007*math.sin(f*math.pi*4)**2*math.sin(t*math.pi)
        row.append(bm.verts.new((x,y,z)))
      rows.append(row)
    for j in range(12):
      for i in range(24):bm.faces.new((rows[j][i],rows[j][i+1],rows[j+1][i+1],rows[j+1][i]))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);bmesh.ops.solidify(bm,geom=bm.faces[:],thickness=.094)
    for f in bm.faces:f.smooth=True
    m.add(bm,mi=MI['fabric_blue'])
    pb=p_cushion(.704,.655,.169,.058,2)
    for v in pb.verts:
      if v.co.z>0:v.co.z-=.018*math.exp(-((v.co.x/.24)**2+(v.co.y/.25)**2))
    m.add(pb,loc=(0,.048,.430),mi=MI['fabric_blue'])
    m.cushion(0,.027,.307,.659,.60,.088,r=.024,levels=1,mi=MI['fabric_blue'])
    for s in (-1,1):
      for t in (-1,1):
        bottom=(s*.287,t*.28,.015);top=(s*.234,t*.189,.387)
        m.between(bottom,top,.014,seg=12,mi=MI['navy']);m.cylz(bottom[0],bottom[1],0,.02,.021,seg=12,mi=MI['rubber'])
      m.between((s*.234,-.189,.385),(s*.253,-.281,.695),.012,seg=10,mi=MI['navy'])
      m.between((s*.259,.166,.386),(s*.363,.173,.625),.012,seg=10,mi=MI['navy'])
      # Timber armrests have an elliptical section and a gentle ergonomic sweep.
      pr=bmesh.new();rings=[]
      for k in range(15):
        t=k/14;cx=s*(.353+.014*math.sin(t*math.pi));cy=-.254+t*.468;cz=.586+.064*math.sin(t*math.pi*.85)
        ring=[pr.verts.new((cx+.03*math.cos(TAU*i/12),cy,cz+.014*math.sin(TAU*i/12))) for i in range(12)];rings.append(ring)
      for k in range(14):
        for i in range(12):pr.faces.new((rings[k][i],rings[k][(i+1)%12],rings[k+1][(i+1)%12],rings[k+1][i]))
      pr.faces.new(rings[0][::-1]);pr.faces.new(rings[-1]);bmesh.ops.recalc_face_normals(pr,faces=pr.faces[:])
      for f in pr.faces:f.smooth=True
      m.add(pr,mi=MI['oak'])
    for y in (-.18,.18):m.between((-.234,y,.376),(.234,y,.376),.012,seg=12,mi=MI['navy'])
    finish(m,name+'_barrel_upholstery_timber_arms_frame',c,r)
    pts=[(.375*f,-.310+.155*f*f-.046,.975-.055*f*f) for f in [2*i/36-1 for i in range(37)]]
    curve(name+'_curved_back_crown_welt',pts,.0023,'blue_thread',c,r,res=1)
    for x in (-.215,0,.215):
      f=x/.37;curve(name+'_tailored_channel_'+str(x),[(x,-.310+.155*f*f-.095,.39),(x,-.310+.155*f*f-.095,.89)],.0018,'blue_thread',c,r,res=1)
    supported(r,'lounge_rug',[(s*.287,t*.28,0) for s in (-1,1) for t in (-1,1)])

def kiosk(c):
    remove('Kiosk_food_selection');remove('order_kiosk')
    r=root_at('order_kiosk',c,13.1,-66.8,0);m=mb()
    m.rbox(0,0,.024,.62,.459,.048,.012,mi=MI['steel'])
    tapered(m,(0,.015,.542),(.197,.143),(.252,.144),.989,'navy')
    m.rbox(0,.015,.974,.242,.171,.197,.012,mi=MI['black'])
    m.rbox(0,0,1.371,.493,.081,.715,.024,rot=(-.15,0,0),mi=MI['navy'])
    m.rbox(0,-.048,1.373,.458,.012,.674,.012,rot=(-.15,0,0),mi=MI['black'])
    m.rbox(0,.056,.643,.157,.015,.62,.007,mi=MI['navy'])
    for z in (.20,.24,.28,.32):m.rbox(0,.066,z,.122,.005,.011,.002,mi=MI['black'])
    for x in (-.064,.064):
      for z in (.398,.828):screw(m,(x,.067,z),(0,1,0),.0035)
    # Receipt printer and its curled receipt, separate from the touch-screen face.
    m.rbox(0,-.059,.797,.221,.132,.191,.014,mi=MI['steel'])
    m.rbox(0,-.131,.791,.151,.009,.011,.002,mi=MI['black'])
    m.rbox(.146,-.087,.975,.111,.11,.143,.016,rot=(-.32,0,0),mi=MI['black'])
    m.rbox(.146,-.15,.994,.079,.007,.070,.004,rot=(-.32,0,0),mi=MI['field'])
    m.rbox(.146,-.157,.953,.085,.006,.007,.001,mi=MI['steel'])
    for k in range(3):m.sphere(.121+k*.026,-.155,.970,.005,.002,.005,rings=4,seg=6,mi=MI['ivory'])
    m.rbox(0,.01,1.75,.299,.024,.016,.004,mi=MI['ochre'])
    finish(m,'Kiosk_tilted_touchscreen_pedestal_payment_and_receipt',c,r)
    panel('Kiosk_touchscreen_menu',(0,-.057,1.376),.419,.558,'kiosk_menu.png',c,rot=(-.15,0,0),parent=r,lit=.52)
    me=bpy.data.meshes.new('Kiosk_receipt');vs=[]
    for j in range(6):
      t=j/5
      for s in (-1,1):vs.append((s*.053,-.135-.019*math.sin(t*math.pi/2),.787-t*.079))
    me.from_pydata(vs,[],[(j*2,j*2+1,j*2+3,j*2+2) for j in range(5)]);me.materials.append(MATS[MI['ivory']]);o=bpy.data.objects.new('Kiosk_curled_receipt',me);c.objects.link(o);o.parent=r;o['support']='assembly'
    supported(r,'caf_floor',[(x,y,0) for x in (-.23,.23) for y in (-.17,.17)])

def table_life(c):
    # Two authored meal clusters; quiet tables keep the room legible.
    for label,x,y,z in [('Lunch',15.73,-73.59,.748),('Late_break',23.58,-77.26,.748)]:
      idx=0 if label=='Lunch' else 5
      for suffix in ('tableset','mug','bottle'):remove(f'caf_{suffix}_{idx}')
      r=root_at('TABLE_'+label,c,x,y,z,.12);m=mb()
      m.lathe([(0,0),(.075,0),(.131,.013),(.142,.021),(.134,.025),(.079,.009),(0,.009)],seg=28,mi=MI['ceramic'])
      for j in range(2):
        m.rbox(-.026+j*.052,.017,.047,.069,.10,.034,.007,rot=(0,0,-.13),mi=MI['food_gold'])
        m.rbox(-.026+j*.052,.017,.042,.071,.102,.009,.003,rot=(0,0,-.13),mi=MI['food_green'])
      m.between((.194,-.078,.015),(.194,.079,.016),.005,seg=6,mi=MI['steel'])
      for k in range(4):m.between((.182+k*.008,.07,.016),(.182+k*.008,.099,.016),.0017,seg=4,mi=MI['steel'])
      m.lathe([(0,0),(.028,0),(.039,.068),(.036,.073),(.031,.068),(.027,.011)],loc=(-.204,.018,0),seg=22,mi=MI['ceramic'])
      m.cylz(-.204,.018,.055,.057,.03,seg=22,mi=MI['walnut'])
      m.torus(-.244,.018,.039,.019,.004,ns=20,nt=4,rot=(math.pi/2,0,0),mi=MI['ceramic'])
      m.rbox(.177,-.031,.004,.091,.171,.007,.002,mi=MI['ivory'])
      finish(m,'Plate_sandwich_fork_napkin_coffee_'+label,c,r)
      target='caf_table_0' if label=='Lunch' else 'caf_table_5';supported(r,target,[(0,0,0)])

def table_stories(c):
    # The closest dining table has an actual finished meal, not another perfect setting.
    for suffix in ('tray','tableset','mug','bottle'):remove('caf_'+suffix+'_1')
    r=root_at('TABLE_FINISHED_LUNCH',c,15.51,-77.27,.748,-.11);m=mb()
    m.rbox(0,0,.008,.476,.337,.016,.012,mi=MI['navy'])
    for y in (-.158,.158):m.rbox(0,y,.022,.456,.018,.025,.005,mi=MI['navy'])
    for x in (-.229,.229):m.rbox(x,0,.022,.018,.311,.025,.005,mi=MI['navy'])
    m.lathe([(0,0),(.074,0),(.118,.011),(.132,.021),(.128,.024),(.08,.008),(0,.008)],loc=(-.058,.019,.017),seg=32,mi=MI['ceramic'])
    m.lathe([(0,0),(.030,0),(.037,.068),(.034,.073),(.029,.068),(.026,.010)],loc=(.153,.047,.017),seg=26,mi=MI['ceramic'])
    m.torus(.19,.049,.053,.018,.0038,ns=18,nt=4,rot=(math.pi/2,0,0),mi=MI['ceramic'])
    m.cylz(.153,.047,.037,.039,.027,seg=24,mi=MI['walnut'])
    for x,y in [(-.10,.033),(-.04,-.037),(-.061,.069)]:m.sphere(x,y,.033,.012,.008,.007,rings=5,seg=8,mi=MI['food_gold'])
    m.leaf((-.049,.054,.036),.039,.010,bend=.07,yaw=-.61,segs=6,mi=MI['food_green'])
    m.between((.069,-.121,.029),(.088,.024,.031),.005,seg=6,mi=MI['steel'])
    for k in range(4):m.between((.077+k*.008,.025,.031),(.079+k*.008,.05,.031),.0016,seg=4,mi=MI['steel'])
    # Crumpled napkin is an authored surface rather than a white block.
    pb=bmesh.new();vs=[pb.verts.new(p) for p in [(.099,-.117,.026),(.185,-.103,.028),(.176,-.054,.043),(.112,-.04,.03),(.14,-.079,.047)]]
    for f in [(0,1,4),(1,2,4),(2,3,4),(3,0,4)]:pb.faces.new([vs[i] for i in f])
    m.add(pb,mi=MI['ivory']);finish(m,'Used_tray_empty_plate_coffee_napkin_and_fork',c,r)
    supported(r,'caf_table_1',[(0,0,0)])
    # Trays left at a wiped table explain the sparse neighboring setting.
    for suffix in ('tray','tableset','mug','bottle'):remove('caf_'+suffix+'_6')
    r=root_at('TABLE_WIPED_READY',c,2.42,-63.51,.748,.06);m=mb()
    for j in range(3):
      m.rbox(0,0,.012+j*.018,.427,.291,.017,.008,mi=MI['navy' if j<2 else 'ochre'])
      for y in (-.131,.131):m.rbox(0,y,.024+j*.018,.417,.018,.019,.004,mi=MI['navy' if j<2 else 'ochre'])
    m.rbox(.32,-.08,.010,.099,.121,.020,.009,mi=MI['fabric_blue'])
    finish(m,'Stacked_trays_and_folded_cleaning_cloth',c,r);supported(r,'caf_table_6',[(0,0,.003),(.32,-.08,0)])

def fan(c,x,y,label):
    r=root_at('CEILING_FAN_'+label,c,x,y,3.99);m=mb()
    m.cylz(0,0,.11,.965,.025,seg=16,mi=MI['navy']);m.cylz(0,0,.965,1.01,.088,seg=24,mi=MI['black'])
    m.lathe([(.03,-.064),(.087,-.04),(.12,.015),(.13,.10),(.095,.137),(.03,.144)],seg=32,mi=MI['navy'])
    for k in range(5):
      a=k*TAU/5;pts=[(.09,-.038),(.29,-.083),(.58,-.081),(.657,-.017),(.61,.059),(.25,.047)]
      pb=p_ring_prism(pts,.009,.003);m.add(pb,loc=(0,0,.062),rot=(0,.024,a),mi=MI['walnut'])
    finish(m,'Fan_motor_five_timber_blades_'+label,c,r)
    supported(r,'caf_roof_deck4' if label=='DINING' else 'caf_roof_deck1',[(0,0,1.01)],(0,0,1))

def services(c):
    # One coherent HVAC trunk and a sprinkler main; details occur at their functional joints.
    m=mb();z=4.48;y=-68.28
    m.rbox(*local(9,y,z),32.5,.33,.25,.008,mi=MI['steel'])
    for x in (-6,-1,4,9,14,19,24):
      m.rbox(*local(x,y,z),.022,.355,.276,.003,mi=MI['navy'])
      for sy in (-.13,.13):m.between(local(x,y+sy,z+.13),local(x,y+sy,5.0),.004,seg=6,mi=MI['steel'])
      m.rbox(*local(x,y,z-.129),.65,.255,.013,.003,mi=MI['navy'])
      for k in range(7):m.rbox(*local(x-.24+k*.08,y,z-.138),.039,.196,.01,.001,mi=MI['black'])
    m.between(local(24.75,-78.6,4.35),local(24.75,-60.2,4.35),.027,seg=14,mi=MI['rust'])
    for y in (-77.8,-74.5,-71.5,-67.2,-63.8):
      m.torus(*local(24.75,y,4.35),.034,.009,ns=16,nt=5,rot=(math.pi/2,0,0),mi=MI['steel'])
      m.between(local(24.75,y,4.35),local(24.75,y,5.0),.004,seg=6,mi=MI['steel'])
      m.between(local(24.75,y,4.32),local(24.75,y,4.27),.009,seg=10,mi=MI['copper'])
      m.cylz(*local(24.75,y)[:2],4.254,4.263,.028,seg=16,mi=MI['copper'])
    finish(m,'HVAC_trunk_outlet_grilles_hangers_sprinklers',c)
    fan(c,18.85,-70.54,'DINING');fan(c,1.83,-71.91,'CENTRAL')
    # Every pendant gains a practical light, positioned beneath the modeled diffuser.
    for o in list(CAF.objects):
      if not o.name.startswith('caf_pendant_'):continue
      p=o.location.copy();p.z-=.027
      area('R8_Practical_'+o.name,p,p+Vector((0,0,-1)),68 if '_L' not in o.name else 90,.36,(1,.88,.70),c)
    for name in ('lounge_floor_lamp_0','lounge_floor_lamp_1'):
      ob=bpy.data.objects.get(name)
      if ob:area('R8_'+name,ob.location+Vector((0,0,1.63)),ob.location+Vector((0,0,.6)),25,.22,(1,.78,.48),c)
    for o in bpy.data.collections['LIGHTS'].objects:
      if o.name.startswith('CAF_FILL_'):
        # Quiet main routes are intentionally less intense than the functional clusters.
        o.data=o.data.copy();o.data.energy=140 if abs(o.location.x+2)<.2 else 170 if o.location.x<0 else 220
        o.data.color=(1,.96,.87) if o.location.x>0 else (.94,.94,1)
    for label,p,t,e in [('N',(-7.35,-64.27,3.52),(-3.7,-64.2,1.2),240),('S',(-7.35,-76.25,3.45),(-4,-77,1.15),125)]:
      light=area('R8_Window_fill_'+label,local(*p),local(*t),e,2.6,(.71,.82,1),c)
      light.data.shape='RECTANGLE';light.data.size_y=.65
      if hasattr(light.data,'use_shadow'):light.data.use_shadow=False
    # Two compact track heads are mounted to the existing beam over the game bay.
    r=root_at('GAME_TRACK_LIGHT',c,-4.8,-66,4.345);m=mb()
    m.rbox(0,0,.068,.91,.106,.074,.007,mi=MI['navy'])
    for s,t in [(-1,(-6.30,-64.50,1.25)),(1,(-3.65,-64.10,.84))]:
      p=Vector((s*.337,0,.003));world=Vector(local(-4.8,-66,4.345))+p;direction=(Vector(local(*t))-world).normalized()
      m.between((s*.337,0,.068),tuple(p),.01,seg=10,mi=MI['steel'])
      m.add(p_cyl(.052,.116,20,r2=.043),loc=tuple(p),rot=Vector((0,0,1)).rotation_difference(direction).to_euler(),mi=MI['black'])
      m.add(p_cyl(.042,.006,20),loc=tuple(p+direction*.060),rot=Vector((0,0,1)).rotation_difference(direction).to_euler(),mi=MI['lamp'])
      area('R8_Game_track_'+str(s),world+direction*.069,local(*t),72,.082,(1,.9,.75),c)
    finish(m,'Game_track_light_mount_and_heads',c,r);supported(r,'caf_roof_beam3',[(0,0,.105)],(0,0,1))

def surface_pass():
    wall_mat=MATS[MI['plaster']]
    copies={}
    for ob in CAF.objects:
      if ob.type!='MESH':continue
      replace={}
      for j,mat in enumerate(ob.data.materials):
        if not mat:continue
        if mat.name=='plaster':replace[j]=wall_mat
        elif mat.name in ('dado','cafe_tile'):
          if mat.name not in copies:
            mm=mat.copy();mm.name='CAF_R8_'+mat.name+'_finish';nt=mm.node_tree
            b=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
            for l in list(b.inputs['Roughness'].links):nt.links.remove(l)
            b.inputs['Roughness'].default_value=.59 if mat.name=='cafe_tile' else .62
            # A floor or wall paint does not need bevel-shader micro scratches on every surface.
            copies[mat.name]=mm
          replace[j]=copies[mat.name]
      if replace:
        ob.data=ob.data.copy()
        for j,mat in replace.items():ob.data.materials[j]=mat

def lift_existing_rug_props():
    """Correct the inherited floor-placement convention against the actual 16 mm rug."""
    bpy.context.view_layer.update()
    lamp=bpy.data.objects.get('lounge_floor_lamp_1')
    if lamp:lamp.location.x-=.22
    bpy.context.view_layer.update()
    for o in list(CAF.objects):
      if o.type!='MESH' or o.get('support')!='floor':continue
      bb=bounds([o]);cx=(bb[0][0]+bb[1][0])/2;cy=(bb[0][1]+bb[1][1])/2
      if not (-15.4<cx<-8.8 and .30<cy<6.0) or abs(bb[0][2])>.005:continue
      o.location.z+=.016;o['support']='rug'
      # Explicit anchors are chosen from actual lowest mesh vertices.
      pts=[v.co.copy() for v in o.data.vertices if abs((o.matrix_world@v.co).z-bb[0][2])<.0003]
      if pts:
        chosen=[]
        for dim,sign in [(0,-1),(0,1),(1,-1),(1,1)]:
          p=min(pts,key=lambda v:sign*v[dim]);chosen.append(tuple(p))
        supported(o,'lounge_rug',chosen)
    for n in ('lounge_mug','lounge_bottle','lounge_tray'):
      o=bpy.data.objects.get(n)
      if o:o.location.z+=.016
    for o in CAF.objects:
      if o.name.startswith(('caf_tray_','caf_tableset_','caf_mug_','caf_bottle_')):o.location.z=.748

def interface_records():
    return [{ 'name':o.name,'matrix':[list(row) for row in o.matrix_world],'width':o.get('clear_width_m'),'height':o.get('clear_height_m')} for o in bpy.data.collections['INTERFACES'].objects]

def dining_chairs():
    """Continuous molded shell, curved back, handhold and bent-tube frame."""
    MI['sage']=len(MATS);MATS.append(material('sage',(.17,.25,.20),.55))
    proto=bpy.data.collections['PROTOTYPES'];variants=[]
    profile=[(.243,.452),(.155,.441),(-.075,.445),(-.192,.466),(-.235,.523),(-.25,.674),(-.279,.822)]
    def sample(t):
      t=t*(len(profile)-1);k=min(len(profile)-2,int(t));u=t-k
      p0=Vector(profile[max(0,k-1)]);p1=Vector(profile[k]);p2=Vector(profile[k+1]);p3=Vector(profile[min(len(profile)-1,k+2)])
      return .5*((2*p1)+(-p0+p2)*u+(2*p0-5*p1+4*p2-p3)*u*u+(-p0+3*p1-3*p2+p3)*u*u*u)
    for col in ('rust','navy','ochre','sage'):
      m=mb();bm=bmesh.new();rows=[];N=22;K=12
      for j in range(N+1):
        t=j/N;y,z=sample(t);back=max(0,(t-.48)/.52);width=.218-.016*back
        if j in (0,N):width-=.026
        row=[]
        for i in range(K+1):
          f=2*i/K-1;x=f*width;zz=z+.018*f*f*(1-back);yy=y-.029*f*f*back
          row.append(bm.verts.new((x,yy,zz)))
        rows.append(row)
      for j in range(N):
        for i in range(K):
          if j in (19,20) and 3<=i<=8:continue
          bm.faces.new([rows[j][i],rows[j][i+1],rows[j+1][i+1],rows[j+1][i]])
      bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);bmesh.ops.solidify(bm,geom=bm.faces[:],thickness=.012)
      for f in bm.faces:f.smooth=True
      m.add(bm,mi=MI[col])
      for s in (-1,1):
        pts=[(s*.208,-.231,.014),(s*.182,-.163,.414),(s*.182,.167,.414),(s*.219,.224,.014)]
        for a,b in zip(pts,pts[1:]):m.between(a,b,.012,seg=10,mi=MI['black'])
        for t in (-1,1):
          m.cylz(s*(.208 if t<0 else .219),-.231 if t<0 else .224,0,.022,.017,seg=10,mi=MI['rubber'])
        m.between((s*.18,-.177,.417),(s*.175,-.297,.678),.010,seg=10,mi=MI['black'])
        m.rbox(s*.175,-.291,.674,.038,.013,.058,.003,mi=MI['black'])
      for y in (-.15,.153):m.between((-.18,y,.404),(.18,y,.404),.01,seg=10,mi=MI['black'])
      pr=finish(m,'R8_Chair_shell_handhold_'+col,proto);del pr['support'];variants.append(pr)
    for o in list(CAF.objects):
      if not o.name.startswith(('caf_chair_','caf_booth_chair_')):continue
      # Match the existing chair colour family so the table layout remains recognizable.
      cols=o.data.color_attributes.get('Col');mean=(.4,.2,.1)
      if cols:
        values=[v.color[:3] for v in cols.data if v.color[0]+v.color[1]+v.color[2]>.45]
        if values:mean=tuple(sum(v[i] for v in values)/len(values) for i in range(3))
      import re
      family=re.search(r'chair_([0-3])',o.data.name)
      idx=int(family.group(1)) if family else 3 if mean[1]>mean[0]*1.25 and mean[1]>mean[2]*1.1 else 1 if mean[2]>mean[0]*1.2 else 2 if mean[0]>.6 else 0
      o.data=variants[idx].data
      md=o.modifiers.new('Manufactured surface normals','WEIGHTED_NORMAL');md.keep_sharp=True;md.weight=40
    print('CHAIR_TRIANGLES',[triangles([o]) for o in variants],flush=True)

def art_and_use(c):
    for ob in list(CAF.objects):
      if ob.name.startswith('band_') or ob.name in ('banner_slogan','banner_safer','sign_lounge_wall','game_wall_shelf_1','lounge_wall_shelf_0','lounge_wall_shelf_1'):
        remove(ob.name)
      elif '_poster_' in ob.name or '_poster_l_' in ob.name:remove(ob.name)
    # Three individually chosen artworks; no wall-to-wall repeating decorations.
    for name,x,y,z,w,h,img,rz in [
      ('Staff_league',-4.95,-60.167,1.84,.64,.86,'league_poster.png',0),
      ('Ridge_landscape',17.65,-79.812,1.65,1.38,.88,'ridge_print.png',math.pi),
      ('Ridge_contours',25.812,-76.18,1.86,1.14,.74,'contour_print.png',-math.pi/2)]:
      r=root_at(name,c,x,y,z,rz);m=mb();m.rbox(0,0,0,w+.054,.035,h+.054,.007,mi=MI['walnut'])
      m.rbox(0,-.021,0,w,.007,h,.002,mi=MI['ivory']);finish(m,name+'_frame',c,r)
      panel(name+'_art',(0,-.026,0),w-.03,h-.03,img,c,parent=r)
      target,direction={'Staff_league':('cafhall_mid_seg0_core',(0,1,0)),'Ridge_landscape':('caf_S_seg1_skin',(0,-1,0)),'Ridge_contours':('caf_E_seg0_skin',(1,0,0))}[name]
      supported(r,target,[(0,.0175,0)],direction)
    remove('divider_game_0')
    for n in ('divider_game_1','divider_game_2'):
      o=bpy.data.objects.get(n)
      if o:o.location.y-=.2
    for n in ('caf_tray_2','caf_tray_6','caf_tray_7','caf_tableset_3','caf_tableset_7','caf_mug_4','caf_mug_6','caf_bottle_6','caf_bottle_9'):remove(n)
    chair=bpy.data.objects.get('caf_chair_5_1')
    if chair:chair.location.y-=.23;chair.rotation_euler.z+=.13
    # Paint only the cafeteria face of the shared north wall.
    for o in bpy.data.collections['HALL'].objects:
      if not o.name.startswith('cafhall_mid_') or o.type!='MESH':continue
      if o.name.endswith('_core'):
        o.data=o.data.copy();idx=len(o.data.materials);o.data.materials.append(MATS[MI['plaster']])
        for p in o.data.polygons:
          if p.normal.y<-.9:p.material_index=idx

def door_leaf(c,name,kind,side,loc,rz):
    """Manufactured closed leaf, real window cutout, with its physical hinge retained."""
    W,H=(1.278,2.615) if kind=='airlock' else (1.068,2.43)
    root=root_at(name+'_HINGE',c,*loc,0,rz);root['door_pose']='closed';root['hinge_axis']='local Z';root['open_angle_degrees']=90*side
    m=mb();m.rbox(side*W/2,0,H/2+.02,W,.07 if kind=='airlock' else .054,H,.009,mi=MI['navy' if kind=='airlock' else 'ivory'])
    body=finish(m,name+'_door_leaf_body',c,root);body['support']='door'
    # Cut real holes before adding glass, bolts and frames.
    if kind=='airlock':
      cut=p_cyl(.149,.30,48);pos=(side*W*.57,0,1.72);rot=(math.pi/2,0,0)
    else:
      cut=p_rbox(.273,.30,.612,.01,3);pos=(side*W*.49,0,1.77);rot=(0,0,0)
    mm=mb();mm.add(cut,loc=pos,rot=rot,mi=MI['black']);cutter=finish(mm,name+'_cut_tool',c,root)
    bpy.context.view_layer.objects.active=body
    for old_md in list(body.modifiers):body.modifiers.remove(old_md)
    md=body.modifiers.new('Actual vision aperture','BOOLEAN');md.operation='DIFFERENCE';md.solver='EXACT';md.object=cutter
    bpy.ops.object.modifier_apply(modifier=md.name);remove(cutter.name)
    wn=body.modifiers.new('Manufactured surface normals','WEIGHTED_NORMAL');wn.keep_sharp=True;wn.weight=40
    m=mb()
    for z in (.32,1.29,2.30):
      m.cylz(0,0,z-.072,z+.072,.011 if kind=='airlock' else .021,seg=12,mi=MI['steel'])
      m.rbox(side*.046,.014,z,.088,.011,.048,.003,mi=MI['steel'])
    for x in (side*.055,side*(W-.053)):m.rbox(x,.038,H/2,.012,.011,H-.04,.002,mi=MI['rubber'])
    for z in (.046,H-.018):m.rbox(side*W/2,.038,z,W-.08,.011,.012,.002,mi=MI['rubber'])
    if kind=='airlock':
      for s in (-1,1):
        m.torus(side*W*.57,s*.043,1.72,.162,.015,ns=48,nt=6,rot=(math.pi/2,0,0),mi=MI['steel'])
      m.add(p_cyl(.146,.015,48),loc=(side*W*.57,0,1.72),rot=(math.pi/2,0,0),mi=MI['glass'])
      for k in range(8):
        a=k*TAU/8;screw(m,(side*W*.57+.175*math.cos(a),.043,1.72+.175*math.sin(a)),(0,1,0),.0045)
      for z in (.52,2.19):
        m.rbox(side*W/2,.044,z,W-.13,.021,.04,.004,mi=MI['steel'])
      x=side*W*.78;m.torus(x,.091,1.055,.098,.012,ns=28,nt=6,rot=(math.pi/2,0,0),mi=MI['rust'])
      m.between((x,.046,1.055),(x,.092,1.055),.027,seg=14,mi=MI['steel'])
      for k in range(3):
        a=k*TAU/3;m.between((x,.095,1.055),(x+.091*math.cos(a),.095,1.055+.091*math.sin(a)),.008,seg=8,mi=MI['steel'])
      m.rbox(side*(W-.137),.054,1.23,.032,.021,.285,.007,mi=MI['steel'])
      m.rbox(side*W/2,.039,.16,W-.14,.011,.21,.003,mi=MI['steel'])
    else:
      for xx in (-.146,.146):m.rbox(side*W*.49+xx,.033,1.77,.015,.012,.65,.003,mi=MI['steel'])
      for zz in (1.456,2.084):m.rbox(side*W*.49,.033,zz,.306,.012,.022,.003,mi=MI['steel'])
      m.rbox(side*W*.49,.043,1.77,.251,.012,.588,.005,mi=MI['glass'])
      # The frame above is open in the center too; glazed panel remains distinct.
      m.rbox(side*W/2,.037,1.15,W-.045,.012,.073,.003,mi=MI['field'])
      m.rbox(side*W*.78,.039,1.03,.17,.014,.34,.009,mi=MI['steel'])
      m.rbox(side*W/2,.035,.215,W-.12,.009,.29,.003,mi=MI['steel'])
      m.rbox(side*W*.28,.044,2.32,.28,.044,.061,.009,mi=MI['steel'])
      m.between((side*W*.28,.064,2.31),(side*.08,.080,2.335),.009,seg=10,mi=MI['black'])
      m.between((side*.08,.080,2.335),(0,.024,2.37),.009,seg=10,mi=MI['black'])
    finish(m,name+'_door_leaf_fittings_seals_hinges',c,root)['support']='door'
    return root

def doors(c):
    for n in ('airlock_leaf_L','airlock_leaf_R','med_leaf_S','med_leaf_N'):remove(n)
    for side,n,x in [(1,'airlock_L',6.711),(-1,'airlock_R',9.289)]:
      r=door_leaf(c,n,'airlock',side,(x,-80),0)
      supported(r,'caf_S_frame0_L' if side==1 else 'caf_S_frame0_R',[(-side*.011,0,.32)],(-side,0,0))
    for side,n,y in [(1,'medical_S',-71.079),(-1,'medical_N',-68.921)]:
      r=door_leaf(c,n,'medical',side,(26,y),math.pi/2)
      supported(r,'caf_E_frame0_L' if side==1 else 'caf_E_frame0_R',[(-side*.021,0,.32)],(0,-side,0))
    # Inherited glazed leaves use hinge-centre pivots. Mount their hinge barrels
    # against the jamb's actual cafeteria face instead of the middle of the wall.
    for name,target in [('yard_leaf_S','caf_W_frame0_L'),('yard_leaf_N','caf_W_frame0_R')]:
      ob=bpy.data.objects[name];face=bounds([bpy.data.objects[target]])[1][0]
      pts=[ob.matrix_world@v.co for v in ob.data.vertices];back=min(p.x for p in pts)
      ob.location.x+=face+.001-back;bpy.context.view_layer.update()
      pts=[ob.matrix_world@v.co for v in ob.data.vertices];back=min(p.x for p in pts)
      contacts=[p for p in pts if abs(p.x-back)<.00001]
      supported(ob,target,[tuple(ob.matrix_world.inverted()@p) for p in contacts],(-1,0,0))
    p=Vector(local(8,-79.77,2.775));m=mb()
    m.rbox(*p,.72,.084,.041,.008,mi=MI['navy'])
    m.rbox(p.x,p.y+.005,p.z-.024,.65,.061,.008,.002,mi=MI['lamp'])
    o=finish(m,'Airlock_overdoor_practical',c);supported(o,'caf_S_frame0_H',[(p.x,.19,p.z)],(0,-1,0))
    area('R8_Airlock_hardware_light',p+Vector((0,.054,-.023)),local(8,-79.94,1.23),16,.65,(1,.86,.68),c)

def plants(c):
    """Three branching ficus plants; curved blades, midribs and secondary veins."""
    MI['terracotta']=len(MATS);MATS.append(material('terracotta',(.37,.14,.057),.79,texture='plaster',bump=.08))
    MI['leaf_light']=len(MATS);MATS.append(material('leaf_light',(.115,.26,.073),.75))
    MI['leaf_vein']=len(MATS);MATS.append(material('leaf_vein',(.135,.235,.087),.82))
    for i,name in enumerate(('lounge_plant_0','lounge_plant_2','plant_ne')):
      old=bpy.data.objects.get(name);pos=old.location.copy();remove(name)
      if name=='lounge_plant_0':pos=Vector(local(-1.0,-78.55,.016))
      r=empty(name,c,tuple(pos));rng=random.Random(44+i);m=mb()
      m.lathe([(.131,0),(.146,.016),(.184,.291),(.195,.314),(.195,.338),(.177,.341),(.169,.311),(.126,.054)],seg=36,close=True,mi=MI['terracotta'])
      m.cylz(0,0,.302,.308,.169,seg=32,mi=MI['soil'])
      for k in range(5):m.sphere(rng.uniform(-.09,.09),rng.uniform(-.09,.09),.311,.017,.012,.008,rings=4,seg=6,mi=MI['oak'])
      stem=[(0,0,.301),(.022,-.005,.54),(-.019,.014,.91),(.016,.027,1.20),(0,.014,1.43)]
      for j,(a,b) in enumerate(zip(stem,stem[1:])):m.between(a,b,.011-j*.002,seg=10,r2=.009-j*.002,mi=MI['walnut'])
      for k in range(25):
        z=.48+k*.038;a=k*2.399+i*.7;rr=.061+math.sin(k/24*math.pi)*.12
        base=Vector((0,.02,z));tip=Vector((rr*math.cos(a),.02+rr*math.sin(a),z+.05))
        m.between(base,tip,.003,seg=6,r2=.0018,mi=MI['walnut'])
        L=.28+rng.uniform(-.055,.045);W=.102+rng.uniform(-.014,.018);pitch=.46+rng.uniform(-.23,.34);yaw=a-math.pi/2
        m.leaf(tuple(tip),L,W,bend=.18,twist=rng.uniform(-.16,.16),segs=11,droop=.17,yaw=yaw,pitch=pitch,mi=MI['leaf_light' if k%4==0 else 'leaf'])
        rot=Euler((pitch,0,yaw),'XYZ').to_matrix()
        def lp(t,x=0):return tip+rot@Vector((x,L*t,.18*L*t*t-.17*L*t*t*t))
        for t0,t1 in [(0,.33),(.33,.66),(.66,.96)]:m.between(lp(t0),lp(t1),.0008,seg=4,mi=MI['leaf_vein'])
        for t in (.3,.5,.7):
          for s in (-1,1):m.between(lp(t),lp(t+.15,s*W*math.sin(math.pi*(t*.92+.04))*.70),.0005,seg=3,mi=MI['leaf_vein'])
      finish(m,name+'_pot_branches_curved_lamina_veins',c,r)
      supported(r,'lounge_rug' if name=='lounge_plant_0' else 'caf_floor',[(0,0,0),(.09,0,0),(-.09,0,0)])

def detail_cameras():
    cc=bpy.data.collections['CAMERAS']
    for name,eye,target,lens in [
      ('R8_GAMES_HERO',(-.52,-66.65,1.90),(-4.5,-63.7,1.34),28),
      ('R8_FOOSBALL_DETAIL',(-1.40,-65.82,1.54),(-3.65,-64.2,.85),48),
      ('R8_DARTBOARD_DETAIL',(-.21,-61.69,1.91),(-1.13,-60.30,1.75),64),
      ('R8_BASKETBALL_DETAIL',(-2.70,-66.20,1.88),(-6.29,-65.15,1.32),28),
      ('R8_LOUNGE_HERO',(.35,-72.61,1.71),(-4.35,-77.25,1.18),26),
      ('R8_COFFEE_DETAIL',(25.03,-67.19,1.68),(24.70,-65.35,1.235),52),
      ('R8_DINING_HERO',(11.21,-77.30,1.59),(20.30,-72.52,1.11),26)]:
      camera(name,local(*eye),local(*target),lens,cc)

def consolidate_palette():
    """Reimports share identical palette shaders, with exact node-value comparison."""
    import re
    def fingerprint(mat):
      if not mat.use_nodes:return None
      nodes=[]
      for n in mat.node_tree.nodes:
        inputs=[]
        for s in n.inputs:
          if not hasattr(s,'default_value'):continue
          v=s.default_value
          try:v=list(v)
          except TypeError:pass
          inputs.append((s.identifier,v))
        settings={k:getattr(n,k) for k in ('operation','blend_type','noise_dimensions','distribution') if hasattr(n,k)}
        ramp=[(e.position,list(e.color)) for e in n.color_ramp.elements] if hasattr(n,'color_ramp') else None
        nodes.append((n.name,n.bl_idname,inputs,settings,ramp))
      links=sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in mat.node_tree.links)
      return json.dumps((nodes,links),sort_keys=True)
    merged=[]
    for mat in list(bpy.data.materials):
      base=re.sub(r'\.\d{3}$','',mat.name)
      if base==mat.name or not base.startswith('CAF_R8_') or 'image_' in base:continue
      canonical=bpy.data.materials.get(base)
      if canonical and fingerprint(mat)==fingerprint(canonical):
        merged.append({'copy':mat.name,'shared':base});mat.user_remap(canonical);bpy.data.materials.remove(mat)
    bpy.context.scene['cafeteria_shared_materials']=json.dumps(merged)
    return merged

if __name__=='__main__':
    argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    out=Path(argv[0]) if argv else ROOT/'front_end_area_cafeteria_revamp.blend'
    assert out.resolve()!= (ROOT/'front_end_area.blend').resolve(),'Additive output required'
    original=interface_records();palette()
    c=collection('CAFETERIA_R8_DETAIL',CAF)
    games(c);lounge(c);serving(c);table_life(c);kiosk(c);services(c);surface_pass();lift_existing_rug_props();dining_chairs();art_and_use(c);table_stories(c);doors(c);plants(c);detail_cameras()
    contact_repairs=complete_contacts(CAF,SUPPORTS,supported)
    (HERE/'support_repairs.json').write_text(json.dumps(contact_repairs,indent=2)+'\n')
    material_merges=consolidate_palette()
    (HERE/'material_consolidation.json').write_text(json.dumps(material_merges,indent=2)+'\n')
    bpy.context.view_layer.update();assert interface_records()==original,'Interface changes are forbidden'
    # Support roots and immutable interfaces are retained for the validation extension.
    bpy.context.scene['cafeteria_revamp_supports']=json.dumps(SUPPORTS)
    bpy.context.scene['cafeteria_revamp_imports']=json.dumps(IMPORTED)
    bpy.context.scene['cafeteria_revamp_interfaces']=json.dumps(original)
    render_settings(32,(1600,900));bpy.context.scene.camera=bpy.data.objects['R8_GAMES_HERO']
    pack();bpy.ops.wm.save_as_mainfile(filepath=str(out.resolve()),compress=True)
    (HERE/'reimport_report.json').write_text(json.dumps({'imports':IMPORTED,'interfaces_unchanged':True,'supports':SUPPORTS,'blender':bpy.app.version_string},indent=2))
    print('REVAMP_SAVED',str(out),flush=True)
