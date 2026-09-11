"""Deterministic final art pass on the original full-hall build. No asset imports.

Run after build_room.py; saves the same owned blend with a complete source receipt.
"""
import bpy,json,hashlib,sys,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--revision',default='E05')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
s=bpy.context.scene
assert s.get('section')=='electrical-room' and s.get('stage')=='full'
def rgb(h):
 v=[int(h[i:i+2],16)/255 for i in [0,2,4]]
 return [x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v]
m=bpy.data.materials['Dry ground concrete'];base=rgb('55534D');m.diffuse_color=(*base,1)
for n in m.node_tree.nodes:
 if n.type=='VALTORGB':
  n.color_ramp.elements[0].color=(*(v*.80 for v in base),1)
  n.color_ramp.elements[1].color=(*(v*1.20 for v in base),1)
 if n.type=='BSDF_PRINCIPLED':n.inputs['Base Color'].default_value=(*base,1)
 if n.type=='TEX_NOISE' and n.inputs['Scale'].default_value<10:
  n.inputs['Scale'].default_value=3.4;n.inputs['Detail'].default_value=.8
# Preserve machinery task illumination; reduce broad central floor fill.
for name,power in [('Rear hall practical photometric area',210),('Entry fluorescent photometric area',135)]:
 bpy.data.lights[name].energy=power
# The ten C cameras remain fixed. W02 supplementary lens now contains full sign.
bpy.data.objects['W02_Waste_Approach'].data.lens=22
# Close swept curve ends. Surface decals and font tessellation remain intentional.
for o in s.objects:
 if o.type=='CURVE' and o.data.bevel_depth>0:o.data.use_fill_caps=True
s['revision']=a.revision;s['final_art_pass']='final_adjustments.py'
s['authoring_sources']=json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in Path(__file__).parent.glob('*.py')})
bpy.context.view_layer.update()
out=ROOT/'blender/electrical_room.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
receipt=ROOT/'production/checkpoints'/a.revision;receipt.mkdir(parents=True,exist_ok=True)
for f in Path(__file__).parent.glob('*.py'):(receipt/f.name).write_bytes(f.read_bytes())
data={'section':'electrical-room','revision':a.revision,'stage':'full','objects':len(s.objects),'mesh_objects':sum(o.type=='MESH' for o in s.objects),'materials':len(bpy.data.materials),'source_sha256':s['source_sha256'],'authoring_sources':json.loads(s['authoring_sources']),'pipeline':['build_room.py --stage full','final_adjustments.py'],'cameras':[{'name':o.name,'location':list(o.location),'rotation_euler':list(o.rotation_euler),'lens_mm':o.data.lens} for o in s.objects if o.type=='CAMERA']}
(receipt/'build_manifest.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print('FINAL_ART_PASS_SAVED',a.revision,out)
