param(
    [string]$Stage='slice',
    [string]$Revision='s01',
    [string]$Cameras='S01_style,S02_material',
    [int]$Samples=48,
    [int]$Width=1440
)
$ErrorActionPreference='Stop'
$sectionPath = Split-Path $PSScriptRoot -Parent
$env:BLENDER_USER_RESOURCES = Join-Path $sectionPath '.blender-user'
$blenderPath='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
$pythonPath='C:/Users/Camer/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$gatePath='C:/Users/Camer/Games/critical-shift/ops/facility-run/gpu_gate.py'
$buildPath=Join-Path $PSScriptRoot 'build_dock.py'
$logPath=Join-Path $sectionPath "production/logs/$Revision.log"
if ($Cameras) {
    & $pythonPath $gatePath --owner compliance-dock -- $blenderPath --background --factory-startup --python-exit-code 1 --python $buildPath -- --stage $Stage --revision $Revision --render $Cameras --samples $Samples --width $Width *> $logPath
} else {
    & $blenderPath --background --factory-startup --python-exit-code 1 --python $buildPath -- --stage $Stage --revision $Revision --samples $Samples --width $Width *> $logPath
}
$code=$LASTEXITCODE
Get-Content -LiteralPath $logPath -Tail 16
exit $code
