$SCRIPT_DIR = $PSScriptRoot
$BUILD_DIR = Join-Path $SCRIPT_DIR "build"
$LIB_DIR = Join-Path $SCRIPT_DIR "lib"

New-Item -ItemType Directory -Force -Path $BUILD_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $LIB_DIR | Out-Null

$cacheFile = Join-Path $BUILD_DIR "CMakeCache.txt"
if (Test-Path $cacheFile) {
    $cachedSource = Select-String -Path $cacheFile -Pattern "^CMAKE_HOME_DIRECTORY:" | ForEach-Object { ($_ -split "=")[1].Trim() }
    if ($cachedSource -and $cachedSource -ne $SCRIPT_DIR) {
        Write-Host "Stale CMake cache detected, cleaning build directory..."
        Remove-Item -Path "$BUILD_DIR\*" -Recurse -Force
    }
}

Set-Location $BUILD_DIR

cmake $SCRIPT_DIR
cmake --build . --config Release

Write-Host "Build complete. Library located at: $LIB_DIR"
