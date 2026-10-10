"""Move the complete steam gauge/tap clear of its wall penetration sleeve."""
import json
import bpy
import bmesh
from mathutils import Vector
from rh_blind_covers import components


def build():
    scene = bpy.context.scene
    assert 'rh_steam_gauge_placement' not in scene
    center = Vector((10.7,-3.8,6.4))
    axis = Vector((0,-1,0))
    offset = Vector((-.7,0,0))
    specifications = [
        ('gauge bezel GALV',.1359,.1901,.0541,1,28),
        ('gauge face WHITE',.1889,.1926,.0451,1,24),
        ('gauge needle BLACK',.1929,.1951,.0362,1,8),
        ('valve body IRON',.0439,.1381,.0201,2,32),
    ]
    changes = {}
    for suffix,lower,upper,radius,count,vertex_count in specifications:
        obj = bpy.data.objects['RH services R2 PIPING '+suffix]
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        selected = []
        for island in components(bm):
            points = [obj.matrix_world @ vertex.co for vertex in island]
            axial = [(point-center).dot(axis) for point in points]
            radial = [((point-center)-axis*(point-center).dot(axis)).length for point in points]
            if min(axial)>=lower and max(axial)<=upper and max(radial)<=radius:
                selected.append(island)
        assert len(selected)==count and sum(len(island) for island in selected)==vertex_count, (suffix,len(selected))
        local_offset = obj.matrix_world.to_3x3().inverted() @ offset
        ids = []
        for island in selected:
            for vertex in island:
                vertex.co += local_offset
                ids.append(vertex.index)
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()
        changes[obj.name] = sorted(ids)
    scene['rh_steam_gauge_placement'] = json.dumps({
        'old_pipe_tap':list(center),'new_pipe_tap':list(center+offset),
        'offset':list(offset),'changed_vertex_indices':changes,
        'scope':'Complete gauge, pointer, stem and union move along the same straight bare pipe. Main pipe, wall sleeve, gate valve and named ports remain intact.'})
    bpy.context.view_layer.update()
    print('STEAM_GAUGE_PLACEMENT',{name:len(ids) for name,ids in changes.items()},flush=True)
