param([string]$Phase='slice',[string]$Revision='slice-01',[string]$Cameras='C08_maintenance,C10_materials',[int]$Samples=48,[switch]$Reopen,[switch]$Final)
$ErrorActionPreference='Stop'
$sectionRoot=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$env:BLENDER_USER_RESOURCES=Join-Path $sectionRoot '.blender-user'
$env:PYTHONUTF8='1'
New-Item -ItemType Directory -Force -Path $env:BLENDER_USER_RESOURCES | Out-Null
$blenderExe='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
$pythonExe='C:/Users/Camer/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$gate='C:/Users/Camer/Games/critical-shift/ops/facility-run/gpu_gate.py'
if ($Reopen) {
    $blenderArgs=@('--background',(Join-Path $PSScriptRoot 'turbine-room.blend'),'--python-exit-code','1','--python',(Join-Path $PSScriptRoot 'render.py'),'--','--revision',$Revision,'--render',$Cameras,'--samples',"$Samples")
    if($Final){$blenderArgs+='--final'}
} else {
    $blenderArgs=@('--background','--factory-startup','--python-exit-code','1','--python',(Join-Path $PSScriptRoot 'build.py'),'--','--phase',$Phase,'--revision',$Revision,'--render',$Cameras,'--samples',"$Samples")
}
& $pythonExe $gate --owner turbine-room --max-wait 900 -- $blenderExe @blenderArgs
exit $LASTEXITCODE
