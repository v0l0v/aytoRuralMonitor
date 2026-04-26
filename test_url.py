from eu_api_monitor import EUAPIMonitor
import json

monitor = EUAPIMonitor()
results = monitor.search_opportunities("España")
if results:
    for call in results[:5]:
        meta = call.get("metadata", {})
        print(f"Type: {call.get('type')}")
        print(f"Title: {meta.get('title', [''])[0]}")
        print(f"Identifier: {meta.get('identifier', [''])[0] if meta.get('identifier') else 'N/A'}")
        print(f"Call Identifier: {meta.get('callIdentifier', [''])[0] if meta.get('callIdentifier') else 'N/A'}")
        print(f"cftId: {meta.get('cftId', [''])[0] if meta.get('cftId') else 'N/A'}")
        print("-" * 40)
