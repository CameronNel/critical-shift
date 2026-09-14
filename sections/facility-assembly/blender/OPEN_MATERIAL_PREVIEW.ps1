$assemblyRoot = Split-Path -Parent $PSScriptRoot
$env:BLENDER_USER_CONFIG = Join-Path $assemblyRoot 'production/blender-profile'
$previewScript = Join-Path $PSScriptRoot 'open_material_preview.py'
Start-Process -FilePath 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -ArgumentList @('--window-geometry','80','60','1920','1080','--python',('"' + $previewScript + '"')) -WindowStyle Normal
