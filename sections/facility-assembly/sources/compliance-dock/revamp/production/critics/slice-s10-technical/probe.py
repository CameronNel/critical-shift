"""Read-only independent s10 technical witness sampling. Never saves a blend."""
import bpy, bmesh, json, math, hashlib, importlib.util
from pathlib import Path
from collections import Counter, defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
REPO = ROOT.parents[3]
SOURCE = ROOT/'module_overhaul_R1.blend'
EXPECTED = 'f817b83c4d0bcf1dec88e6f3b7bf39ddc9100da66e74a1a1c5015ebbe52c5265'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def xyz(v): return [float(c) for c in v]
def safe(v):
    if isinstance(v, Vector): return xyz(v)
    if isinstance(v, dict): return {k:safe(x) for k,x in v.items()}
    if isinstance(v, (list,tuple)): return [safe(x) for x in v]
    return v

class Geometry:
    def __init__(self,o,dg):
        self.name=o.name;self.type=o.type;self.matrix=[list(r) for r in o.matrix_world]
        e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles()
        self.vertices=[o.matrix_world@v.co for v in m.vertices]
        self.tris=[tuple(t.vertices) for t in m.loop_triangles]
        self.polyindices=[t.polygon_index for t in m.loop_triangles]
        self.bounds=([min(v[i] for v in self.vertices) for i in range(3)], [max(v[i] for v in self.vertices) for i in range(3)])
        self.normals=[];self.areas=[];self.polys=[];self.zero=0;self.edges=Counter();self.edge_winding=Counter()
        for tr in self.tris:
            a,b,c=(self.vertices[i] for i in tr);cross=(b-a).cross(c-a);self.areas.append(cross.length*.5)
            self.normals.append(cross.normalized() if cross.length else Vector((0,0,0)))
            if cross.length==0:self.zero+=1
            for x,y in zip(tr,tr[1:]+tr[:1]):
                self.edges[tuple(sorted((x,y)))]+=1;self.edge_winding[tuple(sorted((x,y)))]+=1 if x<y else -1
        self.closed=all(n==2 for n in self.edges.values())
        self.boundaries=sum(n==1 for n in self.edges.values());self.multiface=sum(n>2 for n in self.edges.values())
        self.inconsistent_winding=sum(self.edge_winding[k]!=0 for k,n in self.edges.items() if n==2)
        origin=Vector([(self.bounds[0][i]+self.bounds[1][i])*.5 for i in range(3)])
        self.volume=sum((self.vertices[a]-origin).dot((self.vertices[b]-origin).cross(self.vertices[c]-origin))/6 for a,b,c in self.tris)
        self.polygons=len(m.polygons)
        for p in m.polygons:
            v=[self.vertices[i] for i in p.vertices]
            self.polys.append({'verts':v,'normal':(o.matrix_world.to_3x3().inverted().transposed()@p.normal).normalized(),'index':p.index})
        self.materials=[x.name if x else None for x in m.materials]
        self.submeshes=len(set(p.material_index for p in m.polygons))
        self.uv=None
        if o.get('overhaul_surface') or any(x and x.name.startswith('CD |') for x in m.materials):
            uv=m.uv_layers.get('CD_Physical_1m');fail=[];ratios=[];arearatios=[];cats=Counter();short=[]
            for t in m.loop_triangles:
                p=[self.vertices[i] for i in t.vertices]
                n=(p[1]-p[0]).cross(p[2]-p[0]).normalized()
                cat='axis_plane' if max(abs(c) for c in n)>.99999 else 'sloped_or_bevel'
                cats[cat]+=1
                if not uv:continue
                q=[uv.data[i].uv.copy() for i in t.loops]
                ar=abs((q[1].x-q[0].x)*(q[2].y-q[0].y)-(q[1].y-q[0].y)*(q[2].x-q[0].x))*.5
                area=(p[1]-p[0]).cross(p[2]-p[0]).length*.5
                if area>1e-12:arearatios.append(ar/area)
                for i in range(3):
                    length=(p[(i+1)%3]-p[i]).length
                    if length<=1e-10:continue
                    ratio=(q[(i+1)%3]-q[i]).length/length
                    if length>.0001:ratios.append(ratio)
                    if abs(ratio-1)>.01 and length>.0001 and len(fail)<8:fail.append({'triangle':t.index,'edge_m':length,'uv_per_m':ratio,'category':cat})
                    if not all(math.isfinite(c) for c in q[i]):fail.append({'triangle':t.index,'nonfinite':True})
            consumed=[];active_materials=set(p.material_index for p in m.polygons)
            if o.type=='FONT':active_materials=set(range(len(m.materials)))
            for mi in active_materials:
                if mi>=len(m.materials) or not m.materials[mi] or not m.materials[mi].use_nodes:continue
                mat=m.materials[mi];visited=set()
                def walk(node):
                    if node in visited:return
                    visited.add(node)
                    for inp in node.inputs:
                        for link in inp.links:walk(link.from_node)
                for node in mat.node_tree.nodes:
                    if node.type=='OUTPUT_MATERIAL' and node.is_active_output:walk(node)
                for node in visited:
                    if node.type=='UVMAP':consumed.append({'material':mat.name,'source':'UVMAP','layer':node.uv_map,'present':node.uv_map in m.uv_layers})
                    if node.type=='TEX_COORD':
                        for socket in node.outputs:
                            if socket.is_linked:consumed.append({'material':mat.name,'source':'TEX_COORD','socket':socket.name,'mapping_contract':mat.get('mapping_contract')})
            self.uv={'layers':[x.name for x in m.uv_layers],'consumer_paths_to_active_output':consumed,'triangle_categories':dict(cats),'edge_ratio_range':([min(ratios),max(ratios)] if ratios else None),'area_ratio_range':([min(arearatios),max(arearatios)] if arearatios else None),'failures':fail}
        e.to_mesh_clear()
        self.bvh=BVHTree.FromPolygons(self.vertices,self.tris,all_triangles=True,epsilon=0)
    def ray(self,p,d,maxdist=100):
        q,n,tri,dist=self.bvh.ray_cast(Vector(p),Vector(d).normalized(),maxdist)
        return {'point':q,'normal':self.normals[tri],'triangle':tri,'distance':dist,'object':self.name} if q is not None else None
    def summary(self):
        return {'object':self.name,'type':self.type,'bounds':self.bounds,'triangles':len(self.tris),'polygons':self.polygons,'closed':self.closed,'boundary_edges':self.boundaries,'multiface_edges':self.multiface,'inconsistent_winding_edges':self.inconsistent_winding,'zero_area':self.zero,'signed_volume_m3':self.volume,'uv':self.uv}

def collect(scene, predicate=lambda o:True):
    dg=bpy.context.evaluated_depsgraph_get()
    return {o.name:Geometry(o,dg) for o in scene.objects if o.type in {'MESH','CURVE','FONT'} and predicate(o)}

assert sha(SOURCE)==EXPECTED
protected=json.loads((ROOT/'revamp/production/protected-inputs.json').read_text())
protected_rows=[{'path':p,'expected':v,'actual':sha(REPO/p),'pass':sha(REPO/p)==v} for p,v in protected.items()]
baseline=json.loads((ROOT/'revamp/production/baseline.json').read_text())

# Baseline is loaded natively, never saved. Captured numeric arrays survive reopen.
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'module.blend'),load_ui=False)
BS=bpy.context.scene
base_matrices={o.name:[list(r) for r in o.matrix_world] for o in BS.objects}
def structure(o):return o.get('support_class')=='architectural' or o.name.startswith('D1 frame') or o.name.startswith('Hatch counter leg')
BG=collect(BS,structure)
base_geom_hash={n:hashlib.sha256(json.dumps({'vertices':[xyz(v) for v in g.vertices],'triangles':g.tris}).encode()).hexdigest() for n,g in BG.items()}

bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False)
S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=S
G=collect(S)
matrices=[]
for name,m in base_matrices.items():
    o=S.objects.get(name)
    delta=max(abs(o.matrix_world[i][j]-m[i][j]) for i in range(4) for j in range(4)) if o else None
    matrices.append({'object':name,'max_delta':delta,'pass':delta==0})
arch=[]
for n,g in BG.items():
    current=G[n];h=hashlib.sha256(json.dumps({'vertices':[xyz(v) for v in current.vertices],'triangles':current.tris}).encode()).hexdigest()
    arch.append({'object':n,'geometry_identical':h==base_geom_hash[n]})

# Surface-to-surface signed separation using actual intersections, not boxes.
bearings=[]
def bearing(child,target,at,d,label=None):
    at=Vector(at);d=Vector(d).normalized();cg=G[child];tg=G[target]
    # At must lie well inside the intended contact patch; opposite rays find
    # each actual surface from clear free space. Negative = actual engagement.
    cr=cg.ray(at+d*.05,-d,.10);tr=tg.ray(at-d*.05,d,.10)
    gap=(tr['point']-cr['point']).dot(d) if cr and tr else None
    row={'label':label or child+' -> '+target,'child':child,'target':target,'sample':at,'direction':d,'child_hit':cr,'target_hit':tr,'signed_separation_m':gap}
    bearings.append(row);return row
for x,suffix in [(-3.715,''),(-3.305,'.001')]:
    bearing('CD | Speaking stanchion foot'+suffix,'CD | Counter linoleum inset',(x,3.599,1.043),(0,0,-1),'stanchion foot on liner')
    bearing('CD | Speaking load-bearing stanchion'+suffix,'CD | Speaking stanchion foot'+suffix,(x,3.599,1.048),(0,0,-1),'upright on foot')
    bearing('CD | Speaking glazing clamp'+suffix,'CD | Speaking load-bearing stanchion'+suffix,(x,3.595,1.4),(0,1,0),'clamp engagement in upright')
    bearing('Hatch speaking aperture plate','CD | Speaking glazing clamp'+suffix,(x,3.595,1.4),(0,-1,0),'glazing side seated in clamp')
for x,n in [(-4.25,'Hatch counter leg west'),(-2.75,'Hatch counter leg east')]:
    bearing('Transaction counter slab',n,(x,3.6,1),(0,0,-1),'worktop on steel post')
    bearing(n,'Floor slab',(x,3.6,0),(0,0,-1),'steel post on floor')
    # Infill boundary is a real opposed butt surface, tested at both post sides.
    for side in [-1,1]:bearing('Hatch wall sill base',n,(x+side*.04,3.6,.5),(-side,0,0),'infill butt against post')
bearing('CD | Counter linoleum inset','Transaction counter slab',(-3.51,3.7,1.04),(0,0,-1))
bearing('CD | Molded stamping pad','CD | Counter linoleum inset',(-2.915,3.43,1.042),(0,0,-1))
bearing('Authority stamp rubber base','CD | Molded stamping pad',(-2.95,3.42,1.048),(0,0,-1))
bearing('Ink pad tin base','CD | Molded stamping pad',(-2.8,3.42,1.048),(0,0,-1))
bearing('Ink pad felt cushion','Ink pad tin base',(-2.8,3.42,1.0695),(0,0,-1),'felt on hollow case seat')
for suffix,x in [('',-2.838),('.001',-2.762)]:
    bearing('CD | Ink pad pin hinge'+suffix,'Ink pad tin base',(x,3.46,1.073),(0,-1,0),'hinge into case rear edge')
    bearing('Ink pad lid open','CD | Ink pad pin hinge'+suffix,(x,3.47,1.073),(0,-1,0),'open lid bearing on physical pin')
bearing('CD | Ink pad lid inner lip','Ink pad lid open',(-2.8,3.4705,1.095),(0,1,0),'lip engagement in lid')
bearing('CD | Folded wipe lower ply','CD | Counter linoleum inset',(-4.11,3.39,1.042),(0,0,-1))
bearing('CD | Folded wipe middle ply','CD | Folded wipe lower ply',(-4.11,3.39,1.053),(0,0,-1))
for x,y in [(-4.2,3.35),(-4.12,3.345),(-4.03,3.43)]:bearing('CD | Used cotton wipe','CD | Folded wipe middle ply',(x,y,1.062),(0,0,-1),'upper cloth actual drape support')
bearing('D1 keycard reader','Office front wall mid',(-4.7,3.52,1.25),(0,1,0),'reader on actual wall')
bearing('D1 keycard light green','D1 keycard reader',(-4.7,3.488,1.30),(0,1,0),'lens on housing front through aperture')
for suffix,x,z in [('',-4.7,1.20),('.001',-4.7,1.325),('.002',-4.74,1.30),('.003',-4.66,1.30)]:bearing('CD | Reader aperture cap'+suffix,'D1 keycard reader',(x,3.488,z),(0,1,0),'cap seat on actual shell')
for z,suffix in [(1.75,''),(1.92,'.001')]:
    bearing('CD | Service saddle fixing'+suffix,'Office front wall mid',(-4.6125,3.52,z),(0,1,0),'saddle on wall')
    bearing('CD | Door armored conduit','CD | Service saddle fixing'+suffix,(-4.6125,3.489,z),(0,1,0),'conduit held by saddle')
for z,suffix in [(.32,''),(1.12,'.001'),(1.96,'.002')]:
    bearing('CD | D1 hinge strap'+suffix,'D1 door leaf',(-5.86,3.599,z),(0,1,0),'door strap on leaf')
    bearing('CD | D1 hinge strap'+suffix,'CD | D1 captive hinge'+suffix,(-5.9,3.594,z),(-1,0,0),'hinge strap engages barrel')
for suffix,x in [('',-3.72),('.001',-3.30)]:
    bearing('CD | Task wall bracket'+suffix,'Office front head lintel',(x,3.52,2.43),(0,1,0),'practical wall bracket')
    bearing('CD | Task folded shade','CD | Task wall bracket'+suffix,(x,3.43,2.43),(0,1,0),'shade engagement with bracket')
bearing('CD | Task frosted lens','CD | Task folded shade',(-3.51,3.41,2.412),(0,0,1),'practical lens seating')

# Genuine cap aperture rays: opening must miss every cap and hit the lens.
reader_rays=[]
capnames=[n for n in G if n.startswith('CD | Reader aperture cap')]
for x,z in [(-4.7,1.3),(-4.717,1.292),(-4.683,1.308),(-4.74,1.3),(-4.7,1.323)]:
    hits=[G[n].ray((x,3.45,z),(0,1,0),.1) for n in capnames+['D1 keycard light green','D1 keycard reader']]
    reader_rays.append({'sample':[x,z],'hits':sorted([h for h in hits if h],key=lambda h:h['distance'])})

# Finite grid of *combined evaluated* shell surfaces, including retained frames
# and posts. Aperture occupancy is tested from both sides with unchanged parts.
frontnames=[n for n in BG if n.startswith('Office front') or n.startswith('Hatch wall') or n.startswith('D1 frame') or n.startswith('Hatch counter leg')]
newfrontnames=frontnames+['CD | D1 transom closure']
def first(geom,names,p,d):
    hits=[geom[n].ray(p,d,1.) for n in names if n in geom]
    hits=[h for h in hits if h];return min(hits,key=lambda h:h['distance']) if hits else None
xs={-6.799+i*.013 for i in range(339)};zs={.001+i*.011 for i in range(278)}
for g in list(BG.values())+[G[n] for n in newfrontnames]:
    if g.name in frontnames or g.name=='CD | D1 transom closure':
        for v in g.vertices:
            if -6.8<=v.x<=-2.4:xs.update([v.x-1e-4,v.x+1e-4])
            if 0<=v.z<=3.05:zs.update([v.z-1e-4,v.z+1e-4])
# Dense grid plus geometry boundary-near cross-sections, not just AABB.
xs=sorted(x for x in xs if -6.8<x<-2.4);zs=sorted(z for z in zs if 0<z<3.05)
envelope_diff=[];envelope_total=0;missing=0;maxdelta=0;diffzones=Counter();largest=[]
for x in xs:
    for z in zs:
        for y,d in [(3.25,(0,1,0)),(3.95,(0,-1,0))]:
            b=first(BG,frontnames,(x,y,z),d);c=first(G,newfrontnames,(x,y,z),d);envelope_total+=1
            delta=abs(b['distance']-c['distance']) if b and c else None
            if delta is not None:maxdelta=max(maxdelta,delta)
            if bool(b)!=bool(c) or (delta is not None and delta>1e-5):
                missing+=1
                diffzones['door_transom' if -5.925<x<-4.875 and 2.3<z<2.35 else 'door_frame' if -6.025<x<-4.775 and z<2.35 else 'wall_lower' if z<1.05 else 'wall_upper']+=1
                if delta is not None and delta>.005 and len(largest)<10 and -.01+3.05>z>.05 and -6.7<x<-2.5:largest.append({'sample':[x,y,z],'baseline':b,'overhaul':c,'delta_m':delta})
                if len(envelope_diff)<40:envelope_diff.append({'sample':[x,y,z],'baseline':b,'overhaul':c,'delta_m':delta})

local=[g for n,g in G.items() if (n.startswith('CD |') or n.startswith('Office front') or n.startswith('Hatch wall') or S.objects[n].parent and S.objects[n].parent.name in {'D1 Staff Front Door','Checkin Counter Hatch'})]
libraries=[{'path':l.filepath,'parent':l.parent.filepath if l.parent else None,'resolved':bpy.path.abspath(l.filepath),'exists':Path(bpy.path.abspath(l.filepath)).is_file(),'relative':l.filepath.startswith('//'),'resolution_note':'Blender library paths are already rebased into the loaded main file; parent is provenance, not a second path prefix.'} for l in bpy.data.libraries]
report={'source_sha256':sha(SOURCE),'frozen_source_unchanged':sha(SOURCE)==EXPECTED,'native_saved':False,'protected':protected_rows,'used_native_material_datablocks':sorted({m.name for o in S.objects if o.type in {'MESH','CURVE','FONT'} for m in o.data.materials if m}),'cd_authored_material_datablocks':sorted({m.name for o in S.objects if o.type in {'MESH','CURVE','FONT'} for m in o.data.materials if m and m.name.startswith('CD |')}),'contact_assembly_registration':json.loads(S.get('contact_assemblies','[]')),'inventory':{'scene':S.name,'objects':len(S.objects),'triangles':sum(len(g.tris) for g in G.values()),'material_submeshes':sum(g.submeshes for g in G.values()),'local_material_names':sorted({m for g in G.values() for m in g.materials if m and m.startswith('CD |')})},'libraries':libraries,'inherited_matrices':{'count':len(matrices),'exact_unchanged':all(r['pass'] for r in matrices),'differences':[r for r in matrices if not r['pass']]},'architecture_geometry':arch,'local_geometry':[g.summary() for g in local],'bearings':bearings,'reader_aperture':reader_rays,'combined_front_envelope_rays':{'samples':envelope_total,'differences':missing,'difference_zones':dict(diffzones),'max_hit_delta_m':maxdelta,'interior_witnesses':largest,'witnesses':envelope_diff,'baseline_parts':frontnames,'overhaul_parts':newfrontnames},'unverified':['Finite ray sampling is not proof of every possible surface point.','Full room route, engine collision, navigation, runtime draw calls, FPS, and full art acceptance are outside this local audit.','Inherited open curve ends and evaluated FONT boundaries are classified separately, not a universal manifold failure.']}
(OUT/'probe.json').write_text(json.dumps(safe(report),indent=2)+'\n')
print('PROBE_COMPLETE',report['inventory'],flush=True)
print('BEARING_ROWS',len(bearings),'ENVELOPE',envelope_total,missing,'MATRICES',report['inherited_matrices'],flush=True)
