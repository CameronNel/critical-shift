"""Bake source shader inputs into a delivery atlas; never bake scene lighting into albedo."""
import hashlib
import json
import math
import os
from pathlib import Path

import bpy
import numpy as np
from export_spawn_view import export_view


UV = "CS_DeliveryUV"
SOURCE_UV = "CS_SourceUV"


def thin_visor(material):
    """Export the active clear/Fresnel/glossy graph, not its unused Principled node."""
    if material.get("cs_transparency_model") != "thin_surface_no_refraction": return None
    nt = material.node_tree
    output = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output)
    mix = output.inputs["Surface"].links[0].from_node
    if mix.type != "MIX_SHADER": raise ValueError("Unexpected thin visor output")
    clear = mix.inputs[1].links[0].from_node
    glossy = mix.inputs[2].links[0].from_node
    weight = mix.inputs[0].links[0].from_node
    if clear.type != "BSDF_TRANSPARENT" or glossy.bl_idname != "ShaderNodeBsdfAnisotropic" or weight.type != "MATH" or weight.operation != "MULTIPLY":
        raise ValueError("Unsupported thin visor graph: " + material.name)
    fresnel = weight.inputs[0].links[0].from_node
    mask = weight.inputs[1].links[0].from_node
    if fresnel.type != "FRESNEL" or mask.type != "MAP_RANGE" or any(abs(c-1)>1e-6 for c in clear.inputs["Color"].default_value):
        raise ValueError("Unsupported thin visor tint/falloff: " + material.name)
    if clear.inputs["Color"].is_linked or any(glossy.inputs[k].is_linked for k in ("Color","Roughness","Normal","Anisotropy")) or \
            glossy.inputs["Anisotropy"].default_value != 0 or fresnel.inputs["IOR"].is_linked or fresnel.inputs["Normal"].is_linked:
        raise ValueError("Thin visor requires a uniform isotropic reflection lobe: " + material.name)
    return {"thinSurface": True, "reflectionIOR": float(fresnel.inputs["IOR"].default_value),
            "reflectionColor": list(glossy.inputs["Color"].default_value),
            "smoothness": 1-float(glossy.inputs["Roughness"].default_value), "maskNode": mask.name}


def surface_opacity(material):
    """Retain constant transparent/Principled Mix Shader coverage for raster delivery."""
    if thin_visor(material): return 0.0  # View-dependent reflection is evaluated in Unity.
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
    thin = thin_visor(material)
    if thin:
        return {k:v for k,v in dict(thin, baseConstant=True, normalConstant=True,
            metallicConstant=True, roughnessConstant=True, emissionConstant=True,
            surfaceOpacity=0.0, dielectricSpecular=0.0, baseColor=[0,0,0,1], metallic=1.0,
            emissionColor=[0,0,0,1], emissionStrength=0.0).items() if k != "maskNode"}
    bsdf=next(n for n in material.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
    def constant(name): return not bsdf.inputs[name].is_linked
    if not constant("IOR") or not constant("Specular IOR Level"):
        raise ValueError("Linked dielectric reflectivity requires an explicit export: "+material.name)
    ior=float(bsdf.inputs["IOR"].default_value)
    # Blender's neutral specular level is 0.5; Unity's fixed Standard dielectric
    # F0 cannot represent the source paint's lower level (0.3).
    f0=((ior-1)/(ior+1))**2 * 2*float(bsdf.inputs["Specular IOR Level"].default_value)
    return {"baseConstant":constant("Base Color"),"normalConstant":constant("Normal"),
        "metallicConstant":constant("Metallic"),"roughnessConstant":constant("Roughness"),
        "emissionConstant":constant("Emission Strength") and
            (constant("Emission Color") or bsdf.inputs["Emission Strength"].default_value == 0),
        "surfaceOpacity":surface_opacity(material),
        "dielectricSpecular":f0,
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


def bake_atlas(scene, objects, mappings, output, source_view, atlas_key, room="spawn-room"):
    size = 2048 if atlas_key in {"floor","lettering"} else int(os.environ.get("CS_SURFACE_SIZE", "4096"))
    if size not in (2048, 4096, 8192):
        raise ValueError("Unsupported reviewed surface atlas resolution")
    meshes = [o for o in objects if o.type == "MESH" and len(o.data.polygons) and len(o.data.materials)]
    originals = list(dict.fromkeys(m for o in meshes for m in o.data.materials if m))
    copies, states, definitions, coordinate_attributes, thin_states, wood_states = {}, {}, [], {}, {}, {}
    joined = room != "mine" or os.environ.get("CS_MINE_JOIN_BAKE") == "1"
    if room == "mine" and any(n.type=="OBJECT_INFO" and any(s.is_linked for s in n.outputs) for m in originals for n in m.node_tree.nodes): joined=False
    for index, original in enumerate(originals):
        prefix = "spawn" if room == "spawn-room" else room
        m = original.copy(); m.name = "CS_" + prefix + "_surface_" + atlas_key + "_" + str(index).zfill(3)
        copies[original] = m
        nt = m.node_tree
        bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
        source_constants = original
        if bsdf is None and atlas_key.startswith("mine-context-"):
            glass = next((n for n in nt.nodes if n.type == "BSDF_GLASS"), None)
            if glass is not None:
                # Raster approximation of depot glazing, in the disposable export only.
                # The source's shadow-ray transparent branch has no raster equivalent.
                bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
                for old_name, new_name in (("Color", "Base Color"), ("Roughness", "Roughness"), ("IOR", "IOR"), ("Normal", "Normal")):
                    old_socket, new_socket = glass.inputs[old_name], bsdf.inputs[new_name]
                    if old_socket.is_linked: nt.links.new(old_socket.links[0].from_socket, new_socket)
                    else: new_socket.default_value = old_socket.default_value
                bsdf.inputs["Transmission Weight"].default_value = 1
                out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output)
                nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
                for node in list(nt.nodes):
                    if node.type in {"BSDF_GLASS", "BSDF_TRANSPARENT", "MIX_SHADER", "LIGHT_PATH"}: nt.nodes.remove(node)
                source_constants = m
        if bsdf is None: raise ValueError("Unsupported source surface: " + original.name)
        # Explicitly retain the old UV input while baking into an additional UV layer.
        source_uv = nt.nodes.new("ShaderNodeUVMap"); source_uv.uv_map = SOURCE_UV
        for n in list(nt.nodes):
            if room == "mine" and n.type == "NORMAL_MAP" and n.space == "TANGENT" and not n.uv_map:
                # The original tangent basis must not silently switch to the new atlas UVs.
                n.uv_map = SOURCE_UV
            if joined and n.type in {"TEX_NOISE","TEX_VORONOI","TEX_WAVE","TEX_MAGIC","TEX_GRADIENT","TEX_BRICK","TEX_CHECKER","TEX_WHITE_NOISE"} and not n.inputs["Vector"].is_linked:
                coordinate_attributes["CS_Generated"]=("Generated",None)
                attribute=nt.nodes.new("ShaderNodeAttribute");attribute.attribute_name="CS_Generated"
                nt.links.new(attribute.outputs["Vector"],n.inputs["Vector"])
            if n.type == "TEX_IMAGE" and not n.inputs["Vector"].is_linked:
                nt.links.new(source_uv.outputs["UV"], n.inputs["Vector"])
            if joined and n.type == "TEX_COORD":
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
        thin_states[m] = thin_visor(m)
        transmission = bsdf.inputs["Transmission Weight"].default_value
        alpha = bsdf.inputs["Alpha"].default_value
        definition={"key":m.name,"source":original.name,"transmission":float(transmission),
            "alpha":float(alpha),"transparent":transmission > 0.01 or alpha < 0.999 or any(n.type == "BSDF_TRANSPARENT" for n in nt.nodes)}
        definition.update(constant_inputs(source_constants))
        if room == "mine" and not atlas_key.startswith("mine-context-"):
            from export_source_wood import export as export_wood
            wood = export_wood(original, output)
            if wood:
                definition["sourceWood"] = wood
                grain = nt.nodes[wood["clampNode"]].outputs["Result"]
                destinations = [link.to_socket for link in grain.links]
                replacement = nt.nodes.new("ShaderNodeValue")
                wood_states[m] = (grain, destinations, replacement)
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
        wood_uvs = {d["sourceWood"]["sourceUvLayer"] for d in definitions if "sourceWood" in d and d["key"] in [slot.material.name for slot in o.material_slots]}
        if len(wood_uvs) > 1: raise ValueError("Wood materials require distinct source UV channels: " + o.name)
        if wood_uvs:
            original_uv = o.data.uv_layers.get(next(iter(wood_uvs)))
            if original_uv is None: raise ValueError("Missing authored wood UV channel: " + o.name)
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
    elif room=="mine" and atlas_key not in {"mine-mountain","mine-ground","mine-rocks"}:
        # Source topology can split every painted face. Weld only temporary unwrap
        # proxies, retaining every delivered vertex, polygon and custom attribute.
        from mine_delivery_uv import unwrap
        unwrap(meshes,UV,margin/size,world_vertices=True)
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
    if room == 'mine' and atlas_key in {'mine-tunnel-floor', 'mine-duct'}:
        from mine_delivery_uv import surface_density
        floor_density = [surface_density(o, UV, size) for o in meshes]
        minimum_density = 64 if atlas_key == 'mine-tunnel-floor' else 128
        if any(not math.isfinite(r['pixelsPerMetre']) or r['pixelsPerMetre'] < minimum_density for r in floor_density):
            raise ValueError('Mine surface has insufficient texture density: ' + repr(floor_density))
        (output / ('mine-floor-density.json' if atlas_key == 'mine-tunnel-floor' else 'mine-duct-density.json')).write_text(json.dumps({
            'minimumPixelsPerMetre': minimum_density, 'surfaces': floor_density,
            'status': 'Passed', 'limits': 'UV density guard; native visual review is still required.'}, indent=2) + '\n')
    # Bake one temporary joined mesh rather than compiling the scene once for each of 1,700 objects.
    # Store object/generated coordinates first: joining alone would change the procedural recipes.
    batch = None
    if not joined:
        bpy.ops.object.select_all(action="DESELECT")
        for o in meshes: o.select_set(True)
        bpy.context.view_layer.objects.active = meshes[0]
    else:
        batches=[]
        for o in meshes:
            batch=o.copy(); batch.data=o.data.copy(); batch.parent=None; batch.matrix_world=o.matrix_world
            # Source material coordinates/tangents are captured in the bind pose. The
            # original skinned meshes keep their modifiers and weights for FBX export.
            for modifier in list(batch.modifiers):
                if modifier.type == "ARMATURE": batch.modifiers.remove(modifier)
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
        schema_groups={}
        for o in batches:
            signature=(tuple(sorted((a.name,a.data_type,a.domain) for a in o.data.attributes if not a.name.startswith('.'))),tuple(u.name for u in o.data.uv_layers)) if room=='mine' else ('spawn',)
            schema_groups.setdefault(signature,[]).append(o)
        joined_batches=[]
        for group in schema_groups.values():
            bpy.ops.object.select_all(action="DESELECT")
            for o in group:o.select_set(True)
            bpy.context.view_layer.objects.active=group[0]
            if len(group)>1:bpy.ops.object.join()
            joined_batches.append(bpy.context.view_layer.objects.active)
        original_visibility={o:o.hide_render for o in meshes}
        if room=="mine":
            for o in meshes:o.hide_render=True
        bpy.ops.object.select_all(action="DESELECT")
        for o in joined_batches:o.select_set(True)
        bpy.context.view_layer.objects.active=joined_batches[0]
        batch=joined_batches
        print("CS_SURFACE_COMPATIBLE_BATCHES",atlas_key,len(joined_batches),flush=True)
    scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = 1
    scene.render.use_persistent_data = room == "mine"
    scene.render.bake.margin = margin; scene.render.bake.use_clear = False
    scene.render.bake.use_selected_to_active = False
    folder = output / "Surfaces" / atlas_key; folder.mkdir(parents=True,exist_ok=True)
    files = {}

    def connect(nt, source, destination):
        if source.is_linked: nt.links.new(source.links[0].from_socket, destination)
        else: destination.default_value = source.default_value

    reuse_path=os.environ.get("CS_REUSE_MINE_ATLASES") if room=="mine" else None
    cache=json.loads(Path(reuse_path).read_text()) if reuse_path else {}
    reused=cache.get("atlases",{}).get(atlas_key)
    from export_source_wood import RECIPE as wood_recipe
    if wood_states and reused and ("woodHigh" not in reused or cache.get("woodRecipe") != wood_recipe):
        # A flattened grain atlas is not a colour coefficient map.
        reused = None
    channels = ["albedo", "metallic-smoothness", "normal", "emission"]
    if wood_states: channels.append("wood-high")
    for channel in channels:
        key="metallicSmoothness" if channel=="metallic-smoothness" else "woodHigh" if channel=="wood-high" else channel
        if reused and key in reused:
            record=reused[key]
            if hashlib.sha256((output/record["file"]).read_bytes()).hexdigest()!=record["sha256"]:
                raise ValueError("Cached mine atlas changed: "+record["file"])
            files[key]=record
            print("CS_SURFACE_REUSE_VERIFIED",atlas_key,channel,flush=True)
            continue
        image = bpy.data.images.new("CS_spawn_"+channel,width=size,height=size,alpha=True,float_buffer=True)
        image.colorspace_settings.name = "sRGB" if channel in {"albedo", "wood-high"} else "Non-Color"
        if room == "mine" and channel == "normal":
            # use_clear=False preserves these values outside baked islands. Black
            # is an invalid encoded normal and contaminates small-chart mipmaps.
            background = np.empty((size*size,4),dtype=np.float32)
            background[:] = (.5,.5,1,1)
            image.pixels.foreach_set(background.ravel())
            del background
        for m, (bsdf,out,root,target,emission) in states.items():
            nt = m.node_tree; target.image = image; nt.nodes.active = target
            if m in wood_states:
                grain, destinations, replacement = wood_states[m]
                replacement.outputs[0].default_value = 1 if channel == "wood-high" else 0
                for destination in destinations:
                    nt.links.new(replacement.outputs[0] if channel in {"albedo", "wood-high"} else grain, destination)
            for n in nt.nodes: n.select = n == target
            if channel == "normal": nt.links.new(root,out.inputs["Surface"])
            else:
                nt.links.new(emission.outputs[0],out.inputs["Surface"])
                for link in list(emission.inputs["Color"].links): nt.links.remove(link)
                for link in list(emission.inputs["Strength"].links): nt.links.remove(link)
                emission.inputs["Strength"].default_value=1
                thin = thin_states[m]
                if thin and channel in {"albedo", "emission"}:
                    emission.inputs["Color"].default_value=(0,0,0,1)
                elif thin:
                    rgb=nt.nodes.new("ShaderNodeCombineColor"); rgb.mode="RGB"
                    rgb.inputs["Red"].default_value=1
                    rgb.inputs["Green"].default_value=thin["smoothness"]
                    nt.links.new(nt.nodes[thin["maskNode"]].outputs["Result"],rgb.inputs["Blue"])
                    nt.links.new(rgb.outputs[0],emission.inputs["Color"])
                elif channel in {"albedo", "wood-high"}:
                    if channel == "wood-high" and m not in wood_states: emission.inputs["Color"].default_value=(0,0,0,1)
                    else: connect(nt,bsdf.inputs["Base Color"],emission.inputs["Color"])
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
        uniform = room == "mine" and channel != "wood-high" and all(d["baseConstant"] if channel == "albedo" else
            d["normalConstant"] if channel == "normal" else d["emissionConstant"] if channel == "emission" else
            d["metallicConstant"] and d["roughnessConstant"] for d in definitions)
        if uniform:
            # Every runtime material carries the exact source constants; this atlas channel is unused.
            # Retain its declared file without compiling the scene repeatedly for a discarded map.
            print("CS_SURFACE_CONSTANT_CHANNEL",atlas_key,channel,flush=True)
        else:
            # Source shader AO is stochastic. Both colour coefficients need a
            # stable estimate; a single ray turns their difference into mottling.
            scene.cycles.samples = 16 if (wood_states and channel in {"albedo", "wood-high"}) or (room == "mine" and atlas_key == "mine-duct" and channel == "normal") else 1
            bpy.ops.object.bake(type="NORMAL" if channel == "normal" else "EMIT",uv_layer=UV)
        if room == "mine" and channel == "normal":
            from normal_bake_pixels import neutralize_empty
            pixels = np.empty((size*size,4),dtype=np.float32)
            image.pixels.foreach_get(pixels.ravel())
            empty = neutralize_empty(pixels)
            if empty:
                image.pixels.foreach_set(pixels.ravel())
                print("CS_NORMAL_EMPTY_TEXELS_NEUTRALIZED",atlas_key,empty,flush=True)
            del pixels
        if channel == "metallic-smoothness":
            # Alpha is numeric smoothness, not opacity. Straight/premultiplied saving
            # would divide metallic by smoothness and turn painted steel into metal.
            image.alpha_mode="CHANNEL_PACKED"
            pixels=np.empty(size*size*4,dtype=np.float32); image.pixels.foreach_get(pixels)
            pixels=pixels.reshape((-1,4)); pixels[:,3]=pixels[:,1]; pixels[:,1]=0
            if not any(d.get("thinSurface") for d in definitions): pixels[:,2]=0
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
        files[key]={"file":"Surfaces/"+atlas_key+"/"+name,"sha256":hashlib.sha256((folder/name).read_bytes()).hexdigest(),
            "colorSpace":"sRGB" if channel in {"albedo", "wood-high"} else "linear","size":size}
        print("CS_SURFACE_BAKE_DONE",atlas_key,channel,flush=True)
        for state in states.values(): state[3].image=None
        bpy.data.images.remove(image)
    if batch is not None:
        for o in batch:bpy.data.objects.remove(o,do_unlink=True)
        for o,visible in original_visibility.items():o.hide_render=visible
    # Joining/deleting temporary objects leaves their mesh datablocks allocated.
    # Large room bakes must not accumulate a second copy of every preceding atlas.
    bpy.data.batch_remove([mesh for mesh in bpy.data.meshes if mesh.users == 0])
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
            if room=="mine":
                used_slots={polygon.material_index for polygon in o.data.polygons}
                mapping["faceMaterials"]=list(dict.fromkeys(mapping["materials"][i] for i in sorted(used_slots)))
            used=[d for d in definitions if d["key"] in mapping["materials"]]
            mapping["sourceUv"]=any(d.get("directEmission") for d in used)
            if atlas_key=="floor": mapping["deliveryUvAxes"]=[0,1]
            if mapping["sourceUv"] and any(not d.get("directEmission") and not all(d[k] for k in ("baseConstant","normalConstant","metallicConstant","roughnessConstant","emissionConstant")) for d in used):
                raise ValueError("Source image UVs require uniform companion surfaces: "+mapping["node"])
    # Avoid embedding the atlas four times per material in FBX; the manifest binds it explicitly in Unity.
    for m, (bsdf,out,root,target,emission) in states.items():
        if m in wood_states:
            grain, destinations, replacement = wood_states[m]
            for destination in destinations: m.node_tree.links.new(grain,destination)
        m.node_tree.links.new(root,out.inputs["Surface"])
        for n in list(m.node_tree.nodes):
            if n.type=="TEX_IMAGE": m.node_tree.nodes.remove(n)
    return {"room":room,"uv":UV,"maps":files,"definitions":definitions,"displayLut":export_view(output,source_view,"spawn" if room=="spawn-room" else room),
        "lightingIncludedInAlbedo":False,"sourceView":source_view,
        "meshes":len(meshes)}
