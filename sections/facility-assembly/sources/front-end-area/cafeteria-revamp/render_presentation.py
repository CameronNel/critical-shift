"""Higher-resolution Cycles presentation; reuse the original camera renderer."""
import bpy
import json
import runpy
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:]
scene=bpy.context.scene
scene.cycles.use_adaptive_sampling=True
scene.cycles.adaptive_threshold=.035
scene.cycles.adaptive_min_samples=8
runpy.run_path(str(HERE.parent/'render_views.py'),run_name='__main__')
(Path(args[0])/'render_settings.json').write_text(json.dumps({
    'engine':scene.render.engine,'device':scene.cycles.device,
    'maximum_samples':scene.cycles.samples,'adaptive_threshold':scene.cycles.adaptive_threshold,
    'adaptive_minimum_samples':scene.cycles.adaptive_min_samples,
    'resolution':[scene.render.resolution_x,scene.render.resolution_y],
    'view_transform':scene.view_settings.view_transform,'exposure':scene.view_settings.exposure,
    'cameras':args[1].split(','),'geometry_modified':False,'scene_saved':False,
},indent=2)+'\n')
