param(
    [ValidateSet('slice','full','render','cold')][string]$Mode='full',
    [string]$Revision='R01',
    [string]$Cameras='all',
    [int]$Samples=48,
    [int]$Width=1440,
    [int]$Height=900
)
$ErrorActionPreference='Stop'
$SectionRoot=Split-Path -Parent $PSScriptRoot
$BlenderExe='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
$PythonExe='C:/Users/Camer/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$GpuGate='C:/Users/Camer/Games/critical-shift/ops/facility-run/gpu_gate.py'
$env:BLENDER_USER_RESOURCES=Join-Path $SectionRoot '.blender-user'
if($Mode -in @('slice','full')) {
    & $BlenderExe --background --factory-startup --python (Join-Path $PSScriptRoot 'build_room.py') -- --stage $Mode --revision $Revision
    if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
}
$BlendFile=Join-Path $PSScriptRoot $(if($Mode -eq 'slice'){'electrical_slice.blend'}else{'electrical_room.blend'})
$Out=Join-Path $SectionRoot "production/renders/review/$Revision"
if($Mode -eq 'cold'){$Out=Join-Path $SectionRoot 'production/renders/final'}
& $PythonExe $GpuGate --owner electrical-room -- $BlenderExe --background $BlendFile --python (Join-Path $PSScriptRoot 'render_room.py') -- --out $Out --cameras $Cameras --samples $Samples --width $Width --height $Height
exit $LASTEXITCODE
