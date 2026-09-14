param([Parameter(Mandatory=$true)][string]$Revision,[int]$Samples=32)
$ErrorActionPreference='Stop'
$sectionRoot=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$blender='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
$comparePython='C:/Users/Camer/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$env:BLENDER_USER_RESOURCES=Join-Path $sectionRoot 'production/astra-blender-profile'
$env:ASTRA_RENDER_MODE='GPU'
$env:ASTRA_GPU_DENOISE='1'

# One bounded complete-room evidence round, never an automatic art acceptance.
& $blender --background --factory-startup --disable-autoexec --threads 0 --python-exit-code 1 --python (Join-Path $PSScriptRoot 'resource_guard.py') (Join-Path $PSScriptRoot 'condenser_bay.blend') --python (Join-Path $PSScriptRoot 'astra_validate_saved.py')
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& (Join-Path $PSScriptRoot 'astra_review.ps1') -Revision $Revision -Samples $Samples
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& (Join-Path $PSScriptRoot 'astra_evidence.ps1') -Revision $Revision -Samples $Samples
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& $comparePython (Join-Path $sectionRoot 'production/compare_pack.py') $Revision
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& $comparePython (Join-Path $sectionRoot 'production/compare_pack.py') "$Revision-supplemental"
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
Write-Output "COMPLETE_EVIDENCE_ROUND $Revision - independent Luna scoring still required"
