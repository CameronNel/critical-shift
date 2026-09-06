"""Authored decay pockets, anchored webs and readable industrial darkness."""
import bpy,math,random
from mathutils import Vector
from geometry import curve,plank,box,cylinder,mesh,planar_patch
from geology_repairs import tree,settle
from materials import basic,rgba,noise,ramp

def anchored_web(scene,m,origin,seed):
    rng=random.Random(seed);skin=scene.objects.get('CSM_Continuous_stratified_mine_skin');bvh=tree([skin]);origin=Vector(origin)
    sign=-1 if origin.x<0 else 1
    directions=[Vector((sign*.65,-.7,.7)),Vector((sign*.90,.6,.36)),Vector((sign*.20,.35,1.))]
    anchors=[]
    for d in directions:
        hit=bvh.ray_cast(origin,d.normalized(),3.2)
        if hit[0] is None:return None
        norm=hit[1]
        if norm.dot(origin-hit[0])<0:norm=-norm
        anchors.append(hit[0]+norm*.005)
    if max((a-b).length for a in anchors for b in anchors)>3.3:return None
    center=sum(anchors,Vector())/3+(origin-sum(anchors,Vector())/3).normalized()*.06
    ends=[]
    for edge in range(3):
        a,b=anchors[edge],anchors[(edge+1)%3]
        for k in range(6):ends.append(a.lerp(b,k/6))
    paths=[]
    for end in ends:
        paths.append([tuple(center.lerp(end,t)+Vector((0,0,-.045*math.sin(t*math.pi)))) for t in [0,.25,.5,.75,1]])
    for scale in [.18,.32,.49,.67,.84]:
        for i in range(len(ends)):
            if rng.random()<.13:continue
            a=center.lerp(ends[i],scale);b=center.lerp(ends[(i+1)%len(ends)],scale)
            mid=(a+b)*.5+Vector((0,0,-rng.uniform(.008,.021)))
            paths.append([tuple(a),tuple(mid),tuple(b)])
    o=curve('Anchored_dust_web',paths,.0014,m['web']);o['q50_web_anchors']='Raycast to actual geological shell';o['q50_web_seed']=seed
    return {'object':o.name,'anchors':[list(a) for a in anchors],'strand_radius_m':.0014}

def rot_pockets(scene,m):
    floor=scene.objects.get('CSM_Excavated_floor');support=tree([floor]);done=[]
    for k,(x,y) in enumerate([(-2.75,8.5),(-2.72,24.4),(9.25,16.45),(8.75,26.2),(-1.85,36.5)]):
        rng=random.Random(900+k)
        for j in range(4):
            o=plank('Discarded_split_timber',(x+(j-1.5)*.11,y+j*.08,-.025*y+.30),(rng.uniform(.45,.95),rng.uniform(.05,.09),rng.uniform(.035,.07)),m['rot'],rot=(rng.uniform(-.10,.10),rng.uniform(-.05,.05),rng.uniform(-.5,.5)),seed=600+k*10+j,rotted=True)
            bpy.context.view_layer.update();settle(o,support);done.append(o.name)
    return done

def runoff(scene,m):
    skin=scene.objects.get('CSM_Continuous_stratified_mine_skin');bvh=tree([skin]);made=[]
    for k,(x,y,z) in enumerate([(-1.9,7.4,2.3),(1.95,11.8,2.4),(-1.9,24.7,2.0),(8.4,24.9,1.0),(1.9,34.8,1.8),(-1.8,37.2,1.8)]):
        origin=Vector((x,y,z));direction=Vector((1 if x>0 else -1,0,0))
        if x>5:direction=Vector((.6,.6,.1)).normalized()
        for strip in range(3):
            vv=[];ff=[]
            for j in range(11):
                height=z-j*.12;width=.030*(1-j*.06)*(1+.24*math.sin(j*1.8))
                for side in [-1,1]:
                    start=Vector((x,y+(strip-1)*.08+side*width,height));hit=bvh.ray_cast(start,direction,3.)
                    if hit[0] is None:break
                    normal=hit[1]
                    if normal.dot(start-hit[0])<0:normal=-normal
                    vv.append(tuple(hit[0]+normal*.004))
                if len(vv)!=(j+1)*2:break
            for j in range(len(vv)//2-1):ff.append((j*2,j*2+1,j*2+3,j*2+2))
            if ff:
                o=mesh('Rock_water_bleed',vv,ff,m['stain']);made.append(o.name)
    return made

def tune_lighting(scene):
    records=[];main_practicals=[]
    for o in scene.objects:
        if o.type!='LIGHT':continue
        y=o.matrix_world.translation.y;old=o.data.energy
        if o.data.type=='SUN':o.data.energy=.13;o.data.color=(.51,.66,1.)
        elif 'Overcast_sky' in o.name:o.data.energy=1100;o.data.color=(.58,.70,1.)
        elif 'Bay_warm_bounce' in o.name:o.data.energy=120
        elif 'Portal_daylight' in o.name:o.data.energy=85
        elif 'portal_stone_bounce' in o.name:o.data.energy=55
        elif y<0:o.data.energy=old*.65
        elif 'Sump' in o.name or (y>20 and y<23 and o.matrix_world.translation.x>7):o.data.energy=old*.34;o.data.color=(.55,.72,.75)
        elif 'Portable' in o.name:o.data.energy=old*.40
        elif 'bounce' in o.name:o.data.energy=old*.28
        else:
            o.data.energy=old*.29
            if abs(o.matrix_world.translation.x)<1:
                main_practicals.append(o)
                if 9<y<12 or 28<y<32:o.data.energy=old*.065
                o.data.color=(1.,.64,.32) if 20<y<28 else (.52,.67,.82)
            else:o.data.color=(.96,.61,.30)
        if o.data.type=='AREA':o.data.size=max(.35,min(o.data.size,.80))
        records.append({'light':o.name,'before':old,'after':o.data.energy})
    lights=[o for o in scene.objects if o.type=='LIGHT' and o.name.startswith('CSM_Practical')]
    for o in scene.objects:
        if o.type!='MESH' or 'Diffuser' not in o.name:continue
        nearest=min(lights,key=lambda a:(a.matrix_world.translation-o.matrix_world.translation).length)
        if (nearest.matrix_world.translation-o.matrix_world.translation).length>.5:continue
        for slot in o.material_slots:
            if not slot.material:continue
            mat=slot.material.copy();mat.name='Q50_lamp_diffuser_'+o.name;slot.link='OBJECT';slot.material=mat
            p=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
            if p:
                p.inputs['Emission Strength'].default_value=max(.08,min(2.,nearest.data.energy/48))
                p.inputs['Emission Color'].default_value=(*nearest.data.color,1)
                p.inputs['Roughness'].default_value=.82
    bg=scene.world.node_tree.nodes.get('Background')
    if bg:bg.inputs[0].default_value=(.052,.073,.12,1);bg.inputs[1].default_value=.035
    scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-.15
    try:scene.view_settings.look='AgX - Medium High Contrast'
    except TypeError:pass
    mat=bpy.data.materials.new('Q50_Suspended_mine_dust');mat.use_nodes=True;n=mat.node_tree.nodes;n.clear()
    out=n.new('ShaderNodeOutputMaterial');vol=n.new('ShaderNodeVolumePrincipled');vol.inputs['Density'].default_value=.004;vol.inputs['Color'].default_value=(.38,.34,.27,1);vol.inputs['Anisotropy'].default_value=.25
    mat.node_tree.links.new(vol.outputs['Volume'],out.inputs['Volume'])
    haze=box('Localized_underground_haze',(0,28,1),(40,56,12),mat,bevel=0);haze['q50_volumetric']=True
    scene.cycles.volume_bounces=1
    return records

def sump_water(scene,m):
    water=bpy.data.materials.get('GULLET_PBR_groundwater')
    if water:
        n=water.node_tree.nodes;l=water.node_tree.links;p=next(x for x in n if x.type=='BSDF_PRINCIPLED')
        p.inputs['Base Color'].default_value=rgba('292D22');p.inputs['Roughness'].default_value=.38;p.inputs['Transmission Weight'].default_value=.12
        coord=n.new('ShaderNodeTexCoord');v=noise(n,l,coord.outputs['Object'],5.5,3)
        b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.5;b.inputs['Distance'].default_value=.009;l.new(v,b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
    z=-.025*21.55-.235;rng=random.Random(601)
    for j in range(12):
        planar_patch('Sump_floating_scum',(8.57+rng.uniform(-.07,.07),20.37+j*.19,z+.001),(1,0,0),(0,1,0),(.07,.10),m['mineral'],seed=j)
    return True

def all_dressing(scene,m):
    webs=[]
    for i,p in enumerate([(-1.9,7.5,2.35),(-1.85,14.8,2.1),(1.8,21.5,2.0),(-1.7,29.0,1.9),(1.9,35.8,1.7),(-1.6,37.7,2.0),(8.8,16.8,1.65),(8.5,25.6,1.3)]):
        result=anchored_web(scene,m,p,820+i)
        if result:webs.append(result)
    return {'web_clusters':webs,'rotten_timber':rot_pockets(scene,m),'runoff_strips':runoff(scene,m),'lights':tune_lighting(scene),'dirty_water':sump_water(scene,m)}

def excavation_lamps(scene,m):
    import geometry,json
    emit,p=basic('caged_task_lamp_lens','CC9C55',.8)
    p.inputs['Emission Color'].default_value=rgba('FFD697');p.inputs['Emission Strength'].default_value=1.8
    results=[]
    positions=[('A',2,-8.4,18.8),('A',3,-13,19.2),('B',2,8.5,34.1),('B',3,12.5,34.6),('C',2,-1.2,45),('C',3,2.8,51.4)]
    for sec,stage,x,y in positions:
        before={o.name for o in scene.objects};z=-.025*y
        for a in [0,2.094,4.189]:
            cylinder('Old_task_lamp_leg',(x,y,z+.28),(x+.27*math.cos(a),y+.27*math.sin(a),z+.027),.014,m['iron'])
        cylinder('Old_task_lamp_post',(x,y,z+.20),(x,y,z+1.55),.022,m['iron'])
        box('Old_task_lamp_back',(x,y+.03,z+1.50),(.23,.09,.36),m['iron'],bevel=.01)
        box('Old_task_lamp_lens',(x,y-.020,z+1.50),(.17,.025,.27),emit,bevel=.01)
        for zz in [1.38,1.49,1.60]:cylinder('Old_task_lamp_guard',(x-.105,y-.054,z+zz),(x+.105,y-.054,z+zz),.004,m['iron'])
        ld=bpy.data.lights.new('Q50_Excavation_practical','POINT');ld.energy=58 if stage==2 else 75;ld.color=(1,.59,.27) if sec!='C' else (.45,.66,.76);ld.shadow_soft_size=.16
        ob=bpy.data.objects.new('Q50_Excavation_practical',ld);geometry.COLLECTION.objects.link(ob);ob.location=(x,y-.15,z+1.50)
        meta={'sector':sec,'min_stage':stage,'interaction':'portable_lamp'}
        for o in scene.objects:
            if o.name not in before:o['csm_meta']=json.dumps(meta);o['csm_sector']=sec;o['csm_min_stage']=stage
        results.append({'sector':sec,'minimum_stage':stage,'position':list(ob.location),'watts':ld.energy})
    return results
