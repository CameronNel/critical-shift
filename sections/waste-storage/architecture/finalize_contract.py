"""Update owned contract from measured neighboring evidence; no neighbor writes."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=R/'interface.json';i=json.loads(p.read_text())
i['revision']='W22';i['status']='measured authored contract; see production/HANDOFF.md for independent acceptance'
for port in i['portals']:
    if port['id'] in ['WS_RECEIVING','WS_DISPATCH']:port['door']='rolling shutter with barrel and side guides; parked fully open'
    port['owner']='waste-storage'
i['receiving_alignment']={'status':'measured proposal, not an assembled scene','neighbor':'electrical-room','neighbor_portal':'D02','neighbor_source_sha256':'01447dce65a406afa84448e440176aefd37cdda702dc0a4cd51cee366c298dfd','waste_origin_in_electrical':[0,16.97,0],'rotation_z_degrees':0,'neighbor_exterior_y':16.65,'waste_receiving_exterior_y':-.32,'neighbor_opening_m':[2.4,2.7],'waste_opening_m':[3,3.2],'effective_joined_opening_m':[2.4,2.7],'floor_owner':'Electrical Waste seam slab owns X[-1.5,1.5], ElectricalY[16.4,16.97], topZ0. Waste removes its duplicate floor in local X[-1.5,1.5], Y[-.32,0]. Main Waste floor begins atY0.','wall_ownership':'Each module retains its own wall. Back-to-back exterior faces; no neighboring geometry altered.'}
i['personnel_swing_reservation']={'owner':'waste-storage leaf','hinge':[6.36,3.065,0],'closed_z_degrees':-90,'open_z_degrees':0,'conservative_external_xy':[[6.32,1.80],[7.65,3.14]],'status':'neighbor space unbound; reserved before network placement'}
i['internal_portals'][0]['hinge']=[-2.48,2.815,0];i['internal_portals'][0]['closed_z_degrees']=-90;i['internal_portals'][0]['open_z_degrees']=-180
i['implementation_decisions'] = ['Receiving/dispatch use rolling shutters, parked open. Personnel and booth use hinged leaves. Opening dimensions remain contract-owned.','Residue centers (-4.55,5.50,0),(-4.55,6.80,0),(-4.55,8.10,0). Dry centers(4.25,6.285,0),(4.25,7.315,0), opposed service faces; body depth .70m. Jib(-3.15,9.95,0),45deg parked boom, aligned fixed pedestal.','Intake bridge atZ4.48 crosses above exhaust topZ4.30; separate filter drop atX-5.38. Explicit process-joint checks retained.','Waste removes its duplicate receiving under-slab where measured Electrical seam owns the floor; unassembled exterior threshold support is not claimed.','Services terminate at exact owned exterior socket faces. Neighbor utilities remain unbound.','Cell gates use retracted side pockets; no fixed overhead obstruction crosses an entrance.']
i['equipment_manifest']='architecture/equipment-measured.json';i['runtime_implementation']='Editable geometry plus engine-host-owned hook anchors only; no gameplay runtime implemented in Blender.'
p.write_text(json.dumps(i,indent=2))

