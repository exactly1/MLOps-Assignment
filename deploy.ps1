# PowerShell deployment script for California Housing ML API
# Usage: .\deploy.ps1 [build|deploy|stop|logs|status]

param(
    [string]$Action = "main"
)

# Configuration
$DOCKER_IMAGE = "california-housing-ml"
$CONTAINER_NAME = "ml-api"
$PORT = 8000

# Function to check if container is running
function Test-Container {
    $result = docker ps -q -f name=$CONTAINER_NAME 2>$null
    return $result -ne $null -and $result -ne ""
}

# Function to stop and remove existing container
function Remove-Container {
    if (Test-Container) {
        Write-Host "Stopping existing container..." -ForegroundColor Yellow
        docker stop $CONTAINER_NAME | Out-Null
        docker rm $CONTAINER_NAME | Out-Null
    }
}

# Function to build Docker image
function Build-Image {
    Write-Host "🔨 Building Docker image..." -ForegroundColor Blue
    docker build -t "${DOCKER_IMAGE}:latest" .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker image built successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to build Docker image" -ForegroundColor Red
        exit 1
    }
}

# Function to deploy container
function Deploy-Container {
    Write-Host "🚀 Deploying container..." -ForegroundColor Blue
    
    # Create necessary directories
    if (!(Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" }
    if (!(Test-Path "models")) { New-Item -ItemType Directory -Path "models" }
    if (!(Test-Path "exports")) { New-Item -ItemType Directory -Path "exports" }
    
    # Get current directory
    $currentDir = (Get-Location).Path
    
    # Run container
    docker run -d `
        --name $CONTAINER_NAME `
        -p "${PORT}:8000" `
        -v "${currentDir}/logs:/app/logs" `
        -v "${currentDir}/models:/app/models" `
        -v "${currentDir}/exports:/app/exports" `
        -e PYTHONPATH=/app `
        --restart unless-stopped `
        "${DOCKER_IMAGE}:latest"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Container deployed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to deploy container" -ForegroundColor Red
        exit 1
    }
}

# Function to check deployment health
function Test-Health {
    Write-Host "🔍 Performing health check..." -ForegroundColor Blue
    
    # Wait for service to start
    Start-Sleep -Seconds 10
    
    # Check if container is running
    if (!(Test-Container)) {
        Write-Host "❌ Container is not running" -ForegroundColor Red
        return $false
    }
    
    # Check API health endpoint
    $maxAttempts = 30
    $attempt = 1
    
    while ($attempt -le $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:${PORT}/health" -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Health check passed" -ForegroundColor Green
                return $true
            }
        } catch {
            # Continue trying
        }
        
        Write-Host "⏳ Attempt $attempt/$maxAttempts`: Waiting for service to be ready..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
        $attempt++
    }
    
    Write-Host "❌ Health check failed after $maxAttempts attempts" -ForegroundColor Red
    return $false
}

# Function to show deployment info
function Show-Info {
    Write-Host ""
    Write-Host "📋 Deployment Information:" -ForegroundColor Cyan
    Write-Host "  API URL: http://localhost:${PORT}" -ForegroundColor White
    Write-Host "  Health Check: http://localhost:${PORT}/health" -ForegroundColor White
    Write-Host "  API Docs: http://localhost:${PORT}/docs" -ForegroundColor White
    Write-Host "  Metrics: http://localhost:${PORT}/metrics" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Useful Commands:" -ForegroundColor Cyan
    Write-Host "  View logs: docker logs $CONTAINER_NAME" -ForegroundColor White
    Write-Host "  Stop service: docker stop $CONTAINER_NAME" -ForegroundColor White
    Write-Host "  Start service: docker start $CONTAINER_NAME" -ForegroundColor White
    Write-Host "  Remove service: docker stop $CONTAINER_NAME; docker rm $CONTAINER_NAME" -ForegroundColor White
}

# Main deployment process
function Invoke-Main {
    Write-Host "🚀 Starting deployment of California Housing ML API..." -ForegroundColor Blue
    
    # Check if Docker is running
    try {
        docker info | Out-Null
    } catch {
        Write-Host "❌ Docker is not running. Please start Docker and try again." -ForegroundColor Red
        exit 1
    }
    
    # Cleanup existing deployment
    Remove-Container
    
    # Build image
    Build-Image
    
    # Deploy container
    Deploy-Container
    
    # Health check
    if (Test-Health) {
        Show-Info
        Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Deployment failed health check" -ForegroundColor Red
        Write-Host "📋 Container logs:" -ForegroundColor Yellow
        docker logs $CONTAINER_NAME
        exit 1
    }
}

# Handle command line arguments
switch ($Action.ToLower()) {
    "build" {
        Build-Image
        break
    }
    "deploy" {
        Remove-Container
        Deploy-Container
        if (Test-Health) { Show-Info }
        break
    }
    "stop" {
        Remove-Container
        Write-Host "✅ Service stopped" -ForegroundColor Green
        break
    }
    "logs" {
        docker logs -f $CONTAINER_NAME
        break
    }
    "status" {
        if (Test-Container) {
            Write-Host "✅ Service is running" -ForegroundColor Green
            try {
                $health = Invoke-RestMethod -Uri "http://localhost:${PORT}/health" -TimeoutSec 5
                $health | ConvertTo-Json -Depth 3
            } catch {
                Write-Host "API not responding" -ForegroundColor Yellow
            }
        } else {
            Write-Host "❌ Service is not running" -ForegroundColor Red
        }
        break
    }
    default {
        Invoke-Main
        break
    }
}
