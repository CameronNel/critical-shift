"""Owned dead-shift construction and lighting for the existing fuel module.

No runtime controllers or external material assets. Damage is authored in a few
measured clusters; original wall/floor/port contracts stay fixed. Flicker keys
belong to each fixture's isolated optic material and its own light data.
"""
import json, math, random, hashlib
import bpy
from mathutils import Matrix, Vector
from fuel_kit import *

FLOOR_DAMAGE = []
ROOF_DAMAGE = []
FLICKER = []
ALARMS = []
PERIOD = 240

def palette_age():
    colors = {'plaster':'#999282','warm plaster':'#968B78','cool plaster':'#7A8987',
              'transfer plaster':'#99857A','mineral':'#87847A',
              'floor':'#706A5E','floor border':'#3D494F','fuel tile light':'#7B7466',
              'fuel tile dark':'#655F54','service tile':'#85735B',
              'service tile light':'#92806A','service tile dark':'#776A58',
              'clean floor':'#879489','clean floor light':'#98A298','clean floor dark':'#7B877D'}
    for family, color in colors.items():
        m=mat(family);rgb=linear(color)
        m.diffuse_color=(*rgb,1)
        ramp=next(n for n in m.node_tree.nodes if n.type=='VALTORGB')
        ramp.color_ramp.elements[0].color=(*(v*.84 for v in rgb),1)
        ramp.color_ramp.elements[1].color=(*(min(1,v*1.11) for v in rgb),1)
    surface('tile mortar','#514E41',.96,0,.0025,4,.19)
    surface('tile exposed biscuit','#A1906F',.96,0,.0016,5,.16)
    surface('corroded iron','#58422C',.87,.25,.0010,3,.24)
    surface('dead tube','#575A4D',.82,0,.0005,5,.12)
    surface('alarm lens','#D3301F',.43,0,.0002,6,.09,emission=3)
    surface('ceiling torn core','#A1947A',.98,0,.0021,5,.16)
    surface('void lining','#242827',.96,.08,.0005,2,.14)

def damage_at(cell,i,j):
    # Missing tiles are small, flush 20 mm recesses in the retained slab, not
    # giant holes in the route. No prop foot or painted arrow lands in them.
    wanted={'west_turn':{(2,3):'missing',(1,3):'broken',(3,2):'broken'},
            'east_turn':{(1,2):'missing',(0,2):'broken'},
            'bypass_north':{(8,6):'missing',(9,6):'broken',(19,3):'missing',(20,3):'broken'},
            'entry':{(2,5):'broken',(1,5):'missing'}}
    return wanted.get(cell['id'],{}).get((i,j))

def worn_tile(b,rect,material,state,cell,i,j):
    a,c,d,e=rect;w=c-a;h=e-d
    if state is None:
        b.box((w,h,.020),((a+c)/2,(d+e)/2,-.010),mat(material),.0014,seg=3)
        return
    FLOOR_DAMAGE.append({'cell':cell['id'],'tile':[i,j],'state':state,'bounds':list(rect),'bed_z':-.020})
    seed=int(hashlib.sha256((cell['id']+str(i)+','+str(j)).encode()).hexdigest()[:8],16)
    rng=random.Random(seed)
    def fracture(pts):
        result=[]
        for p,q in zip(pts,pts[1:]+pts[:1]):
            result.append(p)
            # Retain the tile's original outside boundaries; fracture only the
            # newly exposed edges. Secondary chips stay inside the old tile.
            boundary=(abs(p[0]-q[0])<1e-8 and min(abs(p[0]-a),abs(p[0]-c))<1e-8) or (abs(p[1]-q[1])<1e-8 and min(abs(p[1]-d),abs(p[1]-e))<1e-8)
            if boundary:continue
            dx=q[0]-p[0];dy=q[1]-p[1];length=math.hypot(dx,dy)
            if length<.035:continue
            for t in [.24,.49,.73]:
                nick=rng.uniform(-.009,.009)
                xx=p[0]+t*dx-dy/length*nick;yy=p[1]+t*dy+dx/length*nick
                result.append((min(c-.0005,max(a+.0005,xx)),min(e-.0005,max(d+.0005,yy))))
        return result
    # Rough mineral adhesive, with combed ridges ending beneath retained shards.
    b.box((w,h,.001),( (a+c)/2,(d+e)/2,-.0195),mat('tile mortar'),0)
    for k in range(max(2,int(w/.08))):
        xx=a+.024+k*.08
        b.box((.008,h*.72,.002),(xx,(d+e)/2,-.018),mat('tile mortar'),.0005)
    if state=='missing':
        for pts in [[(a,d),(a+w*.29,d),(a+w*.19,d+h*.11),(a,d+h*.14)],
                    [(c,e),(c-w*.22,e),(c-w*.13,e-h*.09),(c,e-h*.14)],
                    [(a,d+h*.34),(a+w*.09,d+h*.39),(a+w*.04,d+h*.51),(a+w*.12,d+h*.59),(a,d+h*.72)],
                    [(c,d+h*.12),(c-w*.075,d+h*.24),(c-w*.045,d+h*.34),(c-w*.11,d+h*.43),(c,d+h*.57)],
                    [(a+w*.42,d),(a+w*.64,d),(a+w*.58,d+h*.065),(a+w*.48,d+h*.11)],
                    [(a+w*.32,e),(a+w*.58,e),(a+w*.49,e-h*.10),(a+w*.37,e-h*.045)]]:
            pts=fracture(pts)
            polygon(b,pts,.018,mat('tile exposed biscuit'),pos=(0,0,-.019),bevel=.0008)
            polygon(b,pts,.001,mat(material),pos=(0,0,-.001),bevel=.0003)
        for k in range(7):
            xx=a+w*(.23+.085*k);yy=d+h*(.22+((k*3)%5)*.11);s=.018+.003*(k%3)
            polygon(b,[(xx-s,yy),(xx+s,yy-s*.3),(xx+s*.4,yy+s),(xx-s*.5,yy+s*.5)],.003+.001*(k%3),mat('tile exposed biscuit'),pos=(0,0,-.018),bevel=.0005)
    else:
        # Two fractured capped pieces leave an irregular opening and actual
        # exposed biscuit sidewalls, rather than drawing a crack on a full tile.
        pieces=[[(a,d),(c,d),(c,d+h*.32),(a+w*.63,d+h*.38),(a+w*.39,d+h*.61),(a,d+h*.52)],
                [(a,e),(a,d+h*.66),(a+w*.30,d+h*.74),(a+w*.53,d+h*.56),(c,e-h*.20),(c,e)]]
        for pts in pieces:
            pts=fracture(pts)
            polygon(b,pts,.019,mat('tile exposed biscuit'),pos=(0,0,-.020),bevel=.0006)
            polygon(b,pts,.001,mat(material),pos=(0,0,-.001),bevel=.0002)

def roof_tile_missing(cell,i,j):
    return (cell['id']=='west_turn' and (i,j)==(1,2)) or (cell['id']=='entry' and (i,j)==(1,1))

def roof_void(b,rect,h,cell):
    a,c,d,e=rect;w=c-a;depth=e-d
    # The entry canopy already has a 0.60m plenum. The staging roof needs a
    # local enclosed weather hood after cutting the original underside sheet.
    core=bpy.data.objects['Ceiling_'+cell['id']]
    if cell['id']=='west_turn':
        cutter=B();cutter.box((w-.03,depth-.03,.50),((a+c)/2,(d+e)/2,h+.16),mat('void lining'))
        tool=add(cutter,'Roof damage cutter','FC | Construction helpers')
        mod=core.modifiers.new('Authored torn roof opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool
        bpy.context.view_layer.objects.active=core;bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(tool,do_unlink=True)
        top=h+.43
        b.box((w+.10,depth+.10,.025),((a+c)/2,(d+e)/2,top),mat('void lining'),.002)
        for xx in [a-.035,c+.035]:b.box((.025,depth+.10,.43),(xx,(d+e)/2,h+.205),mat('void lining'),.001)
        for yy in [d-.035,e+.035]:b.box((w+.10,.025,.43),((a+c)/2,yy,h+.205),mat('void lining'),.001)
    else:top=cell['height']-.04
    # Jagged retained edges, a bent sheet caught by real straps, pipework and
    # hanging paired cables form the silhouette of this construction failure.
    polygon(b,[(a,d),(c,d),(c,d+.16),(a+w*.67,d+.10),(a+w*.43,d+.21),(a+w*.20,d+.12),(a,d+.25)],.038,mat('ceiling torn core'),pos=(0,0,h-.018))
    for pts in [[(a,e),(c,e),(c,e-.12),(a+w*.78,e-.19),(a+w*.54,e-.09),(a+w*.32,e-.17),(a,e-.11)],
                [(a,d+.28),(a+.12,d+.40),(a+.06,d+.66),(a+.14,e-.30),(a,e-.22)]]:
        polygon(b,pts,.030,mat('ceiling torn core'),pos=(0,0,h-.022),bevel=.001)
        polygon(b,pts,.003,mat('warm enamel'),pos=(0,0,h-.025),bevel=.0005)
    for xx in [a+.08,c-.08]:
        b.box((.035,depth,.09),(xx,(d+e)/2,h+.06),mat('corroded iron'),.002)
        b.box((.09,.055,.012),(xx,d+.12,h+.03),mat('dark steel'),.001)
    b.tube([(a+.15,d+.20,top-.04),(c-.15,d+.20,top-.04)],.034,mat('corroded iron'),seg=16)
    for xx in [a+.22,c-.22]:
        b.box((.030,.022,top-h-.03),(xx,d+.16,(top+h)/2),mat('corroded iron'),.001)
    # Torn hanging flap is still physically connected at its two upper clips.
    flap=B();pw=w*.64;pd=depth*.40
    polygon(flap,[(-pw/2,0),(pw/2,0),(pw/2,pd*.74),(pw*.24,pd*.94),(-pw*.06,pd*.79),(-pw*.32,pd),(-pw/2,pd*.68)],.012,mat('replacement enamel'))
    merge(b,flap,((a+c)/2,d+.16,h+.025),Matrix.Rotation(-.52,3,'X'))
    for xx in [a+w*.30,a+w*.57]:
        b.tube(rounded_path([(xx,d+.20,h+.20),(xx+.10,d+.35,h-.02),(xx+.07,d+.58,h-.35),(xx+.16,d+.63,h-.43)]),.009,mat('rubber'),seg=10)
        b.box((.055,.05,.018),(xx,d+.20,h+.20),mat('dark steel'),.002)
    ROOF_DAMAGE.append({'cell':cell['id'],'opening':list(rect),'underside_z':h,'enclosed_void_top_z':top,'scope':'Authored opening with capped service/weather enclosure; no unintended open sky seam.'})

def local_wear():
    # Broad wheel/contact wear masks in world metres. Keep the packed surface
    # maps and physical UVs; add only the scuffed traffic/contact zones.
    for family in ['floor','floor border','fuel tile light','fuel tile dark','service tile','service tile light','service tile dark','clean floor','clean floor light','clean floor dark','transfer tile','transfer tile light','transfer tile dark']:
        m=mat(family);nodes=m.node_tree.nodes;links=m.node_tree.links;p=nodes.get('Principled BSDF')
        pos=nodes.new('ShaderNodeNewGeometry');split=nodes.new('ShaderNodeSeparateXYZ');links.new(pos.outputs['Position'],split.inputs[0])
        axis=split.outputs['X'];sub=nodes.new('ShaderNodeMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=.25;links.new(axis,sub.inputs[0])
        ab=nodes.new('ShaderNodeMath');ab.operation='ABSOLUTE';links.new(sub.outputs[0],ab.inputs[0])
        mask=nodes.new('ShaderNodeMapRange');mask.clamp=True;mask.inputs['From Min'].default_value=.15;mask.inputs['From Max'].default_value=1.65;mask.inputs['To Min'].default_value=.52;mask.inputs['To Max'].default_value=0;links.new(ab.outputs[0],mask.inputs['Value'])
        noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=2.8;noise.inputs['Detail'].default_value=1.0;links.new(pos.outputs['Position'],noise.inputs['Vector'])
        weight=nodes.new('ShaderNodeMath');weight.operation='MULTIPLY';links.new(mask.outputs['Result'],weight.inputs[0]);links.new(noise.outputs['Fac'],weight.inputs[1])
        prior=p.inputs['Base Color'].links[0].from_socket
        mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[2].default_value=(.26,.27,.22,1)
        links.new(weight.outputs[0],mix.inputs[0]);links.new(prior,mix.inputs[1]);links.new(mix.outputs[0],p.inputs['Base Color'])
    # Damp low-wall contact bands and a few leaking ceiling junctions. The
    # falloff is in world metres, and retains the packed albedo/relief beneath.
    for family in ['plaster','warm plaster','cool plaster','transfer plaster','navy enamel','repaired blue enamel','sanitary ceramic','sanitary ceramic light']:
        m=mat(family);nodes=m.node_tree.nodes;links=m.node_tree.links;p=nodes.get('Principled BSDF')
        pos=nodes.new('ShaderNodeNewGeometry');split=nodes.new('ShaderNodeSeparateXYZ');links.new(pos.outputs['Position'],split.inputs[0])
        low=nodes.new('ShaderNodeMapRange');low.clamp=True;low.inputs['From Min'].default_value=.12;low.inputs['From Max'].default_value=.68;low.inputs['To Min'].default_value=.55;low.inputs['To Max'].default_value=0;links.new(split.outputs['Z'],low.inputs['Value'])
        noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=6;noise.inputs['Detail'].default_value=2;links.new(pos.outputs['Position'],noise.inputs['Vector'])
        damp=nodes.new('ShaderNodeMath');damp.operation='MULTIPLY';links.new(low.outputs['Result'],damp.inputs[0]);links.new(noise.outputs['Fac'],damp.inputs[1])
        total=damp.outputs[0]
        for center in [(-2.17,3.62,3.48),(1.30,13.16,3.94),(9.85,18.045,2.80)]:
            vec=nodes.new('ShaderNodeVectorMath');vec.operation='SUBTRACT';vec.inputs[1].default_value=center;links.new(pos.outputs['Position'],vec.inputs[0])
            stretch=nodes.new('ShaderNodeVectorMath');stretch.operation='MULTIPLY';stretch.inputs[1].default_value=(2.3,2.3,.58);links.new(vec.outputs[0],stretch.inputs[0])
            dist=nodes.new('ShaderNodeVectorMath');dist.operation='LENGTH';links.new(stretch.outputs[0],dist.inputs[0])
            fall=nodes.new('ShaderNodeMapRange');fall.clamp=True;fall.inputs['From Min'].default_value=.12;fall.inputs['From Max'].default_value=1.15;fall.inputs['To Min'].default_value=.83;fall.inputs['To Max'].default_value=0;links.new(dist.outputs['Value'],fall.inputs['Value'])
            weigh=nodes.new('ShaderNodeMath');weigh.operation='MULTIPLY';links.new(fall.outputs['Result'],weigh.inputs[0]);links.new(noise.outputs['Fac'],weigh.inputs[1])
            union=nodes.new('ShaderNodeMath');union.operation='MAXIMUM';links.new(total,union.inputs[0]);links.new(weigh.outputs[0],union.inputs[1]);total=union.outputs[0]
        prior=p.inputs['Base Color'].links[0].from_socket
        mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[2].default_value=(.18,.24,.18,1);links.new(total,mix.inputs[0]);links.new(prior,mix.inputs[1]);links.new(mix.outputs[0],p.inputs['Base Color'])

def action_curve(owner,path,points,interpolation='CONSTANT'):
    for frame,value in points:
        owner.path_resolve(path)
        if path=='energy':owner.energy=value
        else:owner.default_value=value
        owner.keyframe_insert(data_path=path,frame=frame)
    action=owner.id_data.animation_data.action
    slot=owner.id_data.animation_data.action_slot
    for layer in action.layers:
        for strip in layer.strips:
            bag=strip.channelbag(slot)
            if bag:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:key.interpolation=interpolation
                    curve.modifiers.new('CYCLES')

def fixture_keys(light_ob,phase=0):
    base=light_ob.data.energy
    schedule=[(1,.82),(17,.78),(18,.12),(20,.76),(45,.77),(46,.10),(49,.72),(109,.78),(110,.07),(116,.75),(148,.65),(151,.16),(154,.80),(198,.70),(200,.18),(205,.79),(241,.82)]
    if phase:
        mapped=sorted((((f-1+phase)%PERIOD+1,v) for f,v in schedule[:-1]))
        value=next((v for f,v in reversed(mapped) if f<=1),mapped[-1][1]);schedule=[(1,value)]+[(f,v) for f,v in mapped if f>1]+[(241,value)]
    action_curve(light_ob.data,'energy',[(f,base*v) for f,v in schedule])
    fixture=light_ob.parent
    optics=[]
    for slot in fixture.material_slots:
        material=slot.material
        if material and 'diffuser' in material.name:
            own=material.copy();own.name=material.name+' | '+fixture.name
            slot.material=own;p=own.node_tree.nodes.get('Principled BSDF');strength=p.inputs['Emission Strength'];original=strength.default_value
            action_curve(strength,'default_value',[(f,original*v) for f,v in schedule])
            optics.append({'material':own.name,'emission_base':original})
    FLICKER.append({'fixture':fixture.name,'light':light_ob.name,'optics':optics,'keys':schedule,'energy_base_w':base,'period_frames':PERIOD,'channel_scope':'Individual light energy and isolated fixture optic emission; constant interpolation, Cycles repeat.'})

def red_beacon(mounted,name,wall,point,power=16):
    b=B();b.box((.21,.018,.25),(0,-.009,0),mat('ink enamel'),.008)
    for xx in [-.074,.074]:
        for zz in [-.09,.09]:bolt(b,(xx,-.021,zz),.006)
    rot=Matrix.Rotation(math.pi/2,3,'X')
    b.lathe([(0,0),(.071,0),(.080,.015),(.080,.035),(.065,.043),(.065,.075),(.052,.099),(0,.104)],(0,-.018,0),mat('dark steel'),seg=24,rot=rot)
    b.lathe([(.046,.043),(.046,.08),(.035,.11),(0,.114)],(0,-.018,0),mat('alarm lens'),seg=24,rot=rot)
    for xx in [-.052,0,.052]:b.tube([(xx,-.097,-.075),(xx,-.146,-.042),(xx,-.146,.042),(xx,-.097,.075)],.0035,mat('dark steel'),seg=8)
    fixture=mounted(b,name,wall,point,'FC | Practicals','guarded wall-mounted red emergency beacon')
    T=fixture.matrix_world
    pool=light(name+' pool',T@Vector((0,-.146,0)),T@Vector((0,-1.1,-.75)),power,(1,.035,.016),size=.085,parent=fixture.name)
    original=mat('alarm lens');own=original.copy();own.name='FC | '+name+' isolated lens'
    fixture.data.materials[fixture.data.materials.find(original.name)]=own
    schedule=[(1,.70),(25,.70),(32,1),(38,.45),(48,.70),(100,.70),(108,.96),(116,.45),(126,.70),(241,.70)]
    action_curve(pool.data,'energy',[(f,power*v) for f,v in schedule],interpolation='LINEAR')
    action_curve(own.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'],'default_value',[(f,3*v) for f,v in schedule],interpolation='LINEAR')
    ALARMS.append({'fixture':fixture.name,'light':pool.name,'optics':[{'material':own.name,'emission_base':3}],'keys':schedule,'energy_base_w':power,'period_frames':PERIOD,'interpolation':'LINEAR'})

def apply(mounted):
    local_wear()
    for m in list(MATERIALS.values()):
        if 'diffuser' in m.name:m.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value*=.34
    # Actual fixture pools fall off between occupied task points. Emergency
    # beacons are added afterwards, so this does not dim their intended powers.
    for o in list(bpy.context.scene.objects):
        if o.type!='LIGHT' or not o.name.startswith('FC |'):continue
        o.data.energy*=.34
        if 'Bench' in o.name:o.data.energy*=1.20;o.data.color=(1,.64,.32)
        elif 'Cask' in o.name or 'Staging' in o.name:o.data.color=(1,.78,.49)
        elif any(s in o.name for s in ['Clean','North','Bypass']):o.data.color=(.63,.82,.72)
    for name,power in [('Crossing fluorescent pool',29),('Entry fluorescent pool',27),('Staging main pool',80),('Bypass fluorescent pool',24),('Reactor transfer fluorescent pool',47),('Clean fluorescent pool',20),('North fluorescent pool',16),('Delivery fluorescent pool',31)]:
        if (o:=bpy.data.objects.get('FC | '+name)):o.data.energy=power
    dead=bpy.data.objects.get('FC | East fluorescent pool')
    if dead:
        dead.data.energy=0
        for slot in dead.parent.material_slots:
            if slot.material and 'diffuser' in slot.material.name:slot.material=mat('dead tube')
        dead.parent['fc_failure']='Failed lamp; non-emitting optic and zero associated illumination.'
    for name,phase in [('Entry fluorescent pool',0),('Staging main pool',11),('Bench practical pool',73),('Crossing fluorescent pool',57),('Bypass fluorescent pool',113),('Reactor transfer fluorescent pool',31)]:
        if (o:=bpy.data.objects.get('FC | '+name)):fixture_keys(o,phase)
    red_beacon(mounted,'Transfer alarm beacon','Wall_W-2.2_0_1.2',(1.13,-.004,2.47),18)
    red_beacon(mounted,'Waste alarm beacon','Wall_E16.4_0_17.32',(.10,-.004,2.82),13)
    red_beacon(mounted,'Reactor alarm beacon','Wall_E17.0_0_21',(-.25,-.004,3.02),20)
    scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=PERIOD;scene.frame_set(1)
    bg=scene.world.node_tree.nodes.get('Background')
    if bg:bg.inputs['Color'].default_value=(.095,.13,.12,1);bg.inputs['Strength'].default_value=.012
    return {'direction':'Owner-requested eerie, rundown dead-shift fuel corridor; latest reactor WIP PR54 atmosphere, spawn craftsmanship reference unchanged.','floor_damage':FLOOR_DAMAGE,'roof_damage':ROOF_DAMAGE,'flicker':FLICKER,'alarms':ALARMS,'frame_start':1,'frame_end':PERIOD,'closure_frame':PERIOD+1,'fps':scene.render.fps,'fps_base':scene.render.fps_base,'runtime':'Blender authoring keys only; runtime behaviour unverified.'}
