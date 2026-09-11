param([ValidateSet('build','render')][string]$Action='build',[string]$Stage='full',[string]$Revision='R10',[string]$Cameras='all',[int]$Samples=48,[int]$Width=1440,[string]$Output='')
$ErrorActionPreference='Stop'
$coolingSection=Split-Path $PSScriptRoot -Parent
$env:BLENDER_USER_RESOURCES=Join-Path $coolingSection '.blender-user'
$coolingBlender='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
$coolingPython='C:/Users/Camer/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$coolingGate='C:/Users/Camer/Games/critical-shift/ops/facility-run/gpu_gate.py'
if($Action -eq 'build') {
  & $coolingBlender --background --factory-startup --threads 6 --python (Join-Path $PSScriptRoot 'build_scene.py') -- --stage $Stage --revision $Revision
} else {
  if(!$Output) {$Output=Join-Path $coolingSection "production/renders/review/$Revision"}
  & $coolingPython $coolingGate --owner "cooling-plant-$Revision" -- $coolingBlender --background (Join-Path $PSScriptRoot 'cooling_plant.blend') --threads 6 --python (Join-Path $PSScriptRoot 'render.py') -- --out $Output --cameras $Cameras --samples $Samples --width $Width
}
exit $LASTEXITCODE
