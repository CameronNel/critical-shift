"""Refresh wall/floor textures, lettering, or constant inputs without changing room geometry.

Run in Blender with the pinned spawn source open. All writes are runtime derivatives.
"""
import json
import sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from export_spawn_materials import bake_atlas, constant_inputs
from export_spawn_map import export


def main():
    output=Path(sys.argv[sys.argv.index("--")+1]).resolve()
    path=output/"map-bindings.json"
    manifest=json.loads(path.read_text())
    room=next(r for r in manifest["rooms"] if r["key"]=="spawn-room")
    binding=next(o for o in room["objects"] if o["source"]=="V_LOCKER_porcelain_tiles")
    if len(binding["materials"])!=1: raise ValueError("Unexpected source floor material inventory")
    package=next(p for p in manifest["materials"] if p["room"]=="spawn-room")
    definition=next(d for d in package["definitions"] if d["key"]==binding["materials"][0])
    if definition["source"]!="CS_tile_floor": raise ValueError("Unexpected floor source shader")
    if "--lettering" in sys.argv or "--walls" in sys.argv:
        walls="--walls" in sys.argv
        key="walls" if walls else "lettering"
        suffix="__Walls" if walls else "__Lettering"
        wanted={d["key"] for d in package["definitions"] if d["source"].startswith("V13_") and d["source"].endswith(("_wall","_dado"))}
        source_scene=bpy.context.scene
        view=source_scene.view_settings
        source_view={"transform":view.view_transform,"look":view.look,"exposure":view.exposure,"gamma":view.gamma}
        graph=bpy.context.evaluated_depsgraph_get()
        scene=bpy.data.scenes.new("CS_"+key.upper()+"_DELIVERY")
        objects=[]; bindings=[]
        for entry in room["objects"]:
            original=bpy.data.objects.get(entry["source"])
            if original is None: continue
            if walls:
                if original.type!="MESH" or not wanted.intersection(entry.get("materials",[])): continue
            elif original.type!="FONT": continue
            mesh=bpy.data.meshes.new_from_object(original.evaluated_get(graph),preserve_all_data_layers=True,depsgraph=graph)
            if not len(mesh.polygons):
                bpy.data.meshes.remove(mesh)
                continue
            copy=bpy.data.objects.new(entry["node"]+suffix,mesh)
            copy.matrix_world=original.matrix_world
            scene.collection.objects.link(copy); objects.append(copy)
            bindings.append({"node":copy.name,"source":entry["source"]})
        bpy.context.window.scene=scene;bpy.context.view_layer.update()
        baked=bake_atlas(scene,objects,bindings,output,source_view,key)
        indices=[i for i,m in enumerate(package["atlases"]) if m["albedo"]["file"].startswith("Surfaces/"+key+"/")]
        if indices: index=indices[0];package["atlases"][index]=baked["maps"]
        else: index=len(package["atlases"]);package["atlases"].append(baked["maps"])
        package["definitions"]=[d for d in package["definitions"] if not d["key"].startswith("CS_spawn_surface_"+key+"_")]
        for entry in baked["definitions"]: entry["atlas"]=index
        package["definitions"].extend(baked["definitions"])
        by_source={entry["source"]:entry for entry in bindings}
        for entry in room["objects"]:
            if entry["source"] in by_source:
                entry["wallSurface" if walls else "lettering"]=True;entry["materials"]=by_source[entry["source"]]["materials"]
        file=output/("Surfaces/"+key+"/"+("Walls" if walls else "Lettering")+".fbx")
        export(file,objects)
        import hashlib
        package["wallMesh" if walls else "letteringMesh"]={"file":file.relative_to(output).as_posix(),"sha256":hashlib.sha256(file.read_bytes()).hexdigest()}
        path.write_text(json.dumps(manifest,indent=2)+"\n")
        from prepare_player import meta
        for asset in [output/("Surfaces/"+key),*sorted((output/("Surfaces/"+key)).rglob("*"))]:
            if not asset.name.endswith(".meta"):meta(asset)
        print("CS_SOURCE_SURFACE_DELIVERY_OK; kind="+key+"; meshes="+str(len(objects))+"; original room geometry hashes unchanged",flush=True)
        return
    if "--inputs-only" in sys.argv:
        for entry in package["definitions"]:
            material=bpy.data.materials.get(entry["source"])
            if material is not None: entry.update(constant_inputs(material))
            elif entry["transparent"]: raise ValueError("Missing glass source: "+entry["source"])
            else: entry["surfaceOpacity"]=1.0  # Exterior skin already retains its constant inputs.
        path.write_text(json.dumps(manifest,indent=2)+"\n")
        print("CS_SOURCE_SURFACE_INPUTS_OK; texture and geometry hashes unchanged",flush=True)
        return
    original=bpy.data.objects["V_LOCKER_porcelain_tiles"]
    view=bpy.context.scene.view_settings
    source_view={"transform":view.view_transform,"look":view.look,"exposure":view.exposure,"gamma":view.gamma}
    scene=bpy.data.scenes.new("CS_FLOOR_DELIVERY")
    copy=original.copy();copy.data=original.data.copy();copy.parent=None
    scene.collection.objects.link(copy);bpy.context.window.scene=scene;bpy.context.view_layer.update()
    baked=bake_atlas(scene,[copy],[],output,source_view,"floor")
    indices=[i for i,m in enumerate(package["atlases"]) if m["albedo"]["file"].startswith("Surfaces/floor/")]
    if indices: index=indices[0];package["atlases"][index]=baked["maps"]
    else: index=len(package["atlases"]);package["atlases"].append(baked["maps"])
    key=definition["key"];definition.update(baked["definitions"][0]);definition.update(key=key,atlas=index)
    binding["deliveryUvAxes"]=[0,1]
    package["displayLut"]=baked["displayLut"]
    path.write_text(json.dumps(manifest,indent=2)+"\n")
    from prepare_player import meta
    for asset in [output/"Surfaces/floor",*sorted((output/"Surfaces/floor").rglob("*"))]:
        if not asset.name.endswith(".meta"):meta(asset)
    print("CS_SOURCE_FLOOR_DELIVERY_OK; geometry hashes unchanged",flush=True)


if __name__=="__main__":main()
