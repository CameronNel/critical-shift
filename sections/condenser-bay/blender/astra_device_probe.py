"""Read the installed Cycles GPU capabilities without opening a room or rendering."""
import bpy,json
from pathlib import Path
p=bpy.context.preferences.addons['cycles'].preferences
p.compute_device_type='HIP'
p.refresh_devices()
report={'blender':bpy.app.version_string,'compute_device_type':p.compute_device_type,
        'devices':[{'name':d.name,'type':d.type,'id':d.id,'use':d.use} for d in p.devices],
        'backend_properties':{key:str(getattr(p,key)) for key in p.bl_rna.properties.keys() if any(t in key.lower() for t in ['hip','denois','raytrac'])}}
out=Path(__file__).resolve().parent.parent/'production/validation/gpu-device-probe.json'
out.write_text(json.dumps(report,indent=2)+'\n')
print('ASTRA_DEVICE_PROBE',json.dumps(report),flush=True)
