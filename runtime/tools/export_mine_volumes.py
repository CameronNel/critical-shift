"""Sample authored volume density through Blender's shader evaluator into small 3D atlases."""
import hashlib
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector


def export_volumes(scene, instance, output, matrix):
    records=[]
    for o in instance.instance_collection.all_objects:
        if o.type!='MESH':continue
        for original in o.data.materials:
            if not original or not original.use_nodes:continue
            volume=next((n for n in original.node_tree.nodes if n.type=='PRINCIPLED_VOLUME'),None)
            if volume is None:continue
            world=instance.matrix_world @ matrix(o)
            bounds=[world @ Vector(v) for v in o.bound_box]
            minimum=np.array([min(v[i] for v in bounds) for i in range(3)])
            maximum=np.array([max(v[i] for v in bounds) for i in range(3)])
            nx,ny,nz=128,16,16;width,height=nx,ny*nz
            verts=[];faces=[];coordinates=[];uvs=[]
            for z in range(nz):
                for y in range(ny):
                    row=z*ny+y
                    for x in range(nx):
                        index=len(verts)
                        for dx,dy in ((0,0),(1,0),(1,1),(0,1)):
                            verts.append((x+dx,row+dy,0));uvs.append(((x+dx)/width,(row+dy)/height))
                            coordinates.append(tuple(minimum+(maximum-minimum)*np.array([(x+.5)/nx,(y+.5)/ny,(z+.5)/nz])))
                        faces.append(tuple(range(index,index+4)))
            mesh=bpy.data.meshes.new('CS_volume_samples');mesh.from_pydata(verts,[],faces);mesh.update()
            node=bpy.data.objects.new('CS_volume_samples',mesh);scene.collection.objects.link(node)
            layer=mesh.uv_layers.new(name='CS_VolumeUV')
            layer.data.foreach_set('uv',np.asarray(uvs,dtype=np.float32).ravel())
            material=original.copy();mesh.materials.append(material);nt=material.node_tree
            for name,values in [('CS_VolumeWorld',coordinates),('CS_VolumeObject',[tuple(world.inverted() @ Vector(v)) for v in coordinates]),
                                ('CS_VolumeGenerated',[tuple((np.array(v)-minimum)/(maximum-minimum)) for v in coordinates])]:
                attr=mesh.attributes.new(name=name,type='FLOAT_VECTOR',domain='POINT');attr.data.foreach_set('vector',np.asarray(values,dtype=np.float32).ravel())
            def attribute(name):
                n=nt.nodes.new('ShaderNodeAttribute');n.attribute_name=name;return n.outputs['Vector']
            for n in list(nt.nodes):
                if n.type=='TEX_COORD':
                    for socket,name in [('Object','CS_VolumeObject'),('Generated','CS_VolumeGenerated')]:
                        for link in list(n.outputs[socket].links):nt.links.new(attribute(name),link.to_socket)
                if n.type in {'TEX_NOISE','TEX_VORONOI','TEX_WAVE','TEX_MAGIC','TEX_GRADIENT','TEX_BRICK','TEX_CHECKER','TEX_WHITE_NOISE'} and not n.inputs['Vector'].is_linked:
                    nt.links.new(attribute('CS_VolumeGenerated'),n.inputs['Vector'])
                if n.type=='NEW_GEOMETRY':
                    for link in list(n.outputs['Position'].links):nt.links.new(attribute('CS_VolumeWorld'),link.to_socket)
            copied=nt.nodes[volume.name];out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output)
            for link in list(out.inputs['Volume'].links):nt.links.remove(link)
            emission=nt.nodes.new('ShaderNodeEmission')
            density=copied.inputs['Density']
            if density.is_linked:nt.links.new(density.links[0].from_socket,emission.inputs['Color'])
            else:emission.inputs['Color'].default_value=(density.default_value,)*3+(1,)
            nt.links.new(emission.outputs[0],out.inputs['Surface'])
            image=bpy.data.images.new('CS_volume_density',width=width,height=height,float_buffer=True)
            image.colorspace_settings.name='Non-Color'
            target=nt.nodes.new('ShaderNodeTexImage');target.image=image;nt.nodes.active=target
            bpy.context.window.scene=scene;bpy.ops.object.select_all(action='DESELECT');node.select_set(True);bpy.context.view_layer.objects.active=node
            scene.render.engine='CYCLES';scene.cycles.samples=1;scene.render.bake.margin=0;scene.render.bake.use_clear=True
            bpy.ops.object.bake(type='EMIT',uv_layer='CS_VolumeUV')
            file=output/'Surfaces'/('mine-volume-'+str(len(records))+'-density.exr')
            scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='32';scene.render.image_settings.exr_codec='ZIP'
            image.save_render(str(file),scene=scene)
            pixels=np.empty(width*height*4,dtype=np.float32);image.pixels.foreach_get(pixels);density_values=pixels.reshape(-1,4)[:,0]
            if not np.isfinite(density_values).all() or density_values.min()<0:raise ValueError('Invalid sampled volume density: '+o.name)
            record={'source':o.name,'minimum':minimum.tolist(),'maximum':maximum.tolist(),'color':list(volume.inputs['Color'].default_value),
                'anisotropy':float(volume.inputs['Anisotropy'].default_value),'grid':[nx,ny,nz],
                'densityMinimum':float(density_values.min()),'densityMaximum':float(density_values.max()),
                'densityMap':{'file':'Surfaces/'+file.name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'colorSpace':'linear','size':height}}
            records.append(record);print('CS_MINE_VOLUME_DENSITY',record,flush=True)
            bpy.data.objects.remove(node,do_unlink=True);bpy.data.meshes.remove(mesh);bpy.data.materials.remove(material);bpy.data.images.remove(image)
    return records
