"""Make linked collection instances real, for the derivative and its comparison.

The authoring module links the hero suit (collection HERO_SUIT from hero_suit.blend) into each locker as a collection
instance. A delivery derivative has to be self-contained, so before optimising (and before the signature of the original is
taken, so both sides compare the same geometry) the instances are turned into local objects and the library is dropped.
Call realize_linked_instances() right after opening the file; it does nothing when there are no linked instances."""
import bpy


def realize_linked_instances():
    insts = [o for o in bpy.data.objects
             if o.instance_type == "COLLECTION" and o.instance_collection is not None and o.instance_collection.library is not None]
    if not insts:
        return 0
    names = [o.name for o in insts]
    for nm in names:
        o = bpy.data.objects[nm]
        for x in bpy.context.view_layer.objects:
            x.select_set(False)
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.duplicates_make_real(use_base_parent=True, use_hierarchy=True)
        o.instance_type = "NONE"
        o.instance_collection = None
        bpy.ops.object.make_local(type="SELECT_OBDATA_MATERIAL")
    bpy.ops.object.make_local(type="ALL")
    for lib in list(bpy.data.libraries):
        try:
            bpy.data.libraries.remove(lib)
        except RuntimeError:
            pass
    return len(names)
