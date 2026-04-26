import requests

url = "https://cordis.europa.eu/api/v1/calls"
params = {
    "filters": {
        "keyWords": ["rural", "municipalities"]
    },
    "limit": 5
}
try:
    response = requests.get(url, json=params, timeout=10)
    print("Status:", response.status_code)
    data = response.json()
    print("Total:", data.get('meta', {}).get('total', 'Unknown'))
except Exception as e:
    print("Error:", e)
