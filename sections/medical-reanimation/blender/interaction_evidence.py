"""Saved-artifact state/obstruction evidence. In-memory poses only; never overwrite the source .blend."""
import bpy,json,math,sys,argparse,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
p=argparse.ArgumentParser();p.add_argument('--render',action='store_true');evidence_args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
exec(compile((R/'blender/validate_scene.py').read_text(),str(R/'blender/validate_scene.py'),'exec'))
rows=[]
# Conservative carried-body and recoverable obstruction scenarios through actual shell.
for name,points,hx,hy,obstacle in [
 ('two_person_carry',[(0,-.8),(0,6.9)],.90,.35,None),
 ('dropped_body_bypass',[(0,1.5),(1.45,2.7),(1.45,6.5),(0,7.2)],.30,.30,[-.925,3.95,.925,4.60]),
 ('dropped_cart_bypass',[(0,1.5),(1.2,2.8),(1.2,6.6),(0,7.2)],.30,.30,[-.37,3.58,.37,5.68])]:
 bad=[];num=0
 for pa,pb in zip(points,points[1:]):
  pa=Vector(pa);pb=Vector(pb);steps=max(1,math.ceil((pb-pa).length/.10))
  for j in range(steps+1):
   c=pa.lerp(pb,j/steps);num+=1;hits=hits_box(c.x,c.y,hx,hy)
   if obstacle and c.x+hx>obstacle[0] and c.x-hx<obstacle[2] and c.y+hy>obstacle[1] and c.y-hy<obstacle[3]:hits.append('STAGED_OBSTRUCTION')
   if hits:bad.append({'position':list(c),'hits':hits})
 rows.append({'id':name,'pass':not bad,'path':points,'envelope':[hx*2,hy*2,1.825],'obstacle_xy':obstacle,'samples':num,'obstructions':bad})
cart=s.objects['BODY_CART'];bridge=s.objects['OCRU_TRANSFER_BRIDGE'];tray=s.objects['CART_LIFT_DECK']
surface_cart=1.008;surface_bridge=bridge.get('deploy_z',.999)+.009;surface_berth=1.02
left_cart=-1.08-.37;bridge_outer=-2.70875+.61+.48+.44;hinge_x=-2.70875+.61+.48
rows.append({'id':'transfer_deployed_contact_design','pass':abs(surface_cart-surface_bridge)<.001 and 0<=surface_berth-surface_bridge<=.02 and bridge_outer>left_cart and hinge_x<left_cart,'cart_center':[-1.08,4.63,0],'cart_lift':surface_cart-.92,'surfaces_z':[surface_cart,surface_bridge,surface_berth],'bridge_x':[hinge_x,bridge_outer],'cart_west_edge':left_cart,'bearing_overlap_m':bridge_outer-left_cart,'note':'Slide-assisted lift aligns bridge and cart; evaluate posed rendered mechanism independently.'})
# Exact inherited opening measured in technical report; leaf stroke remains inside owned housing.
leaves=[s.objects['ENTRY_LEAF_L'],s.objects['ENTRY_LEAF_R']]
rows.append({'id':'door_stroke','pass':all(abs(abs(o['open_x']-o['closed_x'])-1.12)<.001 for o in leaves),'strokes':[{'object':o.name,'open_x':o['open_x'],'closed_x':o['closed_x'],'width':1.1} for o in leaves],'note':'Opposed sliding leaves, no swing volume. Closed leaves intentionally fill main_entry.'})
dest=R/'production/validation'/s.get('revision','unknown');dest.mkdir(parents=True,exist_ok=True)
(dest/'interaction.json').write_text(json.dumps({'pass':all(r['pass'] for r in rows),'checks':rows,'limitations':['Specific static recoverable obstruction arrangements, not all possible ragdoll poses.','Host must support repositioning/detaching bodies and carts at the only entry.','No engine navmesh/network/state implementation asserted.']},indent=2));print('INTERACTION',[(r['id'],r['pass']) for r in rows])
if not evidence_args.render:raise SystemExit
# Render original authored material/geometry in temporary state poses with a neutral mannequin.
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='HIP';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='HIP'
if not any(d.use for d in prefs.devices):raise RuntimeError('HIP unavailable')
s.cycles.device='GPU';s.cycles.samples=48;s.cycles.use_denoising=True;s.cycles.seed=17;s.render.resolution_x=1440;s.render.resolution_y=900;s.render.resolution_percentage=100
out=R/'production/renders/states'/s.get('revision','unknown');out.mkdir(parents=True,exist_ok=True);manifest=[]
def camera(name,loc,target,lens=24):
 d=bpy.data.cameras.new(name);d.lens=lens;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;return o
def render(name,loc,target,lens=24):
 c=camera(name,loc,target,lens);s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);manifest.append({'camera':name,'location':loc,'target':target,'sha256':hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest()});(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
cart.location=(-1.08,4.63,0);tray.location.z=.088;bridge.rotation_euler.x=0;bridge.location.z=bridge.get('deploy_z',.999)
scissor_original={o.name:o.matrix_basis.copy() for o in cart.children if o.name.startswith(('Cart lift scissor','Scissor fulcrum','Scissor lower slider'))}
# Re-pose the editable scissor bars against the raised deck; no unsupported lift in demonstration.
for index,o in enumerate(sorted([o for o in cart.children if o.name.startswith('Cart lift scissor')],key=lambda o:o.name)):
 x=-.20 if index<2 else .20;direction=1 if index%2==0 else -1
 span=math.sqrt(1.27**2+.50**2-.588**2)
 aa=Vector((x,(-span/2-.005)*direction,.30));bb=Vector((x,(span/2-.005)*direction,.888))
 local_length=max(v.co.z for v in o.data.vertices)-min(v.co.z for v in o.data.vertices)
 o.location=(aa+bb)/2;o.rotation_euler=(bb-aa).to_track_quat('Z','Y').to_euler();o.scale.z=(bb-aa).length/local_length
for o in cart.children:
 if o.name.startswith('Scissor fulcrum'):o.location.z=.594
 if o.name.startswith('Scissor lower slider'):o.location.y=(-span/2-.005) if o.location.y<0 else (span/2-.005)
# Simple neutral articulated worker proxy is evidence-only, not a shipped character asset.
mat=bpy.data.materials.new('Evidence mannequin neutral');mat.diffuse_color=(.16,.17,.16,1);mat.use_nodes=True;mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.16,.17,.16,1);mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.95
proxy=[]
def ellipsoid(name,loc,scale):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(mat);proxy.append(o)
ellipsoid('Evidence head',(-1.08,5.39,1.16),(.12,.14,.13));ellipsoid('Evidence torso',(-1.08,4.90,1.15),(.23,.30,.13));ellipsoid('Evidence pelvis',(-1.08,4.51,1.12),(.19,.17,.10))
for side in [-1,1]:
 ellipsoid('Evidence leg',(-1.08+side*.11,4.02,1.1),(.085,.34,.08));ellipsoid('Evidence arm',(-1.08+side*.27,4.80,1.10),(.055,.29,.06))
render('S01_TRANSFER',(1.25,3.05,1.68),(-1.60,4.63,1.0),26)
for o in proxy:bpy.data.objects.remove(o,do_unlink=True)
for n,m in scissor_original.items():s.objects[n].matrix_basis=m
cart.location=(0,4.63,0);tray.location.z=0;bridge.rotation_euler.x=math.pi;bridge.location.z=bridge.get('park_z',.924)
render('S02_DROPPED_CART_BYPASS',(1.2,2.1,1.68),(1.2,6.0,1.1),24)
cart.location=(2.15,6.95,0)
# Pose the same wand on the cart deck and extend its editable hose from the 5m reel.
wash=s.objects['DECON_WASH'];hose=s.objects['Wand service hose'];hose.hide_render=True
cu=bpy.data.curves.new('Evidence extended wash hose','CURVE');cu.dimensions='3D';cu.bevel_depth=.020;cu.bevel_resolution=3
pts=[(2.75,10.90,1.78),(2.70,10.3,1.35),(2.4,9.25,.98),(2.15,7.8,.94),(2.15,7.55,.95)]
sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
for bp,co in zip(sp.bezier_points,pts):bp.co=co;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
ext=bpy.data.objects.new('Evidence extended wash hose',cu);s.collection.objects.link(ext);cu.materials.append(hose.data.materials[0])
from mathutils import Matrix
wand_orig={n:s.objects[n].matrix_world.copy() for n in ['Decon wand grip','Decon wash nozzle']}
transform=Matrix.Translation(Vector((2.15,7.55,.95)))@Matrix.Rotation(math.pi/2,4,'X')@Matrix.Translation(-Vector((2.03,10.94,1.12)))
for n,m in wand_orig.items():s.objects[n].matrix_world=transform@m
render('S03_DECON_APRON',(1.2,6.25,1.68),(2.15,9.1,1.10),24)
for n,m in wand_orig.items():s.objects[n].matrix_world=m
bpy.data.objects.remove(ext,do_unlink=True);hose.hide_render=False
cart.location=(-3.12,1.33,0)
for o in leaves:o.location.x=o['closed_x']
render('S04_ENTRY_CLOSED',(0,2.4,1.68),(0,0,1.3),24)
for o in leaves:o.location.x=o['open_x']
cart.location=(-1.65,1.33,0)
render('S06_CART_EXTRACTION',(.55,2.55,1.68),(-1.95,1.33,.8),25)
cart.location=(-3.12,1.33,0)
if 'RESERVE_SERVICE_DOOR' in s.objects:
 s.objects['RESERVE_SERVICE_DOOR'].rotation_euler.z=math.radians(100)
 render('S05_RESERVE_SERVICE',(-.6,7.30,1.68),(-2.15,8.72,.8),32)
print('STATE_RENDER_COMPLETE',len(manifest))
