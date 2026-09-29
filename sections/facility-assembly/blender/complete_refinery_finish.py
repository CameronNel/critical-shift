"""Correct the inspected slice and carry the authored finish around the refinery."""
import bpy,bmesh,math,json,hashlib,ctypes,ast,random
from pathlib import Path
from mathutils import Vector,Matrix
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/refinery-finish';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
report=json.loads((OUT/'verification.json').read_text());assert sha(bpy.data.filepath)==report['candidate_sha256']
main=Path(bpy.data.filepath).with_name('facility_environment.blend');assert sha(main)==report['before_sha256']
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();rng=random.Random(27094);coll=bpy.data.collections['ART | Refinery authored surface finish']
for fn,names in [('build_refinery_exterior.py',('mesh','box','cyl','beam','P','wb')),('finish_refinery_surfaces.py',('surface','decal','label','bolt','vent_finish','groundpoly','groundrect'))]:
 tree=ast.parse(Path(__file__).with_name(fn).read_text())
 for name in names:
  fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
  # label and vent functions have material-valued defaults, bound below.
  if name in ('label','vent_finish'):continue
  exec(compile(ast.Module(body=[fun],type_ignores=[]),'<finish-helpers>','exec'))
for var,name in [('steel','Charcoal coated steel'),('blue','Faded slate cobalt'),('zinc','Dusty galvanized duct'),('concrete','Weathered warm mineral concrete'),('patch','Repair panel mineral'),('ochre','Worn ochre safety enamel'),('dark','Recess and rubber'),('rust','Local oxidation')]:globals()[var]=bpy.data.materials['RFX | '+name]
for var,name in [('bare','Exposed brushed edge metal'),('blade','Louvre folded blue grey metal'),('cream','Worn warm ivory stencil'),('shadow','Joint sealant'),('soot','Mineral runoff')]:globals()[var]=bpy.data.materials['RFS | '+name]
tree=ast.parse(Path(__file__).with_name('finish_refinery_surfaces.py').read_text())
for name in ('label','vent_finish'):
 fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[fun],type_ignores=[]),'<detail>','exec'))
oldlabel=label
def label(name,body,side,u,d,z,size,ma=cream):
 o=oldlabel(name,body,side,u,d,z,size,ma)
 if side in 'EW':o.rotation_euler.z+=math.pi
 return o
def chips(side,u,d,z,w,h,count,ma=rust):
 # Thin, connected edge nicks. Long axis follows the painted edge.
 for j in range(count):
  a=u+rng.uniform(-w*.44,w*.44);b=z+rng.uniform(-h*.43,h*.43);ww=rng.uniform(.003,.015);hh=rng.uniform(.025,.095)
  pts=[(a-ww,b-hh*.6),(a+ww*.4,b-hh*.45),(a+ww*.7,b-hh*.1),(a+ww*.4,b+hh*.55),(a-ww*.6,b+hh*.27),(a-ww*.3,b)]
  decal('Fine edge paint loss',side,pts,d,ma)

# Repair defects seen in the first close-up. Only this pass's objects are touched.
for o in list(coll.objects):
 if o.type=='FONT':o.rotation_euler.z+=math.pi
 if o.name.startswith(('RFX | Edge paint loss','RFX | Entry wall recessed','RFX | Entry wall horizontal')):bpy.data.objects.remove(o,do_unlink=True)
 elif o.name.startswith(('RFX | Cabinet recessed service plate','RFX | Cabinet warning enamel')):o.location.x-=.1
 elif o.name.startswith(('RFS | Cabinet code','RFS | Electrical caution')):o.location.x-=.1
 elif o.name.startswith('RFX | Finish hex fixing') and o.location.x>3.39:o.location.x-=.10
 elif o.name.startswith('RFX | Cabinet folded drip hood'):o.location.z-=.22;o.scale.x=.80
# The original cabinet face ends at x=3.3075; labels now sit at x=3.315, not floating 10cm away.
for m in bpy.data.materials:
 if m.name.startswith(('RFS | Dust worn paving','RFS | Older concrete','RFS | Dark service')):
  for n in m.node_tree.nodes:
   if n.type=='BUMP':n.inputs['Strength'].default_value=.10;n.inputs['Distance'].default_value=.0012
groundrect('Dark mortar beneath apron joints',3.55,6.30,-25.7,-9.38,.001,shadow)

# A gentle mineral panel variation, with real narrow joints rather than floating lines.
panels=[surface('Stained mineral panel '+str(i),c,rough=.94,scale=1.25,relief=.003,vertical=True) for i,c in enumerate(((.29,.248,.182),(.265,.228,.174),(.24,.209,.164),(.315,.275,.213)))]
wall_ranges={'E':[(-23.84,-20.79),(-20.41,-19.83),(-16.71,-9.34)],'W':[(-23.83,-20.59),(-20.21,-16.79),(-16.41,-12.99),(-12.61,-9.34)],'S':[(-10.22,-7.19),(-6.81,-3.69),(-3.31,-1.72)],'N':[(-10.20,-7.18),(-6.82,-3.68)]}
depths={'E':.0093,'W':.0278,'S':-.0075,'N':.001}
def wall_finish(side):
 for a,b in wall_ranges[side]:
  num=max(1,round((b-a)/1.48));width=(b-a)/num
  for j in range(num):
   ua=a+j*width;ub=ua+width
   for k,(za,zb) in enumerate(((.59,1.45),(1.462,2.47),(2.482,3.69))):
    decal('Mineral panel face',side,[(ua+.008,za),(ub-.008,za),(ub-.008,zb),(ua+.008,zb)],depths[side],panels[(j+k+len(side))%4])
   wb('Wall panel sealed vertical joint',side,ua,depths[side]-.001,2.13,.013,.003,3.1,shadow,.001)
  for z in (1.455,2.475):wb('Wall panel sealed horizontal joint',side,(a+b)/2,depths[side]-.001,z,b-a,.003,.013,shadow,.001)
wall_finish('E')
# Small corner wear reads as paint erosion instead of raised dark spots.
for u in (-24,-20.6,-16.9,-9.15):
 for du in (-.105,.105):chips('E',u+du,.2258,2,.007,3.55,10,rust)
 chips('E',u+.105,.2261,2.3,.004,3.0,5,bare)
for u in (-22.5,-10.1):chips('E',u,.5885,.724,.54,.022,13,rust)
for du in (-1.275,1.275):chips('E',-13.8+du,.6458,2.85,.04,.95,9,rust)

# Extend the reviewed vent construction and wall finish to mine/rear faces.
vent_finish('W',-17.9,2.8,3.2,1.25,'01');vent_finish('N',-7.5,2.65,2.1,1.15,'03')
for side in ('W','S','N'):wall_finish(side)
for side,us in [('W',(-24,-20.4,-16.6,-12.8,-9.15)),('S',(-10.4,-7,-3.5,2.25)),('N',(-10.4,-7,-3.5,2.25))]:
 for u in us:
  for du in (-.105,.105):chips(side,u+du,.2258,2.25,.005,3.7,9,rust)
  chips(side,u+.1,.226,2.5,.004,3.2,4,bare)
label('Mine side process number','02','W',-15.05,.03,2.75,.65)
label('Mine side process legend','REFINING','W',-15.05,.03,2.22,.13)
label('Receiving instruction','ORE RECEIVING','S',-.10,.02,2.97,.20)
label('Track instruction','KEEP TRACK CLEAR','S',-.10,.021,2.71,.095,ochre)

# Duct sheet-metal construction: standing seams, folded inspection hatch, bolts,
# restrained seam oxidation, a direction arrow and a non-branded asset stencil.
for z in (3.15,4.28,5.15):
 box('Duct circumferential seam front',(-11.55,-22.294,z),(.94,.038,.032),bare,.005)
 box('Duct circumferential seam outside',(-12.017,-21.8,z),(.035,.97,.032),bare,.005)
 for x in (-11.91,-11.19):bolt('S',x,-2.184,z,.023)
box('Duct inspection gasket',(-11.55,-22.283,3.71),(.59,.014,.62),dark,.014)
box('Duct inspection lid',(-11.55,-22.3,3.71),(.55,.022,.58),zinc,.018)
for x in (-11.76,-11.34):
 for z in (3.49,3.93):bolt('S',x,-2.181,z,.021)
label('Duct asset label','EX / 01','S',-11.55,-2.17,3.74,.105,dark)
decal('Duct airflow arrow','S',[(-11.63,4.55),(-11.47,4.55),(-11.47,4.77),(-11.36,4.77),(-11.55,4.98),(-11.74,4.77),(-11.63,4.77)],-2.219,ochre)
for z in (3.15,4.28,5.15):
 chips('S',-11.56,-2.219,z-.045,.75,.028,8,rust)
for x in (-10.2,-9.1,-8.1):
 box('Duct horizontal seam front',(x,-22.294,6.1),(.035,.04,.91),bare,.004)
 box('Duct horizontal seam top',(x,-21.8,6.565),(.035,.97,.03),bare,.004)
# Narrow panel-edge ribs add a highlight without changing the approved duct envelope.
for x in (-11.99,-11.11):box('Duct folded longitudinal edge',(x,-22.287,4.0),(.022,.022,2.32),zinc,.004)

# Functional pipe labels/collars and fasteners break up the uniform headers.
for side,us in [('W',(-23,-19.5,-15.6,-10.1)),('E',(-23,-21,-18.6)),('S',(-9,-6.2,-3.1)),('N',(-9.4,-6.4))]:
 for u in us:
  for z in (4.02,4.39):
   a=Vector(P(side,u-.045,.34,z));b=Vector(P(side,u+.045,.34,z));cyl('Pipe service identification band',a,b,.114 if z==4.02 else .080,ochre,20)
  label('Pipe direction','>','W' if side=='W' else side,u,.463,4.02,.10,dark)

# Filter unit service panels, fasteners and restrained coating loss.
for idx,y in enumerate((-20.2,-14.6),1):
 d=-(24.5+y-1.34)
 for x in (-6.95,-5.95,-4.85):
  box('Filter recessed panel seal',(x,y-1.305,6.03),(.79,.018,.89),dark,.015)
  box('Filter access face',(x,y-1.324,6.03),(.74,.024,.83),blue,.014)
  for dx in (-.3,.3):
   for z in (5.70,6.35):bolt('S',x+dx,d,z,.019)
  chips('S',x,y*-1-23.163,5.64,.7,.035,9,rust)
 label('Filter machinery code','FILTER / 0'+str(idx),'S',-5.9,d+.01,6.06,.12)
 for z in (7.02,7.12):cyl('Stack safety identification',(-5,y,z-.018),(-5,y,z+.018),.342,ochre,32)

# South receiving apron retains the rail opening. These skins add only millimetres.
paving=[bpy.data.materials['RFS | Dust worn paving '+str(i)] for i in range(4)]
for j in range(6):
 a=-10.7+j*1.5;b=min(a+1.48,-1.73)
 if a>=b:continue
 groundrect('Receiving apron slab',a,b,-26.05,-24.85,-.009,paving[j%4])
groundrect('Receiving apron joint underlay',-10.7,-1.73,-26.05,-24.85,-.011,shadow)
# Warm narrow wall-side strip, retaining the original drain and its clear walkway.
for a,b in ((-25.7,-19.65),(-17.16,-9.38)):
 groundrect('Wall side mineral strip',2.79,3.30,a,b,.002,paving[2])

# Check authored manufactured meshes separately from declared surface overlays.
bad=[];overlay_count=0
for o in coll.objects:
 if o.type!='MESH':continue
 if o.get('intentional_surface_overlay'):overlay_count+=1;continue
 bm=bmesh.new();bm.from_mesh(o.data)
 if any(not e.is_manifold for e in bm.edges) or any(f.calc_area()<1e-10 for f in bm.faces):bad.append(o.name)
 bm.free()
assert not bad,bad
frames=[]
for m in bpy.data.materials:
 if m.name.startswith(('RFS |','RFX |')) and m.node_tree:
  ns=m.node_tree.nodes;loose=[n.name for n in ns if n.type!='FRAME' and (not n.parent or n.parent.type!='FRAME')];counts=[sum(n.parent==f for n in ns) for f in ns if f.type=='FRAME'];assert not loose and all(4<=c<=19 for c in counts),(m.name,loose,counts)
  frames.append(dict(material=m.name,nodes=len(ns)-len(counts),unframed=loose,frame_counts=counts,drawn_bounds='unverified: headless'))
report.update(scope='Refinery exterior material depth, selective wear, vent and duct construction, labels, bounded apron paving',new_objects=[o.name for o in coll.objects],intentional_surface_overlays=overlay_count,manufactured_mesh_failures=bad,node_frame_audit=frames,corrections='Mirrored lettering corrected, cabinet plates seated, coarse spot chips replaced by narrow flush edge nicks, apron grain reduced, pale slab gaps replaced by mortar. No mine, cliff, courtyard, interior or shared library edits.')
s.camera=bpy.data.objects['RFX CAMERA | 06_WALK_ENTRY'];s.cycles.samples=12
assert sha(main)==report['before_sha256'],'Concurrent main change'
bpy.ops.wm.save_as_mainfile(filepath=str(main),check_existing=False);report['saved_sha256']=sha(main);(OUT/'verification.json').write_text(json.dumps(report,indent=2));print('REFINERY_FINISH_SAVED',report['saved_sha256'],flush=True)
s.render.filepath=str(OUT/'entry.png');bpy.ops.render.render(write_still=True);print('FINAL_ENTRY_RENDERED',flush=True)
s.camera=bpy.data.objects['RFX CAMERA | 05_WALK_MINE'];s.cycles.samples=8;s.render.filepath=str(OUT/'mine-approach.png');bpy.ops.render.render(write_still=True);print('FINAL_MINE_APPROACH_RENDERED',flush=True)
