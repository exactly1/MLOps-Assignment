"""
Model training and experiment tracking with MLflow.
"""

import mlflow
import mlflow.sklearn
import os
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import numpy as np
import pandas as pd
import joblib
import os
import sys
import logging
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data.data_processor import DataProcessor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """Handle model training and experiment tracking."""
    
    def __init__(self, experiment_name="california_housing_prediction"):
        self.experiment_name = experiment_name
        self.setup_mlflow()
        
    def setup_mlflow(self):
        """Setup MLflow experiment and tracking URI."""
        tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", None)
        if tracking_uri is None:
            import yaml
            with open("params.yaml", "r") as f:
                params = yaml.safe_load(f)
            tracking_uri = params.get("training", {}).get("mlflow_tracking_uri", "postgresql://mlflow:mlflow@postgres:5432/mlflow")

        # Dynamically switch host for local vs Docker
        # Use 'postgres' in Docker, 'localhost' locally
        if "postgresql://mlflow:mlflow@postgres:5432/mlflow" in tracking_uri:
            # If running locally (not in Docker), switch to localhost
            if not os.path.exists("/.dockerenv"):
                tracking_uri = tracking_uri.replace("@postgres:", "@localhost:")

        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(self.experiment_name)
        logger.info(f"MLflow tracking URI set to: {tracking_uri}")
        logger.info(f"MLflow experiment set to: {self.experiment_name}")
    
    def get_models(self):
        """Get dictionary of models to train."""
        return {
            'linear_regression': LinearRegression(),
            'random_forest': RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            ),
            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
        }
    
    def calculate_metrics(self, y_true, y_pred):
        """Calculate regression metrics."""
        return {
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2_score': r2_score(y_true, y_pred)
        }
    
    def train_model(self, model, model_name, X_train, y_train, X_test, y_test, feature_names):
        """Train a single model and log to MLflow."""
        
        with mlflow.start_run(run_name=f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            # Log parameters
            if hasattr(model, 'get_params'):
                mlflow.log_params(model.get_params())
            
            # Train model
            logger.info(f"Training {model_name}...")
            start_time = datetime.now()
            model.fit(X_train, y_train)
            training_time = (datetime.now() - start_time).total_seconds()
            
            # Make predictions
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            
            # Calculate metrics
            train_metrics = self.calculate_metrics(y_train, y_train_pred)
            test_metrics = self.calculate_metrics(y_test, y_test_pred)
            
            # Log metrics
            mlflow.log_metric("train_rmse", train_metrics['rmse'])
            mlflow.log_metric("train_mae", train_metrics['mae'])
            mlflow.log_metric("train_r2", train_metrics['r2_score'])
            mlflow.log_metric("test_rmse", test_metrics['rmse'])
            mlflow.log_metric("test_mae", test_metrics['mae'])
            mlflow.log_metric("test_r2", test_metrics['r2_score'])
            mlflow.log_metric("training_time_seconds", training_time)
            
            # Log model
            mlflow.sklearn.log_model(
                model, 
                model_name,
                input_example=X_train[:5],
                signature=mlflow.models.infer_signature(X_train, y_train_pred)
            )
            
            # Save model locally
            model_path = f"models/{model_name}.joblib"
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            joblib.dump(model, model_path)
            
            logger.info(f"{model_name} - Test RMSE: {test_metrics['rmse']:.3f}, R²: {test_metrics['r2_score']:.3f}")
            
            return {
                'model': model,
                'model_name': model_name,
                'test_metrics': test_metrics,
                'train_metrics': train_metrics,
                'training_time': training_time,
                'run_id': mlflow.active_run().info.run_id
            }
    
    def train_all_models(self):
        """Train all models and compare performance."""
        logger.info("Starting model training pipeline...")
        
        # Prepare data
        processor = DataProcessor()
        data = processor.prepare_data(save_scaler_path='models/scaler.joblib')
        
        # Get models
        models = self.get_models()
        results = []
        
        # Train each model
        for model_name, model in models.items():
            result = self.train_model(
                model, model_name,
                data['X_train'], data['y_train'],
                data['X_test'], data['y_test'],
                data['feature_names']
            )
            results.append(result)
        
        # Find best model
        best_model = min(results, key=lambda x: x['test_metrics']['rmse'])
        logger.info(f"Best model: {best_model['model_name']} with RMSE: {best_model['test_metrics']['rmse']:.3f}")
        
        # Register best model
        self.register_best_model(best_model)
        
        return results, best_model
    
    def register_best_model(self, best_model):
        """Register the best model in MLflow Model Registry."""
        try:
            model_name = "california_housing_best_model"
            
            # Create registered model if it doesn't exist
            try:
                mlflow.tracking.MlflowClient().create_registered_model(model_name)
            except Exception:
                pass  # Model already exists
            
            # Register this version
            model_uri = f"runs:/{best_model['run_id']}/{best_model['model_name']}"
            model_version = mlflow.register_model(
                model_uri=model_uri,
                name=model_name
            )
            
            # Transition to production
            mlflow.tracking.MlflowClient().transition_model_version_stage(
                name=model_name,
                version=model_version.version,
                stage="Production"
            )
            
            logger.info(f"Model {best_model['model_name']} registered as {model_name} v{model_version.version}")
            
        except Exception as e:
            logger.warning(f"Could not register model: {e}")


def main():
    """Main training script."""
    trainer = ModelTrainer()
    results, best_model = trainer.train_all_models()
    
    # Print summary
    print("\n" + "="*60)
    print("TRAINING SUMMARY")
    print("="*60)
    
    for result in results:
        print(f"\n{result['model_name'].upper()}:")
        print(f"  Test RMSE: {result['test_metrics']['rmse']:.4f}")
        print(f"  Test R²:   {result['test_metrics']['r2_score']:.4f}")
        print(f"  Training Time: {result['training_time']:.2f}s")
    
    print(f"\nBEST MODEL: {best_model['model_name']}")
    print("="*60)


if __name__ == "__main__":
    main()
