"""Blender scene edits only: reposition three review cameras and add task lights."""
import bpy,json
from mathutils import Vector

def apply(scene,rows):
    fixes={'CAM_06':((5.9,-12.6,3.7),(-.5,-3.5,1.85),23),'CAM_39':((8.2,17.35,1.21625),(10,18.5,.0375),30),'CAM_40':((8.25,24,1.1),(8.1,20.5,.9375),23)}
    changed=[]
    for row in rows:
        if row['id'] in fixes:
            position,target,lens=fixes[row['id']]
            row.update(position=position,target=target,lens=lens)
            camera=scene.objects[row['id']]
            camera.location=position
            camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
            camera.data.lens=lens
            camera['q50_view']=json.dumps(row)
            changed.append(row['id'])
    for sector,offset in [('A',Vector((2.85,0,0))),('C',Vector((-.15,-4,.1)))]:
        lights=[o for o in scene.objects if o.type=='LIGHT' and o.get('csm_sector')==sector and o.get('csm_min_stage')==1]
        if lights:continue
        parts=[o for o in scene.objects if (o.name.startswith('Q50_Old_task_lamp') or o.name.startswith('Q50_Excavation_practical')) and o.get('csm_sector')==sector and o.get('csm_min_stage')==2]
        for original in parts:
            obj=original.copy();obj.data=original.data.copy()
            original.users_collection[0].objects.link(obj)
            transform=original.matrix_world.copy();transform.translation+=offset;obj.matrix_world=transform
            metadata=json.loads(original['csm_meta']);metadata['min_stage']=1
            obj['csm_meta']=json.dumps(metadata);obj['csm_min_stage']=1;obj['csm_id']=obj.name
    for light in scene.objects:
        if light.type=='LIGHT' and light.name.startswith('Q50_Excavation_practical'):
            sector=light.get('csm_sector');stage=light.get('csm_min_stage')
            if sector=='C':light.data.energy=100 if stage==2 else 135
            elif sector=='A' and stage==1:light.data.energy=75
    scene['q50_cameras']=json.dumps(rows)
    bpy.context.view_layer.update()
    return {'corrected_camera_ids':changed,'reason':'Remove foreground obstructions from review views and illuminate previously unreadable shallow work areas.'}
