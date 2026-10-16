"""Check, without rendering, that Blender finds the device the owner chose (blender_device.py):

    blender --background --factory-startup --python check_device.py -- --device GPU|CPU

Prints the Blender version and 'BLENDER DEVICE GPU (owner choice): HIP [...]' (or CPU); exits non-zero if the device is unset or a GPU is asked for and none is found."""
import bpy, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import blender_device
print('BLENDER VERSION', bpy.app.version_string, flush=True)
bpy.context.scene.render.engine = 'CYCLES'
print('CHECK', blender_device.apply(bpy.context.scene), flush=True)
