"""Seat the nine retained station glass disks in closed retaining bezels."""
import json
import math
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from rh_gauge_information import STATIONS
import rh_stlib as S
import rh_support_registry as SUPPORT

NAME = 'RH refine gauge glass retainers'
OWNER = 'gauge glass seats'


def build():
    assert NAME not in bpy.data.objects
    collection = bpy.data.objects['Vent label.legend'].users_collection[0]
    bm = bmesh.new()
    SUPPORT.reset(OWNER)
    records = []
    for tag,position,normal,R,group in STATIONS:
        c = Vector(position)
        a,u,v = S.basis(normal)
        glass = bpy.data.objects['RH stations '+group+' GLASS']
        brass = bpy.data.objects['RH stations '+group+' BRASS']
        # Match the actual disk's polygon phase/count, including Kit's segment
        # reduction. A guessed circular bore can cut across polygon corners.
        angles = set()
        for vertex in glass.data.vertices:
            delta = glass.matrix_world @ vertex.co - c
            axial = delta.dot(a)
            radial = delta-a*axial
            if abs(axial-.0285)<.00001 and abs(radial.length-R*.84)<.00001:
                angles.add(round(math.atan2(radial.dot(v),radial.dot(u)),5))
        angles = sorted(angles)
        assert len(angles)>=8, (tag,len(angles))
        # Rear bearing on the existing brass face; a two-sided groove captures
        # the retained glass at its actual .0275/.0285 m planes. Its polygonal
        # outer edge has 150 micrometres of radial clearance in the groove.
        profile = [(.016,R*.86),(.016,R*.985),(.0295,R*.985),
                   (.031,R*.96),(.031,R*.82),(.0285,R*.82),
                   (.0285,R*.84+.00015),(.0275,R*.84+.00015),
                   (.0275,R*.82),(.0265,R*.82),(.0265,R*.86)]
        rows = [[bm.verts.new(c+a*axial+(u*math.cos(t)+v*math.sin(t))*radius)
                 for t in angles] for axial,radius in profile]
        for i,row in enumerate(rows):
            following = rows[(i+1)%len(rows)]
            for j in range(len(angles)):
                k = (j+1)%len(angles)
                bm.faces.new((row[j],row[k],following[k],following[j]))
        target = brass.name
        tree = BVHTree.FromPolygons([brass.matrix_world @ p.co for p in brass.data.vertices],
                                   [list(p.vertices) for p in brass.data.polygons])
        back = []
        for t in angles[::max(1,len(angles)//4)]:
            p = c+a*.016+(u*math.cos(t)+v*math.sin(t))*(R*.92)
            hit,_,_,_ = tree.ray_cast(p+a*.002,-a,.004)
            assert hit is not None and (hit-p).length<.00001, (tag,hit,p)
            back.append(p)
        SUPPORT.register(OWNER,tag+' bezel bearing',NAME,target,back,-a,'wall',gap=.0001)
        for axial,direction,side in ((.0275,a,'rear'),(.0285,-a,'front')):
            anchors = [c+a*axial+(u*math.cos(t)+v*math.sin(t))*(R*.83)
                       for t in angles[::max(1,len(angles)//4)]]
            SUPPORT.register(OWNER,tag+' glass '+side+' seat',NAME,glass.name,anchors,direction,'wall',gap=.0001)
        records.append({'tag':tag,'center':list(c),'axis':list(a),'radius':R,
                        'segments':len(angles),'profile':profile,'glass':glass.name,
                        'rear_bearing':target,'radial_groove_clearance_m':.00015})
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    assert all(edge.is_manifold for edge in bm.edges)
    assert bm.calc_volume(signed=True)>0
    mesh = bpy.data.meshes.new(NAME)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(NAME,mesh)
    collection.objects.link(obj)
    mesh.materials.append(bpy.data.objects['RH stations east BRASS'].data.materials[0])
    bpy.context.scene['rh_gauge_glass_seats'] = json.dumps(records)
    bpy.context.view_layer.update()
    print('GAUGE_GLASS_SEATS',len(records),'closed bezels; measured disk phases; retained glass/needles',flush=True)
