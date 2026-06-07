import os
import requests
import joblib
import pandas as pd
import warnings
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

warnings.filterwarnings("ignore")

# --- SUPABASE REST API CONFIGURATION ---
# The code will now pull the keys securely from Render and Streamlit Cloud
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

app = FastAPI(title="Sibu AquaML API")


# --- MACHINE LEARNING API ---
class SimulatedData(BaseModel):
    ph: float
    turbidity: float


print("Loading Machine Learning Model...")
try:
    rf_model = joblib.load("random_forest_sibu.pkl")
    print("Success: random_forest_sibu.pkl loaded.")
except Exception as e:
    print(f"Error: Model not found. Did you run train_model.py? {e}")


@app.post("/api/predict")
async def predict_water_quality(data: SimulatedData):
    try:
        # 1. Prepare data for the ML Model
        ml_input = pd.DataFrame([{
            'ph': data.ph, 'Hardness': 196.0, 'Solids': 22000.0, 'Chloramines': 7.1,
            'Sulfate': 333.0, 'Conductivity': 426.0, 'Organic_carbon': 14.0,
            'Trihalomethanes': 66.0, 'Turbidity': data.turbidity
        }])

        # 2. Make the AI Prediction
        prediction_val = rf_model.predict(ml_input)[0]
        status = "Safe" if prediction_val == 1 else "Unsafe"

        # 3. Push to Supabase
        db_url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/water_readings"
        payload = {
            "ph_level": round(data.ph, 2),
            "turbidity_ntu": round(data.turbidity, 2),
            "ai_prediction": status
        }

        db_response = requests.post(db_url, json=payload, headers=HEADERS)

        if db_response.status_code not in [200, 201]:
            raise Exception(f"Supabase Direct API Error: {db_response.text}")

        return {"message": "Success", "ai_prediction": status, "logged_to_db": True}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))