"""Deterministic electrical overhaul from the preserved E05 module, slice first."""
import bpy,sys,math,hashlib,json,argparse
from pathlib import Path
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));import kit as k
parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=['slice','full'],default='slice');parser.add_argument('--output',required=True)
a=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(a.output).resolve();base=Path(bpy.data.filepath)
assert not any(o.name.startswith(k.PREFIX) for o in bpy.data.objects),'Build from preserved baseline, not a previous overhaul'
baseline_sha=hashlib.sha256(base.read_bytes()).hexdigest()
original_names=set(o.name for o in bpy.data.objects)
# The current map's baked electrical cache links original material IDs from this
# module. Keep the original definitions even when the new room no longer uses
# them; dropping unused IDs would break the map before its cache is refreshed.
for material in bpy.data.materials:
    material.use_fake_user=True
k.collection('Repair workshop');m=k.palette()
# Replace the inherited repair bench and its small primitive dressing. Preserve
# the cart/lockout station until the polished bench slice has been reviewed.
for o in list(bpy.data.objects):
    if o.get('assembly_member')=='WB01_Repair_bench':bpy.data.objects.remove(o,do_unlink=True)
k.root('Repair bench frame','Floor',[[-3.81,12.8,0],[-5.03,12.8,0],[-3.81,14.96,0],[-5.03,14.96,0]])
for x in [-3.81,-5.03]:
    for y in [12.8,14.96]:
        k.box('Bench rubber foot',(x,y,.022),(.095,.095,.044),m['rubber'],.007)
        k.box('Bench folded leg',(x,y,.48),(.05,.05,.876),m['slate'],.003)
        k.bolt('Bench leg fixing',(x+.026,y,.78),(1,0,0),m['zinc'])
    k.box('Bench long apron',(x,13.88,.835),(.045,2.21,.135),m['slate'])
for y in [12.8,14.96]:k.box('Bench cross brace',(-4.42,y,.32),(1.26,.045,.045),m['slate'])
k.box('Bench lower shelf',(-4.42,13.88,.365),(1.20,2.13,.035),m['zinc'])
k.box('Bench thick phenolic top',(-4.42,13.88,.98),(1.55,2.5,.08),m['wood'],.009)
k.box('Bench front steel edge',(-3.643,13.88,.964),(.009,2.48,.039),m['steel'],.002)
k.box('Bench insulating service mat',(-4.14,13.83,1.026),(.80,1.36,.012),m['rubber'],.007)
for y in [13.41,13.9,14.39]:
    k.box('Drawer side return',(-4.38,y,.73),(1.04,.022,.18),m['slate'])
for z in [.635,.827]:k.box('Drawer folded housing',(-4.39,13.9,z),(1.05,1.0,.025),m['slate'])
k.box('Drawer recessed face',(-3.88,13.9,.731),(.04,.96,.154),m['oxide'],.007)
k.tube('Drawer bowed pull',[(-3.85,13.73,.73),(-3.795,13.73,.73),(-3.795,14.06,.73),(-3.85,14.06,.73)],.011,m['steel'])
# Local wall construction: backing remains the original fixed wall.
k.root('Workshop wall panels','West wall',[[-5.5,13.63,2.2],[-5.5,15,2.2]],'WORLD_-X')
for y in [12.36,13.63,14.90]:
    k.box('Wall raised mineral panel',(-5.4775,y,2.9),(.045,1.237,2.25),m['cream'],.003)
    k.box('Wall lower impact liner',(-5.478,y,.85),(.044,1.237,1.48),m['slate'],.004)
    k.box('Wall panel seated cap',(-5.46,y,1.605),(.072,1.25,.025),m['zinc'])
k.root('Bench tool rack','Floor',[[-5.05,12.8,0],[-5.05,14.96,0]])
for y in [12.8,14.96]:k.box('Rack steel upright',(-5.05,y,1.1),(.035,.035,2.2),m['slate'])
k.box('Rack recessed backplate',(-5.066,13.88,1.765),(.02,2.18,.61),m['replacement'])
k.ring('Rack folded perimeter',-5.037,13.88,1.765,2.22,.65,.026,.036,m['slate'])
for y in [12.85,13.4,13.95,14.5,14.91]:
    for z in [1.54,2.00]:k.bolt('Rack screw',(-5.015,y,z),(1,0,0),m['zinc'],.007)
for i,y in enumerate([13.00,13.23,13.51]):
    z=1.89;k.tube('Tool hanging peg',[(-5.025,y,z),(-4.96,y,z),(-4.96,y,z+.018)],.006,m['steel'])
    # Open jaw spanner: forked open head, tapered shaft and a ring lower end.
    k.box('Spanner shank',(-4.966,y,1.70),(.012,.034,.27),m['steel'],.004)
    k.tube('Spanner open jaw',[(-4.966,y-.052,1.93),(-4.966,y-.042,1.884),(-4.966,y+.042,1.884),(-4.966,y+.052,1.93)],.012,m['zinc'])
    r=.032;rot=Matrix.Rotation(math.pi/2,3,'Y')
    k.lathe('Spanner ring',(-4.966,y,1.55),[(r,-.007),(r,.007),(.019,.007),(.019,-.007),(r,-.007)],m['zinc'],rot=rot)
for y in [13.85,14.08]:
    k.tube('Screwdriver hang hook',[(-5.026,y,1.95),(-4.968,y,1.95),(-4.968,y,1.97)],.005,m['steel'])
    k.lathe('Insulated driver handle',(-4.958,y,1.83),[(0,0),(.018,0),(.023,.025),(.02,.11),(.014,.13),(0,.13)],m['ochre'],24)
    k.cyl('Driver steel shaft',(-4.958,y,1.59),(-4.958,y,1.83),.003,m['steel'])
    for z in [1.86,1.89,1.92]:k.lathe('Driver grip ring',(-4.958,y,z),[(.021,0),(.021,.006),(.018,.006),(.018,0),(.021,0)],m['rubber'],24)
# Articulated bench lamp: distinct base, elbows, double arms and spun metal hood.
k.root('Bench task lamp','EOH | Bench thick phenolic top',[[-4.82,14.74,1.02]])
k.lathe('Lamp cast base',(-4.82,14.74,1.02),[(0,0),(.10,0),(.11,.02),(.09,.04),(.035,.052),(0,.052)],m['slate'])
k.tube('Lamp jointed arm',[(-4.82,14.74,1.07),(-4.96,14.74,1.48),(-4.57,14.56,1.82),(-4.40,14.56,1.82)],.013,m['slate'])
k.tube('Lamp parallel tension arm',[(-4.86,14.71,1.07),(-5,14.71,1.48),(-4.61,14.53,1.82)],.009,m['steel'])
for x,z in [(-4.82,1.09),(-4.96,1.48),(-4.57,1.82)]:k.cyl('Lamp knuckle',(x,14.71,z),(x,14.77,z),.035,m['zinc'])
k.lathe('Lamp spun hood',(-4.39,14.56,1.69),[(.15,0),(.15,.012),(.085,.13),(.04,.16),(.022,.16),(.06,.11),(.13,.016),(.15,0)],m['oxide'])
k.cyl('Lamp frosted diffuser',(-4.39,14.56,1.687),(-4.39,14.56,1.692),.13,m['ceramic'])
k.lamp('Bench practical',(-4.39,14.56,1.68),(-4.1,14,1.02),32,(1,.78,.53),.23)
# Hollow mug and a visible coffee stain; paper has thickness and a curled corner.
k.root('Mug assembly','EOH | Bench thick phenolic top',[[-4.76,12.98,1.02]])
k.lathe('Mug ceramic shell',(-4.76,12.98,1.02),[(0,0),(.042,0),(.048,.007),(.049,.12),(.046,.126),(.041,.124),(.04,.012),(0,.012)],m['ceramic'])
k.tube('Mug C handle',[(-4.718,12.98,1.12),(-4.688,12.98,1.117),(-4.67,12.98,1.09),(-4.679,12.98,1.062),(-4.718,12.98,1.049)],.007,m['ceramic'])
k.cyl('Mug coffee surface',(-4.76,12.98,1.113),(-4.76,12.98,1.114),.041,m['coffee'])
k.lathe('Mug stained lip',(-4.76,12.98,1.144),[(.044,0),(.044,.001),(.041,.001),(.041,0),(.044,0)],m['coffee'])
k.root('Clipboard assembly','EOH | Bench thick phenolic top',[[-4.61,13.32,1.02]])
k.box('Clipboard backing',(-4.61,13.32,1.024),(.22,.31,.008),m['wood'],.004)
def sheet(b):
    pts=[(-4.71,13.18),(-4.51,13.18),(-4.51,13.44),(-4.535,13.465),(-4.71,13.465)]
    b.prism(pts,.0015,m['paper'],z0=1.029)
k.add('Shift sheet',sheet)
k.tube('Curled paper corner',[(-4.535,13.44,1.03),(-4.529,13.459,1.034),(-4.515,13.463,1.045),(-4.508,13.455,1.049)],.002,m['paper'])
k.box('Clipboard spring clip',(-4.61,13.444,1.033),(.066,.027,.006),m['steel'])
for i in range(7):k.box('Paper ruled record',(-4.61,13.22+i*.025,1.031),(.158-(i%3)*.018,.001,.0008),m['ink'],0)
k.text('Shift sheet heading','SHIFT  /  03',(-4.691,13.397,1.032),.016,m['ink'],'Z')
# Cartridge fuses have inset ceramic barrel, rolled caps and contact blades.
k.root('Spare fuses','EOH | Bench insulating service mat',[[-4.19,13.75,1.032],[-4.05,14.04,1.032]])
for y in [13.73,14.06]:
    k.box('Fuse cradle',(-4.18,y,1.05),(.46,.16,.036),m['slate'],.006)
    k.cyl('Fuse ceramic barrel',(-4.36,y,1.107),(-4.07,y,1.107),.054,m['ceramic'])
    for x in [-4.374,-4.06]:
        k.lathe('Fuse crimped end cap',(x,y,1.107),[(0,-.012),(.055,-.012),(.058,-.007),(.058,.007),(.054,.014),(0,.014)],m['zinc'],rot=Matrix.Rotation(math.pi/2,3,'Y'))
        sign=-1 if x<-4.2 else 1
        k.box('Fuse knife contact blade',(x+sign*.046,y,1.107),(.092,.033,.021),m['copper'],.002)
        k.bolt('Fuse contact retaining screw',(x+sign*.024,y,1.118),(0,0,1),m['steel'],.007)
    for x in [-4.328,-4.104]:
        k.lathe('Fuse ceramic shoulder',(x,y,1.107),[(.054,0),(.059,0),(.059,.009),(.054,.009),(.054,0)],m['ceramic'],rot=Matrix.Rotation(math.pi/2,3,'Y'))
    k.box('Fuse ceramic batch imprint',(-4.23,y,1.161),(.075,.027,.001),m['ink'],.0003)
    k.text('Fuse ceramic stamp','F-06',(-4.15,y-.041,1.144),.013,m['ink'],'Z')
# Soft folded gloves: cuff, palm and separately tapered fingers, broad folds.
k.root('Folded insulating gloves','EOH | Bench thick phenolic top',[[-4.71,14.31,1.02]])
def gloves(b):
    for dx,dy in [(0,0),(.16,.045)]:
        x=-4.70+dx;y=14.30+dy
        b.pillow(.12,.17,.027,(x,y,1.012),m['ochre'],n=8)
        for i in range(4):
            length=[.075,.102,.094,.069][i]
            b.tube([(x-.043+i*.028,y+.057,1.046),(x-.043+i*.028,y+.09,1.052),(x-.036+i*.028,y+.057+length,1.034)],.012,m['ochre'])
        b.tube([(x+.05,y-.005,1.044),(x+.082,y+.02,1.043),(x+.092,y+.062,1.034)],.015,m['ochre'])
        b.lathe([(.055,0),(.053,.047),(.041,.047),(.043,0),(.055,0)],(x,y-.077,1.047),m['rubber'],seg=32,rot=Matrix.Rotation(math.pi/2,3,'X'),scale=(1,.40,1))
        b.tube([(x-.039,y,1.047),(x-.012,y+.009,1.063),(x+.028,y+.012,1.057)],.002,m['oxide'])
k.add('Folded working gloves',gloves)
k.root('Canvas service bag','EOH | Bench lower shelf',[[-4.35,13.88,.3825]])
k.box('Bag reinforced cloth base',(-4.35,13.88,.4),(.62,.89,.035),m['cloth'],.008)
def bag(b):
    b.pillow(.62,.89,.30,(-4.35,13.88,.4095),m['cloth'],n=10)
    b.ribbon([(13.44,.59),(13.46,.69),(13.72,.74),(14.18,.73),(14.30,.62)],-4.64,-4.07,.009,m['cloth'])
k.add('Soft canvas maintenance bag',bag)
for y in [13.60,14.13]:
    k.tube('Bag webbing handle',[(-4.55,y,.58),(-4.57,y,.79),(-4.18,y,.79),(-4.15,y,.58)],.012,m['rubber'])
    k.box('Bag strap reinforcement',(-4.15,y,.55),(.014,.08,.14),m['rubber'])
k.tube('Bag zipper piping',[(-4.642,13.48,.59),(-4.642,13.7,.64),(-4.642,14.16,.64),(-4.642,14.29,.57)],.003,m['steel'])
k.box('Bag stitched ID patch',(-4.028,13.73,.515),(.003,.22,.09),m['paper'],.001)
k.text('Bag department marking','E / 03',(-4.025,13.64,.498),.038,m['ink'])
# A formed tool case, open, foam recesses, hinge pins and carry grip.
k.root('Open tool case','EOH | Bench thick phenolic top',[[-4.49,14.75,1.02]])
k.box('Case bottom',(-4.46,14.71,1.05),(.53,.34,.06),m['rubber'],.016)
k.box('Case foam insert',(-4.46,14.71,1.082),(.49,.3,.012),m['slate'],.009)
for yy in [14.55,14.87]:k.box('Case formed rim',(-4.46,yy,1.094),(.53,.018,.025),m['oxide'],.005)
for xx in [-4.716,-4.204]:k.box('Case return rim',(xx,14.71,1.094),(.018,.3,.025),m['oxide'],.005)
k.box('Case raised lid',(-4.70,14.71,1.22),(.035,.345,.3),m['oxide'],.015)
k.box('Case lid padded inside',(-4.68,14.71,1.22),(.009,.31,.26),m['rubber'],.009)
for yy in [14.60,14.82]:k.cyl('Case hinge pin',(-4.705,yy-.045,1.10),(-4.705,yy+.045,1.10),.008,m['steel'])
k.tube('Case carry grip',[(-4.206,14.63,1.09),(-4.16,14.63,1.09),(-4.16,14.8,1.09),(-4.206,14.8,1.09)],.009,m['rubber'])
for y in [14.64,14.76]:
    k.lathe('Case driver handle',(-4.41,y,1.088),[(0,0),(.016,0),(.019,.07),(.011,.10),(0,.10)],m['ochre'],rot=Matrix.Rotation(math.pi/2,3,'Y'))
    k.cyl('Case driver shaft',(-4.64,y,1.106),(-4.41,y,1.106),.003,m['zinc'])
# Selective use: exposed steel on pull and a small repair patch, no blanket grunge.
k.root('Bench wear','EOH | Bench thick phenolic top',[[-3.71,13.04,1.02]])
for i in range(5):
    y=13.04+i*.035;k.box('Localized worktop scratch',(-3.71+i%3*.009,y,1.0205),(.022+i%3*.007,.0015,.001),m['paper'],0)
if a.stage=='full':
    exec((Path(__file__).with_name('expand.py')).read_text(),globals())
    from door_history import apply as apply_door_history
    apply_door_history(k,m)
# Neutral overhead fill is tied to the existing fluorescent practical in this bay.
rear=bpy.data.objects.get('West rear practical light')
if rear:rear.data.color=(.79,.88,1);rear.data.energy=290
if a.stage=='full':
    from surface_finish import apply as apply_surface_finish
    apply_surface_finish(k,m)
    from lead_finish import apply as apply_lead_finish
    from vision_finish import apply as apply_vision_finish
    apply_lead_finish(k,m)
    apply_vision_finish()
    from reserve_finish import apply as apply_reserve_finish
    apply_reserve_finish(k,m)
bpy.context.scene['electrical_overhaul_stage']=a.stage;bpy.context.scene['electrical_baseline_sha256']=baseline_sha
bpy.context.scene['electrical_reference']='Reworked spawn module / final-pass renders; independent reference=100'
bpy.context.view_layer.update()
out.parent.mkdir(parents=True,exist_ok=True);bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
print('OVERHAUL_SAVED',out,'STAGE',a.stage,flush=True)
# This cloud host's PulseAudio teardown hangs even with -noaudio. All intended
# outputs are closed and saved before the success-only process termination.
import os
sys.stdout.flush();sys.stderr.flush();os._exit(0)
