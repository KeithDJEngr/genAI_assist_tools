#!/bin/python3

import requests

# URL of your SearXNG instance
base_url = "http://localhost:8080"

# Search parameters
params = {
    "q": "python tutorials",
    "format": "json",        # Required for JSON output
    "engines": "google,bing", # Optional: specify engines
    "pageno": 1              # Optional: pagination
}

response = requests.get(f"{base_url}/search", params=params)
print(f"for params: \n{params}\nresults: {response}")

if response.status_code == 200:
    results = response.json()
    for result in results.get("results", []):
        print(f"Title: {result['title']}\nURL: {result['url']}\n")
else:
    print(f"Error: {response.status_code}")

