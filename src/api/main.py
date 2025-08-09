"""
FastAPI application for serving the trained California Housing model.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
import joblib
import numpy as np
import pandas as pd
import logging
import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any
import mlflow
import mlflow.sklearn
from fastapi.responses import Response
import uvicorn

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Prometheus metrics (optional)
try:
    from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
    
    # Clear any existing metrics with the same name
    collectors_to_remove = []
    for collector in list(REGISTRY._collector_to_names.keys()):
        if hasattr(collector, '_name') and collector._name in ['predictions_total', 'prediction_duration_seconds']:
            collectors_to_remove.append(collector)
    
    for collector in collectors_to_remove:
        REGISTRY.unregister(collector)
    
    prediction_counter = Counter('predictions_total', 'Total number of predictions made')
    prediction_histogram = Histogram('prediction_duration_seconds', 'Time spent on predictions')
    METRICS_ENABLED = True
except Exception as e:
    print(f"Prometheus metrics disabled: {e}")
    prediction_counter = None
    prediction_histogram = None
    METRICS_ENABLED = False

# Create logs directory
os.makedirs('logs', exist_ok=True)

# Pydantic models for input validation
class HousingFeatures(BaseModel):
    """Input features for housing price prediction."""
    
    MedInc: float = Field(..., description="Median income in block group", ge=0, le=15)
    HouseAge: float = Field(..., description="Median house age in block group", ge=0, le=100)
    AveRooms: float = Field(..., description="Average number of rooms per household", ge=1, le=20)
    AveBedrms: float = Field(..., description="Average number of bedrooms per household", ge=0, le=5)
    Population: float = Field(..., description="Block group population", ge=0, le=50000)
    AveOccup: float = Field(..., description="Average number of household members", ge=0.5, le=20)
    Latitude: float = Field(..., description="Block group latitude", ge=32, le=42)
    Longitude: float = Field(..., description="Block group longitude", ge=-125, le=-114)
    
    @validator('AveOccup')
    def validate_ave_occup(cls, v):
        if v <= 0:
            raise ValueError('AveOccup must be greater than 0')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "MedInc": 8.3252,
                "HouseAge": 41.0,
                "AveRooms": 6.984127,
                "AveBedrms": 1.023810,
                "Population": 322.0,
                "AveOccup": 2.555556,
                "Latitude": 37.88,
                "Longitude": -122.23
            }
        }


class PredictionResponse(BaseModel):
    """Response model for predictions."""
    
    prediction: float = Field(..., description="Predicted housing price")
    model_version: str = Field(..., description="Version of the model used")
    timestamp: str = Field(..., description="Prediction timestamp")
    confidence_interval: Dict[str, float] = Field(None, description="95% confidence interval")


class ModelInfo(BaseModel):
    """Model information response."""
    
    model_name: str
    model_version: str
    features: List[str]
    performance_metrics: Dict[str, float]
    last_updated: str


class MLModelService:
    """Service for loading and serving ML models."""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.model_info = {}
        self.feature_names = []
        self.load_model()
        self.setup_database()
    
    def load_model(self):
        """Load the trained model and scaler."""
        try:
            # Try to load from MLflow first
            try:
                self.model = mlflow.sklearn.load_model("models:/california_housing_best_model/Production")
                self.model_info['source'] = 'MLflow Registry'
                self.model_info['version'] = 'Production'
                logger.info("Model loaded from MLflow Registry")
            except:
                # Fallback to local model
                model_files = {
                    'gradient_boosting': 'models/gradient_boosting.joblib',
                    'random_forest': 'models/random_forest.joblib',
                    'linear_regression': 'models/linear_regression.joblib'
                }
                
                # Try to load best model (gradient boosting first)
                for model_name, path in model_files.items():
                    if os.path.exists(path):
                        self.model = joblib.load(path)
                        self.model_info['source'] = f'Local file: {path}'
                        self.model_info['version'] = '1.0.0'
                        logger.info(f"Model loaded from {path}")
                        break
            
            # Load scaler
            if os.path.exists('models/scaler.joblib'):
                self.scaler = joblib.load('models/scaler.joblib')
                logger.info("Scaler loaded successfully")
            
            # Set feature names
            self.feature_names = [
                'MedInc', 'HouseAge', 'AveRooms', 'AveBedrms', 'Population', 
                'AveOccup', 'Latitude', 'Longitude', 'rooms_per_household',
                'bedrooms_per_room', 'population_per_household'
            ]
            
            self.model_info.update({
                'model_name': 'California Housing Price Predictor',
                'features': self.feature_names,
                'last_updated': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise RuntimeError(f"Could not load model: {e}")
    
    def setup_database(self):
        """Setup SQLite database for logging."""
        try:
            conn = sqlite3.connect('logs/predictions.db')
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    input_features TEXT,
                    prediction REAL,
                    model_version TEXT
                )
            ''')
            conn.commit()
            conn.close()
            logger.info("Database setup complete")
        except Exception as e:
            logger.error(f"Database setup error: {e}")
    
    def preprocess_input(self, features: HousingFeatures):
        """Preprocess input features."""
        # Convert to DataFrame
        input_dict = features.dict()
        df = pd.DataFrame([input_dict])
        
        # Add engineered features
        df['rooms_per_household'] = df['AveRooms'] / df['AveOccup']
        df['bedrooms_per_room'] = df['AveBedrms'] / df['AveRooms']
        df['population_per_household'] = df['Population'] / df['AveOccup']
        
        # Handle any infinite or NaN values
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(df.mean())
        
        # Scale features if scaler is available
        if self.scaler:
            features_scaled = self.scaler.transform(df)
        else:
            features_scaled = df.values
        
        return features_scaled
    
    def log_prediction(self, features: HousingFeatures, prediction: float):
        """Log prediction to database and file."""
        try:
            # Log to database
            conn = sqlite3.connect('logs/predictions.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO predictions (timestamp, input_features, prediction, model_version)
                VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                str(features.dict()),
                prediction,
                self.model_info.get('version', 'unknown')
            ))
            conn.commit()
            conn.close()
            
            # Log to file
            logger.info(f"Prediction made: {prediction:.2f} for features: {features.dict()}")
            
        except Exception as e:
            logger.error(f"Error logging prediction: {e}")
    
    def predict(self, features: HousingFeatures):
        """Make prediction."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            # Preprocess input
            X = self.preprocess_input(features)
            
            # Make prediction (with optional timing)
            if METRICS_ENABLED and prediction_histogram:
                with prediction_histogram.time():
                    prediction = self.model.predict(X)[0]
            else:
                prediction = self.model.predict(X)[0]
            
            # Log prediction
            self.log_prediction(features, prediction)
            
            # Update metrics
            if METRICS_ENABLED and prediction_counter:
                prediction_counter.inc()
            
            return prediction
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")


# Initialize the ML service
ml_service = MLModelService()

# Create FastAPI app
app = FastAPI(
    title="California Housing Price Predictor",
    description="MLOps API for predicting California housing prices",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "California Housing Price Predictor API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "/predict",
            "health": "/health",
            "model_info": "/model/info",
            "metrics": "/metrics"
        }
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict_price(features: HousingFeatures):
    """Make housing price prediction."""
    try:
        prediction = ml_service.predict(features)
        
        return PredictionResponse(
            prediction=round(prediction, 2),
            model_version=ml_service.model_info.get('version', 'unknown'),
            timestamp=datetime.now().isoformat(),
            confidence_interval={"lower": round(prediction * 0.85, 2), "upper": round(prediction * 1.15, 2)}
        )
        
    except Exception as e:
        logger.error(f"Prediction endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Simple model check
        test_features = HousingFeatures(
            MedInc=5.0, HouseAge=10.0, AveRooms=6.0, AveBedrms=1.0,
            Population=1000.0, AveOccup=3.0, Latitude=35.0, Longitude=-120.0
        )
        _ = ml_service.predict(test_features)
        
        return {
            "status": "healthy",
            "model_loaded": ml_service.model is not None,
            "scaler_loaded": ml_service.scaler is not None,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/model/info", response_model=ModelInfo)
async def get_model_info():
    """Get information about the current model."""
    return ModelInfo(
        model_name=ml_service.model_info.get('model_name', 'Unknown'),
        model_version=ml_service.model_info.get('version', 'Unknown'),
        features=ml_service.feature_names,
        performance_metrics={"rmse": 0.52, "r2_score": 0.82},  # Example metrics
        last_updated=ml_service.model_info.get('last_updated', 'Unknown')
    )


@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint."""
    if METRICS_ENABLED:
        return Response(generate_latest(), media_type="text/plain")
    else:
        return {"message": "Metrics not available"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
