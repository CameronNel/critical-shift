"""Printed range/unit scales on the sixteen retained pressure-gauge faces.

The 0–10 bar scale is authored instrument artwork, not a runtime pressure model.
Existing pointers, housings and glass remain unchanged.
"""
import json
import math
import bpy
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
import rh_stlib as S
import rh_support_registry as SUPPORT

NAME = 'RH refine gauge calibration ink'
OWNER = 'gauge calibration'
STATIONS = [
    ('coolant pump', (-3.85,-8.95,1.02), (0,1,0), .125, 'south'),
    ('EC-1', (3.28,-9.16,1.49), (0,1,0), .075, 'south'),
    ('EC-2', (1.78,-9.16,1.49), (0,1,0), .075, 'south'),
    ('pool sample', (1.60,-3.74,1.14), (0,-1,0), .085, 'south'),
    ('turbine left', (9.65,-5.865,1.40), (0,-1,0), .070, 'east'),
    ('turbine right', (9.93,-5.865,1.40), (0,-1,0), .070, 'east'),
    ('turbine oil', (8.975,-2.60,1.66), (-1,0,0), .095, 'east'),
    ('steam riser', (10.27,-2.58,2.28), (-1,0,0), .065, 'east'),
    ('waste cask', (7.045-.071/math.sqrt(2),7.645-.071/math.sqrt(2),1.64), (-.7071,-.7071,0), .080, 'east'),
]
PIPING = [
    ('coolant chain', (2.55,-10.0905,3.9), (0,1,0)),
    ('EC-1 injection', (3.30,-10.66,1.1925), (0,0,1)),
    ('EC-2 injection', (1.80,-10.66,1.1925), (0,0,1)),
    ('pump discharge', (-2.75,-9.0,2.450501), (0,0,1)),
    ('steam supply', (10.00,-3.9925,6.400001), (0,-1,0)),
    ('waste vent', (7.695106,8.104894,4.2), (.7071,-.7071,0)),
    ('fire main', (-2.8,10.088501,8.900002), (0,-1,0)),
]


def build():
    scene = bpy.context.scene
    assert NAME not in bpy.data.objects and 'rh_gauge_information' not in scene
    collection = bpy.data.objects['Vent label.legend'].users_collection[0]
    receivers = {}
    def receiver(name):
        if name not in receivers:
            obj = bpy.data.objects[name]
            receivers[name] = BVHTree.FromPolygons(
                [obj.matrix_world @ v.co for v in obj.data.vertices],
                [list(f.vertices) for f in obj.data.polygons])
        return receivers[name]
    vertices, faces, records = [], [], []
    SUPPORT.reset(OWNER)
    def merge(points, polygons):
        base = len(vertices)
        vertices.extend([list(p) for p in points])
        faces.extend([tuple(base+i for i in polygon) for polygon in polygons])
    def label(body, position, normal, size):
        curve = bpy.data.curves.new('RH gauge temporary', 'FONT')
        curve.body = body
        curve.size = size
        curve.align_x = curve.align_y = 'CENTER'
        curve.resolution_u = 8
        temp = bpy.data.objects.new('RH gauge temporary', curve)
        collection.objects.link(temp)
        # Keep text upright on wall-facing dials; use a stable frame on top dials.
        a = Vector(normal).normalized()
        if abs(a.z) < .01:
            rotation = Matrix.Rotation(math.atan2(a.y,a.x)+math.pi/2,4,'Z') @ Matrix.Rotation(math.pi/2,4,'X')
        else:
            rotation = a.to_track_quat('Z','Y').to_matrix().to_4x4()
        transform = Matrix.Translation(position) @ rotation
        bpy.context.view_layer.update()
        mesh = bpy.data.meshes.new_from_object(temp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        points = [transform @ v.co for v in mesh.vertices]
        merge(points, [list(f.vertices) for f in mesh.polygons])
        bpy.data.objects.remove(temp,do_unlink=True)
        bpy.data.curves.remove(curve)
        bpy.data.meshes.remove(mesh)
        return points
    gauges = [(tag,Vector(c)+Vector(n).normalized()*.0165,n,R,'RH stations '+group+' WHITE',False)
              for tag,c,n,R,group in STATIONS]
    service_names = [o.name for o in bpy.data.objects if o.name.endswith('gauge face WHITE')]
    assert len(service_names) == 1, service_names
    gauges += [(tag,Vector(c),n,.045/.84,service_names[0],True) for tag,c,n in PIPING]
    for tag,nominal,normal,R,target,needs_ticks in gauges:
        a,u,v = S.basis(normal)
        tree = receiver(target)
        actual,hit_normal,index,distance = tree.ray_cast(nominal+a*.025,-a,.05)
        assert actual is not None and (actual-nominal).length < .0001, (tag,actual,nominal)
        assert abs(hit_normal.dot(a)) > .99, (tag,hit_normal,a)
        origin = actual + a*.0007
        anchors = []
        bodies = []
        for angle,body in ((-135,'0'),(0,'5'),(135,'10')):
            # This retained pointer is at +10 degrees. Offset its midscale
            # numeral toward the neighboring gap while keeping it nearest
            # the zero-degree tick, rather than printing underneath the needle.
            if tag == 'turbine right' and body == '5':
                angle = -12
            theta = math.radians(angle)
            position = origin + (u*math.cos(theta)+v*math.sin(theta))*(R*.48)
            points = label(body,position,a,R*.17)
            bodies.append(body)
            anchors.append(points[0])
            assert all(((p-origin)-a*(p-origin).dot(a)).length < R*.60 for p in points), tag
        points = label('bar',origin-u*(R*.32),a,R*.16)
        bodies.append('bar')
        anchors.append(points[0])
        assert all(((p-origin)-a*(p-origin).dot(a)).length < R*.60 for p in points), tag
        if needs_ticks:
            # The seven piping gauges had no ticks. Print nine matching divisions.
            for k in range(9):
                theta = math.radians(-135+k*33.75)
                radial = u*math.cos(theta)+v*math.sin(theta)
                tangent = a.cross(radial)
                inner = origin+radial*(R*.64)
                outer = origin+radial*(R*(.78 if k%2==0 else .72))
                width = R*.014
                merge([inner-tangent*width,outer-tangent*width,
                       outer+tangent*width,inner+tangent*width],[(0,1,2,3)])
        SUPPORT.register(OWNER,tag+' printed face',NAME,target,anchors,-a,'wall',gap=.0015)
        records.append({'tag':tag,'receiver':target,'face_center':list(actual),
                        'normal':list(a),'nominal_radius':R,'ink_gap_m':.0007,
                        'numerals':bodies,'range':[0,10],'unit':'bar','added_ticks':9 if needs_ticks else 0})
    mesh = bpy.data.meshes.new(NAME)
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    obj = bpy.data.objects.new(NAME,mesh)
    collection.objects.link(obj)
    mesh.materials.append(bpy.data.materials['RH refine moulded black polymer'])
    scene['rh_gauge_information'] = json.dumps(records)
    bpy.context.view_layer.update()
    print('GAUGE_INFORMATION',len(records),'faces; retained pointers/housings/glass; authored 0–10 bar scale',flush=True)
