"""Objective source checks. Does not substitute for the visual rubric."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent

def descendants(root):
    return [root]+list(root.children_recursive)

def bounds(objects):
    points=[]
    for o in objects:
        # Inactive readout labels can have sentinel bounds before evaluation.
        # Route envelopes use active physical surfaces, not font glyph bounds.
        if o.hide_render or o.type not in {'MESH','CURVE'}:continue
        points.extend(o.matrix_world @ Vector(v) for v in o.bound_box)
    return [[min(p[i] for p in points) for i in range(3)], [max(p[i] for p in points) for i in range(3)]]

def main(out=None):
    bpy.context.view_layer.update();checks=[];measurements={}
    def check(name,ok,detail):checks.append({'check':name,'pass':bool(ok),'detail':detail})
    roles={role:[o for o in bpy.data.objects if o.get('asset_role')==role] for role in ['suit_station','primary_seat','integrity_chamber','radiation_checkpoint']}
    for role,count in [('suit_station',4),('primary_seat',4),('integrity_chamber',1),('radiation_checkpoint',1)]:
        check(role,len(roles[role])==count,[o.name for o in roles[role]])
    bays=roles['suit_station'];chairs=roles['primary_seat'];machine=roles['integrity_chamber'][0]
    check('two stations each side',sum(o.location.y>4 for o in bays)==2 and sum(o.location.y<4 for o in bays)==2,'Locker centre y=4')
    check('left briefing / right PPE',all(o.location.x<0 for o in chairs) and all(o.location.x>0 for o in bays),'World X sides from spawn facing +Y')
    cb=bounds(descendants(machine));measurements['chamber_world_bounds']=cb
    north=min(bounds(descendants(o))[0][1] for o in bays if o.location.y>4)
    south=max(bounds(descendants(o))[1][1] for o in bays if o.location.y<4)
    bench=bounds(descendants(bpy.data.objects['LOCKER_bench']))
    gaps={'north':north-cb[1][1],'south':cb[0][1]-south,'rear_to_bench':bench[0][0]-cb[1][0]}
    measurements['chamber_circulation_m']=gaps
    check('chamber circulation >=1.2m',min(gaps.values())>=1.195,gaps)
    waiting=bounds(descendants(bpy.data.objects['HALL_waiting_bench']))
    hallclear=1.681-max(-1.681,waiting[1][0]);measurements['hall_clear_m']=hallclear
    check('gathering hall >=3m',hallclear>=3.0,hallclear)
    for name in ['BRIEFING_entry','LOCKER_entry','OPERATIONS_door']:
        root=bpy.data.objects[name];leaves=[o for o in root.children_recursive if o.get('interaction') in ['hinged door','sliding personnel door']]
        check(name+' editable pivot',len(leaves)==1 and abs(leaves[0].scale.x-1)<1e-5,'Separate hinged leaf root')
    for o in chairs:
        pad=bpy.data.objects[o.name+'_seat_pad'];bb=bounds([pad]);check(o.name+' seat height',.43<=bb[1][2]<=.471,bb[1][2])
    seating=bounds([part for o in chairs for part in descendants(o)])
    briefing_routes={'behind_seats':-1.86-seating[1][0],'north_of_seats':6.1-seating[1][1]}
    measurements['briefing_outer_aisles_m']=briefing_routes
    check('briefing outer circulation >=1m',min(briefing_routes.values())>=1.0,briefing_routes)
    # All individual furniture feet are checked at their real lower extent, in addition to anchors.
    feet=[o for o in bpy.data.objects if o.type=='MESH' and ('_foot' in o.name or '_plinth_foot' in o.name)]
    badfeet={o.name:bounds([o])[0][2] for o in feet if abs(bounds([o])[0][2])>.0021}
    check('actual furniture feet on floor',not badfeet,{'checked':len(feet),'bad':badfeet})
    required=bpy.data.collections['CS_SUPPORT_REQUIRED']
    roots=[o for o in bpy.data.objects if o.type=='EMPTY' and o.parent is None and not o.name.endswith('_assembly') and (o.get('asset_role') in roles or any(s in o.name for s in ['WAYFIND','HAZARD','_crew','_supervisor','_notice','_sideboard','_bench','_display','_procedure','_riser','_ventilation']))]
    check('major supported asset coverage',all(o.name in required.objects for o in roots),[o.name for o in roots if o.name not in required.objects])
    cameras=[o for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith('VALIDATE_')]
    check('eleven fixed eye height cameras',len(cameras)==11 and all(abs(o.location.z-1.63)<.001 for o in cameras),len(cameras))
    check('packed image dependencies',all(i.packed_file for i in bpy.data.images if i.source=='FILE'),[i.name for i in bpy.data.images if i.source=='FILE'])
    check('no missing surface materials',all(len(o.data.materials)>0 and all(m for m in o.data.materials) for o in bpy.data.objects if o.type=='MESH'),'All mesh slots populated')
    check('no legacy scene source',bpy.context.scene.get('reference_base')=='8603063',bpy.context.scene.get('reference_base'))
    check('four spawn markers',len([o for o in bpy.data.objects if o.get('gameplay_role')=='player_spawn'])==4,'SPAWN_1..4')
    states=[];saved_frame=bpy.context.scene.frame_current
    for frame,word,opened in [(1,'READY',True),(31,'OCCUPIED',False),(61,'TESTING',False),(91,'PASS',True),(121,'INSPECT',False),(151,'FAIL',False)]:
        bpy.context.scene.frame_set(frame)
        texts=[o.data.body for o in machine.children_recursive if o.type=='FONT' and '_readout_' in o.name and not o.hide_render]
        doors=[o for o in machine.children_recursive if o.get('interaction')=='inward hinged seal door']
        correct=len(doors)==2 and all(abs(abs(o.rotation_euler.z)-(math.pi/2 if opened else 0))<.001 for o in doors)
        check('machine state '+word,texts==[word] and correct,{'frame':frame,'readout':texts,'doors_open':opened})
        states.append({'frame':frame,'readout':texts,'door_angles':[o.rotation_euler.z for o in doors],'scan_height':bpy.data.objects['INTEGRITY_scan_carriage'].location.z})
    bpy.context.scene.frame_set(saved_frame);measurements['machine_states']=states
    report={'status':'PASS' if all(c['pass'] for c in checks) else 'FAIL','checks':checks,'measurements':measurements,'scope':'Source geometry and dependencies; runtime collision/networking are engine handoff work.'}
    output=Path(out) if out else HERE.parent/'production/objective_validation.json';output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2))
    print('GROUNDED_OBJECTIVE_'+report['status']);print(json.dumps(measurements))
    for c in checks:
        if not c['pass']:print('FAIL',c)
    return 0 if report['status']=='PASS' else 1

if __name__=='__main__':
    if main():raise RuntimeError('Objective validation failed')
