import requests
import json

url = "https://data.europa.eu/api/hub/search/search"
params = {"query": "España ayudas", "limit": 2}

try:
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    results = data.get("result", {}).get("results", [])
    
    print(f"Total results found: {data.get('result', {}).get('count', 0)}")
    
    for i, res in enumerate(results):
        print(f"\n--- Result {i+1} ---")
        title = res.get("title", {})
        desc = res.get("description", {})
        
        print("Title:", title.get("en", list(title.values())[0] if title else "N/A") if isinstance(title, dict) else title)
        print("Description:", str(desc.get("en", list(desc.values())[0] if desc else "N/A") if isinstance(desc, dict) else desc)[:200] + "...")
        print("Type:", res.get("@type", "N/A"))
        # Print a few other keys to see what we actually get
        print("Keys available:", list(res.keys()))

except Exception as e:
    print(f"Error: {e}")
