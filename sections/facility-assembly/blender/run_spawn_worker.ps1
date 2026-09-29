param(
    [string]$Scene = 'facility_environment.spawn-candidate.blend',
    [string]$Script = 'render_spawn_finish.py',
    [string]$Mode = '',
    [switch]$Gpu
)
$ErrorActionPreference = 'Stop'
$taskRoot = 'C:/Users/Camer/Games/critical-shift'
$blendRoot = Join-Path $PSScriptRoot $Scene
$taskScript = Join-Path $PSScriptRoot $Script
if (-not (Test-Path -LiteralPath $blendRoot)) { throw 'Missing source blend' }
if (-not (Test-Path -LiteralPath $taskScript)) { throw 'Missing task script' }
$blendExe = 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
$arguments = '--background --factory-startup --python-exit-code 1 --threads 1 "' + $blendRoot + '" --python "' + $taskScript + '"'
if ($Mode) { $arguments += ' -- ' + $Mode }
$workerExe = $blendExe
$spawnProfile = $taskRoot + '/runtime/out/spawn-blender-profile'
$env:BLENDER_USER_RESOURCES = $spawnProfile
$env:BLENDER_USER_CONFIG = $spawnProfile + '/config'
$env:BLENDER_USER_SCRIPTS = $spawnProfile + '/scripts'
$env:BLENDER_USER_DATAFILES = $spawnProfile + '/datafiles'
$env:BLENDER_USER_EXTENSIONS = $spawnProfile + '/extensions'
if ($Gpu) {
    $workerExe = 'C:/Users/Camer/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
    $arguments = '"' + $taskRoot + '/ops/facility-run/gpu_gate.py" --owner spawn-yard-finish --max-wait 300 -- "' + $blendExe + '" ' + $arguments
}
$worker = Start-Process -FilePath $workerExe -ArgumentList $arguments -WindowStyle Hidden -PassThru -RedirectStandardOutput ($taskRoot + '/runtime/out/spawn-finish.log') -RedirectStandardError ($taskRoot + '/runtime/out/spawn-finish-errors.log')
$worker.PriorityClass = 'BelowNormal'
$worker.Id
