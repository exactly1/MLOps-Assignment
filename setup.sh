#!/bin/bash
# Setup script for MLOps Assignment

set -e

echo "🔧 Setting up MLOps Assignment environment..."

# Check Python version
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo "❌ Python not found. Please install Python 3.9+"
        exit 1
    fi
    
    echo "✅ Using Python: $($PYTHON_CMD --version)"
}

# Create virtual environment
setup_venv() {
    echo "📦 Setting up virtual environment..."
    
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
        echo "✅ Virtual environment created"
    else
        echo "✅ Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
}

# Install dependencies
install_dependencies() {
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
}

# Setup directories
setup_directories() {
    echo "📁 Creating project directories..."
    mkdir -p logs models exports plots data/raw data/processed mlruns
    echo "✅ Directories created"
}

# Initialize Git (if not already initialized)
setup_git() {
    if [ ! -d ".git" ]; then
        echo "🔄 Initializing Git repository..."
        git init
        git add .
        git commit -m "Initial commit: MLOps Assignment setup"
        echo "✅ Git repository initialized"
    else
        echo "✅ Git repository already exists"
    fi
}

# Initialize DVC (if not already initialized)
setup_dvc() {
    if [ ! -d ".dvc" ]; then
        echo "📊 Initializing DVC..."
        dvc init
        echo "✅ DVC initialized"
    else
        echo "✅ DVC already initialized"
    fi
}

# Setup MLflow
setup_mlflow() {
    echo "🔬 Setting up MLflow..."
    export MLFLOW_TRACKING_URI=sqlite:///mlflow.db
    echo "✅ MLflow configured"
}

# Run initial model training
train_models() {
    echo "🤖 Training initial models..."
    $PYTHON_CMD src/models/train.py
    echo "✅ Models trained successfully"
}

# Test API
test_api() {
    echo "🧪 Testing API..."
    $PYTHON_CMD -m pytest tests/ -v
    echo "✅ Tests completed"
}

# Main setup function
main() {
    echo "Starting MLOps Assignment setup..."
    
    check_python
    setup_venv
    install_dependencies
    setup_directories
    setup_git
    # setup_dvc  # Uncomment if you want to use DVC
    setup_mlflow
    train_models
    # test_api  # Uncomment to run tests
    
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Activate virtual environment: source venv/bin/activate"
    echo "  2. Start the API: python src/api/main.py"
    echo "  3. Visit: http://localhost:8000/docs"
    echo "  4. Or deploy with Docker: ./deploy.sh"
    echo ""
    echo "🔧 Development commands:"
    echo "  - Train models: python src/models/train.py"
    echo "  - Evaluate models: python src/models/evaluate.py"
    echo "  - Run tests: pytest tests/"
    echo "  - Start MLflow UI: mlflow ui"
}

# Handle command line arguments
case "${1:-}" in
    "venv")
        check_python
        setup_venv
        ;;
    "deps")
        install_dependencies
        ;;
    "train")
        setup_mlflow
        train_models
        ;;
    "test")
        test_api
        ;;
    *)
        main
        ;;
esac
