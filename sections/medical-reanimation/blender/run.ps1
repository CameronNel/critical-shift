param([string]$Phase='slice',[string]$Revision='s01',[string]$Cameras='C00_slice',[int]$Samples=32,[int]$Width=1280,[switch]$NoRender,[switch]$Cpu)
$ErrorActionPreference='Stop'
$sectionRoot=Split-Path $PSScriptRoot -Parent
$env:BLENDER_USER_RESOURCES=Join-Path $sectionRoot 'production/runtime/blender-user'
New-Item -ItemType Directory -Force -Path $env:BLENDER_USER_RESOURCES | Out-Null
$blenderExe='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
$buildArgs=@('--background','--factory-startup','--python-exit-code','1','--python',(Join-Path $PSScriptRoot 'build_medical.py'),'--','--phase',$Phase,'--revision',$Revision,'--cameras',$Cameras,'--samples',"$Samples",'--width',"$Width")
if($Cpu){ $buildArgs+=@('--render','--cpu'); & $blenderExe @buildArgs } elseif($NoRender){ & $blenderExe @buildArgs } else {
    $buildArgs+='--render'
    & 'C:/Users/Camer/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'C:/Users/Camer/Games/critical-shift/ops/facility-run/gpu_gate.py' --owner medical-reanimation -- $blenderExe @buildArgs
}
exit $LASTEXITCODE
