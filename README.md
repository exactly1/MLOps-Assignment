
# MLOps Pipeline - California Housing Price Prediction

This repository contains a complete MLOps pipeline for predicting California housing prices, featuring modular code, experiment tracking, containerized API and UI, CI/CD, and robust monitoring.


## 🏗️ Architecture Overview

**Key Components:**
- **Data Processing**: Preprocessing and feature engineering (`src/data/data_processor.py`)
- **Model Training & Evaluation**: Multiple models, tracked with MLflow (`src/models/train.py`, `src/models/evaluate.py`)
- **API Service**: FastAPI for serving predictions (`src/api/main.py`)
- **Monitoring**: Logging, metrics, Prometheus integration (`src/monitoring/monitor.py`)
- **UI**: Streamlit dashboard for visualization (`src/ui/streamlit_app.py`)
- **Containerization**: Docker & Docker Compose for deployment
- **CI/CD**: GitHub Actions (if configured)


## 📁 Project Structure

```
├── data/                  # Raw and processed datasets
├── exports/               # Exported artifacts
├── logs/                  # API and monitoring logs, predictions DB
├── models/                # Trained model artifacts (joblib, scaler)
├── mlruns/                # MLflow experiment tracking
├── src/
│   ├── api/               # FastAPI app
│   ├── data/              # Data processing scripts
│   ├── models/            # Training & evaluation
│   ├── monitoring/        # Monitoring utilities
│   └── ui/                # Streamlit dashboard
├── tests/                 # Unit tests
├── Dockerfile.api         # API Dockerfile
├── Dockerfile.ui          # UI Dockerfile
├── docker-compose.yml     # Multi-service orchestration
├── requirements.txt       # Python dependencies
├── run_api.py             # API runner script
├── show_monitoring.py     # Monitoring dashboard runner
└── ... (other configs)
```


## 🚀 Quick Start

1. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Train models**
   ```powershell
   python src/models/train.py
   ```

3. **Run API service**
   ```powershell
   python run_api.py
   ```

4. **Run Streamlit UI**
   ```powershell
   python src/ui/streamlit_app.py
   ```

5. **Monitoring Dashboard**
   ```powershell
   python show_monitoring.py
   ```

6. **Docker Deployment**
   ```powershell
   docker-compose up --build
   ```


## 📊 Model Performance

| Model | RMSE | R² Score | Training Time |
|-------|------|----------|---------------|
| Linear Regression | 0.743 | 0.667 | 0.12s |
| Random Forest | 0.526 | 0.795 | 2.45s |
| Gradient Boosting | 0.498 | 0.821 | 5.32s |


## 🔍 API Endpoints

- `POST /predict` — Predict housing prices
- `GET /health` — Health check
- `GET /metrics` — Prometheus metrics (if enabled)
- `GET /model/info` — Current model info


## 📈 Monitoring & Logging

- Request/response logging to `logs/`
- Prediction and model monitoring in `logs/predictions.db` and `logs/model_monitor.log`
- Prometheus metrics endpoint for integration
- Monitoring dashboard via `show_monitoring.py`


## 🧪 Testing

```powershell
pytest tests/
```


## 📝 License

MIT License
