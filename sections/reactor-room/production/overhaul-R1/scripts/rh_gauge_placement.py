"""Move complete turbine gauges within their panel to clear the wall trim."""
import json
import bpy
import bmesh
from mathutils import Vector
from rh_blind_covers import components


def build():
    scene = bpy.context.scene
    assert 'rh_gauge_placement' not in scene
    expected = {'STEEL':1,'BRASS':1,'WHITE':1,'BLACK':10,'RED':1,'GLASS':1}
    vertex_counts = {'STEEL':32,'BRASS':64,'WHITE':28,'BLACK':160,'RED':16,'GLASS':28}
    moves = [(Vector((9.77,-5.865,1.40)),Vector((-.12,0,0))),
             (Vector((10.13,-5.865,1.40)),Vector((-.20,0,0)))]
    axis = Vector((0,-1,0))
    changes = {}
    for material,count in expected.items():
        obj = bpy.data.objects['RH stations east '+material]
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        islands = list(components(bm))
        changed = []
        for center,offset in moves:
            selected = []
            for island in islands:
                world = [obj.matrix_world @ vertex.co for vertex in island]
                axial = [(point-center).dot(axis) for point in world]
                radial = [((point-center)-axis*(point-center).dot(axis)).length for point in world]
                # The inherited bevel reaches 70.657 mm on the nominal
                # 70 mm brass ring. Use its measured complete envelope.
                radius_limit = .0708 if material == 'BRASS' else .07001
                if min(axial)>=-.03001 and max(axial)<=.02951 and max(radial)<=radius_limit:
                    selected.append(island)
            assert len(selected)==count, (material,list(center),len(selected),count)
            assert sum(len(island) for island in selected)==vertex_counts[material]
            local_offset = obj.matrix_world.to_3x3().inverted() @ offset
            for island in selected:
                for vertex in island:
                    vertex.co += local_offset
                    changed.append(vertex.index)
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()
        changes[obj.name] = sorted(changed)
    record = {'moves':[{'old_center':list(center),'offset':list(offset),
                         'new_center':list(center+offset)} for center,offset in moves],
              'changed_vertex_indices':changes,
              'scope':'Only complete gauge components move; same panel, radius, axes, layers and materials.'}
    scene['rh_gauge_placement'] = json.dumps(record)
    bpy.context.view_layer.update()
    print('GAUGE_PLACEMENT', {name:len(ids) for name,ids in changes.items()},flush=True)
