"""User-authorized fast HIP GPU mode; explicit CPU mode preserves the prior cap."""
import os
MODE=os.environ.get('ASTRA_RENDER_MODE','GPU').upper()
assert MODE in {'CPU','GPU'},'Unsupported Astra render mode'
THREADS=2 if MODE=='CPU' else os.cpu_count() or 2
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','OIDN_NUM_THREADS']:
    os.environ[key]=str(THREADS)
for key in ['CUDA_VISIBLE_DEVICES','HIP_VISIBLE_DEVICES']:
    if MODE=='CPU':os.environ[key]='-1'
    elif os.environ.get(key)=='-1':del os.environ[key]

def limit_process():
    if os.name=='nt':
        import ctypes, builtins, atexit
        api=ctypes.windll.kernel32
        if not hasattr(builtins,'_astra_cpu_mutex'):
            api.CreateMutexW.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_wchar_p]
            api.CreateMutexW.restype=ctypes.c_void_p
            api.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_uint32]
            api.ReleaseMutex.argtypes=[ctypes.c_void_p]
            api.CloseHandle.argtypes=[ctypes.c_void_p]
            mutex=api.CreateMutexW(None,False,'Local\\AstraCondenserCpuWorker')
            result=api.WaitForSingleObject(mutex,0)
            if result not in (0,0x80):
                api.CloseHandle(mutex)
                raise RuntimeError('Another Astra Blender worker is active; refusing concurrent jobs')
            builtins._astra_cpu_mutex=mutex
            atexit.register(lambda: (api.ReleaseMutex(mutex),api.CloseHandle(mutex)))
        api.GetCurrentProcess.restype=ctypes.c_void_p
        handle=api.GetCurrentProcess()
        api.SetPriorityClass.argtypes=[ctypes.c_void_p,ctypes.c_uint32]
        api.SetProcessAffinityMask.argtypes=[ctypes.c_void_p,ctypes.c_size_t]
        if not api.SetPriorityClass(handle,0x40 if MODE=='CPU' else 0x20):raise OSError('Cannot set task priority')
        count=min(os.cpu_count() or 2,64)
        mask=sum(1<<i for i in range(max(0,count-2) if MODE=='CPU' else 0,count))
        if not api.SetProcessAffinityMask(handle,mask):raise OSError('Cannot set CPU affinity')
        print('ASTRA_RESOURCE_GUARD',MODE,'IDLE' if MODE=='CPU' else 'NORMAL',hex(mask),flush=True)

def configure_scene(scene,samples=32):
    scene.render.engine='CYCLES'
    scene.cycles.device=MODE
    scene.render.threads_mode='FIXED' if MODE=='CPU' else 'AUTO'
    scene.render.threads=THREADS
    if MODE=='GPU':
        import bpy,json
        from pathlib import Path
        owner=json.loads(Path('C:/Users/Camer/Games/critical-shift/ops/facility-run/gpu_owner.json').read_text())
        assert owner.get('owner')=='astra-condenser-bay' and owner.get('status')=='running' and owner.get('pid')==os.getppid(), 'GPU render/build must be a child of the shared Astra GPU gate'
        prefs=bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type='HIP';prefs.refresh_devices()
        devices=[d for d in prefs.devices if d.type=='HIP']
        assert devices,'No HIP GPU found; do not silently fall back to CPU'
        for d in prefs.devices:d.use=d.type=='HIP'
        if hasattr(prefs,'use_hiprt'):prefs.use_hiprt=True
        scene['astra_gpu_devices']='; '.join(d.name for d in devices)
        scene['astra_gpu_backend']='HIP'
        scene['astra_hardware_raytracing']=bool(getattr(prefs,'use_hiprt',False))
    scene.render.use_persistent_data=True
    scene.cycles.samples=samples
    scene.cycles.use_adaptive_sampling=True
    scene.cycles.adaptive_threshold=.04
    scene.cycles.use_denoising=True
    scene.cycles.denoiser='OPENIMAGEDENOISE'
    gpu_denoise=MODE=='GPU' and os.environ.get('ASTRA_GPU_DENOISE','1')!='0'
    if hasattr(scene.cycles,'denoising_use_gpu'):scene.cycles.denoising_use_gpu=gpu_denoise
    scene.cycles.max_bounces=10
    scene.cycles.diffuse_bounces=3
    scene.cycles.glossy_bounces=3
    scene.cycles.transmission_bounces=8
    scene.cycles.transparent_max_bounces=8
    scene.cycles.sample_clamp_indirect=3
    scene['astra_resource_policy']=('CPU only; 2 threads and 2 logical processors; IDLE priority; GPU denoising disabled' if MODE=='CPU' else 'User authorized full GPU speed; HIP hardware ray tracing; '+('GPU' if gpu_denoise else 'CPU')+' denoising; normal priority; all CPU threads; shared GPU gate; one worker')

limit_process()
