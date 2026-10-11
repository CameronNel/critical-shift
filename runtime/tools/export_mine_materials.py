"""Material-only delivery of the assembled wooden R39 mine; source files stay immutable."""
import hashlib
import numpy as np
from export_spawn_materials import bake_atlas


def geometry_digest(objects):
    digest = hashlib.sha256()
    for o in sorted((o for o in objects if o.type == "MESH"), key=lambda o: o.name):
        digest.update(o.name.encode())
        vertices = np.empty(len(o.data.vertices)*3, dtype=np.float32)
        o.data.vertices.foreach_get("co", vertices)
        digest.update(vertices.tobytes())
        indices = np.empty(len(o.data.loops), dtype=np.int32)
        o.data.loops.foreach_get("vertex_index", indices)
        digest.update(indices.tobytes())
        digest.update(np.asarray(o.matrix_world, dtype=np.float32).tobytes())
    return digest.hexdigest()


def bake_mine(scene, objects, mappings, output, source_view):
    before = geometry_digest(objects)
    groups = {key: [] for key in ("mine-mountain", "mine-ground", "mine-rocks", "mine-structure", "mine-props")}
    unsupported = []
    by_name = {o.name: o for o in objects}
    for mapping in mappings:
        o = by_name[mapping["node"]]
        if o.type != "MESH" or not mapping["visible"] or not o.data.polygons: continue
        # Volumes are not surface maps. Do not turn the haze containers into solid walls.
        if any(m and m.use_nodes and any(n.type in {"PRINCIPLED_VOLUME", "VOLUME_SCATTER"} for n in m.node_tree.nodes) for m in o.data.materials):
            mapping["visible"] = False
            unsupported.append({"node": o.name, "reason": "Authored volume requires engine-specific atmosphere, not an albedo atlas."})
            continue
        name = mapping["source"].lower()
        if "mine cliff" in name: group = "mine-mountain"
        elif any(s in name for s in ("floor", "gravel", "ground", "ledge debris")): group = "mine-ground"
        elif any(s in name for s in ("boulder", "rockfall", "rock", "crystal")): group = "mine-rocks"
        elif any(s in name for s in ("timber", "board", "shed", "rail", "sleeper", "duct", "pipe", "roof", "beam", "support", "wall")): group = "mine-structure"
        else: group = "mine-props"
        groups[group].append(o)
    packages = []
    for key, group in groups.items():
        if not group: continue
        print("CS_MINE_ATLAS", key, len(group), sum(len(o.data.vertices) for o in group), flush=True)
        package = bake_atlas(scene, group, mappings, output, source_view, key, room="mine")
        for definition in package["definitions"]: definition["atlas"] = len(packages)
        packages.append(package)
    if before != geometry_digest(objects): raise ValueError("Mine material baking changed geometry or placement.")
    result = packages[0]
    result["atlases"] = [p["maps"] for p in packages]
    result["definitions"] = [d for p in packages for d in p["definitions"]]
    result["meshes"] = sum(p["meshes"] for p in packages)
    result["geometrySha256"] = before
    result["unsupported"] = unsupported
    from mine_lightmap_uv import generate
    if generate(objects) != result["meshes"]:
        raise ValueError("Mine lighting UV coverage changed.")
    if before != geometry_digest(objects): raise ValueError("Lighting unwrap changed mine geometry.")
    from mine_join_rays import generate as join_rays
    result["joinRays"] = join_rays(objects,mappings)
    result["limits"] = "Unlit surface delivery. Source shader AO is retained; scene illumination is not baked into albedo. View-dependent crystal color, transmission and volumetric haze need native comparison; no independent art acceptance."
    return result
