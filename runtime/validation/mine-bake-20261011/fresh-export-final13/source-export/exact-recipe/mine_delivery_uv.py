"""Weld temporary UV proxies; transfer corner UVs without editing delivered geometry."""
import math
import bpy
import numpy as np


def surface_density(obj, layer_name, size):
    """Measure delivered texture area against physical triangle area."""
    mesh = obj.data
    mesh.calc_loop_triangles()
    vertices = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
    mesh.vertices.foreach_get('co', vertices)
    transform = np.asarray(obj.matrix_world, dtype=np.float64)
    world = vertices.reshape((-1, 3)) @ transform[:3, :3].T + transform[:3, 3]
    indices = np.empty(len(mesh.loop_triangles) * 3, dtype=np.int32)
    corners = np.empty_like(indices)
    mesh.loop_triangles.foreach_get('vertices', indices)
    mesh.loop_triangles.foreach_get('loops', corners)
    points = world[indices.reshape((-1, 3))]
    areas = np.linalg.norm(np.cross(points[:, 1] - points[:, 0], points[:, 2] - points[:, 0]), axis=1) / 2
    values = np.empty(len(mesh.loops) * 2, dtype=np.float32)
    mesh.uv_layers[layer_name].data.foreach_get('uv', values)
    uv = values.reshape((-1, 2))[corners.reshape((-1, 3))]
    a, b = uv[:, 1] - uv[:, 0], uv[:, 2] - uv[:, 0]
    uv_areas = np.abs(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]) / 2
    sampled = areas > 1e-9
    area, coverage = float(areas[sampled].sum()), float(uv_areas[sampled].sum())
    density = size * math.sqrt(coverage / area) if area else 0
    return {'node': obj.name, 'worldArea': area, 'uvArea': coverage,
            'pixelsPerMetre': density, 'atlasSize': size}


def unwrap(objects, layer_name, margin, world_vertices=False):
    proxies=[];records=[]
    for original in objects:
        vertices=[];lookup={};indices=[]
        for vertex in original.data.vertices:
            p=vertex.co.copy() if world_vertices else original.matrix_world @ vertex.co
            key=tuple(round(v*1000000) for v in p)
            if key not in lookup:lookup[key]=len(vertices);vertices.append(tuple(p))
            indices.append(lookup[key])
        faces=[];source_faces=[];degenerate=[]
        for polygon in original.data.polygons:
            face=[indices[i] for i in polygon.vertices]
            if len(set(face))<3 or len(set(face))!=len(face):
                degenerate.append(polygon);continue
            faces.append(face);source_faces.append(polygon)
        mesh=bpy.data.meshes.new('CS_UV_PROXY');mesh.from_pydata(vertices,[],faces);mesh.update()
        if len(mesh.polygons)!=len(source_faces):raise ValueError('UV proxy changed face inventory')
        node=bpy.data.objects.new('CS_UV_PROXY',mesh);bpy.context.scene.collection.objects.link(node)
        node.hide_render=True;mesh.uv_layers.new(name=layer_name)
        proxies.append(node);records.append((original,node,source_faces,degenerate))
    bpy.ops.object.select_all(action='DESELECT')
    for node in proxies:node.select_set(True)
    bpy.context.view_layer.objects.active=proxies[0]
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=margin,area_weight=0,
        correct_aspect=False,scale_to_bounds=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    for original,node,source_faces,degenerate in records:
        target=original.data.uv_layers[layer_name]
        source=node.data.uv_layers[layer_name]
        for polygon,proxy in zip(source_faces,node.data.polygons):
            if len(polygon.loop_indices)!=len(proxy.loop_indices):raise ValueError('UV proxy changed corner count')
            for old,new in zip(polygon.loop_indices,proxy.loop_indices):target.data[old].uv=source.data[new].uv
        # Zero-area source faces remain in the delivered mesh; they have no sampled surface.
        for polygon in degenerate:
            for loop in polygon.loop_indices:target.data[loop].uv=(.5,.5)
        values=np.empty(len(original.data.loops)*2,dtype=np.float32);target.data.foreach_get('uv',values)
        if not np.isfinite(values).all() or values.min()<0 or values.max()>1.001:raise ValueError('Invalid proxy UVs')
        print('CS_MINE_UV_PROXY',original.name,len(original.data.vertices),'to',len(node.data.vertices),flush=True)
        mesh=node.data;bpy.data.objects.remove(node,do_unlink=True);bpy.data.meshes.remove(mesh)
