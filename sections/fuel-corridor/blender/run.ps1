param([string]$Stage='full',[string]$Revision='r01',[string]$Cameras='all',[int]$Samples=32,[int]$Width=1440,[switch]$NoRender)
$section = Split-Path $PSScriptRoot -Parent
$env:BLENDER_USER_RESOURCES = Join-Path $section 'production/runtime'
$env:BLENDER_USER_CONFIG = Join-Path $section 'production/runtime/config'
New-Item -ItemType Directory -Force -Path $env:BLENDER_USER_CONFIG | Out-Null
$env:FUEL_CORRIDOR_ROOT = $section
$python = 'C:/Users/Camer/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$blender = 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
$gate = 'C:/Users/Camer/Games/critical-shift/ops/facility-run/gpu_gate.py'
$snapshotDir = Join-Path $section ('production/checkpoints/' + $Revision)
New-Item -ItemType Directory -Force -Path $snapshotDir | Out-Null
$snapshot = Join-Path $snapshotDir 'build.py'
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'build.py') -Destination $snapshot
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'valorant_details.py') -Destination (Join-Path $snapshotDir 'valorant_details.py')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'wayfinding.py') -Destination (Join-Path $snapshotDir 'wayfinding.py')
Copy-Item -LiteralPath (Join-Path $section 'interface.json') -Destination (Join-Path $snapshotDir 'interface.json')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'validate.py') -Destination (Join-Path $snapshotDir 'validate.py')
if ($NoRender) {
    & $blender --background --factory-startup --python-exit-code 1 --python $snapshot -- --stage $Stage --revision $Revision --samples $Samples --width $Width
} else {
    & $python $gate --owner fuel-corridor -- $blender --background --factory-startup --python-exit-code 1 --python $snapshot -- --stage $Stage --revision $Revision --render $Cameras --samples $Samples --width $Width
}
$fcExit = $LASTEXITCODE
if ($fcExit -eq 0) {
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'Fuel_Corridor.blend') -Destination (Join-Path $snapshotDir 'Fuel_Corridor.blend')
    Copy-Item -LiteralPath (Join-Path $section ('production/renders/review/' + $Revision + '/build_manifest.json')) -Destination (Join-Path $snapshotDir 'build_manifest.json')
    if ($Stage -eq 'full') { Copy-Item -LiteralPath (Join-Path $section 'scenery/handoff.json') -Destination (Join-Path $snapshotDir 'handoff.json') }
}
exit $fcExit
