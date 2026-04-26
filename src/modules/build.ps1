$SCRIPT_DIR = $PSScriptRoot

Write-Host "========================================"
Write-Host "Building all modules..."
Write-Host "========================================"

Get-ChildItem -Path $SCRIPT_DIR -Directory | ForEach-Object {
    $moduleDir = $_.FullName
    $moduleName = $_.Name
    $buildScript = Join-Path $moduleDir "build.ps1"

    if (Test-Path $buildScript) {
        Write-Host ""
        Write-Host ">>> Building $moduleName..."
        & $buildScript
        Write-Host ">>> $moduleName build complete."
    }
}

Write-Host ""
Write-Host "========================================"
Write-Host "All modules built successfully."
Write-Host "========================================"
