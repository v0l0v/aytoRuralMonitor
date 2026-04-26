import requests
import json

api_url = "https://api.tech.ec.europa.eu/search-api/prod/rest/search"
params = {"apiKey": "SEDIA", "text": "España", "pageSize": "5", "pageNumber": "1"}

query = {"bool": {"must": [{"terms": {"type": ["0","1","2"]}}]}}
languages = ["es", "en"]
sort = {"field": "sortStatus", "order": "ASC"}

try:
    response = requests.post(
        api_url,
        params=params,
        files={
            "query": (None, json.dumps(query), "application/json"),
            "languages": (None, json.dumps(languages), "application/json"),
            "sort": (None, json.dumps(sort), "application/json"),
        },
        timeout=10
    )
    
    print("Status Code:", response.status_code)
    data = response.json()
    print("Total results:", data.get('totalResults', 'N/A'))
    
    results = data.get('results', [])
    for res in results[:1]:
        print("\n--- Raw Result Schema ---")
        print(json.dumps(res, indent=2))
        
except Exception as e:
    print(f"Error: {e}")
