import time
import random
import requests
from datetime import datetime


API_URL = "https://water-potability-api-z2uw.onrender.com/api/predict"


def generate_sensor_data():
    """Generates synthetic water quality data matching Sibu's peat water profile."""
    # Sibu peat water is naturally acidic (pH 4.0 - 6.5)
    ph = round(random.uniform(4.0, 6.5), 2)

    # 15% chance of a pipe rupture/heavy rain simulation (high turbidity)
    if random.random() < 0.15:
        turbidity = round(random.uniform(15.0, 35.0), 2)
        print(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Generated -> pH: {ph} | Turbidity: {turbidity} NTU [PIPE RUPTURE SIMULATED]")
    else:
        # Normal Sibu turbidity (clear but stained)
        turbidity = round(random.uniform(1.0, 5.0), 2)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Generated -> pH: {ph} | Turbidity: {turbidity} NTU")

    return {"ph": ph, "turbidity": turbidity}


def run_simulation():
    print("--- Starting Advanced Environmental Data Simulator ---")
    print("Target Environment: Permai Sibu, Sarawak")
    print("Interval: 5 Seconds\n")

    while True:
        try:
            data = generate_sensor_data()
            response = requests.post(API_URL, json=data)

            if response.status_code == 200:
                result = response.json()
                print(f"   └─ AI Prediction: {result['ai_prediction']} | Logged to Cloud: {result['logged_to_db']}")
            else:
                print(f"   └─ API Error: {response.status_code} - {response.text}")

        except requests.exceptions.ConnectionError:
            print("   └─ Error: Could not connect to API. Is the Render server awake?")

        print("-" * 50)
        time.sleep(5)


if __name__ == "__main__":
    try:
        run_simulation()
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")