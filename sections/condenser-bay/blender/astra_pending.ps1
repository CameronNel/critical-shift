function Get-AstraPendingCameras {
    param([string]$SectionRoot,[string]$Pack,[string[]]$Names,[int]$Samples)
    $folder=Join-Path $SectionRoot "production/renders/review/$Pack"
    $manifestPath=Join-Path $folder 'render_manifest.json'
    if(-not (Test-Path -LiteralPath $manifestPath)){return $Names}
    $manifest=Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    if($manifest.gpu_denoising -ne $true){throw "Pack $Pack uses a different denoising backend; preserve it and use a distinct pack name."}
    $blendHash=(Get-FileHash -LiteralPath (Join-Path $SectionRoot 'blender/condenser_bay.blend') -Algorithm SHA256).Hash.ToLowerInvariant()
    if($manifest.blend_sha256 -ne $blendHash -or $manifest.engine -ne 'CYCLES' -or $manifest.device -ne 'GPU' -or $manifest.gpu_backend -ne 'HIP' -or $manifest.samples -ne $Samples -or $manifest.resolution[0] -ne 1920 -or $manifest.resolution[1] -ne 1080){throw "Pack $Pack does not match the saved scene/render settings; use a distinct pack name."}
    $toolNames=@('render.py','resource_guard.py')
    if($Pack.EndsWith('-supplemental')){$toolNames+=@('astra_evidence.py','kit.py')}
    foreach($toolName in $toolNames){
        $toolHash=(Get-FileHash -LiteralPath (Join-Path $SectionRoot "blender/$toolName") -Algorithm SHA256).Hash.ToLowerInvariant()
        if($manifest.renderer_source_sha256.$toolName -ne $toolHash){throw "Renderer source changed for $Pack; preserve it and use a distinct pack name."}
    }
    foreach($name in $Names){
        $entry=@($manifest.cameras | Where-Object camera -EQ $name)
        $file=Join-Path $folder "$name.png"
        if($entry.Count -eq 1 -and (Test-Path -LiteralPath $file)){
            $imageHash=(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
            if($imageHash -eq $entry[0].sha256){continue}
        }
        Write-Output $name
    }
}
