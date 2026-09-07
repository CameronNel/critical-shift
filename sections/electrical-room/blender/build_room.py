"""Original Electrical Room. Blender 5.2; factory-empty, no external assets.

Build: blender --background --factory-startup --python build_room.py -- --stage slice --revision S01
Rendering is separate and MUST be invoked through the shared gpu_gate.py.
All dimensions are metres. Equipment is authored in local coordinates, front -Y.
"""
import bpy, math, json, argparse, sys, random, hashlib
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
SOURCE_BYTES = Path(__file__).read_bytes()
P = argparse.ArgumentParser()
P.add_argument('--stage', choices=['slice','full'], default='full')
P.add_argument('--revision', default='R01')
P.add_argument('--output', default='')
args = P.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
random.seed(1709)
bpy.ops.wm.read_factory_settings(use_empty=True)
SC = bpy.context.scene
SC.unit_settings.system='METRIC'
SC.unit_settings.scale_length=1
SC['section']='electrical-room'
SC['revision']=args.revision
SC['stage']=args.stage
SC['source_sha256']=hashlib.sha256(SOURCE_BYTES).hexdigest()
COL={}
for name in ['Architecture','Switchgear','Utilities','Transformer','Essential','Workshop','Lighting','Cameras','Validation']:
    c=bpy.data.collections.new(name); SC.collection.children.link(c); COL[name]=c
current='Architecture'

def srgb(h):
    vals=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in vals)

def material(name, color, rough=.6, metal=0, variation=.035, bump=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*srgb(color),1); m.use_nodes=True
    nt=m.node_tree; bs=nt.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*srgb(color),1)
    bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    if variation or bump:
        tc=nt.nodes.new('ShaderNodeTexCoord'); n=nt.nodes.new('ShaderNodeTexNoise')
        n.inputs['Scale'].default_value=2.8; n.inputs['Detail'].default_value=2.1; n.inputs['Roughness'].default_value=.55
        nt.links.new(tc.outputs['Generated'],n.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        rgb=srgb(color)
        ramp.color_ramp.elements[0].position=.15; ramp.color_ramp.elements[1].position=.85
        ramp.color_ramp.elements[0].color=(*(v*(1-variation) for v in rgb),1)
        ramp.color_ramp.elements[1].color=(*(min(1,v*(1+variation)) for v in rgb),1)
        nt.links.new(n.outputs['Fac'],ramp.inputs[0]); nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
        rem=nt.nodes.new('ShaderNodeMapRange'); rem.inputs['From Min'].default_value=0; rem.inputs['From Max'].default_value=1
        rem.inputs['To Min'].default_value=max(.1,rough-.045); rem.inputs['To Max'].default_value=min(1,rough+.05)
        nt.links.new(n.outputs['Fac'],rem.inputs['Value']); nt.links.new(rem.outputs['Result'],bs.inputs['Roughness'])
        if bump:
            fine=nt.nodes.new('ShaderNodeTexNoise'); fine.inputs['Scale'].default_value=115; fine.inputs['Detail'].default_value=1.5
            nt.links.new(tc.outputs['Generated'],fine.inputs['Vector'])
            b=nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value=.22; b.inputs['Distance'].default_value=bump
            nt.links.new(fine.outputs['Fac'],b.inputs['Height']); nt.links.new(b.outputs['Normal'],bs.inputs['Normal'])
    return m

M={
 'wall':material('Warm precast concrete','B4B0A2',.86,variation=.12,bump=.009),
 'floor':material('Dry ground concrete','747E7B',.78,variation=.09,bump=.003),
 'patch':material('Replacement concrete','A3A39A',.87,variation=.04,bump=.005),
 'joint':material('Elastomer joint filler','505752',.95,variation=0),
 'paint':material('Petrol enamel - original','31585E',.39,.10,.13,.0006),
 'pale':material('Warm grey enamel','A8AFA9',.52,.15,.04,.001),
 'bus':material('Galvanized bus casing','546764',.64,.32,.08,.0008),
 'darkpaint':material('Structural blue graphite','37474D',.58,.3,.04,.001),
 'metal':material('Brushed galvanized steel','7D898A',.32,1,.045,.0006),
 'edge':material('Exposed steel at contact wear','899293',.55,.7,.015),
 'undercoat':material('Exposed ochre primer','7F8171',.82,.08,.07),
 'dirt':material('Dried contact grime','47564F',.94,0,.05),
 'rubber':material('Insulating rubber','202A2A',.91,0,.035,.002),
 'black':material('Switch housing phenolic','202826',.48,0,.035,.001),
 'yellow':material('Ochre safety enamel','CEAC57',.57,.08,.04),
 'orange':material('Standby ochre enamel','B68B55',.55,.14,.045,.001),
 'red':material('Isolator vermilion','A54833',.5,.12,.03),
 'copper':material('Bus copper - aged','8A5B3B',.46,.75,.035),
 'ceramic':material('Porcelain standoff','B7ADA0',.33,.05,.015),
 'paper':material('Work order paper','C6C1AD',.98,0,.02),
 'ink':material('Printed charcoal','202D2D',.93,0,0),
 'cloth':material('Cotton electrician rag','96846C',.98,0,.065,.002),
 'scuff':material('Localized contact abrasion','646C69',.85,0,.02),
}
def emission(name, color, energy):
    m=material(name,color,.35,0,0); bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Emission Color'].default_value=(*srgb(color),1);bs.inputs['Emission Strength'].default_value=energy;return m
M['lamp']=emission('Warm prismatic diffuser','FFF0CB',4)
M['green']=emission('Energized pilot lens','93C59B',.8)
M['amber']=emission('Transfer pilot lens','F5B359',1)
M['glass']=material('Instrument glass','617C79',.23,.1,.01)
M['glass'].node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.25

def link(o):
    for c in list(o.users_collection):c.objects.unlink(o)
    COL[current].objects.link(o)
    return o

def finish(o,name,mat,parent=None,bevel=0):
    o.name=name; link(o)
    if mat:o.data.materials.append(M[mat] if isinstance(mat,str) else mat)
    if parent:o.parent=parent
    if o.type=='MESH':
        o['assembly_member']=parent.name if parent else 'fixed-architecture'
        if bevel:
            mod=o.modifiers.new('Manufactured edge treatment','BEVEL');mod.width=bevel;mod.segments=2
            mod=o.modifiers.new('Face weighted normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=30
    return o

def box(name,loc,dims,mat,parent=None,bevel=.004):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,name,mat,parent,bevel)

def cyl(name,loc,r,depth,mat,parent=None,axis='Z',vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc)
    o=bpy.context.object
    if axis=='Y':o.rotation_euler[0]=math.pi/2
    elif axis=='X':o.rotation_euler[1]=math.pi/2
    finish(o,name,mat,parent,min(.002,depth*.12,r*.08) if r>.012 and depth>=.012 else 0)
    for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
    return o

def ring(name,loc,r,thick,mat,parent=None,axis='Z'):
    bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=8,location=loc,major_radius=r,minor_radius=thick)
    o=bpy.context.object
    if axis=='Y':o.rotation_euler[0]=math.pi/2
    elif axis=='X':o.rotation_euler[1]=math.pi/2
    finish(o,name,mat,parent,0)
    for p in o.data.polygons:p.use_smooth=True
    return o

def tube(name,points,r,mat,parent=None):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=12;cu.bevel_depth=r;cu.bevel_resolution=3
    sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
    for p,co in zip(sp.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,cu);COL[current].objects.link(o);o.data.materials.append(M[mat]);o.parent=parent
    o['assembly_member']=parent.name if parent else 'fixed-architecture';return o

def beam(name,a,b,w,mat,parent=None):
    mid=(Vector(a)+Vector(b))/2;o=box(name,mid,(w,w,(Vector(b)-Vector(a)).length),mat,parent, min(.003,w/5));o.rotation_euler=(Vector(b)-Vector(a)).to_track_quat('Z','Y').to_euler();return o

def text(name,body,loc,size,mat='paper',parent=None,rot=(math.pi/2,0,0),align='LEFT'):
    cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.extrude=.00015;cu.align_x=align
    o=bpy.data.objects.new(name,cu);COL[current].objects.link(o);o.location=loc;o.rotation_euler=rot;o.parent=parent;cu.materials.append(M[mat]);o['assembly_member']=parent.name if parent else 'fixed-architecture';return o

SUP=[]
def assembly(name,loc=(0,0,0),rot=0,support=None,anchors=None,direction=None,parent=None):
    o=bpy.data.objects.new(name,None);COL[current].objects.link(o);o.location=loc;o.rotation_euler[2]=rot
    o['assembly_root']=True
    if parent:o.parent=parent
    if support:
        o['support_target']=support; o['support_anchors']=json.dumps(anchors or [[0,0,0]])
        o['support_direction']=json.dumps(direction or ([0,0,1] if support.startswith('Ceiling') else [0,0,-1]))
        SUP.append(o)
    return o

def fasteners(name,xs,zs,y,parent,mat='metal',r=.012):
    for x in xs:
        for z in zs:
            cyl(name,(x,y,z),r,.008,mat,parent,'Y',8)
            box('Screwdriver slot',(x,y-.0045,z),(r*1.12,.001,r*.16),'black',parent,.0003)

def plaque(parent,body,loc,w=.48,h=.15,mat='darkpaint',size=.055):
    x,y,z=loc;box('Recessed engraved plate',(x,y,z),(w,.008,h),mat,parent,.002)
    text('Engraved '+body,body,(x-w*.43,y-.006,z-size*.35),size,'paper',parent)

def handle(parent,x,y,z,mat='metal',height=.19):
    for zz in [z-height/2,z+height/2]:cyl('Handle mounting boss',(x,y+.025,zz),.021,.07,mat,parent,'Y')
    beam('Formed pull grip',(x,y-.015,z-height/2),(x,y-.015,z+height/2),.026,mat,parent)

def gauge(parent,x,y,z,r=.115,label='A',needle=.4):
    cyl('Instrument cast bezel',(x,y,z),r,.065,'darkpaint',parent,'Y',48)
    ring('Rolled bezel rim',(x,y-.036,z),r*.90,r*.043,'metal',parent,'Y')
    cyl('Ivory instrument dial',(x,y-.035,z),r*.84,.003,'paper',parent,'Y',48)
    for i in range(9):
        a=math.radians(-125+i*31.25);p=(x+math.sin(a)*r*.72,y-.04,z+math.cos(a)*r*.72)
        q=(x+math.sin(a)*r*.61,y-.04,z+math.cos(a)*r*.61);beam('Calibration tick',p,q,.006,'ink',parent)
    a=needle;beam('Meter needle',(x,y-.046,z),(x+math.sin(a)*r*.63,y-.046,z+math.cos(a)*r*.63),.006,'red',parent)
    cyl('Needle pivot',(x,y-.049,z),.012,.007,'black',parent,'Y')
    text('Meter unit',label,(x,y-.051,z-r*.49),r*.28,'ink',parent,align='CENTER')
    for xx,zz in [(x-r*.71,z),(x+r*.71,z)]:cyl('Dial fixing pin',(xx,y-.043,zz),.003,.004,'metal',parent,'Y',8)

def rotary(parent,x,y,z,color='black',label=None):
    cyl('Selector escutcheon',(x,y,z),.065,.022,'metal',parent,'Y')
    box('Mechanical selector',(x,y-.035,z),(.025,.065,.098),color,parent,.006)
    if label:plaque(parent,label,(x,y+.004,z-.11),.21,.045,size=.018)

def wear(parent,x,y,z,w=.1):
    # Authored contact chips: sparse and planar, not universal noise.
    verts=[(x-w/2,y,z),(x-w*.1,y,z+.007),(x+w*.45,y,z+.004),(x+w/2,y,z-.003),(x+w*.17,y,z-.008),(x-w*.45,y,z-.004)]
    me=bpy.data.meshes.new('Contact chip');me.from_pydata(verts,[],[list(range(6))]);me.update();o=bpy.data.objects.new('Localized chipped paint',me);COL[current].objects.link(o);o.parent=parent;me.materials.append(M['edge']);o['assembly_member']=parent.name

def contact_scars(parent,x,y,z,w=.18,h=.07,seed=1):
    # Irregular, purpose-placed abrasion islands; no uniform edge-wear generator.
    rng=random.Random(seed)
    for k in range(12):
        xx=x+rng.uniform(-w/2,w/2);zz=z+rng.uniform(-h/2,h/2)
        rx=rng.uniform(.007,.036);rz=rng.uniform(.002,.009)
        vv=[(xx+math.cos(i*math.tau/7)*rx*rng.uniform(.7,1.15),y,zz+math.sin(i*math.tau/7)*rz*rng.uniform(.5,1.2)) for i in range(7)]
        me=bpy.data.meshes.new('Authored handling abrasion');me.from_pydata(vv,[],[list(range(7))]);me.update();ob=bpy.data.objects.new('Wear at repeatedly handled edge',me);COL[current].objects.link(ob);ob.parent=parent;me.materials.append(M['undercoat' if k%3 else 'edge']);ob['assembly_member']=parent.name

def folded_panel(parent,loc,w,h,mat='paint'):
    # Press-formed instrument panel with an inward sloping return and clipped corners.
    x,y,z=loc
    def outline(ww,hh,cc,yy):
        return [(x+xx,yy,z+zz) for xx,zz in [(-ww/2+cc,-hh/2),(ww/2-cc,-hh/2),(ww/2,-hh/2+cc),(ww/2,hh/2-cc),(ww/2-cc,hh/2),(-ww/2+cc,hh/2),(-ww/2,hh/2-cc),(-ww/2,-hh/2+cc)]]
    vv=outline(w,h,.045,y)+outline(w-.10,h-.10,.028,y+.037)
    ff=[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]+[tuple(range(8,16))]
    me=bpy.data.meshes.new('Press formed recess');me.from_pydata(vv,[],ff);me.update();o=bpy.data.objects.new('Folded instrument recess',me);COL[current].objects.link(o);o.parent=parent;me.materials.append(M[mat]);o['assembly_member']=parent.name
    so=o.modifiers.new('Sheet steel gauge','SOLIDIFY');so.thickness=.002

def switchgear(name,y,kind='feeder',label='DISTRIBUTION',width=1.17):
    global current
    current='Switchgear'
    root=assembly(name,(-4.32,y,0),math.pi/2,'Floor',[[u,v,0] for u in [-width/2+.1,width/2-.1] for v in [-.55,.55]])
    w=width;d=1.3
    box('Anchored channel plinth',(0,0,.065),(w,1.3,.13),'darkpaint',root,.008)
    for x in [-w/2+.07,w/2-.07]:
        for yy in [-.52,.52]:cyl('Foundation anchor',(x,yy,.143),.026,.023,'metal',root,vertices=8)
    # Cabinet is a folded enclosure with separate structural corners and door skins.
    box('Rear shell',(0,.61,1.43),(w-.05,.075,2.55),'paint',root,.006)
    for x in [-w/2+.025,w/2-.025]:
        box('Folded return side',(x,0,1.44),(.05,1.25,2.58),'paint',root,.007)
        box('Stiffened front upright',(x,-.596,1.44),(.065,.09,2.58),'darkpaint',root,.005)
    box('Crown rain lip',(0,0,2.745),(w+.025,1.34,.085),'paint',root,.008)
    if kind!='repair':box('Door recess shadow',(0,-.58,1.46),(w-.11,.04,2.42),'rubber',root,.002)
    box('Meter compartment skin',(0,-.633,2.20),(w-.14,.055,.87),'paint' if kind!='incoming' else 'pale',root,.005)
    fasteners('Captive panel screw',[-w/2+.13,w/2-.13],[1.81,2.59],-.669,root,r=.011)
    plaque(root,label,(0,-.672,2.48),w-.27,.12,size=.048)
    folded_panel(root,(0,-.705,2.16),w-.26,.44,'pale' if kind=='incoming' else 'paint')
    gauge(root,-.21,-.685,2.18,.091,'kV' if kind=='incoming' else 'A',-.4 if kind=='incoming' else .5)
    if kind=='incoming':
        gauge(root,.20,-.68,2.18,.091,'MW',.8)
    else:
        box('Protection relay bezel',(.18,-.680,2.17),(.29,.045,.21),'black',root,.004)
        box('Recessed relay glass',(.18,-.705,2.20),(.238,.008,.105),'glass',root,.001)
        text('Relay reading','50.0 Hz',(.075,-.710,2.183),.039,'paper',root)
        for xx in [.1,.18,.26]:box('Relay membrane key',(xx,-.709,2.102),(.035,.007,.018),'pale',root,.001)
    for x,col in [(-.23,'green'),(.02,'amber'),(.27,'black')]:
        cyl('Pilot retaining ring',(x,-.681,1.94),.032,.02,'metal',root,'Y');cyl('Pilot glass lens',(x,-.695,1.94),.024,.017,col,root,'Y')
    if kind=='repair':
        # Withdrawn breaker exposes tangible contacts and insulators within a rigid cage.
        box('Service cavity backplane',(0,.42,1.12),(w-.16,.045,1.08),'metal',root,.003)
        for x in [-.31,0,.31]:
            cyl('Breaker porcelain pole',(x,-.28,1.05),.082,.90,'ceramic',root)
            for z in [.69,.75,.81,1.16,1.22,1.28]:cyl('Insulator rib',(x,-.28,z),.099,.029,'ceramic',root)
            box('Copper stab contact',(x,-.20,1.56),(.075,.40,.055),'copper',root,.007)
            box('Copper bus terminal',(x,.27,1.33),(.09,.045,.48),'copper',root,.004)
            beam('Insulated mechanical operating link',(x,-.25,.62),(x,-.89,.62),.04,'darkpaint',root)
            cyl('Pole lower collar',(x,-.28,.62),.089,.07,'metal',root)
        for x in [-.43,.43]:
            box('Carriage structural cheek',(x,-.27,.97),(.035,1.0,.90),'darkpaint',root,.004)
            for z in [.64,1.33]:box('Drawout cheek folded edge',(x,-.27,z),(.07,1.02,.035),'metal',root,.003)
        # Spring-pack and trip linkage make the device's mechanical role visible.
        for x in [-.23,.23]:
            cyl('Stored-energy spring guide',(x,-.71,.76),.018,.35,'metal',root)
            pts=[(x+.042*math.cos(i*.48),-.71+.042*math.sin(i*.48),.60+i*.0021) for i in range(140)]
            tube('Stored-energy operating spring',pts,.006,'metal',root)
        beam('Trip cross shaft',(-.39,-.78,1.07),(.39,-.78,1.07),.036,'metal',root)
        for x in [-.31,0,.31]:
            beam('Insulating trip link',(x,-.78,1.07),(x,-.44,.76),.025,'black',root)
        box('Service lamp bracket',(-.42,-.51,1.54),(.06,.10,.14),'metal',root,.003)
        tube('Service lamp gooseneck',[(-.42,-.54,1.57),(-.42,-.62,1.70),(-.23,-.72,1.68)],.014,'black',root)
        cyl('Repair lamp hood',(-.20,-.73,1.66),.064,.14,'darkpaint',root,'Y')
        cyl('Repair lamp diffuser',(-.20,-.806,1.66),.053,.006,'lamp',root,'Y')
        ld=bpy.data.lights.new('Local breaker service light','AREA');ld.energy=16;ld.color=(1,.73,.43);ld.shape='DISK';ld.size=.18
        lo=bpy.data.objects.new('Local breaker service light',ld);COL[current].objects.link(lo);lo.parent=root;lo.location=(-.2,-.60,1.62);lo.rotation_euler=(Vector((0,-.30,.85))-Vector(lo.location)).to_track_quat('-Z','Y').to_euler()
        box('Withdrawn breaker carriage',(0,-.75,.49),(w-.20,1.17,.12),'darkpaint',root,.012)
        for x in [-.42,.42]:box('Drawout rail',(x,-.70,.38),(.08,1.24,.12),'metal',root,.004)
        box('Breaker operating fascia',(0,-1.18,.79),(w-.23,.10,.46),'pale',root,.006)
        cyl('Racking spindle',(0,-1.31,.62),.038,.07,'metal',root,'Y')
        handle(root,.23,-1.33,.83,height=.16)
        rotary(root,-.25,-1.255,.83,'red')
        plaque(root,'WITHDRAWN',(0,-1.236,.974),.43,.05,size=.023)
        for z in [.57,.91]:fasteners('Drawout fascia bolts',[-.40,.40],[z],-1.239,root,r=.012)
        root['interaction']='breaker_rack;isolated_repair'
    else:
        box('Breaker access door',(0,-.64,1.12),(w-.14,.05,1.23),'paint',root,.006)
        for z in [.67,1.55]:
            box('Steel lift-off hinge',(-w/2+.067,-.674,z),(.071,.066,.115),'metal',root,.005)
            cyl('Hinge pin',(-w/2+.067,-.677,z),.014,.135,'darkpaint',root)
        box('Breaker inset escutcheon',(0,-.674,1.29),(.45,.025,.47),'darkpaint',root,.007)
        fasteners('Isolator mechanism retaining screws',[-.18,.18],[1.10,1.48],-.691,root,r=.007)
        cyl('Disconnect hub',(0,-.71,1.28),.103,.07,'black',root,'Y')
        # Gripped disconnect with a cast neck, visible pivot, and rounded grasping barrel.
        beam('Cast isolator arm',(0,-.754,1.28),(0,-.793,1.39),.037,'metal',root)
        cyl('Operating grip',(0,-.798,1.4),.031,.16,'red' if kind=='incoming' else 'black',root)
        cyl('Mechanism axle',(0,-.757,1.28),.023,.055,'metal',root,'Y')
        plaque(root,'I   /   O',(0,-.698,1.02),.25,.06,size=.026)
        handle(root,w/2-.21,-.724,.85,height=.17)
        fasteners('Access door latch',[-w/2+.13,w/2-.13],[.56,1.68],-.675,root)
        wear(root,w/2-.22,-.667,.75,.17);wear(root,-w/2+.13,-.667,1.65,.055)
        wear(root,-.30,-.667,.516,.12);wear(root,.30,-.667,1.71,.07)
        contact_scars(root,w/2-.20,-.6656,.83,.14,.25,8)
        contact_scars(root,-.32,-.6656,.55,.3,.04,3)
        root['interaction']='turbine_disconnect' if kind=='incoming' else 'load_shed_'+label.lower()
    box('Removable lower ventilation plate',(0,-.64,.32),(w-.14,.05,.26),'paint',root,.004)
    for zz in [.26,.30,.34,.38]:box('Folded cooling louvre',(0,-.679,zz),(w-.34,.045,.018),'darkpaint',root,.002)
    # Top terminal boot creates an enclosed power continuation to overhead duct.
    box('Cable termination boot',(0,.02,2.91),(.67,.65,.29),'darkpaint',root,.009)
    for z,ww in [(2.78,.78),(3.04,.70)]:box('Bolted termination flange',(0,.02,z),(ww,.76,.055),'metal',root,.004)
    fasteners('Crown fastener',[-w/2+.1,w/2-.1],[2.748],-.681,root)
    contact_scars(root,.30,-.671,2.73,.26,.03,19)
    if kind=='repair':contact_scars(root,.3,-1.231,.59,.24,.03,32)
    return root

def door(name,x,y,rot=0,label='TURBINE'):
    global current
    current='Architecture';r=assembly(name,(x,y,0),rot,'Floor',[[-1.27,0,0],[1.27,0,0]])
    for xx in [-1.27,1.27]:
        box('Deep steel portal jamb',(xx,0,1.39),(.14,.35,2.78),'darkpaint',r,.006)
        box('Rubber jamb seal',(xx*.956,-.035,1.34),(.015,.06,2.68),'rubber',r,.002)
        fasteners('Portal anchor',[xx],[.2,1.34,2.5],-.185,r,r=.018)
    box('Portal header',(0,0,2.80),(2.68,.35,.20),'darkpaint',r,.008)
    box('Sliding door rail hood',(0,-.32,2.93),(5.05,.24,.16),'darkpaint',r,.008)
    # Two open sliding leaves parked on either side, flush to outer wall.
    for side in [-1,1]:
        xx=side*1.86
        box('Parked sliding leaf',(xx,-.30,1.34),(1.26,.07,2.65),'pale',r,.006)
        box('Door impact shoe',(xx,-.352,.32),(1.16,.032,.38),'metal',r,.003)
        box('Door vertical edge fold',(xx-side*.60,-.351,1.35),(.047,.035,2.60),'darkpaint',r,.004)
        box('Door recessed vision trim',(xx,-.343,1.95),(.53,.035,.32),'darkpaint',r,.005)
        box('Door wired vision glass',(xx,-.364,1.95),(.46,.01,.25),'glass',r,.003)
        for wx in [-.12,0,.12]:box('Vision glass wire',(xx+wx,-.371,1.95),(.002,.002,.23),'metal',r,0)
        handle(r,xx-side*.38,-.405,1.1,height=.25)
        for xx2 in [xx-.42,xx+.42]:
            cyl('Sliding roller axle',(xx2,-.31,2.74),.025,.11,'metal',r,'Y')
            cyl('Sliding roller',(xx2,-.31,2.82),.056,.043,'black',r,'Y')
        wear(r,xx-side*.34,-.337,1.14,.11);wear(r,xx+.25,-.37,.24,.22)
        contact_scars(r,xx-side*.37,-.336,1.07,.11,.37,11 if side<0 else 21)
        contact_scars(r,xx,-.369,.20,.83,.06,32 if side<0 else 17)
    box('Flush portal threshold',(0,0,-.006),(2.4,.45,.012),'metal',r,.001)
    plaque(r,label,(0,-.193,2.82),1.10,.14,size=.077)
    return r

def light_fixture(name,loc,power=750,warm=False,rot=0):
    global current
    current='Lighting';r=assembly(name,loc,rot,'Ceiling',[[x,0,.20] for x in [-.66,.66]])
    for x in [-.66,.66]:box('Luminaire hanger',(x,0,.10),(.04,.04,.20),'metal',r,.002)
    box('Folded fluorescent tray',(0,0,0),(1.65,.33,.13),'darkpaint',r,.006)
    box('Recessed prismatic diffuser',(0,0,-.075),(1.48,.23,.025),'lamp',r,.003)
    for xx in [-.74,.74]:box('Diffuser retaining clip',(xx,0,-.082),(.025,.27,.033),'metal',r,.002)
    ld=bpy.data.lights.new(name+' photometric area','AREA');ld.energy=power;ld.shape='RECTANGLE';ld.size=1.5;ld.size_y=.28;ld.color=(1,.83,.62) if warm else (.84,.93,1)
    ob=bpy.data.objects.new(name+' light',ld);COL[current].objects.link(ob);ob.parent=r;ob.location=(0,0,-.13)
    return r

def architecture(slice=False):
    global current
    current='Architecture'
    end=7.2 if slice else 16.4
    box('Floor',(0,end/2,-.12),(11,end,.24),'floor',bevel=.0)
    # Slab joints are inlays, not floating carpet or repetitive tiles.
    for y in [i*2.73 for i in range(1,7) if i*2.73<end]:box('Transverse slab joint',(0,y,.0003),(11,.008,.0006),'joint',bevel=0)
    for x in [-2.75,2.75]:box('Longitudinal slab joint',(x,end/2,.0003),(.008,end,.0006),'joint',bevel=0)
    for side in [-1,1]:
        x=side*5.625
        if not slice and side==1:
            for cy,ln in [(5.5,11),(15.9,1)]:box('East structural wall',(x,cy,2.4),(.25,ln,4.8),'wall',bevel=.012)
            box('Reserve bay opening head',(x,13.2,4.0),(.25,4.4,1.6),'wall',bevel=.007)
            box('Reserve opening south return',(x,11.5,1.6),(.25,1,3.2),'wall')
            box('Reserve opening north return',(x,14.9,1.6),(.25,1,3.2),'wall')
        else:box('West wall' if side==-1 else 'East wall',(x,end/2,2.4),(.25,end,4.8),'wall',bevel=.014)
        for yy in [1.0,6.7,11.5,16.15]:
            if yy>end:continue
            box('Wall pilaster',(side*5.42,yy,2.4),(.16,.25,4.8),'wall',bevel=.006)
        box('Damp-proof concrete curb',(side*5.43,end/2,.10),(.14,end,.2),'patch',bevel=.006)
        for zz in [1.25,3.1]:box('Precast horizontal reveal',(side*5.497,end/2,zz),(.005,end,.014),'joint',bevel=0)
        for yy in [2.5,5,7.5,10,12.5,15]:
            if yy<end:box('Precast vertical reveal',(side*5.497,yy,2.4),(.005,.012,4.8),'joint',bevel=0)
    for y,is_back in [(0,False)]+([] if slice else [(end,True)]):
        for x in [-3.35,3.35]:box('Portal wall return',(x,y+(.125 if is_back else -.125),2.4),(4.3,.25,4.8),'wall',bevel=.006)
        box('Portal wall head',(0,y+(.125 if is_back else -.125),3.8),(2.4,.25,2),'wall',bevel=.006)
        door('D02_Waste' if is_back else 'D01_Turbine',0,y,math.pi if not is_back else 0,'WASTE / SERVICE' if is_back else 'TURBINE')
        # Short matching connection stub is part of this module; no borrowed room geometry.
        outside=1 if is_back else -1
        box('Connection vestibule floor',(0,y+outside*1.4,-.12),(3,2.8,.24),'floor',bevel=0)
        # Door pocket depth reserved at the threshold before the narrower vestibule returns.
        for x in [-1.62,1.62]:box('Connection vestibule side',(x,y+outside*1.73,1.65),(.24,2.14,3.3),'wall')
        box('Connection vestibule ceiling',(0,y+outside*1.53,3.4),(3.5,2.54,.2),'darkpaint')
        box('Connection privacy return',(0,y+outside*2.85,1.65),(3.5,.2,3.3),'wall')
    box('Ceiling',(0,end/2,4.9),(11,end,.2),'wall',bevel=0)
    for yy in [1.0,6.7,11.5,16.15]:
        if yy>end:continue
        # Rolled I-section, flange-web construction with bolted haunches.
        for zz in [4.42,4.72]:box('I beam flange',(0,yy,zz),(11,.23,.035),'darkpaint',bevel=.003)
        box('I beam web',(0,yy,4.57),(11,.024,.27),'darkpaint',bevel=.002)
        for x in [-5.24,5.24]:box('Beam end plate',(x,yy,4.57),(.025,.42,.52),'metal',bevel=.003)
    # Continuity of route is communicated by restrained edge guides.
    for x in [-1.26,1.26]:
        for y,ln in [(1.5,1.0),(end-1.5,1.0)]:box('Route edge guide',(x,y,.001),( .045,ln,.002),'yellow',bevel=0)

def busway(yend=10.8):
    global current
    current='Utilities'
    r=assembly('Enclosed main busway',(-4.32,0,3.88),0,'Ceiling',[[x,y, .92] for y in [1.2,5.8,10.5,15.6] if y<yend for x in [-.49,.49]])
    box('Main bus duct casing',(0,yend/2,0),(.72,yend,.48),'bus',r,.009)
    for x in [-.28,.28]:box('Longitudinal folded bus seam',(x,yend/2,-.25),(.035,yend,.04),'metal',r,.002)
    for yy in [i*1.7 for i in range(1,11) if i*1.7<yend]:
        box('Bolted bus splice cover',(0,yy,0),(.79,.17,.55),'metal',r,.007)
        for x in [-.31,.31]:cyl('Splice clamp bolt',(x,yy,-.282),.016,.022,'darkpaint',r,vertices=8)
    for yy in [2.15,5.75]:
        # Stencilled direction chevrons and small cable-class identifier on the duct side.
        for k in [0,1]:
            vv=[(.362,yy-.13+k*.12,-.055),(.362,yy+k*.12,.06),(.362,yy+.045+k*.12,.06),(.362,yy-.085+k*.12,-.055)]
            me=bpy.data.meshes.new('Bus stencil arrow');me.from_pydata(vv,[],[(0,1,2,3)]);me.update();o=bpy.data.objects.new('Power flow direction stencil',me);COL[current].objects.link(o);o.parent=r;me.materials.append(M['yellow']);o['assembly_member']=r.name
    for yy in [1.2,5.8,10.5,15.6]:
        if yy>yend:continue
        for x in [-.49,.49]:cyl('Threaded bus hanger',(x,yy,.38),.017,1.08,'metal',r)
        box('Hanger strut',(0,yy,-.30),(1.06,.09,.055),'darkpaint',r,.004)
        for x in [-.49,.49]:box('Ceiling anchor plate',(x,yy,.905),(.16,.18,.03),'metal',r,.003)
    for yy in [3.9,5.1] + ([] if args.stage=='slice' else [6.3,7.5,8.7,9.9]):
        # Folded tapered duct transition, with the broad connection sized to the bus.
        verts=[]
        for z,w,d in [(-.89,.57,.52),(-.54,.57,.52),(-.30,.69,.69)]:
            verts.extend([(-w/2,yy-d/2,z),(w/2,yy-d/2,z),(w/2,yy+d/2,z),(-w/2,yy+d/2,z)])
        faces=[(0,3,2,1),(8,9,10,11)]+[(j*4+i,j*4+(i+1)%4,(j+1)*4+(i+1)%4,(j+1)*4+i) for j in range(2) for i in range(4)]
        me=bpy.data.meshes.new('Tapered folded sheet duct');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new('Tapered tap-off transition',me);COL[current].objects.link(ob);ob.parent=r;me.materials.append(M['paint']);ob['assembly_member']=r.name
        box('Tap flange',(0,yy,-.3),(.66,.65,.08),'metal',r,.004)
    return r

def work_cart(y=1.8):
    global current
    current='Workshop';r=assembly('Electrician service cart',(-4.45,y,0),math.pi/2,'Floor',[[-.32,-.26,0],[.32,-.26,0],[-.32,.26,0],[.32,.26,0]])
    for x in [-.32,.32]:
        for yy in [-.26,.26]:
            cyl('Rubber castor tyre',(x,yy,.095),.095,.062,'rubber',r,'X')
            cyl('Castor steel hub',(x,yy,.095),.047,.065,'metal',r,'X')
            box('Castor swivel bracket',(x,yy,.21),(.065,.12,.09),'metal',r,.005)
            beam('Cart upright',(x,yy,.23),(x,yy,.86),.035,'darkpaint',r)
    for z in [.28,.86]:
        box('Cart upper tray' if z>.5 else 'Cart lower tray',(0,0,z),(.77,.65,.04),'paint',r,.004)
        for yy in [-.3,.3]:box('Tray folded rim',(0,yy,z+.035),(.77,.03,.10),'paint',r,.004)
    contact_scars(r,-.19,-.316,.91,.31,.023,56)
    contact_scars(r,.26,-.316,.33,.13,.035,82)
    tube('Push handle',[(-.36,.24,.85),(-.36,.35,1.0),(.36,.35,1.0),(.36,.24,.85)],.018,'metal',r)
    # Multimeter case, leads, spare fuse and laid-down work order.
    meter=assembly('Multimeter on tray',support='Cart upper tray',anchors=[[0,-.06,.88]],parent=r)
    box('Multimeter rubber bumper',(0,-.06,.91),(.17,.26,.06),'rubber',meter,.017)
    box('Handheld multimeter',(0,-.06,.932),(.138,.228,.024),'yellow',meter,.010)
    box('Multimeter screen',(0,-.115,.947),(.100,.074,.008),'black',meter,.003)
    text('Meter LCD','0.00',(0,-.135,.952),.032,'paper',meter,rot=(0,0,0),align='CENTER')
    cyl('Range selector',(0,-.014,.951),.028,.013,'black',meter)
    for side in [-1,1]:
        for yy in [-.10,-.05,0,.05]:box('Meter moulded grip rib',(side*.081,yy,.916),(.012,.014,.026),'black',meter,.003)
    tube('Red test lead',[(.04,.051,.94),(.25,.08,.889),(.24,-.18,.884),(.08,-.24,.884)],.004,'red',meter)
    tube('Black test lead',[(-.02,.051,.94),(-.16,.14,.889),(-.27,.07,.884),(-.2,-.15,.884)],.004,'rubber',meter)
    for x in [-.24,-.14]:
        fuse=assembly('Spare fuse on tray '+str(x),support='Cart upper tray',anchors=[[x,-.037,.881],[x,.137,.881]],parent=r)
        cyl('Spare ceramic fuse',(x,.05,.905),.022,.16,'ceramic',fuse,'Y')
        for yy in [-.037,.137]:cyl('Fuse end cap',(x,yy,.905),.024,.025,'metal',fuse,'Y')
    paper=assembly('Work order on tray',support='Cart upper tray',anchors=[[.22,.05,.88]],parent=r)
    box('Work order paper',(.22,.05,.8805),(.18,.23,.001),'paper',paper,0)
    text('Work order imprint','D-04\nISOLATED\n________\n07:20  OK',(.15,.1,.8813),.018,'ink',paper,rot=(0,0,0))
    for x in [-.24,-.14]:
        text('Fuse ceramic marking','63 A',(x-.014,-.01,.929),.015,'ink',r,rot=(0,0,0))
    # Folded cotton rag uses an undulating stitched surface with thickness.
    verts=[];faces=[]
    for j in range(9):
        for i in range(13):
            x=-.28+i*.037;y=-.18+j*.038;z=.303+.054*(1+math.sin(i*.8))*(1+math.sin(j*.7))/4
            verts.append((x,y,z))
    for j in range(8):
        for i in range(12):a=j*13+i;faces.append((a,a+1,a+14,a+13))
    low=min(verts,key=lambda v:v[2]);rag=assembly('Rag on lower tray',support='Cart lower tray',anchors=[[low[0],low[1],low[2]-.003]],parent=r)
    me=bpy.data.meshes.new('Folded rag mesh');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new('Cotton rag on lower tray',me);COL[current].objects.link(ob);ob.parent=rag;me.materials.append(M['cloth']);ob['assembly_member']=rag.name
    for f in me.polygons:f.use_smooth=True
    so=ob.modifiers.new('Cloth thickness','SOLIDIFY');so.thickness=.003
    return r

def mat_strip(y,ln):
    global current
    current='Switchgear';r=assembly('Insulating operating mat '+str(y),(-2.97,y,0),0,'Floor',[[0,0,0]])
    box('Rubber mat backing',(0,0,.0045),(1.02,ln,.009),'rubber',r,.004)
    for i in range(int(ln/.065)):
        box('Molded anti-slip rib',(0,-ln/2+.04+i*.065,.011),(.95,.013,.006),'rubber',r,.002)

def slice_work_evidence():
    global current
    current='Workshop'
    r=assembly('Isolation work permit board',(-5.465,2.05,0),math.pi/2,'West wall',[[0,.035,1.48]],direction=[0,1,0])
    box('Wall permit board',(0,0,1.48),(.49,.07,.65),'darkpaint',r,.008)
    box('Clipped work permit',(0,-.041,1.49),(.33,.006,.43),'paper',r,.001)
    box('Permit spring clip',(0,-.052,1.68),(.105,.027,.041),'metal',r,.004)
    text('Permit heading','ISOLATED',(0,-.046,1.59),.041,'ink',r,align='CENTER')
    text('Permit content','D-04  /  07:20\n\nContacts inspected\nReturn fuse to stores',(-.14,-.046,1.53),.020,'ink',r)
    for xx in [-.18,.18]:
        cyl('Lockout hook',(xx,-.081,1.28),.009,.1,'metal',r,'Y')
        tube('Padlock steel shackle',[(xx-.028,-.121,1.17),(xx-.028,-.121,1.25),(xx+.028,-.121,1.25),(xx+.028,-.121,1.17)],.007,'metal',r)
        box('Lockout padlock body',(xx,-.121,1.14),(.078,.036,.095),'red' if xx<0 else 'yellow',r,.013)
        cyl('Padlock keyway',(xx,-.144,1.13),.009,.005,'black',r,'Y')
    # Authored low-frequency concrete patch: a repaired cable penetration, not general grunge.
    current='Architecture'
    r=assembly('Historic conduit patch',(-5.499,2.22,.63),0,'West wall',[[0,0,0]],direction=[-1,0,0])
    vv=[(0,-.24,-.28),(0,.19,-.3),(0,.25,-.16),(0,.22,.20),(0,-.16,.26),(0,-.26,.08)]
    me=bpy.data.meshes.new('Irregular plaster repair');me.from_pydata(vv,[],[(0,1,2,3,4,5)]);me.update();o=bpy.data.objects.new('Subtle repaired wall patch',me);COL[current].objects.link(o);o.parent=r;me.materials.append(M['patch']);o['assembly_member']=r.name

def floor_wear():
    global current
    current='Architecture'
    r=assembly('Localized floor use marks',support='Floor',anchors=[[-3.5,2.2,.001]])
    for k,(x,y,w,ln) in enumerate([(-3.5,2.2,.022,.19),(-3.6,2.21,.015,.12),(-3.47,2.28,.018,.13),(-2.6,3.0,.023,.21),(-2.45,3.14,.012,.18),(-3.42,5.6,.011,.27)]):
        vv=[(x-w/2,y-ln/2,.001),(x+w/2,y-ln*.42,.001),(x+w*.3,y+ln/2,.001),(x-w*.4,y+ln*.39,.001)]
        me=bpy.data.meshes.new('Shoe scuff');me.from_pydata(vv,[],[(0,1,2,3)]);me.update();o=bpy.data.objects.new('Sparse floor handling scuff',me);COL[current].objects.link(o);o.parent=r;me.materials.append(M['scuff']);o['assembly_member']=r.name

def camera(name,loc,target,lens=27):
    global current
    current='Cameras';d=bpy.data.cameras.new(name);d.lens=lens;d.sensor_width=36;d.clip_start=.06;d.clip_end=150
    o=bpy.data.objects.new(name,d);COL[current].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler();return o

def setup():
    SC.render.engine='CYCLES';SC.cycles.samples=48;SC.cycles.use_denoising=True;SC.cycles.seed=17
    SC.cycles.max_bounces=7;SC.cycles.diffuse_bounces=4;SC.cycles.glossy_bounces=4
    SC.render.resolution_x=1440;SC.render.resolution_y=900;SC.render.resolution_percentage=100
    SC.render.image_settings.file_format='PNG';SC.render.image_settings.color_mode='RGB';SC.render.image_settings.color_depth='8'
    SC.world=bpy.data.worlds.new('Soft service ambient');SC.world.use_nodes=True
    SC.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.27,.32,1);SC.world.node_tree.nodes['Background'].inputs[1].default_value=.18
    SC.view_settings.view_transform='AgX';SC.view_settings.look='AgX - Medium High Contrast';SC.view_settings.exposure=0
    SC.render.film_transparent=False

architecture(args.stage=='slice')
switchgear('SG01_Incoming_turbine',3.9,'incoming','01  TURBINE')
switchgear('SG02_Main_bus',5.1,'repair' if args.stage=='slice' else 'feeder','02  MAIN BUS')
busway(6.7 if args.stage=='slice' else 16.4)
work_cart();mat_strip(4.5,2.9);slice_work_evidence();floor_wear()
light_fixture('West task fluorescent',( -2.5,4.55,4.6),550)
light_fixture('Entry fluorescent',(1.1,1.8,4.6),325,True)
if args.stage=='slice':
    camera('S01_Validation',(.6,6.7,1.65),(-3.4,2.8,1.65),25)
    camera('S02_Construction',(-1.6,6.45,1.7),(-4.25,4.15,1.42),31)
    camera('S03_Slice_Coverage',(3.8,6.9,1.65),(-2.5,1.8,1.85),25)
    camera('S04_Work_Evidence',(-2.4,3.0,1.65),(-4.45,1.85,1.03),40)
else:
    # Full expansion is added after independent slice approval.
    pass
setup()
SC.camera=bpy.data.objects.get('S01_Validation') or next(o for o in bpy.data.objects if o.type=='CAMERA')
bpy.context.view_layer.update()
manifest={'section':'electrical-room','revision':args.revision,'stage':args.stage,'blender_version':bpy.app.version_string,'source_sha256':SC['source_sha256'],'objects':len(bpy.data.objects),'mesh_objects':len([o for o in bpy.data.objects if o.type=='MESH']),'materials':len(bpy.data.materials),'support_roots':[o.name for o in SUP],'cameras':[{'name':o.name,'location':list(o.location),'rotation_euler':list(o.rotation_euler),'lens_mm':o.data.lens} for o in bpy.data.objects if o.type=='CAMERA']}
out=Path(args.output) if args.output else ROOT/'blender'/('electrical_slice.blend' if args.stage=='slice' else 'electrical_room.blend')
out.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
md=ROOT/'production'/'checkpoints'/args.revision;md.mkdir(parents=True,exist_ok=True)
(md/'build_manifest.json').write_text(json.dumps(manifest,indent=2))
(md/'build_room.py').write_bytes(SOURCE_BYTES)
print('BUILD_SAVED',out,'OBJECTS',len(bpy.data.objects),flush=True)
