param([string]$Revision='R22', [int]$Samples=64, [int]$MaxWait=60)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'astra_pending.ps1')
$sectionRoot=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
# Keep each whole pack resident for GPU speed; cold remains an independent reopen.
$names=@('C01_ENTRY','C02_HERO','C03_REVERSE','C04_EXHAUST','C05_RETURN','C06_COOLING','C07_OPERATOR','C08_MAINT','C09_ROOF','C10_MATERIALS','W01_ENTRY_CORNER','W02_SW_TURN','W03_NW','W04_NE','W05_SE','W06_WEST_AISLE','W07_EAST_PULL','W08_GALLERY_TURN')
foreach($pack in @($Revision,"cold-$Revision")) {
    $pending=@(Get-AstraPendingCameras -SectionRoot $sectionRoot -Pack $pack -Names $names -Samples $Samples)
    for($i=0;$i -lt $pending.Count;$i+=18) {
        $batch=$pending[$i..([Math]::Min($i+17,$pending.Count-1))] -join ','
        & (Join-Path $PSScriptRoot 'run.ps1') -Revision $pack -Reopen -Cameras $batch -Samples $Samples -MaxWait $MaxWait
        if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
    }
}
