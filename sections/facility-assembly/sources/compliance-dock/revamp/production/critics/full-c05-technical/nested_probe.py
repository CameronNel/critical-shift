"""Fresh read-only world-surface measurements of nested manufactured interfaces."""
import bpy,json,math,pathlib,hashlib
from collections import defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=pathlib.Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock/revamp/production/critics/full-c05-technical')
dg=bpy.context.evaluated_depsgraph_get();geo={};trees={}
for o in bpy.context.scene.objects:
    if o.library or o.type!='MESH':continue
    ev=o.evaluated_get(dg);me=ev.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];fs=[list(p.vertices) for p in me.polygons];geo[o.name]=(vs,fs)
    if vs and fs:trees[o.name]=BVHTree.FromPolygons(vs,fs,all_triangles=False)
    ev.to_mesh_clear()
R={'native_sha256':hashlib.sha256(pathlib.Path(bpy.data.filepath).read_bytes()).hexdigest(),'surface_rays':[],'scanner_sleeve_radii':[],'custody_emitter_grid':[],'p2_units':[],'joined_components':{},'raw_selected_geometry':{}}
def ray(label,target,point,direction,offset=.02,length=.1):
    p=Vector(point);di=Vector(direction).normalized();h=trees[target].ray_cast(p-di*offset,di,length)
    r={'label':label,'target':target,'point':list(p),'direction':list(di),'start_offset_m':offset,'hit':h[0] is not None}
    if h[0] is not None:r.update(gap_m=h[3]-offset,hit_point=list(h[0]),normal=list(h[1]))
    R['surface_rays'].append(r);return r
def components(name):
    vs,fs=geo[name];adj=defaultdict(set)
    for f in fs:
        for a,b in zip(f,f[1:]+f[:1]):adj[a].add(b);adj[b].add(a)
    unseen=set(range(len(vs)));result=[]
    while unseen:
        todo=[next(iter(unseen))];ids=set()
        while todo:
            i=todo.pop()
            if i in ids:continue
            ids.add(i);todo.extend(adj[i]-ids)
        unseen-=ids;v=[vs[i] for i in ids]
        result.append({'ids':list(ids),'bounds':{'min':[min(q[k] for q in v) for k in range(3)],'max':[max(q[k] for q in v) for k in range(3)]},'centroid':[sum(q[k] for q in v)/len(v) for k in range(3)],'vertex_count':len(v)})
    R['joined_components'][name]=result;return result
scanner=components('CD | Joined Person Scanner Arch / steel')
for side in [-1,1]:
    column='Scanner portal column '+str(side)
    for j in range(6):
        z=.4+.36*j;pod=f'Sensor emitter {side}_{j}';optic=f'Sensor optic {side}_{j}'
        vv=geo[pod][0];back=max(q.x*side for q in vv)*side
        for yy,zz in [(7,z),(6.96,z),(7.04,z),(7,z-.07),(7,z+.07)]:ray(f'pod_back_{side}_{j}',column,(back,yy,zz),(side,0,0),.008,.05)
        # The optic axis must pass an actual opening, then encounter pod back web.
        ray(f'optic_axis_into_pod_{side}_{j}',pod,(.62*side,7,z),(side,0,0),.015,.08)
        candidates=[c for c in scanner if abs(c['centroid'][0]-.62875*side)<.0001 and abs(c['centroid'][1]-7)<.0001 and abs(c['centroid'][2]-z)<.0001]
        for c in candidates:
            radii=sorted(set(round(math.hypot(geo['CD | Joined Person Scanner Arch / steel'][0][i].y-7,geo['CD | Joined Person Scanner Arch / steel'][0][i].z-z),7) for i in c['ids']))
            optic_r=max(math.hypot(q.y-7,q.z-z) for q in geo[optic][0]);R['scanner_sleeve_radii'].append({'side':side,'index':j,'component_bounds':c['bounds'],'actual_sleeve_radii':radii,'actual_optic_max_radius':optic_r,'radial_clearance_m':min(radii)-optic_r})
    cover='Scanner column inset '+str(side);back=min(q.x*side for q in geo[cover][0])*side
    for yy in [6.91,7,7.09]:
        for zz in [.24,1.35,2.46]:ray('service_cover_back_'+str(side),column,(back,yy,zz),(-side,0,0),.008,.05)
for j in [0,1]:
    screen='Conveyor monitor screen '+str(j);housing='Conveyor monitor housing '+str(j);cy=7.35+j*.6
    for yy,zz in [(cy,1.3),(cy-.163,1.3),(cy+.163,1.3),(cy,1.181),(cy,1.419)]:ray('cargo_screen_back_edge_'+str(j),housing,(3.475,yy,zz),(-1,0,0),.02,.4)
    for yy,zz in [(cy,1.3),(cy-.12,1.3),(cy+.12,1.3),(cy,1.21),(cy,1.39)]:ray('cargo_visible_screen_face_'+str(j),housing,(3.486,yy,zz),(1,0,0),0,.05)
for x,y in [(4.05,6.65),(4.05,8.65),(5.25,6.65),(5.25,8.65)]:ray('cargo_lifting_stem_roof', 'Lead tunnel main body',(x,y,2.15),(0,0,-1))
for y in [6.5,8.8]:
    for x,z in [(3.905,1.3),(5.395,1.3),(4.65,2.15)]:ray('cargo_throat_collar_to_skin','Lead tunnel main body',(x,y,z),(0,1 if y<7 else -1,0),.08,.16)
lamp=bpy.data.objects['CD | Custody transfer practical'];origin=lamp.matrix_world.translation;axis=-(lamp.matrix_world.to_3x3()@Vector((0,0,1)));right=lamp.matrix_world.to_3x3()@Vector((1,0,0));up=lamp.matrix_world.to_3x3()@Vector((0,1,0))
fixture=[n for n in trees if bpy.data.objects[n].get('assembly')=='CD | Custody transfer luminaire']
for x in [-.115,-.0575,0,.0575,.115]:
    for y in [-.045,0,.045]:
        p=origin+right*x+up*y;forward=[];back=[]
        for name in fixture:
            h=trees[name].ray_cast(p,axis,.25)
            if h[0] is not None:forward.append({'name':name,'distance_m':h[3]})
            h=trees[name].ray_cast(p,-axis,.05)
            if h[0] is not None:back.append({'name':name,'distance_m':h[3]})
        R['custody_emitter_grid'].append({'area_offset':[x,y],'origin':list(p),'forward_direction':list(axis),'forward_fixture_blockers':forward,'back_fixture_hits':back})
for name in ['CD | Joined P2 blast leaf west / steel','CD | Joined P2 blast leaf east / steel','CD | Joined P2 blast leaf west / charcoal','CD | Joined P2 blast leaf east / charcoal']:components(name)
for side in [-1,1]:
    leaf='P2 blast leaf '+('west' if side<0 else 'east')
    for xx in [side*.65,side*1.75]:
        unit={'x':xx,'roller_track':ray('p2_roller_track','P2 frame head lintel',(xx,15.94,3.52),(0,0,-1)),'hanger_leaf':ray('p2_hanger_leaf',leaf,(xx,15.86,3.48),(0,0,-1)), 'components':[]}
        for group,cs in R['joined_components'].items():
            if 'P2 blast leaf' not in group:continue
            for c in cs:
                if abs(c['centroid'][0]-xx)<.0001 and c['bounds']['min'][2]>3.47:
                    unit['components'].append({'group':group,**c})
        R['p2_units'].append(unit)
key=components('CD | Joined CD | Office key cabinet / steel')
for x,z in [(-3.13,1.5),(-2.87,1.5),(-3,1.32),(-3,1.68)]:ray('key_glazing_rear_ledge','CD | Joined CD | Office key cabinet / steel',(x,9.475,z),(0,1,0))
for x in [-3.075,-3,-2.925]:ray('key_hook_rear_web','Office key box cabinet',(x,9.514,1.55),(0,1,0),.01,.05)
R['g1_leaves']=[]
for j in [1,2,3]:
    panel=f'G1 leaf {j} panel';obj=bpy.data.objects[panel];loc=obj.matrix_world.translation;vs=geo[panel][0];front=min(v.y for v in vs);back=max(v.y for v in vs)
    r={'leaf':j,'panel_bounds':{'front_y':front,'rear_y':back},'panel_materials':[m.name for m in obj.data.materials],'joined_groups':[],'bays':[],'fixings':[]}
    for name in [n for n in geo if n.startswith(f'CD | Joined G1 leaf {j} panel /')]:
        cs=components(name);r['joined_groups'].append({'name':name,'materials':[m.name for m in bpy.data.objects[name].data.materials]})
        for c in cs:
            b=c['bounds'];dx=b['max'][0]-b['min'][0];dy=b['max'][1]-b['min'][1];dz=b['max'][2]-b['min'][2]
            if .47<dx<.51 and .44<dz<.48:
                z=c['centroid'][2];bay={'component':c,'group':name,'front_offset_from_panel_m':front-b['min'][1],'back_gap_to_panel_m':front-b['max'][1],'sample_back_to_panel':ray('G1_bay_back_to_panel_'+str(j),panel,(loc.x,b['max'][1],z),(0,1,0),.008,.03)}
                vv,ff=geo[name];ids=set(c['ids']);tri_volume=0;normals=[]
                for f in ff:
                    if not set(f)<=ids:continue
                    for k in range(1,len(f)-1):tri_volume+=vv[f[0]].dot(vv[f[k]].cross(vv[f[k+1]]))/6
                    if all(abs(vv[i].y-b['min'][1])<1e-5 for i in f):normals.append(list((vv[f[1]]-vv[f[0]]).cross(vv[f[2]]-vv[f[0]]).normalized()))
                bay['signed_component_volume_m3']=tri_volume;bay['front_face_normals']=normals;r['bays'].append(bay)
            if dx<.011 and dz<.011 and dy<.011:
                z=c['centroid'][2]
                if abs(abs(c['centroid'][0]-loc.x)-.21)<.002:
                    r['fixings'].append({'component':c,'screw_back_to_bay_front_m':b['max'][1]-(front-.005)})
    R['g1_leaves'].append(r)
for name in [n for n in geo if n.startswith(('Sensor emitter','Sensor optic','Scanner portal column','Scanner column inset','Conveyor monitor','G1 leaf','CD | Joined G1 leaf'))]+['P2 frame head lintel','CD | Open inspection luminaire.001','CD | Inspection frosted aperture.001','CD | Joined P2 blast leaf west / steel','CD | Joined P2 blast leaf east / steel','CD | Joined P2 blast leaf west / charcoal','CD | Joined P2 blast leaf east /charcoal','CD | Joined Person Scanner Arch / steel','CD | Joined CD | Office key cabinet / steel']:
    if name not in geo:continue
    vs,fs=geo[name];R['raw_selected_geometry'][name]={'vertices':[list(v) for v in vs],'faces':fs}
(OUT/'nested-probe.json').write_text(json.dumps(R,indent=2));print('NESTED_PROBE_DONE',len(R['surface_rays']),len(R['custody_emitter_grid']),len(R['p2_units']),flush=True)
