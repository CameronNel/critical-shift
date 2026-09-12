"""New Fuel-only interactive window: configure viewport without saving the file.

Launch with the verified .blend as a command-line file, never in another room's
existing window. Uses a solid viewport; does not start a GPU render or enable
an automation add-on in the user's other sessions.
"""
import bpy,os,json,hashlib,datetime
from pathlib import Path
root=Path(os.environ['FUEL_CORRIDOR_ROOT']).resolve()
expected=(root/'blender/Fuel_Corridor.blend').resolve()
assert Path(bpy.data.filepath).resolve()==expected and not bpy.app.background
before=hashlib.sha256(expected.read_bytes()).hexdigest()
def configure():
    views=0
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type!='VIEW_3D':continue
            space=area.spaces.active
            space.shading.type='SOLID';space.shading.color_type='MATERIAL'
            space.overlay.show_overlays=False
            space.region_3d.view_perspective='CAMERA';views+=1
    report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pid':os.getpid(),'file':str(expected),'sha256':before,'objects':len(bpy.context.scene.objects),'revision':bpy.context.scene.get('revision'),'camera':bpy.context.scene.camera.name,'viewports_configured':views,'scene_saved':False,'gpu_render_started':False,'file_unchanged':hashlib.sha256(expected.read_bytes()).hexdigest()==before}
    (root/'production/runtime/inspection-window.json').write_text(json.dumps(report,indent=2))
    print('FUEL_INSPECTION_WINDOW',json.dumps(report),flush=True)
    return None
bpy.app.timers.register(configure,first_interval=1)
