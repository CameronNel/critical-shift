"""Fit a weathered cover to the measured existing medical canopy, preserving its source."""
import bpy,bmesh,math,json,hashlib,ctypes,ast
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/spawn-finish';SRC=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((OUT/'construction.json').read_text());before=sha(SRC);assert before==r['candidate_sha256'];assert sha(SRC.with_name('facility_environment.blend'))==r['before_sha256']
coll=bpy.data.collections['ART | Spawn and medical courtyard'];steel=bpy.data.materials['RFX | Charcoal coated steel'];zinc=bpy.data.materials['RFX | Dusty galvanized duct'];oxide=bpy.data.materials['RFX | Muted oxide maintenance enamel'];cream=bpy.data.materials['RFS | Worn warm ivory stencil']
tree=ast.parse(Path(__file__).with_name('build_refinery_exterior.py').read_text().replace("'RFX | '","'SY | '"))
for name in ('box','beam','cyl'):
 fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[fun],type_ignores=[]),'<mesh>','exec'))
box('Medical canopy fitted weather cap',(-18,29.14,3.397),(7.58,2.26,.035),steel,.005)
box('Medical canopy folded front',(-18,27.954,3.12),(7.58,.085,.43),steel,.006)
for x in (-21.773,-14.227):box('Medical canopy side return',(x,29.14,3.28),(.046,2.29,.26),steel,.006)
box('Medical canopy underside edge',(-18,28.015,2.908),(7.57,.18,.025),zinc,.003)
box('Medical canopy sign enamel',(-18,27.902,3.12),(4.7,.020,.29),oxide,.007)
cu=bpy.data.curves.new('SY | Medical canopy lettering','FONT');cu.body='MEDICAL + RECOVERY';cu.size=.196;cu.align_x='CENTER';cu.align_y='CENTER';cu.extrude=.0005;cu.materials.append(cream)
o=bpy.data.objects.new(cu.name,cu);coll.objects.link(o);o.location=(-18,27.888,3.12);o.rotation_euler=(math.pi/2,0,0)
for x in (-21.3,-14.7):
 beam('Medical canopy connected support',(x,30.71,2.50),(x,28.16,3.21),.095,.10,steel)
 box('Medical canopy support wall plate',(x,30.68,2.73),(.18,.07,.58),steel,.005)
 for z in (2.51,2.96):cyl('Medical support seated anchor',(x,30.636,z),(x,30.62,z),.026,zinc,6)
for x in (-21.2,-14.8):
 for z in (2.98,3.27):cyl('Medical fascia bolt',(x,27.907,z),(x,27.896,z),.019,zinc,6)
# Depth and localized wet response remain distinct; never blanket gloss.
for m in bpy.data.materials:
 if m.name.startswith('SY | Courtyard dimensional slab mineral'):
  for n in m.node_tree.nodes:
   if n.type=='MAP_RANGE':n.inputs['To Max'].default_value=.21
bpy.context.view_layer.update();assert sha(SRC)==before;bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(SRC));r['candidate_sha256']=sha(SRC);r['new_objects']=len(coll.objects);r['medical_canopy']='Measured existing bounds [-21.75,28.02,2.92] to [-14.25,30.25,3.38]; additive fitted steel cover and replacement visible lettering, linked source retained.'
(OUT/'construction.json').write_text(json.dumps(r,indent=2));print('CANOPY_CORRECTED',flush=True)
