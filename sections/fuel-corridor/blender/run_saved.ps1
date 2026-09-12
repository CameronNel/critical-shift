param([string]$Revision,[string]$OutName,[string]$Cameras='all',[switch]$RequireFull)
$section = Split-Path $PSScriptRoot -Parent
$env:BLENDER_USER_RESOURCES = Join-Path $section 'production/runtime'
$env:BLENDER_USER_CONFIG = Join-Path $section 'production/runtime/config'
New-Item -ItemType Directory -Force -Path $env:BLENDER_USER_CONFIG | Out-Null
$env:FUEL_CORRIDOR_ROOT = $section
$python = 'C:/Users/Camer/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$blender = 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
$gate = 'C:/Users/Camer/Games/critical-shift/ops/facility-run/gpu_gate.py'
$saved = Join-Path $section ('production/checkpoints/' + $Revision + '/Fuel_Corridor.blend')
if (-not $Revision) { $saved = Join-Path $section 'blender/Fuel_Corridor.blend' }
elseif (-not (Test-Path -LiteralPath $saved)) { $saved = Join-Path $section ('production/checkpoints/' + $Revision + '/blender/Fuel_Corridor.blend') }
$output = Join-Path $section ('production/renders/' + $OutName)
$renderArgs = @('--out',$output,'--cameras',$Cameras)
if ($RequireFull) { $renderArgs += '--require-full' }
& $python $gate --owner fuel-corridor -- $blender --background $saved --python-exit-code 1 --python (Join-Path $PSScriptRoot 'render_saved.py') -- @renderArgs
exit $LASTEXITCODE
