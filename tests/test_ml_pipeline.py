"""
Test suite for the California Housing ML API.
"""

import pytest
import numpy as np
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data.data_processor import DataProcessor
from api.main import HousingFeatures


class TestDataProcessor:
    """Test the data processing functionality."""
    
    def test_data_loading(self):
        """Test that data loads correctly."""
        processor = DataProcessor()
        X, y = processor.load_data()
        
        assert X is not None
        assert y is not None
        assert len(X) > 0
        assert len(y) > 0
        assert len(X) == len(y)
    
    def test_data_preprocessing(self):
        """Test data preprocessing."""
        processor = DataProcessor()
        X, y = processor.load_data()
        X_processed, y_processed = processor.preprocess_data(X, y)
        
        # Check that new features are added
        assert 'rooms_per_household' in X_processed.columns
        assert 'bedrooms_per_room' in X_processed.columns
        assert 'population_per_household' in X_processed.columns
        
        # Check no NaN or infinite values
        assert not X_processed.isnull().any().any()
        assert not np.isinf(X_processed).any().any()
    
    def test_data_splitting(self):
        """Test data splitting."""
        processor = DataProcessor(test_size=0.2, random_state=42)
        X, y = processor.load_data()
        X_processed, y_processed = processor.preprocess_data(X, y)
        X_train, X_test, y_train, y_test = processor.split_data(X_processed, y_processed)
        
        # Check split sizes
        total_size = len(X_processed)
        expected_test_size = int(total_size * 0.2)
        
        assert len(X_test) == pytest.approx(expected_test_size, abs=10)
        assert len(X_train) == total_size - len(X_test)
        assert len(y_train) == len(X_train)
        assert len(y_test) == len(X_test)


class TestHousingFeatures:
    """Test the Pydantic model for housing features."""
    
    def test_valid_features(self):
        """Test valid housing features."""
        features = HousingFeatures(
            MedInc=8.3252,
            HouseAge=41.0,
            AveRooms=6.984127,
            AveBedrms=1.023810,
            Population=322.0,
            AveOccup=2.555556,
            Latitude=37.88,
            Longitude=-122.23
        )
        
        assert features.MedInc == 8.3252
        assert features.HouseAge == 41.0
        assert features.AveRooms == 6.984127
    
    def test_invalid_features(self):
        """Test invalid housing features."""
        with pytest.raises(ValueError):
            HousingFeatures(
                MedInc=-1.0,  # Should be >= 0
                HouseAge=41.0,
                AveRooms=6.984127,
                AveBedrms=1.023810,
                Population=322.0,
                AveOccup=2.555556,
                Latitude=37.88,
                Longitude=-122.23
            )
        
        with pytest.raises(ValueError):
            HousingFeatures(
                MedInc=8.3252,
                HouseAge=41.0,
                AveRooms=6.984127,
                AveBedrms=1.023810,
                Population=322.0,
                AveOccup=0,  # Should be > 0
                Latitude=37.88,
                Longitude=-122.23
            )


class TestModelPredictions:
    """Test model predictions (requires trained models)."""
    
    def test_prediction_format(self):
        """Test that predictions are in the correct format."""
        # This test requires a trained model
        # Skip if model file doesn't exist
        model_path = "models/gradient_boosting.joblib"
        if not os.path.exists(model_path):
            pytest.skip("Model file not found")
        
        import joblib
        model = joblib.load(model_path)
        
        # Create sample input
        sample_input = np.array([[8.3252, 41.0, 6.984127, 1.023810, 322.0, 
                                 2.555556, 37.88, -122.23, 2.735, 0.146, 125.9]])
        
        prediction = model.predict(sample_input)
        
        assert len(prediction) == 1
        assert isinstance(prediction[0], (int, float))
        assert prediction[0] > 0  # Housing prices should be positive


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
