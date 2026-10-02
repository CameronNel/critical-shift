"""Authored assembly recipes. Geometry carries identity; shaders finish it."""
import math
from mathutils import Matrix, Vector
from fuel_kit import B, mat, frame, bolt, ring, polygon, rounded_path, wear, channel,merge

def instrument_dial(b,x,y,z,r=.085):
    rot=Matrix.Rotation(math.pi/2,3,'X')
    b.lathe([(0,0),(r*.91,0),(r,.010),(r,.044),(r*.88,.055),
             (r*.80,.055),(r*.80,.050),(0,.050)],(x,y,z),mat('steel'),seg=48,rot=rot)
    b.cyl(r*.79,.001,(x,y-.051,z),mat('paper'),seg=48,axis='Y')
    for i in range(17):
        a=math.radians(30+i*18)
        rr=r*.64
        b.tube([(x+rr*math.cos(a),y-.0525,z+rr*math.sin(a)),
                (x+(rr-r*.10)*math.cos(a),y-.0525,z+(rr-r*.10)*math.sin(a))],
               .0012 if i%4 else .0018,mat('ink'),seg=6)
    b.tube([(x+r*.10,y-.054,z-r*.065),(x-r*.49,y-.054,z+r*.30)],.0018,mat('red'),seg=8)
    b.cyl(r*.050,.003,(x,y-.054,z),mat('dark steel'),seg=16,axis='Y')
    b.lathe([(0,0),(r*.79,0),(r*.79,.002),(0,.002)],(x,y-.056,z),mat('glass'),seg=48,rot=rot)

def fuel_conditioner():
    """Supported twin filter/skimmer bank with connected purge and drain headers."""
    b=B();steel=mat('dark steel');w=1.76
    for x in [-.78,.78]:
        channel(b,.095,.075,1.78,(x,-.012,.89),steel)
        for z in [.13,1.65]:
            b.box((.13,.022,.135),(x,-.011,z),steel,.003)
            for zz in [z-.044,z+.044]:bolt(b,(x,-.029,zz),.007)
    for z in [.08,1.73]:b.box((w,.065,.095),(0,-.045,z),mat('navy enamel'),.006)
    # An open drip tray has folded returns and two real cantilever brackets.
    b.box((1.63,.40,.016),(0,-.205,.052),mat('replacement enamel'),.003)
    for x in [-.81,.81]:b.box((.018,.40,.08),(x,-.205,.085),mat('replacement enamel'),.003)
    b.box((1.63,.016,.074),(0,-.398,.086),mat('replacement enamel'),.003)
    for x in [-.63,.63]:
        polygon(b,[(0,0),(-.33,0),(0,-.14)],.018,steel,pos=(x,0,.06),
                rot=Matrix.Rotation(math.pi/2,3,'Y')@Matrix.Rotation(math.pi/2,3,'Z'))
    # Two formed pressure bowls, rolled end caps and separate clamped joints.
    for i,x in enumerate([-.36,.36]):
        profile=[(0,0),(.06,0),(.104,.034),(.119,.086),(.12,.95),(.109,1.005),(.06,1.035),(0,1.035)]
        b.lathe(profile,(x,-.215,.355),mat('warm enamel' if i==0 else 'repaired blue enamel'),seg=48)
        for z in [.45,1.265]:
            b.lathe([(.116,0),(.13,0),(.133,.010),(.13,.037),(.116,.037),(.116,0)],(x,-.215,z),mat('steel'),seg=48)
            for a in [0,math.pi/2,math.pi,3*math.pi/2]:
                bolt(b,(x+.115*math.cos(a),-.215+.115*math.sin(a),z+.039),.006,axis='Z')
        for z in [.67,1.12]:
            b.box((.29,.12,.040),(x,-.060,z),steel,.004)
            b.lathe([(.119,0),(.128,0),(.128,.026),(.119,.026),(.119,0)],(x,-.215,z),mat('navy enamel'),seg=40)
        b.cyl(.022,.165,(x,-.215,1.391),mat('brass'),seg=20)
        b.cyl(.020,.077,(x,-.215,.282),mat('brass'),seg=20)
        # Front process ID is attached to a real curved stand-off plate.
        b.box((.115,.012,.055),(x,-.332,.80),mat('ink enamel'),.004)
        for xx in [x-.049,x+.049]:bolt(b,(xx,-.340,.80),.0035)
    for z in [.282,1.53]:
        b.tube([(-.70,-.215,z),(.69,-.215,z)],.029,mat('steel'),seg=24)
        for x in [-.60,0,.59]:ring(b,.040,.027,(x,-.215,z),mat('brass'),axis='X',seg=24)
    b.tube(rounded_path([(-.69,-.215,.282),(-.75,-.215,.36),(-.75,-.215,1.53),(-.69,-.215,1.53)]),.026,mat('steel'),seg=24)
    # Inlet rises from the bank and has real wall saddle clamps along its height.
    b.tube(rounded_path([(-.69,-.215,1.53),(-.71,-.215,1.65),(-.71,-.13,3.06),(-.65,-.13,3.16),(.11,-.13,3.16)]),.029,mat('steel'),seg=24)
    for z in [1.97,2.47]:
        b.box((.14,.025,.10),(-.71,-.0125,z),steel,.003)
        b.box((.07,.12,.025),(-.71,-.075,z),steel,.003)
        ring(b,.036,.010,(-.71,-.13,z-.005),mat('brass'),seg=24)
        for xx in [-.76,-.66]:bolt(b,(xx,-.029,z),.006)
    # Isolation bonnet/handwheel and a connected analog pressure dial.
    b.cyl(.014,.075,(.59,-.250,1.53),mat('brass'),seg=20,axis='Y')
    b.lathe([(0,0),(.028,0),(.037,.012),(.027,.043),(.014,.054),(0,.054)],(.59,-.245,1.53),mat('brass'),seg=24,rot=Matrix.Rotation(math.pi/2,3,'X'))
    b.tube([(.59+.08*math.cos(i*2*math.pi/36),-.326,1.53+.08*math.sin(i*2*math.pi/36)) for i in range(37)],.008,mat('ochre enamel'),seg=10)
    for a in [0,2.094,4.189]:b.tube([(.59,-.326,1.53),(.59+.075*math.cos(a),-.326,1.53+.075*math.sin(a))],.006,mat('ochre enamel'),seg=8)
    b.tube([(.11,-.215,1.53),(.11,-.215,1.65)],.011,mat('brass'),seg=16)
    instrument_dial(b,.11,-.222,1.72,.086)
    # A single retained hose with a closed quick-release end, not loose clutter.
    b.tube(rounded_path([(.69,-.215,.282),(.76,-.30,.23),(.70,-.31,.16),(.45,-.31,.12),(.08,-.31,.15),(-.15,-.31,.24),(-.20,-.28,.32)]),.014,mat('rubber'),seg=16)
    b.lathe([(0,0),(.019,0),(.025,.009),(.025,.03),(.016,.044),(0,.044)],(-.20,-.28,.32),mat('brass'),seg=24)
    wear(b,(-.66,-.408,.096),(1,0,0),.16,.002,7)
    return b

def extraction_header(length=3.5):
    """Hollow sheet-metal horizontal duct with folded seams and service hatch."""
    b=B();w=length;d=.31;h=.27
    for y in [-.032,-d]:b.box((w,.018,h),(0,y,0),mat('replacement enamel'),.003)
    for z in [-h/2,h/2]:b.box((w,d-.018,.018),(0,-d/2-.009,z),mat('replacement enamel'),.003)
    for x in [-w/2+.014,0,w/2-.014]:
        # The four sides form a hollow flange rather than a solid plate through the duct.
        for z in [-h/2-.012,h/2+.012]:b.box((.03,d+.05,.024),(x,-d/2,z),mat('steel'),.003)
        for y in [-d-.015,.007]:b.box((.03,.024,h+.025),(x,y,0),mat('steel'),.003)
        for z in [-h/2-.010,h/2+.010]:bolt(b,(x,-d-.030,z),.006)
    for x in [-w*.32,w*.32]:
        b.box((.14,.030,.39),(x,-.015,0),mat('dark steel'),.003)
        b.box((.11,.34,.022),(x,-.17,-.195),mat('dark steel'),.003)
        for z in [-.155,.155]:bolt(b,(x,-.034,z),.008)
    frame(b,.59,.18,.012,.012,-d-.008,0,mat('dark steel'),r=.014)
    b.box((.555,.015,.145),(0,-d-.009,0),mat('warm enamel'),.004)
    for x in [-.25,.25]:bolt(b,(x,-d-.020,0),.005)
    return b

def protective_kit():
    """Open PPE rack with a draped canvas apron, straps, mask and gloves."""
    b=B();steel=mat('dark steel')
    for x in [-.29,.29]:
        b.box((.07,.020,.14),(x,-.010,.75),steel,.003)
        for z in [.71,.79]:bolt(b,(x,-.023,z),.006)
    b.tube([(-.33,-.085,.76),(.33,-.085,.76)],.013,steel,seg=16)
    for x in [-.22,.20]:b.tube(rounded_path([(x,-.04,.76),(x,-.12,.76),(x,-.135,.68),(x,-.08,.65)]),.007,mat('steel'),seg=12)
    # Panels follow sagged folds; bound seams and pockets are actual geometry.
    profile=[(-.205,0),(-.16,-.018),(-.09,-.005),(-.03,-.025),(.04,-.016),(.12,-.032),(.20,-.019)]
    cloth=[];grid=[]
    for layer in [0,1]:
        rows=[]
        for z in [.03,.16,.30,.43,.55]:
            row=[]
            for x,y in profile:
                v=b.bm.verts.new((x*(1-.20*z/.55),-.13+y*(1+.4*z/.55)+layer*.003,z))
                row.append(v);cloth.append(v)
            rows.append(row)
        grid.append(rows)
    for layer in [0,1]:
        for j in range(4):
            for i in range(6):
                vs=[grid[layer][j][i],grid[layer][j][i+1],grid[layer][j+1][i+1],grid[layer][j+1][i]]
                b.bm.faces.new(vs if layer==0 else list(reversed(vs)))
    for j in range(4):
        for i in [0,6]:b.bm.faces.new([grid[0][j][i],grid[1][j][i],grid[1][j+1][i],grid[0][j+1][i]])
    for j in [0,4]:
        for i in range(6):b.bm.faces.new([grid[0][j][i],grid[0][j][i+1],grid[1][j][i+1],grid[1][j][i]])
    b._fin(cloth,mat('canvas'),True)
    b.tube([(-.20,-.130,.035),(-.09,-.142,.024),(.04,-.15,.031),(.20,-.15,.025)],.003,mat('leather'),seg=8)
    for x in [-.20,.20]:b.tube([(x,-.135,.04),(x,-.135,.55)],.003,mat('leather'),seg=8)
    b.tube(rounded_path([(-.15,-.14,.55),(-.11,-.13,.66),(0,-.085,.73),(.10,-.13,.65),(.15,-.14,.55)]),.012,mat('canvas'),seg=12)
    b.box((.16,.012,.13),(-.02,-.174,.24),mat('cotton'),.007)
    b.tube([(-.10,-.183,.30),(.06,-.183,.30)],.002,mat('canvas'),seg=8)
    # A moulded half-mask has a shaped central seal and two filter cassettes.
    b.sph(1,(.22,-.13,.58),mat('rubber'),scale=(.066,.041,.053),seg=32,ring=20)
    for x in [.18,.26]:
        b.lathe([(0,0),(.029,0),(.032,.007),(.032,.025),(.026,.034),(0,.034)],(x,-.17,.58),mat('warm enamel'),seg=32,rot=Matrix.Rotation(math.pi/2,3,'X'))
        for j in range(4):b.box((.034,.002,.002),(x,-.205,.567+j*.008),mat('ink'),.0002)
    b.tube(rounded_path([(.17,-.11,.60),(.14,-.10,.69),(.20,-.08,.75),(.28,-.10,.67),(.28,-.11,.59)]),.006,mat('rubber'),seg=10)
    return b

def linen_rack():
    """Open clean-transfer storage: shaped frame, cloth, paper and supply bottles."""
    b=B();coat=mat('navy enamel');w=.88
    for x in [-.40,.40]:
        for y in [-.055,-.29]:
            b.box((.045,.042,1.51),(x,y,.785),coat,.006)
            b.box((.067,.061,.030),(x,y,.015),mat('rubber'),.006)
            b.lathe([(0,0),(.030,0),(.030,.008),(.025,.016),(0,.016)],(x,y,1.538),mat('steel'),seg=24)
    for z in [.16,.68,1.20,1.49]:
        b.box((w,.34,.022),(0,-.17,z),mat('replacement enamel'),.003)
        b.box((w-.018,.016,.056),(0,-.325,z+.017),coat,.004)
        for x in [-.424,.424]:b.box((.017,.33,.048),(x,-.17,z+.016),coat,.003)
    b.box((.76,.017,.30),(0,-.039,1.365),mat('wood'),.006)
    # Folded stacks show rounded compression, stitched edges and alternate cloth.
    for x,z in [(-.225,.704),(.15,1.224),(-.19,1.224)]:
        for i in range(3):
            b.pillow(.265,.228,.043,(x,-.173,z+i*.037),mat('canvas' if i%2==0 else 'cotton'),n=9,seam=.002)
    # A canvas supply bag occupies the lowest shelf with a soft lid and real straps.
    b.pillow(.40,.255,.265,(-.15,-.18,.308),mat('canvas'),n=11,seam=.003)
    for x in [-.27,-.03]:
        b.tube(rounded_path([(x,-.302,.23),(x,-.312,.43),(x,-.26,.447),(x,-.07,.43)]),.009,mat('leather'),seg=12)
        b.box((.035,.012,.049),(x,-.323,.30),mat('steel'),.004)
    # Lathed refill bottles have moulded shoulders, recessed caps and bent spouts.
    for x in [.11,.28]:
        b.lathe([(0,0),(.040,0),(.047,.007),(.047,.16),(.039,.188),(.017,.207),(.017,.235),(0,.235)],(x,-.18,.702),mat('warm enamel'),seg=32)
        ring(b,.023,.021,(x,-.18,.91),mat('navy enamel'),seg=24)
        b.tube(rounded_path([(x,-.18,.944),(x,-.18,.969),(x,-.22,.974),(x,-.25,.963)]),.005,mat('dark steel'),seg=12)
        b.box((.053,.007,.071),(x,-.227,.79),mat('oxide enamel'),.003)
    b.box((.35,.004,.073),(0,-.053,1.37),mat('ink enamel'),.003)
    for x in [-.34,.34]:
        for z in [.58,1.04]:
            bolt(b,(x,-.041,z),.006)
    return b

def clean_log_board():
    b=B();frame(b,.90,.72,.035,.028,-.014,.36,mat('navy enamel'),r=.025)
    b.box((.84,.014,.66),(0,-.033,.36),mat('warm enamel'),.004)
    for x in [-.385,.385]:
        for z in [.072,.648]:bolt(b,(x,-.043,z),.006)
    # Real inspection sheet and envelope tray; the route drawing is raised ink.
    merge(b,clipboard(),(-.21,-.051,.32),Matrix.Rotation(math.pi/2,3,'X'))
    for z in [.21,.34,.47]:
        b.box((.055,.002,.037),(.25,-.043,z),mat('navy enamel'),.003)
    b.tube([(.25,-.045,.21),(.25,-.045,.47)],.003,mat('ink'),seg=8)
    b.box((.11,.015,.021),(.09,-.052,.09),mat('dark steel'),.003)
    b.cyl(.010,.14,(.09,-.060,.091),mat('ochre enamel'),seg=16,axis='X')
    b.box((.33,.020,.044),(.20,-.056,.62),mat('ink enamel'),.003)
    return b

def tool_case(w=.38,d=.25,h=.18,opened=False):
    b=B();coat=mat('oxide enamel');edge=mat('dark steel')
    # Folded open shell, rolled rim, inset removable lid and split catch hardware.
    b.box((w,d,.016),(0,0,.008),coat,.004)
    for x in [-w/2+.008,w/2-.008]:b.box((.016,d,h-.025),(x,0,h/2),coat,.005)
    for y in [-d/2+.008,d/2-.008]:b.box((w-.02,.016,h-.025),(0,y,h/2),coat,.005)
    b.box((w-.020,d-.020,.090 if opened else .009),(0,0,.068 if opened else h-.014),mat('rubber'),.003)
    for s in [-1,1]:
        x=s*w*.31
        b.box((.047,.010,.058),(x,-d/2-.008,h-.025),mat('brass'),.005)
        b.box((.033,.010,.024),(x,-d/2-.016,h-.007),edge,.003)
        b.cyl(.009,.040,(x-.02,-d/2-.019,h+.003),mat('steel'),seg=16,axis='X')
        b.lathe([(.012,0),(.012,.018),(.007,.021),(.007,.023)],(x,d/2-.012,h-.011),edge,seg=16,rot=Matrix.Rotation(math.pi/2,3,'Y'))
        b.box((.048,.043,.045),(s*(w/2-.016),-d/2+.016,.029),mat('rubber'),.009)
        b.box((.048,.043,.045),(s*(w/2-.016),d/2-.016,.029),mat('rubber'),.009)
    before=set(b.bm.verts)
    b.box((w+.005,d+.005,.018),(0,0,h+.003),coat,.006)
    b.tube(rounded_path([(-.07,0,h+.019),(-.07,0,h+.055),(-.05,0,h+.071),(.05,0,h+.071),(.07,0,h+.055),(.07,0,h+.019)]),.010,edge,seg=12)
    b.box((w-.033,d-.033,.006),(0,0,h-.009),mat('replacement enamel'),.002)
    if opened:
        pivot=Vector((0,d/2,h));r=Matrix.Rotation(-1.35,3,'X')
        for v in b.bm.verts:
            if v not in before:v.co=pivot+r@(v.co-pivot)
        for i in range(5):
            x=-w*.34+i*w*.165;r=.012+i*.002
            if i!=1:
                hh=.040+i*.009
                b.lathe([(r*.55,0),(r,0),(r,hh),(r*.55,hh),(r*.55,0)],(x,-.027,.114),mat('steel'),seg=24)
            else:
                b.lathe([(.006,0),(.014,0),(.014,.002),(.006,.002),(.006,0)],(x,-.027,.114),mat('ink'),seg=24)
            for y in [-d*.28,d*.15]:b.box((.028,.018,.018),(x,y,.118),mat('rubber'),.002)
    b.box((.095,.004,.034),(0,-d/2-.011,h*.49),mat('warm enamel'),.002)
    for x in [-.042,.042]:bolt(b,(x,-d/2-.014,h*.49),.0035)
    wear(b,(-.12,-d/2-.011,h-.058),(1,0,0),.15,.003,8)
    return b

def carrier():
    b=B();steel=mat('dark steel');paint=mat('ochre enamel')
    polygon(b,[(-.76,-.28),(-.69,-.37),(.69,-.37),(.76,-.28),(.76,.28),(.69,.37),(-.69,.37),(-.76,.28)],.032,steel,pos=(0,0,.285))
    for y in [-.325,.325]:
        b.box((1.4,.05,.085),(0,y,.26),steel,.006)
        b.box((1.24,.012,.034),(0,y-.031,.255),paint,.003)
    for x in [-.61,.61]:
        for y in [-.29,.29]:
            rot=Matrix.Rotation(math.pi/2,3,'X')
            b.lathe([(.038,0),(.067,0),(.083,.007),(.085,.022),(.085,.046),(.079,.063),(.038,.065),(.038,0)],(x,y+.0325,.085),mat('rubber'),seg=32,rot=rot)
            b.lathe([(0,0),(.025,0),(.037,.005),(.038,.014),(.025,.019),(0,.019)],(x,y-.034,.085),mat('steel'),seg=24,rot=rot)
            for side in [-1,1]:
                polygon(b,[(-.050,0),(.050,0),(.028,.136),(-.017,.14)],.015,steel,
                        pos=(x,y+side*.045,.084),rot=Matrix.Rotation(math.pi/2,3,'X'))
            b.cyl(.052,.019,(x-.01,y,.22),steel,seg=24)
            b.cyl(.022,.058,(x-.01,y,.237),mat('steel'),seg=20)
            if x<0:
                b.box((.07,.06,.015),(x-.055,y,.185),paint,.004,rot=Matrix.Rotation(.28,3,'Y'))
    # Cast saddles hug the specified reactor-size cartridge, with rubber inserts.
    for x in [-.43,.43]:
        rot=Matrix.Rotation(math.pi/2,3,'Y')@Matrix.Rotation(math.pi/2,3,'Z')
        def saddle(r1,r2):
            a=[(r1*math.cos(math.pi+math.pi*i/20),.725+r1*math.sin(math.pi+math.pi*i/20)) for i in range(21)]
            a += [(r2*math.cos(2*math.pi-math.pi*i/20),.725+r2*math.sin(2*math.pi-math.pi*i/20)) for i in range(21)]
            return a
        polygon(b,saddle(.157,.196),.068,paint,pos=(x-.034,0,0),rot=rot)
        polygon(b,saddle(.153,.157),.068,mat('rubber'),pos=(x-.034,0,0),rot=rot)
        b.box((.068,.105,.025),(x,0,.517),paint,.003)
        for y in [-.146,.146]:bolt(b,(x-.034,y,.602),.009,axis='NX')
        b.box((.086,.32,.023),(x,0,.49),steel,.004)
        for y in [-.135,.135]:bolt(b,(x,y,.506),.010,axis='Z')
        # Steel uprights, not a cartridge floating over a deck.
        for y in [-.11,.11]:b.box((.067,.036,.18),(x,y,.414),steel,.005)
    rz=Matrix.Rotation(math.pi/2,3,'Y')
    body=[(0,0),(.086,0),(.134,.018),(.151,.042),(.155,.08),(.155,1.10),(.151,1.14),(.134,1.174),(.086,1.18),(0,1.18)]
    b.lathe(body,(-.59,0,.725),mat('warm enamel'),seg=48,rot=rz)
    # An exposed rolled service seam and selective handling marks below a clasp.
    b.lathe([(.154,0),(.157,0),(.157,.014),(.154,.014),(.154,0)],(-.23,0,.725),mat('steel'),seg=48,rot=rz)
    for x in [-.40,.37]:
        for j in range(3):
            a=math.pi*1.02+j*.10
            prof=[(.1558*math.cos(a+k*.035),.725+.1558*math.sin(a+k*.035)) for k in range(4)]
            b.ribbon(prof,x-.008-j*.004,x+.012+j*.006,.0004,mat('chip'))
    for x in [-.6145,.5825]:
        b.lathe([(.095,0),(.17,0),(.17,.018),(.151,.032),(.095,.032),(.095,0)],(x,0,.725),mat('steel'),seg=40,rot=rz)
        for i in range(8):
            a=2*math.pi*i/8;bolt(b,(x if x<0 else x+.032,.131*math.cos(a),.725+.131*math.sin(a)),.006,axis='NX' if x<0 else 'X')
    for side in [-1,1]:
        b.lathe([(0,0),(.100,0),(.105,.010),(.095,.025),(.088,.0325),(0,.0325)],(side*.59,0,.725),mat('warm enamel'),seg=40,rot=Matrix.Rotation(side*math.pi/2,3,'Y'))
    for x in [-.43,.43]:
        prof=[(.160*math.cos(math.pi*k/18),.725+.160*math.sin(math.pi*k/18)) for k in range(19)]
        b.ribbon(prof,x-.022,x+.022,.006,mat('canvas'))
        for y in [-.169,.169]:
            b.box((.077,.026,.060),(x,y,.702),mat('dark steel'),.003)
            b.box((.036,.029,.042),(x,y-.018,.708),mat('steel'),.003)
        for side in [-1,1]:
            for k in range(12):
                angle=.12+math.pi*k/12
                y=.164*math.cos(angle);z=.725+.164*math.sin(angle)
                b.tube([(x+side*.016-.002,y,z),(x+side*.016+.002,y,z)],.00065,mat('ink'),seg=6)
    b.tube(rounded_path([(-.70,.29,.33),(-.70,.29,1.12),(-.70,.22,1.20),(-.70,-.22,1.20),(-.70,-.29,1.12),(-.70,-.29,.33)]),.025,paint,seg=16)
    b.tube([(-.70,-.19,1.20),(-.70,.19,1.20)],.030,mat('rubber'),seg=16)
    b.box((.13,.008,.047),(.04,-.157,.72),mat('ink enamel'),.002)
    b.lathe([(0,0),(.023,0),(.027,.004),(.027,.009),(.023,.013),(0,.013)],(.27,0,.871),mat('dark steel'),seg=28)
    bolt(b,(.27,0,.884),.011,axis='Z',material='brass')
    # An inspection band and handled scuffs at the couplings, rather than a
    # generic scratch shader across the complete pressure vessel.
    b.lathe([(.1554,0),(.156,0),(.156,.035),(.1554,.035),(.1554,0)],(.105,0,.725),mat('repaired blue enamel'),seg=48,rot=rz)
    for x in [-.51,.49]:
        for j in range(3):
            a=math.pi+.13+j*.08
            b.ribbon([(.156*math.cos(a+k*.07),.725+.156*math.sin(a+k*.07)) for k in range(5)],x-.012,x+.016,.0003,mat('chip'))
    wear(b,(-.40,-.366,.317),(1,0,0),.35,.003,11)
    for x in [-.70,.70]:
        b.lathe([(.025,0),(.037,0),(.037,.022),(.025,.022),(.025,0)],(x,-.29,.318),mat('dark steel'),seg=24)
    # A replaced restraint on one saddle has a different paint value; equipment
    # stays maintained rather than becoming uniformly distressed.
    b.box((.070,.027,.030),(.43,-.194,.675),mat('replacement enamel'),.003)
    return b

def screwdriver():
    b=B();rot=Matrix.Rotation(math.pi/2,3,'X')
    b.lathe([(0,0),(.012,0),(.019,.006),(.021,.018),(.018,.086),(.014,.097),(.010,.102),(0,.102)],(0,-.010,0),mat('oxide enamel'),seg=28)
    b.cyl(.004,.117,(0,-.010,.102),mat('steel'),seg=16)
    b.box((.009,.003,.020),(0,-.010,.228),mat('steel'),.0006)
    for k in range(8):
        a=2*math.pi*k/8
        b.tube([(.018*math.cos(a),-.010+.018*math.sin(a),.023),(.016*math.cos(a),-.010+.016*math.sin(a),.080)],.001,mat('dark steel'),seg=6)
    b.tube([(-.01,0,.226),(-.01,0,.25),(.01,0,.25),(.01,0,.226)],.0022,mat('steel'),seg=8)
    return b

def pliers():
    b=B();steel=mat('steel')
    for s in [-1,1]:
        pts=[(s*.004,.115),(s*.032,.18),(s*.022,.218),(s*.009,.225),(s*.009,.179),(-s*.005,.131)]
        polygon(b,pts,.011,steel,rot=Matrix.Rotation(math.pi/2,3,'X'))
        path=rounded_path([(s*.003,-.006,.125),(s*.029,-.006,.093),(s*.037,-.006,.044),(s*.052,-.006,.005)])
        b.tube(path,.008,steel,seg=12)
        b.tube(path[5:],.011,mat('oxide enamel'),seg=12)
        for z in [.188,.197,.205]:b.box((.003,.002,.002),(s*.011,-.012,z),mat('dark steel'),.0003)
    bolt(b,(0,-.018,.124),.008,material='dark steel')
    return b

def bench():
    b=B();steel=mat('navy enamel');w=1.47;d=.59
    for x in [-.63,.63]:
        for y in [-.51,-.075]:
            b.box((.075,.065,.68),(x,y,.36),steel,.005)
            b.box((.095,.087,.02),(x,y,.01),mat('rubber'),.005)
        b.box((.075,.485,.043),(x,-.29,.18),steel,.004)
    b.box((w,.047,.12),(0,-.535,.725),steel,.003)
    b.box((w,.047,.12),(0,-.050,.725),steel,.003)
    b.box((w-.08,d-.08,.032),(0,-.30,.225),steel,.005)
    for x in [-.49,0,.49]:
        b.box((.47,.58,.055),(x,-.30,.868),mat('wood'),.003)
        for y in [-.51,-.085]:bolt(b,(x,y,.896),.005,axis='Z',material='dark steel')
    # A cup ring and a few real worktop nicks by the vice, localized to use.
    b.lathe([(.033,0),(.035,0),(.035,.0003),(.033,.0003),(.033,0)],(.14,-.30,.8956),mat('wood dark'),seg=40)
    for i in range(5):
        polygon(b,[(-.028,0),(.023,.001),(.035,.003),(-.018,.002)],.0003,mat('wood dark'),pos=(.34+i*.022,-.40-i*.020,.8955),rot=Matrix.Rotation(.21+i*.14,3,'Z'))
    # Real drawer opening, inset front, return handle, reveal around all four sides.
    for x in [-.35,.35]:
        b.box((.59,.39,.019),(x,-.31,.76),mat('dark steel'),.002)
        b.box((.59,.024,.19),(x,-.49,.665),mat('replacement enamel') if x>0 else steel,.003)
        b.tube(rounded_path([(x-.105,-.51,.685),(x-.105,-.545,.685),(x+.105,-.545,.685),(x+.105,-.51,.685)]),.010,mat('steel'),seg=12)
    for x in [-.67,.67]:
        for z in [.30,.78]:bolt(b,(x,-.574,z),.010)
    # Forged vice with asymmetric cast body, separate jaws and lead screw.
    polygon(b,[(-.095,0),(.08,0),(.095,.035),(.06,.08),(.072,.145),(-.065,.145),(-.05,.08),(-.10,.042)],.10,mat('ink enamel'),
            pos=(.45,-.52,.90),rot=Matrix.Rotation(math.pi/2,3,'X'))
    b.box((.14,.09,.025),(.46,-.56,1.055),mat('steel'),.003)
    b.box((.14,.058,.095),(.46,-.69,1.015),mat('navy enamel'),.006)
    b.box((.14,.016,.037),(.46,-.658,1.050),mat('steel'),.002)
    b.cyl(.013,.17,(.46,-.71,.987),mat('steel'),seg=20,axis='Y')
    for i in range(12):ring(b,.017,.003,(.46,-.712+i*.01,.987),mat('steel'),axis='Y',seg=16)
    b.cyl(.006,.18,(.37,-.729,.987),mat('steel'),seg=12,axis='X')
    for x in [.37,.55]:b.sph(.011,(x,-.729,.987),mat('dark steel'),seg=16,ring=8)
    return b

def spanner(length=.22):
    b=B();s=mat('steel');w=length*.10
    poly=[(-w*.52,.04),(-w*.52,length*.72),(-w*1.8,length*.86),(-w*1.5,length),(-w*.80,length*.98),
          (-w*.64,length*.90),(w*.64,length*.90),(w*.80,length*.98),(w*1.5,length),(w*1.8,length*.86),
          (w*.52,length*.72),(w*.52,.04)]
    polygon(b,poly,.006,s,rot=Matrix.Rotation(math.pi/2,3,'X'))
    b.lathe([(.009,0),(.020,0),(.020,.006),(.009,.006),(.009,0)],(0,0,.021),s,seg=20,rot=Matrix.Rotation(math.pi/2,3,'X'))
    b.box((.012,.001,.08),(0,-.0065,length*.49),mat('dark steel'),.0005)
    return b

def perforated_board(w=1.12,h=.58):
    b=B();s=mat('navy enamel');step=.044
    nx=int(w/step);nz=int(h/step);actualw=nx*step;actualh=nz*step
    for ix in range(nx):
        for iz in range(nz):
            cx=(ix-(nx-1)/2)*step;cz=(iz-(nz-1)/2)*step
            outer=[(-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0)]
            rows=[]
            for y in [-.029,-.025]:
                op=[b.bm.verts.new((cx+x*step/2,y,cz+z*step/2)) for x,z in outer]
                ip=[b.bm.verts.new((cx+.005*math.cos(-3*math.pi/4+i*math.pi/4),y,cz+.005*math.sin(-3*math.pi/4+i*math.pi/4))) for i in range(8)]
                rows.append((op,ip))
            for i in range(8):
                j=(i+1)%8
                for row in rows:b.bm.faces.new((row[0][i],row[0][j],row[1][j],row[1][i]))
                b.bm.faces.new((rows[0][1][i],rows[0][1][j],rows[1][1][j],rows[1][1][i]))
    b._fin(list(b.bm.verts),s,False)
    frame(b,actualw+.028,actualh+.028,.024,.035,-.017,0,mat('steel'),r=.018)
    for x in [-actualw/2+.025,actualw/2-.025]:
        for z in [-actualh/2+.025,actualh/2-.025]:
            b.box((.028,.025,.025),(x,-.0125,z),mat('dark steel'),.003);bolt(b,(x,-.031,z),.006)
    return b

def manifold(w=.68,h=.72):
    b=B();coat=mat('navy enamel');brass=mat('brass')
    frame(b,w,h,.045,.045,-.0225,h/2,mat('dark steel'),r=.03)
    b.box((w-.025,.012,h-.025),(0,-.047,h/2),coat,.004)
    frame(b,w-.09,h-.09,.005,.006,-.055,h/2,mat('replacement enamel'),r=.018)
    for x in [-w/2+.07,w/2-.07]:
        for z in [.07,h-.07]:bolt(b,(x,-.057,z),.007)
    # Collector, two genuine pipe branches, hex unions and distinct bonnet bodies.
    rz=Matrix.Rotation(math.pi/2,3,'Y');cy=.25
    b.lathe([(0,0),(.034,0),(.05,.015),(.05,.04),(.035,.055),(.035,.385),(.05,.40),(.05,.425),(.034,.44),(0,.44)],
            (-.22,-.16,cy),mat('dark steel'),seg=32,rot=rz)
    for x in [-.16,.16]:
        b.cyl(.016,.060,(x,-.16,cy+.025),brass,seg=20)
        b.lathe([(0,0),(.027,0),(.029,.018),(.025,.033),(.016,.041),(0,.041)],(x,-.16,.335),brass,seg=6)
        b.lathe([(0,0),(.031,0),(.038,.013),(.032,.034),(.023,.047),(.013,.052),(0,.052)],(x,-.16,.374),brass,seg=28)
        b.cyl(.008,.039,(x,-.16,.423),mat('steel'),seg=16)
        wheelz=.462
        b.tube([(x+.058*math.cos(2*math.pi*i/32),-.16+.058*math.sin(2*math.pi*i/32),wheelz) for i in range(33)],.008,mat('ochre enamel'),seg=12)
        for i in range(3):
            a=i*2*math.pi/3;b.tube([(x,-.16,wheelz),(x+.055*math.cos(a),-.16+.055*math.sin(a),wheelz)],.006,mat('ochre enamel'),seg=8)
        bolt(b,(x,-.16,wheelz+.002),.009,axis='Z')
    gx,gz=.025,h-.11
    b.tube(rounded_path([(0,-.16,cy+.030),(0,-.16,.43),(gx,-.12,gz-.12),(gx,-.12,gz)]),.009,brass,seg=16)
    b.lathe([(0,0),(.068,0),(.074,.012),(.074,.037),(.065,.049),(.056,.049),(.056,.045),(0,.045)],(gx,-.15,gz),mat('steel'),seg=40,rot=Matrix.Rotation(math.pi/2,3,'X'))
    b.cyl(.055,.001,(gx,-.196,gz),mat('paper'),seg=40,axis='Y')
    for i in range(15):
        a=math.radians(40+i*20);p=(gx+.044*math.cos(a),-.198,gz+.044*math.sin(a))
        b.box((.003,.0012,.007),p,mat('ink'),.0002,rot=Matrix.Rotation(-a+math.pi/2,3,'Y'))
    b.tube([(gx,-.199,gz),(gx-.032,-.199,gz+.018)],.0015,mat('ink'),seg=6)
    b.lathe([(0,0),(.055,0),(.055,.0015),(0,.0015)],(gx,-.200,gz),mat('glass'),seg=40,rot=Matrix.Rotation(math.pi/2,3,'X'))
    for x in [-.26,.22]:
        b.lathe([(0,0),(.030,0),(.030,.012),(.023,.018),(.023,.050),(0,.050)],(x,-.16,cy),brass,seg=6,rot=rz)
    # Feed inlet and a separate quick-release hose end parked in a retaining clip.
    b.tube(rounded_path([(.26,-.16,cy),(.30,-.20,.13),(.27,-.23,-.08),(.14,-.23,-.18),(-.09,-.23,-.17),(-.26,-.23,-.04),(-.25,-.19,.19)]),.014,mat('rubber'),seg=16)
    b.lathe([(0,0),(.017,0),(.024,.013),(.024,.033),(.017,.039),(.014,.062),(0,.062)],(-.25,-.19,.19),mat('steel'),seg=24)
    before=set(b.bm.verts);frame(b,.068,.065,.009,.026,-.174,.21,mat('dark steel'),r=.02)
    for v in b.bm.verts:
        if v not in before:v.co.x-=.25
    b.box((.13,.006,.033),(-.17,-.058,h-.08),mat('warm enamel'),.002)
    return b

def vent(w=.65,h=.29):
    b=B();coat=mat('replacement enamel')
    frame(b,w,h,.027,.023,-.012,0,coat,r=.015)
    frame(b,w-.053,h-.053,.012,.012,-.012,0,mat('rubber'),r=.008)
    # Open blades in front of a real recess, with inclined sheet return edges.
    for z in [(-h/2+.057)+i*(h-.1)/7 for i in range(8)]:
        b.box((w-.073,.034,.006),(0,.019,z),mat('dark steel'),.001,rot=Matrix.Rotation(.44,3,'X'))
    for x in [-w/2+.012,w/2-.012]:
        for z in [-h/2+.012,h/2-.012]:bolt(b,(x,-.028,z),.004)
    return b

def cabinet(w=.57,h=.7,depth=.17,firstaid=False):
    b=B();coat=mat('warm enamel') if firstaid else mat('navy enamel')
    # Fabricated open box with inward return lips and recessed gasket.
    b.box((w,.012,h),(0,-.006,h/2),coat,.004)
    for x in [-w/2+.01,w/2-.01]:b.box((.020,depth,h),(x,-depth/2,h/2),coat,.004)
    for z in [.01,h-.01]:b.box((w,depth,.02),(0,-depth/2,z),coat,.004)
    frame(b,w-.03,h-.03,.012,.013,-depth+.012,h/2,mat('rubber'),r=.019)
    b.box((w-.056,.019,h-.056),(0,-depth-.004,h/2),coat,.006)
    for z in [h*.21,h*.79]:
        b.cyl(.012,.055,(-w/2+.02,-depth-.019,z),mat('steel'),seg=16)
    b.tube(rounded_path([(w*.34,-depth-.019,h*.36),(w*.34,-depth-.048,h*.38),(w*.34,-depth-.048,h*.57),(w*.34,-depth-.019,h*.59)]),.010,mat('dark steel'),seg=12)
    if firstaid:
        # A single stamped cross, no coplanar crossing-bar artefact.
        s=.052;pts=[(-s/2,-s*1.5),(s/2,-s*1.5),(s/2,-s/2),(s*1.5,-s/2),(s*1.5,s/2),(s/2,s/2),(s/2,s*1.5),(-s/2,s*1.5),(-s/2,s/2),(-s*1.5,s/2),(-s*1.5,-s/2),(-s/2,-s/2)]
        polygon(b,pts,.0018,mat('red'),pos=(0,-depth-.016,h*.58),rot=Matrix.Rotation(math.pi/2,3,'X'))
    else:
        b.cyl(.043,.018,(0,-depth-.018,h*.57),mat('dark steel'),seg=24,axis='Y')
        b.box((.026,.025,.107),(0,-depth-.044,h*.57),mat('ochre enamel'),.005,rot=Matrix.Rotation(.20,3,'Y'))
    return b

def maintenance_notice():
    """A framed shift board: raised route diagram, clipped papers and folded note."""
    b=B();w=.98;h=.68
    b.box((w,.023,h),(0,-.0115,h/2),mat('dark steel'),.004)
    frame(b,w+.035,h+.035,.027,.025,-.024,h/2,mat('wood'),r=.012)
    b.box((w-.048,.016,h-.048),(0,-.031,h/2),mat('navy enamel'),.003)
    for x in [-.44,.44]:
        for z in [.035,h-.035]:bolt(b,(x,-.050,z),.006)
    b.box((.48,.0018,.34),(-.19,-.041,.305),mat('paper'),.0003)
    b.box((.255,.0018,.31),(.29,-.041,.345),mat('paper'),.0003)
    # Route markings are ink on the actual paper; paper edges remain separate.
    for pts in [[(-.375,-.043,.23),(-.30,-.043,.23),(-.30,-.043,.37),(-.12,-.043,.37),(-.12,-.043,.23),(.015,-.043,.23)],
                [(-.30,-.043,.31),(-.035,-.043,.31)]]:
        b.tube(pts,.002,mat('ink'),seg=6)
    for x,z in [(-.30,.31),(-.12,.37)]:
        b.lathe([(.012,0),(.018,0),(.018,.0006),(.012,.0006),(.012,0)],(x,-.043,z),mat('oxide enamel'),seg=20,rot=Matrix.Rotation(math.pi/2,3,'X'))
    for x in [-.19,.29]:
        b.box((.062,.010,.019),(x,-.047,.483 if x<0 else .508),mat('steel'),.002)
        b.tube([(x-.024,-.055,.48),(x-.024,-.055,.50),(x+.024,-.055,.50),(x+.024,-.055,.48)],.002,mat('steel'),seg=8)
    polygon(b,[(-.07,0),(.08,0),(.08,.13),(.05,.16),(-.07,.16)],.001,mat('ochre enamel'),pos=(.245,-.045,.094),rot=Matrix.Rotation(math.pi/2,3,'X'))
    b.cyl(.004,.008,(.26,-.055,.24),mat('red'),seg=12,axis='Y')
    return b

def interlock_console():
    """Human-height reactor interlock, with folded casing and serviceable front."""
    b=B();w=.62;h=.92;d=.17
    b.box((w,.018,h),(0,-.009,h/2),mat('dark steel'),.004)
    for x in [-w/2+.012,w/2-.012]:
        polygon(b,[(0,0),(-d,0),(-d-.028,.29),(-d-.028,.74),(-d,.92),(0,.92)],.023,mat('oxide enamel'),pos=(x,0,0),rot=Matrix.Rotation(math.pi/2,3,'Y')@Matrix.Rotation(math.pi/2,3,'Z'))
    b.box((w,.17,.022),(0,-.085,.011),mat('oxide enamel'),.003)
    b.box((w,.17,.022),(0,-.085,h-.011),mat('oxide enamel'),.003)
    b.box((w-.045,.018,.45),(0,-.20,.53),mat('warm enamel'),.004)
    b.box((w-.045,.016,.22),(0,-.175,.13),mat('navy enamel'),.003)
    for x in [-.255,.255]:
        for z in [.05,.22,.33,.73]:bolt(b,(x,-.214 if z>.3 else -.187,z),.006)
    # The dial has a metal bezel, recessed face, glass and a pointer.
    b.lathe([(.074,0),(.085,0),(.090,.014),(.085,.031),(.074,.031),(.074,0)],(-.12,-.215,.60),mat('steel'),seg=40,rot=Matrix.Rotation(math.pi/2,3,'X'))
    b.lathe([(0,0),(.074,0),(.074,.002),(0,.002)],(-.12,-.225,.60),mat('paper'),seg=40,rot=Matrix.Rotation(math.pi/2,3,'X'))
    for k in range(13):
        a=math.radians(-210+k*20)
        b.tube([(-.12+.059*math.cos(a),-.228,.60+.059*math.sin(a)),(-.12+.068*math.cos(a),-.228,.60+.068*math.sin(a))],.001,mat('ink'),seg=6)
    b.tube([(-.12,-.231,.60),(-.14,-.231,.65)],.0018,mat('red'),seg=8)
    b.lathe([(0,0),(.073,0),(.073,.002),(0,.002)],(-.12,-.244,.60),mat('glass'),seg=40,rot=Matrix.Rotation(math.pi/2,3,'X'))
    b.lathe([(0,0),(.045,0),(.045,.020),(.036,.025),(0,.025)],(.14,-.213,.52),mat('dark steel'),seg=24,rot=Matrix.Rotation(math.pi/2,3,'X'))
    b.box((.025,.020,.083),(.14,-.248,.52),mat('ochre enamel'),.004,rot=Matrix.Rotation(.25,3,'Y'))
    for x in [.095,.18]:
        b.lathe([(0,0),(.014,0),(.014,.009),(0,.009)],(x,-.213,.67),mat('dark steel'),seg=20,rot=Matrix.Rotation(math.pi/2,3,'X'))
        b.lathe([(0,0),(.009,0),(.009,.003),(0,.003)],(x,-.223,.67),mat('amber'),seg=20,rot=Matrix.Rotation(math.pi/2,3,'X'))
    b.box((.30,.003,.055),(0,-.212,.39),mat('ink enamel'),.002)
    for z in [.06,.19]:
        b.cyl(.010,.04,(-.277,-.187,z),mat('steel'),seg=16)
    b.box((.055,.027,.032),(.21,-.202,.13),mat('steel'),.004)
    return b

def exhaust_collector(riser=1.55):
    """A folded extractor with an open heat-exchanger face and flanged riser."""
    b=B();w=1.02;h=1.18
    frame(b,w,h,.047,.028,-.014,h/2,mat('dark steel'),r=.032)
    for x in [-w/2+.02,w/2-.02]:
        polygon(b,[(-.045,0),(-.31,.075),(-.39,.48),(-.29,1.13),(-.045,h)],.025,mat('oxide enamel'),pos=(x,0,0),rot=Matrix.Rotation(math.pi/2,3,'Y')@Matrix.Rotation(math.pi/2,3,'Z'))
    for z,y in [(.058,-.17),(1.13,-.165)]:b.box((w-.025,.25,.032),(0,y,z),mat('oxide enamel'),.003)
    merge(b,vent(.91,.49),(0,-.36,.46))
    b.box((.84,.012,.44),(0,-.11,.46),mat('rubber'),.003)
    b.box((.89,.027,.265),(0,-.295,.95),mat('warm enamel'),.005)
    for x in [-.39,.39]:
        for z in [.85,1.05]:bolt(b,(x,-.313,z),.008)
        b.box((.037,.042,.071),(x,-.322,.94),mat('dark steel'),.004)
    # Thin sheet sides surround a real hollow rectangular duct.
    z0=1.18;z1=z0+riser;dw=.34;dd=.26
    for x in [-dw/2,dw/2]:b.box((.004,dd,riser),(x,-.16,(z0+z1)/2),mat('steel'),.0006)
    for y in [-.29,-.03]:b.box((dw,.004,riser),(0,y,(z0+z1)/2),mat('steel'),.0006)
    for z in [z0+.025,z0+riser*.46,z1-.025]:
        for x in [-.185,.185]:b.box((.026,.30,.037),(x,-.16,z),mat('dark steel'),.002)
        for y in [-.31,-.01]:b.box((.37,.026,.037),(0,y,z),mat('dark steel'),.002)
        for x in [-.185,.185]:bolt(b,(x,-.326,z),.007)
    boot=B();frame(boot,.44,.35,.045,.015,0,0,mat('dark steel'),r=.020)
    merge(b,boot,(0,-.16,z1+.0025),Matrix.Rotation(math.pi/2,3,'X'))
    # Wall-bearing straps, a connected terminal gland and actual control lead.
    for z in [1.0,z1-.12]:
        b.box((.46,.018,.073),(0,-.009,z),mat('dark steel'),.003)
        for x in [-.19,.19]:bolt(b,(x,-.021,z),.006)
    b.tube(rounded_path([(.36,-.07,1.1),(.36,-.09,1.35),(.20,-.09,1.38),(.18,-.05,1.43)]),.010,mat('rubber'),seg=12)
    b.box((.20,.003,.051),(0,-.312,.948),mat('ink enamel'),.002)
    return b

def clean_station():
    """A shallow hygiene rack with folded wipes, dispensing lip and job sheet."""
    b=B();w=.83;h=.72
    b.box((w,.020,h),(0,-.010,h/2),mat('warm enamel'),.004)
    for x in [-w/2+.014,w/2-.014]:
        b.box((.028,.24,.49),(x,-.12,.28),mat('replacement enamel'),.005)
        for z in [.08,.48]:bolt(b,(x,-.025,z),.006)
    b.box((w,.245,.019),(0,-.12,.019),mat('replacement enamel'),.003)
    b.box((w-.06,.020,.17),(0,-.232,.10),mat('navy enamel'),.003)
    # Individually folded cloth, including the thin sewn border of each pack.
    merge(b,rag(),(-.205,-.122,.040))
    merge(b,rag(),(.060,-.115,.053),Matrix.Rotation(.11,3,'Z'))
    for xx in [-.34,-.10,.16]:b.box((.011,.21,.14),(xx,-.116,.090),mat('dark steel'),.001)
    frame(b,.76,.31,.023,.025,-.035,.535,mat('dark steel'),r=.023)
    merge(b,clipboard(),(.20,-.040,.53),Matrix.Rotation(math.pi/2,3,'X')@Matrix.Rotation(-.06,3,'Z'))
    b.box((.23,.002,.058),(-.20,-.050,.535),mat('ink enamel'),.002)
    b.tube([(-.30,-.052,.40),(-.30,-.08,.40),(-.24,-.09,.405)],.004,mat('steel'),seg=12)
    b.box((.068,.003,.084),(-.26,-.093,.35),mat('ochre enamel'),.002,rot=Matrix.Rotation(.09,3,'Y'))
    return b

def sealed_transfer_bin():
    """A wheeled, gasketed waste vessel with foot latch and clamped lid."""
    b=B();rz=Matrix.Rotation(math.pi/2,3,'X')
    for x in [-.15,.15]:
        b.lathe([(0,0),(.021,0),(.047,.006),(.049,.025),(.044,.037),(.019,.037),(0,.037)],(x,.155,.049),mat('rubber'),seg=28,rot=rz)
        b.cyl(.022,.021,(x,.14,.103),mat('steel'),seg=20)
        b.box((.044,.08,.038),(x,.14,.126),mat('dark steel'),.003)
        b.box((.047,.060,.117),(x,-.14,.0585),mat('rubber'),.005)
    b.lathe([(0,0),(.15,0),(.192,.014),(.212,.051),(.210,.49),(.202,.53),(.190,.548),(0,.548)],(0,0,.115),mat('oxide enamel'),seg=48)
    for k in range(8):
        a=2*math.pi*k/8
        b.tube([(.212*math.cos(a),.212*math.sin(a),.20),(.212*math.cos(a),.212*math.sin(a),.57)],.003,mat('oxide enamel'),seg=8)
    b.lathe([(.189,0),(.214,0),(.216,.013),(.214,.028),(.190,.028),(.189,0)],(0,0,.647),mat('steel'),seg=48)
    b.lathe([(0,0),(.20,0),(.217,.010),(.220,.028),(.214,.040),(.184,.053),(.168,.066),(0,.066)],(0,0,.671),mat('warm enamel'),seg=48)
    b.lathe([(.188,0),(.211,0),(.211,.005),(.188,.005),(.188,0)],(0,0,.668),mat('rubber'),seg=48)
    for k in range(3):
        a=math.pi/6+2*math.pi*k/3;x=.214*math.cos(a);y=.214*math.sin(a)
        b.box((.032,.051,.073),(x,y,.674),mat('dark steel'),.004,rot=Matrix.Rotation(a,3,'Z'))
        bolt(b,(x,y,.716),.007,axis='Z')
    b.tube(rounded_path([(-.09,-.202,.455),(-.09,-.260,.455),(-.064,-.280,.465),(.064,-.280,.465),(.09,-.260,.455),(.09,-.202,.455)]),.009,mat('steel'),seg=12)
    b.box((.14,.077,.025),(0,-.238,.028),mat('dark steel'),.004,rot=Matrix.Rotation(-.09,3,'X'))
    for x in [-.050,-.025,0,.025,.05]:b.box((.006,.060,.003),(x,-.239,.043),mat('rubber'),.0006)
    b.tube(rounded_path([(0,-.22,.043),(0,-.211,.09),(0,-.212,.635)]),.007,mat('dark steel'),seg=10)
    b.box((.125,.009,.075),(0,-.216,.395),mat('ink enamel'),.003)
    for x in [-.049,.049]:bolt(b,(x,-.223,.395),.004)
    return b

def flow_monitor():
    """Shallow process gauge with a real tapped connection into the water main."""
    b=B();w=.47;h=.53
    b.box((w,.018,h),(0,-.009,h/2),mat('dark steel'),.004)
    b.box((w-.022,.065,h-.024),(0,-.05,h/2),mat('oxide enamel'),.009)
    b.box((w-.056,.014,h-.061),(0,-.089,h/2),mat('warm enamel'),.005)
    for x in [-.185,.185]:
        for z in [.057,.467]:bolt(b,(x,-.101,z),.006)
    b.lathe([(.073,0),(.083,0),(.089,.012),(.084,.031),(.073,.031),(.073,0)],(0,-.099,.322),mat('steel'),seg=40,rot=Matrix.Rotation(math.pi/2,3,'X'))
    b.lathe([(0,0),(.073,0),(.073,.002),(0,.002)],(0,-.110,.322),mat('paper'),seg=40,rot=Matrix.Rotation(math.pi/2,3,'X'))
    for k in range(13):
        a=math.radians(-210+k*20)
        b.tube([(.056*math.cos(a),-.113,.322+.056*math.sin(a)),(.065*math.cos(a),-.113,.322+.065*math.sin(a))],.0011,mat('ink'),seg=6)
    b.tube([(0,-.117,.322),(.039,-.117,.352)],.0018,mat('red'),seg=8)
    b.lathe([(0,0),(.073,0),(.073,.002),(0,.002)],(0,-.128,.322),mat('glass'),seg=40,rot=Matrix.Rotation(math.pi/2,3,'X'))
    b.tube([(0,-.11,.53),(0,-.11,1.12)],.013,mat('brass'),seg=20)
    for z in [.60,1.07]:b.lathe([(0,0),(.025,0),(.025,.025),(.016,.030),(0,.030)],(0,-.11,z),mat('brass'),seg=6)
    ring(b,.034,.006,(0,-.11,1.12),mat('brass'),axis='X',seg=24)
    b.box((.30,.003,.055),(0,-.099,.109),mat('ink enamel'),.002)
    return b

def thermos():
    b=B();coat=mat('ochre enamel')
    b.lathe([(0,0),(.040,0),(.045,.008),(.044,.19),(.038,.212),(.03,.221),(.028,.249),(0,.249)],(0,0,0),coat,seg=32)
    b.lathe([(0,0),(.035,0),(.039,.007),(.039,.038),(.034,.044),(0,.044)],(0,0,.223),mat('dark steel'),seg=28)
    b.lathe([(.044,0),(.045,0),(.045,.019),(.044,.019),(.044,0)],(0,0,.075),mat('steel'),seg=32)
    return b

def mug():
    b=B();m=mat('warm enamel')
    b.lathe([(0,0),(.033,0),(.04,.007),(.042,.086),(.041,.095),(.035,.095),(.034,.015),(0,.015)],(0,0,0),m,seg=32)
    b.lathe([(0,0),(.034,0)],(0,0,.067),mat('coffee'),seg=32)
    b.tube([(.04+.025*math.cos(math.radians(-90+i*180/20)),0,.05+.032*math.sin(math.radians(-90+i*180/20))) for i in range(21)],.006,m,seg=12)
    return b

def rag():
    b=B();pts=[]
    for i in range(3):
        z=.005+i*.016
        seq=[(-.115,z),(.108,z)] if i%2==0 else [(.108,z),(-.115,z)]
        pts.extend(seq)
        if i<2:
            y=seq[-1][0]
            for j in range(1,6):
                a=-math.pi/2+(math.pi if i%2==0 else -math.pi)*j/5
                pts.append((y+.008*math.cos(a),z+.008+.008*math.sin(a)))
    b.ribbon(pts,-.13,.13,.004,mat('cotton'))
    b.box((.014,.19,.001),(.075,0,.042),mat('canvas'),.0002)
    return b

def glove():
    b=B();m=mat('leather')
    b.sph(.048,(0,0,.023),m,scale=(.80,1.25,.40),seg=24,ring=12)
    for i,(x,l) in enumerate([(-.026,.070),(-.009,.082),(.009,.080),(.026,.064)]):
        b.tube(rounded_path([(x,.034,.021),(x,.07,.022),(x+.006,.034+l,.012)]),.0095,m,seg=12)
    b.tube(rounded_path([(-.028,-.023,.020),(-.052,-.003,.016),(-.065,.014,.007)]),.014,m,seg=12)
    before=set(b.bm.verts)
    b.lathe([(.025,0),(.034,0),(.036,.010),(.034,.038),(.029,.040),(.025,.038),(.025,0)],(0,-.064,.021),mat('cotton'),seg=24,rot=Matrix.Rotation(math.pi/2,3,'X'))
    for v in b.bm.verts:
        if v not in before:v.co.z=.021+(v.co.z-.021)*.33
    b.tube([(-.028,-.085,.029),(0,-.092,.032),(.028,-.085,.029)],.0012,mat('canvas'),seg=8)
    return b

def clipboard():
    b=B();w=.22;d=.31
    polygon(b,[(-w/2+.01,-d/2),(w/2-.01,-d/2),(w/2,-d/2+.01),(w/2,d/2-.01),(w/2-.01,d/2),(-w/2+.01,d/2),(-w/2,d/2-.01),(-w/2,-d/2+.01)],.006,mat('wood'))
    # Paper has a lifted corner and irregular stacked sheet edges, not a decal box.
    for j in range(3):
        verts=[]
        for i in range(9):
            for k in range(11):
                x=(i/8-.5)*.196;y=(k/10-.5)*.282
                z=.008+j*.0007+.008*max(0,(i-6)/2)*max(0,(3-k)/3)
                verts.append(b.bm.verts.new((x,y,z)))
        for i in range(8):
            for k in range(10):b.bm.faces.new([verts[i*11+k],verts[(i+1)*11+k],verts[(i+1)*11+k+1],verts[i*11+k+1]])
        b._fin(verts,mat('paper'),False)
    b.box((.062,.035,.006),(0,.127,.013),mat('steel'),.003)
    b.tube([(-.025,.137,.018),(-.025,.118,.022),(.025,.118,.022),(.025,.137,.018)],.0023,mat('steel'),seg=8)
    for i in range(9):
        b.box((.131,.0007,.0001),(.008,.075-i*.017,.011),mat('ink'),.00004)
    b.box((.021,.017,.0001),(-.068,.08,.011),mat('oxide enamel'),.00004)
    return b


def radio():
    b=B();coat=mat('dark steel')
    polygon(b,[(-.039,0),(.039,0),(.045,.024),(.037,.139),(-.035,.143),(-.044,.025)],.033,coat,rot=Matrix.Rotation(math.pi/2,3,'X'))
    b.box((.055,.004,.026),(0,-.036,.109),mat('glass'),.003)
    for z in [.035,.045,.055,.065,.075]:b.box((.054,.004,.004),(0,-.036,z),mat('rubber'),.001)
    for x in [-.025,.025]:b.cyl(.010,.019,(x,-.016,.143),mat('rubber'),seg=16)
    b.tube(rounded_path([(-.025,-.012,.161),(-.026,-.012,.205),(-.013,-.012,.238)]),.0045,mat('rubber'),seg=12)
    b.box((.018,.008,.024),(.038,-.018,.109),mat('ochre enamel'),.002)
    return b

def pail():
    b=B();coat=mat('oxide enamel')
    b.lathe([(0,0),(.125,0),(.14,.012),(.153,.31),(.154,.33),(.145,.337),(.136,.321),(.129,.023),(0,.023)],(0,0,0),coat,seg=40)
    b.lathe([(0,0),(.154,0),(.155,.01),(.147,.019),(.035,.019),(.03,.025),(0,.025)],(0,0,.335),mat('warm enamel'),seg=40)
    b.tube(rounded_path([(-.145,0,.285),(-.19,0,.38),(-.11,0,.49),(.11,0,.49),(.19,0,.38),(.145,0,.285)]),.005,mat('steel'),seg=12)
    b.tube([(-.055,0,.485),(.055,0,.485)],.012,mat('rubber'),seg=12)
    for x in [-.151,.151]:bolt(b,(x,-.009,.29),.009,axis='NX' if x<0 else 'X')
    return b

def extinguisher():
    b=B();red=mat('red')
    # Forged cylinder with rolled foot and domed shoulder, valve, bent lever and hose.
    b.lathe([(0,0),(.073,0),(.085,.012),(.082,.038),(.082,.33),(.078,.364),(.059,.392),(.031,.405),(.025,.435),(0,.435)],(0,-.12,.17),red,seg=40)
    b.lathe([(.076,0),(.086,0),(.086,.022),(.076,.022),(.076,0)],(0,-.12,.174),mat('dark steel'),seg=32)
    b.cyl(.019,.047,(0,-.12,.604),mat('brass'),seg=20)
    polygon(b,[(-.045,0),(.082,0),(.088,.015),(-.025,.025),(-.045,.015)],.016,mat('dark steel'),pos=(0,-.108,.649),rot=Matrix.Rotation(math.pi/2,3,'X'))
    b.tube(rounded_path([(.028,-.13,.646),(.106,-.13,.601),(.109,-.15,.445),(.106,-.20,.288),(.070,-.207,.247)]),.009,mat('rubber'),seg=12)
    b.lathe([(0,0),(.014,0),(.017,.035),(.013,.065),(0,.065)],(.070,-.207,.247),mat('dark steel'),seg=24)
    # Wall rack bears the foot and holds the upper body with a retaining band.
    b.box((.09,.014,.48),(0,-.007,.42),mat('dark steel'),.003)
    b.box((.16,.22,.016),(0,-.115,.162),mat('dark steel'),.003)
    for z in [.25,.55]:bolt(b,(0,-.017,z),.006)
    b.tube([(0,-.008,.50),(0,-.032,.50)],.010,mat('steel'),seg=12)
    b.lathe([(.080,0),(.086,0),(.086,.025),(.080,.025),(.080,0)],(0,-.12,.496),mat('dark steel'),seg=32)
    b.box((.053,.004,.114),(0,-.203,.378),mat('paper'),.004)
    for z in [.34,.365,.39,.415]:b.box((.038,.001,.002),(0,-.206,z),mat('ink'),.0002)
    return b

def lockout_station():
    b=B();coat=mat('warm enamel')
    frame(b,.45,.39,.016,.019,-.010,.195,coat,r=.022)
    b.box((.426,.009,.366),(0,-.015,.195),mat('patch'),.002)
    for x in [-.18,.18]:
        for z in [.05,.34]:bolt(b,(x,-.021,z),.004)
    for i in range(3):
        x=-.12+i*.12
        b.tube([(x,-.020,.29),(x,-.048,.29),(x,-.05,.30)],.003,mat('steel'),seg=8)
        b.box((.035,.018,.049),(x,-.052,.23),mat('red' if i!=1 else 'ochre enamel'),.005)
        b.tube(rounded_path([(x-.012,-.051,.254),(x-.012,-.051,.285),(x+.012,-.051,.285),(x+.012,-.051,.254)]),.0035,mat('steel'),seg=8)
        if i!=1:
            polygon(b,[(-.023,0),(.023,0),(.025,.065),(.012,.083),(-.012,.083),(-.025,.065)],.0008,mat('paper'),pos=(x,-.064,.112),rot=Matrix.Rotation(math.pi/2,3,'X'))
            b.tube([(x,-.058,.231),(x,-.065,.191)],.001,mat('canvas'),seg=6)
            for z in [.133,.143,.154]:b.box((.027,.0008,.0018),(x,-.065,z),mat('ink'),.0002)
    return b

def cable_ladder(length=1.7):
    b=B();steel=mat('dark steel')
    # An open ladder with folded rails; loose cables have gentle gravity sag.
    for y in [-.075,-.245]:
        b.box((length,.012,.071),(0,y,0),steel,.002)
        b.box((length,.025,.012),(0,y-.003,-.030),steel,.001)
    for i in range(int(length/.17)+1):
        x=-length/2+.028+i*(length-.056)/max(1,int(length/.17))
        b.box((.028,.176,.010),(x,-.159,-.020),steel,.001)
    for i in range(3):
        y=-.104-i*.038
        path=[(-length/2,0,.024),(-length/2+.07,y*.55,.017)]+[(-length/2+.13+k*(length-.26)/30,y,.011-.012*math.sin(math.pi*k/30)) for k in range(31)]+[(length/2-.07,y*.55,.017),(length/2,0,.024)]
        b.tube(path,.008 if i<2 else .011,mat('rubber') if i!=1 else mat('oxide enamel'),seg=10)
        for x in [-length/2,length/2]:
            b.lathe([(0,0),(.018,0),(.018,.009),(.012,.012),(0,.012)],(x,0,.024),mat('dark steel'),seg=16,rot=Matrix.Rotation(math.pi/2,3,'X'))
    for x in [-length*.37,length*.37]:
        b.box((.055,.017,.16),(x,-.0085,-.03),steel,.003)
        b.box((.026,.22,.026),(x,-.117,-.085),steel,.002)
        for z in [-.090,.036]:bolt(b,(x,-.019,z),.005)
        b.tube([(x-.006,-.068,.01),(x-.006,-.268,.01)],.002,mat('steel'),seg=8)
    return b

def pipe_run(length=2.1,drop=.85):
    b=B();metal=mat('steel');r=.023;y=-.13
    path=rounded_path([(-length/2,0,0),(-length/2+.05,y*.65,0),(-length/2+.12,y,0),(length/2-.12,y,0),(length/2,y,-.10),(length/2,y,-drop)])
    b.tube(path,r,metal,seg=20)
    b.lathe([(r*.8,0),(.043,0),(.043,.012),(.034,.018),(r*.8,.018),(r*.8,0)],(-length/2,0,0),mat('dark steel'),seg=32,rot=Matrix.Rotation(math.pi/2,3,'X'))
    for x in [-length/2+.15,0,length/2-.15]:
        ring(b,r+.006,.014,(x-.007,y,0),mat('brass'),axis='X',seg=24)
    for x in [-length*.33,length*.24]:
        b.box((.068,.014,.16),(x,-.007,-.025),mat('dark steel'),.003)
        for z in [-.083,.031]:bolt(b,(x,-.016,z),.005)
        b.tube([(x,-.014,-.025),(x,-.11,-.025)],.008,mat('dark steel'),seg=12)
        ring(b,.03,.007,(x-.004,y,0),mat('dark steel'),axis='X',seg=24)
    ring(b,.035,.025,(length/2,y,-drop+.065),mat('brass'),seg=24)
    # Wrapped repair on a single real joint, not noisy scratches everywhere.
    for z in [-drop+.22,-drop+.235,-drop+.25,-drop+.265]:ring(b,.026,.014,(length/2,y,z),mat('canvas'),seg=24)
    b.lathe([(0,0),(.025,0),(.027,.022),(.030,.03),(.030,.049),(.023,.063),(0,.063)],(length/2,y,-drop),mat('brass'),seg=6)
    b.lathe([(0,0),(.017,0),(.017,.012),(0,.012)],(length/2,y,-drop-.012),mat('dark steel'),seg=24)
    return b

def gate_drive(width=3.0):
    b=B();dark=mat('dark steel')
    # Twin opposing tracks, clevis supports, rollers, guarded pulley and cast motor.
    L=width+4.80
    for y in [-.22,-.095]:
        # Horizontal C rail: continuous web, running flange and return lips.
        b.box((L,.008,.13),(0,y+.026,.105),dark,.0015)
        for z in [.044,.166]:b.box((L,.060,.008),(0,y,z),dark,.0015)
        for z in [.0555,.1545]:b.box((L,.009,.023),(0,y-.0255,z),dark,.0015)
    for x in [-L/2+.12,-width/2,width/2,L/2-.12]:
        b.box((.072,.36,.040),(x,-.070,.17),dark,.003)
        for y in [-.18,.04]:bolt(b,(x,y,.193),.007,axis='Z')
    b.tube([(-L/2+.07,-.265,.133),(L/2-.07,-.265,.133)],.007,mat('rubber'),seg=12)
    x=1.0
    polygon(b,[(-.11,0),(.11,0),(.135,.047),(.11,.18),(-.09,.20),(-.135,.04)],.095,mat('replacement enamel'),pos=(x,-.215,.19),rot=Matrix.Rotation(math.pi/2,3,'X'),bevel=.007)
    b.lathe([(0,0),(.060,0),(.074,.006),(.074,.012),(.066,.021),(.047,.023),(.047,.026),(0,.026)],(x,-.310,.285),mat('dark steel'),seg=40,rot=Matrix.Rotation(math.pi/2,3,'X'))
    for k in range(6):
        a=k*math.pi/3;bolt(b,(x+.057*math.cos(a),-.333,.285+.057*math.sin(a)),.005)
    bolt(b,(x-.085,-.312,.221),.008,material='brass')
    for xx in [x-.065,x+.065]:
        b.box((.06,.105,.037),(xx,-.225,.176),mat('dark steel'),.003)
        bolt(b,(xx,-.258,.197),.006,axis='Z')
    b.lathe([(0,0),(.092,0),(.107,.018),(.105,.235),(.084,.255),(0,.255)],(x+.07,-.172,.31),mat('navy enamel'),seg=32,rot=Matrix.Rotation(math.pi/2,3,'Y'))
    for i in range(7):ring(b,.110,.010,(x+.097+i*.025,-.172,.31),mat('dark steel'),axis='X',seg=28)
    b.box((.18,.055,.074),(x+.21,-.12,.385),mat('dark steel'),.005)
    b.lathe([(0,0),(.020,0),(.020,.010),(.017,.013),(.017,.027),(0,.027)],(x+.297,-.13,.385),mat('dark steel'),seg=6,rot=Matrix.Rotation(math.pi/2,3,'Y'))
    b.tube(rounded_path([(x+.21,-.12,.42),(x+.31,-.14,.48),(x+.36,-.13,.44),(x+.324,-.13,.385)]),.009,mat('rubber'),seg=12)
    b.box((.026,.017,.20),(x-.15,-.22,.36),dark,.002)
    b.tube([(x-.15,-.22,.448),(x-.15,-.425,.448)],.009,dark,seg=12)
    b.box((.20,.12,.05),(x-.10,-.425,.478),mat('navy enamel'),.004)
    b.box((.165,.084,.007),(x-.10,-.427,.450),mat('warm diffuser'),.001)
    return b


def spare_filter_box():
    b=B();paper=mat('paper');metal=mat('steel')
    # Open folded package with one loose corrugated filter and folded end flaps.
    w,d,h=.34,.24,.15
    b.box((w,d,.007),(0,0,.0035),paper,.001)
    for x in [-w/2+.0035,w/2-.0035]:b.box((.007,d,h),(x,0,h/2),paper,.001)
    for y in [-d/2+.0035,d/2-.0035]:b.box((w,.007,h),(0,y,h/2),paper,.001)
    for side in [-1,1]:
        b.box((w,.095,.007),(0,side*.152,.163),paper,.001,rot=Matrix.Rotation(side*.29,3,'X'))
    start=set(b.bm.verts)
    frame(b,.275,.20,.012,.026,0,.10,metal,r=.012)
    count=18
    for i in range(count):
        x=-.125+i*.25/count;xx=x+.25/count
        for xa,ya,xb,yb in [(x,-.012,(x+xx)/2,.010),((x+xx)/2,.010,xx,-.012)]:
            angle=math.atan2(yb-ya,xb-xa);length=math.hypot(xb-xa,yb-ya)
            b.box((length,.0011,.173),((xa+xb)/2,(ya+yb)/2,.10),mat('canvas'),.0002,rot=Matrix.Rotation(angle,3,'Z'))
    rot=Matrix.Rotation(-.24,3,'X')
    for v in b.bm.verts:
        if v not in start:v.co=rot@v.co+Vector((0,.015,.045))
    b.box((.09,.0007,.036),(.04,-d/2-.0004,.09),mat('ink'),.001)
    for x in [-.02,-.012,.004,.012,.031,.042]:b.box((.003,.0006,.028),(x,-d/2-.001,.09),paper,.0002)
    return b
