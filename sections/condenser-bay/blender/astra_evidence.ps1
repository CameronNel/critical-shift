param([string]$Revision,[int]$Samples=32,[int]$MaxWait=60)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'astra_pending.ps1')
$root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$env:BLENDER_USER_RESOURCES=Join-Path $root 'production/astra-blender-profile'
$blender='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
$gatePython='C:/Program Files/Blender Foundation/Blender 5.2/5.2/python/bin/python.exe'
$gate='C:/Users/Camer/Games/critical-shift/ops/facility-run/gpu_gate.py'
$env:ASTRA_RENDER_MODE='GPU'
foreach($round in @("$Revision-supplemental","cold-$Revision-supplemental")) {
    $pending=@(Get-AstraPendingCameras -SectionRoot $root -Pack $round -Names @('S01_LOCAL_U02','S02_LOCAL_CW','S03_FULL_ROOF','S04_GLASS','S05_FEET','S06_OPERATOR_WORK','S07_U04_CUTAWAY') -Samples $Samples)
    for($i=0;$i -lt $pending.Count;$i+=7){
        $batch=$pending[$i..([Math]::Min($i+6,$pending.Count-1))] -join ','
        & $gatePython $gate --owner astra-condenser-bay --max-wait $MaxWait -- $blender --background --factory-startup --disable-autoexec --threads 0 --python-exit-code 1 --python (Join-Path $PSScriptRoot 'resource_guard.py') (Join-Path $PSScriptRoot 'condenser_bay.blend') --python (Join-Path $PSScriptRoot 'astra_evidence.py') -- $round $batch $Samples
        if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
    }
}
