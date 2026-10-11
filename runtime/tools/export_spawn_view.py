"""Use Blender's own display transform to export a HDR-input colour lookup table."""
import bpy
import hashlib
import numpy as np


def export_view(output, source_view):
    scene=bpy.data.scenes.new("CS_Display_Transform")
    scene.view_settings.view_transform=source_view["transform"]
    scene.view_settings.look=source_view["look"]
    scene.view_settings.exposure=source_view["exposure"]
    scene.view_settings.gamma=source_view["gamma"]
    scene.render.image_settings.file_format="PNG"
    scene.render.image_settings.color_mode="RGBA"
    scene.render.image_settings.color_depth="16"
    image=bpy.data.images.new("CS_Display_LUT",width=4096,height=64,alpha=True,float_buffer=True)
    image.colorspace_settings.name="Linear Rec.709"
    levels=np.exp2(np.linspace(-12,6,64,dtype=np.float32))
    data=np.ones((64,4096,4),dtype=np.float32)
    for blue in range(64):
        data[:,blue*64:(blue+1)*64,0]=levels[None,:]
        data[:,blue*64:(blue+1)*64,1]=levels[:,None]
        data[:,blue*64:(blue+1)*64,2]=levels[blue]
    image.pixels.foreach_set(data.ravel())
    file=output/"Surfaces"/"spawn-display-lut.png"
    image.save_render(str(file),scene=scene)
    bpy.data.images.remove(image); bpy.data.scenes.remove(scene)
    return {"file":"Surfaces/"+file.name,"sha256":hashlib.sha256(file.read_bytes()).hexdigest(),
        "colorSpace":"sRGB","size":4096,"grid":64,"inputLog2Min":-12,"inputLog2Max":6}
