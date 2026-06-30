import requests
import json

def test_live_pipeline():
    url = "http://localhost:8000/process-voice"
    payload = {
        "transcript": "i was insulted because of my casst on the road by the landlord",
        "district": "Belagavi",
        "language": "en"
    }
    
    print("Sending request to /process-voice...")
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Success! Response JSON:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_live_pipeline()
