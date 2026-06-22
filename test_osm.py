import requests
query = """
[out:json];
(
  way["building"](40.416,-3.704,40.418,-3.702);
);
out center;
"""
try:
    headers = {"User-Agent": "Aero-AI-Drone-Simulation/1.0"}
    response = requests.post("https://overpass-api.de/api/interpreter", data={'data': query}, headers=headers, timeout=10)
    print("Status 1:", response.status_code)
    print("Keys:", response.json().keys())
    print("Elements length:", len(response.json().get('elements', [])))
except Exception as e:
    print("Error:", e)
