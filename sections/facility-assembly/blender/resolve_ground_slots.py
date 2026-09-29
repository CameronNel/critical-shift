"""Resolve inherited object-level material overrides on the copied courtyard rocks."""
import bpy,json,hashlib,ctypes
from pathlib import Path
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runtime/out/environment/ground-finish';SRC=Path(bpy.data.filepath);MAIN=SRC.with_name('facility_environment.blend');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((OUT/'verification.json').read_text());assert sha(SRC)==r['candidate_sha256'] and sha(MAIN)==r['before_sha256'];slots=[]
for name in r['changed']:
 o=bpy.data.objects[name]
 if not name.startswith('CY | Existing boulder'):continue
 for i,slot in enumerate(o.material_slots):
  before=(slot.link,slot.material.name if slot.material else None);wanted=o.data.materials[i];assert wanted.name.startswith('GF | Mineral ')
  slot.link='DATA';slot.material=wanted;slots.append(dict(object=name,before=before,after=slot.material.name))
r['resolved_object_overrides']=slots;print('ROCK_SLOTS',json.dumps(slots),flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SRC),check_existing=False);r['candidate_sha256']=sha(SRC);(OUT/'verification.json').write_text(json.dumps(r,indent=2))
s=bpy.context.scene;s.camera=bpy.data.objects['GF CAMERA | mine-cliff-yard'];s.render.filepath=str(OUT/'mine-cliff-yard.png');bpy.ops.render.render(write_still=True);print('SLOTS_RESOLVED',flush=True)
