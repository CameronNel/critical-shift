import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_walkthrough_A13_roof_services.blend'),load_ui=False)
r={}
for o in bpy.data.collections['06_LINKED_EXTERIORS'].objects:
 if not o.instance_collection:continue
 r[o.name]=[{'name':x.name,'loc':list(x.location),'dim':list(x.dimensions)} for x in o.instance_collection.objects if x.type=='MESH' and any(k in x.name.lower() for k in ['roof','cap','coping','ceiling'])][:30]
(R/'production/A14_ROOF_INSPECTION.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
