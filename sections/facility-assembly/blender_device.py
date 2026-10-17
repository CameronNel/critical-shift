"""Blender compute device: the owner's choice, never the agent's (owner rule, 2026-10-16: "the AI model that directs it should only let blender run from the gpu
or cpu depending on what I tell it to do").

Every Cycles render or bake started by the map and Unity tools goes through apply(scene). The device comes from `--device GPU|CPU` after Blender's `--`,
or else from the environment variable CS_BLENDER_DEVICE. There is no default and no fallback:
  * not set              -> the script stops and says so (the agent must ask the owner, not pick one);
  * CPU                  -> Cycles on the CPU;
  * GPU                  -> Cycles on the first GPU backend Blender finds (HIP for AMD, OptiX or CUDA for NVIDIA, oneAPI, Metal); if there is none, the script
                            stops instead of quietly running on the CPU.
Scripts that do not render (walk tests, audits, the build) do not need it."""
import os, sys

BACKENDS = ('HIP', 'OPTIX', 'CUDA', 'ONEAPI', 'METAL')

def requested():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    v = a[a.index('--device') + 1] if '--device' in a and a.index('--device') + 1 < len(a) else os.environ.get('CS_BLENDER_DEVICE', '')
    v = v.strip().upper()
    if v not in ('GPU', 'CPU'):
        raise SystemExit('BLENDER DEVICE NOT SET%s: the owner decides whether Blender renders on the GPU or the CPU. Pass --device GPU or --device CPU after "--", '
                         'or set CS_BLENDER_DEVICE. Agents: ask the owner; do not choose.' % ((' (got %r)' % v) if v else ''))
    return v

def apply(scene):
    """Set scene.cycles.device to the owner's device; returns a dict for the run log."""
    import bpy
    dev = requested()
    scene.cycles.device = 'CPU'
    if dev == 'CPU':
        print('BLENDER DEVICE CPU (owner choice)', flush=True); return dict(device='CPU')
    cp = bpy.context.preferences.addons['cycles'].preferences
    for backend in BACKENDS:
        try: cp.compute_device_type = backend
        except TypeError: continue
        cp.get_devices(); gpus = [d for d in cp.devices if d.type == backend]
        if gpus:
            for d in cp.devices: d.use = d.type == backend
            scene.cycles.device = 'GPU'
            print('BLENDER DEVICE GPU (owner choice): %s %s' % (backend, [d.name for d in gpus]), flush=True)
            return dict(device='GPU', backend=backend, gpus=[d.name for d in gpus])
    raise SystemExit('BLENDER DEVICE GPU was asked for, but Blender found no GPU backend (%s). Not falling back to the CPU: check the driver, or ask the owner '
                     'whether to run on the CPU instead.' % ', '.join(BACKENDS))
