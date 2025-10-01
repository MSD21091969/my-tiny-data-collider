# Alternative: Start Solid Server with direct docker run
# (Avoids docker-compose credential issues)

Write-Host "Starting Solid Server container (direct docker run)..." -ForegroundColor Cyan

$dockerExe = "C:\Program Files\Docker\Docker\resources\bin\docker.exe"

if (Test-Path $dockerExe) {
    Write-Host "Found Docker at: $dockerExe" -ForegroundColor Green
    
    # Stop existing container if running
    & $dockerExe stop tiny-collider-solid 2>$null
    & $dockerExe rm tiny-collider-solid 2>$null
    
    # Create solid-data directory if doesn't exist
    if (-not (Test-Path ".\solid-data")) {
        New-Item -ItemType Directory -Path ".\solid-data" | Out-Null
        Write-Host "Created ./solid-data directory" -ForegroundColor Green
    }
    
    # Run container
    Write-Host "`nStarting container..." -ForegroundColor Yellow
    & $dockerExe run -d `
        --name tiny-collider-solid `
        -p 3000:3000 `
        -v "${PWD}\solid-data:/data" `
        -v "${PWD}\solid-config:/config" `
        -e CSS_CONFIG=/config/config.json `
        -e CSS_BASE_URL=http://localhost:3000/ `
        -e CSS_PORT=3000 `
        solidproject/community-server:latest `
        npx @solid/community-server -c /config/config.json -p 3000
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Solid server started successfully!" -ForegroundColor Green
        Write-Host "   Container: tiny-collider-solid" -ForegroundColor Cyan
        Write-Host "   Access at: http://localhost:3000" -ForegroundColor Cyan
        Write-Host "`nWait 10-15 seconds for server to initialize..." -ForegroundColor Yellow
        Write-Host "`nView logs:" -ForegroundColor Yellow
        Write-Host "   & '$dockerExe' logs tiny-collider-solid -f" -ForegroundColor Gray
        Write-Host "`nStop server:" -ForegroundColor Yellow
        Write-Host "   & '$dockerExe' stop tiny-collider-solid" -ForegroundColor Gray
    } else {
        Write-Host "`n❌ Failed to start container" -ForegroundColor Red
    }
} else {
    Write-Host "`n❌ Docker not found at expected location" -ForegroundColor Red
}
