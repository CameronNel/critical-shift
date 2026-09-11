import json
from pathlib import Path
R=Path(__file__).resolve().parent;data=json.loads((R/'equipment-measured.json').read_text())
lines=['# Evaluated equipment envelopes','', 'Metres; measured from saved Blender geometry including projecting hardware. These are assembly envelopes, not load or shielding ratings.','', '| ID | Type | Origin X,Y,Z | Envelope W × D × H | Min X,Y,Z | Max X,Y,Z |','|---|---|---|---|---|---|']
def v(a):return ', '.join(f'{x:.3f}' for x in a)
for e in data:lines.append(f"| {e['id']} | {e['type']} | {v(e['origin'])} | {' × '.join(f'{e['max'][k]-e['min'][k]:.3f}' for k in range(3))} | {v(e['min'])} | {v(e['max'])} |")
lines+=['','The jib envelope includes the overhead parked boom; its floor obstruction is the aligned 0.8 × 0.8 pedestal. Dry crates have a 2.15 × 0.70 × 1.10 nominal body, with hardware outside that body. The quarantine container retains its larger interior and open inspection lid.','', 'The dimensioned floorplan uses these evaluated plan envelopes. Separate dashed service boxes and swept body checks establish the working space.']
(R/'EQUIPMENT_DIMENSIONS.md').write_text('\n'.join(lines),encoding='utf-8')
