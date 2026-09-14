"""Supplemental saved-scene views. No saving or changes to the 18 room cameras.

CPU-only resource guard is mandatory. S07 is explicitly labelled a cutaway.
"""
import bpy, bmesh, sys, json
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(HERE))
import kit as k
from render import render_set
k.S=bpy.context.scene;k.group('Supplemental diagnostics only')
rev,selection=sys.argv[sys.argv.index('--')+1:sys.argv.index('--')+3]
extra=sys.argv[sys.argv.index('--')+3:]
samples=int(extra[0]) if extra else 32
width=int(extra[1]) if len(extra)>1 else 1920
height=int(extra[2]) if len(extra)>2 else 1080
views={
 'S01_LOCAL_U02':((8.70,1.15,5.15),(7.9,.10,5.42),38),
 'S02_LOCAL_CW':((7.5,6.25,3.50),(9.55,4.10,3.15),26),
 'S03_FULL_ROOF':((8.8,8.8,4.45),(3.8,4.4,5.50),20),
 'S04_GLASS':((2.05,1.85,1.60),(2.38,2.78,1.51),46),
 'S05_FEET':((4.7,6.15,.75),(3.1,7.05,.45),28),
 'S06_OPERATOR_WORK':((.05,4.5,1.40),(-1.02,4.34,1.02),45),
 'S07_U04_CUTAWAY':((7.5,.8,7.10),(3,4.05,5.9),36),
}
for name in selection.split(','):
    p,t,lens=views[name];cam=k.camera(name,p,t,lens)
    if name=='S07_U04_CUTAWAY':
        prefixes=('CD chest','bellow','U04 lower','U04 upper','U04 visible','U04 slab',
                  'U04 reveal','U04 pit','U04 underside','U04 side underside','Ceiling slab','opening header')
        for o in list(k.S.objects):
            if o.type not in {'MESH','CURVE','FONT'}:continue
            if not o.name.startswith(prefixes):o.hide_render=True;continue
            if o.type!='MESH':continue
            # True mesh section at x=3, retaining the west half and open throat.
            bm=bmesh.new();bm.from_mesh(o.data)
            transform=o.matrix_world.copy()
            for v in bm.verts:v.co=transform@v.co
            bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
                dist=.00001,plane_co=(3,0,0),plane_no=(1,0,0),clear_outer=True,clear_inner=False)
            for v in bm.verts:v.co=transform.inverted()@v.co
            bm.to_mesh(o.data);bm.free()
        light=k.light('Diagnostic section light',(5,3,7),(2,4,5.7),450,(1,.95,.85),3)
    # Label is genuinely rendered on a camera-facing plane; cannot be confused
    # with a normal uncut player view. No post-editing of the scene image.
    material=bpy.data.materials.new('Evidence caption white');material.use_nodes=True
    bs=material.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.8,.8,.8,1)
    bs.inputs['Emission Color'].default_value=(.8,.8,.8,1);bs.inputs['Emission Strength'].default_value=1
    font=bpy.data.curves.new('Evidence caption','FONT')
    font.body='LABELLED CUTAWAY / U04 RECTANGULAR THROAT / 2.5 x 1.5 m' if name=='S07_U04_CUTAWAY' else 'SUPPLEMENTAL / '+name[4:].replace('_',' ')+' / LOCAL SAVED SCENE'
    width=36/lens
    font.size=.015*width*.05; font.align_x='LEFT';font.materials.append(material)
    label=bpy.data.objects.new('Evidence caption',font);k.S.collection.objects.link(label)
    cam.data.clip_start=.01
    label.parent=cam;label.location=(-.45*width*.05,.235*width*.05,-.05)
    label.visible_shadow=False
    render_set(ROOT,rev,name,samples,width,height)
    bpy.data.objects.remove(label,do_unlink=True)
    bpy.data.objects.remove(cam,do_unlink=True)
