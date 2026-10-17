"""Write where each room sits in the combined map, for the Unity importer (Critical Shift > Rooms > Import Baked Map):

    blender --background --factory-startup sections/facility-assembly/combined/combined_map.blend --python sections/facility-assembly/unity/map_placement.py

Reads the map's ROOM_<room> instancers (the compact layout, build_compact_map.py) and writes map/map_placement.json: per room, the Blender map-frame
location and Z rotation that carry its room frame (where bake_all.ps1 -Map bakes it) into the map. The connector piece is baked in the map frame
already, so it is placed at the origin. Renders nothing, so no device is needed."""
import bpy, json, math, os
from mathutils import Matrix

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'map', 'map_placement.json')
rooms = {}
for o in sorted(bpy.data.objects, key=lambda o: o.name):
    if o.instance_type != 'COLLECTION' or not o.name.startswith('ROOM_') or not o.instance_collection: continue
    m = o.matrix_world @ Matrix.Translation(-o.instance_collection.instance_offset); e = m.to_euler()   # the collection's instance offset is part of the placement
    if abs(e.x) > 1e-4 or abs(e.y) > 1e-4 or any(abs(s - 1) > 1e-4 for s in m.to_scale()):
        raise SystemExit('%s has tilt or scale; the importer only carries location and Z rotation' % o.name)
    rooms[o.name[len('ROOM_'):]] = dict(collection=o.instance_collection.name, location=[round(v, 4) for v in m.translation],
                                        rotation_z_deg=round(math.degrees(e.z), 4))
rooms['map-connections'] = dict(collection='(connectors, signs, evacuation; baked in the map frame)', location=[0.0, 0.0, 0.0], rotation_z_deg=0.0)
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(dict(source='sections/facility-assembly/combined/combined_map.blend', frame='Blender map frame: metres, +Z up. Unity: (x, y, z) -> (-x, z, -y), '
               'Z rotation r -> Y rotation -r', rooms=rooms), open(out, 'w'), indent=1)
print('PLACEMENT', len(rooms), 'rooms ->', out)
