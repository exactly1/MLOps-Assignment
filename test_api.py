"""
Test script for the ML API
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_model_info():
    """Test model info endpoint"""
    response = requests.get(f"{BASE_URL}/model/info")
    print(f"Model info: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_prediction():
    """Test prediction endpoint"""
    # Sample California housing data
    sample_data = {
        "MedInc": 8.3252,
        "HouseAge": 41.0,
        "AveRooms": 6.984127,
        "AveBedrms": 1.023810,
        "Population": 322.0,
        "AveOccup": 2.555556,
        "Latitude": 37.88,
        "Longitude": -122.23
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=sample_data)
    print(f"Prediction: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2))
        print(f"Predicted price: ${result['prediction']} (hundreds of thousands)")
    else:
        print(f"Error: {response.text}")
    print()

def test_metrics():
    """Test metrics endpoint"""
    response = requests.get(f"{BASE_URL}/metrics")
    print(f"Metrics: {response.status_code}")
    if response.status_code == 200:
        print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
    print()

def test_invalid_prediction():
    """Test prediction with invalid data"""
    invalid_data = {
        "MedInc": -1.0,  # Invalid negative income
        "HouseAge": 41.0,
        "AveRooms": 6.984127,
        "AveBedrms": 1.023810,
        "Population": 322.0,
        "AveOccup": 2.555556,
        "Latitude": 37.88,
        "Longitude": -122.23
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=invalid_data)
    print(f"Invalid prediction: {response.status_code}")
    print(f"Response: {response.text}")
    print()

if __name__ == "__main__":
    print("🧪 Testing ML API...")
    print("=" * 50)
    
    try:
        test_health()
        test_model_info()
        test_prediction()
        test_metrics()
        test_invalid_prediction()
        
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure it's running at http://localhost:8000")
    except Exception as e:
        print(f"❌ Test error: {e}")
