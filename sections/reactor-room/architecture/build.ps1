$ErrorActionPreference = 'Stop'
$drawingDirectory = $PSScriptRoot
$drawingPython = 'C:/Users/Camer/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$drawingPoppler = 'C:/Users/Camer/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe'
& $drawingPython (Join-Path $drawingDirectory 'build_drawings.py')
if ($LASTEXITCODE -ne 0) { throw 'Architectural drawing generation failed.' }
$drawingPreviews = Join-Path $drawingDirectory 'output/previews'
New-Item -ItemType Directory -Force -Path $drawingPreviews | Out-Null
& $drawingPoppler -png -scale-to 2400 (Join-Path $drawingDirectory 'output/reactor_compact_stair_architectural_set.pdf') (Join-Path $drawingPreviews 'sheet')
if ($LASTEXITCODE -ne 0) { throw 'Architectural PDF rendering failed.' }
