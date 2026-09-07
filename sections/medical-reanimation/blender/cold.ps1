param([string]$Revision='cold',[string]$Blend='medical_reanimation.blend',[string]$Cameras='all',[int]$Samples=64,[int]$Width=1440,[switch]$Cpu,[switch]$Final)
$ErrorActionPreference='Stop'
$sectionRoot=Split-Path $PSScriptRoot -Parent
$env:BLENDER_USER_RESOURCES=Join-Path $sectionRoot 'production/runtime/cold-blender-user'
New-Item -ItemType Directory -Force -Path $env:BLENDER_USER_RESOURCES | Out-Null
$blenderExe='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
$renderArgs=@('--background','--factory-startup',(Join-Path $PSScriptRoot $Blend),'--python-exit-code','1','--python',(Join-Path $PSScriptRoot 'render_saved.py'),'--','--revision',$Revision,'--cameras',$Cameras,'--samples',"$Samples",'--width',"$Width")
if($Final){$renderArgs+='--final'}
if($Cpu){$renderArgs+='--cpu'; & $blenderExe @renderArgs } else {
    & 'C:/Users/Camer/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'C:/Users/Camer/Games/critical-shift/ops/facility-run/gpu_gate.py' --owner medical-reanimation -- $blenderExe @renderArgs
}
exit $LASTEXITCODE
