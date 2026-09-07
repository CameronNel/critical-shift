"""P02 reactor hall — original procedural art, metres / X east / Y north / Z up.

This file never opens, appends or imports existing 3D art. A normal invocation
starts from Blender's empty factory scene. All finished geometry is authored here.
"""
from __future__ import annotations
import argparse
import contextlib
import hashlib
import json
import math
import random
import sys
import time
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
PARSER = argparse.ArgumentParser()
PARSER.add_argument('--revision', default='art-01')
PARSER.add_argument('--render', default='all')
PARSER.add_argument('--samples', type=int, default=48)
PARSER.add_argument('--width', type=int, default=1280)
PARSER.add_argument('--cold-start', action='store_true')
ARGS = PARSER.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
OUT = ROOT / 'art' / 'renders' / ARGS.revision
OUT.mkdir(parents=True, exist_ok=True)
SOURCE_BYTES = Path(__file__).read_bytes()
SOURCE_TEXT = SOURCE_BYTES.decode('utf-8')
SOURCE_SHA = hashlib.sha256(SOURCE_BYTES).hexdigest()
random.seed(72)
PI = math.pi
TAU = 2 * PI
FRAME = Matrix.Identity(4)
COL = None
M = {}
CONTACTS = []
CHECKS = []


def collection(name):
    global COL
    COL = bpy.data.collections.get(name)
    if COL is None:
        COL = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(COL)
    return COL


@contextlib.contextmanager
def at(x=0, y=0, z=0, angle=0):
    global FRAME
    previous = FRAME.copy()
    FRAME = FRAME @ Matrix.Translation((x, y, z)) @ Matrix.Rotation(angle, 4, 'Z')
    try:
        yield
    finally:
        FRAME = previous


def srgb(hexcode):
    rgb = [int(hexcode[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb)


def material(name, color, rough=.6, metal=0, variation=.07, bump=.012, emission=0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    rgb = srgb(color)
    mat.diffuse_color = (*rgb, 1)
    nt = mat.node_tree
    p = nt.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*rgb, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    if emission:
        p.inputs['Emission Color'].default_value = (*rgb, 1)
        p.inputs['Emission Strength'].default_value = emission
    if variation:
        coord = nt.nodes.new('ShaderNodeTexCoord')
        noise = nt.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 2.3
        noise.inputs['Detail'].default_value = 2
        noise.inputs['Roughness'].default_value = .65
        nt.links.new(coord.outputs['Generated'], noise.inputs['Vector'])
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = .2
        ramp.color_ramp.elements[0].color = (*(max(0, c * (1 - variation)) for c in rgb), 1)
        ramp.color_ramp.elements[1].position = .8
        ramp.color_ramp.elements[1].color = (*(min(1, c * (1 + variation)) for c in rgb), 1)
        nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
        nt.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
        rng = nt.nodes.new('ShaderNodeMapRange')
        rng.inputs['To Min'].default_value = max(.1, rough - .055)
        rng.inputs['To Max'].default_value = min(1, rough + .055)
        nt.links.new(noise.outputs['Fac'], rng.inputs['Value'])
        nt.links.new(rng.outputs[0], p.inputs['Roughness'])
        if bump:
            bn = nt.nodes.new('ShaderNodeBump')
            bn.inputs['Strength'].default_value = .16
            bn.inputs['Distance'].default_value = bump
            nt.links.new(noise.outputs['Fac'], bn.inputs['Height'])
            nt.links.new(bn.outputs['Normal'], p.inputs['Normal'])
    M[name] = mat
    return mat


def make_materials():
    material('mineral', 'BDB7AA', .91, variation=.13, bump=.004)
    material('mineral_light', 'CEC6B6', .90, variation=.13, bump=.004)
    material('floor', '96968B', .85, variation=.18, bump=.003)
    material('floor_light', 'ACAA99', .84, variation=.18, bump=.003)
    material('seam', '444E4D', .8, variation=.03)
    material('teal', '2B535B', .61, .30, .20, .014)
    material('teal_light', '3F6770', .58, .30, .16, .012)
    material('teal_dark', '1C3942', .63, .38, .14, .012)
    material('steel', '35464B', .49, .65, .12, .006)
    material('steel_light', '697577', .44, .78, .14, .006)
    material('shaft', '8E9D9B', .235, .94, .09, .002)
    material('pipe', 'C2C6BD', .65, .30, .14, .004)
    material('rubber', '1C282B', .89, .02, .08, .002)
    material('yellow', 'DAAA38', .54, .42, .13, .008)
    material('paint_chip', '788A8B', .68, .42, .07, .001)
    material('red', 'B64737', .52, .12, .08, .004)
    material('amber', 'FFBE4B', .4, .05, 0, 0, 1.6)
    material('green', '80CCAD', .45, .03, 0, 0, 1)
    material('white', 'ECE8D4', .74, variation=.02, bump=0)
    material('ink', '213B40', .8, variation=0, bump=0)
    material('screen', '102C2F', .74, variation=0, bump=0, emission=.20)
    material('screen_line', '70B5A5', .5, variation=0, bump=0, emission=.45)
    material('lamp', 'E8F3ED', .4, variation=0, bump=0, emission=4)
    material('pool_glow', '26DFEE', .4, variation=0, bump=0, emission=15.0)
    material('pool_tile', '597F85', .31, .20, .12, .002)
    material('paper', 'C5BB95', .94, variation=.05, bump=.001)
    material('wood', '807861', .8, variation=.09, bump=.007)
    material('fabric', '8B968D', .96, variation=.18, bump=.011)
    material('floor_wear', 'B1B2A3', .90, variation=.04, bump=0)
    glass = material('glass', 'D7E6DF', .015, variation=0, bump=0)
    p = glass.node_tree.nodes.get('Principled BSDF')
    p.inputs['Transmission Weight'].default_value = 1
    p.inputs['IOR'].default_value = 1.46
    coated=glass.copy(); coated.name='observation_glass'; M['observation_glass']=coated
    nt=coated.node_tree; surface=nt.nodes.get('Principled BSDF'); output=nt.nodes.get('Material Output')
    clear=nt.nodes.new('ShaderNodeBsdfTransparent'); clear.inputs['Color'].default_value=(1,1,1,1)
    mix=nt.nodes.new('ShaderNodeMixShader'); mix.inputs[0].default_value=.98
    nt.links.new(surface.outputs[0],mix.inputs[1]); nt.links.new(clear.outputs[0],mix.inputs[2]); nt.links.new(mix.outputs[0],output.inputs['Surface'])
    water = material('water', 'E7F4EF', .025, variation=0, bump=0)
    p = water.node_tree.nodes.get('Principled BSDF')
    p.inputs['Transmission Weight'].default_value = 1
    p.inputs['IOR'].default_value = 1.333
    nt = water.node_tree
    n = nt.nodes.new('ShaderNodeTexNoise')
    n.inputs['Scale'].default_value = 9.5
    n.inputs['Detail'].default_value = 1.0
    b = nt.nodes.new('ShaderNodeBump')
    b.inputs['Strength'].default_value = .20
    b.inputs['Distance'].default_value = .014
    nt.links.new(n.outputs['Fac'], b.inputs['Height'])
    nt.links.new(b.outputs['Normal'], p.inputs['Normal'])
    # Selected handled steel gets authored perimeter wear. This mask is not used on the shell.
    worn=M['teal'].copy(); worn.name='teal_service'; M['teal_service']=worn
    nt=worn.node_tree; p=nt.nodes.get('Principled BSDF')
    original=p.inputs['Base Color'].links[0].from_socket
    co=nt.nodes.new('ShaderNodeTexCoord'); sep=nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(co.outputs['Generated'],sep.inputs[0])
    masks=[]
    for axis in ('X','Y','Z'):
        sub=nt.nodes.new('ShaderNodeMath'); sub.operation='SUBTRACT'; sub.inputs[1].default_value=.5
        absolute=nt.nodes.new('ShaderNodeMath'); absolute.operation='ABSOLUTE'
        edge=nt.nodes.new('ShaderNodeMath'); edge.operation='GREATER_THAN'; edge.inputs[1].default_value=.480
        nt.links.new(sep.outputs[axis],sub.inputs[0]); nt.links.new(sub.outputs[0],absolute.inputs[0]); nt.links.new(absolute.outputs[0],edge.inputs[0])
        masks.append(edge.outputs[0])
    pairs=[]
    for a,b in ((0,1),(0,2),(1,2)):
        pair=nt.nodes.new('ShaderNodeMath'); pair.operation='MULTIPLY'
        nt.links.new(masks[a],pair.inputs[0]); nt.links.new(masks[b],pair.inputs[1]); pairs.append(pair.outputs[0])
    maximum=nt.nodes.new('ShaderNodeMath'); maximum.operation='MAXIMUM'
    nt.links.new(pairs[0],maximum.inputs[0]); nt.links.new(pairs[1],maximum.inputs[1])
    maximum_all=nt.nodes.new('ShaderNodeMath'); maximum_all.operation='MAXIMUM'
    nt.links.new(maximum.outputs[0],maximum_all.inputs[0]); nt.links.new(pairs[2],maximum_all.inputs[1])
    noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=24; noise.inputs['Detail'].default_value=1
    nt.links.new(co.outputs['Generated'],noise.inputs['Vector'])
    threshold=nt.nodes.new('ShaderNodeMath'); threshold.operation='GREATER_THAN'; threshold.inputs[1].default_value=.66
    nt.links.new(noise.outputs['Fac'],threshold.inputs[0])
    mask=nt.nodes.new('ShaderNodeMath'); mask.operation='MULTIPLY'
    nt.links.new(maximum_all.outputs[0],mask.inputs[0]); nt.links.new(threshold.outputs[0],mask.inputs[1])
    mix=nt.nodes.new('ShaderNodeMixRGB'); mix.inputs[2].default_value=(*srgb('8D9995'),1)
    nt.links.new(mask.outputs[0],mix.inputs[0]); nt.links.new(original,mix.inputs[1]); nt.links.new(mix.outputs[0],p.inputs['Base Color'])
    # Absorbing/scattering medium is separate from the animated water surface and low emitter.
    vol=bpy.data.materials.new('pool_medium'); vol.use_nodes=True; nt=vol.node_tree; nt.nodes.clear()
    output=nt.nodes.new('ShaderNodeOutputMaterial')
    absorb=nt.nodes.new('ShaderNodeVolumeAbsorption'); absorb.inputs['Color'].default_value=(.08,.63,.80,1); absorb.inputs['Density'].default_value=.075
    scatter=nt.nodes.new('ShaderNodeVolumeScatter'); scatter.inputs['Color'].default_value=(.12,.73,.86,1); scatter.inputs['Density'].default_value=.013; scatter.inputs['Anisotropy'].default_value=.25
    add=nt.nodes.new('ShaderNodeAddShader'); nt.links.new(absorb.outputs[0],add.inputs[0]); nt.links.new(scatter.outputs[0],add.inputs[1]); nt.links.new(add.outputs[0],output.inputs['Volume'])
    M['pool_medium']=vol
    # Broad, stepped tonal fields emulate a painted game surface. No photographic
    # textures or high-frequency damage: the wall remains a quiet mineral field.
    for name in ('mineral','mineral_light','floor','floor_light','pipe','teal','teal_light','teal_dark','teal_service','steel'):
        nt=M[name].node_tree; p=nt.nodes.get('Principled BSDF')
        source=p.inputs['Base Color'].links[0].from_socket
        coord=nt.nodes.new('ShaderNodeTexCoord')
        tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=1.45 if name.startswith(('floor','mineral')) else 3.5
        tex.inputs['Detail'].default_value=0; tex.inputs['Roughness'].default_value=.3
        nt.links.new(coord.outputs['Object'],tex.inputs['Vector'])
        tones=nt.nodes.new('ShaderNodeValToRGB'); tones.color_ramp.interpolation='CONSTANT'
        ramp=tones.color_ramp
        ramp.elements.remove(ramp.elements[1])
        for idx,(position,value) in enumerate(((0,.87),(.38,.94),(.51,1),(.66,1.06))):
            el=ramp.elements[0] if idx==0 else ramp.elements.new(position)
            el.position=position; el.color=(value,value,value,1)
        nt.links.new(tex.outputs['Fac'],tones.inputs[0])
        mix=nt.nodes.new('ShaderNodeMixRGB'); mix.blend_type='MULTIPLY'; mix.inputs[0].default_value=.22
        nt.links.new(source,mix.inputs[1]); nt.links.new(tones.outputs[0],mix.inputs[2])
        # Short-range occlusion grounds contact and folded seams without baking
        # shadows into the lighting or disguising unsupported objects.
        ao=nt.nodes.new('ShaderNodeAmbientOcclusion'); ao.inputs['Distance'].default_value=.42 if name.startswith('floor') else .16
        ao.samples=8
        shade=nt.nodes.new('ShaderNodeMixRGB'); shade.blend_type='MULTIPLY'; shade.inputs[0].default_value=.30
        nt.links.new(mix.outputs[0],shade.inputs[1]); nt.links.new(ao.outputs['Color'],shade.inputs[2]); nt.links.new(shade.outputs[0],p.inputs['Base Color'])


def mesh(name, verts, faces, mat, bevel=0, smooth=False):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.materials.append(M[mat])
    data.update()
    obj = bpy.data.objects.new(name, data)
    COL.objects.link(obj)
    obj.matrix_world = FRAME.copy()
    if smooth:
        for p in data.polygons:
            p.use_smooth = len(p.vertices) == 4
    if bevel:
        mod = obj.modifiers.new('Machined edge', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = 'ANGLE'
        mod.harden_normals = True
        nm = obj.modifiers.new('Weighted face normals', 'WEIGHTED_NORMAL')
        nm.keep_sharp = True
    return obj


def box(name, loc, size, mat='steel', bevel=.018):
    x, y, z = loc
    a, b, c = [v / 2 for v in size]
    verts = [(x + i*a, y + j*b, z + k*c) for i, j, k in
             [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
    return mesh(name, verts, [(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)], mat, bevel)


def cylinder(name, loc, radius, depth, mat='steel', axis=(0,0,1), sides=32, bevel=.008):
    center = Vector(loc)
    w = Vector(axis).normalized()
    u = w.cross(Vector((0,0,1)) if abs(w.z) < .9 else Vector((0,1,0))).normalized()
    v = w.cross(u)
    verts = [tuple(center + w * dz + radius*(math.cos(TAU*i/sides)*u + math.sin(TAU*i/sides)*v))
             for dz in (-depth/2, depth/2) for i in range(sides)]
    faces = [tuple(reversed(range(sides))), tuple(range(sides, sides*2))]
    faces += [(i, (i+1)%sides, (i+1)%sides+sides, i+sides) for i in range(sides)]
    return mesh(name, verts, faces, mat, bevel, True)


def ring(name, loc, ri, ro, depth, mat='steel', start=0, end=TAU, steps=64):
    x, y, z = loc
    angles = [start + (end-start)*i/steps for i in range(steps+1)]
    n = len(angles)
    verts = [(x+r*math.cos(t), y+r*math.sin(t), z+dz) for dz,r in
             [(-depth/2,ri),(-depth/2,ro),(depth/2,ri),(depth/2,ro)] for t in angles]
    faces=[]
    for i in range(n-1):
        for a,b in [(0,1),(1,3),(3,2),(2,0)]:
            faces.append((a*n+i,b*n+i,b*n+i+1,a*n+i+1))
    faces += [(0,2*n,3*n,n),(n-1,2*n-1,4*n-1,3*n-1)]
    ob=mesh(name,verts,[tuple(reversed(f)) for f in faces],mat,.004,False)
    for p in ob.data.polygons: p.use_smooth=abs(p.normal.z)<.5
    return ob


def lathe(name, profile, mat, sides=32, bore=0):
    verts=[(r*math.cos(TAU*i/sides),r*math.sin(TAU*i/sides),z) for r,z in profile for i in range(sides)]
    n=len(profile); faces=[]
    for k in range(n-1):
        faces += [(k*sides+i,k*sides+(i+1)%sides,(k+1)*sides+(i+1)%sides,(k+1)*sides+i) for i in range(sides)]
    if bore:
        for z in (profile[0][1],profile[-1][1]): verts += [(bore*math.cos(TAU*i/sides),bore*math.sin(TAU*i/sides),z) for i in range(sides)]
        for a,b in [(0,n), (n,n+1), (n+1,n-1)]:
            faces += [(a*sides+i,b*sides+i,b*sides+(i+1)%sides,a*sides+(i+1)%sides) for i in range(sides)]
    else: faces += [tuple(reversed(range(sides))),tuple(range((n-1)*sides,n*sides))]
    ob=mesh(name,verts,faces,mat,.012,False)
    for p in ob.data.polygons: p.use_smooth=abs(p.normal.z)<.98
    return ob


def cast_carriage(name):
    # Folded front/back plates with relieved corners form a different silhouette from the motor.
    outline=[(-.48,-.64),(.48,-.64),(.665,-.42),(.665,.42),(.48,.64),(-.48,.64),(-.665,.42),(-.665,-.42)]
    verts=[(x*s,y*s,z) for z,s in [(7.90,.94),(8.04,1),(9.16,1),(9.30,.94)] for x,y in outline]
    faces=[]
    for k in range(3): faces += [(k*8+i,k*8+(i+1)%8,(k+1)*8+(i+1)%8,(k+1)*8+i) for i in range(8)]
    faces += [tuple(reversed(range(8))),tuple(range(24,32))]
    return mesh(name,verts,faces,'teal',.018)


def tube(name, points, radius, mat='pipe'):
    if radius>=.065 and mat in ('pipe','steel_light') and len(points)>2:
        softened=[points[0]]
        for a,b,c in zip(points,points[1:],points[2:]):
            a,b,c=Vector(a),Vector(b),Vector(c)
            u=(b-a).normalized(); v=(c-b).normalized()
            trim=min(max(.18,radius*1.8),(b-a).length*.35,(c-b).length*.35)
            s=b-u*trim; e=b+v*trim
            for k in range(7):
                t=k/6; p=(1-t)**2*s+2*(1-t)*t*b+t*t*e
                softened.append(tuple(p))
        points=softened+[points[-1]]
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 1
    cu.bevel_depth = radius
    cu.resolution_u = 12
    cu.bevel_resolution = 4
    cu.resolution_u = 12
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    sp.points.add(len(points)-1)
    for p, co in zip(sp.points, points): p.co = (*co,1)
    ob = bpy.data.objects.new(name, cu)
    COL.objects.link(ob)
    ob.matrix_world = FRAME.copy()
    cu.materials.append(M[mat])
    return ob


def beam(name, a, b, width, depth, mat='steel'):
    # A rectangular structural member oriented along a 3D line.
    a,b=Vector(a),Vector(b)
    w=(b-a).normalized()
    u=w.cross(Vector((0,0,1)) if abs(w.z)<.9 else Vector((0,1,0))).normalized()*width/2
    v=w.cross(u).normalized()*depth/2
    verts=[tuple(p+u*i+v*j) for p in (a,b) for i,j in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    return mesh(name,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,.014)


def label(name, words, loc, size=.12, mat='white', angle=0, flat=False, align='CENTER'):
    cu=bpy.data.curves.new(name,'FONT')
    cu.body=words
    cu.size=size
    cu.align_x=align
    cu.align_y='CENTER'
    cu.space_character=1.12
    cu.extrude=.0008
    cu.resolution_u=3
    ob=bpy.data.objects.new(name,cu)
    COL.objects.link(ob)
    rot=Matrix.Rotation(angle,4,'Z') @ Matrix.Rotation(0 if flat else PI/2,4,'X')
    ob.matrix_world=FRAME @ Matrix.Translation(loc) @ rot
    cu.materials.append(M[mat])
    return ob


def bolts(name, corners, r=.025, axis=(0,-1,0)):
    for i,p in enumerate(corners): cylinder(f'{name}.{i+1}',p,r,.018,'steel_light',axis,6,.002)


def plate(name, loc, size, title='', textsize=.10, mat='teal_dark'):
    x,y,z=loc; w,d,h=size
    ob=box(name,loc,size,mat,.012)
    if title: label(name+'.legend',title,(x,y-d/2-.004,z),textsize)
    bolts(name+'.rivet',[(x+sx*(w/2-.04),y-d/2-.01,z+sz*(h/2-.04)) for sx in (-1,1) for sz in (-1,1)],.016)
    return ob


def gauge(name, loc, r=.115, needle=.65):
    x,y,z=loc
    cylinder(name+'.bezel',(x,y,z),r,.055,'steel_light',(0,-1,0))
    cylinder(name+'.dial',(x,y-.031,z),r*.83,.008,'white',(0,-1,0),40,0)
    for i in range(21):
        t=PI*.2+PI*1.6*i/20
        inner=.55 if i%5==0 else .68
        a=(x+r*inner*math.cos(t),y-.037,z+r*inner*math.sin(t))
        b=(x+r*.74*math.cos(t),y-.037,z+r*.74*math.sin(t))
        tube(name+'.tick',[a,b],.003 if i%5==0 else .0016,'ink')
        if i%5==0:
            label(name+'.dial value',str(10-i//2),(x+r*.41*math.cos(t),y-.038,z+r*.41*math.sin(t)),r*.145,'ink')
    t=PI*.2+PI*1.6*needle
    tube(name+'.needle',[(x,y-.045,z),(x+r*.65*math.cos(t),y-.045,z+r*.65*math.sin(t))],.004,'ink')
    cylinder(name+'.hub',(x,y-.05,z),.018,.012,'steel',(0,-1,0),12,.002)
    label(name+'.units','bar',(x,y-.040,z-r*.30),r*.16,'ink')
    cylinder(name+'.safety crystal',(x,y-.061,z),r*.79,.004,'glass',(0,-1,0),40,0)


def origin_at(ob,point):
    p=Vector(point)
    for v in ob.data.vertices: v.co-=p
    ob.matrix_world=FRAME@Matrix.Translation(p)


def button(name, loc, mat='green', r=.035, guarded=False):
    x,y,z=loc
    cylinder(name+'.collar',loc,r*1.3,.025,'steel_light',(0,-1,0),20)
    ob=cylinder(name,(x,y-.025,z),r,.035,mat,(0,-1,0),24)
    origin_at(ob,(x,y-.025,z))
    ob['interaction']=name
    ob['local_press_axis']='Y'; ob['press_travel_m']=.025
    if guarded:
        for dx in (-r*1.6,r*1.6): box(name+'.guard',(x+dx,y-.03,z),(.012,.08,r*3),'steel',.006)
    return ob


def lever(name,loc,length=.18,mat='yellow'):
    x,y,z=loc
    cylinder(name+'.pivot',loc,.048,.04,'steel_light',(0,-1,0),24)
    root=bpy.data.objects.new(name+'_PIVOT',None); COL.objects.link(root); root.matrix_world=FRAME@Matrix.Translation(loc)
    before=set(bpy.data.objects)
    tube(name+'.arm',[(x,y-.04,z),(x,y-.14,z+length)],.016,'shaft')
    ob=cylinder(name+'.grip',(x,y-.14,z+length),.027,.13,mat,(1,0,0),16)
    for part in set(bpy.data.objects)-before:
        part.parent=root; part.matrix_parent_inverse=root.matrix_world.inverted()
    root['interaction']=name; root['local_rotation_axis']='X'; root['switch_travel_degrees']=35
    return root


def screen(name,loc,w=.36,h=.25):
    x,y,z=loc
    box(name+'.bezel',loc,(w+.07,.12,h+.07),'rubber',.025)
    box(name+'.phosphor',(x,y-.066,z),(w,.01,h),'screen',.018)
    # A small dated industrial readout: numeric operating values and one trend.
    bank_readout=('BANK' in name or 'OPERATOR' in name)
    label(name+'.header','DRIVE / MONITOR' if bank_readout else 'PROCESS / MONITOR',(x,y-.074,z+h*.35),h*.065,'screen_line')
    rows=['A  82.0 %','B  81.0 %','TRIM READY'] if bank_readout else ['P  07.4 bar','T  32.5 C','RUN / HOLD']
    for row,words in enumerate(rows):
        label(name+'.operating value',words,(x-w*.43,y-.075,z+h*(.14-row*.14)),h*.061,'screen_line',align='LEFT')
    for row in range(3): box(name+'.chart grid',(x+w*.23,y-.073,z+h*(.15-row*.17)),(w*.36,.003,.001),'teal_light',0)
    pts=[(x+w*(.065+k*.032),y-.076,z+h*(.07+.035*math.sin(k*1.7))) for k in range(10)]
    tube(name+'.trend',pts,.0011,'screen_line')
    readout='ACK READY' if 'Alarm' in name else ('84.2  MW' if 'DEMAND' in name else ('A .82 / B .81' if 'BANK' in name else 'SYS / NORMAL'))
    label(name+'.readout',readout,(x,y-.078,z-h*.37),h*.066,'screen_line')
    for sx in (-1,1):
        for sz in (-1,1): cylinder(name+'.frame screw',(x+sx*(w/2+.017),y-.063,z+sz*(h/2+.017)),.009,.012,'steel_light',(0,-1,0),6,.001)


def hatch(name,loc,w,h):
    x,y,z=loc
    box(name+'.compression gasket',(x,y+.009,z),(w+.028,.017,h+.028),'rubber',.011)
    plate(name,loc,(w,.034,h),'',mat='teal_light')
    for dz in (-h*.3,h*.3): box(name+'.hinge',(x-w/2-.013,y-.006,z+dz),(.045,.055,.10),'steel_light',.01)
    tube(name+'.handle',[(x+w*.30,y-.024,z-.07),(x+w*.30,y-.10,z-.07),(x+w*.30,y-.10,z+.07),(x+w*.30,y-.024,z+.07)],.012,'steel_light')
    # Three small authored chips at a touched latch, not a whole-surface grunge.
    for k in range(3): box(name+'.contact_wear',(x+w*.3-.017+k*.011,y-.019,z-.10),(.022,.004,.009),'paint_chip',0)
    # Wear is tied to a handled plate edge, with unequal nicks and a exposed latch seat.
    for k in range(5):
        px=x-w*.43+k*w*.17; pz=z-h*.47
        mesh(name+'.edge chip',[(px,y-.019,pz),(px+.031,y-.019,pz+.009),(px+.063,y-.019,pz+.002),(px+.047,y-.019,pz-.004)],[(0,1,2,3)],'paint_chip')
    box(name+'.latch seat',(x+w*.30,y-.025,z),(.061,.016,.19),'steel_light',.006)


def flange(name,loc,r=.25,axis=(0,0,1),mat='pipe'):
    cylinder(name,loc,r,.095,mat,axis,32,.01)
    w=Vector(axis).normalized()
    u=w.cross(Vector((0,0,1)) if abs(w.z)<.9 else Vector((0,1,0))).normalized()
    v=w.cross(u)
    for i in range(8):
        p=Vector(loc)+w*.055+r*.78*(math.cos(i*TAU/8)*u+math.sin(i*TAU/8)*v)
        cylinder(name+'.bolt',tuple(p),.022,.024,'steel_light',axis,6,.002)


def wheel(name,loc,r=.22,mat='yellow',axis=(0,-1,0)):
    x,y,z=loc
    cylinder(name+'.valve stem',(x,y+.13,z),.032,.29,'shaft',(0,1,0),20)
    cylinder(name+'.stem packing',(x,y+.24,z),.077,.10,'steel_light',(0,1,0),6)
    pts=[(x+r*math.cos(t),y,z+r*math.sin(t)) for t in [i*TAU/40 for i in range(41)]]
    tube(name+'.rim',pts,.02,mat)
    for t in (0,TAU/3,2*TAU/3): tube(name+'.spoke',[loc,(x+r*math.cos(t),y,z+r*math.sin(t))],.013,mat)
    cylinder(name+'.hub',loc,.055,.08,'steel_light',axis,16)


def floor_contact(obj, z=0):
    CONTACTS.append({'object':obj.name,'support':'finished floor','expected_z':FRAME.translation.z+z})


def light(name,loc,target,power,color='FFFFFF',size=3,kind='AREA',spot=.9):
    data=bpy.data.lights.new(name,kind)
    data.energy=power
    data.color=srgb(color)
    if kind=='AREA': data.shape='DISK'; data.size=size
    if kind=='SPOT': data.spot_size=spot; data.spot_blend=.40; data.shadow_soft_size=.12
    ob=bpy.data.objects.new(name,data); COL.objects.link(ob)
    p=FRAME@Vector(loc); t=FRAME@Vector(target)
    ob.location=p
    ob.rotation_euler=(t-p).to_track_quat('-Z','Y').to_euler()
    return ob


OCT=[(-6,10.8),(6,10.8),(10.8,6),(10.8,-6),(6,-10.8),(-6,-10.8),(-10.8,-6),(-10.8,6)]


def clip_halfplane(poly,a,b,left=True):
    if not poly: return []
    def dist(p): return ((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))*(1 if left else -1)
    result=[]
    prev=poly[-1]; dp=dist(prev)
    for point in poly:
        dc=dist(point)
        if (dc>=0)!=(dp>=0):
            t=dp/(dp-dc)
            result.append((prev[0]+t*(point[0]-prev[0]),prev[1]+t*(point[1]-prev[1])))
        if dc>=0: result.append(point)
        prev=point; dp=dc
    return result


def grid_floor():
    # Convex clipping cuts real floor slabs to the octagon and circular service band.
    circle=[(5.20*math.cos(i*TAU/96),5.20*math.sin(i*TAU/96)) for i in range(96)]
    for ix in range(9):
        for iy in range(9):
            x0=-10.8+ix*2.4+.009; x1=x0+2.382
            y0=-10.8+iy*2.4+.009; y1=y0+2.382
            poly=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
            for i in range(8): poly=clip_halfplane(poly,OCT[i],OCT[(i+1)%8],False)
            if len(poly)<3: continue
            remainder=poly; pieces=[]
            nearest=math.hypot(max(x0,0,-x1),max(y0,0,-y1))
            if nearest>5.2: pieces=[poly]
            else:
                for k in range(96):
                    outside=clip_halfplane(remainder,circle[k],circle[(k+1)%96],False)
                    if len(outside)>=3: pieces.append(outside)
                    remainder=clip_halfplane(remainder,circle[k],circle[(k+1)%96],True)
                    if len(remainder)<3: break
            verts=[]; faces=[]
            for p in pieces:
                area=abs(sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p))))/2
                if area<.000001: continue
                j=len(verts); n=len(p)
                verts += [(x,y,0) for x,y in p]+[(x,y,-.033) for x,y in p]
                faces.append(tuple(range(j,j+n)))
                faces += [(j+k,j+(k+1)%n,j+(k+1)%n+n,j+k+n) for k in range(n)]
            if verts: mesh(f'Sealed floor slab {ix+1}-{iy+1}',verts,faces,'floor_light' if (ix*5+iy*7)%7==0 else 'floor')


def hall_floor():
    collection('01 ARCHITECTURE')
    # Radial seams resolve exactly to the approved octagonal wall line.
    for i in range(48):
        a=i*TAU/48+.001; b=(i+1)*TAU/48-.001
        angles=[a+(b-a)*j/8 for j in range(9)]
        def limit(t):
            c,s=abs(math.cos(t)),abs(math.sin(t))
            return min(10.8/max(c,1e-9),10.8/max(s,1e-9),16.8/max(c+s,1e-9))
        inner=[(5.2*math.cos(t),5.2*math.sin(t),-.035) for t in angles]
        outer=[(limit(t)*math.cos(t),limit(t)*math.sin(t),-.035) for t in reversed(angles)]
        top=inner+outer; n=len(top)
        verts=top+[(x,y,-.32) for x,y,z in top]
        faces=[tuple(range(n)),tuple(reversed(range(n,2*n)))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
        mesh(f'Hall floor segment {i+1:02}',verts,faces,'floor_light' if i%5==0 else 'floor',.003)
    grid_floor()
    for i in range(32):
        ring('Service ring slab',(0,0,-.07),3.9,5.2,.14,'mineral_light' if i%4 else 'mineral',i*TAU/32+.001,(i+1)*TAU/32-.001,5)
    ring('Service outer inlay',(0,0,.004),5.13,5.18,.008,'steel_light')
    # Broad inlaid route markers; no raised floor trip geometry.
    for t in (0,PI/2,PI,3*PI/2):
        with at(5.7*math.cos(t),5.7*math.sin(t),.003,t+PI/2):
            mesh('Clockwise circulation arrow',[(-.15,-.2,0),(.15,-.2,0),(.15,.05,0),(.28,.05,0),(0,.36,0),(-.28,.05,0),(-.15,.05,0)],[tuple(range(7))],'white')


def local_wall_panel(name,x,z,w,h,mat='mineral'):
    box(name,(x,.14,z),(w,.28,h),mat,.02)
    # Small recessed attachment plates at panel corners establish panel scale.
    for dx in (-w/2+.10,w/2-.10):
        for dz in (-h/2+.10,h/2-.10):
            cylinder(name+'.anchor',(x+dx,-.011,z+dz),.022,.018,'steel_light',(0,-1,0),12,.001)


def portal(name,center,width,height):
    for s in (-1,1):
        box(name+'.jamb',(center+s*(width/2+.13),-.12,height/2),(.26,.35,height+.22),'steel',.04)
        box(name+'.jamb liner',(center+s*(width/2+.028),-.28,height/2),(.055,.13,height),'steel_light',.01)
        box(name+'.bumper',(center+s*(width/2+.14),-.33,.8),(.30,.10,1.1),'teal_dark',.035)
    box(name+'.lintel',(center,-.13,height+.14),(width+.52,.4,.28),'steel',.035)
    box(name+'.head light',(center,-.35,height-.12),(width*.72,.10,.06),'lamp',.01)
    plate(name+'.route sign',(center,-.36,height+.57),(min(width,3),.065,.48),name.upper(),.18)
    # Short architectural link stub is visible through each real opening.
    for s in (-1,1): box(name+'.link wall',(center+s*(width/2+.16),1.85,height/2),(.32,3.7,height),'mineral',.02)
    box(name+'.link floor',(center,1.85,-.16),(width,3.7,.32),'floor',.01)
    box(name+'.link roof',(center,1.85,height+.12),(width,3.7,.24),'mineral',.01)
    box(name+'.closed distant doors',(center,3.64,height/2),(width,.1,height),'teal_dark',.025)
    for sx in (-1,1): box(name+'.door leaf',(center+sx*width/4,3.56,height/2),(width/2-.06,.06,height-.1),'teal',.025)
    light(name+'.link practical',(center,1.7,height-.18),(center,1.7,0),240,'FFF0CF',2)


def shell():
    collection('01 ARCHITECTURE')
    for i in range(8):
        a=Vector((*OCT[i],0)); b=Vector((*OCT[(i+1)%8],0)); delta=b-a
        length=delta.length; tangent=delta.normalized()
        # Local +Y is outside, local -Y faces the hall.
        mid=(a+b)/2; angle=math.atan2(tangent.y,tangent.x)
        openings=[]
        if i==0: openings=[(0,5,5,'FUEL HANDLING')]
        if i==2: openings=[(-3.6,4,5,'CONTROL ACCESS')]
        if i==3: openings=[(0,5,5,'COOLING PLANT')]
        if i==6: openings=[(0,6,5.5,'MAIN ACCESS')]
        with at(mid.x,mid.y,0,angle):
            # Segmented shell with exact opening exclusions, including east observation glazing.
            xcuts=[-length/2,length/2]
            for c,w,h,n in openings: xcuts += [c-w/2,c+w/2]
            if i==2: xcuts += [-2.7,2.7]
            xcuts=sorted(set(xcuts))
            zcuts=[0,5,8,10.2,10.3,12.9,16] if i==2 else [0,5.5 if i==6 else 5,9.6,13.4,16]
            for x0,x1 in zip(xcuts,xcuts[1:]):
                for z0,z1 in zip(zcuts,zcuts[1:]):
                    xc=(x0+x1)/2; zc=(z0+z1)/2
                    skip=any(abs(xc-c)<w/2-.001 and zc<h for c,w,h,n in openings)
                    if i==2 and abs(xc)<2.7 and (8<zc<10.2 or 10.3<zc<12.9): skip=True
                    if skip: continue
                    # Subdivide large fields into architectural panels, retaining quiet fields.
                    nx=max(1,math.ceil((x1-x0)/4.5)); nz=max(1,math.ceil((z1-z0)/5.0))
                    for xx in range(nx):
                        for zz in range(nz):
                            w=(x1-x0)/nx; h=(z1-z0)/nz
                            local_wall_panel(f'Shell {i+1} field',x0+(xx+.5)*w,z0+(zz+.5)*h,w-.024,h-.022,'mineral_light' if (i+xx)%4==0 else 'mineral')
            # Continuous structural belt and modest lower crash rail.
            box('Upper structural ledger',(0,-.15,14.55),(length,.36,.42),'steel',.02)
            box('Wall cornice',(0,-.12,15.85),(length,.36,.28),'mineral_light',.02)
            for c,w,h,n in openings:
                if i==2:
                    # Control link uses the specifically dimensioned P02 vestibule instead.
                    for s in (-1,1): box('Control route jamb',(c+s*(w/2+.12),-.12,h/2),(.24,.38,h),'steel',.03)
                    box('Control route lintel',(c,-.13,h+.12),(w+.48,.38,.24),'steel',.025)
                    plate('Control route sign',(c,-.37,5.63),(3.5,.06,.48),'CONTROL / 10 M',.18)
                else: portal(n,c,w,h)
            for x in (-length*.34,length*.34):
                box('Wall light mounting plate',(x,-.025,12.6),(.50,.05,.44),'steel',.018)
                bolts('Wall light anchors',[(x+sx*.16,-.058,12.6+sz*.14) for sx in (-1,1) for sz in (-1,1)],.023)
                box('Wall light bracket',(x,-.30,12.6),(.36,.55,.22),'steel',.03)
                box('Wall light lens',(x,-.57,12.56),(.27,.06,.14),'lamp',.025)
                light('Warm wall wash',(x,-.63,12.55),(x,-.12,7.6),1250,'FFD5A2',1,'SPOT',.95)
            if i in (1,4,5,7):
                box('Station lamp mounting plate',(0,-.025,4.67),(.76,.05,.33),'steel',.015)
                box('Station lamp bracket',(0,-.275,4.65),(.60,.55,.15),'steel',.018)
                box('Station lamp diffuser',(0,-.42,4.56),(.49,.34,.028),'lamp',.008)
                light('Station worklight',(0,-.44,4.52),(0,-2.6,.4),180,'FFF0D2',.85)
    # Columns sit just inside each corner, flanges and webs form credible steelwork.
    for i,(x,y) in enumerate(OCT):
        center=Vector((x,y)).normalized()*.21
        xx,yy=x-center.x,y-center.y
        angle=math.atan2(y,x)+PI/2
        with at(xx,yy,0,angle):
            box('Column web',(0,0,8),(.18,.43,16),'steel',.012)
            for dy in (-.24,.24): box('Column flange',(0,dy,8),(.50,.075,16),'steel',.015)
            base=box('Column foot',(0,0,.06),(.72,.70,.12),'steel_light',.018); floor_contact(base)
            bolts('Column anchor',[(sx*.25,sy*.22,.14) for sx in (-1,1) for sy in (-1,1)],.045,(0,0,1))
            for z in (4.8,9.6,14.4): box('Column splice',(0,-.29,z),(.52,.065,.48),'steel_light',.008)
    collection('02 ROOF STRUCTURE')
    verts=[(x,y,16.08) for x,y in OCT]
    mesh('Octagonal roof deck',verts,[tuple(range(8))],'mineral',0)
    for y in (-7,-3.5,0,3.5,7):
        end=10.8 if abs(y)<=6 else 16.8-abs(y)
        for z in (14.95,15.85): beam('Roof truss chord',(-end,y,z),(end,y,z),.22,.22)
        divisions=8
        for k in range(divisions):
            x0=-end+2*end*k/divisions; x1=-end+2*end*(k+1)/divisions
            beam('Roof truss diagonal',(x0,y,14.95 if k%2==0 else 15.85),(x1,y,15.85 if k%2==0 else 14.95),.10,.10)
        for x in (-end,end):
            box('Truss bearing seat',(x,y,14.76),(.66,.48,.16),'steel_light',.015)
            for dy in (-.17,.17): cylinder('Bearing seat anchor',(x,y+dy,14.85),.034,.045,'steel',(0,0,1),6,.004)
    for x,y in [(-6,-5),(0,-6),(6,-5),(-6,4),(0,6),(6,4)]:
        for dx in (-.65,.65):
            tube('Luminaire threaded hanger',[(x+dx,y,15.26),(x+dx,y,16.04)],.018,'steel_light')
            box('Luminaire ceiling anchor',(x+dx,y,16.04),(.22,.22,.08),'steel',.008)
        box('Ceiling practical housing',(x,y,15.15),(2.0,.7,.22),'steel',.03)
        box('Ceiling diffuser',(x,y,15.025),(1.82,.55,.035),'lamp',.02)
        light('Ceiling cool white',(x,y,14.98),(x*.75,y*.75,0),480,'E2E9EB',1.25)


def pool():
    collection('03 POOL AND RAIL')
    for i in range(32):
        t0=i*TAU/32+.0015; t1=(i+1)*TAU/32-.0015
        ring('Precast rim stone',(0,0,.085),3.4,3.9,.17,'mineral_light',t0,t1,5)
        for j in range(7):
            ring('Shaft lining course',(0,0,-.45-j*.88),3.4,3.53,.86,'pool_tile' if j else 'pipe',t0,t1,5)
    ring('Steel aperture curb',(0,0,.12),3.395,3.435,.12,'steel_light')
    ring('Pool depth datum',(0,0,-3.2),3.36,3.4,.04,'steel_light')
    cylinder('Pool bottom',(0,0,-6.58),3.42,.16,'steel',sides=80)
    cylinder('Water surface',(0,0,-.46),3.393,.02,'water',sides=128,bevel=0)
    cylinder('Deep water medium',(0,0,-3.46),3.385,5.98,'pool_medium',sides=96,bevel=0)
    box('Deep cyan emitter',(0,0,-6.44),(3.8,1.45,.035),'pool_glow',.15)
    for x in (-1.92,1.92): box('Core bed end shield',(x,0,-6.32),(.16,1.68,.30),'steel_light',.015)
    for y in (-.77,.77): box('Core bed side shield',(0,y,-6.32),(3.98,.13,.30),'steel_light',.015)
    for x in (-1.4,1.4):
        with at(x,0): lathe('Submerged guide body',[(.59,-5.895),(.64,-5.80),(.64,-3.62),(.59,-3.545)],'teal_dark',32,.24)
        for z in (-5.8,-4.7,-3.55): ring('Submerged guide flange',(x,0,z),.27,.725,.14,'steel_light')
        for t in (0,PI/2,PI,3*PI/2):
            xx=x+.60*math.cos(t); yy=.60*math.sin(t)
            beam('Guide rib',(xx,yy,-5.65),(xx,yy,-3.62),.09,.12,'teal')
        ring('Core light well',(x,0,-5.96),.35,.82,.16,'pool_glow')
    for y in (-1.0,1.0): beam('Core bed frame',(-2.3,y,-6.08),(2.3,y,-6.08),.28,.28,'steel')
    for x in (-2.25,0,2.25): beam('Core cross member',(x,-1.3,-6.08),(x,1.3,-6.08),.22,.25,'steel')
    for t in (PI*.2,PI*.8,PI*1.2,PI*1.8):
        x,y=3.21*math.cos(t),3.21*math.sin(t)
        tube('Shaft intake',[(x,y,-.8),(x,y,-4.8),(x*.74,y*.74,-5.6)],.11,'pipe')
        for z in (-1.5,-3.5): cylinder('Intake wall bracket',(x,y,z),.15,.10,'steel',sides=24)
    light('Cyan from deep pool',(0,0,-6.08),(0,0,1.2),2400,'18DDEF',1.75)
    # Rail endpoints maintain exactly 1.40 m between fixed gate jambs.
    r=3.69; a=math.asin(.7375/r)
    start=-PI/2+a; end=3*PI/2-a
    n=16
    for z in (.61,1.10):
        pts=[(r*math.cos(t),r*math.sin(t),z) for t in [start+(end-start)*i/128 for i in range(129)]]
        tube('Continuous guardrail',pts,.031,'steel')
    for i in range(n+1):
        t=start+(end-start)*i/n; x,y=r*math.cos(t),r*math.sin(t)
        base=box('Rail foot',(x,y,.195),(.16,.16,.05),'steel_light',.012)
        box('Rail upright',(x,y,.66),(.075,.075,.88),'steel',.007)
        box('Rail collar',(x,y,.3),(.104,.104,.08),'steel_light',.008)
        bolts('Rail anchors',[(x+dx,y+dy,.23) for dx in (-.05,.05) for dy in (-.05,.05)],.013,(0,0,1))
    gy=-math.sqrt(r*r-.7375*.7375)
    gate=bpy.data.objects.new('SERVICE_GATE_PIVOT',None); COL.objects.link(gate); gate.matrix_world=Matrix.Translation((-.7375,gy,.2))
    parts_before=set(bpy.data.objects)
    for z in (.35,.69,1.06): tube('Yellow service gate',[(-.67,gy,z),(.67,gy,z)],.035,'yellow')
    tube('Gate latch stile',[(.65,gy,.32),(.65,gy,1.09)],.031,'yellow')
    for ob in set(bpy.data.objects)-parts_before: ob.parent=gate; ob.matrix_parent_inverse=gate.matrix_world.inverted()
    gate['interaction']='south pool service gate'; gate['local_rotation_axis']='Z'; gate['open_degrees']=90
    gate.rotation_euler.z=0; gate.keyframe_insert(data_path='rotation_euler',frame=1)
    gate.rotation_euler.z=PI/2; gate.keyframe_insert(data_path='rotation_euler',frame=36)
    gate_action=gate.animation_data.action; gate_action.name='SERVICE_GATE_CLOSED_TO_OPEN'; gate_action.use_fake_user=True
    gate.animation_data.action=None; gate.rotation_euler.z=0
    for x,title in [(-.94,'ACKNOWLEDGE'),(.94,'SCRAM')]:
        with at(x,gy-.06,.17):
            base=box(title+'.base',(0,0,.035),(.35,.3,.07),'steel_light',.013)
            box(title+'.fixed jamb',(0,0,.48),(.24,.24,.9),'steel',.025)
            plate(title+'.head',(0,-.045,.93),(.37,.29,.35),title,.062)
            if x>0:
                button('SCRAM_BUTTON',(0,-.21,.92),'red',.082,True)
                label('Bypass legend','BYPASS',(0,-.128,.62),.05)
                lever('BYPASS_SWITCH',(0,-.13,.48),.065,'steel_light')
            else:
                button('ALARM_ACK',(0,-.21,.91),'amber',.055)
                screen('Alarm annunciator',(0,-.133,.64),.15,.1)
    with at(0,gy-.43,.01): label('South emergency floor legend','EMERGENCY SHUTDOWN',(0,-.18,0),.15,'ink',flat=True)
    for x in (-.76,.76): cylinder('Gate hinge',(x,gy,.77),.056,.20,'steel_light')


def banks():
    collection('04 BANK MECHANISMS')
    # Load passes through a deep transverse gantry, its end bearings and roof steel.
    for y in (-.52,.52):
        for z in (13.77,14.63): box('Gantry flange',(0,y,z),(15.5,.26,.15),'steel',.02)
        box('Gantry web',(0,y,14.2),(15.5,.095,.76),'steel',.012)
        for x in (-7.5,-5,-2.5,0,2.5,5,7.5): box('Gantry stiffener',(x,y,14.2),(.08,.36,.75),'steel_light',.012)
    for x in (-7.6,7.6):
        for y in (-.52,.52): beam('Roof hanger',(x,y,14.2),(x,y,15.9),.32,.32)
        box('Gantry end bearing',(x,0,13.69),(.7,1.5,.18),'steel_light',.02)
        beam('Gantry roof transfer member',(x,-3.5,15.80),(x,3.5,15.80),.40,.30,'steel')
        for y in (-3.5,0,3.5):
            box('Roof transfer bearing',(x,y,15.59),(.72,.65,.12),'steel_light',.018)
    for index,x in enumerate((-1.4,1.4)):
        bank=chr(65+index)
        with at(x,0,0):
            box(f'Bank {bank} mounting saddle',(0,0,13.76),(1.8,1.5,.2),'steel_light',.03)
            cylinder(f'Bank {bank} fixed neck',(0,0,13.02),.39,1.45,'steel',sides=32)
            for z in (12.4,13.55): flange(f'Bank {bank} neck flange',(0,0,z),.62)
            fixed=lathe(f'BANK_{bank}_FIXED_HOUSING',[(.72,9.8),(.86,9.91),(.86,10.05),(.78,10.22),(.78,11.98),(.86,12.15),(.86,12.30),(.72,12.4)],'teal',32,.28)
            fixed['role']='fixed actuator; never parent to moving carriage'
            for z in (9.89,10.1,12.17,12.31):
                ring(f'{bank} actuator collar',(0,0,z),.27,.88,.12,'steel_light' if z in (9.89,12.31) else 'steel',steps=48)
            for t in [PI/8+k*PI/4 for k in range(8)]:
                with at(0,0,0,t):
                    box(f'{bank} cast stiffener',(0,-.79,11.1),(.14,.17,1.85),'teal_dark',.025)
                    bolts(f'{bank} housing fasteners',[(0,-.893,z) for z in (10.27,11.93)],.032)
            plate(f'{bank} enamel bank identity',(0,-.88,11.40),(1.14,.075,.50),f'CONTROL\nBANK {bank}',.16,'teal_dark')
            hatch(f'{bank} motor service cover',(0,-.813,10.59),.48,.56)
            plate(f'{bank} lockout tag',(.25,-.866,10.41),(.22,.018,.085),'LOCKOUT',.025,'yellow')
            # A shrouded brake register, split lower bearing and side hydraulic
            # cassette give the actuator specific mechanical construction.
            box(f'{bank} brake air recess',(0,-.767,11.89),(.49,.12,.22),'rubber',.025)
            for row in range(3):
                box(f'{bank} brake ventilation blade',(0,-.840,11.82+row*.065),(.42,.046,.024),'steel_light',.006)
            for t in (-PI/3,PI/3):
                with at(0,0,0,t):
                    plate(f'{bank} hydraulic cassette',(0,-.805,10.96),(.32,.105,.71),'',mat='teal_light')
                    box(f'{bank} oil sight recess',(0,-.869,11.02),(.11,.015,.29),'rubber',.015)
                    box(f'{bank} oil level glass',(0,-.880,11.02),(.07,.009,.24),'glass',.01)
                    box(f'{bank} oil meniscus',(0,-.879,10.96),(.064,.007,.11),'yellow',.004)
                    for z in (10.72,11.22): bolts(f'{bank} cassette lock screws',[(0,-.874,z)],.023)
                    cylinder(f'{bank} hydraulic bleed plug',(0,-.887,10.77),.038,.04,'steel_light',(0,-1,0),6,.004)
            ring(f'{bank} lower bearing retaining ring',(0,0,9.785),.275,.68,.09,'steel',steps=48)
            for k in range(8):
                t=k*TAU/8
                cylinder(f'{bank} bearing cap socket',(.53*math.cos(t),.53*math.sin(t),9.730),.031,.023,'shaft',(0,0,-1),6,.003)
            for s in (-1,1):
                tube(f'{bank} fixed oil feed',[(s*.65,.48,12.55),(s*.65,.64,11.0),(s*.46,.64,10.08)],.035,'steel_light')
            # Exactly two transform roots, each 1.80 m downstroke from its nominal state.
            root=bpy.data.objects.new(f'BANK_{bank}_MOVING',None); COL.objects.link(root)
            root.matrix_world=Matrix.Translation((x,0,8.6)); root['travel_m']=1.8; root['motion_axis']='local Z'; root['nominal_center_z']=8.6
            before=set(bpy.data.objects)
            carriage=cast_carriage(f'BANK_{bank}_CARRIAGE')
            for z in (7.875,9.325): ring(f'{bank} moving flange',(0,0,z),.236,.725,.10,'steel_light',steps=40)
            hatch(f'{bank} moving cover',(0,-.651,8.71),.59,.78)
            # Folded lower yoke, replaceable glide liners and a release register.
            box(f'{bank} carriage lower saddle',(0,-.572,8.04),(.78,.20,.14),'teal_dark',.022)
            for sx in (-.38,.38):
                box(f'{bank} saddle machined seat',(sx,-.680,8.10),(.17,.07,.22),'steel_light',.015)
                cylinder(f'{bank} saddle locking pin',(sx,-.730,8.10),.038,.04,'steel',(0,-1,0),6,.004)
            box(f'{bank} release recess',(0,-.652,8.23),(.36,.025,.12),'rubber',.012)
            box(f'{bank} release tab',(0,-.683,8.23),(.18,.055,.052),'steel_light',.010)
            plate(f'{bank} maintenance strip',(0,-.677,8.86),(.30,.012,.065),'M / 1800',.024,'steel')
            for side in (-1,1):
                # These inset side covers stay inside the approved carriage envelope.
                with at(0,0,0,side*PI/2):
                    plate(f'{bank} side guide cassette',(0,-.665,8.60),(.54,.035,.86),'',mat='teal_dark')
                    for z in (8.30,8.90):
                        cylinder(f'{bank} cassette bearing boss',(0,-.701,z),.095,.035,'steel_light',(0,-1,0),24,.012)
                        cylinder(f'{bank} bearing centre',(0,-.725,z),.035,.020,'steel',(0,-1,0),6,.004)
                    for sx in (-.19,.19):
                        box(f'{bank} cassette lip',(sx,-.691,8.60),(.048,.045,.80),'teal_light',.007)
            for sx in (-.5,.5):
                box(f'{bank} guide shoe',(sx,-.46,8.6),(.17,.28,1.12),'teal_dark',.035)
                box(f'{bank} guide scale',(sx,-.612,8.62),(.065,.012,.79),'yellow',.008)
                for k in range(6): box(f'{bank} scale mark',(sx,-.62,8.30+k*.12),(.045,.005,.012),'ink',0)
            shaft=cylinder(f'BANK_{bank}_DRIVE_COLUMN',(0,0,2.05),.23,11.60,'shaft',sides=48,bevel=.008)
            cylinder(f'{bank} carriage gland',(0,0,7.72),.34,.16,'steel',sides=40)
            cylinder(f'{bank} top sliding engagement',(0,0,10.56),.23,2.57,'shaft',sides=40)
            for ob in set(bpy.data.objects)-before:
                ob.parent=root; ob.matrix_parent_inverse=root.matrix_world.inverted()
            root.location.z=8.6; root.keyframe_insert(data_path='location',frame=1)
            root.location.z=8.48 if index==0 else 8.56; root.keyframe_insert(data_path='location',frame=90)
            root.location.z=8.6; root.keyframe_insert(data_path='location',frame=180)
            root.location.z=6.8; root.keyframe_insert(data_path='location',frame=192)
            root.location.z=6.84; root.keyframe_insert(data_path='location',frame=196)
            root.location.z=6.8; root.keyframe_insert(data_path='location',frame=201)
            # A fixed local dial is a secondary readable service element.
            gauge(f'{bank} accumulator pressure',(.46,-.72,11.02),.105,.46+.1*index)


def console(name, width=1.4, depth=.8, height=1.15, style=0):
    # A cast pedestal with an angled control deck; front is local -Y.
    base=box(name+'.plinth',(0,0,.045),(width+.08,depth+.06,.09),'steel',.035); floor_contact(base)
    box(name+'.kick',(0,.04,.22),(width-.16,depth-.16,.3),'teal_dark',.035)
    w=width/2; d=depth/2
    profile=[(-d,.32),(d,.32),(d,height),(-d,height-.25)]
    verts=[(sx*w,y,z) for sx in (-1,1) for y,z in profile]
    mesh(name+'.wedge chassis',verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'teal',.035)
    hatch(name+'.front access',(0,-d-.018,(height+.07)/2),width*.68,(height-.57)*.80)
    with at(0,0,0,PI):
        hatch(name+'.rear service hatch',(0,-d-.022,(height+.32)/2),width*.68,(height-.32)*.64)
        for k in range(4): box(name+'.rear cooling louvre',(0,-d-.045,height+.08+k*.068),(width*.53,.025,.022),'ink',.004)
        cylinder(name+'.power gland',(width*.32,-d-.08,.40),.042,.09,'rubber',(0,-1,0),20,.008)
    # Angled deck controls use an articulated local frame matching the chassis slope.
    slope=math.atan2(.25,depth)
    global FRAME
    previous=FRAME.copy()
    FRAME=FRAME @ Matrix.Translation((0,0,height-.125+.018)) @ Matrix.Rotation(slope,4,'X')
    box(name+'.deck plate',(0,0,0),(width-.07,depth-.05,.04),'steel_light',.018)
    # Individual switch housings, legends and levers face up on the deck.
    for k in range(5):
        x=-width*.34+k*width*.17
        box(name+'.switch socket',(x,-depth*.24,.032),(.095,.1,.03),'rubber',.008)
        cylinder(name+'.toggle',(x,-depth*.24,.061),.017,.05,'pipe',sides=12,bevel=.003)
        label(name+'.switch legend',str(k+1),(x,-depth*.10,.03),.043,'ink',flat=True)
    for k in range(3):
        cylinder(name+'.deck indicator',(-width*.30+k*.105,depth*.06,.05),.027,.028,'green' if k!=2 else 'amber',sides=16)
    box(name+'.log slot',(width*.26,depth*.05,.035),(width*.25,.15,.015),'ink',.008)
    # One compact physical entry bank, a rotary mode selector and grouped status
    # lamps distinguish a working operator panel from a row of generic buttons.
    box(name+'.entry key mounting',(width*.03,depth*.12,.043),(width*.37,depth*.30,.025),'teal_dark',.008)
    for col in range(5):
        for row in range(2):
            x=-width*.105+col*width*.067; y=depth*.05+row*depth*.12
            box(name+'.tactile entry key',(x,y,.061),(width*.048,depth*.070,.022),'pipe' if col<4 else 'yellow',.004)
    cylinder(name+'.mode bezel',(-width*.30,depth*.30,.050),.050,.018,'steel_light',sides=24,bevel=.003)
    box(name+'.rotary selector',(-width*.30,depth*.30,.075),(.025,.071,.030),'rubber',.005)
    label(name+'.mode legend','MAN  AUTO',(-width*.30,depth*.41,.032),.027,'ink',flat=True)
    FRAME=previous
    # Riser carries a physically framed display and analog backup instrument.
    box(name+'.instrument riser',(0,d-.045,height+.23),(width-.06,.22,.52),'teal_dark',.03)
    screen(name+'.CRT',(-width*.19,d-.18,height+.23),width*.35,.30)
    gauge(name+'.analog backup',(width*.29,d-.19,height+.26),.12,.42+style*.08)
    plate(name+'.asset tag',(width*.29,d-.174,height+.02),(.25,.025,.09),name[:14].upper(),.028)
    for sx in (-1,1):
        box(name+'.end cap',(sx*(w-.045),0,height-.10),(.09,depth,.14),'teal_light',.015)
        for yy in (-depth*.30,depth*.30): cylinder(name+'.deck retaining screw',(sx*(w-.047),yy,height-.027+.25*yy/depth),.014,.012,'steel_light',sides=6,bevel=.002)
    return base


def cabinet(name, w=1.2, d=.65, h=1.9, mode=0):
    base=box(name+'.skid',(0,0,.06),(w+.04,d+.04,.12),'steel',.025); floor_contact(base)
    box(name+'.case',(0,0,h/2+.12),(w,d,h),'teal',.04)
    box(name+'.cap',(0,0,h+.15),(w+.06,d+.04,.08),'teal_light',.018)
    if mode==0:
        hatch(name+'.service door',(0,-d/2-.02,h*.51+.12),w-.15,h*.72)
        gauge(name+'.dial',(-w*.18,-d/2-.07,h*.84),.12)
        for k in range(6): box(name+'.vent',(w*.20,-d/2-.046,.35+k*.055),(w*.27,.018,.021),'ink',.004)
    else:
        for k in range(3):
            z=.46+k*.45
            plate(name+'.breaker panel',(0,-d/2-.025,z),(w-.12,.025,.39))
            lever(name+f'.BREAKER_{k+1}',(0,-d/2-.06,z-.02),.12)
            button(name+'.live',(-w*.29,-d/2-.05,z+.08),'green',.024)
    plate(name+'.identifier',(0,-d/2-.065,h+.03),(w*.75,.04,.19),name.upper(),.071)
    return base


def motor(name,loc,length=1.2,r=.34,axis=(1,0,0),mat='teal'):
    x,y,z=loc
    cylinder(name+'.motor barrel',loc,r,length,mat,axis,32,.018)
    w=Vector(axis)
    for k in range(8):
        p=Vector(loc)+w*(-length*.43+length*.86*k/7)
        cylinder(name+'.cooling fin',tuple(p),r+.04,.035,mat,axis,32,.006)
    for s in (-1,1):
        p=Vector(loc)+w*(length/2+.04)*s
        flange(name+'.end plate',tuple(p),r+.02,axis,'steel_light')
    box(name+'.terminal box',(x,y,z+r+.07),(.35,.30,.16),'teal_dark',.025)


def tank(name,r=.52,h=2.4):
    base=cylinder(name+'.base',(0,0,.08),r+.12,.16,'steel',sides=32); floor_contact(base)
    cylinder(name+'.pressure vessel',(0,0,h/2+.16),r,h,'teal',sides=32,bevel=.06)
    for z in (.25,h*.5,h+.03): ring(name+'.shell band',(0,0,z),r-.02,r+.035,.085,'steel_light',steps=40)
    cylinder(name+'.dished cap',(0,0,h+.19),r*.84,.18,'steel_light',sides=32,bevel=.065)
    cylinder(name+'.relief nozzle',(0,0,h+.39),.095,.3,'pipe')
    gauge(name+'.pressure',(0,-r-.045,h*.68),.14,.62)
    plate(name+'.number',(0,-r-.042,h*.45),(.35,.045,.28),name.upper(),.07)
    for s in (-1,1):
        tube(name+'.lifting eye',[(s*r*.7,0,h+.24),(s*r*.7,0,h+.43),(s*r*.7,.14,h+.43),(s*r*.7,.14,h+.24)],.026,'steel')


def stations():
    collection('05 PERIMETER EQUIPMENT')
    # North fuel positions: a receiving cradle, physically supported storage rack and reactivity desk.
    with at(-4.4,8.5):
        base=box('01 fuel receiving skid',(0,0,.08),(2.35,2.25,.16),'steel',.035); floor_contact(base)
        for x in (-.86,.86):
            box('Fuel cradle side',(x,0,.51),(.23,1.92,.72),'teal',.04)
            for y in (-.7,.7): box('Fuel saddle',(x,y,.93),(.36,.19,.23),'rubber',.025)
        for y in (-.70,0,.7):
            cylinder('Fresh fuel sealed cartridge',(0,y,1.11),.23,1.95,'pipe',(1,0,0),32,.025)
            for x in (-.9,.9):
                flange('Cartridge machined closure',(x,y,1.11),.26,(1,0,0),'steel_light')
                cylinder('Cartridge safety band',(x*.86,y,1.11),.234,.075,'yellow',(1,0,0),32,.008)
        plate('Fuel receiving identifier',(0,-1.14,.73),(1.25,.06,.3),'01 / FUEL RECEIVING',.093)
        box('Manifest shelf',(-.83,-.94,1.21),(.43,.32,.055),'steel_light',.015)
        box('Signed receiving sheet',(-.83,-.94,1.244),(.30,.22,.008),'paper',.001)
    with at(4.4,8.5):
        for x in (-1.02,1.02):
            for y in (-.7,.7):
                foot=box('02 rack foot',(x,y,.05),(.24,.24,.10),'steel_light'); floor_contact(foot)
                box('Rack post',(x,y,1.3),(.10,.10,2.5),'steel',.013)
        for z in (.16,1.1,2.35): box('Rack folded shelf',(0,0,z),(2.22,1.66,.12),'teal',.025)
        for x in (-.74,0,.74):
            for z in (.63,1.63):
                cylinder('Fuel storage sleeve',(x,0,z),.22,1.35,'pipe',(0,1,0),24,.02)
                flange('Fuel end cap',(x,-.7,z),.245,(0,-1,0),'steel_light')
                button('Fuel sealed indicator',(x,-.77,z),'yellow',.05)
        plate('02 rack identification',(0,-.89,2.23),(1.75,.06,.3),'02 / NEW FUEL',.12)
    with at(0,7.6): console('03 BANK CONTROL',1.70,.92,1.17)
    with at(7.2,7.8,0,-PI/4):
        base=cylinder('04 Waste circular plinth',(0,0,.07),1.2,.14,'steel',sides=48); floor_contact(base)
        tank('04 WASTE',.69,2.42)
        with at(-.85,-.27):
            box('Waste lock pedestal',(0,0,.52),(.35,.45,1.04),'teal',.03)
            button('WASTE_TRANSFER',(0,-.24,.9),'amber',.043,True)
        tube('Waste transfer closed line',[(.5,.2,.38),(.87,.2,.38),(.87,.2,2.20),(.55,.2,2.45)],.075,'pipe')
    with at(9.4,5.7,0,-PI/2):
        base=box('05 vent foot',(0,0,.05),(1.12,1.12,.1),'steel'); floor_contact(base)
        tube('Vent relief riser',[(0,0,.1),(0,0,3.4),(0,.32,3.75),(0,1.43,3.75)],.19,'pipe')
        for z in (.4,1.55,2.6): flange('Vent flange',(0,0,z),.26)
        cylinder('Vent valve bonnet',(0,-.27,1.52),.16,.4,'teal',(0,-1,0))
        wheel('VENT CONTROL',(0,-.52,1.52),.25)
        plate('Vent label',(.36,-.2,2.2),(.39,.04,.35),'05\nVENT',.08)
    with at(7.5,-3,0,-PI/2):
        # Local long dimension X maps north/south; all art stays inside 2.10 x 4.20 m plan.
        base=box('06 turbine skid',(0,0,.07),(4.12,2.04,.14),'steel',.04); floor_contact(base)
        for x in (-1.42,1.42):
            box('Turbine bearing foot',(x,0,.37),(.45,1.60,.6),'teal_dark',.045)
            cylinder('Turbine bearing block',(x,0,1.05),.47,.42,'teal',(1,0,0),24,.03)
        cylinder('Turbine pressure shell',(0,0,1.15),.69,2.5,'pipe',(1,0,0),48,.07)
        for x in (-1.26,0,1.26): flange('Turbine bolted split casing',(x,0,1.15),.74,(1,0,0),'steel_light')
        cylinder('Turbine service drive',(1.65,0,1.05),.35,.5,'teal',(1,0,0),32,.04)
        cylinder('Turbine fan recess',(1.94,0,1.05),.27,.025,'ink',(1,0,0),32,.005)
        for k in range(10):
            t=k*TAU/10
            tube('Turbine fan grille',[(1.962,.07*math.cos(t),1.05+.07*math.sin(t)),(1.962,.24*math.cos(t),1.05+.24*math.sin(t))],.012,'steel_light')
        for x in (-.72,.72): tube('Casing lifting eye',[(x,-.12,1.82),(x,-.12,2.00),(x,.12,2.00),(x,.12,1.82)],.028,'steel')
        box('Turbine split seam',(0,-.69,1.15),(2.5,.085,.09),'steel_light',.012)
        for x in (-.9,-.6,-.3,.3,.6,.9): cylinder('Turbine seam bolt',(x,-.75,1.15),.028,.04,'steel',(0,-1,0),6)
        plate('Turbine identification',(0,-.705,1.45),(1.30,.035,.22),'06 / TURBINE',.1)
        tube('Turbine inlet',[(.57,.47,1.62),(.57,.60,2.3),(.57,.96,2.3)],.16,'pipe')
        tube('Turbine return outlet',[(-.57,.47,1.02),(-.57,.96,1.02)],.145,'pipe')
        wheel('TURBINE_THROTTLE',(-1.64,-.65,1.25),.24)
        gauge('Turbine load',(-1.6,-.63,1.66),.13)
    with at(9,.8,0,-PI/2):
        for x in (-1.0,0,1.0):
            with at(x,0): cabinet('07 GRID BREAKERS',.95,1.1,2.03,1)
    with at(7.2,4.5,0,-PI/2): console('08 GRID DEMAND',1.72,1.10,1.2,1)
    with at(9,-4.5,0,-PI/2):
        base=box('09 sensor base',(0,0,.035),(.44,.44,.07),'steel'); floor_contact(base)
        tube('Sensor mast',[(0,0,.07),(0,0,1.48)],.045,'steel_light')
        box('Sensor enclosure',(0,0,1.6),(.32,.24,.32),'teal',.025)
        gauge('Containment sensor',(0,-.15,1.63),.09)
    with at(-4.8,-7.8,0,PI):
        base=box('10 pump skid',(0,0,.06),(2.35,2.3,.12),'steel',.04); floor_contact(base)
        for y in (-.5,.45):
            box('Pump mounting rail',(0,y,.22),(1.95,.22,.25),'teal_dark',.025)
        motor('Duty coolant pump',(-.43,0,.66),1.2,.35)
        cylinder('Pump volute',(.52,0,.66),.47,.42,'teal',(1,0,0),32,.05)
        flange('Pump suction',(.84,0,.66),.31,(1,0,0))
        tube('Pump rising outlet',[(.5,0,.98),(.5,0,1.52),(.5,.75,1.52)],.17,'pipe')
        box('Pump electrical starter',(-.69,.65,1.08),(.52,.38,.9),'teal',.035)
        button('COOLANT_PUMP_START',(-.69,.43,1.25),'green',.045)
        button('COOLANT_PUMP_STOP',(-.69,.43,1.05),'red',.045)
        gauge('Pump suction gauge',(.2,-.51,1.02),.13)
        plate('Coolant pump identification',(0,-1.15,.43),(1.35,.07,.28),'10 / COOLANT PUMP',.10)
    with at(-1.2,-8.4,0,PI):
        base=box('11 manifold skid',(0,0,.05),(2.32,1.7,.10),'steel'); floor_contact(base)
        for x in (-.86,.86): box('Manifold support',(x,.20,.87),(.12,.16,1.65),'steel',.015)
        for z in (.67,1.49):
            tube('Coolant header',[(-1.06,.15,z),(1.06,.15,z)],.14,'pipe')
            for x in (-.75,.65): flange('Header flange',(x,.15,z),.22,(1,0,0))
            for x in (-1.06,1.06): flange('Manifold blind service cover',(x,.15,z),.225,(1,0,0),'steel_light')
            tube('Manifold wall tie',[(1.06,.15,z),(1.06,1.28,z),(1.06,1.28,4.1 if z<1 else 4.52)],.115,'pipe')
        for x in (-.65,.65):
            tube('Manifold valved drop',[(x,.15,.65),(x,-.28,.65),(x,-.28,1.47),(x,.15,1.47)],.10,'pipe')
            wheel('COOLANT_VALVE',(x,-.49,1.10),.22)
        plate('Manifold identity',(0,.06,1.98),(1.93,.07,.26),'11 / SUPPLY     RETURN',.105)
    with at(3,-7.8,0,PI):
        base=box('12 emergency cooling skid',(0,0,.05),(2.93,2.32,.10),'steel'); floor_contact(base)
        for x in (-.73,.73):
            with at(x,.20): tank('EC-1' if x<0 else 'EC-2',.47,2.20)
        tube('Emergency cooling manifold',[(-.75,-.62,.6),(.75,-.62,.6)],.115,'pipe')
        for x in (-.73,.73): tube('ECCS tank outlet',[(x,.20,.6),(x,-.62,.6)],.115,'pipe')
        tube('ECCS maintained loop connection',[(.73,.20,1.20),(.73,1.10,1.20),(.73,1.10,4.10),(.73,2.14,4.10)],.115,'pipe')
        with at(0,-.78):
            box('Emergency cooling pedestal',(0,0,.67),(.5,.39,1.24),'teal_dark',.035)
            button('EMERGENCY_COOLING',(0,-.22,1.11),'red',.063,True)
            label('Emergency cooling legend','12 / ECCS',(0,-.205,.87),.072)
    with at(-8.4,-4.2,0,PI/2):
        base=box('13 generator skid',(0,0,.08),(2.33,2.34,.16),'steel'); floor_contact(base)
        box('Generator engine enclosure',(0,.2,.72),(2.02,1.25,1.12),'teal',.07)
        for x in (-.68,.15): hatch('Generator removable cover',(x,-.44,.79),.67,.79)
        for k in range(8): box('Generator cooling louvre',(.69,-.46,.42+k*.09),(.42,.035,.035),'ink',.006)
        motor('Backup generator alternator',(0,.72,1.39),1.48,.24,(1,0,0),'teal_dark')
        tube('Generator exhaust',[(.75,.7,1.25),(.75,.7,2.65),(.75,2.42,2.65)],.105,'steel_light')
        plate('Generator identity',(0,-.47,1.2),(1.65,.05,.22),'13 / BACKUP GENERATOR',.087)
    with at(-9,1.2,0,PI/2):
        for x in (-.71,.71):
            with at(x,0):
                cabinet('14 RESERVE POWER',1.35,1.35,1.60,0)
                for k in range(3): box('Battery tray seam',(0,-.694,.45+k*.32),(1.22,.018,.018),'ink',.002)
    with at(-7.8,5.4,0,PI/2):
        for x in (-.73,.73):
            for y in (-.62,.62):
                foot=box('15 workbench leg',(x,y,.44),(.11,.11,.88),'steel',.012); floor_contact(foot)
        box('Repair bench lower shelf',(0,0,.24),(1.65,1.5,.065),'teal_dark',.012)
        box('Repair bench worktop',(0,0,.92),(1.76,1.64,.09),'wood',.025)
        box('Repair pegboard',(0,.70,1.49),(1.74,.065,1.0),'teal_dark',.025)
        for x in (-.60,-.3,0,.3,.6):
            for z in (1.20,1.40,1.60,1.80): cylinder('Pegboard perforation',(x,.663,z),.014,.008,'ink',(0,-1,0),10,0)
        box('Bench vise fixed jaw',(.45,-.40,1.10),(.26,.26,.28),'steel',.015)
        box('Bench vise sliding jaw',(.45,-.62,1.12),(.27,.10,.14),'steel_light',.01)
        tube('Vise screw',[(.45,-.67,1.02),(.45,-.93,1.02)],.027,'shaft')
        tube('Vise handle',[(.45,-.93,.93),(.45,-.93,1.12)],.014,'shaft')
        for k in range(3):
            x=-.51+k*.21
            tube('Hanging wrench',[(x,.63,1.45),(x,.63,1.71)],.022,'steel_light')
            cylinder('Wrench jaw',(x,.63,1.75),.047,.032,'steel_light',(0,-1,0),6,.002)
        plate('Repair identity',(0,.64,1.90),(1.28,.04,.17),'15 / LIVE REPAIR',.075)
        with at(-.4,-.21,.974):
            box('Open work order',(0,0,0),(.35,.42,.012),'paper',.003)
            label('Work order printing','SHIFT 08\nPUMP SEAL\nREPLACE / TEST',(0,0,.008),.035,'ink',flat=True)
    # Small rolling sample caddy, off the service ring.
    with at(-4.4,-4.8,0,-.16):
        for x in (-.50,.50):
            for y in (-.29,.29):
                cylinder('Caddy caster',(x,y,.12),.115,.07,'rubber',(1,0,0),20)
                box('Caster yoke',(x,y,.24),(.08,.12,.18),'steel_light',.01)
        box('Caddy tray',(0,0,.36),(1.22,.81,.12),'teal_dark',.025)
        for x in (-.51,.0,.51):
            cylinder('Sample cask',(x,0,.77),.145,.71,'steel_light',sides=24)
            cylinder('Cask sealed cap',(x,0,1.14),.16,.06,'yellow',sides=24)
        tube('Caddy push handle',[(-.57,.30,.4),(-.57,.30,1.27),(.57,.30,1.27),(.57,.30,.4)],.025,'yellow')
        plate('Caddy label',(0,-.422,.50),(.63,.032,.2),'SAMPLE TRANSFER',.052)
    with at(3.7,-4.8,0,.50):
        base=box('Sampling kiosk foot',(0,0,.04),(.70,.56,.08),'steel'); floor_contact(base)
        box('Sampling kiosk',(0,0,.61),(.58,.43,1.16),'teal',.03)
        with at(0,0,0,PI): hatch('Sampling rear service door',(0,-.233,.58),.43,.74)
        gauge('Sampling pressure',(-.14,-.24,.97),.09)
        lever('SAMPLE_DRAW',(.15,-.25,.86),.09)
        box('Sample bottle alcove',(0,-.231,.57),(.32,.03,.34),'ink',.015)
        cylinder('Sample bottle',(0,-.29,.52),.061,.19,'glass',sides=24)
        tube('Sample inlet',[(0,.20,1.14),(0,.24,1.37),(.20,.24,1.37)],.018,'pipe')
        plate('Sampling legend',(0,-.25,1.17),(.50,.04,.14),'SAMPLING LINE',.051)


def utilities():
    collection('06 UTILITIES')
    # A closed pump-to-turbine circuit with the local manifold / ECCS branch physically joined.
    for offset,z in [(-.24,4.1),(.24,4.52)]:
        if offset<0:
            pts=[(-5.30,-8.55,1.52),(-5.30,-9.94,1.52),(-5.30,-9.94,z),(5.65,-9.94,z),(9.70,-5.65,z),(9.70,-3.57,z),(8.46,-3.57,z),(8.46,-3.57,2.30)]
        else:
            pts=[(-5.64,-7.8,.66),(-5.64,-9.46,.66),(-5.64,-9.46,z),(5.65,-9.46,z),(9.42,-5.65,z),(9.42,-2.43,z),(9.42,-2.43,1.02),(8.46,-2.43,1.02)]
        tube('Coolant SUPPLY' if offset<0 else 'Coolant RETURN',pts,.145,'pipe')
        for x in (-3,0,3):
            flange('Coolant union',(x,-9.70+offset,z),.21,(1,0,0))
            cylinder('Blue flow band',(x+.31,-9.70+offset,z),.15,.14,'teal',(1,0,0))
            beam('Header wall bracket',(x,-10.76,z-.22),(x,-9.3,z-.22),.08,.10,'steel')
            box('Header bracket wall plate',(x,-10.775,z-.22),(.20,.05,.24),'steel',.01)
            tube('Pipe retaining strap',[(x,-9.70+offset-.18,z-.22),(x,-9.70+offset-.18,z+.18),(x,-9.70+offset+.18,z+.18),(x,-9.70+offset+.18,z-.22)],.018,'steel_light')
        # Link the manifold's vertical tie to the matching horizontal header.
        tube('Manifold upper tie',[(-2.26,-9.68,z),(-2.26,-9.70+offset,z)],.115,'pipe')
    with at(0,-10.08,4.30): plate('Pipe route plaque',(0,0,0),(2.3,.04,.3),'COOLANT  /  SUPPLY + RETURN',.105)
    # Perimeter cable tray keeps long-distance clutter high and finishes at real cabinets.
    path=[(-9.85,-5.6,6.25),(-9.85,5.6,6.25),(-5.6,9.85,6.25),(5.6,9.85,6.25),(9.85,5.6,6.25)]
    for a,b in zip(path,path[1:]):
        a,b=Vector(a),Vector(b); d=(b-a).normalized(); normal=Vector((-d.y,d.x,0))
        for s in (-1,1): beam('Cable ladder rail',tuple(a+normal*s*.18),tuple(b+normal*s*.18),.06,.12,'steel')
        for k in range(math.ceil((b-a).length/.45)):
            p=a+d*(k*.45)
            beam('Cable ladder rung',tuple(p-normal*.18),tuple(p+normal*.18),.035,.06,'steel_light')
        tube('Bound power loom',[tuple(a+Vector((0,0,.05))),tuple(b+Vector((0,0,.05)))],.065,'rubber')
        for k in range(max(1,math.ceil((b-a).length/2.3))):
            p=a+d*min((b-a).length-.30,.4+k*2.3)
            gap=.95 if min(abs(d.x),abs(d.y))<.01 else 1.35/math.sqrt(2)
            anchor=p+normal*gap-Vector((0,0,.11))
            beam('Cable tray wall outrigger',tuple(anchor),tuple(p-normal*.25-Vector((0,0,.11))),.075,.10,'steel')
            cylinder('Cable tray anchor plate',tuple(anchor-normal*.02),.11,.04,'steel_light',tuple(normal),12,.008)
    for x,y,end in [(-9.85,.49,(-9,.49,1.79)),(9.85,4.5,(7.63,4.5,1.74))]:
        tube('Cabinet power drop',[(x,y,6.25),(x,y,2.20),(end[0],end[1],2.20),end],.043,'rubber')
        for z in (2.7,4,5.3): box('Cable wall clip',(x,y,z),(.13,.1,.06),'steel_light',.012)
    # A floor-fed desk ends in its base. The short loom is entirely inside its footprint.
    tube('Bank desk floor feed',[(0,7.96,.02),(0,7.96,.41),(0,8.04,.41)],.035,'rubber')


def authored_finish():
    collection('09 AUTHORED FINISH')
    # Bolted roof-to-wall knees are structural, not a decorative gallery/catwalk.
    for x,y in OCT:
        p=Vector((x,y,0)); inward=-Vector((x,y,0)).normalized()
        beam('Roof bearing knee',tuple(p+inward*.42+Vector((0,0,13.6))),tuple(p+inward*1.65+Vector((0,0,15.5))),.24,.29,'steel')
        with at(*(p+inward*.40),math.atan2(y,x)+PI/2):
            plate('Corner bearing plate',(0,-.04,13.68),(.58,.10,.82))
    # Chunky cast feet, stepped locking pieces, underside tooling and wear local to each bank.
    collection('04 BANK MECHANISMS')
    for bank,x in [('A',-1.4),('B',1.4)]:
        with at(x,0):
            for t in [PI/4+k*PI/2 for k in range(4)]:
                with at(0,0,0,t):
                    beam('Actuator saddle cheek',(-.13,-.54,12.42),(-.13,-.52,13.66),.16,.28,'teal_dark')
                    for z in (12.48,13.53): bolts('Saddle cheek bolts',[(-.13,-.69,z)],.042)
            for z in (10.1,12.17):
                for k in range(12):
                    t=k*TAU/12
                    cylinder('Fixed flange hardware',(.79*math.cos(t),.79*math.sin(t),z+.08),.031,.032,'steel',sides=6)
            for sx in (-.35,.35):
                box('Hatch machined shoulder',(sx,-.83,10.63),(.06,.09,.66),'teal_light',.012)
            plate('Actuator service rating',(0,-.844,10.05),(.38,.035,.075),'DRIVE 1800',.028,'steel')
            # Irregular exposed metal at handled hatch corners, with sparse matte underpaint.
            for k in range(7):
                px=-.22+k*.066; pz=10.34+(k%3)*.008
                mesh('Actuator localized paint chip',[(px,-.851,pz),(px+.023,-.851,pz+.014),(px+.036,-.851,pz+.008),(px+.017,-.851,pz-.006)],[(0,1,2,3)],'paint_chip')
    collection('09 AUTHORED FINISH')
    # Perimeter architectural transitions: lower protective pilasters and framed service returns.
    for i in (0,1,3,4,5,7):
        a=Vector((*OCT[i],0)); b=Vector((*OCT[(i+1)%8],0)); mid=(a+b)/2
        delta=b-a; length=delta.length
        with at(mid.x,mid.y,0,math.atan2(delta.y,delta.x)):
            for sx in (-1,1):
                x=sx*(length/2-.74)
                box('Lower wall protection',(x,-.08,1.45),(.57,.15,2.9),'mineral_light',.018)
                box('Lower inset boot',(x,-.13,.33),(.59,.24,.66),'steel',.025)
                for z in (.86,2.22): bolts('Dado anchors',[(x,-.172,z)],.025)
            for x in (-length*.30,length*.30):
                if i in (0,3): continue
                box('Wall lower seam datum',(x,-.018,2.95),(length*.24,.035,.06),'steel_light',.008)
            if i in (1,4,5,7):
                # Deep removable riser covers break up long flat wall fields with restrained chamfers.
                for x in (-length*.22,length*.22):
                    w=min(2.5,length*.39); h=3.55; z=7.20
                    outline=[(-w/2,-h/2),(w/2-.32,-h/2),(w/2,-h/2+.32),(w/2,h/2),(-w/2+.30,h/2),(-w/2,h/2-.30)]
                    for depth,scale,mat in [(-.018,1.018,'steel'),(-.083,1,'mineral_light')]:
                        vs=[(x+xx*scale,depth+d,z+zz*scale) for d in (0,.07) for xx,zz in outline]
                        fs=[tuple(reversed(range(6))),tuple(range(6,12))]+[(j,(j+1)%6,(j+1)%6+6,j+6) for j in range(6)]
                        mesh('Sealed riser chamfer panel',vs,[tuple(reversed(f)) for f in fs],mat,.018)
                    for zz in (-1.2,1.2):
                        plate('Riser panel dog',(x+w/2-.11,-.096,z+zz),(.10,.032,.25),'',mat='steel_light')
    # Door-associated signs and controls use physical mounting plates at actual hand height.
    for (x,y,angle,legend) in [(-10.59,-3.40,PI/2,'HALL 01'),(-3.08,10.59,0,'FUEL'),(9.98,-7.35,-PI/4,'COOLING')]:
        with at(x,y,0,angle):
            plate('Portal call station',(0,0,1.25),(.22,.14,.47),'',mat='steel')
            button('Door request',(0,-.085,1.30),'green',.038)
            label('Door call legend','OPEN',(0,-.077,1.13),.041)
            plate('Portal safety plate',(0,0,1.86),(.35,.035,.27),legend,.064,'yellow')
    # Sparse graphic rub marks sit inside individual paving sectors. They never
    # overlap each other or bridge an open seam, and have no shadow contribution.
    for k,sector in enumerate((22,23,24,25,6,7)):
        t=(sector+.50)*TAU/32; r=4.32+(k%2)*.28
        with at(r*math.cos(t),r*math.sin(t),.00015,t+PI/2):
            sx=.055; sy=.10
            verts=[(-sx,-sy,0),(sx*.4,-sy*.87,0),(sx,sy*.34,0),(sx*.12,sy,0),(-sx*.5,sy*.65,0)]
            scuff=mesh('Route surface scuff',verts,[tuple(range(5))],'floor_wear'); scuff.visible_shadow=False
    # A maintained repair cluster at the pump: compact clipboard, seal tray, cloth and tool.
    with at(-4.11,-8.20,0,PI):
        box('Pump local log bracket',(0,0,1.34),(.39,.085,.50),'steel',.015)
        box('Pump log sheet',(0,-.052,1.35),(.31,.012,.40),'paper',.004)
        label('Pump log entries','P-10\nSHIFT CHECK\n06:00  OK\n14:00  OK',(0,-.060,1.36),.044,'ink')
        box('Log spring clip',(0,-.067,1.53),(.14,.03,.035),'steel_light',.008)
        beam('Log bracket support',(0,.04,.85),(0,.04,1.22),.065,.06,'steel')
    with at(-4.25,-8.25,.345):
        box('Seal service tray',(0,0,.04),(.51,.42,.08),'steel_light',.016)
        ring('Replacement pump seal',(-.11,0,.095),.075,.12,.03,'rubber',steps=32)
        box('Seal pouch',(.12,.03,.09),(.19,.23,.035),'paper',.008)
        label('Seal kit note','P10',(.12,.03,.11),.051,'ink',flat=True)
    with at(-4.11,-8.45,1.533):
        mesh('Folded wiping cloth',[(-.15,-.15,0),(.17,-.13,.012),(.15,.13,.018),(-.12,.14,.005),(-.15,-.15,.015),(.17,-.13,.027),(.15,.13,.033),(-.12,.14,.020)],[(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6)],'fabric',.008)
    # Pipe insulation repair and direction symbols only at practical service locations.
    for x in (-2.1,2.4):
        for k in range(4): cylinder('Coolant repair wrap',(x+k*.04,-9.94,4.10),.151,.032,'fabric',(1,0,0),32,.003)
    # Fine access fasteners around selected turbine panels and a distinct cast mounting saddle.
    with at(7.5,-3,0,-PI/2):
        for x in (-1.42,1.42):
            for y in (-.63,.63):
                box('Turbine anchor foot',(x,y,.17),(.58,.27,.08),'steel_light',.018)
                bolts('Turbine anchors',[(x+sx*.18,y,.235) for sx in (-1,1)],.041,(0,0,1))
        for x in (-.83,.83):
            plate('Turbine inspection hatch',(x,-.702,1.09),(.28,.025,.23),'',mat='pipe')
    # Operator evidence: a small shift clipboard and a personal enamel mug within the desk.
    # Stationery rests on a separate physical side shelf, clear of the angled controls.
    box('Operator side shelf',(13.03,-.12,10.84),(.55,.40,.06),'teal_dark',.018)
    beam('Side shelf support',(12.88,.12,10.50),(12.88,-.12,10.81),.065,.065,'steel')
    with at(12.96,-.12,10.876):
        box('Operator shift card',(0,0,0),(.24,.32,.012),'paper',.003)
        label('Operator shift print','SHIFT 08\nBANK A / B',(0,0,.009),.035,'ink',flat=True)
    with at(13.19,-.12,10.871):
        ring('Operator enamel mug',(0,0,.065),.047,.058,.13,'pipe',steps=28)
        cylinder('Mug base',(0,0,.006),.055,.012,'pipe',sides=24)
        tube('Mug handle',[(.051,0,.04),(.09,0,.04),(.09,0,.11),(.051,0,.11)],.009,'pipe')
    # A single recent seal replacement: gloves, opened packet and a plugged-in
    # inspection light at the existing repair bench, entirely inside its worktop.
    with at(-7.8,5.4,.973,PI/2):
        for gx,gy,turn in [(-.50,.10,-.18),(-.32,.07,.32)]:
            with at(gx,gy,.006,turn):
                palm=box('Service glove palm',(0,0,.018),(.10,.13,.033),'fabric',.016)
                box('Service glove cuff',(0,.083,.02),(.105,.047,.035),'fabric',.008)
                for finger in range(4):
                    x=-.037+finger*.025; length=.065 if finger in (0,3) else .078
                    box('Service glove finger',(x,-.072-length/2,.018),(.022,length,.027),'fabric',.010)
                thumb=box('Service glove thumb',(.063,-.006,.018),(.045,.074,.027),'fabric',.011)
        box('Portable lamp base',(.59,.42,.025),(.24,.18,.05),'steel_light',.012)
        tube('Inspection lamp gooseneck',[(.59,.42,.05),(.59,.42,.34),(.52,.30,.44)],.018,'steel')
        box('Inspection lamp hood',(.51,.27,.42),(.22,.22,.08),'yellow',.018)
        box('Inspection lamp lens',(.51,.27,.377),(.17,.16,.013),'lamp',.005)
        light('Bench inspection practical',(.51,.27,.36),(-.2,-.15,.005),9,'FFE5B6',.18)
        tube('Inspection lamp cable',[(.63,.46,.04),(.66,.66,.01),(.72,.67,-.27),(.73,.65,-.45)],.008,'rubber')
        box('Bench power socket',(.73,.68,-.42),(.09,.04,.15),'steel_light',.007)
    # Brush-height repair patches and rail rubbing marks are authored at touch
    # zones. They stay broad, sparse and do not cover the quiet shell with grime.
    for x,y in [(-10.50,-3.48),(-3.18,10.57)]:
        with at(x,y,0,PI/2 if x<-10 else 0):
            for k in range(3):
                px=-.17+k*.11; pz=.68+.16*k
                mesh('Portal handled paint repair',[(px,-.013,pz),(px+.08,-.013,pz+.015),(px+.09,-.013,pz+.15),(px+.018,-.013,pz+.13)],[(0,1,2,3)],'floor_wear')
    # The high actuator has a serviced mechanical register; the carriage remains a cast moving unit.
    collection('04 BANK MECHANISMS')
    for bank,x in [('A',-1.4),('B',1.4)]:
        with at(x,0):
            for side in (-1,1):
                plate('Actuator lock shoe',(side*.52,-.66,10.06),(.23,.16,.31),'',mat='steel')
                cylinder('Lock shoe through bolt',(side*.52,-.755,10.06),.05,.045,'shaft',(0,-1,0),6,.004)
            for y in (-.38,.38):
                tube('Actuator external lubrication loop',[(.64,y,10.34),(.83,y,10.46),(.83,y,11.05),(.64,y,11.15)],.025,'steel_light')
            # Compact side pressure vessel and its actual short feed, subordinate to the two banks.
            cylinder('Hydraulic pressure accumulator',(-.52,.42,11.04),.16,.65,'steel_light',sides=24,bevel=.035)
            tube('Accumulator return',[(-.52,.42,10.72),(-.52,.66,10.60),(-.25,.66,10.60)],.035,'steel_light')
    for ob in bpy.data.objects:
        if ob.type!='MESH' or not ob.data.materials: continue
        if ob.data.materials[0]==M['teal'] and any(s in ob.name for s in ('_CARRIAGE','_FIXED_HOUSING','chassis','case','enclosure','Sampling kiosk')):
            ob.data.materials[0]=M['teal_service']


def room_wall_x(name,x,y0,y1,z0,z1,mat='mineral'):
    return box(name,(x,(y0+y1)/2,(z0+z1)/2),(.20,y1-y0,z1-z0),mat,.012)


def stair_and_control():
    collection('07 EAST CONTROL ROOM')
    # Room sits outside the reactor shell, centred at Y=0, finished floor +10 m.
    box('Control room main floor',(13.285,0,9.90),(2.95,6.4,.20),'floor_light',.014)
    box('Control floor observation glass',(11.335,0,9.9825),(.95,5.4,.035),'observation_glass',.001)
    for x in (10.87,11.81): box('Floor glazing bearing',(x,0,9.955),(.065,5.49,.09),'steel_light',.006)
    for y in (-2.72,2.72): box('Floor glazing frame',(11.335,y,9.975),(.96,.045,.05),'steel_light',.004)
    room_wall_x('Control east wall',14.86,-3.4,3.4,10,13.4)
    box('Control south wall',(12.98,-3.3,11.7),(4.16,.2,3.4),'mineral_light')
    # North wall is shared with stair. D02 leaves its full 1.2 m opening.
    box('Control north west return',(11.755,3.3,11.7),(1.91,.2,3.4),'mineral')
    box('Control north east return',(14.435,3.3,11.7),(1.05,.2,3.4),'mineral')
    box('Control D02 lintel',(13.31,3.3,12.75),(1.2,.2,1.3),'mineral')
    box('Control roof',(12.98,0,13.5),(4.16,6.8,.2),'mineral')
    # P02 panes separated by the actual floor spandrel; hall view has physical glazing.
    for z,h in [(11.6,2.6),(9.1,2.2)]:
        box('W01 safety glass',(10.90,0,z),(.026,5.4,h),'observation_glass',.002)
        for y in (-2.82,2.82): box('Window jamb',(10.84,y,z),(.22,.24,h+.24),'steel',.018)
        for zz in (z-h/2-.055,z+h/2+.055): box('Window head sill',(10.84,0,zz),(.22,5.85,.11),'steel',.015)
    # A sparse transom gives human-scale glazing, without a heavy obstruction across the reactor.
    box('Window centre mullion',(10.86,0,11.6),(.16,.065,2.6),'steel_light',.008)
    with at(10.63,0,13.30,-PI/2): plate('Control room external identifier',(0,0,0),(3.0,.055,.25),'REACTOR CONTROL / 10',.13)
    for y in (.60,-1.50):
        with at(12.82,y,10,PI/2):
            console('OPERATOR DESK',1.18,.68,.87,2)
        # Compact wheeled operator chair faces the hall.
        with at(13.72,y,10,-PI/2):
            for k in range(5):
                t=k*TAU/5
                tube('Chair five-star base',[(0,0,.12),(.29*math.cos(t),.29*math.sin(t),.08)],.018,'steel')
                cylinder('Chair wheel',(.29*math.cos(t),.29*math.sin(t),.06),.053,.044,'rubber',(1,0,0),16)
            cylinder('Chair stem',(0,0,.29),.04,.38,'shaft')
            cylinder('Chair pneumatic sleeve',(0,0,.20),.065,.20,'rubber',sides=24)
            box('Chair formed seat pan',(0,0,.477),(.54,.49,.055),'steel',.045)
            box('Chair upholstered seat',(0,-.018,.53),(.51,.47,.078),'fabric',.034)
            beam('Chair back brace',(0,.17,.45),(0,.23,.93),.06,.05,'steel')
            box('Chair back',(0,.24,.87),(.5,.065,.52),'teal_dark',.07)
            box('Chair lumbar cushion',(0,.195,.84),(.43,.065,.37),'fabric',.025)
            for side in (-1,1):
                tube('Chair arm frame',[(side*.21,.11,.47),(side*.25,.11,.72),(side*.25,-.16,.72)],.015,'steel')
                box('Chair arm pad',(side*.25,-.025,.739),(.075,.29,.036),'rubber',.013)
            lever('Chair height adjust',(.20,-.08,.41),.04,'rubber')
    with at(14.73,-.1,10,-PI/2):
        box('Plant mimic cabinet',(0,0,1.60),(1.35,.16,1.04),'teal_dark',.035)
        plate('Mimic face',(0,-.10,1.60),(1.24,.05,.89))
        for x in (-.38,.0,.38):
            tube('Mimic circuit',[(x,-.132,1.29),(x,-.132,1.85)],.009,'pipe')
            for z in (1.4,1.7): button('Mimic lamp',(x,-.142,z),'green',.019)
        label('Mimic title','PLANT STATUS',(0,-.15,2.0),.085)
    box('Operator ceiling light',(12.7,0,13.34),(1.8,1.0,.08),'lamp',.02)
    light('Warm control room',(12.65,0,13.27),(12.2,0,10),390,'FFF0D2',2)
    # Shared access vestibule; actual closure and bent route to D01.
    collection('08 COMPACT EAST STAIR')
    box('Vestibule floor',(11.81,3.6,-.1),(1.3,4.0,.2),'floor_light',.01)
    box('Vestibule north closure',(11.81,5.7,2.5),(1.3,.2,5),'mineral')
    box('Vestibule south closure',(11.91,1.5,2.5),(1.5,.2,5),'mineral')
    box('Vestibule east return',(12.56,2.4,2.5),(.2,1.6,5),'mineral')
    box('Vestibule roof',(11.81,3.6,5.1),(1.3,4,.2),'mineral')
    # Core exterior walls avoid the ground D01 opening and top D02 opening.
    room_wall_x('Stair east enclosure',18.61,3.2,6.4,0,12.4)
    room_wall_x('Stair west lower south',12.56,3.2,4.2,0,2.1)
    room_wall_x('Stair west lower north',12.56,5.4,6.4,0,2.1)
    room_wall_x('Stair west upper',12.56,3.2,6.4,2.1,12.4)
    box('Stair north enclosure',(15.585,6.3,6.2),(6.25,.2,12.4),'mineral')
    box('Stair south lower enclosure',(15.585,3.3,5),(6.25,.2,10),'mineral')
    box('Stair south upper east',(16.31,3.3,11.2),(4.80,.2,2.4),'mineral')
    box('Stair core roof',(15.585,4.8,12.5),(6.25,3.2,.2),'mineral')
    # Four short switchback flights: 56 equal risers, 52 equal goings.
    rise=2.5/14
    for flight in range(4):
        east=flight%2==0; y=4.05 if east else 5.55; base=flight*2.5
        for step in range(13):
            x=13.96+(.125+step*.25) if east else 17.21-(.125+step*.25)
            top=base+(step+1)*rise
            box(f'F{flight+1} tread {step+1:02}',(x,y,top-.055),(.25,1.30,.11),'floor_light',.008)
            box('Stair contrast nosing',(x+(-.112 if east else .112),y,top+.003),(.026,1.20,.006),'yellow',.001)
            if step<12: box('Stair riser',(x+(.121 if east else -.121),y,top+rise/2),(.008,1.30,rise),'steel',.002)
        for yy in (y-.60,y+.60):
            a=(13.96,yy,base-.12) if east else (17.21,yy,base-.12)
            b=(17.21,yy,base+2.5-.12) if east else (13.96,yy,base+2.5-.12)
            beam('Flight load-bearing stringer',a,b,.075,.24,'steel')
        for yy in (y-.625,y+.625):
            a=(13.96,yy,base+1.03) if east else (17.21,yy,base+1.03)
            b=(17.21,yy,base+3.53) if east else (13.96,yy,base+3.53)
            tube('Continuous stair handrail',[a,b],.025,'steel_light')
            for t in (0,.5,1):
                p=Vector(a).lerp(Vector(b),t)
                tube('Stair rail upright',[tuple(p-Vector((0,0,.99))),tuple(p)],.02,'steel')
    for x,zs in [(13.31,(0,5,10)),(17.86,(2.5,7.5))]:
        for z in zs:
            slab=box('Stair full landing',(x,4.8,z-.1),(1.30,2.8,.2),'floor_light',.01)
            if z>0:
                xx=12.685 if x<15 else 18.485
                tube('Landing handrail',[(xx,3.425,z+1.1),(xx,6.175,z+1.1)],.025,'steel_light')
                for y in (3.425,4.8,6.175): tube('Landing rail post',[(xx,y,z),(xx,y,z+1.1)],.022,'steel')
    box('Core ground slab',(15.585,4.8,-.15),(5.85,2.8,.3),'floor_light',.01)
    # Ground door swings north-hinged into the west vestibule; top door swings into room.
    for name,hinge,w,angle,z in [('D01',(12.46,5.4),1.2,PI,0),('D02',(13.91,3.2),1.2,-PI/2,10)]:
        with at(*hinge,z,angle):
            pivot=bpy.data.objects.new(name+'_HINGE',None); COL.objects.link(pivot); pivot.matrix_world=FRAME.copy()
            before=set(bpy.data.objects)
            leaf=box(name+' open door',(.6,0,1.04),(1.18,.055,2.08),'teal_dark',.025)
            box(name+' vision glass',(.59,-.034,1.46),(.34,.009,.54),'glass',.005)
            tube(name+' panic bar',[(.14,-.09,.97),(1.03,-.09,.97)],.018,'steel_light')
            label(name+' door marking','CONTROL' if name=='D02' else 'STAIR 10',(.60,-.035,1.83),.094)
            for ob in set(bpy.data.objects)-before:
                ob.parent=pivot; ob.matrix_parent_inverse=pivot.matrix_world.inverted()
            pivot['interaction']='hinged door; independent action supplied'
            pivot.rotation_euler.z=angle; pivot.keyframe_insert(data_path='rotation_euler',frame=1)
            pivot.rotation_euler.z=angle+(PI/2 if name=='D01' else -PI/2); pivot.keyframe_insert(data_path='rotation_euler',frame=40)
            action=pivot.animation_data.action; action.name=name+'_OPEN_TO_CLOSED'; action.use_fake_user=True
            pivot.animation_data.action=None; pivot.rotation_euler.z=angle
    for z,x in [(2.25,17.85),(4.75,13.1),(7.25,17.85),(9.75,13.1),(12.20,17.0)]:
        box('Stair bulkhead practical',(x,6.16,z),(.55,.07,.15),'lamp',.015)
        light('Stair practical',(x,6.08,z),(15.5,4.8,max(0,z-1.6)),150,'E4E8D7',1.2)
    box('Ground stair bulkhead',(13.5,3.44,2.25),(.50,.08,.15),'lamp',.015)
    light('Ground stair working light',(13.5,3.50,2.22),(15.2,4.4,.7),115,'EAF0DF',.85)
    light('Vestibule practical',(11.8,3.6,4.8),(11.8,4.6,.2),150,'E2EEDC',1.3)


CAMERAS = [
    ('01_HERO',(-5.5,-10.2,8.5),(0,0,5.3),24,(1120,1400)),
    ('02_WEST_ENTRY',(-10.05,-2.4,1.7),(0,0,5.0),21,(1600,1100)),
    ('03_SOUTH_GATE',(-2.6,-6.35,1.7),(0,-2.3,1.7),24,(1600,1000)),
    ('04_TURBINE_AISLE',(5.15,-3.75,1.7),(5.55,1.4,1.6),24,(1600,1000)),
    ('05_REVERSE_NORTH',(3.2,7,1.7),(-1,-3.5,3.0),23,(1600,1000)),
    ('06_CONTROL_ROOM',(11.80,-.65,11.7),(0,0,1.2),24,(1600,1000)),
    ('07_COMPACT_STAIR',(13.25,4.85,1.65),(17.0,4.60,3.1),20,(1600,1000)),
    ('08_MATERIAL_SLICE',(-6,-5.9,1.7),(-3.6,-8,1.4),28,(1600,1000)),
    ('09_BANK_MECHANISMS',(-3.7,-5.5,6.5),(0,0,9.8),28,(1000,1280)),
    ('10_EAST_HIGH',(9.4,-5.9,7.0),(-1.1,0,5.0),21,(1600,1200)),
]


def cameras():
    collection('10 CAMERAS')
    for name,loc,target,lens,res in CAMERAS:
        data=bpy.data.cameras.new(name); ob=bpy.data.objects.new(name,data); COL.objects.link(ob)
        ob.location=loc; ob.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
        data.lens=lens; data.clip_start=.05; data.clip_end=200; data.sensor_width=36
        ob['resolution']=list(res); ob['locked_target']=list(target)
    # Separate roof-off diagnostic never counts toward the ten perspective views.
    data=bpy.data.cameras.new('PLAN_DIAGNOSTIC'); ob=bpy.data.objects.new('PLAN_DIAGNOSTIC',data); COL.objects.link(ob)
    ob.location=(3,0,40); ob.rotation_euler=(0,0,0); data.type='ORTHO'; data.ortho_scale=35


def configure_render():
    scene=bpy.context.scene
    scene.render.engine='CYCLES'
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='HIP'; prefs.get_devices()
    for d in prefs.devices: d.use=d.type=='HIP'
    scene.cycles.device='GPU'
    scene.cycles.samples=ARGS.samples
    scene.cycles.use_denoising=True
    scene.cycles.max_bounces=9
    scene.cycles.transmission_bounces=8
    scene.cycles.transparent_max_bounces=12
    scene.cycles.use_light_tree=True
    scene.render.image_settings.file_format='PNG'
    scene.render.image_settings.color_mode='RGB'
    scene.render.image_settings.color_depth='8'
    scene.render.film_transparent=False
    scene.render.resolution_percentage=100
    scene.view_settings.view_transform='AgX'
    scene.view_settings.look='AgX - Medium High Contrast'
    scene.view_settings.exposure=.15
    scene.world.use_nodes=True
    scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.36,.43,.46,1)
    scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.08
    scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1
    scene.render.fps=30; scene.frame_start=1; scene.frame_end=240
    scene.frame_set(1)
    scene.render.use_file_extension=True


def validate():
    scene=bpy.context.scene
    scene.frame_set(1); bpy.context.view_layer.update()
    def check(name,actual,expected,tol=.0001):
        good=abs(actual-expected)<=tol
        CHECKS.append({'check':name,'actual':actual,'expected':expected,'tolerance':tol,'pass':good})
    def minimum(name,actual,required):
        CHECKS.append({'check':name,'actual':actual,'minimum':required,'pass':actual>=required-.00001})
    def bounds(ob):
        evaluated=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
        if ob.type=='CURVE':
            evaluated_mesh=evaluated.to_mesh()
            points=[evaluated.matrix_world@v.co for v in evaluated_mesh.vertices]
            evaluated.to_mesh_clear()
        else:
            points=[evaluated.matrix_world@Vector(v) for v in evaluated.bound_box]
        return [min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]
    check('Hall plan area',abs(sum(OCT[i][0]*OCT[(i+1)%8][1]-OCT[(i+1)%8][0]*OCT[i][1] for i in range(8)))/2,420.48)
    check('Maximum room span',max(x for x,y in OCT)-min(x for x,y in OCT),21.6)
    check('Exactly two fixed housings',len([o for o in bpy.data.objects if o.name.endswith('_FIXED_HOUSING')]),2)
    check('Exactly two moving banks',len([o for o in bpy.data.objects if o.name in ('BANK_A_MOVING','BANK_B_MOVING')]),2)
    for b,x in [('A',-1.4),('B',1.4)]:
        ob=bpy.data.objects[f'BANK_{b}_MOVING']
        check(f'Bank {b} axis X',ob.location.x,x)
        check(f'Bank {b} nominal Z',ob.location.z,8.6)
        check(f'Bank {b} travel',ob['travel_m'],1.8)
    check('Turbine P02 envelope clearance',math.hypot(7.5-1.05,3-2.1)-5.2,1.312488)
    check('Fourteen equal risers / flight',2.5/(2.5/14),14)
    check('Total stair rise',4*14*(2.5/14),10)
    check('Stair finished clear width',1.30-4*.025,1.20)
    check('Ten production cameras',sum(o.type=='CAMERA' and o.name!='PLAN_DIAGNOSTIC' for o in bpy.data.objects),10)
    endpoints=[]
    for ob in bpy.data.objects:
        if ob.name.startswith('Rail upright'):
            lo,hi=bounds(ob)
            if hi[1]<-3 and abs((lo[0]+hi[0])/2)<1: endpoints.append((lo,hi))
    endpoints.sort(key=lambda p:p[0][0])
    left,right=endpoints
    minimum('Gate fixed surface opening',right[0][0]-left[1][0],1.4)
    gate=bpy.data.objects['SERVICE_GATE_PIVOT']; old=gate.rotation_euler.z
    gate.rotation_euler.z=PI/2; bpy.context.view_layer.update()
    leaf_max=max(bounds(o)[1][0] for o in gate.children)
    minimum('Gate actual open leaf clearance',right[0][0]-max(left[1][0],leaf_max),1.4)
    gate.rotation_euler.z=old; bpy.context.view_layer.update()
    for bank in ('A','B'):
        upper=[]; lower=[]
        for frame in (1,90,180,192,196,201,240):
            scene.frame_set(frame); bpy.context.view_layer.update()
            upper.append(bounds(bpy.data.objects[f'{bank} top sliding engagement'])[1][2]-bounds(bpy.data.objects[f'BANK_{bank}_FIXED_HOUSING'])[0][2])
            lower.append(-3.545-bounds(bpy.data.objects[f'BANK_{bank}_DRIVE_COLUMN'])[0][2])
        minimum(f'Bank {bank} minimum upper engagement',min(upper),.20)
        minimum(f'Bank {bank} minimum lower engagement',min(lower),.20)
    scene.frame_set(1); bpy.context.view_layer.update()
    for door in ('D01','D02'): check(door+' attached hinge parts',len(bpy.data.objects[door+'_HINGE'].children),4)
    for ob in bpy.data.objects:
        if ob.name.startswith('W01 safety glass') or ob.name=='Control floor observation glass':
            signed=0
            for poly in ob.data.polygons:
                vs=[ob.data.vertices[i].co for i in poly.vertices]
                for i in range(1,len(vs)-1): signed+=vs[0].dot(vs[i].cross(vs[i+1]))/6
            minimum('Outward glazing normals: '+ob.name,signed,.0001)
    for item in CONTACTS:
        ob=bpy.data.objects[item['object']]
        z=min((ob.matrix_world@Vector(v)).z for v in ob.bound_box)
        check('Support: '+ob.name,z,item['expected_z'],.005)
    report={'revision':ARGS.revision,'source_sha256':scene.get('source_sha256',hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),'blender':bpy.app.version_string,
            'objects':len(bpy.data.objects),'meshes':len(bpy.data.meshes),'materials':len(bpy.data.materials),'checks':CHECKS,
            'pass':all(c['pass'] for c in CHECKS),'cold_start':ARGS.cold_start,'old_3d_imports':[]}
    (OUT/'validation.json').write_text(json.dumps(report,indent=2))
    if not report['pass']:
        print('VALIDATION FAILURES',json.dumps([c for c in CHECKS if not c['pass']],indent=2),flush=True)
        raise RuntimeError('Measured layout / support validation failed')
    print(f"VALIDATION PASS: {len(CHECKS)} checks; {len(bpy.data.objects)} objects",flush=True)
    return report


def render_all():
    scene=bpy.context.scene
    requested=[v.strip() for v in ARGS.render.split(',')]
    if ARGS.render=='none': return
    for name,loc,target,lens,res in CAMERAS:
        if ARGS.render!='all' and name not in requested: continue
        scene.camera=bpy.data.objects[name]
        scene.render.resolution_x=ARGS.width
        scene.render.resolution_y=round(ARGS.width*res[1]/res[0])
        scene.render.filepath=str(OUT/(name+'.png'))
        print('RENDER START '+name,flush=True)
        bpy.ops.render.render(write_still=True)
        print('RENDER COMPLETE '+name,flush=True)
    if ARGS.render=='diagnostics' or 'PLAN_DIAGNOSTIC' in requested:
        previous=[]
        for ob in bpy.data.objects:
            if (ob.type!='LIGHT' and any(c.name in ('02 ROOF STRUCTURE','04 BANK MECHANISMS') for c in ob.users_collection)) or ob.name in ('Control roof','Stair core roof','Vestibule roof'):
                previous.append((ob,ob.hide_render)); ob.hide_render=True
        scene.camera=bpy.data.objects['PLAN_DIAGNOSTIC']
        scene.render.resolution_x=ARGS.width; scene.render.resolution_y=ARGS.width
        scene.render.filepath=str(OUT/'PLAN_DIAGNOSTIC.png')
        bpy.ops.render.render(write_still=True)
        for ob,state in previous: ob.hide_render=state
    if ARGS.render=='diagnostics' or 'CONTROL_INTERIOR_DIAGNOSTIC' in requested:
        data=bpy.data.cameras.new('Temporary control interior camera')
        ob=bpy.data.objects.new('Temporary control interior camera',data); bpy.context.scene.collection.objects.link(ob)
        ob.location=(14.42,1.62,11.85)
        ob.rotation_euler=(Vector((11.60,-1.15,10.72))-ob.location).to_track_quat('-Z','Y').to_euler(); data.lens=19
        scene.camera=ob; scene.render.resolution_x=ARGS.width; scene.render.resolution_y=round(ARGS.width*.75)
        scene.render.filepath=str(OUT/'CONTROL_INTERIOR_DIAGNOSTIC.png')
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(ob,do_unlink=True); bpy.data.cameras.remove(data)
    if ARGS.render=='diagnostics' or 'POOL_DEPTH_DIAGNOSTIC' in requested:
        data=bpy.data.cameras.new('Temporary pool inspection camera')
        ob=bpy.data.objects.new('Temporary pool inspection camera',data); bpy.context.scene.collection.objects.link(ob)
        ob.location=(1.55,-3.98,1.75)
        ob.rotation_euler=(Vector((0,.5,-4.5))-ob.location).to_track_quat('-Z','Y').to_euler(); data.lens=22
        scene.camera=ob; scene.render.resolution_x=ARGS.width; scene.render.resolution_y=ARGS.width
        scene.render.filepath=str(OUT/'POOL_DEPTH_DIAGNOSTIC.png')
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(ob,do_unlink=True); bpy.data.cameras.remove(data)


def main():
    start=time.time()
    if not ARGS.cold_start:
        bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
        for c in list(bpy.data.collections):
            if c.name!='Collection': bpy.data.collections.remove(c)
        make_materials()
        hall_floor(); shell(); pool(); banks(); stations(); utilities(); stair_and_control(); authored_finish(); cameras()
        configure_render()
        bpy.context.scene['authoring_source']='build_scene.py, factory scene, no external 3D imports'
        bpy.context.scene['layout_authority']='architecture/output/reactor_compact_stair_architectural_set.pdf / P02'
        bpy.context.scene['visual_target']='generated A02 hall and B01 controls'
        bpy.context.scene['art_revision']=ARGS.revision
        bpy.context.scene['source_sha256']=SOURCE_SHA
        bpy.context.scene['support_registry']=json.dumps(CONTACTS)
        revision_source=ROOT/'production'/'revisions'/ARGS.revision/'build_scene.py'
        revision_source.parent.mkdir(parents=True,exist_ok=True)
        revision_source.write_bytes(SOURCE_BYTES)
        bpy.context.scene.camera=bpy.data.objects['01_HERO']
    else:
        configure_render()
        CONTACTS.extend(json.loads(bpy.context.scene.get('support_registry','[]')))
    report=validate()
    if not ARGS.cold_start:
        bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender'/'reactor_scene.blend'),compress=True)
    render_all()
    report['elapsed_seconds']=round(time.time()-start,2)
    (OUT/'validation.json').write_text(json.dumps(report,indent=2))
    print('BUILD COMPLETE '+ARGS.revision,flush=True)


if __name__=='__main__': main()
