"""Fifty immutable camera/state pairs for the whole mine quality pass."""
import bpy,json
from mathutils import Vector

def f(y):return -.025*max(y,0)
def h(x,y,z):return (x,y,f(y)+z)

def build_cameras(scene):
    for o in list(scene.objects):
        if o.type=='CAMERA':bpy.data.objects.remove(o,do_unlink=True)
    c=bpy.data.collections.new('Q50_FIXED_REVIEW_CAMERAS');scene.collection.children.link(c)
    rows=[]
    def add(title,pos,target,lens=26,sector=None,state=None,gate=1,kind='gameplay'):
        rows.append({'id':f'CAM_{len(rows)+1:02}','title':title,'position':pos,'target':target,'lens':lens,'sector':sector,'state':state,'gate':gate,'kind':kind})
    add('Facility approach and preparation',(3.7,-13.05,1.72),(-.15,1,2.18),23)
    add('Preparation reverse',(1.8,-1.5,1.65),(0,-15,1.0),25)
    add('Weathered charge issue',(2.75,-10.1,1.65),(6.25,-7.6,1.45),38)
    add('Corroded blast door',(2.8,-5.4,1.65),(4.4,-.79,1.9),32)
    add('Rough concrete and rail transition',(-1.6,-7,.40),(0,-1,.10),27,kind='detail')
    add('Preparation circulation overview',(9.8,-17.2,4.05),(-.5,-4,2.3),27,kind='overview')
    add('Instructions and worn workbench',(-3.45,-7.5,1.72),(-7.30,-8.8,2.04),30)
    add('Wooden cart from player height',(1.55,-11,1.68),(0,-8.8,.80),30)
    add('Door lower track and threshold',(2.8,-2.5,.65),(3.3,-.79,.35),35,kind='detail')
    add('Canopy and service connections',(2.6,-8.3,1.65),(0,-4,4.2),25)
    add('Portal to sloping adit',(1.8,-1,1.70),h(.1,6,1.6),24)
    add('Main working route',h(1.95,3.2,1.80),h(-.50,19.4,1.78),23)
    add('Main route reverse',h(1.93,14.6,1.80),(-.1,-3,1.80),25)
    add('Rail level contact view',h(.17,6,.43),h(0,13,.10),27,kind='detail')
    add('Walkway and drainage edge',h(1.95,8,1.65),h(2.1,15,.20),26)
    add('Support to geology contact',h(1.8,9.5,1.70),h(2.8,11.3,1.10),29)
    add('Rusted utility route',h(-1.3,10,1.65),h(-2.4,13,2.35),29)
    add('Mid-adit darkness and work lights',h(1.9,20,1.65),h(0,28,1.40),24)
    add('Loaded wooden cart and passing space',h(1.8,24.8,1.65),h(0,22.7,.75),29)
    add('Ventilation and ceiling',h(.5,16,2.0),h(.6,22,3.4),25)
    add('A dry sector sealed',h(-2.2,17.8,1.70),h(-3.9,17.8,1.50),26,'A',0)
    add('A dry shallow pocket',h(-2.7,17.6,1.73),h(-8.8,17.9,1.20),26,'A',1)
    add('A dry extended chamber',h(-4.65,17.8,1.66),h(-10.5,17.8,.90),26,'A',2)
    add('A dry deep extraction',h(-8.3,17.7,1.70),h(-14.5,18.8,1.50),26,'A',3)
    add('A settled collapse',h(-2.7,17.6,1.73),h(-7.5,17.8,.90),26,'A',4)
    add('B wet sector sealed',h(3.55,32.4,1.76),h(10.1,33.15,1.20),26,'B',0)
    add('B wet shallow pocket',h(3.55,32.4,1.76),h(10.1,33.15,1.20),26,'B',1)
    add('B wet extended chamber',h(5.5,32.7,1.70),h(10,33,1.20),26,'B',2)
    add('B wet deep excavation',h(8.6,33,1.70),h(14,34,1.30),26,'B',3)
    add('B settled collapse',h(3.55,32.4,1.76),h(7.5,33,.90),26,'B',4)
    add('C deep sector sealed',h(1.65,36.4,1.76),h(0,42,1.27),26,'C',0)
    add('C shallow working space',h(1.65,36.4,1.76),h(0,42,1.27),26,'C',1)
    add('C extended working space',h(.8,40.7,1.70),h(0,45.5,1.10),26,'C',2)
    add('C deep branching excavation',h(.5,44.9,1.70),h(0,51.4,1.40),26,'C',3)
    add('C settled collapse',h(1.65,36.4,1.76),h(0,42,1.27),26,'C',4)
    add('Sump and service overview',h(6.4,18.8,1.74),h(9,22,.80),25)
    add('Sump rail and walkway contact',h(7.7,20.5,1.70),h(8.4,21.5,.50),30)
    add('Dirty water and mineral rim',h(8,20.6,1.10),h(9.4,21.8,-.30),32,kind='detail')
    add('Pump and damp services',h(7.1,17.9,1.65),h(10,18.5,.50),30)
    add('Service alcove reverse',h(8.3,24,1.70),h(6.6,20,1.50),26)
    add('Anchored ceiling web',h(1.75,12.8,1.72),h(-1.8,15,2.90),35,kind='detail')
    add('Discarded rotten timber',h(8.35,15,1.65),h(9.25,16.45,.35),33,kind='detail')
    add('Eerie return loop',h(6,27.6,1.70),h(8.2,24.9,1.50),25)
    add('Fracture and rubble contact',h(-2.7,17.6,1.4),h(-5.7,17.8,.55),38,'A',4,kind='detail')
    add('Damp mineral bleeding',h(-1.2,22.4,1.65),h(-2.3,24.5,2),35,kind='detail')
    add('Cabinet wear and readable issue label',(4,-8.7,1.60),(5.85,-7.6,2.35),38,kind='detail')
    add('Blast door closed from mine side',h(1.8,2.5,1.68),(0,-.8,1.80),24,gate=0)
    add('Cart interior from standing eye',(1.05,-9.8,1.65),(0,-8.8,.80),30,kind='gameplay')
    add('Deep-route silhouette and dark gaps',h(1.8,29.5,1.70),h(0,37,1.40),25,'C',4)
    add('Final entry atmosphere',(2.7,-11.5,1.65),(0,2,1.90),23)
    assert len(rows)==50
    for r in rows:
        cam=bpy.data.cameras.new(r['id']);cam.lens=r['lens'];cam.clip_start=.025;cam.clip_end=180
        o=bpy.data.objects.new(r['id'],cam);c.objects.link(o);o.location=r['position'];o.rotation_euler=(Vector(r['target'])-o.location).to_track_quat('-Z','Y').to_euler()
        o['q50_camera']=True;o['q50_view']=json.dumps(r);o['csm_camera_key']=r['id'];o['csm_gameplay_camera']=r['kind']=='gameplay'
    scene.camera=scene.objects['CAM_01'];scene['q50_cameras']=json.dumps(rows)
    return rows

def set_review_state(scene,row):
    states={'A':1,'B':2,'C':4}
    if row.get('sector'):states[row['sector']]=int(row['state'])
    data={k:{'state':v,'unlocked_stage':3 if v==4 else v,'remaining_rubble':22 if v==4 else 0,'cleared_rubble':[]} for k,v in states.items()}
    scene['csm_states_json']=json.dumps(data)
    for o in scene.objects:
        if 'csm_meta' not in o:continue
        m=json.loads(o['csm_meta']);visible=True;sec=m.get('sector')
        if m.get('collision_only'):visible=False
        elif sec:
            st=data[sec]
            if 'gate_index' in m:visible=st['state']==int(m['gate_index'])
            elif m.get('collapse_only'):visible=st['state']==4
            elif m.get('ore_chunk') and st['state']==4:visible=False
            elif 'min_stage' in m:visible=st['unlocked_stage']>=int(m['min_stage'])
        o.hide_render=not visible;o.hide_set(not visible)
    frac=float(row.get('gate',1))
    for name in ['CSM_Blast_leaf_L','CSM_Blast_leaf_R']:
        o=scene.objects[name];o.location.x=o['csm_closed_x']+o['csm_travel']*frac
    ctrl=scene.objects.get('CSM_CTRL_BLAST_GATE')
    if ctrl:ctrl['csm_open_fraction']=frac
    bpy.context.view_layer.update()
