"""Build one standalone game asset in a fresh Blender process.

blender -b --factory-startup --disable-autoexec --python-exit-code 1 -P build_assets.py -- foosball
Kinds: foosball, dartboard, basketball. Each writes an editable studio .blend and renders.
"""
import sys, os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from kit import *

def foosball(c,root):
    # Real cabinet construction: a hollow perimeter, supported playfield and goal throats.
    m=mb()
    for s in (-1,1):
        m.rbox(0,s*.383,.773,1.48,.078,.215,.012,mi=MI['walnut'])
        m.rbox(0,s*.426,.792,1.47,.007,.033,.002,mi=MI['oak'])
        m.rbox(0,s*.391,.879,1.52,.092,.044,.014,mi=MI['oak'])
        m.rbox(0,s*.43,.851,1.5,.008,.012,.002,mi=MI['black'])
        for x in (-.6,.6):screw(m,(x,s*.428,.746),(0,s,0),.007)
    m.rbox(0,0,.785,1.32,.68,.04,.002,mi=MI['black'])
    m.rbox(0,0,.817,1.27,.682,.024,.002,mi=MI['field'])
    for s in (-1,1):
        x=s*.704
        m.rbox(x,0,.69,.085,.79,.047,.008,mi=MI['walnut'])
        for sy in (-1,1):m.rbox(x,sy*.265,.791,.084,.23,.175,.009,mi=MI['walnut'])
        m.rbox(x,0,.871,.1,.80,.039,.011,mi=MI['oak'])
        m.rbox(s*.682,0,.742,.016,.246,.08,.003,mi=MI['black'])
        # Goal framing and sloped collection tunnel, open above the playfield.
        for sy in (-1,1):m.rbox(s*.662,sy*.121,.8,.077,.016,.078,.005,mi=MI['steel'])
        m.rbox(s*.697,0,.774,.068,.235,.019,.002,rot=(0,s*.23,0),mi=MI['black'])
        m.rbox(s*.751,0,.75,.012,.23,.04,.006,mi=MI['steel'])
        for sy in (-1,1):
            # Splayed steel legs, wood socket collars, threaded height adjusters.
            m.between((s*.535,sy*.283,.676),(s*.596,sy*.326,.05),.038,seg=4,mi=MI['navy'])
            m.rbox(s*.537,sy*.286,.649,.098,.088,.09,.01,mi=MI['walnut'])
            m.cylz(s*.596,sy*.326,.017,.064,.011,seg=12,mi=MI['steel'])
            m.cylz(s*.596,sy*.326,0,.022,.044,seg=18,bevel=.005,mi=MI['rubber'])
            screw(m,(s*.536,sy*.334,.642),(0,sy,0),.008)
        m.between((s*.575,-.313,.264),(s*.575,.313,.264),.018,seg=4,mi=MI['navy'])
    m.rbox(0,-.432,.75,.36,.008,.075,.006,mi=MI['black'])
    # Ball-return cup on the player's side.
    m.rbox(.44,-.436,.713,.19,.03,.059,.015,mi=MI['black'])
    m.rbox(.44,-.461,.685,.19,.071,.012,.004,mi=MI['oak'])
    m.sphere(.44,-.459,.704,.012,rings=6,seg=12,mi=MI['ivory'])
    finish(m,'FT_Cabinet_leg_frame_goal_returns',c,root)
    panel('FT_Maker_plate',(0,-.437,.75),.33,.062,'foosball_plate.png',c,parent=root)
    # Pitch markings are actual thin inlays, not floating graphic planes.
    m=mb();rectline(m,0,0,.8301,1.208,.595,.004,'ivory')
    m.rbox(0,0,.8302,.004,.596,.0013,0,mi=MI['ivory'])
    m.torus(0,0,.8302,.102,.002,ns=48,nt=4,mi=MI['ivory'])
    m.cylz(0,0,.8302,.831,.008,seg=16,mi=MI['ivory'])
    for s in (-1,1):
        rectline(m,s*.506,0,.8302,.2,.35,.0035,'ivory')
        rectline(m,s*.567,0,.8302,.08,.20,.0035,'ivory')
        m.cylz(s*.459,0,.8302,.831,.004,seg=12,mi=MI['ivory'])
        for sy in (-1,1):
            m.rbox(s*.581,sy*.281,.841,.09,.044,.023,.003,rot=(0,s*.18,0),mi=MI['field'])
    m.sphere(.206,-.067,.844,.014,rings=8,seg=16,mi=MI['ivory'])
    finish(m,'FT_Pitch_markings_ball_corner_banks',c,root)
    # Eight independent rods, bearing bushes, sprung bumpers and knurled grips.
    layout=[(-.546,1,'rust',-1),(-.411,2,'rust',-1),(-.274,3,'navy',1),(-.137,5,'rust',-1),(.137,5,'navy',1),(.274,3,'rust',-1),(.411,2,'navy',1),(.546,1,'navy',1)]
    for i,(x,n,col,side) in enumerate(layout):
        pivot=empty(f'FT_Rod_{i+1:02d}_pivot',c,(x,0,.937),root)
        pivot['axis']='local Y';pivot['players']=n
        m=mb();m.between((0,-.555,0),(0,.555,0),.0078,seg=14,mi=MI['steel'])
        for s in (-1,1):
            m.between((0,s*.348,0),(0,s*.413,0),.019,seg=16,mi=MI['black'])
            m.between((0,s*.305,0),(0,s*.332,0),.017,seg=12,mi=MI['rubber'])
            m.between((0,s*.414,0),(0,s*.426,0),.024,seg=16,mi=MI['steel'])
            for k in range(3):m.torus(0,s*(.311+k*.006),0,.017,.0016,ns=12,nt=4,rot=(math.pi/2,0,0),mi=MI['black'])
        m.between((0,side*.51,0),(0,side*.655,0),.023,seg=18,mi=MI['rubber'])
        m.between((0,side*.645,0),(0,side*.667,0),.024,seg=18,mi=MI[col])
        for k in range(7):m.torus(0,side*(.523+k*.017),0,.024,.0012,ns=16,nt=4,rot=(math.pi/2,0,0),mi=MI['black'])
        m.between((0,-side*.548,0),(0,-side*.57,0),.011,seg=12,mi=MI['rubber'])
        for k in range(n):
            y=(k-(n-1)/2)*(.128 if n==5 else .186 if n==3 else .258 if n==2 else 0)
            m.sphere(0,y,.081,.020,.019,.024,rings=6,seg=12,mi=MI[col])
            m.cylz(0,y,.047,.069,.009,seg=8,mi=MI[col])
            tapered(m,(0,y,.015),(.027,.037),(.046,.041),.068,col)
            m.rbox(-.023,y,.029,.006,.014,.016,.002,mi=MI['ivory'])
            m.rbox(0,y,-.049,.031,.027,.063,.004,mi=MI[col])
            tapered(m,(0,y,-.091),(.042,.051),(.031,.027),.021,col)
            m.rbox(0,y,-.100,.042,.051,.006,.0015,mi=MI['black'])
        finish(m,f'FT_Rod_{i+1:02d}_players_handle_bearings',c,pivot)
    # Slider scoring beads on both short ends, each on a real rod and upright brackets.
    for s in (-1,1):
        m=mb();x=s*.717
        for y in (-.29,.29):m.rbox(x,y,.943,.026,.025,.08,.004,mi=MI['black'])
        m.between((x,-.292,.976),(x,.292,.976),.004,seg=8,mi=MI['steel'])
        for k in range(10):m.between((x,-.265+k*.031,.976),(x,-.245+k*.031,.976),.016,seg=12,mi=MI['rust' if s<0 else 'navy'])
        finish(m,f'FT_Score_slider_{s}',c,root)
    for s in (-1,1):
      for t in (-1,1):empty(f'CONTACT_FT_{s}_{t}',c,(s*.596,t*.326,0),root)

def sector_mesh(name,r0,r1,a0,a1,depth,mat,c,root,steps=5):
    # Extruded sisal block. All scoring zones are correctly dimensioned and separate.
    vs=[]
    for y in (-.127,-.127-depth):
      for r in (r0,r1):
        for i in range(steps+1):
          a=a0+(a1-a0)*i/steps;vs.append((r*math.sin(a),y,r*math.cos(a)))
    n=steps+1;faces=[]
    for i in range(steps):
      faces += [(i,i+1,n+i+1,n+i),(2*n+i,3*n+i,3*n+i+1,2*n+i+1),(i,2*n+i,2*n+i+1,i+1),(n+i,n+i+1,3*n+i+1,3*n+i)]
    faces += [(0,n,3*n,2*n),(n-1,3*n-1,4*n-1,2*n-1)]
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.materials.append(MATS[MI[mat]])
    o=bpy.data.objects.new(name,me);c.objects.link(o);o.parent=root;o['support']='assembly';return o

def dartboard(c,root):
    # Bull's-eye is the origin; the mounting back plane is y=0. Floor height set on import.
    m=mb();m.rbox(0,-.033,0,.61,.066,.72,.009,mi=MI['walnut'])
    m.rbox(0,-.069,0,.548,.008,.642,.002,mi=MI['black'])
    for s in (-1,1):
      m.rbox(s*.298,-.089,0,.028,.13,.72,.007,mi=MI['oak'])
      m.rbox(0,-.089,s*.346,.59,.13,.026,.006,mi=MI['oak'])
      # Open shutter, supported by metal hinges along the cabinet jamb.
      m.rbox(s*.458,-.062,0,.274,.038,.715,.009,rot=(0,0,s*.15),mi=MI['walnut'])
      for z in (-.237,.237):
        m.between((s*.309,-.077,z-.022),(s*.309,-.077,z+.022),.005,seg=12,mi=MI['steel'])
        m.rbox(s*.311,-.082,z,.054,.008,.026,.002,mi=MI['steel'])
      m.rbox(s*.4614,-.08475,0,.240,.004,.654,.002,rot=(0,0,s*.15),mi=MI['black'])
    m.rbox(0,-.139,-.307,.538,.117,.038,.009,mi=MI['oak'])
    m.rbox(0,-.111,.405,.4,.023,.073,.009,mi=MI['black'])
    finish(m,'DB_Walnut_cabinet_open_doors_hinges',c,root)
    panel('DB_House_league_plaque',(0,-.125,.405),.38,.062,'dart_plaque.png',c,parent=root)
    panel('DB_Home_chalk',(-.4621,-.0897,0),.223,.63,'chalk_left.png',c,rot=(0,0,-.15),parent=root)
    panel('DB_Away_chalk',(.4621,-.0897,0),.223,.63,'chalk_right.png',c,rot=(0,0,.15),parent=root)
    m=mb();m.add(p_cyl(.226,.038,96),loc=(0,-.108,0),rot=(math.pi/2,0,0),mi=MI['black'])
    m.torus(0,-.132,0,.220,.003,ns=96,nt=4,rot=(math.pi/2,0,0),mi=MI['steel'])
    finish(m,'DB_Board_body_mount_and_outer_wire',c,root)
    sequence=[20,1,18,4,13,6,10,15,2,17,3,19,7,16,8,11,14,9,12,5]
    for i,n in enumerate(sequence):
      a=i*TAU/20;lo=a-math.pi/20+.0018;hi=a+math.pi/20-.0018
      for j,(r0,r1) in enumerate([(.016,.0985),(.099,.107),(.1075,.1615),(.162,.170)]):
        mat=('sisalblack' if i%2==0 else 'sisalcream') if j in (0,2) else ('sisalred' if i%2==0 else 'sisalgreen')
        sector_mesh(f'DB_{n:02d}_'+['single_inner','triple','single_outer','double'][j],r0,r1,lo,hi,.003,mat,c,root,5)
    m=mb()
    # An annular outer bull surrounds the inner plug; no overlapping front disks.
    annulus=p_lathe([(.00635,-.002),(.0158,-.002),(.0158,.002),(.00635,.002)],seg=40,close=False)
    vs=list(annulus.verts)
    # Close the inner cylindrical wall; the helper's close=True would fill the hole.
    for i in range(40):annulus.faces.new((vs[120+i],vs[120+(i+1)%40],vs[(i+1)%40],vs[i]))
    bmesh.ops.recalc_face_normals(annulus,faces=annulus.faces[:])
    m.add(annulus,loc=(0,-.131,0),rot=(math.pi/2,0,0),mi=MI['sisalgreen'])
    m.add(p_cyl(.00635,.004,40),loc=(0,-.131,0),rot=(math.pi/2,0,0),mi=MI['sisalred'])
    # Razor wire divisions: radius and angular boundaries correspond to the modeled sectors.
    for r in (.00635,.0158,.099,.107,.162,.170):m.torus(0,-.133,0,r,.00075,ns=80,nt=4,rot=(math.pi/2,0,0),mi=MI['steel'])
    for i in range(20):
      a=(i+.5)*TAU/20
      m.between((.016*math.sin(a),-.133,.016*math.cos(a)),(.17*math.sin(a),-.133,.17*math.cos(a)),.0007,seg=4,mi=MI['steel'])
    finish(m,'DB_Bulls_and_staple_free_spider',c,root)
    # Raised metal numerals, with editable text retained in the standalone source.
    font=bpy.data.fonts.load('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    for i,n in enumerate(sequence):
      a=i*TAU/20;cu=bpy.data.curves.new(f'DB_number_{n}','FONT');cu.body=str(n);cu.font=font;cu.size=.026;cu.align_x='CENTER';cu.align_y='CENTER';cu.extrude=.0005;cu.resolution_u=3
      cu.materials.append(MATS[MI['ivory']]);o=bpy.data.objects.new(cu.name,cu);c.objects.link(o);o.parent=root
      o.location=(.195*math.sin(a),-.135,.195*math.cos(a));o.rotation_euler=(math.pi/2,0,0);o['support']='assembly'
    # Three darts, one embedded in the 20 triple, two resting in the cabinet ledge.
    for i,(p,d,col) in enumerate([((.002,-.136,.103),(.015,-.15,.016),'rust'),((-.13,-.19,-.28),(.12,.008,.01),'navy'),((.03,-.19,-.28),(.12,.008,.01),'rust')]):
      m=mb();p=Vector(p);d=Vector(d);u=d.normalized();m.between(p,p+u*.023,.0007,seg=6,mi=MI['steel'])
      m.between(p+u*.023,p+u*.06,.0042,seg=12,r2=.003,mi=MI['steel'])
      for k in range(5):
        q=p+u*(.027+k*.005);m.between(q,q+u*.0018,.0048,seg=10,mi=MI['black'])
      m.between(p+u*.06,p+u*.105,.0018,seg=8,mi=MI['black'])
      # Four flight fins oriented along the actual shaft, rather than arbitrary flat crosses.
      q=Vector((0,0,1)).rotation_difference(u).to_matrix()
      for k in range(4):
        a=k*math.pi/2;rad=Vector((math.cos(a),math.sin(a),0))
        pts=[(0,0,.091),tuple(rad*.012+Vector((0,0,.095))),tuple(rad*.014+Vector((0,0,.121))),(0,0,.117)]
        pb=bmesh.new();v=[pb.verts.new(p+q@Vector(t)) for t in pts];pb.faces.new(v);m.add(pb,mi=MI[col])
      finish(m,f'DB_Dart_{i+1}_barrel_shaft_flights',c,root)
    empty('CONTACT_DB_MOUNT',c,(0,0,0),root)

def ball_mesh(m,p):
    x,y,z=p;r=.101;m.sphere(x,y,z,r,r,r,rings=10,seg=20,mi=MI['ball'])
    for rot in [(0,0,0),(math.pi/2,0,0),(0,math.pi/2,0)]:m.torus(x,y,z,r+.00015,.0018,ns=36,nt=4,rot=rot,mi=MI['black'])

def basketball(c,root):
    # One independent cabinet: front faces -Y. Paired cabinets are imported separately.
    W=.99;front=-1.065;back=1.065
    m=mb()
    m.rbox(0,0,.114,W,2.18,.115,.009,mi=MI['black'])
    m.rbox(0,0,.26,.882,2.07,.18,.006,mi=MI['navy'])
    # Folded side cheeks use an authored profile with a rising return channel.
    pts=[(-1.06,.27),(-1.06,.7),(-.94,.82),(.77,1.10),(1.08,1.30),(1.08,.27)]
    for s in (-1,1):
      pb=p_ring_prism(pts,.056,.003)
      # Profile local x->Y, y->Z, extrusion->X.
      for v in pb.verts:v.co=Vector((s*(.44+v.co.z),v.co.x,v.co.y))
      m.add(pb,mi=MI['navy'])
      m.between((s*.435,-.99,.823),(s*.435,.90,1.115),.015,seg=10,mi=MI['steel'])
      for y in (-.85,.84):
        m.cylz(s*.365,y,.02,.101,.009,seg=10,mi=MI['steel']);m.cylz(s*.365,y,0,.027,.037,seg=14,bevel=.003,mi=MI['rubber'])
      for y in (-.8,.75):screw(m,(s*.499,y,.41),(s,0,0),.006)
    m.rbox(0,front,.429,.875,.034,.365,.005,mi=MI['rust'])
    m.rbox(0,front-.02,.394,.61,.005,.221,.002,mi=MI['navy'])
    m.rbox(0,front-.026,.421,.042,.007,.081,.002,mi=MI['steel'])
    m.rbox(0,front-.032,.44,.024,.003,.003,0,mi=MI['black'])
    for x in (-.27,.27):screw(m,(x,front-.027,.39),(0,-1,0),.005)
    # Actual rear service panel, latch, intake slots, and a power cable.
    m.rbox(0,back,.60,.874,.04,.641,.004,mi=MI['black'])
    m.rbox(0,back+.023,.57,.64,.012,.43,.004,mi=MI['navy'])
    for z in (.46,.50,.54,.58):m.rbox(0,back+.031,z,.42,.004,.012,.002,mi=MI['black'])
    m.rbox(.259,back+.039,.63,.017,.016,.064,.003,mi=MI['steel'])
    finish(m,'BB_Folded_cabinet_levellers_service_panels',c,root)
    # Graphics on both sides of the chassis.
    for s in (-1,1):
      panel(f'BB_Side_art_{s}',(s*.5,-.14,.56),1.61,.46,'basket_side.png',c,rot=(0,0,s*math.pi/2),parent=root)
    m=mb()
    # Sloping ball-return ramp from the high rear trough to the front well.
    m.rbox(0,-.035,.79,.805,1.874,.034,.004,rot=(.154,0,0),mi=MI['black'])
    for x in (-.26,0,.26):m.rbox(x,-.035,.811,.018,1.80,.014,.004,rot=(.154,0,0),mi=MI['steel'])
    m.rbox(0,-.893,.705,.79,.295,.052,.011,mi=MI['rust'])
    m.between((-.445,-1.04,.81),(.445,-1.04,.81),.018,seg=14,mi=MI['rubber'])
    for x in (-.435,.435):
      m.between((x,.98,.96),(x,.98,2.39),.021,seg=12,mi=MI['navy'])
      m.between((x,-.91,.85),(x,-.91,1.34),.018,seg=12,mi=MI['navy'])
      m.between((x,-.91,1.34),(x,.98,2.39),.018,seg=12,mi=MI['navy'])
      m.between((x,-.91,.96),(x,.98,1.225),.015,seg=10,mi=MI['navy'])
    m.between((-.435,.98,2.39),(.435,.98,2.39),.021,seg=12,mi=MI['navy'])
    m.between((-.435,.98,1.2),(.435,.98,1.2),.018,seg=12,mi=MI['navy'])
    finish(m,'BB_Return_ramp_channels_tubular_frame',c,root)
    # Mesh side containment, spaced sufficiently to read as wire rather than a solid wall.
    m=mb()
    for x in (-.429,.429):
      for k in range(13):
        y=-.90+k*.156;top=1.34+(y+.91)*1.05/1.89
        m.between((x,y,1.01+(y+.91)*.14),(x,y,top-.015),.0016,seg=4,mi=MI['black'])
      for k in range(5):
        z=1.09+k*.14;ymin=max(-.90,-.91+(z-1.34)*1.89/1.05)
        m.between((x,ymin,z),(x,.96,z),.0016,seg=4,mi=MI['black'])
      for k in range(4):
        z=1.85+k*.12;ymin=-.91+(z-1.34)*1.89/1.05
        m.between((x,ymin,z),(x,.96,z),.0016,seg=4,mi=MI['black'])
    for k in range(12):
      x=-.39+k*.071;m.between((x,.992,1.24),(x,.992,2.36),.0015,seg=4,mi=MI['black'])
    for k in range(9):m.between((-.413,.992,1.3+k*.12),(.413,.992,1.3+k*.12),.0015,seg=4,mi=MI['black'])
    finish(m,'BB_Welded_safety_mesh',c,root)
    m=mb()
    m.rbox(0,.879,2.076,.811,.047,.46,.016,mi=MI['ivory'])
    m.rbox(0,.851,2.076,.762,.008,.411,.009,mi=MI['navy'])
    m.rbox(0,.846,2.079,.728,.004,.379,.005,mi=MI['ivory'])
    # Target rectangle mounted immediately behind the basket.
    for z in (1.969,2.114):m.rbox(0,.841,z,.24,.008,.012,.002,mi=MI['rust'])
    for x in (-.114,.114):m.rbox(x,.841,2.041,.012,.008,.15,.002,mi=MI['rust'])
    for x in (-.352,.352):
      for z in (1.91,2.245):screw(m,(x,.839,z),(0,-1,0),.005)
    m.rbox(0,.793,1.935,.12,.129,.027,.004,mi=MI['rust'])
    m.torus(0,.609,1.935,.166,.012,ns=52,nt=6,mi=MI['rust'])
    m.rbox(0,.77,1.982,.092,.033,.09,.003,mi=MI['steel'])
    # A shot sensor with a visible cable and metal retaining bracket.
    m.rbox(-.188,.605,1.944,.025,.048,.035,.004,mi=MI['black'])
    m.cylz(-.192,.604,1.961,1.968,.006,seg=10,mi=MI['redled'])
    finish(m,'BB_Backboard_rim_shot_sensor',c,root)
    # Hanging knotted diamond net, tapered naturally toward the open bottom.
    m=mb();N=12;rows=[]
    for j in range(5):
      radius=.161-j*.0175;z=1.924-j*.061
      rows.append([(radius*math.cos(TAU*k/N+(j%2)*math.pi/N),.609+radius*math.sin(TAU*k/N+(j%2)*math.pi/N),z) for k in range(N)])
    for j in range(4):
      for k in range(N):
        m.between(rows[j][k],rows[j+1][k],.0019,seg=4,mi=MI['rope'])
        m.between(rows[j][k],rows[j+1][(k-1 if j%2==0 else k+1)%N],.0019,seg=4,mi=MI['rope'])
    for k in range(N):m.sphere(*rows[2][k],.003,rings=4,seg=6,mi=MI['rope'])
    finish(m,'BB_Diamond_knotted_basket_net',c,root)
    m=mb()
    m.rbox(0,1.016,2.518,1.016,.172,.288,.025,mi=MI['rust'])
    m.rbox(0,.924,2.518,.935,.014,.22,.013,mi=MI['black'])
    m.rbox(0,.875,1.405,.79,.04,.21,.008,mi=MI['navy'])
    m.rbox(0,.849,1.405,.731,.006,.16,.003,mi=MI['black'])
    finish(m,'BB_Marquee_and_score_enclosure',c,root)
    panel('BB_Marquee',(0,.914,2.518),.911,.205,'basket_marquee.png',c,parent=root,lit=.8)
    # Physical seven-segment LEDs, with unused segments present but dark.
    m=mb();patterns={0:'abcdef',2:'abged',3:'abgcd',4:'fgbc',5:'afgcd',6:'afgecd',8:'abcdefg'}
    for digit,(x,n) in enumerate([(-.267,0),(-.172,8),(.147,6),(.24,0)]):
      segs={'a':(0,.051,.05,.009),'g':(0,0,.05,.009),'d':(0,-.051,.05,.009),'f':(-.029,.028,.009,.043),'b':(.029,.028,.009,.043),'e':(-.029,-.028,.009,.043),'c':(.029,-.028,.009,.043)}
      for key,(dx,dz,w,h) in segs.items():m.rbox(x+dx,.844,1.405+dz,w,.007,h,.003,mi=MI['redled' if key in patterns[n] else 'black'])
    m.rbox(0,.842,1.43,.009,.005,.009,.003,mi=MI['redled']);m.rbox(0,.842,1.382,.009,.005,.009,.003,mi=MI['redled'])
    m.rbox(0,-1.081,.616,.69,.049,.108,.015,rot=(.15,0,0),mi=MI['black'])
    m.cylz(.302,-.90,.847,.884,.025,seg=20,bevel=.004,mi=MI['led'])
    finish(m,'BB_Seven_segment_score_timer_and_start',c,root)
    panel('BB_Control_instructions',(0,-1.11,.618),.645,.081,'basket_control.png',c,parent=root,lit=.2)
    m=mb()
    for p in [(-.24,-.88,.806),(.05,-.90,.806),(.24,-.65,.853),(-.1,.24,.987)]:ball_mesh(m,p)
    finish(m,'BB_Four_seamed_basketballs',c,root)
    curve('BB_Mains_cable',[(.29,1.09,.36),(.32,1.12,.20),(.34,1.11,.08),(.31,1.0,.045)],.006,'rubber',c,root,res=1)
    for x in (-.365,.365):
      for y in (-.85,.84):empty(f'CONTACT_BB_{x}_{y}',c,(x,y,0),root)

if __name__=='__main__':
    argv=sys.argv[sys.argv.index('--')+1:];kind=argv[0]
    bpy.ops.wm.read_factory_settings(use_empty=True);palette()
    sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
    c=collection('ASSET_'+kind.upper());root=empty(kind.upper()+'_ROOT',c)
    root['asset_kind']=kind;root['origin_description']='bullseye / mounting back' if kind=='dartboard' else 'floor centre';root['authoring_units']='metres'
    globals()[kind](c,root);bpy.context.view_layer.update()
    report={'kind':kind,'triangles':triangles(c.all_objects),'bounds_m':bounds(c.all_objects),'components':len(c.all_objects),'source':'build_assets.py','blender':bpy.app.version_string}
    c['asset_report']=json.dumps(report);print('ASSET_REPORT',json.dumps(report),flush=True)
    studio(c,root,kind);render_settings(32,(1200,1000));pack()
    out=HERE/'assets';out.mkdir(exist_ok=True);renders=HERE/'renders'/'assets';renders.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/(kind+'.blend')),compress=True)
    (out/(kind+'.json')).write_text(json.dumps(report,indent=2))
    if '--no-render' not in argv:
      sc.render.filepath=str(renders/(kind+'.png'));bpy.ops.render.render(write_still=True)
    print('BUILT',kind,flush=True)
