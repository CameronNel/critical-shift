param(
    [ValidateSet('build','render','validate')][string]$Action = 'build',
    [string]$Revision = 'slice-r01',
    [ValidateSet('slice','full')][string]$Stage = 'slice',
    [string]$Cameras = 'all',
    [int]$Samples = 64,
    [int]$Width = 1280,
    [int]$Height = 800,
    [string]$Blend = '',
    [string]$Output = ''
)
$ErrorActionPreference = 'Stop'
$sectionRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$runtimeRoot = Join-Path $sectionRoot '.runtime'
New-Item -ItemType Directory -Force -Path $runtimeRoot | Out-Null
$env:BLENDER_USER_RESOURCES = $runtimeRoot
$blenderExe = 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
$pythonExe = 'C:/Users/Camer/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$gpuGate = 'C:/Users/Camer/Games/critical-shift/ops/facility-run/gpu_gate.py'
if (-not $Blend) { $Blend = Join-Path $sectionRoot 'blender/waste-storage.blend' }
if ($Action -eq 'build') {
    & $blenderExe --background --factory-startup --python-exit-code 1 --python (Join-Path $sectionRoot 'blender/build_scene.py') -- --stage $Stage --output $Blend --revision $Revision
} elseif ($Action -eq 'render') {
    if (-not $Output) { $Output = Join-Path $sectionRoot "production/renders/review/$Revision" }
    & $pythonExe $gpuGate --owner waste-storage -- $blenderExe --background --factory-startup $Blend --python-exit-code 1 --python (Join-Path $PSScriptRoot 'render_batch.py') -- --output $Output --cameras $Cameras --samples $Samples --width $Width --height $Height --revision $Revision
} elseif ($Action -eq 'validate') {
    if (-not $Output) { $Output = Join-Path $sectionRoot "production/validation/$Revision.json" }
    & $blenderExe --background --factory-startup $Blend --python-exit-code 1 --python (Join-Path $PSScriptRoot 'validate_scene.py') -- --output $Output
}
if ($LASTEXITCODE -ne 0) { throw "Waste Storage $Action exited $LASTEXITCODE" }
