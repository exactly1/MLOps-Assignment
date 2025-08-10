import streamlit as st
import requests

st.set_page_config(page_title="California Housing Price Predictor", page_icon="🏠", layout="centered")
st.title("🏠 California Housing Price Predictor")
st.write("Enter the housing features below to predict the price.")

# Input fields for the API
medinc = st.number_input("Median Income (MedInc)", min_value=0.0, max_value=15.0, value=5.0)
houseage = st.number_input("Median House Age (HouseAge)", min_value=0.0, max_value=100.0, value=20.0)
averooms = st.number_input("Average Rooms (AveRooms)", min_value=1.0, max_value=20.0, value=6.0)
avebedrms = st.number_input("Average Bedrooms (AveBedrms)", min_value=0.0, max_value=5.0, value=1.0)
population = st.number_input("Population", min_value=0.0, max_value=500000.0, value=1000.0)
aveoccup = st.number_input("Average Occupancy (AveOccup)", min_value=0.5, max_value=20.0, value=3.0)
latitude = st.number_input("Latitude", min_value=32.0, max_value=42.0, value=36.0)
longitude = st.number_input("Longitude", min_value=-125.0, max_value=-114.0, value=-120.0)


api_url = "http://ml-api:8000/predict"

# Add API health check button
if st.button("Test API Connection"):
    try:
        response = requests.get("http://ml-api:8000/health")
        st.write("API Health:", response.status_code, response.text)
    except Exception as e:
        st.error(f"API connection failed: {e}")

if st.button("Predict Price"):
    features = {
        "MedInc": medinc,
        "HouseAge": houseage,
        "AveRooms": averooms,
        "AveBedrms": avebedrms,
        "Population": population,
        "AveOccup": aveoccup,
        "Latitude": latitude,
        "Longitude": longitude
    }
    try:
        response = requests.post(api_url, json=features)
        if response.status_code == 200:
            result = response.json()
            st.success(f"Predicted Price: ${result['prediction']}")
            st.write(f"Model Version: {result['model_version']}")
            st.write(f"Timestamp: {result['timestamp']}")
            ci = result.get('confidence_interval', None)
            if ci:
                st.write(f"95% Confidence Interval: ${ci['lower']} - ${ci['upper']}")
        else:
            st.error(f"API Error: {response.text}")
    except Exception as e:
        st.error(f"Connection Error: {e}")

st.markdown("---")
st.write("API must be running at [http://localhost:8000](http://localhost:8000)")
st.write("Powered by Streamlit & FastAPI")
