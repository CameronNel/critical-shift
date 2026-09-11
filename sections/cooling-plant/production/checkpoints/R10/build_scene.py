"""Cooling Plant: original reproducible factory-empty Blender environment."""
import bpy, sys, math, json, hashlib, argparse
from pathlib import Path
from math import pi, sin, cos
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from kit import *

ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['slice','full'],default='slice');ap.add_argument('--revision',default='S01');ap.add_argument('--output',default='cooling_plant.blend')
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.read_factory_settings(use_empty=True);palette();random.seed(817)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene['section']='cooling-plant';scene['revision']=args.revision;scene['stage']=args.stage
scene['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()+ (HERE/'kit.py').read_bytes()+(HERE/'develop_room.py').read_bytes()).hexdigest()
scene['authorship']='Original factory-empty Python geometry; no imported legacy meshes or external textures.'

def floor():
    arch=before()
    slab=box('Floor',(0,6.65,-.16),(11.6,13.3,.32),'floor',.002)
    for xx in (-1.58,4.98):
        cutter=box('temporary trench cutter',(xx,6.4,-.12),(.20,8.4,.7),None)
        mod=slab.modifiers.new('recessed flush drainage trench','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter
        bpy.context.view_layer.objects.active=slab;bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cutter,do_unlink=True)
    # Large poured bays, saw-cut expansion joints, sparse replacement repair.
    for x in (-3.5,0,3.5):box('floor saw cut',(x,6.5,.0005),(.014,13,.003),'dark',0)
    for y in (2.6,5.2,7.8,10.4):box('floor saw cut',(0,y,.0005),(11,.014,.003),'dark',0)
    for x,y,w,d in [(-3.8,8.95,1.8,.52),(3.4,4.2,1.8,.38),(-4.1,3,1.35,.26)]:box('patched concrete',(x,y,.003),(w,d,.004),'patch',.005)
    # Level trench covers outside travel lane; no raised trip lips.
    for x in (-1.58,4.98):
        box('drain channel',(x,6.4,-.038),(.20,8.4,.065),'dark',.004)
        for j in range(67):box('drain flush grate',(x,2.25+j*.126,-.004),(.19,.036,.008),'steel',.002)
    for x in (-1.15,1.15):
        for y in (1.3,4.5,7.7,10.9):box('route worn edge',(x,y,.007),(.045,1.40,.002),'cream',.001)
    architecture(arch)

def sidewall(x,y0,y1):
    arch=before()
    box('WestWall' if x<0 else 'EastWall',(x,y0+(y1-y0)/2,2.9),(.30,y1-y0,5.8),'mineral',.018)
    inner=x+(.15 if x<0 else -.15)
    box('lower wall impact paint',(inner,y0+(y1-y0)/2,.56),(.018,y1-y0,1.1),'cream',.005)
    for y in (1.5,5.6,9.8,12.9):
        if y0<=y<=y1:
            box('steel column',(inner+(.08 if x<0 else -.08),y,2.83),(.16,.20,5.66),'dark',.009)
            box('column base shoe',(inner+(.1 if x<0 else -.1),y,.085),(.24,.34,.17),'steel',.006)
    for y in range(max(1,math.ceil(y0)),math.floor(y1)+1,2):
        box('wall control joint',(inner+(.012 if x<0 else -.012),y,3.35),(.007,.01,4.4),'dark',0)
    for z in (1.12,3.38):box('panel horizontal reveal',(inner,y0+(y1-y0)/2,z),(.024,y1-y0,.012),'dark',0)
    architecture(arch)

def ceiling(y0=0):
    arch=before()
    box('Ceiling',(0,(13+y0)/2,5.94),(11.6,13-y0,.28),'dark',.015)
    for y in (1.6,5.6,9.8,12.9):
        if y>=y0:
            box('roof girder lower flange',(0,y,5.41),(11.0,.23,.05),'steel',.007)
            box('roof girder web',(0,y,5.58),(11,.025,.34),'dark',.004)
            box('roof girder top flange',(0,y,5.76),(11,.23,.05),'steel',.007)
            for x in (-3.8,0,3.8):
                box('beam end gusset',(x,y,5.54),(.10,.23,.28),'steel',.005)
    architecture(arch)

def practical(name,x,y,z=4.65,power=240,color=(.80,.88,1.0)):
    start=before()
    for yy in (y-.56,y+.56):rod(name+' pendant',(x,yy,z+.12),(x,yy,5.8),.009,'edge')
    box(name+' steel batten',(x,y,z),(.25,1.45,.12),'steel',.012)
    box(name+' sealed diffuser',(x,y,z-.069),(.19,1.35,.035),'lamp',.015)
    for yy in (y-.45,y+.45):box(name+' retaining clip',(x,yy,z-.08),(.24,.015,.036),'dark',.003)
    area(name+' actual light',(x,y,z-.10),(x,y,0),power,color,1.2,'RECTANGLE',.18)
    group(name,start,'Ceiling',[[x,y-.56,5.8],[x,y+.56,5.8]],(0,0,1))

def rear_annex():
    arch=before()
    box('RearWall',(0,13.15,2.9),(11.6,.30,5.8),'mineral',.018)
    # Panel wall with a real door aperture, transom and glazed sidelights.
    box('Alcove wall west',(-5.1,9.98,1.65),(.80,.16,3.3),'cream',.012)
    box('Alcove wall east',(-2.55,9.98,1.65),(1.9,.16,3.3),'cream',.012)
    box('Alcove lintel',(-4.1,9.98,2.79),(1.2,.16,1.02),'cream',.012)
    box('Alcove side lower',(-1.68,11.53,.82),(.16,2.94,1.64),'cream',.012)
    box('Alcove side upper',(-1.68,11.53,3.0),(.16,2.94,.60),'cream',.012)
    for yy in (10.32,12.85):box('Alcove side pier',(-1.68,yy,2.17),(.16,.25,1.06),'cream',.010)
    for xx in (-4.75,-3.45):box('D02 metal jamb',(xx,10.005,1.14),(.10,.21,2.28),'dark',.012)
    box('D02 header',(-4.1,10.005,2.26),(1.42,.21,.10),'dark',.009)
    # Partition shifted 100mm toward pumps; full-width leaf clears bench approach.
    start=before();hinge=Vector((-4.74,10.145,0));theta=pi/2;u=Vector((cos(theta),sin(theta),0))
    o=box('D02 recessed door leaf',hinge+u*.61+Vector((0,0,1.1)),(1.22,.07,2.18),'teal',.006);o.rotation_euler.z=theta
    o=box('D02 pressed panel',hinge+u*.61+Vector((.040,0,1.15)),(.99,.014,1.45),'teal_light',.003);o.rotation_euler.z=theta
    for z in (.26,1.8):cyl('D02 hinge pin',hinge+Vector((0,0,z)),.032,.15,'edge',verts=24)
    h=hinge+u*1.02+Vector((0,0,1.05));rod('D02 lever',h+Vector((.04,-.04,0)),h-u*.13+Vector((.04,-.04,0)),.016,'edge')
    dr=group('D02 swinging leaf',start,'D02 metal jamb',[[-4.74,10.113,.26],[-4.74,10.113,1.8]],(0,-1,0));dr['interaction']='hinged door';dr['hinge_m']=list(hinge);dr['open_angle_deg']=90
    # Workshop clear height deliberately lower than mechanical room.
    box('Alcove ceiling',(-3.55,11.5,3.35),(3.9,3,.1),'dark',.005)
    for yy in (10.51,12.64):box('workshop glazing side frame',(-1.69,yy,2.17),(.19,.065,1.09),'dark',.008)
    for zz in (1.66,2.68):box('workshop glazing rail',(-1.69,11.575,zz),(.19,2.20,.065),'dark',.008)
    box('workshop glazing',(-1.68,11.575,2.17),(.016,2.08,.99),'glass',.002)
    # Human-height bench with bracing, under-shelf, drawers and a vise.
    bench_members=before();start=before()
    for x in (-4.95,-2.45):
        for y in (12.3,12.85):box('bench angle leg',(x,y,.442),(.05,.05,.884),'dark',.004)
    box('BenchTop',(-3.7,12.55,.91),(2.8,.70,.052),'wood',.005)
    box('bench rear folded upstand',(-3.7,12.8775,1.01),(2.8,.025,.20),'steel',.004)
    box('bench under shelf',(-3.7,12.57,.24),(2.68,.61,.027),'teal',.007)
    for x in (-4.92,-2.48):rod('bench diagonal brace',(x,12.32,.25),(x,12.82,.82),.015,'steel')
    for z in (.65,.79):
        box('bench shallow drawer',(-4.38,12.61,z),(.88,.58,.125),'teal',.012)
        rod('drawer pull',(-4.57,12.286,z),(-4.2,12.286,z),.015,'edge')
    group('maintenance workbench',start,'Floor',[[-4.95,12.3,0],[-2.45,12.85,0]])
    start=before();box('vise mounting sole',(-4.65,12.45,.957),(.35,.31,.042),'dark',.004)
    cyl('vise swivel base',(-4.65,12.45,.992),.14,.060,'teal',verts=48,bevel=.008)
    profile=[(-.23,0),(.23,0),(.19,.085),(.08,.14),(.07,.285),(-.018,.285),(-.025,.16),(-.12,.115),(-.23,.055)]
    vs=[(-4.59+a,12.45+b,1.024+c) for b in (-.105,.105) for a,c in profile];n=len(profile)
    mesh('vise cast arched body',vs,[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'teal',.009)
    box('vise sliding backbone',(-4.76,12.45,1.087),(.41,.073,.077),'edge',.002)
    box('vise moving jaw',(-4.82,12.45,1.229),(.067,.235,.16),'teal',.009)
    for xx in (-4.781,-4.620):
        box('vise hardened jaw insert',(xx,12.45,1.295),(.012,.232,.047),'edge',.001)
        for yy in (12.39,12.51):cyl('jaw fixing screw',(xx-.008,yy,1.295),.009,.006,'dark',(1,0,0),12,.001)
    rod('vise threaded shaft',(-5.01,12.45,1.084),(-4.45,12.45,1.084),.020,'edge')
    for i in range(11):torus('vise screw thread',(-4.97+i*.018,12.45,1.084),.021,.004,'dark',(1,0,0))
    rod('vise tommy bar',(-5.01,12.32,1.084),(-5.01,12.65,1.084),.010,'edge')
    for yy in (12.32,12.65):sphere('vise bar stop',(-5.01,yy,1.084),(.015,.015,.015),'edge')
    for xx in (-4.76,-4.55):
        for yy in (12.34,12.56):cyl('vise base bolt',(xx,yy,.991),.022,.026,'edge',verts=6,bevel=.002)
    group('bench vise',start,'BenchTop',[[-4.65,12.45,.936]])
    start=before();cloth('folded wiping rag',(-4.05,12.57,.936),.52,.38);group('bench cloth',start,'BenchTop',[[-4.05,12.57,.936]])
    start=before();wrench('large service spanner',(-3.78,12.39,.936),-.85);group('bench wrench',start,'BenchTop',[[-3.78,12.39,.936]])
    start=before();box('clipboard backing',(-2.78,12.49,.945),(.25,.35,.018),'dark',.002)
    box('shift repair sheet',(-2.78,12.49,.956),(.23,.325,.002),'paper',0)
    box('clipboard clip',(-2.78,12.633,.962),(.10,.026,.008),'edge',.002)
    text('work order','P-02\nSEAL / 17B\nRETURN TO SERVICE',(-2.78,12.54,.959),.025,'ink',(0,0,0))
    for j in range(4):box('work sheet pencil line',(-2.78,12.45-j*.025,.959),(.15,.002,.0005),'ink',0)
    group('maintenance clipboard',start,'BenchTop',[[-2.78,12.49,.936]])
    start=before();cyl('thermos body',(-3.10,12.74,1.071),.051,.27,'edge',bevel=.004);cyl('thermos rubber lid',(-3.10,12.74,1.221),.055,.034,'rubber',bevel=.003)
    for zz in (.944,1.198):torus('thermos rolled rim',(-3.10,12.74,zz),.052,.005,'dark')
    for i in range(20):
        ang=i*2*pi/20;rod('thermos cap grip',(-3.10+cos(ang)*.054,12.74+sin(ang)*.054,1.210),(-3.10+cos(ang)*.054,12.74+sin(ang)*.054,1.232),.0018,'edge',6)
    group('worker thermos',start,'BenchTop',[[-3.10,12.74,.936]])
    start=before()
    annulus('seal lower retainer',(-3.46,12.58,.949),.116,.059,.026,'steel')
    annulus('seal graphite ring',(-3.46,12.58,.980),.084,.058,.035,'rubber')
    annulus('seal upper retainer',(-3.46,12.58,1.024),.105,.059,.026,'edge')
    helix=[(-3.46+.088*cos(i*2*pi/32),12.58+.088*sin(i*2*pi/32),.969+i*.00034) for i in range(128)]
    pipe('seal compression spring',helix,.006,'edge',.015)
    for j in range(6):
        ang=j*pi/3;cyl('seal compression stud',(-3.46+.099*cos(ang),12.58+.099*sin(ang),1.039),.008,.017,'dark',verts=6,bevel=.001)
    group('spare mechanical seal',start,'BenchTop',[[-3.56,12.58,.936]])
    start=before()
    annulus('removed blackened seal ring',(-4.08,12.63,.951),.066,.045,.024,'rubber')
    annulus('worn seal ferrule',(-4.08,12.63,.969),.069,.046,.012,'steel')
    group('removed seal on rag',start,'folded wiping rag',[[-4.14,12.63,.950]])
    # Local top wear from tool use, broad scrape marks with nonuniform ends.
    for xx,yy,ww in [(-4.2,12.36,.15),(-3.61,12.38,.10),(-3.67,12.42,.22),(-4.4,12.33,.05)]:
        box('bench localized scrape',(xx,yy,.937),(ww,.005,.001),'wood_wear',.0005)
    # Unequal board joints and grain marks are restricted to this sacrificial timber worktop.
    for yy in (12.40,12.62,12.84):box('worktop board joint',(-3.70,yy,.937),(2.79,.003,.001),'dark',0)
    for j in range(23):
        yy=12.235+j*.031;xx=-4.84+(j%5)*.09
        pts=[(xx+q*.20,yy+.003*sin(q*.7+j),.9375) for q in range(5+(j%5))]
        pipe('sparse timber grain',pts,.0006,'wood_wear',.03)
    for ob in list(scene.objects):
        if ob.name not in bench_members and ob.parent is None:
            ob.location+=Vector((.05,.10,0))
            if 'support_anchors' in ob:
                ob['support_anchors']=[[p[0]+.05,p[1]+.10,p[2]] for p in ob['support_anchors']]
    # Task light physically fastened to rear wall; warm local pool.
    start=before();box('bench lamp backplate',(-3.6,12.978,1.70),(.14,.044,.20),'dark',.005)
    pipe('bench lamp arm',[(-3.6,12.96,1.7),(-3.6,12.68,1.93),(-3.6,12.50,1.93)],.014,'steel',.05)
    cyl('bench lamp shade',(-3.6,12.5,1.89),.115,.13,'cream')
    cyl('bench lamp lens',(-3.6,12.5,1.82),.095,.009,'lamp')
    area('bench warm pool',(-3.6,12.5,1.80),(-3.65,12.52,.91),24,(1,.80,.60),.20)
    group('bench practical lamp',start,'RearWall',[[-3.6,13,1.70]],(0,1,0))
    start=before();area('alcove practical',(-3.5,11.5,3.18),(-3.6,12.1,.7),48,(1,.90,.74),1.2)
    box('alcove luminaire',(-3.5,11.5,3.26),(.22,1.25,.08),'lamp',.008)
    group('alcove ceiling lamp',start,'Alcove ceiling',[[-3.5,11.5,3.30]],(0,0,1))
    # Small shift-work evidence: a clipped inspection sketch with bent corner.
    start=before()
    box('work order clip backplate',(-4.55,12.988,1.77),(.043,.024,.068),'edge',.002)
    mesh('wall inspection sheet',[(-4.70,12.975,1.72),(-4.40,12.975,1.73),(-4.40,12.960,1.33),(-4.66,12.975,1.32),(-4.70,12.95,1.36)],[(0,1,2,3,4)],'paper')
    text('inspection sheet heading','P-02 / SEAL REPAIR',(-4.55,12.953,1.663),.025,'ink')
    text('inspection sheet body','Isolated   /   02:10\nReplace packing\nFlush and prove flow',(-4.55,12.952,1.49),.018,'ink')
    group('clipped inspection sheet',start,'RearWall',[[-4.55,13,1.77]],(0,1,0))
    architecture(arch)

def west_services(ys):
    start=before()
    # Incoming primary RETURN at the reactor boundary, splits to pump suctions.
    pipe('PRIMARY RETURN header',[(-5.03,0,3.76),(-5.03,9.15,3.76)],.16,'cream')
    for y in ys:
        pipe('pump return branch '+str(y),[(-5.03,y,3.76),(-5.03,y,.91),(-4.69,y,.91)],.15,'cream',.24)
        flange('return isolation '+str(y),(-5.03,y,2.36),.225,(0,0,1))
        cyl('return valve bonnet',(-4.78,y,2.45),.085,.35,'teal',(1,0,0))
        wheel('return isolation wheel',(-4.55,y,2.45),.20,(1,0,0))
        pipe('pump discharge riser '+str(y),[(-4.1,y-.34,1.88),(-4.1,y-.34,3.05),(-4.43,y-.34,3.05)],.13,'cream',.22)
    pipe('pumped hot header',[(-4.43,2.5,3.05),(-4.43,9.0,3.05)],.14,'cream')
    for y in (2.1,5.9,8.9):
        # Wall brackets and straps, visibly load-bearing.
        box('pipe bracket wall pad',(-5.472,y,3.48),(.055,.20,.32),'steel',.005)
        box('pipe bracket arm',(-4.95,y,3.43),(1.02,.08,.08),'steel',.005)
        rod('pipe bracket knee',(-5.47,y,3.32),(-4.52,y,3.43),.029,'steel')
        torus('header clamp',(-5.03,y,3.76),.175,.016,'edge',(0,1,0))
        rod('return pipe standoff',(-5.03,y,3.44),(-5.03,y,3.585),.025,'steel')
        box('discharge bracket extension',(-4.20,y,3.18),(.06,.07,.50),'steel',.004)
        box('discharge hanger shelf',(-4.32,y,2.897),(.30,.07,.03),'steel',.003)
    for y in (1.3,6.0):
        cyl('return pipe identity band',(-5.03,y,3.76),.163,.19,'teal',(0,1,0),48,.001)
        cyl('hot pipe identity band',(-4.43,y,3.05),.143,.17,'orange',(0,1,0),48,.001)
    group('west primary pipework',start,'WestWall',[[-5.5,5.9,3.48],[-5.5,8.9,3.48]],(-1,0,0))

def exchanger():
    start=before();x=3.45;z=1.82
    for y in (5.50,8.27):
        box('HX soleplate',(x,y,.065),(2.12,.68,.13),'dark',.012)
        # Saddle custom cut profile embraces the circular barrel.
        profile=[(-.95,0),(.95,0),(.83,.55),(.68,.93)]
        profile += [(cos(pi*.18+(pi*.64)*i/16)*.89,1.69-sin(pi*.18+(pi*.64)*i/16)*.89) for i in range(17)]
        profile += [(-.68,.93),(-.83,.55)]
        vs=[(x+a,y+dy,.13+b) for dy in (-.22,.22) for a,b in profile];n=len(profile)
        mesh('HX sculpted saddle',vs,[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'teal',.018)
        for xx in (x-.81,x+.81):
            cyl('HX anchor washer',(xx,y,.143),.073,.022,'edge',verts=32)
            cyl('HX anchor hex',(xx,y,.17),.049,.042,'dark',verts=6)
    cyl('HX barrel',(x,6.93,z),.82,3.85,'cream',(0,1,0),96,.022)
    for y in (5.42,8.12):
        torus('HX shell seam',(x,y,z),.821,.016,'edge',(0,1,0))
    for y in (4.97,8.89):
        flange('HX bolted head '+str(y),(x,y,z),.94,(0,-1 if y<6 else 1,0),'steel',20,.91)
    sphere('HX front dished head',(x,4.79,z),(.79,.24,.79),'teal')
    sphere('HX bundle removable head',(x,9.05,z),(.79,.24,.79),'teal_light')
    torus('HX head weld',(x,9.20,z),.49,.013,'edge',(0,1,0))
    # Front primary hot inlet, rear cold outlet and separate secondary circuit.
    pipe('HX primary inlet neck',[(x,4.58,z),(x,4.05,z)],.14,'cream')
    flange('HX primary inlet flange',(x,4.28,z),.225,(0,-1,0))
    pipe('HX cooled outlet neck',[(x,8.30,2.53),(x,8.30,3.15),(4.99,8.30,3.15)],.15,'cream',.25)
    flange('HX upper outlet flange',(x,8.30,2.72),.23,(0,0,1))
    for y,zv,portz in ((5.8,1.70,3.0),(7.85,1.92,3.3)):
        pipe('secondary water nozzle',[(4.13,y,zv),(4.60,y,zv),(4.60,y,portz),(5.5,y,portz)],.10,'steel',.14)
        flange('secondary wall union',(4.9,y,portz),.17,(1,0,0),'steel',8)
        cyl('secondary blue ID',(5.2,y,portz),.104,.13,'blue',(1,0,0),40,.001)
        box('secondary wall sleeve',(5.478,y,portz),(.048,.38,.38),'dark',.006)
    gauge('HX inlet pressure',(3.12,4.56,2.21),.14)
    box('HX riveted rating plate',(3.46,4.552,1.53),(.62,.014,.24),'dark',.009)
    text('HX ID','HX-01 / COOLING', (3.46,4.541,1.57),.061)
    text('HX rating','TUBE BUNDLE / 240', (3.46,4.541,1.48),.034)
    for x1 in (3.19,3.73):
        for zz in (1.44,1.62):cyl('rating plate rivet',(x1,4.532,zz),.009,.009,'edge',(0,-1,0),12,.001)
    # Subtle isolated contact rub on service cover.
    for j in range(7):
        box('head rim paint rub',(3.2+j*.052,4.619,2.53),(.024,.01,.007),'edge',.002)
    group('HX-01 exchanger',start,'Floor',[[x,5.5,0],[x,8.27,0]])
    # Drain spur terminates in a covered tundish, not free-air pipe ends.
    start=before()
    pipe('HX drain',[(3.45,6.1,1.05),(3.45,6.1,.50),(4.71,6.1,.50),(4.71,6.1,.15)],.035,'steel',.1)
    wheel('drain cock',(3.77,6.03,.50),.09,(0,-1,0))
    box('drain tundish',(4.71,6.1,.04),(.22,.28,.08),'dark',.011)
    group('HX drain assembly',start,'Floor',[[4.71,6.1,0]])
    # Rail-mounted chain block, parked above the access envelope.
    hoist_start=before()
    box('bundle pull I beam web',(3.45,8.85,4.88),(.028,6.6,.28),'dark',.003)
    for zz in (4.73,5.03):box('bundle pull beam flange',(3.45,8.85,zz),(.23,6.6,.033),'steel',.004)
    for y in (5.6,9.8,12):rod('hoist beam hanger',(3.45,y,5.03),(3.45,y,5.8),.026,'steel')
    box('chain trolley bridge',(3.45,10.15,4.62),(.43,.28,.10),'teal',.018)
    for xx in (3.28,3.62):cyl('trolley wheel',(xx,10.15,4.76),.073,.045,'edge',(1,0,0),32)
    cyl('chainblock hoist',(3.45,10.15,4.38),.19,.24,'yellow',(0,1,0),40,.014)
    for i in range(35):
        torus('hoist short link',(3.45,10.15,4.20-i*.026),.019,.005,'dark',(0,1,0) if i%2 else (1,0,0))
    pipe('hoist forged hook',[(3.45,10.15,3.30),(3.45,10.15,3.14),(3.52,10.15,3.10),(3.60,10.15,3.17),(3.58,10.15,3.24)],.025,'edge',.04)
    group('HX dedicated hoist',hoist_start,'Ceiling',[[3.45,5.6,5.8],[3.45,12,5.8]],(0,0,1))
    # Dashed no-storage bay perimeter, not a decorative hazard carpet.
    for xx in (2.05,4.62):
        for yy in (9.7,10.7,11.7,12.5):box('tube pull bay marking',(xx,yy,.007),(.045,.52,.002),'yellow',.001)
    text('tube withdrawal floor label','BUNDLE PULL / KEEP CLEAR',(3.35,11.0,.009),.13,'cream',(0,0,-pi/2))

def entry():
    arch=before()
    # Open service shutter clear 5 x 5; tracks behind jambs, no route swing.
    for x in (-4.15,4.15):box('front facade',(x,.15,2.9),(2.70,.30,5.8),'mineral',.018)
    box('portal head',(0,.15,5.47),(5.6,.30,.66),'mineral',.012)
    for x in (-2.61,2.61):
        box('D01 reveal',(x,.23,2.5),(.20,.42,5.0),'dark',.012)
        box('D01 inner guide',(x,.30,2.5),(.05,.1,4.96),'edge',.004)
    box('D01 head track',(0,.24,5.11),(5.42,.38,.18),'dark',.012)
    for i in range(4):box('D01 raised folded shutter',(0,.37,5.30+i*.105),(5.01,.10,.097),'teal',.006)
    box('D01 threshold',(0,.18,-.004),(5,.36,.008),'steel',.002)
    text('entry department','COOLING / 02',(0,.319,5.03),.17,'paper',(pi/2,0,pi))
    architecture(arch)
    # Local reserve-power service point, not an entire duplicate reactor control.
    start=before()
    box('reserve service wall backplate',(5.473,2.03,1.22),(.055,.81,1.03),'steel',.007)
    box('reserve isolator folded enclosure',(5.22,2.03,1.22),(.46,.70,.88),'teal',.018)
    box('reserve hinged front',(4.978,2.03,1.22),(.028,.64,.80),'teal_light',.009)
    cyl('reserve power socket',(4.94,1.9,1.03),.088,.09,'dark',(1,0,0),32,.009)
    cyl('reserve cap',(4.88,1.9,1.03),.069,.043,'rubber',(1,0,0),32,.009)
    rod('reserve selector shaft',(4.96,2.13,1.35),(4.88,2.13,1.35),.021,'edge')
    box('reserve guarded lever',(4.88,2.13,1.40),(.05,.035,.13),'red',.010)
    text('reserve label','RESERVE\nRESTART',(4.955,2.03,1.57),.069,'paper',(pi/2,0,-pi/2))
    pipe('reserve cable upfeed',[(5.27,2.03,1.66),(5.27,2.65,1.66),(5.27,2.65,3.0),(5.27,.0,3.0)],.024,'dark',.08)
    bpy.data.objects['reserve cable upfeed']['envelope_role']='utility'
    group('reserve restart socket',start,'EastWall',[[5.5,2.03,1.22]],(1,0,0))
    # Emergency hose connection, capped and clearly usable from front apron.
    start=before()
    pipe('mine water contingency port',[(5.5,3.15,.78),(5.0,3.15,.78)],.076,'steel')
    flange('mine water cap flange',(4.95,3.15,.78),.13,(1,0,0),'steel',6)
    cyl('mine water blank cap',(4.86,3.15,.78),.102,.035,'blue',(1,0,0),40)
    wheel('mine water isolation',(4.98,3.15,1.13),.15,(0,-1,0),'blue')
    cyl('mine water valve bonnet',(4.98,3.15,.955),.054,.35,'steel')
    box('mine water mounting sleeve',(5.478,3.15,.78),(.044,.32,.32),'dark',.006)
    group('mine water connection',start,'EastWall',[[5.5,3.15,.78]],(1,0,0))

floor();sidewall(-5.65,0 if args.stage=='full' else 5.6,13);ceiling(0 if args.stage=='full' else 5.6);rear_annex()
pump('P-02',7.60);west_services([7.6]);cart('service cart',-2.47,10.95)
practical('pump task light',-3.2,7.3,4.25,210,(.93,.92,.85))
area('west wall rake',(-4.70,9.4,4.8),(-5.48,7.1,1.8),100,(.90,.92,1),1.7)
area('soft motor return',(-.3,7.0,2.5),(-3.0,7.6,1.0),42,(.70,.81,1.0),2.2)
if args.stage=='full':
    sidewall(5.65,0,13);entry();pump('P-01',4.15)
    p01_services=before()
    # P-01 primary branches join existing headers.
    pipe('P01 return branch',[(-5.03,4.15,3.76),(-5.03,4.15,.91),(-4.69,4.15,.91)],.15,'cream',.24)
    flange('P01 return isolation',(-5.03,4.15,2.36),.225,(0,0,1));wheel('P01 isolation',(-4.55,4.15,2.45),.20,(1,0,0))
    cyl('P01 valve bonnet',(-4.78,4.15,2.45),.085,.35,'teal',(1,0,0))
    pipe('P01 discharge branch',[(-4.1,3.81,1.88),(-4.1,3.81,3.05),(-4.43,3.81,3.05)],.13,'cream',.22)
    for ob in list(scene.objects):
        if ob.name not in p01_services and ob.parent is None:ob.parent=bpy.data.objects['west primary pipework']
    exchanger()
    hotstart=before()
    pipe('hot crossfeed to HX',[(-4.43,2.50,3.05),(-4.43,2.50,4.22),(3.45,2.50,4.22),(3.45,4.05,4.22),(3.45,4.05,1.82)],.14,'cream',.33)
    bpy.data.objects['hot crossfeed to HX'].parent=bpy.data.objects['west primary pipework']
    supply_start=before()
    pipe('cooled SUPPLY return to reactor',[(4.99,8.30,3.15),(4.99,8.30,3.76),(4.99,0,3.76)],.15,'cream',.28)
    for y in (1.6,5.6,8.5):
        box('supply wall bracket',(5.22,y,3.54),(.53,.07,.07),'steel',.005)
        box('supply bracket backplate',(5.478,y,3.64),(.044,.20,.27),'steel',.005)
        torus('supply clamp',(4.99,y,3.76),.167,.014,'edge',(0,1,0))
        rod('supply clamp stem',(4.99,y,3.57),(4.99,y,3.60),.022,'edge')
    for y in (1.2,5.6):cyl('supply teal band',(4.99,y,3.76),.153,.2,'teal',(0,1,0),48,.001)
    group('east primary supply',supply_start,'EastWall',[[5.5,5.6,3.64]],(1,0,0))
    practical('entry batten',1.75,1.55,5.10,360,(.78,.86,1))
    practical('lead pump practical',-3.2,3.90,4.25,300,(.92,.92,.84))
    practical('exchanger practical',2.25,6.45,4.60,420,(.86,.93,1))
    practical('rear circulation practical',.1,11.4,4.80,150,(.88,.91,1))
    area('exchanger side wall shaping',(4.90,8.5,4.90),(4.0,6.2,1.3),220,(1,.82,.60),2.0)
    area('entry borrowed corridor light',(0,.3,3.80),(0,6,1),190,(.82,.89,1),3.0)
    from develop_room import develop
    develop()
    contract=json.loads((ROOT/'interface.json').read_text(encoding='utf-8'))
    for port in contract['portals']+contract['utilities']['sockets']:
        marker=bpy.data.objects.new(port['id'],None);scene.collection.objects.link(marker)
        marker.location=port.get('threshold',port.get('position',[0,0,0]));marker.empty_display_type='ARROWS';marker.empty_display_size=.25
        marker['connection_id']=port['id'];marker['contract_json']=json.dumps(port)

CAMERAS=[
 ('C01_ENTRY',(0,.65,1.68),(0,6.8,1.60),26),
 ('C02_HERO',(-.68,2.25,1.68),(2.9,6.7,1.9),28),
 ('C03_REVERSE',(.45,11.95,1.68),(-.15,3.7,1.75),26),
 ('C04_ROUTE',(.00,5.1,1.68),(.1,11.3,1.50),26),
 ('C05_PUMP_A',(-.65,2.40,1.68),(-3.63,4.24,1.00),30),
 ('C06_EXCHANGER',(.90,3.60,1.68),(3.63,7.0,1.73),24),
 ('C07_PINCH',(-.30,5.84,1.68),(-3.55,8.48,1.48),28),
 ('C08_WORKSHOP',(-3.91,10.57,1.68),(-3.69,12.59,1.11),27),
 ('C09_BUNDLE_BAY',(.50,12.25,1.68),(3.53,9.1,1.55),24),
 ('C10_MATERIALS',(-1.84,6.75,1.50),(-3.04,7.63,1.01),46),
]
for name,loc,target,lens in CAMERAS:camera(name,loc,target,lens)
WALK_CAMERAS=[
 ('W01_ENTRY_APPROACH',(0,.12,1.68),(0,6.5,1.5),20),
 ('W02_RESERVE_APRON',(3.4,.85,1.68),(5.1,2.5,1.35),28),
 ('W03_PUMP_OPERATOR',(-2.0,5.82,1.68),(-4.6,7.6,1.4),24),
 ('W04_ALCOVE_APPROACH',(-4.1,8.95,1.68),(-4.1,11.4,1.4),20),
 ('W05_WORKSHOP_ROUTE',(-3.8,10.6,1.68),(-3.0,12.1,1.35),20),
 ('W06_WITHDRAWAL_CLEAR',(-.10,11.05,1.68),(3.5,11.05,1.25),18),
 ('W07_SECONDARY_SERVICE',(5.08,10.5,1.68),(4.9,6.7,1.6),20),
 ('W08_RETURN_THRESHOLD',(.65,6.25,1.68),(0,0,2.05),18),
]
for name,loc,target,lens in WALK_CAMERAS:camera(name,loc,target,lens)
scene.camera=bpy.data.objects['C07_PINCH' if args.stage=='slice' else 'C01_ENTRY']
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.cycles.seed=87
scene.cycles.max_bounces=7;scene.cycles.diffuse_bounces=4;scene.cycles.glossy_bounces=4;scene.cycles.transmission_bounces=5
scene.render.resolution_x=1440;scene.render.resolution_y=960;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.10
scene.world=bpy.data.worlds.new('low indirect environment');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.32,.39,.46,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.055
wn=scene.world.node_tree.nodes;wl=scene.world.node_tree.links
bg=wn.get('Background');boundary=wn.new('ShaderNodeBackground');boundary.name='Unassembled boundary neutral backdrop';boundary.inputs[0].default_value=(.15,.15,.15,1);boundary.inputs[1].default_value=1
lp=wn.new('ShaderNodeLightPath');mix=wn.new('ShaderNodeMixShader');wl.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);wl.new(bg.outputs[0],mix.inputs[1]);wl.new(boundary.outputs[0],mix.inputs[2]);wl.new(mix.outputs[0],wn.get('World Output').inputs[0])
scene.render.film_transparent=False
scene['contacts_json']=json.dumps(CONTACTS);scene['assemblies_json']=json.dumps(ASSEMBLIES)
scene['camera_manifest_json']=json.dumps([dict(id=n,position_m=p,target_m=t,lens_mm=l) for n,p,t,l in CAMERAS])
out=HERE/args.output;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(ROOT/'production'/'cameras.json').write_text(scene['camera_manifest_json'],encoding='utf-8')
(ROOT/'production'/'build_manifest.json').write_text(json.dumps(dict(revision=args.revision,stage=args.stage,source_sha256=scene['source_sha256'],objects=len(scene.objects),materials=len(bpy.data.materials),blend=str(out),fixed_cameras=10,supplementary_cameras=8,total_cameras=18),indent=2))
print('COOLING_BUILD_OK '+json.dumps(dict(revision=args.revision,stage=args.stage,objects=len(scene.objects),file=str(out))))
