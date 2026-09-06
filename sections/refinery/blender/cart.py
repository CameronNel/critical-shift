"""Authentic Gullet cart plus refinery side-tipping cradle.

The serialized cart comes from the original pure geometry functions; no Blender
session is required for extraction. Only the loading/material bootstrap is
substituted in memory. Run --extract SOURCE_GULLET_DIR to regenerate the asset.
"""
from pathlib import Path
import json
import math

ASSET = Path(__file__).resolve().parent.parent / 'assets' / 'cart_geometry.json'
CART_POSITION = (-5.15, -3.65, .02)
PIVOT_POSITION = (-5.15, -2.85, .38)
TIP_ANGLE = math.radians(-50)


def extract(source):
    import hashlib
    import numpy as np
    source = Path(source)
    parts = sorted((source / 'source_parts').glob('build_mine.part*.pyfrag'))
    code = '\n'.join(p.read_text(encoding='utf-8') for p in parts)
    code = code.replace('ROOT=package_root()', 'ROOT=Path(__file__).resolve().parent')
    code = code.replace("self.materials=json.loads((ASSETS/'materials.json').read_text())", 'self.materials={}')
    import types, sys
    module=types.ModuleType('cart_source_extract');sys.modules[module.__name__]=module
    scope=module.__dict__;scope['__file__']=str(source/'geometry_source.py')
    exec(compile(code, str(source/'geometry_source.py'), 'exec'), scope)
    scene = scope['SceneData']()
    root = scope['ore_cart'](scene, (0,0,0), loaded=False, name='Refinery_authentic_cart')
    meshes = {k: {'vertices':m.vertices.tolist(),'faces':m.faces.tolist(), 'smooth':m.smooth,
                  'uv': None if m.uv is None else m.uv.tolist()} for k,m in scene.meshes.items()}
    items = [dict(name=o.name,mesh=o.mesh,material=o.material,parent=o.parent,
                  matrix=o.matrix.tolist(),meta=o.meta) for o in scene.items]
    empties = [dict(e, matrix=e['matrix'].tolist()) for e in scene.empties]
    points = np.concatenate([(o.matrix @ np.column_stack((scene.meshes[o.mesh].vertices,np.ones(len(scene.meshes[o.mesh].vertices)))).T).T[:,:3] for o in scene.items])
    result = {'provenance': {'source':str(source), 'function':'ore_cart', 'loaded':False,
        'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in parts},
        'bootstrap_substitutions':['ROOT only: no package discovery','SceneData material JSON replaced with empty mapping'],
        'geometry_modified':False, 'units':'metres'},
        'root':root,'bounds':[points.min(0).tolist(),points.max(0).tolist()],
        'meshes':meshes,'items':items,'empties':empties}
    ASSET.parent.mkdir(parents=True,exist_ok=True)
    ASSET.write_text(json.dumps(result,separators=(',',':')),encoding='utf-8')
    print('Cart extraction:',len(items),'mesh objects; bounds', result['bounds'])


def build():
    import bpy
    from mathutils import Matrix
    import geometry as g
    data=json.loads(ASSET.read_text(encoding='utf-8'))
    def obstacle(o):
        o['collision_role']='cart_obstacle'
        return o
    receiving=g.root('RECEIVING')
    g.marker('RECEIVING','INPUT',(-5.15,-3.65,1.13))
    g.marker('RECEIVING','OUTPUT',(-5.15,-1.25,.32))
    with g.use('03_CART_UNLOAD',parent=receiving):
        pivot=g.empty('CART_SIDE_TIP_PIVOT',PIVOT_POSITION,component='cart_tip_pivot',max_tip_degrees=50)
        pivot['tip_axis']='WORLD_X'
        pivot['source_geometry']=str(ASSET)
        cartroot=g.empty('AUTHENTIC_GULLET_CART',CART_POSITION,component='authentic_cart')
        cartroot.rotation_euler.z=-math.pi/2
        bpy.context.view_layer.update()
        saved=cartroot.matrix_world.copy();cartroot.parent=pivot;cartroot.matrix_world=saved
        base=Matrix.Translation(CART_POSITION)@Matrix.Rotation(-math.pi/2,4,'Z')
        mapping={data['root']:cartroot}
        for e in data['empties']:
            if e['name']==data['root']:continue
            obj=g.empty(e['name'],component=e.get('meta',{}).get('component','cart_detail'))
            obj.parent=mapping.get(e['parent'],cartroot)
            obj.matrix_world=base@Matrix(e['matrix']);mapping[e['name']]=obj
        mats={'paint_teal':'yellow','paint_ochre':'yellow','dark_steel':'darksteel',
              'steel':'steel','rubber':'rubber','paint_red':'red','label_cart':'ink'}
        for item in data['items']:
            m=data['meshes'][item['mesh']]
            obj=g.mesh(item['name'],m['vertices'],m['faces'],mats.get(item['material'],'darksteel'))
            obj.parent=mapping.get(item['parent'],cartroot)
            obj.matrix_world=base@Matrix(item['matrix'])
            obj['authentic_cart_part']=True
            obj['source_name']=item['name']
            for poly in obj.data.polygons:poly.use_smooth=m['smooth']
        # Entire captive platform rotates with the authentic unmodified cart.
        rails={}
        with g.use('03_CART_UNLOAD',parent=pivot):
            for yy in [-4.20,-3.10]:
                rails[yy]=g.box('Tip_cradle_rail',(-5.15,yy,.135),(2.72,.09,.05),'steel')
            for xx in [-6.29,-4.01]:
                g.box('Tip_cradle_crossmember',(xx,-3.65,.055),(.10,1.48,.10),'darksteel')
            for xx in [-6.11,-4.19]:
                g.box('Captive_wheel_guide',(xx,-3.65,.10),(.07,1.48,.07),'yellow')
            g.box('Cart_stop_buffer',(-3.89,-3.65,.40),(.12,1.02,.16),'rubber')
            for yy in [-4.32,-2.98]:
                g.rod('Cart_retaining_clamp',(-4.47,yy,.10),(-4.47,yy,.56),.032,'steel')
        bpy.context.view_layer.update()
        for e in data['empties']:
            if e.get('meta',{}).get('component')=='wheel':
                wheel=mapping[e['name']]
                yy=-4.20 if e['matrix'][0][3]>0 else -3.10
                point=(-5.15+e['matrix'][1][3],yy,.16)
                g.support(wheel,rails[yy],'LOCAL_-Z',[point])
        # Trunnions and floor-mounted frame stay fixed during the tip cycle.
        for xx in [-6.52,-3.78]:
            foot=obstacle(g.box('Tipper_floor_base',(xx,-3.28,.045),(.28,1.22,.09),'darksteel'))
            bearing=obstacle(g.box('Tipper_trunnion_support',(xx,-2.85,.27),(.22,.28,.36),'teal'))
            g.rod('Tipper_trunnion_axle',(xx-.13,-2.85,.38),(xx+.13,-2.85,.38),.068,'steel')
            g.support(bearing,foot,'WORLD_-Z',[(xx,-2.85,.09)])
        g.box('Tip_lock_housing',(-6.54,-3.70,.26),(.18,.28,.34),'teal')
        g.rod('Tip_lock_handle',(-6.54,-3.7,.39),(-6.54,-3.7,.65),.027,'red')
        # Open welded hopper with a real 1.10m-wide belt outlet, including rim.
        top=[(-6.20,-2.375,.65),(-4.10,-2.375,.65),(-4.10,-.825,.65),(-6.20,-.825,.65)]
        bottom=[(-5.75,-1.60,.24),(-4.55,-1.60,.24),(-4.55,-.95,.24),(-5.75,-.95,.24)]
        for i in range(4):
            j=(i+1)%4
            if i==2:
                # The outgoing upper/return belts, idlers and side skirts pass
                # through this full-height opening; no invisible closed face.
                for side,verts in enumerate([
                    [top[2],(-4.60,-.825,.65),(-4.60,-.95,.24),bottom[2]],
                    [(-5.70,-.825,.65),top[3],bottom[3],(-5.70,-.95,.24)]
                ]):
                    wall=obstacle(g.mesh('Receiving_hopper_outlet_cheek_%d'%side,verts,[(0,1,2),(0,2,3)],'darksteel'))
                    solid=wall.modifiers.new('Welded plate thickness','SOLIDIFY');solid.thickness=.025
                    obstacle(g.rod('Receiving_hopper_outlet_rim',verts[0],verts[1],.025,'yellow'))
                continue
            wall=obstacle(g.mesh('Receiving_hopper_wall_%d'%i,[top[i],top[j],bottom[j],bottom[i]],[(0,1,2),(0,2,3)],'darksteel'))
            solid=wall.modifiers.new('Welded plate thickness','SOLIDIFY');solid.thickness=.025
            obstacle(g.rod('Receiving_hopper_rolled_edge',top[i],top[j],.025,'yellow'))
        for xx in [-6.08,-4.22]:
            for yy in [-2.20,-1.0]:
                obstacle(g.box('Hopper_support_leg',(xx,yy,.23),(.09,.09,.46),'darksteel'))
        # Slotted cleanout below the spill edge; ore falls through open slots.
        for i in range(13):
            g.box('Cleanup_grate_bar',(-6.15+i*.167,-2.53,.025),(.034,.25,.05),'steel')
        g.box('Hopper_cleanout_access',(-5.15,-2.02,.27),(.60,.035,.22),'steel')
        g.rod('Hopper_cleanout_handle',(-5.32,-2.07,.28),(-4.98,-2.07,.28),.018,'darksteel')
    bpy.context.view_layer.update()
    return pivot,cartroot


if __name__=='__main__':
    import sys
    if '--extract' in sys.argv:extract(sys.argv[sys.argv.index('--extract')+1])
