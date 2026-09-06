#!/usr/bin/env python3
"""Canonical Gullet entrypoint. Builds the CC0-textured Blender revision.
The original geometry/state API remains available to imports and audit tools.
"""
from pathlib import Path
import importlib.util, runpy, sys
_ROOT=Path(__file__).resolve().parent

def _geometry_module():
    spec=importlib.util.spec_from_file_location('gullet_geometry_source',_ROOT/'geometry_source.py')
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module

if __name__=='__main__' and '--audit-only' not in sys.argv:
    runpy.run_path(str(_ROOT/'pbr'/'build_textured_mine.py'),run_name='__main__')
else:
    _base=_geometry_module()
    globals().update({k:v for k,v in vars(_base).items() if not k.startswith('__')})
    if __name__=='__main__':_base.main()
