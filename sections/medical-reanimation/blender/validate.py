"""Scene-space contact and source integrity checks; executable on cold reopen."""
from mathutils import Vector
import hashlib, datetime
report={'revision':scene['revision'],'blender_version':bpy.app.version_string,'checks':{},'support_contacts':[],'limitations':['Static Blender asset validation; runtime ragdoll, multiplayer and navigation are engine handoff tasks.']}
checks=report['checks']
checks['metric_units']=scene.unit_settings.system=='METRIC'
checks['ten_cameras']=all(n in bpy.data.objects for n in CAMERAS if n!='C00_slice')
checks['materials_present']=all(len(o.data.materials)>0 for o in scene.objects if o.type=='MESH')
checks['no_external_libraries']=len(bpy.data.libraries)==0
checks['no_external_images']=all(i.packed_file or i.source=='GENERATED' for i in bpy.data.images if i.type!='RENDER_RESULT')
checks['finite_geometry']=all(math.isfinite(v) for o in scene.objects for row in o.matrix_world for v in row)
for o in scene.objects:
    if 'support_target' not in o:continue
    target=bpy.data.objects.get(o['support_target']);p=Vector(o['support_anchor']);direction=Vector(o['support_direction']).normalized()
    hit=False;distance=None;angle=None
    if target:
        inv=target.matrix_world.inverted();start=p-direction*.03
        ok,loc,normal,index=target.ray_cast(inv@start,inv.to_3x3()@direction,distance=.20)
        if ok:
            worldloc=target.matrix_world@loc;distance=(worldloc-p).dot(direction)
            normal=(target.matrix_world.to_3x3().inverted().transposed()@normal).normalized()
            angle=math.degrees(math.acos(min(1,max(-1,normal.dot(-direction)))))
            hit=(-o['support_penetration_tolerance']-1e-5<=distance<=o['support_gap_tolerance']+1e-5 and angle<=12)
    report['support_contacts'].append({'object':o.name,'target':o['support_target'],'signed_gap_m':distance,'angle_deg':angle,'pass':hit})
checks['registered_contacts_pass']=all(c['pass'] for c in report['support_contacts'])
report['object_count']=len(scene.objects);report['mesh_count']=sum(o.type=='MESH' for o in scene.objects)
import importlib.util
spec=importlib.util.spec_from_file_location('medical_geometry_validation',ROOT/'blender/validate_geometry.py')
geometry_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(geometry_module)
report['geometry']=geometry_module.validate_geometry(scene)
for name,value in report['geometry']['checks'].items():checks['geometry_'+name]=value
report['base_mesh_triangles']=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in scene.objects if o.type=='MESH')
report['pass']=all(checks.values())
(out/'validation.json').write_text(json.dumps(report,indent=2))
print('MEDICAL_VALIDATION',json.dumps({'pass':report['pass'],'checks':checks,'failed_contacts':[c for c in report['support_contacts'] if not c['pass']]}),flush=True)
