"""Restore readable stylized shaded facades without losing R16 non-RT quality."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'production/spawn-exterior-review'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_spawn_concept02_R16.blend'),load_ui=False)
s=bpy.context.scene
for ob in s.objects:
 if ob.type!='LIGHT':continue
 if ob.name=='S01 broad exterior skylight':ob.data.energy=5000
 elif ob.name=='S01 South sky fill':ob.data.energy=2200
 elif ob.name in ('S01 East sky fill','S01 West sky fill'):ob.data.energy=1500
 if ob.name=='A10 afternoon sun':ob.data.angle=.12
s.view_settings.look='AgX - Medium High Contrast'
s.eevee.shadow_resolution_scale=1.0
s.name='FACILITY_SPAWN_CONCEPT02_R17'
dest=R/'blender/facility_spawn_concept02_R17.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
b=json.loads((O/'BUILD_R16.json').read_text());b.update(revision='R17',file=str(dest),lighting_correction='Restored broad stylized fill for readable shaded facades; sun angle .12 radians. Retained baked R16 indirect cache; fills are direct-only and not rebaked. RT disabled.');b['render_quality']['artificial_sky_fill_lights_disabled']=False
b['fill_lights']={o.name:o.data.energy for o in s.objects if o.type=='LIGHT' and o.name.startswith('S01 ') and ('sky fill' in o.name or 'skylight' in o.name)}
(O/'BUILD_R17.json').write_text(json.dumps(b,indent=2));print('R17_SAVED',flush=True)
