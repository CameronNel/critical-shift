"""User resource limit: CPU only, two logical processors, idle priority."""
import os
os.environ['OMP_NUM_THREADS']='2'
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OIDN_NUM_THREADS']='2'
os.environ['CUDA_VISIBLE_DEVICES']='-1'
os.environ['HIP_VISIBLE_DEVICES']='-1'

def limit_process():
    if os.name=='nt':
        import ctypes
        api=ctypes.windll.kernel32
        api.GetCurrentProcess.restype=ctypes.c_void_p
        handle=api.GetCurrentProcess()
        api.SetPriorityClass.argtypes=[ctypes.c_void_p,ctypes.c_uint32]
        api.SetProcessAffinityMask.argtypes=[ctypes.c_void_p,ctypes.c_size_t]
        if not api.SetPriorityClass(handle,0x40):raise OSError('Cannot set idle priority')
        count=min(os.cpu_count() or 2,64)
        mask=sum(1<<i for i in range(max(0,count-2),count))
        if not api.SetProcessAffinityMask(handle,mask):raise OSError('Cannot cap CPU affinity')
        print('ASTRA_RESOURCE_GUARD CPU_ONLY IDLE two_logical_processors',hex(mask),flush=True)

def configure_scene(scene,samples=32):
    scene.render.engine='CYCLES'
    scene.cycles.device='CPU'
    scene.render.threads_mode='FIXED';scene.render.threads=2
    scene.cycles.samples=samples
    scene.cycles.use_adaptive_sampling=True
    scene.cycles.adaptive_threshold=.04
    scene.cycles.use_denoising=True
    scene.cycles.denoiser='OPENIMAGEDENOISE'
    if hasattr(scene.cycles,'denoising_use_gpu'):scene.cycles.denoising_use_gpu=False
    scene.cycles.max_bounces=6
    scene.cycles.diffuse_bounces=3
    scene.cycles.glossy_bounces=3
    scene.cycles.transmission_bounces=4
    scene.cycles.transparent_max_bounces=8
    scene.cycles.sample_clamp_indirect=3
    scene['astra_resource_policy']='CPU only; 2 threads and 2 logical processors; IDLE priority; GPU denoising disabled'

limit_process()
