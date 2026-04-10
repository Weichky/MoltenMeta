$SCRIPT_DIR = $PSScriptRoot
$BUILD_DIR = Join-Path $SCRIPT_DIR "build"
$LIB_DIR = Join-Path $SCRIPT_DIR "lib"

New-Item -ItemType Directory -Force -Path $BUILD_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $LIB_DIR | Out-Null

Set-Location $BUILD_DIR

cmake ..
cmake --build . --config Release

Write-Host "Build complete. Library located at: $LIB_DIR"
