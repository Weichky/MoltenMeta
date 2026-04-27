$SCRIPT_DIR = $PSScriptRoot

Write-Host "========================================"
Write-Host "Building all modules in parallel..."
Write-Host "========================================"

$jobs = @()
Get-ChildItem -Path $SCRIPT_DIR -Directory | ForEach-Object {
    $moduleDir = $_.FullName
    $moduleName = $_.Name
    $buildScript = Join-Path $moduleDir "build.ps1"

    if (Test-Path $buildScript) {
        Write-Host ">>> Building $moduleName in background..."
        $jobs += Start-Job -ScriptBlock {
            param($script, $name)
            & $script
            if ($LASTEXITCODE -ne 0) {
                Write-Host ">>> $name build FAILED"
                exit 1
            }
            Write-Host ">>> $name build complete."
        } -ArgumentList $buildScript, $moduleName
    }
}

Write-Host ""
Write-Host ">>> Waiting for all builds to complete..."
Write-Host ""

$failed = $false
foreach ($job in $jobs) {
    Receive-Job -Job $job -Wait -AutoRemove
    if ($job.State -eq "Failed") {
        $failed = $true
    }
}

Write-Host ""
Write-Host "========================================"
if ($failed) {
    Write-Host "Some modules failed to build."
    exit 1
} else {
    Write-Host "All modules built successfully."
}
Write-Host "========================================"
