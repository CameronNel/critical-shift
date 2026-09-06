#!/usr/bin/env python3
"""Canonical entrypoint for the implemented fifty-camera Gullet revision.
CLI: blender -b --factory-startup --python build_mine.py -- --output ./output
GUI: open Gullet_MaterialReview.blend before running this file.
"""
from pathlib import Path
import argparse,importlib.util,runpy,sys
ROOT=Path(__file__).resolve().parent

def geometry_module():
    spec=importlib.util.spec_from_file_location('gullet_geometry_source',ROOT/'geometry_source.py')
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    return module

def main():
    import bpy
    argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'output'/'quality50')
    p.add_argument('--render',default='');p.add_argument('--quality',choices=['balanced','high'],default='balanced')
    p.add_argument('--mode',choices=['showcase','intact'],default='showcase')
    args=p.parse_args(argv)
    if not any(s.get('csm_material_revision') and not s.get('q50_revision') for s in bpy.data.scenes):
        if not bpy.app.background:raise RuntimeError('Open Gullet_MaterialReview.blend first. Your current unsaved scene has not been changed.')
        source=ROOT/'Gullet_MaterialReview.blend'
        if not source.is_file():raise FileNotFoundError(source)
        bpy.ops.wm.open_mainfile(filepath=str(source))
    previous=list(sys.argv)
    try:
        sys.argv=['blender','--','--output',str(args.output)]
        runpy.run_path(str(ROOT/'quality50'/'build_quality.py'),run_name='__main__')
        if args.mode=='intact':
            sys.path.insert(0,str(ROOT/'quality50'));import controls
            scene=next(s for s in bpy.data.scenes if s.get('q50_revision'));controls.reset(scene)
            bpy.ops.wm.save_as_mainfile(filepath=str(args.output/'Gullet_Quality50.blend'),compress=True)
        if args.render:
            quality=['--width','1600','--samples','64'] if args.quality=='high' else ['--width','1100','--samples','32']
            sys.argv=['blender','--','--output',str(args.output/'renders')]+quality
            if args.render!='all':
                aliases={'entry':1,'main_route':12,'sump':36,'collapse':35,'dispatch':7,'bay_overview':6}
                keys=[str(aliases[k]) if k in aliases else str(int(k.upper().replace('CAM_',''))) for k in args.render.split(',')]
                sys.argv+=['--views',','.join(keys)]
            runpy.run_path(str(ROOT/'quality50'/'render_quality.py'),run_name='__main__')
    finally:sys.argv=previous

if __name__=='__main__':
    if '--audit-only' in sys.argv:geometry_module().main()
    else:main()
else:
    _base=geometry_module();globals().update({k:v for k,v in vars(_base).items() if not k.startswith('__')})
