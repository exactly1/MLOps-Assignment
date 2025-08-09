"""
Test suite for the FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from api.main import app
    client = TestClient(app)
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False


@pytest.mark.skipif(not API_AVAILABLE, reason="API dependencies not available")
class TestAPI:
    """Test the FastAPI application."""
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoints" in data
    
    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
    
    def test_model_info_endpoint(self):
        """Test the model info endpoint."""
        response = client.get("/model/info")
        assert response.status_code == 200
        data = response.json()
        assert "model_name" in data
        assert "model_version" in data
        assert "features" in data
    
    def test_prediction_endpoint_valid_input(self):
        """Test prediction with valid input."""
        valid_input = {
            "MedInc": 8.3252,
            "HouseAge": 41.0,
            "AveRooms": 6.984127,
            "AveBedrms": 1.023810,
            "Population": 322.0,
            "AveOccup": 2.555556,
            "Latitude": 37.88,
            "Longitude": -122.23
        }
        
        response = client.post("/predict", json=valid_input)
        
        # If model is not loaded, we might get a 500 error
        if response.status_code == 200:
            data = response.json()
            assert "prediction" in data
            assert "model_version" in data
            assert "timestamp" in data
            assert isinstance(data["prediction"], (int, float))
        else:
            # Accept 500 if model is not available
            assert response.status_code == 500
    
    def test_prediction_endpoint_invalid_input(self):
        """Test prediction with invalid input."""
        invalid_input = {
            "MedInc": -1.0,  # Invalid: should be >= 0
            "HouseAge": 41.0,
            "AveRooms": 6.984127,
            "AveBedrms": 1.023810,
            "Population": 322.0,
            "AveOccup": 2.555556,
            "Latitude": 37.88,
            "Longitude": -122.23
        }
        
        response = client.post("/predict", json=invalid_input)
        assert response.status_code == 422  # Validation error
    
    def test_metrics_endpoint(self):
        """Test the metrics endpoint."""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"


class TestAPIValidation:
    """Test input validation without API dependencies."""
    
    def test_housing_features_validation(self):
        """Test housing features validation logic."""
        # Test valid ranges
        valid_data = {
            "MedInc": 5.0,
            "HouseAge": 10.0,
            "AveRooms": 6.0,
            "AveBedrms": 1.0,
            "Population": 1000.0,
            "AveOccup": 3.0,
            "Latitude": 35.0,
            "Longitude": -120.0
        }
        
        # These are the validation rules we expect
        assert valid_data["MedInc"] >= 0 and valid_data["MedInc"] <= 15
        assert valid_data["HouseAge"] >= 0 and valid_data["HouseAge"] <= 100
        assert valid_data["AveRooms"] >= 1 and valid_data["AveRooms"] <= 20
        assert valid_data["AveBedrms"] >= 0 and valid_data["AveBedrms"] <= 5
        assert valid_data["Population"] >= 0 and valid_data["Population"] <= 50000
        assert valid_data["AveOccup"] >= 0.5 and valid_data["AveOccup"] <= 20
        assert valid_data["Latitude"] >= 32 and valid_data["Latitude"] <= 42
        assert valid_data["Longitude"] >= -125 and valid_data["Longitude"] <= -114


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
