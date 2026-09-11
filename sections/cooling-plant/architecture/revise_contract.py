"""CP-A03: measured neighbour stub ownership and full-room contract corrections."""
import json,math
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'interface.json'
d=json.loads(p.read_text(encoding='utf-8'))
d['revision']='CP-A03'
d['status']='CP-A03 full-room local interface contract. Acceptance evidence is recorded separately under production/technical and production/critics. Neighbours are not assembled.'
door=d['portals'][1]
door['threshold'][1]=9.9
door['clear_bounds']['min'][1]=9.9;door['clear_bounds']['max'][1]=10.11
leaf=door['door'];leaf['hinge'][1]=10.145;leaf['closed_leaf_end'][1]=10.145;leaf['open_leaf_end'][1]=11.365
leaf['swept_volume']['centre_xy'][1]=10.145
leaf['swept_volume']['conservative_bounds']['min'][1]=10.11
leaf['swept_volume']['conservative_bounds']['max'][1]=11.40
leaf['hardware_note']='Full 1.22m leaf on rear-mounted hinges, partition moved 0.1m forward; open leaf ends at Y11.365 before bench standing strip Y11.4.'
for v in d['keep_clear_volumes']:
    if v['id']=='KC-HX-HOIST':v['permitted_object_names']=['HX dedicated hoist']
    if v['id']=='KC-ALCOVE-DOOR':
        v['bounds']=leaf['swept_volume']['conservative_bounds']
        v['shared_space_note']='Conservative swing ends at Y11.40, touching but not occupying bench standing strip. Open leaf ends at Y11.365. Saved-scene geometry and swept route checks are separate evidence.'
    if v['id']=='KC-ALCOVE-APPROACH':v['bounds']['max'][1]=9.9
for e in d['equipment_envelopes']:
    if e['id']=='CP-WORKBENCH':e['source_alignment']='Worktop and upstand trimmed to Y12.3..13; saved-scene evaluated geometry audit verifies the authored envelope.'
    if e['id']=='CP-RESTART':
        e['bounds']['min']=[4.85,1.62,.70];e['bounds']['max'][2]=1.74
    if e['id']=='CP-HX-01':
        e['bounds']['min'][1]=4.49
        e['utility_object_names']=['HX primary inlet neck','HX primary inlet flange cast flange','HX primary inlet flange mating flange','HX primary inlet flange gasket']
for part in d['partitions']:
    if part['id'].startswith('CP-ALCOVE-FRONT'):
        part['bounds']['min'][1]=9.9;part['bounds']['max'][1]=10.06;part['bounds']['max'][2]=3.3
    if part['id']=='CP-ALCOVE-SIDE':part['bounds']['min']=[-1.76,10.06,0];part['bounds']['max']=[-1.6,13,3.3]
r=d['proposed_reactor_connection']
t=8.4+3.7/math.sqrt(2)
r['translation_xyz']=[t,-t,0]
r['authority']='Current reactor build_scene.py portal construction: 3.7m outward link stub from SE threshold. Saved-scene measurement recorded separately.'
r['reactor_hall_threshold_xyz']=[8.4,-8.4,0]
r['reactor_owned_stub_length_m']=3.7
r['reactor_portal_endpoints_xy']=[[t+2.5/math.sqrt(2),-t+2.5/math.sqrt(2)],[t-2.5/math.sqrt(2),-t-2.5/math.sqrt(2)]]
r['coordination_notes']=['Cooling starts at the OUTER end of reactor-owned 3.7m stub, not at reactor hall threshold. Proposed Rz -135 degrees is not applied to either scene.','Reactor static closed door assembly still blocks its stub. Only its owner/integrator may open or replace it.','Fuel Corridor S01_PLANT is a reserved shared header, not a verified installed Cooling connection. Current coherent topology is refinery > Fuel Corridor > reactor > Cooling.','No installed remote utility endpoint or whole-map fit is claimed.']
d['coordination_pending']=['Assemble and validate neighbouring transforms without overlapping their owned connector stubs.','Reactor owner/integrator must resolve its static closed cooling door.','Connect remote primary/secondary water, reserve power and drainage systems; coordinates below describe local sockets.','Fuel Corridor S01_PLANT final destination and global facility placement remain unresolved.']
for socket in d['utilities']['sockets']:
    if socket['id']=='CP-SECONDARY-WATER-01':socket['position'][2]=3.0
    if socket['id']=='CP-SECONDARY-WATER-02':socket['position'][2]=3.3
    if socket['id']=='CP-DRAIN-OUT':
        socket.update(installed=True,source_object='contained drain collector',source_endpoint='end',validation_note='Local buried collector installed; remote drain continuation remains unassembled.')
p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
print('CP-A03 contract written')
