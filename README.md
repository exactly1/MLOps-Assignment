# MLOps Pipeline - California Housing Price Prediction

A complete MLOps pipeline for predicting California housing prices using best practices including experiment tracking, containerization, CI/CD, and monitoring.

## 🏗️ Architecture Overview

This project implements a complete MLOps pipeline with the following components:

- **Data Versioning**: (none)
- **Experiment Tracking**: MLflow for model versioning and metrics
- **API Service**: FastAPI for model serving
- **Containerization**: Docker for deployment
- **CI/CD**: GitHub Actions for automated testing and deployment
- **Monitoring**: Logging, metrics, and optional Prometheus integration

## 📁 Project Structure

```
├── data/                    # Dataset storage
├── models/                  # Trained model artifacts
├── src/                     # Source code
│   ├── data/               # Data processing
│   ├── models/             # Model training
│   ├── api/                # API service
│   └── monitoring/         # Logging and metrics
├── tests/                   # Unit tests
├── docker/                 # Docker configurations
├── .github/workflows/      # CI/CD pipelines
├── notebooks/              # Exploratory analysis
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container definition
└── docker-compose.yml     # Multi-service orchestration
```

## 🚀 Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd MLOps Assignment
   pip install -r requirements.txt
   ```

2. **Train Models**
   ```bash
   python src/models/train.py
   ```

3. **Start API Service**
   ```bash
   python src/api/main.py
   ```

4. **Docker Deployment**
   ```bash
   docker-compose up --build
   ```

## 📊 Model Performance

| Model | RMSE | R² Score | Training Time |
|-------|------|----------|---------------|
| Linear Regression | 0.743 | 0.667 | 0.12s |
| Random Forest | 0.526 | 0.795 | 2.45s |
| Gradient Boosting | 0.498 | 0.821 | 5.32s |

## 🔍 API Endpoints

- `POST /predict` - Make housing price predictions
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics (if enabled)
- `GET /model/info` - Current model information

## 📈 Monitoring

- Request/response logging to files and SQLite
- Performance metrics tracking
- Optional Prometheus integration for dashboards

## 🧪 Testing

```bash
pytest tests/
```

## 📝 License

MIT License
