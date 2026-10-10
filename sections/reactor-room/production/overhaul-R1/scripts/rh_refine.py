"""Owner's 140-item correction pass, applied after the seven existing hall stages.

blender --background --disable-autoexec -noaudio --python rh_refine.py -- IN OUT
All geometry changes are reproducible in this additive candidate. Bindings,
ports, bank symmetry/motion and the control-room/lift interior stay intact.
"""
import bpy, bmesh, math, sys, os, json
from pathlib import Path
from mathutils import Vector, Matrix

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import crk, rh_mats, rh_stlib as S
import rh_support_registry as SUPPORT
from mathutils.bvhtree import BVHTree
from r2lib import WALLS

A=sys.argv[sys.argv.index('--')+1:]
SRC,DST=A[:2]
bpy.ops.wm.open_mainfile(filepath=SRC)
SC=bpy.context.scene
SC.frame_set(1)
crk.STATE=bpy.data.objects['REACTOR_STATE']
COL=bpy.data.collections.get('RH REFINEMENT') or bpy.data.collections.new('RH REFINEMENT')
if COL.name not in SC.collection.children: SC.collection.children.link(COL)
for o in list(bpy.data.objects):
    if o.name.startswith('RH refine '): bpy.data.objects.remove(o,do_unlink=True)
M=dict(rh_mats.lib())
M['SIGN']=rh_mats.emit('RH refine ivory lettering',(.72,.71,.67),.25)
M['INK']=rh_mats.surf('RH refine label ink',(.008,.008,.008),.88,mottle=.05,bump=0)
M['PANEL']=rh_mats.surf('RH refine equipment panel',(.105,.105,.108),.58,.35,mottle=.18,grime=.06,scale=1.5,bump=0)
M['PRACTICAL']=rh_mats.emit('RH refine neutral task diffuser',(.93,.94,.91),2.5)
M['WET_PRACTICAL']=rh_mats.emit('RH refine frosted circulation diffuser',(.85,.86,.83),.35)
K=crk.Kit()
SIGN_RECORDS=[]

def state_glow(name,factor):
    source=bpy.data.materials['R2 state glow']
    m=bpy.data.materials.get(name)
    if not m: m=source.copy(); m.name=name
    original={f.data_path:f for f in source.node_tree.animation_data.drivers}
    for f in m.node_tree.animation_data.drivers:
        if 'Emission Strength' in f.data_path:
            f.driver.expression='('+factor+')*('+original[f.data_path].driver.expression+')'
    return m

for i in range(10):
    M['LEVEL'+str(i)]=state_glow('RH refine stability level '+str(i),
        f'.55*(1 if s >= {(i+1)/10:.3f} else .025)')
for key,condition in (('NORMAL','s >= .7'),('WARNING','.3 <= s < .7'),('CRITICAL','s < .3')):
    M[key]=state_glow('RH refine status '+key,'.65*(1 if '+condition+' else .03)')

def kill(o):
    bpy.data.objects.remove(o,do_unlink=True)

def text(name,body,p,n,size=.1,mat='SIGN',align='CENTER'):
    c=bpy.data.curves.new('RH refine '+name,'FONT')
    c.body=body; c.size=size; c.align_x=align; c.align_y='CENTER'
    c.extrude=.0004; c.resolution_u=8
    o=bpy.data.objects.new('RH refine '+name,c); COL.objects.link(o)
    o.location=p; o.rotation_euler=Vector(n).to_track_quat('Z','Y').to_euler()
    # Track local Y upwards so lettering is upright on every wall orientation.
    if abs(Vector(n).z)<.01:
        o.rotation_euler=(math.pi/2,0,math.atan2(n[1],n[0])+math.pi/2)
    c.materials.append(M[mat]); return o

def wallbox(group,mat,w,u0,u1,z0,z1,v0,v1,ch=.003):
    p=w.pt((u0+u1)/2,(v0+v1)/2)
    K.box((group,mat),p.x,p.y,z0,z1,u1-u0,v1-v0,w.angle,ch)

def walltext(name,body,w,u,z,v,size=.1,mat='SIGN'):
    p=w.pt(u,v)
    return text(name,body,(p.x,p.y,z),(w.n.x,w.n.y,0),size,mat)

_sign_receivers=None
def sign_wall_mount(group,w,us,zs,back):
    global _sign_receivers
    if _sign_receivers is None:
        _sign_receivers=[(o.name,BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons]))
            for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('RH walls mass ','RH walls concrete ','RH walls cladding ','RH walls steel ')) and not any(t in o.name.upper() for t in ('GLASS','LENS'))]
    n=Vector((w.n.x,w.n.y,0))
    for u in us:
        for z in zs:
            q=w.pt(u,back);p=Vector((q.x,q.y,z));hits=[]
            for name,tree in _sign_receivers:
                loc,normal,index,dist=tree.ray_cast(p+n*.10,-n,.85)
                if loc is not None:hits.append((dist,name,loc))
            if not hits:raise RuntimeError('No wall receiver for sign '+group)
            _,target,loc=min(hits,key=lambda h:h[0]);gap=(p-loc).dot(n)
            if gap<-.002:raise RuntimeError('Sign mount penetrates receiver '+group+' '+str(gap))
            if gap>.002:
                K.prism(('sign mounting spacers','STEEL'),loc,p,.012,.012,16,0,True,0)
                SUPPORT.register('refinement signs',group+' wall spacer','RH refine sign mounting spacers STEEL',target,[loc],-n,'wall')
                target='RH refine sign mounting spacers STEEL'
            SUPPORT.register('refinement signs',group+' wall plate','RH refine '+group+' STEEL',target,[p],-n,'wall')


def plate(name,body,wi,u,z,width=1.9,height=.34,depth=.08):
    w=WALLS[wi]; g='sign '+name
    dg=bpy.context.evaluated_depsgraph_get(); requested=(u,z); blockers=set()
    def clear(uu,zz):
        for i in range(65):
            for j in range(5):
                p=w.pt(uu-width*.48+i*width*.96/64,1.4)
                origin=Vector((p.x,p.y,zz+.02+j*(height-.04)/4))
                direction=Vector((-w.n.x,-w.n.y,0))
                for _ in range(12):
                    hit,loc,n,face,ob,mw=SC.ray_cast(dg,origin,direction,distance=1.3)
                    if not hit: break
                    surface=any(m and m.use_nodes and any(node.type=='OUTPUT_MATERIAL' and node.inputs['Surface'].is_linked for node in m.node_tree.nodes) for m in getattr(ob.data,'materials',[]))
                    if surface:
                        if (Vector((loc.x,loc.y))-w.P).dot(w.n)>depth+.041:
                            blockers.add(ob.name); return False
                        break
                    origin=loc+direction*.001
        return True
    found=False; requested_width=width
    for candidate_width in (requested_width,requested_width*.9,requested_width*.8,requested_width*.7,requested_width*.6):
        width=candidate_width
        for zz in (z,z+.5,z+1.0,z+1.2,z+1.5,z+2.0):
            for du in (0,.15,-.15,.30,-.30,.50,-.50,.75,-.75,1.0,-1.0,1.3,-1.3):
                uu=u+du
                if uu-width/2<.55 or uu+width/2>w.L-.55: continue
                if clear(uu,zz): u,z=uu,zz; found=True; break
            if found: break
        if found: break
    if not found: raise RuntimeError('No unobstructed plaque face: '+name+'; blockers: '+str(sorted(blockers)))
    for du in (-width*.35,width*.35):
        wallbox(g,'STEEL',w,u+du-.025,u+du+.025,z+.10,z+height-.05,.014,depth,.003)
    sign_wall_mount(g,w,[u-width*.35,u+width*.35],[z+height*.4,z+height*.7],.014)
    wallbox(g,'PANEL',w,u-width/2,u+width/2,z,z+height,depth,depth+.035,.004)
    wallbox(g,'ORANGE',w,u-width/2+.03,u+width/2-.03,z+.018,z+.030,depth+.035,depth+.036,0)
    size=min(height*.42,width/(max(1,max(map(len,body.splitlines())))*.65))
    o=walltext(name,body,w,u,z+height*.56,depth+.0368,size)
    SIGN_RECORDS.append(dict(name=o.name,plate='RH refine '+g+' PANEL',
        wall=wi,normal=[w.n.x,w.n.y,0],centre=list(o.location),
        width=width,height=height,size=size,requested=list(requested),placed=[u,z]))
    return o

def signs():
    SUPPORT.reset('refinement signs')
    # Legacy sign plates are joined separately from machinery. Replace the whole
    # sign system so there are no abandoned duplicate plaques behind new labels.
    for o in list(bpy.data.objects):
        if o.name.startswith(('R2 board ','R2 station sign ',
            'R2 stations station sign plate','R2 stations station sign rim')):
            kill(o)
        elif o.name.startswith('MERGED 27 R2 STATIO R2 sign text'):
            kill(o)
    # Large boards stand ahead of the columns on registered brackets, rather
    # than moving text alone while leaving indicators bisected by the steel.
    for wi,z,label in ((2,6.4,'REACTOR STABILITY'),(6,6.4,'COOLANT / POWER'),(4,6.4,'CONTAINMENT')):
        # The fixed gantry ladder obscured the east board from the floor
        # circulation approach. Move its complete assembly into the north bay.
        w=WALLS[wi]; u=9.6 if wi==2 else 6.; g='board '+label; W=3.4
        wallbox(g,'STEEL',w,u-.14,u+.14,z+.82,z+1.18,.35,.435)
        sign_wall_mount(g,w,[u-.09,u+.09],[z+.88,z+1.12],.35)
        wallbox(g,'PANEL',w,u-W/2,u+W/2,z,z+1.35,.435,.49,.008)
        wallbox(g,'INK',w,u-1.58,u+1.58,z+.12,z+1.23,.49,.501,.002)
        walltext(label,label,w,u,z+.91,.502,.23)
        walltext(label+' scale','50',w,u-.005,z+.16,.502,.075)
        for i in range(10):
            a=u-1.40+i*.285
            wallbox(g,'LEVEL'+str(9-i),w,a,a+.225,z+.30,z+.55,.502,.513,.003)
        for i,tag in enumerate(('NORMAL','WARNING','CRITICAL')):
            walltext(label+' '+tag,tag,w,u-.95+i*.95,z+1.16,.502,.07,tag)
        SIGN_RECORDS.append(dict(name='RH refine '+label,plate='RH refine '+g+' PANEL',
            wall=wi,normal=[w.n.x,w.n.y,0],centre=list(walltext(label+' identity',
                'REACTOR STABILITY MARGIN',w,u,z+.69,.502,.075).location),width=W,height=1.35,size=.23))
    # Clear wall bays between the column grid; reserve/gen labels now belong to
    # their machine bays instead of the doorway silhouette.
    for body,wi,u,z,width in (
        ('GRID / DEMAND',2,4.5,3.95,2.1),('TURBINE HALL',2,1.3,3.95,1.4),
        ('STANDBY GENERATOR',6,10.6,3.95,1.6),('RESERVE POWER A',6,1.5,3.95,2.0),
        ('FUEL RECEIVING',4,10.5,3.95,2.),
        ('FUEL CART BAY',5,1.6,3.95,1.9),('BANK CONTROL',4,1.5,3.95,1.9),
        ('VENT CONTROL',3,1.7,3.95,1.7),('WASTE TRANSFER',3,5.1,3.95,1.7),
        ('EMERGENCY COOLING',0,7.5,3.95,2.1),('COOLANT PUMP P-10',0,1.5,3.95,2.0)):
        plate(body,body,wi,u,z,width)
    # Reserve B is on the west cabinet, not the diagonal wall behind the lift.
    for y in (-5.02,-4.60):
        K.prism(('reserve B label mounts','STEEL'),(-9.14,y,1.78),(-9.104,y,1.78),.009,.009,12,0,True,0)
    S.nameplate(K,'reserve B label','+x',-9.104,-4.81,1.78,.60,.12,'PANEL',True)
    text('RESERVE POWER B','RESERVE POWER B',(-9.098,-4.81,1.78),(1,0,0),.045)
    o=bpy.data.objects.get('Emergency cooling legend')
    if o:
        K.bx(('emergency cooling lower caption','PANEL'),2.31,2.79,-8.440,-8.434,.82,.92,.001)
        o.location.y=-8.433
        o.data.materials.clear(); o.data.materials.append(M['SIGN'])
    for o in list(bpy.data.objects):
        if o.name.startswith('MERGED 04 BANK MECH R2 sign text'): kill(o)
    for tag,x in (('A',-1.4),('B',1.4)):
        g='bank heading '+tag
        for dx in (-.42,.42):
            K.bx((g,'STEEL'),x+dx-.025,x+dx+.025,-1.230,-1.205,11.67,11.77,.002)
        K.bx((g,'PANEL'),x-.60,x+.60,-1.252,-1.230,11.56,11.88,.004)
        text('bank heading '+tag,'CONTROL BANK '+tag,(x,-1.253,11.74),(0,-1,0),.135)
    # Existing motto geometry is too faint/low; regenerate it in a quiet bay.
    for o in list(bpy.data.objects):
        if o.name.startswith('R2 gfx') and 'watch' in o.name.lower(): kill(o)
    plate('pool instruction','WATCH THE GREEN.\nIF IT TURNS, DON\'T RUN.',4,1.7,4.75,1.7,.52)
    # Exit pictogram faces must retain contrast and use the current safety palette.
    for name,col,energy in (('RH services exit face',(.012,.012,.012),0),
        ('RH services exit green',(.80,.78,.71),.7)):
        m=bpy.data.materials.get(name)
        if m and m.node_tree:
            for b in m.node_tree.nodes:
                if b.type=='BSDF_PRINCIPLED':
                    b.inputs['Base Color'].default_value=(*col,1)
                    b.inputs['Emission Color'].default_value=(*col,1)
                    b.inputs['Emission Strength'].default_value=energy
    # Give the surviving channel/tank text a useful hierarchy at its actual face.
    for o in bpy.data.objects:
        if o.type=='FONT' and o.name.startswith('GRID / L'):
            o.data.size=.10
            o.data.materials.clear(); o.data.materials.append(M['SIGN'])
        if o.type=='FONT' and o.name.startswith(('EC-1.number','EC-2.number')):
            o.location.z=1.92; o.data.size=.105
            o.data.materials.clear(); o.data.materials.append(M['SIGN'])
    for x,tag in ((.1,'V-01'),(-1.2,'V-02')):
        K.prism(('valve tag mounts','STEEL'),(x,-9.345,1.07),(x,-9.065,.85),.006,.006,8,0,True,0)
        K.bx(('valve tags','PANEL'),x-.12,x+.12,-9.08,-9.05,.74,.86,.003)
        text(tag,tag,(x,-9.049,.80),(0,1,0),.075)

def surface(key,base,rough,metal=0,variation=.15,bump=.0):
    m=rh_mats.surf('RH refine '+key,base,rough,metal,mottle=variation,
        streak=0,grime=0,scale=1.3,bump=bump)
    for n in m.node_tree.nodes:
        if n.type=='TEX_NOISE': n.inputs['Detail'].default_value=2
    return m

def architecture():
    # Operable-looking furniture is registered to the existing formed door leaves,
    # rather than guessed from the wider hall openings three metres in front.
    for wi,name in ((6,'MAIN ACCESS'),(4,'FUEL HANDLING'),(1,'COOLING PLANT')):
        w=WALLS[wi]
        for o in list(bpy.data.objects):
            if o.type!='MESH' or not o.name.startswith(name+'.door leaf'): continue
            pts=[o.matrix_world@Vector(v) for v in o.bound_box]
            us=[(Vector((p.x,p.y))-w.P).dot(w.t) for p in pts]
            ds=[(Vector((p.x,p.y))-w.P).dot(w.n) for p in pts]
            a,b=min(us),max(us); z0,z1=min(p.z for p in pts),max(p.z for p in pts)
            d=max(ds)+.045; outer=a if (a+b)/2< w.L/2 else b
            latch=b-.22 if outer==a else a+.22; g='door hardware '+o.name
            for z in (z0+.32,(z0+z1)/2,z1-.32):
                wallbox(g,'STEEL',w,outer-.055,outer+.055,z-.09,z+.09,d-.042,d-.028,.003)
                p=w.pt(outer,d-.020)
                K.cyl((g,'GALV'),p.x,p.y,z-.10,z+.10,.025,16,0)
            for z in (1.17,1.43):
                p0=w.pt(latch,d-.007); p1=w.pt(latch,d+.055)
                K.prism((g,'STEEL'),(p0.x,p0.y,z),(p1.x,p1.y,z),.016,.016,12,0,True,0)
            p=w.pt(latch,d+.055)
            K.cyl((g,'STEEL'),p.x,p.y,1.13,1.47,.021,16,.003)
            wallbox(g,'STEEL',w,a+.10,b-.10,.10,.55,d,d+.006,.003)
            walltext(g+' leaf id',name.split()[0],w,(a+b)/2,3.40,d+.008,.095)

def materials_and_light():
    # Reduce both participating media, using candidate-owned copies. The
    # control-room medium and source world's lighting/background stay intact.
    if SC.world:
        world=SC.world.copy();world.name='RH refine hall world';SC.world=world
        for node in world.node_tree.nodes:
            if node.type in ('VOLUME_SCATTER','VOLUME_ABSORPTION','PRINCIPLED_VOLUME') and not node.inputs['Density'].is_linked:
                node.inputs['Density'].default_value*=.20
    haze=bpy.data.objects.get('LP haze volume')
    if haze:
        for i,material in enumerate(haze.data.materials):
            local=material.copy();local.name='RH refine hall haze';haze.data.materials[i]=local
            for node in local.node_tree.nodes:
                if node.type in ('VOLUME_SCATTER','VOLUME_ABSORPTION','PRINCIPLED_VOLUME') and not node.inputs['Density'].is_linked:
                    node.inputs['Density'].default_value*=.20
    families={
        'RH walls concrete':surface('wall concrete',(.33,.332,.33),.88,bump=.003),
        'RH walls concrete pour':surface('cast concrete',(.40,.402,.398),.85,bump=.003),
        'RH walls concrete plinth':surface('wall plinth',(.095,.097,.096),.86),
        'RH walls audi grey':surface('wall painted steel',(.072,.074,.074),.60,.30),
        'RH walls audi satin':surface('wall steel panel',(.10,.102,.102),.64,.25),
        'RH walls steel':surface('structural steel',(.14,.144,.144),.48,.65),
        'RH dark audi grey':surface('Audi metallic grey',(.105,.106,.107),.48,.28),
        'RH stations audi grey':surface('Audi metallic grey',(.105,.106,.107),.48,.28),
        'RH audi grey satin':surface('equipment painted steel',(.16,.162,.163),.62,.12),
        'RH structural steel':surface('exposed steel',(.12,.123,.123),.46,.65),
        'RH cast iron':surface('cast iron',(.11,.112,.108),.78,.40),
        'RH galvanised steel':surface('galvanised metal',(.29,.292,.288),.43,.80),
        'RH safety yellow':surface('matte safety yellow',(.57,.40,.022),.72),
        'RH safety orange':surface('matte safety orange',(.56,.13,.018),.70),
        'RH safety red':surface('painted safety red',(.32,.023,.017),.60,.18),
        'RH signal white':surface('signal ivory',(.70,.69,.65),.73),
        'RH black polymer':surface('moulded black polymer',(.018,.018,.018),.77),
        'R2 bank enamel':surface('bank enamel',(.09,.092,.093),.57,.35),
        'R2 iron':surface('bank structural steel',(.10,.102,.101),.52,.6),
        'R2 trim rust':surface('bank orange trim',(.46,.105,.018),.68,.15),
        'RP gunmetal':surface('drive gunmetal',(.135,.137,.135),.48,.7),
        'RP chrome rod':surface('polished absorber steel',(.36,.37,.36),.27,.95),
    }
    protected={'31 CR CONTROL ROOM REDO','32 CR COLLISION','20 CONTROL MEZZANINE'}
    for o in bpy.data.objects:
        if o.name.startswith(('CR ','CR_','COL ')) or protected.intersection(c.name for c in o.users_collection): continue
        if o.type in {'MESH','CURVE','FONT'}:
            for i,m in enumerate(o.data.materials):
                if m and m.name in families: o.data.materials[i]=families[m.name]
    # Preserve the source exposure/cameras. The scene itself gets neutral practical
    # lighting and localized pool light, with unchanged seconds/state drivers.
    factors={'Reactor state key':.10,'LP reactor beam':.04,
        'LP reactor fill low':.15,'Pool surface scattered cyan':.10,'Cyan from deep pool':.08,
        'LP waste hatch':.12}
    for o in bpy.data.objects:
        if o.type!='LIGHT' or o.name.startswith(('CR ','CR_')): continue
        if o.name in factors:
            k=factors[o.name]
            if o.name=='LP waste hatch': o.data.color=(.96,.97,.96)
            for fc in (o.data.animation_data.drivers if o.data.animation_data else []):
                if fc.data_path=='energy':
                    if 'rh_refine_energy_expr' not in o: o['rh_refine_energy_expr']=fc.driver.expression
                    fc.driver.expression=str(k)+'*('+o['rh_refine_energy_expr']+')'
            if not o.data.animation_data or not any(f.data_path=='energy' for f in o.data.animation_data.drivers):
                if 'rh_refine_energy' not in o: o['rh_refine_energy']=o.data.energy
                o.data.energy=o['rh_refine_energy']*k
    for name in ('RH services lamp lens','RH walls lamp warm'):
        m=bpy.data.materials.get(name)
        if m and m.node_tree:
            for n in m.node_tree.nodes:
                if n.type=='BSDF_PRINCIPLED':
                    n.inputs['Base Color'].default_value=(.80,.81,.79,1)
                    n.inputs['Emission Color'].default_value=(.93,.94,.91,1)
    rim=state_glow('RH refine pool rim indicator','.4')
    for o in bpy.data.objects:
        if o.name.startswith('R2 detail pool rim glow'):
            for i,m in enumerate(o.data.materials):
                if m and m.name=='R2 state glow': o.data.materials[i]=rim
        elif o.name.startswith(('LP wash','LP roof shaft','LP rim','LP task')):
            o.data.color=(.96,.97,.96)
            # Reveal operating zones while retaining darker secondary spaces.
            k=1.35 if o.name.startswith('LP task') else 1.4
            for fc in (o.data.animation_data.drivers if o.data.animation_data else []):
                if fc.data_path=='energy':
                    if 'rh_refine_energy_expr' not in o: o['rh_refine_energy_expr']=fc.driver.expression
                    fc.driver.expression=str(k)+'*('+o['rh_refine_energy_expr']+')'
            if not o.data.animation_data or not any(f.data_path=='energy' for f in o.data.animation_data.drivers):
                if 'rh_refine_energy' not in o: o['rh_refine_energy']=o.data.energy
                o.data.energy=o['rh_refine_energy']*k

def finish_fixtures_and_banks():
    fixture=surface('cast lamp finish',(.18,.184,.182),.68,.30)
    gantry=surface('gantry structural grey',(.16,.165,.16),.62,.45)
    cone_materials={}
    for key,color,rough in (('ORANGE',(.56,.13,.018),.70),('WHITE',(.65,.64,.60),.56),('RUBBER',(.018,.018,.018),.84)):
        mat=surface('cone '+key.lower(),color,rough,0,variation=.10 if key=='RUBBER' else .06,bump=.0006 if key=='RUBBER' else .0002)
        nt=mat.node_tree;shader=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
        prior=shader.inputs['Base Color'].links[0].from_socket
        geo=nt.nodes.new('ShaderNodeNewGeometry');xyz=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],xyz.inputs[0])
        mask=nt.nodes.new('ShaderNodeMapRange');mask.clamp=True;mask.inputs['From Min'].default_value=.04;mask.inputs['From Max'].default_value=.22
        mask.inputs['To Min'].default_value=.65;mask.inputs['To Max'].default_value=.025;nt.links.new(xyz.outputs['Z'],mask.inputs[0])
        noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=24;nt.links.new(geo.outputs['Position'],noise.inputs['Vector'])
        patches=nt.nodes.new('ShaderNodeValToRGB');patches.color_ramp.elements[0].position=.50;patches.color_ramp.elements[1].position=.66
        nt.links.new(noise.outputs['Fac'],patches.inputs[0])
        weight=nt.nodes.new('ShaderNodeMath');weight.operation='MULTIPLY';nt.links.new(mask.outputs[0],weight.inputs[0]);nt.links.new(patches.outputs['Color'],weight.inputs[1])
        grime_weight=weight.outputs[0]
        if key=='RUBBER':
            limit=nt.nodes.new('ShaderNodeMath');limit.operation='MULTIPLY';limit.inputs[1].default_value=.18
            nt.links.new(grime_weight,limit.inputs[0]);grime_weight=limit.outputs[0]
        dirt=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(grime_weight,dirt.inputs[0]);nt.links.new(prior,dirt.inputs[1]);dirt.inputs[2].default_value=(.075,.062,.042,1)
        nt.links.new(dirt.outputs[0],shader.inputs['Base Color']);cone_materials[key]=mat
    for o in bpy.data.objects:
        if o.type=='MESH' and o.name.startswith(('RH stations props cone ','RH refine legacy cones ')):
            key=o.name.rsplit(' ',1)[-1]
            if key in cone_materials:
                for i in range(len(o.data.materials)):o.data.materials[i]=cone_materials[key]
        if o.type=='MESH' and o.name=='RH pool girder YELLOW':
            for i in range(len(o.data.materials)): o.data.materials[i]=gantry
        if o.type=='LIGHT' and o.name.startswith('LP bank '):
            o.data.color=(.96,.97,.96)
            if 'gantry lamp' in o.name:
                target=Vector((o.location.x,0,4.5))
                o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
        if o.type=='MESH' and o.name.startswith(('RH services fixture GALV','RH services cage GALV')):
            for i,m in enumerate(o.data.materials): o.data.materials[i]=fixture

def refine_pool_optics_and_legacy_labels():
    well=state_glow('RH refine submerged well indicator','.30')
    for object in bpy.data.objects:
        if object.type=='MESH' and object.name.startswith(('Core light well','Deep cyan emitter')):
            for i,material in enumerate(object.data.materials):
                if material and material.name=='pool_glow':object.data.materials[i]=well
    medium=bpy.data.materials.get('pool_medium')
    if medium:
        nt=medium.node_tree
        if nt.animation_data:
            for fc in list(nt.animation_data.drivers):
                if 'Volume Absorption' in fc.data_path and 'Color' in fc.data_path: nt.animation_data.drivers.remove(fc)
        for node in list(nt.nodes):
            if node.type=='VOLUME_ABSORPTION':
                node.inputs['Density'].default_value=.012
                node.inputs['Color'].default_value=(.80,.80,.80,1)
            if node.type=='VOLUME_SCATTER':
                # Water scatters neutral practical light without behaving like
                # a green filter. Retain a restrained driven-color component.
                node.inputs['Density'].default_value=.0003
                destinations=[link.to_socket for link in node.outputs[0].links]
                neutral=nt.nodes.new('ShaderNodeVolumeScatter');neutral.name='RH neutral water scatter'
                neutral.inputs['Density'].default_value=.0027;neutral.inputs['Color'].default_value=(.65,.65,.63,1)
                mix=nt.nodes.new('ShaderNodeAddShader');mix.name='RH water scatter blend'
                nt.links.new(node.outputs[0],mix.inputs[0]);nt.links.new(neutral.outputs[0],mix.inputs[1])
                for socket in destinations:nt.links.new(mix.outputs[0],socket)
    lining=surface('quiet pool lining',(.29,.295,.285),.85,0,variation=.10,bump=.001)
    # Two mineral trails start at actual vertical/horizontal grout junctions,
    # one course below the water surface. No invented pipe leak is implied.
    nt=lining.node_tree;geo=nt.nodes.new('ShaderNodeNewGeometry')
    separate=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],separate.inputs[0])
    masks=[]
    for seam,end in ((7,-2.10),(9,-1.85)):
        angle=2*math.pi*(seam+.5)/32
        origin=Vector((3.4*math.cos(angle),3.4*math.sin(angle),0))
        delta=nt.nodes.new('ShaderNodeVectorMath');delta.operation='SUBTRACT';delta.inputs[1].default_value=origin
        nt.links.new(geo.outputs['Position'],delta.inputs[0])
        xy=nt.nodes.new('ShaderNodeVectorMath');xy.operation='MULTIPLY';xy.inputs[1].default_value=(1,1,0);nt.links.new(delta.outputs['Vector'],xy.inputs[0])
        length=nt.nodes.new('ShaderNodeVectorMath');length.operation='LENGTH';nt.links.new(xy.outputs[0],length.inputs[0])
        width=nt.nodes.new('ShaderNodeMapRange');width.clamp=True;width.interpolation_type='SMOOTHSTEP'
        for i,value in enumerate((.02,.17,.55,0),1):width.inputs[i].default_value=value
        nt.links.new(length.outputs['Value'],width.inputs[0])
        fade=nt.nodes.new('ShaderNodeMapRange');fade.clamp=True
        for i,value in enumerate((end,end+.5,0,1),1):fade.inputs[i].default_value=value
        nt.links.new(separate.outputs['Z'],fade.inputs[0])
        top=nt.nodes.new('ShaderNodeMath');top.operation='LESS_THAN';top.inputs[1].default_value=-1.135;nt.links.new(separate.outputs['Z'],top.inputs[0])
        mask=nt.nodes.new('ShaderNodeMath');mask.operation='MULTIPLY';nt.links.new(width.outputs[0],mask.inputs[0]);nt.links.new(fade.outputs[0],mask.inputs[1])
        clipped=nt.nodes.new('ShaderNodeMath');clipped.operation='MULTIPLY';nt.links.new(mask.outputs[0],clipped.inputs[0]);nt.links.new(top.outputs[0],clipped.inputs[1]);masks.append(clipped.outputs[0])
    maximum=nt.nodes.new('ShaderNodeMath');maximum.operation='MAXIMUM'
    nt.links.new(masks[0],maximum.inputs[0]);nt.links.new(masks[1],maximum.inputs[1])
    shader=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');base=shader.inputs['Base Color'].links[0].from_socket
    mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[2].default_value=(.48,.46,.42,1)
    nt.links.new(maximum.outputs[0],mix.inputs[0]);nt.links.new(base,mix.inputs[1]);nt.links.new(mix.outputs[0],shader.inputs['Base Color'])
    for o in bpy.data.objects:
        if o.name.startswith('R2 pool pool lining'):
            for i in range(len(o.data.materials)): o.data.materials[i]=lining
    water=bpy.data.materials.get('water')
    if water:
        water_surface=bpy.data.objects.get('Water surface')
        if water_surface and water_surface.type=='MESH':
            water_surface.data.materials.clear(); water_surface.data.materials.append(water)
            water_surface.data.materials.append(bpy.data.materials['RH refine transparent film underside'])
            for poly in water_surface.data.polygons: poly.material_index=1 if poly.normal.z<-.5 else 0
        for node in water.node_tree.nodes:
            if node.type=='MATH' and node.operation=='MULTIPLY':
                node.inputs[1].default_value=1.0
            if node.type=='BSDF_GLOSSY':
                node.inputs['Color'].default_value=(.9,.9,.9,1)
                node.inputs['Roughness'].default_value=.075
            if node.type=='BUMP':
                node.inputs['Strength'].default_value=.15
                node.inputs['Distance'].default_value=.0015
    caustics=bpy.data.materials.get('RP caustics')
    if caustics:
        for node in caustics.node_tree.nodes:
            if node.type=='EMISSION': node.inputs['Strength'].default_value=.25
    for o in bpy.data.objects:
        if o.type=='MESH' and o.name.startswith('RP pool depth marker '):
            centre={'1 M':-1.47,'3 M':-3.47,'5 M':-5.47}[o.name.rsplit('marker ',1)[1]]
            for v in o.data.vertices: v.co.z=centre+(v.co.z-centre)*1.5
    # Retained glyphs were left behind replacement face geometry. Move their
    # world geometry onto the actual new face, preserving bindings and names.
    for name,y in (('WA A manifest sheet.legend',10.575),('WA A manifest.legend',10.575),
                   ('WA A supply junction.legend',10.438)):
        o=bpy.data.objects.get(name)
        if not o: continue
        if o.type=='MESH':
            inv=o.matrix_world.inverted()
            for v in o.data.vertices:
                p=o.matrix_world@v.co; p.y=y; v.co=inv@p
        elif o.type=='FONT': o.location.y=y
    for name,p,n in (('03 BANK CONTROL.mode legend',(3.14,10.414,1.17),(0,-1,0)),
                      ('08 GRID DEMAND.mode legend',(10.404,.94,1.17),(-1,0,0))):
        o=bpy.data.objects.get(name)
        if o:
            o.location=p
            o.rotation_euler=(math.pi/2,0,math.atan2(n[1],n[0])+math.pi/2)

M['GLOW']=bpy.data.materials['R2 state glow']
M['BANK_SIGNAL']=state_glow('RH refine restrained bank signal','.04')
M['ABSORBER']=rh_mats.surf('RH refine absorber satin',(.10,.105,.10),.60,.70,bump=0)
M['DRIVE_METAL']=rh_mats.surf('RH refine drive guide metal',(.68,.69,.685),.30,.75,bump=0)
# Existing integrated materials are retained by surf(), so also update their
# linked inputs. This keeps fresh and incremental builds on the same finishes.
import rh_rod_finishes
rh_rod_finishes.apply(SC,bpy.data.materials)
for o in list(bpy.data.objects):
    if any(o.name.startswith('GRID / L'+str(i)+'.identifier') for i in (1,2,3)):
        kill(o)
signs()
architecture()
import rh_refine_geometry
rh_refine_geometry.build(K,M,text)
import rh_refine_alcoves
rh_refine_alcoves.build(K,M,COL)
made=K.build(COL,'RH refine',M)
bpy.context.view_layer.update()
import rh_door_hardware_seats
rh_door_hardware_seats.build()
import rh_drum_hoops
rh_drum_hoops.apply(SC,bpy.data.objects)
rh_refine_geometry.clip_water_to_slab()
materials_and_light()
finish_fixtures_and_banks()
refine_pool_optics_and_legacy_labels()
# Sightline and fixed-guide corrections need the completed panels and final
# fixture materials in the scene, rather than geometry still queued in K.
import rh_roof_utilities, rh_zone_sign, rh_rod_guides, rh_blind_covers, rh_vent_identity, rh_gauge_placement, rh_steam_gauge_placement, rh_steam_gauge_seat, rh_steam_gauge_port, rh_waste_gauge_placement, rh_gauge_information, rh_gauge_bezels, rh_p10_service_practical
corrections=crk.Kit()
bpy.context.view_layer.update()
rh_roof_utilities.build(corrections,M)
rh_zone_sign.build(corrections,M)
rh_rod_guides.build(corrections,M)
rh_blind_covers.build(corrections,M)
rh_vent_identity.build()
rh_gauge_placement.build()
rh_steam_gauge_placement.build()
rh_steam_gauge_seat.build()
rh_steam_gauge_port.build()
rh_waste_gauge_placement.build()
rh_gauge_information.build()
rh_gauge_bezels.build()
rh_p10_service_practical.build(corrections,M)
made+=corrections.build(COL,'RH refine',M)
bpy.context.view_layer.update()
import rh_roof_crossing_fit, rh_roof_girder_finish, rh_floor_aggregate_finish, rh_pool_diffuser_fit, rh_floor_travel_wear, rh_service_oil_film, rh_stability_board_scale
SC['rh_roof_girder_finish']=json.dumps(rh_roof_girder_finish.apply(bpy.data.objects),sort_keys=True)
SC['rh_roof_crossing_fit']=json.dumps(rh_roof_crossing_fit.apply(SC,bpy.data.objects),sort_keys=True)
rh_pool_diffuser_fit.apply(SC,bpy.data.objects)
SC['rh_floor_aggregate_finish']=json.dumps(rh_floor_aggregate_finish.apply(bpy.data.materials),sort_keys=True)
SC['rh_floor_travel_wear']=json.dumps(rh_floor_travel_wear.apply(bpy.data.materials),sort_keys=True)
rh_service_oil_film.build()
rh_stability_board_scale.apply(SC,bpy.data.objects)
# Local material corrections follow the completed pool lining and retained
# doorway return meshes so fresh stage builds reproduce the reviewed candidate.
import rh_pool_stain_contrast_fit, rh_door_return_stain_fit
rh_pool_stain_contrast_fit.apply(SC,bpy.data.materials)
rh_door_return_stain_fit.apply(SC,bpy.data.objects,bpy.data.materials)
import rh_pool_stain_readability_fit
rh_pool_stain_readability_fit.apply(SC,bpy.data.materials)
import rh_switchgear_bollard_access_fit
rh_switchgear_bollard_access_fit.apply(SC,bpy.data.objects)
import rh_hoist_deadend_anchor_fit, rh_hoist_aperture_tasklight
rh_hoist_deadend_anchor_fit.apply(SC,bpy.data.objects,bpy.data.materials)
rh_hoist_aperture_tasklight.apply(SC,bpy.data.objects,bpy.data.materials)
import rh_switchgear_circuit_label_fit
rh_switchgear_circuit_label_fit.apply(SC,bpy.data.objects,bpy.data.materials)
import rh_roof_bearing_tasklights
rh_roof_bearing_tasklights.apply(SC,bpy.data.objects,bpy.data.materials)
import rh_generator_sign_sightline_fit
rh_generator_sign_sightline_fit.apply(SC,bpy.data.objects)
bpy.context.view_layer.update()
Path(DST).parent.mkdir(parents=True,exist_ok=True)
Path(DST).with_suffix('.signs.json').write_text(json.dumps(SIGN_RECORDS,indent=2)+'\n')
SC['hall_refinement']='140-item owner correction pass; independent verification pending'
bpy.ops.wm.save_as_mainfile(filepath=DST)
print('REFINEMENT_SAVED',DST,'new_objects',len(made),flush=True)
sys.stdout.flush(); os._exit(0)
