# PowerShell deployment script for MLOps Assignment
# This script builds, pushes, pulls, and starts all containers for API and UI

param(
    [string]$DockerUsername = "your-docker-username"
)

Write-Host "Building API Docker image..." -ForegroundColor Cyan
docker build -t $DockerUsername/california-housing-ml-api:latest -f Dockerfile.api .

Write-Host "Building UI Docker image..." -ForegroundColor Cyan
docker build -t $DockerUsername/california-housing-ml-ui:latest -f Dockerfile.ui .

Write-Host "Pushing API Docker image to Docker Hub..." -ForegroundColor Cyan
docker push $DockerUsername/california-housing-ml-api:latest

Write-Host "Pushing UI Docker image to Docker Hub..." -ForegroundColor Cyan
docker push $DockerUsername/california-housing-ml-ui:latest

Write-Host "Pulling latest images from Docker Hub..." -ForegroundColor Cyan
$env:DOCKER_USERNAME = $DockerUsername
docker-compose pull

Write-Host "Starting all services..." -ForegroundColor Green
$env:DOCKER_USERNAME = $DockerUsername
docker-compose up -d

Write-Host "Deployment complete!" -ForegroundColor Green
