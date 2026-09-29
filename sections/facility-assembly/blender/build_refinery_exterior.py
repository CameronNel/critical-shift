"""Bounded approved refinery exterior, with exact pavilion-component removal."""
import bpy,bmesh,math,json,hashlib,ctypes,shutil,ast,sys,random
import numpy as np
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/refinery-build';OUT.mkdir(parents=True,exist_ok=True)
SRC=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
inspection=json.loads((OUT/'inspection.json').read_text());assert sha(SRC)==inspection['sha256'],'Concurrent source change'
SLICE='--slice' in sys.argv
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
backup=SRC.with_name('facility_environment.refinery-before.blend')
if backup.exists():assert sha(backup)==sha(SRC),'Different backup; stop'
else:shutil.copy2(SRC,backup)
tree=ast.parse(Path(__file__).with_name('build_transition_courtyard.py').read_text())
for fname in ('fingerprint','material_sig'):
 fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==fname)
 exec(compile(ast.Module(body=[fun],type_ignores=[]),'<audit>','exec'))
original={o.name_full:fingerprint(o) for o in s.objects};mats={m.name_full:material_sig(m) for m in bpy.data.materials}
libraries={bpy.path.abspath(l.filepath):sha(bpy.path.abspath(l.filepath)) for l in bpy.data.libraries}
coll=bpy.data.collections.new('ART | Refinery exterior process systems');s.collection.children.link(coll)
def mesh(name,vs,fs,mat):
 me=bpy.data.meshes.new('RFX | '+name);me.from_pydata(vs,[],fs);me.update();me.materials.append(mat)
 o=bpy.data.objects.new(me.name,me);coll.objects.link(o);return o
def box(name,p,dim,mat,bev=.015):
 bm=bmesh.new();bmesh.ops.create_cube(bm,size=1)
 for v in bm.verts:v.co=Vector([v.co[i]*dim[i] for i in range(3)])
 if bev:bmesh.ops.bevel(bm,geom=list(bm.edges),offset=min(bev,min(dim)*.23),segments=2,affect='EDGES',clamp_overlap=True)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));me=bpy.data.meshes.new('RFX | '+name);bm.to_mesh(me);bm.free();me.materials.append(mat)
 o=bpy.data.objects.new(me.name,me);coll.objects.link(o);o.location=p;return o
def cyl(name,a,b,r,mat,n=20):
 a,b=Vector(a),Vector(b);bm=bmesh.new();bmesh.ops.create_cone(bm,cap_ends=True,segments=n,radius1=r,radius2=r,depth=(b-a).length)
 me=bpy.data.meshes.new('RFX | '+name);bm.to_mesh(me);bm.free();me.materials.append(mat)
 o=bpy.data.objects.new(me.name,me);coll.objects.link(o);o.location=(a+b)/2;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
 for p in me.polygons:p.use_smooth=len(p.vertices)==4
 return o
def beam(name,a,b,w,d,mat):
 a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(w,d,(b-a).length),mat,.008);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def mat(name,col,rough=.78,metal=.1):
 m=bpy.data.materials.new('RFX | '+name);m.diffuse_color=(*col,1);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear()
 fr=nt.nodes.new('NodeFrame');fr.label='Matte Material Variation'
 ns=[nt.nodes.new(t) for t in ('ShaderNodeTexNoise','ShaderNodeValToRGB','ShaderNodeBsdfPrincipled','ShaderNodeOutputMaterial')]
 for j,n in enumerate(ns):n.parent=fr;n.location=(j*240,0);n.width=180
 no,ra,bs,ou=ns;no.inputs['Scale'].default_value=2.4;no.inputs['Detail'].default_value=1.1
 for e,k in zip(ra.color_ramp.elements,(.79,1.12)):e.color=(*(c*k for c in col),1)
 bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 nt.links.new(no.outputs['Fac'],ra.inputs[0]);nt.links.new(ra.outputs[0],bs.inputs['Base Color']);nt.links.new(bs.outputs[0],ou.inputs[0]);return m
steel=mat('Charcoal coated steel',(.065,.075,.083),.7,.45)
blue=mat('Faded slate cobalt',(.115,.16,.21),.82,.18)
zinc=mat('Dusty galvanized duct',(.34,.35,.33),.68,.42)
concrete=mat('Weathered warm mineral concrete',(.38,.355,.31),.92,0)
patch=mat('Repair panel mineral',(.30,.29,.26),.92,0)
ochre=mat('Worn ochre safety enamel',(.54,.31,.065),.75,.15)
dark=mat('Recess and rubber',(.022,.027,.031),.94,0)
rust=mat('Local oxidation',(.20,.093,.041),.9,.08)

# Remove only the inspected 13 connected pavilion pieces, never adjacent canopy.
gaz=bpy.data.objects['SITE | Reconnected MATERIAL_PREVIEW_09_FINISHED_HORIZONTAL_CONNECTIONS'];assert gaz.library is None
grow=next(o for o in inspection['objects'] if o['name']==gaz.name_full)
parts=[c for c in grow['components'] if c['lo'][0]>=2.65 and c['hi'][0]<=8.9 and c['lo'][1]>=-12.7 and c['hi'][1]<=-9.7]
assert len(parts)==13 and sum(c['count'] for c in parts)==728
gaz.data=gaz.data.copy();bm=bmesh.new();bm.from_mesh(gaz.data);bm.verts.ensure_lookup_table();remove=set()
for c in parts:
 start=bm.verts[c['first']];todo=[start];seen={start}
 while todo:
  v=todo.pop()
  for e in v.link_edges:
   w=e.other_vert(v)
   if w not in seen:seen.add(w);todo.append(w)
 assert len(seen)==c['count'];remove.update(seen)
assert len(remove)==728
remaining_before=sorted(tuple(round(q,7) for q in v.co) for v in bm.verts if v not in remove)
bmesh.ops.delete(bm,geom=list(remove),context='VERTS');bm.to_mesh(gaz.data);bm.free()
assert remaining_before==sorted(tuple(round(q,7) for q in v.co) for v in gaz.data.vertices)

# Local outward finish layer; original exterior and interior meshes are untouched.
ext=bpy.data.objects['MATERIAL_PREVIEW_EXTERIOR_INSTANCE_refinery'];me=ext.data
allow=[j for j,m in enumerate(me.materials) if m and any(k in m.name for k in ('exposed plinth','mineral painted concrete','muted cobalt'))]
faces=[p for p in me.polygons if p.material_index in allow];used=sorted({i for p in faces for i in p.vertices});lookup={v:i for i,v in enumerate(used)}
vs=[]
for i in used:
 p=ext.matrix_world@me.vertices[i].co
 distances=[abs(p.x+10.84),abs(p.x-2.68),abs(p.y+24.45),abs(p.y+8.75)];side=distances.index(min(distances))
 p[0 if side<2 else 1]+=[-.028,.028,-.028,.028][side];vs.append(tuple(p))
skin=mesh('Local weathered facade skin',vs,[[lookup[i] for i in p.vertices] for p in faces],concrete);skin.data.materials.append(blue);skin.data.materials.append(patch)
for q,p in zip(skin.data.polygons,faces):
 name=me.materials[p.material_index].name;q.material_index=1 if 'cobalt' in name else 2 if 'plinth' in name else 0
skin['intentional_surface_overlay']=True

# Canonical wall coordinates. Positive depth points out from each facade.
def P(side,u,d,z):
 return {'W':(-10.87-d,u,z),'E':(2.72+d,u,z),'S':(u,-24.5-d,z),'N':(u,-8.7+d,z)}[side]
def wb(name,side,u,d,z,w,depth,h,ma,bev=.015):
 return box(name,P(side,u,d,z),(depth,w,h) if side in 'WE' else (w,depth,h),ma,bev)
def pipe(name,points,r,ma):
 # Rounded polyline with tangent-continuous sampled elbows, capped manifold mesh.
 points=[Vector(p) for p in points];path=[points[0]]
 for j in range(1,len(points)-1):
  a,b,c=points[j-1:j+2];cut=min(.28,(b-a).length*.3,(c-b).length*.3)
  q=b+(a-b).normalized()*cut;t=b+(c-b).normalized()*cut;path.append(q)
  for k in range(1,7):
   f=k/6;path.append((1-f)**2*q+2*f*(1-f)*b+f*f*t)
 path.append(points[-1]);vs=[];fs=[];N=16;previous=None
 for j,p in enumerate(path):
  tangent=(path[min(j+1,len(path)-1)]-path[max(j-1,0)]).normalized()
  axis=tangent.cross(Vector((0,0,1)))
  if axis.length<.01:axis=Vector((1,0,0))
  axis.normalize()
  if previous is not None and axis.dot(previous)<0:axis=-axis
  second=tangent.cross(axis).normalized();previous=axis
  for k in range(N):vs.append(tuple(p+r*(math.cos(k*2*math.pi/N)*axis+math.sin(k*2*math.pi/N)*second)))
 for j in range(len(path)-1):
  for k in range(N):a=j*N+k;b=j*N+(k+1)%N;fs.append((a,b,b+N,a+N))
 fs.extend([tuple(reversed(range(N))),tuple((len(path)-1)*N+k for k in range(N))]);o=mesh(name,vs,fs,ma)
 for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
 return o
def flange(name,p,axis,r=.17):
 p=Vector(p);ax=Vector(axis).normalized();cyl(name+' collar',p-ax*.045,p+ax*.045,r,zinc)
 q=ax.cross(Vector((0,0,1)))
 if q.length<.1:q=Vector((1,0,0))
 q.normalize();v=ax.cross(q)
 for a in range(6):
  c=p+(q*math.cos(a*math.pi/3)+v*math.sin(a*math.pi/3))*r*.76
  cyl(name+' bolt',c-ax*.055,c+ax*.055,.023,steel,6)
def valve(side,u,z):
 p=Vector(P(side,u,.57,z));ax=Vector(P(side,u,.7,z))-p;ax.normalize()
 cyl('Valve stem',p-ax*.2,p+ax*.16,.045,zinc)
 # Wheel torus from a circular closed pipe path.
 up=Vector((0,0,1));right=ax.cross(up)
 pts=[p+ax*.16+.18*(right*math.cos(k*2*math.pi/24)+up*math.sin(k*2*math.pi/24)) for k in range(25)]
 for a,b in zip(pts,pts[1:]):cyl('Valve wheel rim',a,b,.023,ochre,8)
 for k in range(3):beam('Valve wheel spoke',p+ax*.16,p+ax*.16+.16*(right*math.cos(k*2*math.pi/3)+up*math.sin(k*2*math.pi/3)),.025,.025,ochre)
def vent(side,u,z,w=2.8,h=1.2):
 wb('Vent wall penetration',side,u,.04,z,w,.12,h,dark)
 for du in (-w/2,w/2):wb('Vent projecting jamb',side,u+du,.3,z,.13,.6,h+.24,zinc)
 for dz in (-h/2,h/2):wb('Vent folded sill and hood',side,u,.32,z+dz,w+.13,.64,.13,zinc)
 for k in range(8):
  o=wb('Angled louvre blade',side,u,.36,z-h*.43+k*h*.123,w-.15,.48,.065,steel,.009)
  if side in 'WE':o.rotation_euler.y=.30
  else:o.rotation_euler.x=.30
 for du in (-w*.36,w*.36):beam('Vent cantilever brace',P(side,u+du,.02,z-h/2-.55),P(side,u+du,.5,z-h/2),.09,.09,steel)
def wall(side,us):
 for u in us:
  wb('Facade structural pier',side,u,.11,2.45,.26,.23,4.7,blue)
  wb('Pier concrete foot',side,u,.15,.28,.48,.31,.56,concrete)
  for z in (1,3.6,4.5):wb('Pier strap',side,u,.25,z,.35,.06,.10,zinc)
def header(side,a,b):
 for z,r in ((4.02,.11),(4.39,.075)):
  pipe('Service supply header', [P(side,a,-.04,z-.55),P(side,a,.34,z-.55),P(side,a,.34,z),P(side,b,.34,z),P(side,b,.34,z-.6),P(side,b,-.04,z-.6)],r,steel)
  for u in np.arange(a+.7,b-.3,2.5):
   wb('Pipe anchor plate',side,float(u),.045,z,.15,.09,.38,zinc)
   beam('Pipe standoff',P(side,float(u),.08,z),P(side,float(u),.34,z),.07,.07,steel)
   axis=(0,1,0) if side in 'WE' else (1,0,0);flange('Header coupling',P(side,float(u),.34,z),axis,r+.045)
wall('W',[-24,-20.4,-16.6,-12.8,-9.15]);wall('S',[-10.4,-7,-3.5,2.25])
vent('W',-17.9,2.8,3.2,1.25);header('W',-23.3,-9.7);header('S',-9.5,-2.3)

# Roof extraction units: supported skids, removable panels, access handles, stacks.
for y in (-20.2,-14.6):
 for x in (-7.2,-4.5):box('Rooftop equipment concrete curb',(x,y,5.17),(.3,2.6,.26),concrete)
 box('Filter unit sill',(-5.85,y,5.38),(3.25,2.8,.18),steel)
 box('Filter unit housing',(-5.85,y,6.02),(3.1,2.6,1.18),blue,.06)
 box('Filter unit folded top',(-5.85,y,6.65),(3.28,2.77,.10),zinc)
 for x in (-6.65,-5.45):
  box('Removable filter door',(x,y-1.321,6.0),(1.02,.07,.89),zinc)
  beam('Filter door handle',(x+.32,y-1.4,5.86),(x+.32,y-1.4,6.16),.035,.045,steel)
  for z in (5.73,6.3):box('Door hinge',(x-.39,y-1.375,z),(.06,.08,.13),steel)
 box('Filter side intake recess',(-4.285,y,6.0),(.065,1.8,.8),dark)
 for z in np.arange(5.67,6.4,.095):
  ob=box('Filter side intake louvre',(-4.23,y,float(z)),(.15,1.7,.035),zinc,.004);ob.rotation_euler.y=.3
 # Separate exhaust stack with collars and supported rain cowl.
 x=-5.0;cyl('Exhaust stack',(x,y,6.69),(x,y,7.72),.34,zinc,32)
 for z in (6.77,7.48):cyl('Stack reinforcing band',(x,y,z-.06),(x,y,z+.06),.375,steel,32)
 for a in range(4):
  t=a*math.pi/2;beam('Rain cap support',(x+.29*math.cos(t),y+.29*math.sin(t),7.6),(x+.29*math.cos(t),y+.29*math.sin(t),7.86),.045,.045,steel)
 cyl('Rain cap',(x,y,7.84),(x,y,7.94),.46,steel,32)

# Broad bent extraction duct on blank mine-facing wall; real section depth.
path=[Vector(p) for p in [(-10.78,2.8),(-11.55,2.8),(-11.55,5.5),(-10.8,6.1),(-7.4,6.1)]]
dirs=[(b-a).normalized() for a,b in zip(path,path[1:])];norms=[Vector((-d.y,d.x)) for d in dirs];left=[];right=[]
for j,p in enumerate(path):
 if j==0:offset=norms[0]*.45
 elif j==len(path)-1:offset=norms[-1]*.45
 else:
  bis=(norms[j-1]+norms[j]).normalized();offset=bis*(.45/bis.dot(norms[j]))
 left.append(p+offset);right.append(p-offset)
outline=left+list(reversed(right));N=len(outline)
duct=mesh('Continuous mitered extraction duct',[(p.x,y,p.y) for y in (-22.275,-21.325) for p in outline],[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],zinc)
bm=bmesh.new();bm.from_mesh(duct.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(duct.data);bm.free()
box('Extraction final corner',(-7.4,-21.8,6.1),(.95,.95,.90),zinc,.014)
beam('Extraction filter inlet',(-7.4,-21.8,6.1),(-7.4,-20.2,6.1),.95,.9,zinc)
box('Duct upright clamp',(-11.55,-21.8,3.55),(.96,1.01,.065),steel,.003)
box('Duct horizontal clamp',(-9.45,-21.8,6.1),(.065,1.01,.96),steel,.003)
box('Duct inlet clamp',(-7.4,-20.8,6.1),(1.01,.065,.96),steel,.003)
for z in (3.0,4.6):beam('Extraction wall bracket',(-10.82,-21.8,z),(-11.65,-21.8,z),.12,.12,steel)

# Roof access deck and guarded ladder, clear of doors and rail.
box('Maintenance deck substrate',(-9.1,-15.75,5.18),(1.18,10.3,.12),steel)
for y in (-20.7,-18.5,-16,-13.5,-11):box('Deck bearing shoe',(-9.1,y,5.08),(1.15,.20,.08),zinc)
for y in np.arange(-20.8,-10.6,.22):box('Deck serrated tread',(-9.1,float(y),5.255),(1.12,.065,.045),zinc,.005)
for x in (-9.66,-8.54):
 for y in (-20.8,-18.4,-16.1,-13.8,-10.7):beam('Guardrail stanchion',(x,y,5.24),(x,y,6.28),.055,.055,ochre)
 for z in (5.78,6.28):beam('Guardrail horizontal',(x,-20.8,z),(x,-10.7,z),.055,.055,ochre)
 if x==-9.66:
  for a,b in ((-20.8,-13.35),(-12.3,-10.7)):box('Catwalk toe plate',(x,(a+b)/2,5.36),(.045,b-a,.15),steel)
 else:box('Catwalk toe plate',(x,-15.75,5.36),(.045,10.1,.15),steel)
for y in (-20.8,-10.7):
 for z in (5.78,6.28):beam('Catwalk end guard',(-9.66,y,z),(-8.54,y,z),.055,.055,ochre)
for y in (-13.2,-12.45):
 beam('Access ladder rail',(-11.36,y,.18),(-11.36,y,6.15),.065,.065,ochre)
 box('Ladder anchored foot',(-11.36,y,.13),(.20,.16,.26),steel)
 for z in (.5,2.5,4.5):beam('Ladder wall stand-off',(-10.85,y,z),(-11.36,y,z),.06,.06,steel)
for z in np.arange(.4,5.25,.28):cyl('Ladder rung',(-11.36,-13.2,float(z)),(-11.36,-12.45,float(z)),.025,steel,12)
box('Ladder top landing',(-10.3,-12.825,5.18),(2.15,.9,.12),steel)
for y in (-13.1,-12.55):beam('Landing diagonal support',(-10.84,y,4.32),(-11.3,y,5.12),.10,.10,steel)
# Landing joins the near edge of catwalk; local crossing guardrail gap is explicit.
for o in list(coll.objects):
 if o.name.startswith('RFX | Guardrail horizontal') and abs(o.location.x+9.66)<.05:
  # Replace the long two rails with sections around ladder opening.
  z=o.location.z;bpy.data.objects.remove(o,do_unlink=True)
  beam('Guardrail horizontal before landing',(-9.66,-20.8,z),(-9.66,-13.35,z),.055,.055,ochre)
  beam('Guardrail horizontal after landing',(-9.66,-12.3,z),(-9.66,-10.7,z),.055,.055,ochre)

# Pump skid on the blind south wall, safely west of the receiving doorway.
box('Pump pad',(-6.1,-25.0,.12),(3.5,.85,.24),concrete)
for x in (-7.1,-5.6):
 box('Pump foot',(x,-25.05,.32),(.85,.5,.15),steel)
 cyl('Pump motor',(x-.3,-25.05,.61),(x+.28,-25.05,.61),.23,blue,24)
 for f in np.arange(x-.25,x+.25,.08):cyl('Motor cooling fin',(float(f),-25.05,.61),(float(f)+.025,-25.05,.61),.26,steel,20)
 cyl('Pump volute',(x+.29,-25.05,.61),(x+.49,-25.05,.61),.30,zinc,24)
 pipe('Pump return riser',[(x+.48,-25.05,.68),(x+.48,-25.05,1.35),(x+.48,-24.8,1.35),(x+.48,-24.8,3.4),(x+.48,-24.45,3.4)],.10,steel)
 flange('Pump riser union',(x+.48,-25.05,1.1),(0,0,1));valve('S',x+.48,1.75)
box('Pump electrical pedestal',(-8.45,-24.99,.8),(.6,.5,1.35),blue)
box('Pump control face',(-8.45,-25.26,.93),(.49,.05,.62),zinc)

if not SLICE:
 wall('E',[-24,-20.6,-16.9,-9.15]);wall('N',[-10.4,-7,-3.5,2.25])
 vent('E',-13.8,2.85,2.55,1.15);vent('N',-7.5,2.65,2.1,1.15)
 header('E',-23.25,-17.8);header('N',-9.8,-5.9)
 # Raised hatch and protected rooftop conduits around existing roof ventilator.
 for y in (-18.2,-12.2):
  box('Roof access hatch curb',(-2.2,y,5.18),(1.5,1.3,.28),steel)
  box('Roof hatch lid',(-2.2,y,5.34),(1.58,1.38,.10),zinc)
  beam('Hatch lift handle',(-2.5,y,5.44),(-2.1,y,5.44),.035,.055,steel)
 for y in np.arange(-23,-10,2):
  box('Roof pipe sleeper',(.8,float(y),5.17),(.95,.22,.26),concrete)
 for x in (.55,.94):pipe('Roof supply main',[(x,-23,5.35),(x,-10,5.35),(-4.2,-10,5.35),(-4.2,-14.6,5.35),(-4.2,-14.6,5.9)],.10,steel)
 # Exterior personnel-side utility cabinet, away from door at y approximately -15.
 for y in (-22.5,-10.1):
  wb('Service cabinet wall bracket','E',y,.12,1.15,.7,.2,1.05,steel)
  wb('Service cabinet enclosure','E',y,.33,1.15,.68,.43,1.0,blue)
  wb('Service cabinet inset face','E',y,.565,1.15,.57,.045,.88,zinc)
  wb('Cabinet pull','E',y+.19,.61,1.15,.04,.05,.21,steel)
  pipe('Cabinet cable conduit',[P('E',y,.28,1.7),P('E',y,.28,3.6),P('E',y+.7,.28,3.6),P('E',y+.7,-.03,3.6)],.028,steel)

# Localized painted repairs and oxidized drip strips, not blanket noisy grunge.
rng=random.Random(928)
for side,us in [('W',[-23,-19.8,-15.5,-10.1]),('S',[-9.1,-4.4]),('E',[-23,-21,-10]),('N',[-9.2,-6.2])]:
 if SLICE and side in 'EN':continue
 for u in us:
  wb('Lower wall repair',side,u,.06,.65,rng.uniform(.45,.85),.025,rng.uniform(.35,.65),patch,.002)
  for k in range(2):wb('Localized joint oxidation',side,u+k*.09,.065,3.7-rng.random()*.18,.025,.012,.25+rng.random()*.3,rust,.002)

# Save useful elevated and eye-height review cameras in the final scene.
camera_defs=[('01_SW',(-21,-37,13),(-4,-17,2),32),('02_SE',(13,-37,13),(-4,-17,2),32),('03_NE',(13,3,13),(-4,-17,2),32),('04_NW',(-21,3,13),(-4,-17,2),32),('05_WALK_MINE',(-16,-31,1.75),(-7,-22,3.1),25),('06_WALK_ENTRY',(8,-24,1.75),(2,-17,2.3),25)]
for name,pos,target,lens in camera_defs:
 o=bpy.data.objects.new('RFX CAMERA | '+name,bpy.data.cameras.new('RFX CAMERA | '+name));coll.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens
bpy.context.view_layer.update()
errors=[]
for o in coll.objects:
 if o.type!='MESH' or o.get('intentional_surface_overlay'):continue
 bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);deg=sum(f.calc_area()<1e-10 for f in bm.faces);bm.free()
 if bad or deg:errors.append((o.name,bad,deg))
assert not errors,errors
def route(a,b):
 a,b=Vector(a),Vector(b);n=max(1,math.ceil((b-a).length/.35));return [a+(b-a)*j/n for j in range(n+1)]
route_points=[]
for label,a,b in [('west service',(-12.8,-26),(-12.8,-8)),('south service',(-12,-26.3),(-1.9,-26.3)),('rail entry',(0,-28),(0,-24.4)),('personnel entry',(2.8,-18.4),(6,-18.4)),('east service',(5,-25),(5,-8)),('north service',(-10,-6.5),(2,-6.5))]:
 for p in route(a,b):route_points.append(dict(route=label,xy=list(p)))
blockers=[]
for o in coll.objects:
 if o.type!='MESH' or o.get('intentional_surface_overlay'):continue
 bb=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(v[i] for v in bb) for i in range(3)];hi=[max(v[i] for v in bb) for i in range(3)]
 if hi[2]<.28 or lo[2]>2.05:continue
 for p in route_points:
  x,y=p['xy']
  if lo[0]-.4<x<hi[0]+.4 and lo[1]-.4<y<hi[1]+.4:blockers.append((p,o.name))
assert not blockers,blockers
current_objects={o.name_full:o for o in s.objects}
changed=[n for n,h in original.items() if fingerprint(current_objects[n])!=h]
assert changed==[gaz.name_full],changed
assert all(material_sig(m)==mats[m.name_full] for m in bpy.data.materials if m.name_full in mats),'Shared material changed'
assert all(sha(p)==h for p,h in libraries.items()),'Library changed'
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False
s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
s.camera=bpy.data.objects['RFX CAMERA | 01_SW'];s.render.image_settings.file_format='PNG'
assert sha(SRC)==inspection['sha256'],'Concurrent source change; refusing overwrite'
destination=SRC.with_name('facility_environment.refinery-slice.blend') if SLICE else SRC
bpy.ops.wm.save_as_mainfile(filepath=str(destination))
report=dict(source=str(destination),saved_sha256=sha(destination),baseline_sha256=inspection['sha256'],backup=str(backup),slice=SLICE,removed_pavilion_components=parts,removed_vertices=728,original_changes=changed,protected_fingerprints={n:h for n,h in original.items() if n!=gaz.name_full},libraries=libraries,new_objects=len(coll.objects),mesh_errors=errors,cameras=camera_defs,route_samples=route_points,new_route_blockers=blockers,node_layout_note='All new shaders have four framed nodes and left-to-right layout. Drawn node bounds remain unverified in headless mode.')
(OUT/('slice-verification.json' if SLICE else 'build-verification.json')).write_text(json.dumps(report,indent=2))
print('REFINERY_SAVED',str(destination),report['saved_sha256'],flush=True)
s.render.filepath=str(OUT/('slice.png' if SLICE else '01_SW.png'));bpy.ops.render.render(write_still=True)
print('REFINERY_RENDER_COMPLETE',flush=True)
