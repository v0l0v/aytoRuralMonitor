from eu_api_monitor import EUAPIMonitor
import json

monitor = EUAPIMonitor()
results = monitor.search_opportunities("España")
new_calls = monitor.process_search_results(results, only_new=False)

print(f"Total calls relevant to municipality: {len(new_calls)}")
if new_calls:
    print(json.dumps(new_calls[0], indent=2))
