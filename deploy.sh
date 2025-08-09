#!/bin/bash
# Deployment script for California Housing ML API

set -e  # Exit on any error

echo "🚀 Starting deployment of California Housing ML API..."

# Configuration
DOCKER_IMAGE="california-housing-ml"
CONTAINER_NAME="ml-api"
PORT=8000

# Function to check if container is running
check_container() {
    docker ps -q -f name=${CONTAINER_NAME}
}

# Function to stop and remove existing container
cleanup_container() {
    if [ "$(check_container)" ]; then
        echo "Stopping existing container..."
        docker stop ${CONTAINER_NAME}
        docker rm ${CONTAINER_NAME}
    fi
}

# Function to build Docker image
build_image() {
    echo "🔨 Building Docker image..."
    docker build -t ${DOCKER_IMAGE}:latest .
    echo "✅ Docker image built successfully"
}

# Function to deploy container
deploy_container() {
    echo "🚀 Deploying container..."
    
    # Create necessary directories
    mkdir -p logs models exports
    
    # Run container
    docker run -d \
        --name ${CONTAINER_NAME} \
        -p ${PORT}:8000 \
        -v $(pwd)/logs:/app/logs \
        -v $(pwd)/models:/app/models \
        -v $(pwd)/exports:/app/exports \
        -e PYTHONPATH=/app \
        --restart unless-stopped \
        ${DOCKER_IMAGE}:latest
    
    echo "✅ Container deployed successfully"
}

# Function to check deployment health
health_check() {
    echo "🔍 Performing health check..."
    
    # Wait for service to start
    sleep 10
    
    # Check if container is running
    if [ ! "$(check_container)" ]; then
        echo "❌ Container is not running"
        return 1
    fi
    
    # Check API health endpoint
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:${PORT}/health > /dev/null 2>&1; then
            echo "✅ Health check passed"
            return 0
        fi
        
        echo "⏳ Attempt $attempt/$max_attempts: Waiting for service to be ready..."
        sleep 2
        ((attempt++))
    done
    
    echo "❌ Health check failed after $max_attempts attempts"
    return 1
}

# Function to show deployment info
show_info() {
    echo ""
    echo "📋 Deployment Information:"
    echo "  API URL: http://localhost:${PORT}"
    echo "  Health Check: http://localhost:${PORT}/health"
    echo "  API Docs: http://localhost:${PORT}/docs"
    echo "  Metrics: http://localhost:${PORT}/metrics"
    echo ""
    echo "🔧 Useful Commands:"
    echo "  View logs: docker logs ${CONTAINER_NAME}"
    echo "  Stop service: docker stop ${CONTAINER_NAME}"
    echo "  Start service: docker start ${CONTAINER_NAME}"
    echo "  Remove service: docker stop ${CONTAINER_NAME} && docker rm ${CONTAINER_NAME}"
}

# Main deployment process
main() {
    echo "Starting deployment process..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Cleanup existing deployment
    cleanup_container
    
    # Build image
    build_image
    
    # Deploy container
    deploy_container
    
    # Health check
    if health_check; then
        show_info
        echo "🎉 Deployment completed successfully!"
    else
        echo "❌ Deployment failed health check"
        echo "📋 Container logs:"
        docker logs ${CONTAINER_NAME}
        exit 1
    fi
}

# Check command line arguments
case "${1:-}" in
    "build")
        build_image
        ;;
    "deploy")
        cleanup_container
        deploy_container
        health_check && show_info
        ;;
    "stop")
        cleanup_container
        echo "✅ Service stopped"
        ;;
    "logs")
        docker logs -f ${CONTAINER_NAME}
        ;;
    "status")
        if [ "$(check_container)" ]; then
            echo "✅ Service is running"
            curl -s http://localhost:${PORT}/health | python -m json.tool 2>/dev/null || echo "API not responding"
        else
            echo "❌ Service is not running"
        fi
        ;;
    *)
        main
        ;;
esac
