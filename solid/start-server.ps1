# Start Solid Server via Docker Desktop
# 
# Instructions:
# 1. Open Docker Desktop
# 2. Go to "Containers" 
# 3. Click "+" (Create Container)
# 4. Select "docker-compose.yml" from this folder
# 5. Click "Start"
#
# OR use this script if docker is in PATH:

Write-Host "Starting Solid Server container..." -ForegroundColor Cyan

# Try different docker paths
$dockerPaths = @(
    "C:\Program Files\Docker\Docker\resources\bin\docker.exe",
    "C:\Program Files\Docker\Docker\resources\docker.exe",
    "$env:ProgramFiles\Docker\Docker\resources\bin\docker.exe"
)

$dockerExe = $null
foreach ($path in $dockerPaths) {
    if (Test-Path $path) {
        $dockerExe = $path
        Write-Host "Found Docker at: $dockerExe" -ForegroundColor Green
        break
    }
}

if ($dockerExe) {
    & $dockerExe compose -f docker-compose.yml up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Solid server started successfully!" -ForegroundColor Green
        Write-Host "   Access at: http://localhost:3000" -ForegroundColor Cyan
        Write-Host "`nView logs:" -ForegroundColor Yellow
        Write-Host "   & '$dockerExe' logs tiny-collider-solid -f" -ForegroundColor Gray
    } else {
        Write-Host "`n❌ Failed to start container" -ForegroundColor Red
    }
} else {
    Write-Host "`n⚠️  Docker executable not found in common locations" -ForegroundColor Yellow
    Write-Host "`nManual steps:" -ForegroundColor Cyan
    Write-Host "1. Open Docker Desktop"
    Write-Host "2. Navigate to this folder: $PWD"
    Write-Host "3. Right-click docker-compose.yml"
    Write-Host "4. Select 'Compose Up'"
    Write-Host "`nOr add Docker to PATH and run:"
    Write-Host "   docker compose -f docker-compose.yml up -d"
}
