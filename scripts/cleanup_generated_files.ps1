# cleanup_generated_files.ps1
# Deletes all generated Python files while preserving folder structure and __init__.py files
# This script is useful before regenerating tools to ensure a clean state

$ErrorActionPreference = "Stop"

# Get script directory and project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

Write-Host "Cleaning up generated files..." -ForegroundColor Cyan
Write-Host "Project root: $projectRoot" -ForegroundColor Gray
Write-Host ""

# Define paths to clean
$pathsToClean = @(
    "$projectRoot\src\pydantic_ai_integration\tools\generated",
    "$projectRoot\tests\unit",
    "$projectRoot\tests\integration",
    "$projectRoot\tests\api"
)

$totalFilesDeleted = 0
$totalFoldersPreserved = 0

foreach ($basePath in $pathsToClean) {
    if (-not (Test-Path $basePath)) {
        Write-Host "Path not found: $basePath" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "Processing: $basePath" -ForegroundColor Green
    
    # Find all .py files that are NOT __init__.py
    $filesToDelete = Get-ChildItem -Path $basePath -Filter "*.py" -Recurse | Where-Object { $_.Name -ne "__init__.py" }
    
    if ($filesToDelete.Count -eq 0) {
        Write-Host "   No generated files to delete" -ForegroundColor Gray
    } else {
        foreach ($file in $filesToDelete) {
            $relativePath = $file.FullName.Replace($projectRoot, "").TrimStart("\")
            Write-Host "   Deleting: $relativePath" -ForegroundColor DarkGray
            Remove-Item -Path $file.FullName -Force
            $totalFilesDeleted++
        }
        Write-Host "   Deleted $($filesToDelete.Count) file(s)" -ForegroundColor Green
    }
    
    # Count preserved folders
    $folders = Get-ChildItem -Path $basePath -Directory -Recurse
    $totalFoldersPreserved += $folders.Count
    
    Write-Host ""
}

Write-Host "Cleanup complete!" -ForegroundColor Green
Write-Host "   Files deleted: $totalFilesDeleted" -ForegroundColor Cyan
Write-Host "   Folders preserved: $totalFoldersPreserved" -ForegroundColor Cyan
Write-Host "   __init__.py files: Preserved" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ready for fresh tool generation!" -ForegroundColor Magenta

