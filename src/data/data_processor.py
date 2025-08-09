"""
Data processing and loading utilities for California Housing dataset.
"""

import pandas as pd
import numpy as np
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """Handle data loading, preprocessing, and splitting."""
    
    def __init__(self, test_size=0.2, random_state=42):
        self.test_size = test_size
        self.random_state = random_state
        self.scaler = StandardScaler()
        
    def load_data(self):
        """Load California Housing dataset."""
        logger.info("Loading California Housing dataset...")
        
        # Load data
        housing = fetch_california_housing()
        X = pd.DataFrame(housing.data, columns=housing.feature_names)
        y = pd.Series(housing.target, name='price')
        
        logger.info(f"Dataset loaded: {X.shape[0]} samples, {X.shape[1]} features")
        return X, y
    
    def preprocess_data(self, X, y):
        """Preprocess the data (scaling, feature engineering)."""
        logger.info("Preprocessing data...")
        
        # Create new features
        X_processed = X.copy()
        X_processed['rooms_per_household'] = X['AveRooms'] / X['AveOccup']
        X_processed['bedrooms_per_room'] = X['AveBedrms'] / X['AveRooms']
        X_processed['population_per_household'] = X['Population'] / X['AveOccup']
        
        # Handle any infinite or NaN values
        X_processed = X_processed.replace([np.inf, -np.inf], np.nan)
        X_processed = X_processed.fillna(X_processed.mean())
        
        return X_processed, y
    
    def split_data(self, X, y):
        """Split data into train/test sets."""
        logger.info("Splitting data into train/test sets...")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state
        )
        
        logger.info(f"Train set: {X_train.shape[0]} samples")
        logger.info(f"Test set: {X_test.shape[0]} samples")
        
        return X_train, X_test, y_train, y_test
    
    def scale_features(self, X_train, X_test, fit_scaler=True):
        """Scale features using StandardScaler."""
        logger.info("Scaling features...")
        
        if fit_scaler:
            X_train_scaled = self.scaler.fit_transform(X_train)
        else:
            X_train_scaled = self.scaler.transform(X_train)
            
        X_test_scaled = self.scaler.transform(X_test)
        
        return X_train_scaled, X_test_scaled
    
    def save_scaler(self, filepath):
        """Save the fitted scaler."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self.scaler, filepath)
        logger.info(f"Scaler saved to {filepath}")
    
    def load_scaler(self, filepath):
        """Load a fitted scaler."""
        self.scaler = joblib.load(filepath)
        logger.info(f"Scaler loaded from {filepath}")
    
    def prepare_data(self, save_scaler_path=None):
        """Complete data preparation pipeline."""
        # Load data
        X, y = self.load_data()
        
        # Preprocess
        X_processed, y_processed = self.preprocess_data(X, y)
        
        # Split
        X_train, X_test, y_train, y_test = self.split_data(X_processed, y_processed)
        
        # Scale
        X_train_scaled, X_test_scaled = self.scale_features(X_train, X_test, fit_scaler=True)
        
        # Save scaler if path provided
        if save_scaler_path:
            self.save_scaler(save_scaler_path)
        
        return {
            'X_train': X_train_scaled,
            'X_test': X_test_scaled,
            'y_train': y_train,
            'y_test': y_test,
            'feature_names': X_processed.columns.tolist()
        }


if __name__ == "__main__":
    # Example usage
    processor = DataProcessor()
    data = processor.prepare_data(save_scaler_path='models/scaler.joblib')
    
    print(f"Training data shape: {data['X_train'].shape}")
    print(f"Test data shape: {data['X_test'].shape}")
    print(f"Features: {data['feature_names']}")
