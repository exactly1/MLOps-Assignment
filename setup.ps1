# PowerShell setup script for MLOps Assignment
param(
    [string]$Action = "main"
)

# Function to check Python installation
function Test-Python {
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✅ Using Python: $pythonVersion" -ForegroundColor Green
        return "python"
    } catch {
        try {
            $pythonVersion = python3 --version 2>&1
            Write-Host "✅ Using Python: $pythonVersion" -ForegroundColor Green
            return "python3"
        } catch {
            Write-Host "❌ Python not found. Please install Python 3.9+" -ForegroundColor Red
            exit 1
        }
    }
}

# Function to create virtual environment
function New-VirtualEnvironment {
    param([string]$PythonCmd)
    
    Write-Host "📦 Setting up virtual environment..." -ForegroundColor Blue
    
    if (!(Test-Path "venv")) {
        & $PythonCmd -m venv venv
        Write-Host "✅ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
    }
    
    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"
    
    # Upgrade pip
    python -m pip install --upgrade pip
}

# Function to install dependencies
function Install-Dependencies {
    Write-Host "📥 Installing dependencies..." -ForegroundColor Blue
    pip install -r requirements.txt
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
}

# Function to setup directories
function New-ProjectDirectories {
    Write-Host "📁 Creating project directories..." -ForegroundColor Blue
    
    $directories = @("logs", "models", "exports", "plots", "data/raw", "data/processed", "mlruns")
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Write-Host "✅ Directories created" -ForegroundColor Green
}

# Function to initialize Git
function Initialize-Git {
    if (!(Test-Path ".git")) {
        Write-Host "🔄 Initializing Git repository..." -ForegroundColor Blue
        git init
        git add .
        git commit -m "Initial commit: MLOps Assignment setup"
        Write-Host "✅ Git repository initialized" -ForegroundColor Green
    } else {
        Write-Host "✅ Git repository already exists" -ForegroundColor Green
    }
}

# Function to setup MLflow
function Initialize-MLflow {
    Write-Host "🔬 Setting up MLflow..." -ForegroundColor Blue
    $env:MLFLOW_TRACKING_URI = "sqlite:///mlflow.db"
    Write-Host "✅ MLflow configured" -ForegroundColor Green
}

# Function to train initial models
function Start-ModelTraining {
    Write-Host "🤖 Training initial models..." -ForegroundColor Blue
    python src/models/train.py
    Write-Host "✅ Models trained successfully" -ForegroundColor Green
}

# Function to run tests
function Invoke-Tests {
    Write-Host "🧪 Testing API..." -ForegroundColor Blue
    python -m pytest tests/ -v
    Write-Host "✅ Tests completed" -ForegroundColor Green
}

# Function to show setup completion info
function Show-CompletionInfo {
    Write-Host ""
    Write-Host "🎉 Setup completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Activate virtual environment: .\venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "  2. Start the API: python src/api/main.py" -ForegroundColor White
    Write-Host "  3. Visit: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "  4. Or deploy with Docker: .\deploy.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Development commands:" -ForegroundColor Cyan
    Write-Host "  - Train models: python src/models/train.py" -ForegroundColor White
    Write-Host "  - Evaluate models: python src/models/evaluate.py" -ForegroundColor White
    Write-Host "  - Run tests: pytest tests/" -ForegroundColor White
    Write-Host "  - Start MLflow UI: mlflow ui" -ForegroundColor White
}

# Main setup function
function Invoke-Setup {
    Write-Host "🔧 Setting up MLOps Assignment environment..." -ForegroundColor Blue
    
    $pythonCmd = Test-Python
    New-VirtualEnvironment -PythonCmd $pythonCmd
    Install-Dependencies
    New-ProjectDirectories
    Initialize-Git
    Initialize-MLflow
    Start-ModelTraining
    
    Show-CompletionInfo
}

# Handle command line arguments
switch ($Action.ToLower()) {
    "venv" {
        $pythonCmd = Test-Python
        New-VirtualEnvironment -PythonCmd $pythonCmd
        break
    }
    "deps" {
        Install-Dependencies
        break
    }
    "train" {
        Initialize-MLflow
        Start-ModelTraining
        break
    }
    "test" {
        Invoke-Tests
        break
    }
    default {
        Invoke-Setup
        break
    }
}
}
