param(
    [string]$Revision = 'R01',
    [string]$Cameras = '',
    [int]$Samples = 32,
    [int]$Width = 1920,
    [int]$Height = 1080,
    [switch]$Reopen,
    [switch]$ValidateOnly,
    [int]$MaxWait = 900
)
$ErrorActionPreference = 'Stop'
$sectionRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$profile = Join-Path $sectionRoot 'production/astra-blender-profile'
foreach ($d in @('config','scripts','datafiles','extensions')) {
    New-Item -ItemType Directory -Force -Path (Join-Path $profile $d) | Out-Null
}
$env:BLENDER_USER_RESOURCES = $profile
$env:BLENDER_USER_CONFIG = Join-Path $profile 'config'
$env:BLENDER_USER_SCRIPTS = Join-Path $profile 'scripts'
$env:BLENDER_USER_DATAFILES = Join-Path $profile 'datafiles'
$env:BLENDER_USER_EXTENSIONS = Join-Path $profile 'extensions'
$env:PYTHONUTF8 = '1'
$blenderExe = 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
$blend = Join-Path $PSScriptRoot 'condenser_bay.blend'
$gatePython='C:/Program Files/Blender Foundation/Blender 5.2/5.2/python/bin/python.exe'
$gate='C:/Users/Camer/Games/critical-shift/ops/facility-run/gpu_gate.py'
$env:ASTRA_RENDER_MODE='GPU'

if ($ValidateOnly) {
    & $gatePython $gate --owner astra-condenser-bay --max-wait $MaxWait -- $blenderExe --background --factory-startup --disable-autoexec --threads 0 --python-exit-code 1 --python (Join-Path $PSScriptRoot 'resource_guard.py') --python (Join-Path $PSScriptRoot 'build_condenser.py') -- --revision $Revision
    exit $LASTEXITCODE
}

if ($Reopen) {
    $blenderArgs = @(
        '--background', '--factory-startup', '--disable-autoexec', '--threads', '0', '--python-exit-code', '1', '--python', (Join-Path $PSScriptRoot 'resource_guard.py'), $blend,
        '--python', (Join-Path $PSScriptRoot 'render_only.py'), '--',
        '--revision', $Revision, '--render', $(if ($Cameras) { $Cameras } else { 'all' }),
        '--samples', "$Samples", '--width', "$Width", '--height', "$Height"
    )
} else {
    $renderArg = $(if ($Cameras) { $Cameras } else { 'all' })
    $blenderArgs = @(
        '--background', '--factory-startup', '--disable-autoexec', '--python-exit-code', '1', '--threads', '0', '--python', (Join-Path $PSScriptRoot 'resource_guard.py'),
        '--python', (Join-Path $PSScriptRoot 'build_condenser.py'), '--',
        '--revision', $Revision, '--render', $renderArg, '--samples', "$Samples",
        '--width', "$Width", '--height', "$Height"
    )
}

# User reauthorized full GPU speed. The shared gate serializes facility renders.
& $gatePython $gate --owner astra-condenser-bay --max-wait $MaxWait -- $blenderExe @blenderArgs
exit $LASTEXITCODE
