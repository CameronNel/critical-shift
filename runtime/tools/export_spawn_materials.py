"""Bake source shader inputs into a delivery atlas; never bake scene lighting into albedo."""
import hashlib
import math
import os
from pathlib import Path

import bpy
import numpy as np
from export_spawn_view import export_view


UV = "CS_DeliveryUV"
SOURCE_UV = "CS_SourceUV"


def surface_opacity(material):
    """Retain constant transparent/Principled Mix Shader coverage for raster delivery."""
    tree=material.node_tree
    output=next(n for n in tree.nodes if n.type=="OUTPUT_MATERIAL" and n.is_active_output)
    def coverage(socket):
        if not socket.is_linked: return 0.0
        node=socket.links[0].from_node
        if node.type=="BSDF_TRANSPARENT": return 0.0
        if node.type=="BSDF_PRINCIPLED":
            if node.inputs["Alpha"].is_linked: raise ValueError("Linked glass alpha is unsupported: "+material.name)
            return float(node.inputs["Alpha"].default_value)
        if node.type=="MIX_SHADER":
            if node.inputs[0].is_linked: raise ValueError("Linked glass mix is unsupported: "+material.name)
            weight=float(node.inputs[0].default_value)
            return (1-weight)*coverage(node.inputs[1])+weight*coverage(node.inputs[2])
        raise ValueError("Unsupported glass coverage node: "+node.type)
    if any(n.type=="BSDF_TRANSPARENT" for n in tree.nodes): return coverage(output.inputs["Surface"])
    bsdf=next(n for n in tree.nodes if n.type=="BSDF_PRINCIPLED")
    # Pure refractive glass has no constant coverage equivalent in the built-in raster renderer.
    return 0.12 if bsdf.inputs["Transmission Weight"].default_value>0.01 else float(bsdf.inputs["Alpha"].default_value)


def constant_inputs(material):
    bsdf=next(n for n in material.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
    def constant(name): return not bsdf.inputs[name].is_linked
    return {"baseConstant":constant("Base Color"),"normalConstant":constant("Normal"),
        "metallicConstant":constant("Metallic"),"roughnessConstant":constant("Roughness"),
        "emissionConstant":constant("Emission Color") and constant("Emission Strength"),
        "surfaceOpacity":surface_opacity(material),
        "baseColor":list(bsdf.inputs["Base Color"].default_value),
        "metallic":float(bsdf.inputs["Metallic"].default_value),"smoothness":1-float(bsdf.inputs["Roughness"].default_value),
        "emissionColor":list(bsdf.inputs["Emission Color"].default_value),"emissionStrength":float(bsdf.inputs["Emission Strength"].default_value)}


def bake_surfaces(scene, objects, mappings, output, source_view):
    large,small,floor=[],[],[]
    exterior={o.name for o in bpy.data.collections.get("EXTERIOR_spawn-room").all_objects}
    for o in objects:
        name=o.name.removeprefix("CS_spawn-room_")
        if name=="V_LOCKER_porcelain_tiles": floor.append(o)
        else: (large if o.type=="MESH" and max(o.dimensions)>0.65 and name not in exterior else small).append(o)
    packages=[bake_atlas(scene,group,mappings,output,source_view,key) for group,key in ((large,"architecture"),(small,"props"),(floor,"floor"))]
    for atlas,package in enumerate(packages):
        for definition in package["definitions"]: definition["atlas"]=atlas
    package=packages[0]
    package["atlases"]=[p["maps"] for p in packages]
    package["definitions"]=[d for p in packages for d in p["definitions"]]
    package["meshes"]=sum(p["meshes"] for p in packages)
    return package


def bake_atlas(scene, objects, mappings, output, source_view, atlas_key):
    size = 2048 if atlas_key in {"floor","lettering"} else int(os.environ.get("CS_SURFACE_SIZE", "4096"))
    if size not in (2048, 4096, 8192):
        raise ValueError("Unsupported reviewed surface atlas resolution")
    meshes = [o for o in objects if o.type == "MESH" and len(o.data.polygons) and len(o.data.materials)]
    originals = list(dict.fromkeys(m for o in meshes for m in o.data.materials if m))
    copies, states, definitions, coordinate_attributes = {}, {}, [], {}
    for index, original in enumerate(originals):
        m = original.copy(); m.name = "CS_spawn_surface_" + atlas_key + "_" + str(index).zfill(3)
        copies[original] = m
        nt = m.node_tree
        bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf is None: raise ValueError("Unsupported source surface: " + original.name)
        # Explicitly retain the old UV input while baking into an additional UV layer.
        source_uv = nt.nodes.new("ShaderNodeUVMap"); source_uv.uv_map = SOURCE_UV
        for n in list(nt.nodes):
            if n.type in {"TEX_NOISE","TEX_VORONOI","TEX_WAVE","TEX_MAGIC","TEX_GRADIENT","TEX_BRICK","TEX_CHECKER","TEX_WHITE_NOISE"} and not n.inputs["Vector"].is_linked:
                coordinate_attributes["CS_Generated"]=("Generated",None)
                attribute=nt.nodes.new("ShaderNodeAttribute");attribute.attribute_name="CS_Generated"
                nt.links.new(attribute.outputs["Vector"],n.inputs["Vector"])
            if n.type == "TEX_IMAGE" and not n.inputs["Vector"].is_linked:
                nt.links.new(source_uv.outputs["UV"], n.inputs["Vector"])
            if n.type == "TEX_COORD":
                for link in list(n.outputs["UV"].links): nt.links.new(source_uv.outputs["UV"], link.to_socket)
                for socket in ("Generated", "Object"):
                    if not n.outputs[socket].is_linked: continue
                    frame = n.object if socket == "Object" else None
                    attr_name = "CS_Generated" if socket == "Generated" else "CS_Object_" + (frame.name if frame else "Self")
                    coordinate_attributes[attr_name] = (socket,frame)
                    attribute=nt.nodes.new("ShaderNodeAttribute"); attribute.attribute_name=attr_name
                    for link in list(n.outputs[socket].links): nt.links.new(attribute.outputs["Vector"],link.to_socket)
        out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output)
        root = out.inputs["Surface"].links[0].from_socket
        target = nt.nodes.new("ShaderNodeTexImage"); target.name = "CS_delivery_bake_target"
        emission = nt.nodes.new("ShaderNodeEmission")
        states[m] = (bsdf, out, root, target, emission)
        transmission = bsdf.inputs["Transmission Weight"].default_value
        alpha = bsdf.inputs["Alpha"].default_value
        definition={"key":m.name,"source":original.name,"transmission":float(transmission),
            "alpha":float(alpha),"transparent":transmission > 0.01 or alpha < 0.999 or any(n.type == "BSDF_TRANSPARENT" for n in nt.nodes)}
        definition.update(constant_inputs(original))
        emission_socket=bsdf.inputs["Emission Color"]
        if emission_socket.is_linked and emission_socket.links[0].from_node.type=="TEX_IMAGE" and all(not bsdf.inputs[k].is_linked for k in ("Base Color","Metallic","Roughness","Normal","Alpha","Emission Strength")):
            source_image=emission_socket.links[0].from_node.image
            folder=output/"Surfaces"/atlas_key;folder.mkdir(parents=True,exist_ok=True)
            extension=Path(source_image.filepath).suffix or ".png"
            file=folder/(m.name+"-source-emission"+extension)
            if source_image.packed_file: file.write_bytes(source_image.packed_file.data)
            else: file.write_bytes(Path(bpy.path.abspath(source_image.filepath,library=source_image.library)).read_bytes())
            definition.update(directEmission={"file":"Surfaces/"+atlas_key+"/"+file.name,"sha256":hashlib.sha256(file.read_bytes()).hexdigest(),
                "colorSpace":"sRGB","size":2**math.ceil(math.log2(max(source_image.size)))},
                baseColor=list(bsdf.inputs["Base Color"].default_value),metallic=float(bsdf.inputs["Metallic"].default_value),
                smoothness=1-float(bsdf.inputs["Roughness"].default_value),emissionStrength=float(bsdf.inputs["Emission Strength"].default_value))
        definitions.append(definition)
    for o in meshes:
        for slot in o.material_slots: slot.material = copies[slot.material]
        original_uv = o.data.uv_layers.active
        source_uv = o.data.uv_layers.new(name=SOURCE_UV, do_init=True)
        if original_uv:
            values = np.empty(len(original_uv.data)*2, dtype=np.float32)
            original_uv.data.foreach_get("uv",values); source_uv.data.foreach_set("uv",values)
        delivery = o.data.uv_layers.new(name=UV, do_init=False)
        o.data.uv_layers.active = delivery
        delivery.active_render = True
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes: o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    # Pack at physical scale despite authored parent/object scaling; restore exact mesh vertices afterwards.
    positions = {}
    for o in meshes:
        positions[o] = [v.co.copy() for v in o.data.vertices]
        for v in o.data.vertices: v.co = o.matrix_world @ v.co
    margin=max(4,size//1024)
    if atlas_key=="floor":
        for o in meshes:
            low=[min(v.co[i] for v in o.data.vertices) for i in (0,1)]
            extent=[max(v.co[i] for v in o.data.vertices)-low[i] for i in (0,1)]
            for loop,uv in zip(o.data.loops,o.data.uv_layers[UV].data):
                vertex=o.data.vertices[loop.vertex_index].co
                uv.uv=((vertex.x-low[0])/extent[0],(vertex.y-low[1])/extent[1])
    else:
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=margin/size, area_weight=0.0,
            correct_aspect=False, scale_to_bounds=True)
        bpy.ops.object.mode_set(mode="OBJECT")
    for o in meshes:
        for v, p in zip(o.data.vertices, positions[o]): v.co = p
        o.data.update()
    del positions
    # Bake one temporary joined mesh rather than compiling the scene once for each of 1,700 objects.
    # Store object/generated coordinates first: joining alone would change the procedural recipes.
    batches=[]
    for o in meshes:
        batch=o.copy(); batch.data=o.data.copy(); batch.parent=None; batch.matrix_world=o.matrix_world
        scene.collection.objects.link(batch); batches.append(batch)
        local=np.array([tuple(v.co) for v in batch.data.vertices],dtype=np.float32)
        low=local.min(axis=0); extent=np.maximum(local.max(axis=0)-low,1e-8)
        for name,(socket,frame) in coordinate_attributes.items():
            if socket == "Generated": values=(local-low)/extent
            elif frame is None: values=local
            else:
                transform=frame.matrix_world.inverted() @ o.matrix_world
                values=np.array([tuple(transform @ v.co) for v in o.data.vertices],dtype=np.float32)
            attribute=batch.data.attributes.new(name=name,type="FLOAT_VECTOR",domain="POINT")
            attribute.data.foreach_set("vector",values.ravel())
    bpy.ops.object.select_all(action="DESELECT")
    for o in batches: o.select_set(True)
    bpy.context.view_layer.objects.active=batches[0]
    bpy.ops.object.join()
    batch=bpy.context.view_layer.objects.active
    scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = 1
    scene.render.bake.margin = margin; scene.render.bake.use_clear = False
    scene.render.bake.use_selected_to_active = False
    folder = output / "Surfaces" / atlas_key; folder.mkdir(parents=True,exist_ok=True)
    files = {}

    def connect(nt, source, destination):
        if source.is_linked: nt.links.new(source.links[0].from_socket, destination)
        else: destination.default_value = source.default_value

    for channel in ("albedo", "metallic-smoothness", "normal", "emission"):
        image = bpy.data.images.new("CS_spawn_"+channel,width=size,height=size,alpha=True,float_buffer=True)
        image.colorspace_settings.name = "sRGB" if channel == "albedo" else "Non-Color"
        for m, (bsdf,out,root,target,emission) in states.items():
            nt = m.node_tree; target.image = image; nt.nodes.active = target
            for n in nt.nodes: n.select = n == target
            if channel == "normal": nt.links.new(root,out.inputs["Surface"])
            else:
                nt.links.new(emission.outputs[0],out.inputs["Surface"])
                for link in list(emission.inputs["Color"].links): nt.links.remove(link)
                for link in list(emission.inputs["Strength"].links): nt.links.remove(link)
                emission.inputs["Strength"].default_value=1
                if channel == "albedo": connect(nt,bsdf.inputs["Base Color"],emission.inputs["Color"])
                elif channel == "emission":
                    connect(nt,bsdf.inputs["Emission Color"],emission.inputs["Color"])
                    connect(nt,bsdf.inputs["Emission Strength"],emission.inputs["Strength"])
                else:
                    rgb=nt.nodes.new("ShaderNodeCombineColor"); rgb.mode="RGB"
                    connect(nt,bsdf.inputs["Metallic"],rgb.inputs["Red"])
                    invert=nt.nodes.new("ShaderNodeMath"); invert.operation="SUBTRACT"; invert.inputs[0].default_value=1
                    connect(nt,bsdf.inputs["Roughness"],invert.inputs[1]); nt.links.new(invert.outputs[0],rgb.inputs["Green"])
                    connect(nt,bsdf.inputs["Alpha"],rgb.inputs["Blue"])
                    nt.links.new(rgb.outputs[0],emission.inputs["Color"])
        print("CS_SURFACE_BAKE_START",atlas_key,channel,len(meshes),size,flush=True)
        bpy.ops.object.bake(type="NORMAL" if channel == "normal" else "EMIT",uv_layer=UV)
        if channel == "metallic-smoothness":
            # Alpha is numeric smoothness, not opacity. Straight/premultiplied saving
            # would divide metallic by smoothness and turn painted steel into metal.
            image.alpha_mode="CHANNEL_PACKED"
            pixels=np.empty(size*size*4,dtype=np.float32); image.pixels.foreach_get(pixels)
            pixels=pixels.reshape((-1,4)); pixels[:,3]=pixels[:,1]; pixels[:,1:3]=0
            image.pixels.foreach_set(pixels.ravel()); del pixels
        name="spawn-"+channel+(".exr" if channel=="emission" else ".png")
        image.filepath_raw=str(folder/name); image.file_format="OPEN_EXR" if channel=="emission" else "PNG"
        if channel == "emission":
            scene.render.image_settings.file_format="OPEN_EXR"
            scene.render.image_settings.color_mode="RGBA"
            scene.render.image_settings.color_depth="16"
            scene.render.image_settings.exr_codec="ZIP"
            image.save_render(str(folder/name),scene=scene)
        else: image.save()
        files["metallicSmoothness" if channel == "metallic-smoothness" else channel]={"file":"Surfaces/"+atlas_key+"/"+name,"sha256":hashlib.sha256((folder/name).read_bytes()).hexdigest(),
            "colorSpace":"sRGB" if channel=="albedo" else "linear","size":size}
        print("CS_SURFACE_BAKE_DONE",atlas_key,channel,flush=True)
        for state in states.values(): state[3].image=None
        bpy.data.images.remove(image)
    bpy.data.objects.remove(batch,do_unlink=True)
    # UV0 is the atlas, UV1 is reserved for Unity's lightmapper, UV2 retains original screen coordinates.
    for o in meshes:
        delivery=np.empty(len(o.data.loops)*2,dtype=np.float32);source=np.empty_like(delivery)
        o.data.uv_layers[UV].data.foreach_get("uv",delivery);o.data.uv_layers[SOURCE_UV].data.foreach_get("uv",source)
        for uv in list(o.data.uv_layers): o.data.uv_layers.remove(uv)
        for name,values in ((UV,delivery),("CS_LightmapUV",delivery),(SOURCE_UV,source)):
            layer=o.data.uv_layers.new(name=name,do_init=False);layer.data.foreach_set("uv",values)
        o.data.uv_layers.active_index=0;o.data.uv_layers[0].active_render=True
    for mapping in mappings:
        o=next((o for o in meshes if o.name==mapping["node"]),None)
        if o:
            mapping["materials"]=[slot.material.name for slot in o.material_slots]
            used=[d for d in definitions if d["key"] in mapping["materials"]]
            mapping["sourceUv"]=any(d.get("directEmission") for d in used)
            if atlas_key=="floor": mapping["deliveryUvAxes"]=[0,1]
            if mapping["sourceUv"] and any(not d.get("directEmission") and not all(d[k] for k in ("baseConstant","normalConstant","metallicConstant","roughnessConstant","emissionConstant")) for d in used):
                raise ValueError("Source image UVs require uniform companion surfaces: "+mapping["node"])
    # Avoid embedding the atlas four times per material in FBX; the manifest binds it explicitly in Unity.
    for m, (bsdf,out,root,target,emission) in states.items():
        m.node_tree.links.new(root,out.inputs["Surface"])
        for n in list(m.node_tree.nodes):
            if n.type=="TEX_IMAGE": m.node_tree.nodes.remove(n)
    return {"room":"spawn-room","uv":UV,"maps":files,"definitions":definitions,"displayLut":export_view(output,source_view),
        "lightingIncludedInAlbedo":False,"sourceView":source_view,
        "meshes":len(meshes)}
