# Interactive launcher for the saved spawn exterior implementation checkpoint.
$assemblyRoot = Split-Path -Parent $PSScriptRoot
$env:BLENDER_USER_CONFIG = Join-Path $assemblyRoot 'production/blender-profile'
$env:PREVIEW_SOURCE = 'facility_spawn_material_preview_R17.blend'
$previewScript = Join-Path $PSScriptRoot 'open_material_preview.py'
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --window-geometry 80 60 1920 1080 --python $previewScript


