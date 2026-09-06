"""Repairs exposed by the complete camera review, not cosmetic concealment."""
import bpy,math,random
from mathutils import Vector,Matrix
from geology_repairs import tree,settle

def continuous_floor(scene):
    """Close grid-mask pinholes at rock/ground junctions; retain the exact sump."""
    o=scene.objects['CSM_Excavated_floor'];old=o.data
    xs=sorted(set([round(-21+i*.30,5) for i in range(141)]+[8.30,10.60]))
    ys=sorted(set([round(.65+i*.30,5) for i in range(198)]+[20.,23.1]))
    vv=[];ff=[]
    for x in xs:
        for y in ys:
            z=-.025*y+(.018*math.sin(2.5*x+.2*y)*math.sin(.6*y) if abs(x)>=1.1 else 0)
            vv.append((x,y,z))
    ny=len(ys)
    for i in range(len(xs)-1):
        for j in range(ny-1):
            x=(xs[i]+xs[i+1])*.5;y=(ys[j]+ys[j+1])*.5
            if 8.30<x<10.60 and 20<y<23.1:continue
            a=i*ny+j;b=(i+1)*ny+j;c=b+1;d=a+1;ff.extend([(a,b,c),(a,c,d)])
    me=bpy.data.meshes.new('Q50_Continuous_floor_exact_sump');me.from_pydata(vv,[],ff);me.update()
    for mat in old.materials:me.materials.append(mat)
    uv=me.uv_layers.new(name='UVMap')
    for loop in me.loops:
        v=me.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(v.x,v.y)
    o.data=me;o['q50_closed_floor_boundary']=True
    for ob in scene.objects:
        if ob.type=='MESH' and ob.get('csm_collision_only') and 'floor' in ob.name.lower():
            ob.data=me.copy();ob['q50_collision_matches_ground']=True
    skin=scene.objects['CSM_Continuous_stratified_mine_skin'];skin.data=skin.data.copy();adjusted=0
    for v in skin.data.vertices:
        x,y,z=v.co;height=z+.025*max(y,0)
        if .60<=y<=37.2 and 1.40<abs(x)<3.30 and height<1.05:
            weight=max(0,min(1,(1.05-height)/.45));target=max(abs(x),2.91)
            if target>abs(x):v.co.x=math.copysign(abs(x)+(target-abs(x))*weight,x);adjusted+=1
    skin.data.update();skin['q50_walkway_geology_clearance_vertices']=adjusted
    return {'geology_foot_clearance_vertices':adjusted,'previous_floor_triangles':len(old.polygons),'new_floor_triangles':len(ff),'sump_aperture_m':[8.30,10.60,20.,23.1],'reason':'CAM_16/23/28 exposed grid-mask floor holes; CAM_09 exposed the cave foot projecting over the walkway.'}

def natural_resources(scene):
    support=tree([scene.objects['CSM_Excavated_floor']]);skin=tree([scene.objects['CSM_Continuous_stratified_mine_skin']]);report=[]
    config={'A':((-3.9,17.8),(-1,0),(0,3.6,7.,12.7)),'B':((3.9,33),(1,0),(0,3.7,7.1,12.4)),'C':((0,39.2),(0,1),(0,4.5,8.8,16.3))}
    for sec,(entry,axis,depths) in config.items():
        ax=Vector((*axis,0));side=Vector((-axis[1],axis[0],0));placed=[]
        for stage in [1,2,3]:
            objects=sorted([o for o in scene.objects if o.type=='MESH' and o.get('csm_sector')==sec and o.get('csm_component')=='mineable_resource' and o.get('csm_min_stage')==stage],key=lambda o:o.name)
            rng=random.Random(8050+ord(sec)*30+stage)
            for j,o in enumerate(objects):
                o.data=o.data.copy()
                for v in o.data.vertices:v.co*=.62
                o.data.update();bpy.context.view_layer.update()
                radius=max(math.hypot(v.co.x,v.co.y) for v in o.data.vertices)*max(o.scale.x,o.scale.y)+.015
                for trial in range(2000):
                    dep=rng.uniform(depths[stage-1]+radius+.2,depths[stage]-radius-.2)
                    u=rng.choice([-1,1])*rng.uniform(.65+radius,1.4+.20*stage-radius)
                    p=Vector((*entry,0))+ax*dep+side*u;p.z=-.025*max(p.y,0)+.32
                    if any(math.hypot(p.x-q.x,p.y-q.y)<radius+r+.028 for q,r in placed):continue
                    near=skin.find_nearest(p)
                    if near[0] is not None and near[3]<radius+.04:continue
                    break
                else:raise RuntimeError('Unable to place nonintersecting resource '+o.name)
                mat=o.matrix_world.copy();mat.translation=p;o.matrix_world=mat;bpy.context.view_layer.update();settle(o,support);placed.append((p,radius))
                report.append({'object':o.name,'radius_m':radius,'world_origin':list(o.matrix_world.translation)})
    for o in scene.objects:
        if o.type=='MESH' and '_Broken_face_toe' in o.name:settle(o,support)
    for sec in 'ABC':
        rocks=[o for o in scene.objects if o.get('q50_fractured_block') and o.get('csm_sector')==sec]
        contact=tree([scene.objects['CSM_Excavated_floor']]+rocks)
        for o in scene.objects:
            if o.type=='MESH' and o.get('csm_sector')==sec and 'Buckled_steel_member' in o.name:settle(o,contact)
    return {'natural_scatter_count':len(report),'reason':'CAM_23/24/28/29 showed unnatural two-row placement. Replaced with seeded collision-spaced scatter and seated contacts.','placements':report}
