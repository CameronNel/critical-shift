"""Neutral real-scale material and mapping diagnostics; never save the scene.
Run against the A2 native file. This is a labelled studio board, not room proof.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy
from mathutils import Vector

HERE=Path(__file__).resolve().parent

def main(label):
    original=Path(bpy.data.filepath);digest=hashlib.sha256(original.read_bytes()).hexdigest()
    source_scene=bpy.context.scene
    sc=bpy.data.scenes.new('A2 neutral material diagnostic');bpy.context.window.scene=sc
    sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=32;sc.cycles.use_denoising=True
    sc.render.threads_mode='FIXED';sc.render.threads=5
    sc.render.resolution_x=1920;sc.render.resolution_y=1080;sc.render.resolution_percentage=100
    sc.view_settings.view_transform=source_scene.view_settings.view_transform;sc.view_settings.look=source_scene.view_settings.look;sc.view_settings.exposure=-.1
    world=bpy.data.worlds.new('A2 neutral studio world');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.75,.75,.75,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.15;sc.world=world
    def box(name,loc,scale,mat):
        bpy.ops.mesh.primitive_cube_add(size=1,location=loc);ob=bpy.context.object;ob.name=name;ob.scale=scale
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        ob.data.materials.append(mat)
        bevel=ob.modifiers.new('Studio sample edge','BEVEL');bevel.width=.005;bevel.segments=2
        return ob
    base=bpy.data.materials.new('A2 neutral studio background');base.diffuse_color=(.11,.11,.11,1);base.use_nodes=True;base.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.11,.11,.11,1);base.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9
    expanded = 'A2 machine blue enamel' in bpy.data.materials
    box('Labelled studio board',(0,0,-.025),(1.9,1.8 if expanded else 1.22,.05),base)
    names=['Astra ivory painted steel','Service ochre enamel','Astra brushed fastener steel','Machined cast iron','Oiled iron','Warm mineral plaster','Basement coated concrete','Matte vulcanized rubber','Service brass','Astra formed stainless bellows']
    if expanded:names = ['A2 machine blue enamel','A2 waterbox oxide enamel','A2 hotwell graphite blue','Oxide orange enamel','Dense cast concrete'] + names
    lettering=bpy.data.materials.new('A2 studio lettering');lettering.use_nodes=True;bs=lettering.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.7,.7,.7,1);bs.inputs['Emission Color'].default_value=(.7,.7,.7,1);bs.inputs['Emission Strength'].default_value=.3
    label_strip=bpy.data.materials.new('A2 studio label strip');label_strip.use_nodes=True;label_strip.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.012,.015,.019,1);label_strip.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8
    for i,name in enumerate(names):
        x=-.72+(i%5)*.36;y=(.55 if expanded else .27)-(i//5)*.53
        ob=box('0.28m material sample / '+name,(x,y,.11),(.28,.28,.22),bpy.data.materials[name])
        if name=='Basement coated concrete':
            uv=ob.data.uv_layers.new(name='A2 floor metres')
            for li,loop in enumerate(ob.data.loops):p=ob.matrix_world@ob.data.vertices[loop.vertex_index].co;uv.data[li].uv=(p.x,p.y)
        box('Front-face material label / '+name,(x,y-.142,.055),(.27,.001,.035),label_strip)
        font=bpy.data.curves.new(name+' studio caption','FONT');font.body=name.replace('A2 ','').replace('Astra ','').replace(' painted steel',' paint').replace('Basement ','').replace('Matte vulcanized ','').replace('Warm mineral ','');font.size=.017;font.align_x='CENTER';font.materials.append(lettering)
        caption=bpy.data.objects.new(font.name,font);sc.collection.objects.link(caption);caption.location=(x,y-.143,.048);caption.rotation_euler=(math.pi/2,0,0)
    camera=bpy.data.cameras.new('A2 studio camera');camera.lens=48
    cam=bpy.data.objects.new(camera.name,camera);sc.collection.objects.link(cam);cam.location=(0,-3.3,3.9) if expanded else (0,-2.65,2.75);cam.rotation_euler=(Vector((0,0,.08))-cam.location).to_track_quat('-Z','Y').to_euler();sc.camera=cam
    for name,loc,target,watts,size in [('Neutral studio key',(-1,-.6,2),(0,0,0),280,1.7),('Neutral studio rim',(1.2,.7,1.5),(0,0,0),180,1.3)]:
        data=bpy.data.lights.new(name,'AREA');data.energy=watts;data.size=size;data.color=(1,1,1)
        light=bpy.data.objects.new(name,data);sc.collection.objects.link(light);light.location=loc;light.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    out=HERE/'renders-A2'/label;out.mkdir(parents=True,exist_ok=True)
    sc.render.filepath=str(out/'NEUTRAL_MATERIALS.png');bpy.ops.render.render(write_still=True)
    # A diagnostic checker uses exactly the same BOX projection and physical
    # coordinate scale as the production numeric maps. No production slot changes.
    checker=bpy.data.images.new('A2 diagnostic checker',width=512,height=512)
    import numpy as np
    yy,xx=np.indices((512,512));v=((xx//64+yy//64)%2)*.65+.15
    px=np.ones((512,512,4),np.float32);px[:,:,:3]=v[:,:,None];checker.pixels.foreach_set(px.ravel())
    mat=bpy.data.materials.new('A2 diagnostic checker / 0.24m tile');mat.use_nodes=True;nt=mat.node_tree;bs=nt.nodes['Principled BSDF'];bs.inputs['Roughness'].default_value=.65
    geo=nt.nodes.new('ShaderNodeNewGeometry')
    if source_scene.get('condenser_texture_projection')=='WORLD_TRIPLANAR_METRES':
        sys.path.insert(0,str(HERE))
        from condenser_finish_A2 import world_triplanar_image
        nt.links.new(world_triplanar_image(nt,geo,checker,.24,'Diagnostic / production projection'),bs.inputs['Base Color'])
    else:
        scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=1/.24;nt.links.new(geo.outputs['Position'],scale.inputs[0])
        texture=nt.nodes.new('ShaderNodeTexImage');texture.image=checker;texture.projection='BOX';texture.projection_blend=.18;nt.links.new(scale.outputs['Vector'],texture.inputs['Vector']);nt.links.new(texture.outputs['Color'],bs.inputs['Base Color'])
    for ob in sc.objects:
        if ob.type=='MESH' and ob.name.startswith('0.28m material sample'):ob.data.materials[0]=mat
    sc.render.filepath=str(out/'PHYSICAL_BOX_CHECKER.png');bpy.ops.render.render(write_still=True)
    # Verify the same physical mapping on the actual curved housings, fasteners,
    # long walls and floor. These explicitly named checker frames are diagnostics.
    bpy.context.window.scene=source_scene
    families=set(names)|{'Structural painted steel','Oxide orange enamel','Light oxide enamel','Safety burgundy','Charcoal impact dado','Dense cast concrete','Replacement floor patch'}
    for ob in source_scene.objects:
        if ob.type in {'MESH','CURVE','FONT'} and hasattr(ob.data,'materials'):
            for slot in ob.material_slots:
                if slot.material and slot.material.name in families:slot.material=mat
    source_scene.render.threads_mode='FIXED';source_scene.render.threads=5
    source_scene.cycles.samples=16;source_scene.cycles.use_adaptive_sampling=True;source_scene.cycles.adaptive_min_samples=8;source_scene.cycles.adaptive_threshold=.04
    for name in ['C02_HERO','C10_MATERIALS']:
        source_scene.camera=source_scene.objects[name]
        source_scene.render.filepath=str(out/('DIAGNOSTIC_CHECKER_'+name+'.png'))
        bpy.ops.render.render(write_still=True)
    assert hashlib.sha256(original.read_bytes()).hexdigest()==digest
    (out/'diagnostic.json').write_text(json.dumps({'source_sha256':digest,'scene_saved':False,'scope':'Neutral studio and explicitly named temporary checker diagnostics; not room completeness or art proof','projection':source_scene.get('condenser_texture_projection','LEGACY_WORLD_POSITION_BOX'),'projection_policy':'World-normal weighted planar samples in physical metres for corrected candidates; checker uses the exact production helper. Triplanar blend transitions on curved surfaces are disclosed, not claimed as distortion-free UVs.','sample_width_m':.28,'checker_tile_m':.24,'checker_square_m':.03,'resolution':[1920,1080],'studio_samples':32,'room_checker_samples':16,'actual_geometry_checker_cameras':['C02_HERO','C10_MATERIALS'],'source_materials':names,'color_management':{'view_transform':sc.view_settings.view_transform,'look':sc.view_settings.look,'exposure':sc.view_settings.exposure}},indent=2)+'\n')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--label',required=True);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);main(a.label)
