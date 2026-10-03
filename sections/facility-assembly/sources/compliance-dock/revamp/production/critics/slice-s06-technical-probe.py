"""Independent read-only s06 witness; writes JSON only, never saves .blend."""
import bpy, bmesh, json, hashlib, math
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
REPO=ROOT.parents[3]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SOURCE=ROOT/'module_overhaul_R1.blend'
BASE=ROOT/'module.blend'
EXPECTED='a78d03bb5822ce0133cac551ee6e81151e8d7643a9b66050c2c1f9940561e34f'
R={'source_sha256_before':sha(SOURCE),'source_sha256_expected':EXPECTED,'never_saves_blend':True,'limits':['Static rendered-mesh tests cannot establish load capacity, engine collision/navigation or runtime performance.','Surface distances, support rays and actual bearing triangles are separate from ancestry.','Coplanar testing targets local slice positive-area surfaces; this is not a complete general self-intersection proof.']}
assert R['source_sha256_before']==EXPECTED

def bounds(vs):
    return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]] if vs else None
def snapshot(scene):
    dg=bpy.context.evaluated_depsgraph_get();out={}
    for o in scene.objects:
        e={'matrix':[list(r) for r in o.matrix_world],'dimensions':list(o.dimensions),'type':o.type,'architectural':o.get('support_class')=='architectural','parent':o.parent.name if o.parent else None}
        if o.type=='MESH':
            eo=o.evaluated_get(dg);me=eo.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];e['bounds']=bounds(vs)
            e['world_vertex_sha256_1um']=hashlib.sha256(json.dumps(sorted(tuple(round(float(x),6) for x in v) for v in vs)).encode()).hexdigest()
            if o.name.startswith('Office front') or o.name=='Hatch wall sill base':
                me.calc_loop_triangles();e['world_vertices']=[list(v) for v in vs];e['triangles']=[list(t.vertices) for t in me.loop_triangles]
            eo.to_mesh_clear()
        out[o.name]=e
    return out

bpy.ops.wm.open_mainfile(filepath=str(BASE),load_ui=False)
baseline=snapshot(bpy.context.scene)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False)
S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=S
dg=bpy.context.evaluated_depsgraph_get()
current=snapshot(S)
R['stage']=S.get('stage');R['revision']=S.get('revision');R['scene']=S.name
R['retained_matrices']={'count':len(baseline),'missing':[n for n in baseline if n not in current],'changed':[]}
R['dimension_changes']=[]
R['inherited_mesh_world_vertex_cloud_changes']=[]
for n,old in baseline.items():
    if n not in current:continue
    new=current[n];delta=max(abs(old['matrix'][i][j]-new['matrix'][i][j]) for i in range(4) for j in range(4))
    if delta>1e-7:R['retained_matrices']['changed'].append({'name':n,'max_delta':delta})
    if max(abs(old['dimensions'][i]-new['dimensions'][i]) for i in range(3))>1e-6:
        R['dimension_changes'].append({'name':n,'baseline_dimensions':old['dimensions'],'current_dimensions':new['dimensions'],'architectural':old['architectural'],'baseline_bounds':old.get('bounds'),'current_bounds':new.get('bounds')})
    if old['type']=='MESH' and old.get('world_vertex_sha256_1um')!=new.get('world_vertex_sha256_1um'):R['inherited_mesh_world_vertex_cloud_changes'].append(n)
R['protected_hashes']=[{'path':p,'expected':h,'actual':sha(REPO/p),'unchanged':sha(REPO/p)==h} for p,h in json.loads((ROOT/'revamp/production/protected-inputs.json').read_text()).items()]
R['dependencies']={'libraries':[{'path':l.filepath,'resolved':bpy.path.abspath(l.filepath),'exists':Path(bpy.path.abspath(l.filepath)).is_file()} for l in bpy.data.libraries],'editable_objects_linked':[o.name for o in S.objects if o.library or (o.data and o.data.library)],'fonts':[{'name':f.name,'path':f.filepath,'packed':bool(f.packed_file),'exists':f.filepath=='<builtin>' or Path(bpy.path.abspath(f.filepath,library=f.library)).is_file()} for f in bpy.data.fonts],'scene_object_count':len(S.objects),'scene_names':[s.name for s in bpy.data.scenes],'local_material_uv_nodes':[{'material':m.name,'uv_maps':[n.uv_map for n in m.node_tree.nodes if n.type=='UVMAP'],'images':[n.image.name if n.image else None for n in m.node_tree.nodes if n.type=='TEX_IMAGE']} for m in bpy.data.materials if m.name.startswith('CD |') and m.node_tree]}

class Shape:
    def __init__(self,o):
        eo=o.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles()
        self.o=o;self.v=[o.matrix_world@v.co for v in me.vertices];self.tri=[tuple(t.vertices) for t in me.loop_triangles]
        self.norm=[(self.v[t[1]]-self.v[t[0]]).cross(self.v[t[2]]-self.v[t[0]]).normalized() for t in self.tri]
        self.b=bounds(self.v);self.bvh=BVHTree.FromPolygons(self.v,self.tri,all_triangles=True,epsilon=1e-8)
        eo.to_mesh_clear()
    def ray(self,p,d,maxd=1):
        h=self.bvh.ray_cast(Vector(p),Vector(d),maxd)
        return None if h[0] is None else {'point':list(h[0]),'normal':list(self.norm[h[2]]),'distance':h[3],'triangle':h[2]}

local=[o for o in S.objects if o.type=='MESH' and (o.get('overhaul_surface') or o.name.startswith('CD |'))]
shapes={o.name:Shape(o) for o in S.objects if o.type in {'MESH','CURVE'} and (o in local or o.parent and o.parent.name=='Checkin Counter Hatch' or o.name in ['Floor slab','Office front wall mid','Office front wall east','Office front head lintel'])}
R['local_inventory']=[{'name':o.name,'parent':o.parent.name if o.parent else None,'bounds':current[o.name].get('bounds'),'scale':list(o.scale),'modifiers':[(m.name,m.type) for m in o.modifiers]} for o in local]
R['counter_inventory']=[{'name':o.name,'bounds':current[o.name].get('bounds'),'type':o.type} for o in S.objects if o.parent and o.parent.name=='Checkin Counter Hatch']
R['topology']=[];R['uv']=[]
for o in local:
    bm=bmesh.new();bm.from_mesh(o.data);bm.normal_update()
    bad_edges=sum(not e.is_manifold for e in bm.edges)
    inconsistent=sum(e.is_manifold and not e.is_contiguous for e in bm.edges)
    zero=sum(f.calc_area()<1e-12 for f in bm.faces)
    vol=bm.calc_volume(signed=True)
    R['topology'].append({'name':o.name,'verts':len(bm.verts),'faces':len(bm.faces),'nonmanifold_edges':bad_edges,'inconsistent_winding_edges':inconsistent,'degenerate_faces':zero,'degenerate_total_area_m2':sum(f.calc_area() for f in bm.faces if f.calc_area()<1e-12),'zero_normal_faces':sum(f.normal.length<.5 for f in bm.faces),'signed_volume_m3':vol})
    bm.free()
    layer=o.data.uv_layers.get('CD_Physical_1m')
    u={'name':o.name,'layer':layer.name if layer else None,'faces':len(o.data.polygons),'bad_edges':0,'max_relative_edge_error':0,'max_relative_area_error':0,'max_absolute_edge_error_m':0,'max_relative_edge_error_above_10um':0,'significant_errors':[],'degenerate_uv_faces':0,'nonfinite':0,'bevel_or_slope_faces':0,'worst_face':None}
    if layer:
        for f in o.data.polygons:
            ps=[o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co for li in f.loop_indices]
            us=[layer.data[li].uv.copy() for li in f.loop_indices]
            if any(not math.isfinite(x) for uv in us for x in uv):u['nonfinite']+=1
            errs=[]
            for i in range(len(ps)):
                w=(ps[(i+1)%len(ps)]-ps[i]).length;t=(us[(i+1)%len(us)]-us[i]).length
                if w>1e-8:
                    err=abs(t/w-1);errs.append(err)
                    u['max_absolute_edge_error_m']=max(u['max_absolute_edge_error_m'],abs(t-w))
                    if w>1e-5:u['max_relative_edge_error_above_10um']=max(u['max_relative_edge_error_above_10um'],err)
                    if err>.005 and w>1e-5:u['significant_errors'].append({'face':f.index,'edge':i,'world_length_m':w,'uv_length_m':t,'relative_error':err,'absolute_error_m':abs(t-w)})
                    if err>1e-4:u['bad_edges']+=1
            worst=max(errs,default=0)
            if worst>u['max_relative_edge_error']:u['max_relative_edge_error']=worst;u['worst_face']=f.index
            uvarea=abs(sum(us[i].x*us[(i+1)%len(us)].y-us[(i+1)%len(us)].x*us[i].y for i in range(len(us)))*.5)
            worldarea=sum((ps[i]-ps[0]).cross(ps[i+1]-ps[0]).length*.5 for i in range(1,len(ps)-1))
            if uvarea<1e-12 and worldarea>1e-10:u['degenerate_uv_faces']+=1
            if worldarea>1e-10:u['max_relative_area_error']=max(u['max_relative_area_error'],abs(uvarea/worldarea-1))
            if sum(abs(v)>1e-5 for v in f.normal)>1:u['bevel_or_slope_faces']+=1
    R['uv'].append(u)

R['support_roots']=[{'name':o.name,'target':o.get('support_target'),'direction':list(o.get('support_direction',[])),'anchor_names':[c.name for c in o.children if c.get('contact_anchor')]} for o in S.objects if o.get('support_class')=='supported_assembly' and (o.name.startswith('CD |') or o.name in ['Checkin Counter Hatch','D1 Staff Front Door'])]

# Actual paired surface rays: neither bounding-box overlap nor ancestry is used
# to establish the point-to-point bearing measurements below.
R['physical_contacts']=[]
def contact(label,a,b,point,direction):
    direction=Vector(direction).normalized();point=Vector(point)
    ha=shapes[a].ray(point+direction*.02,-direction,.04)
    hb=shapes[b].ray(point-direction*.02,direction,.04)
    row={'label':label,'object':a,'support':b,'nominal_contact_point':list(point),'direction':list(direction),'object_hit':ha,'support_hit':hb}
    if ha and hb:
        row['signed_gap_m']=(Vector(hb['point'])-Vector(ha['point'])).dot(direction)
        row['support_normal_error_deg']=math.degrees(math.acos(max(-1,min(1,-Vector(hb['normal']).dot(direction)))))
    R['physical_contacts'].append(row)

for suffix,x in [('',-3.715),('.001',-3.305)]:
    contact('glass to clamp'+suffix,'Hatch speaking aperture plate','CD | Speaking glazing clamp'+suffix,(x,3.5925,1.4),(0,-1,0))
    contact('clamp to stanchion'+suffix,'CD | Speaking glazing clamp'+suffix,'CD | Speaking load-bearing stanchion'+suffix,(x,3.592,1.4),(0,1,0))
    contact('stanchion to foot'+suffix,'CD | Speaking load-bearing stanchion'+suffix,'CD | Speaking stanchion foot'+suffix,(x,3.599,1.048),(0,0,-1))
    contact('foot to linoleum'+suffix,'CD | Speaking stanchion foot'+suffix,'CD | Counter linoleum inset',(x,3.599,1.042),(0,0,-1))
contact('grille to isolation pad','Speaking baffle ring','CD | Speaking grille isolation pad',(-3.51,3.5855,1.4),(0,1,0))
contact('isolation pad to glass','CD | Speaking grille isolation pad','Hatch speaking aperture plate',(-3.51,3.5925,1.4),(0,1,0))
for a,point in [('Authority stamp rubber base',(-2.95,3.42,1.042)),('Ink pad tin base',(-2.8,3.42,1.042)),('Counter pen holder base',(-3.78,3.46,1.042)),('Counter clipboard board',(-3.35,3.4,1.042)),('CD | Counter docket tray',(-4.045,3.6,1.042)),('CD | Rejected docket',(-3,3.75,1.042))]:
    contact('tabletop bearing',a,'CD | Counter linoleum inset',point,(0,0,-1))
contact('manifest to clipboard','Counter manifest paper','Counter clipboard board',(-3.35,3.4,1.051),(0,0,-1))
contact('linoleum to worktop','CD | Counter linoleum inset','Transaction counter slab',(-3.51,3.8,1.04),(0,0,-1))
for suffix,x,leg in [('',-4.25,'Hatch counter leg west'),('.001',-2.75,'Hatch counter leg east')]:
    contact('worktop to leg'+suffix,'Transaction counter slab',leg,(x,3.6,1),(0,0,-1))
    contact('leg to floor'+suffix,leg,'Floor slab',(x,3.6,0),(0,0,-1))
for a,b,point in [('Authority stamp brass collar','Authority stamp rubber base',(-2.95,3.42,1.074)),('Authority stamp ferrule','Authority stamp brass collar',(-2.95,3.42,1.086)),('Authority stamp wood shaft','Authority stamp ferrule',(-2.95,3.42,1.098)),('Authority stamp wood knob','Authority stamp wood shaft',(-2.95,3.42,1.17)),('Ink pad felt cushion','Ink pad tin base',(-2.8,3.42,1.07)),('Counter pen swivel ball','Counter pen holder base',(-3.78,3.46,1.078))]:
    contact('small item internal mating',a,b,point,(0,0,-1))
contact('plaque back to wall','CD | Plaque wall back','Office front head lintel',(-3.51,3.52,2.7),(0,1,0))
for suffix,x in [('',-3.72),('.001',-3.3)]:
    contact('light bracket to wall'+suffix,'CD | Task wall bracket'+suffix,'Office front head lintel',(x,3.52,2.43),(0,1,0))
contact('junction back to wall','CD | D1 service mounting back','Office front wall mid',(-4.6125,3.52,2),(0,1,0))

# Cloth bearing is measured from each actual underside triangle and a denser
# XY ray grid. Its overhanging front edge bears within tolerance on steel.
cloth=shapes['CD | Used cotton wipe'];liner=shapes['CD | Counter linoleum inset'];top=shapes['Transaction counter slab']
clothrows=[];area_exact=0;area_tolerance=0;area_projected=0
for i,t in enumerate(cloth.tri):
    n=cloth.norm[i]
    if n.z>-.1:continue
    ps=[cloth.v[j] for j in t];p=sum(ps,Vector())/3
    h=liner.ray(p+Vector((0,0,.025)),(0,0,-1),.08);target=liner.o.name
    if h is None:h=top.ray(p+Vector((0,0,.025)),(0,0,-1),.08);target=top.o.name
    gap=p.z-h['point'][2] if h else None
    area=abs((ps[1]-ps[0]).cross(ps[2]-ps[0]).z)*.5;area_projected+=area
    if gap is not None and abs(gap)<1e-6:area_exact+=area
    if gap is not None and -.002<=gap<=.005:area_tolerance+=area
    clothrows.append({'triangle':i,'centroid':list(p),'target':target if h else None,'gap_m':gap,'projected_area_m2':area})
R['cloth_bearing']={'underside_projected_area_m2':area_projected,'centroid_exact_contact_area_m2':area_exact,'centroid_within_5mm_contact_area_m2':area_tolerance,'triangle_samples':clothrows,'boundary_contacts':[]}
R['cloth_bearing']['maximum_underside_centroid_gap_m']=max(r['gap_m'] for r in clothrows if r['gap_m'] is not None)
for p in [(-4.2,3.35,1.042),(-4.2,3.40,1.042),(-4.02,3.35,1.042),(-4.02,3.44,1.042),(-4.20,3.30,1.042),(-4.11,3.30,1.042)]:
    h=liner.ray(Vector(p)+Vector((0,0,.02)),(0,0,-1),.08);target=liner.o.name
    if h is None:h=top.ray(Vector(p)+Vector((0,0,.02)),(0,0,-1),.08);target=top.o.name
    near=cloth.bvh.find_nearest(Vector(p))
    R['cloth_bearing']['boundary_contacts'].append({'point':p,'target':target,'support_hit':h,'nearest_actual_cloth_point':list(near[0]),'distance_to_cloth_m':near[3],'signed_gap_m':near[0].z-h['point'][2] if h else None})

# Compare the architectural union across every front-wall X/Z partition cell.
front={n:e for n,e in baseline.items() if e.get('world_vertices')}
frontnow={n:current[n] for n in front}
def front_bvhs(records):
    return {n:BVHTree.FromPolygons([Vector(v) for v in e['world_vertices']],e['triangles'],all_triangles=True,epsilon=1e-8) for n,e in records.items()}
fb=front_bvhs(front);fn=front_bvhs(frontnow)
xs=sorted(set(round(v[0],5) for e in list(front.values())+list(frontnow.values()) for v in e['world_vertices']))
zs=sorted(set(round(v[2],5) for e in list(front.values())+list(frontnow.values()) for v in e['world_vertices']))
xs=[(a+b)/2 for a,b in zip(xs,xs[1:]) if b-a>2e-5];zs=[(a+b)/2 for a,b in zip(zs,zs[1:]) if b-a>2e-5]
changes=[];count=0
for x in xs:
    for z in zs:
        vals=[]
        for group in [fb,fn]:
            hits=[t.ray_cast(Vector((x,3,z)),Vector((0,1,0)),1.5)[0] for t in group.values()]
            vals.append(min((p.y for p in hits if p is not None),default=None))
        count+=1
        if (vals[0] is None)!=(vals[1] is None) or vals[0] is not None and abs(vals[0]-vals[1])>1e-5:changes.append({'x':x,'z':z,'baseline_front_y':vals[0],'current_front_y':vals[1]})
R['architectural_preservation']={'front_wall_partition_samples':count,'front_union_changes_above_10um':changes,'unchanged_architecture_vertex_cloud_mismatches':[n for n,e in baseline.items() if e['architectural'] and n not in ['Office front wall mid','Office front wall east'] and e.get('world_vertex_sha256_1um')!=current[n].get('world_vertex_sha256_1um')],'combined_architecture_baseline_bounds':bounds([Vector(v) for e in baseline.values() if e['architectural'] and e.get('bounds') for v in e['bounds']]),'combined_architecture_current_bounds':bounds([Vector(v) for e in current.values() if e['architectural'] and e.get('bounds') for v in e['bounds']])}
R['architectural_preservation']['nominal_front_occupancy_changes']=[]
R['architectural_preservation']['nominal_front_occupancy_samples']=0
def front_interval(records,x,z):
    intervals=[]
    for e in records.values():
        lo,hi=e['bounds']
        if lo[0]<x<hi[0] and lo[2]<z<hi[2]:intervals.append((lo[1],hi[1]))
    if not intervals:return None
    return (min(a for a,b in intervals),max(b for a,b in intervals))
for x in [-6.6,-6.2,-5.95,-5.8,-5.4,-5,-4.85,-4.6,-4.4,-4.3,-4,-3.5,-3,-2.7,-2.6,-2.45]:
    for z in [.02,.5,1,1.06,1.5,2.19,2.24,2.31,2.34,2.36,2.5,2.9,3.04]:
        old,new=front_interval(front,x,z),front_interval(frontnow,x,z)
        R['architectural_preservation']['nominal_front_occupancy_samples']+=1
        if old!=new:R['architectural_preservation']['nominal_front_occupancy_changes'].append({'x':x,'z':z,'baseline':old,'current':new})
R['architectural_preservation']['ray_partition_limit']='Thin bevel strips and nearly tangent long triangles can produce unstable ray hits. Raw changes are retained; nominal solid partitions and per-object bounds/clouds independently establish preserved aperture/envelope, not literal identical bevel profile at the two repaired pier/lintel seams.'

# Explicit positive-area coincident face test, including partial overlaps.
# Only axis-planar surfaces are grouped; bevels are separately checked by UV,
# winding and normals and are not silently described as fully intersection-free.
groups=defaultdict(list)
for name,s in shapes.items():
    for i,t in enumerate(s.tri):
        n=s.norm[i];axis=max(range(3),key=lambda a:abs(n[a]))
        ps=[s.v[j] for j in t]
        if abs(n[axis])<.999999 or max(p[axis] for p in ps)-min(p[axis] for p in ps)>1e-6:continue
        axes=[a for a in range(3) if a!=axis];poly=[(float(p[axes[0]]),float(p[axes[1]])) for p in ps]
        groups[(axis,round(sum(p[axis] for p in ps)/3,5),1 if n[axis]>0 else -1)].append((name,i,poly))
def area(poly):return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1])))*.5 if len(poly)>2 else 0
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def clip(subject,cutter):
    if cross(*cutter)<0:cutter=list(reversed(cutter))
    out=subject
    for a,b in zip(cutter,cutter[1:]+cutter[:1]):
        inp=out;out=[]
        if not inp:break
        for p,q in zip(inp,inp[1:]+inp[:1]):
            dp=cross(a,b,p);dq=cross(a,b,q)
            if dp>=-1e-12:out.append(p)
            if (dp>=0)!=(dq>=0):
                t=dp/(dp-dq);out.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
    return out
coplanar=defaultdict(lambda:{'overlap_area_m2':0,'examples':[]})
for plane,rows in groups.items():
    for a in range(len(rows)):
        an,ai,ap=rows[a]
        for bn,bi,bp in rows[a+1:]:
            if an==bn:continue
            if max(p[0] for p in ap)<min(p[0] for p in bp) or max(p[0] for p in bp)<min(p[0] for p in ap) or max(p[1] for p in ap)<min(p[1] for p in bp) or max(p[1] for p in bp)<min(p[1] for p in ap):continue
            aa=area(clip(ap,bp))
            if aa<1e-8:continue
            key=tuple(sorted([an,bn]));row=coplanar[key];row['overlap_area_m2']+=aa
            if len(row['examples'])<4:row['examples'].append({'plane':plane,'triangles':[ai,bi],'area_m2':aa})
R['partial_coplanar_same_facing']=[{'objects':list(k),**v} for k,v in coplanar.items()]
# Sample exposed overlapping jamb/wainscot at both ends of the door, away from
# bevels. Both independently return the same outward-facing Y plane.
R['exposed_door_surface_witness']=[]
for jamb,skin,x in [('D1 frame jamb -1','Office front wainscot west',-5.97),('D1 frame jamb 1','Office front wainscot mid',-4.83)]:
    for z in [.2,.5,.9]:
        p=Vector((x,3.3,z));hs={name:shapes[name].ray(p,(0,1,0),.5) for name in [jamb,skin]}
        closest=[]
        for n,s in shapes.items():
            h=s.ray(p,(0,1,0),.5)
            if h:closest.append((h['distance'],n))
        R['exposed_door_surface_witness'].append({'world_origin':list(p),'hits':hs,'first_surfaces':sorted(closest)[:4]})
R['source_sha256_after']=sha(SOURCE)
(HERE/'slice-s06-technical-probe.json').write_text(json.dumps(R,indent=2)+'\n')
print('WITNESS_WRITTEN',HERE/'slice-s06-technical-probe.json')
print('LOCAL',len(local),'DIMENSION_CHANGES',[(r['name'],r['current_dimensions']) for r in R['dimension_changes']])
