#!/usr/bin/env python
"""Test API endpoints"""
import requests
import json

# Test with JWT token
print("=" * 60)
print("TESTING API ENDPOINTS")
print("=" * 60)

# Get token
print("\n1. Getting authentication token...")
token_resp = requests.post('http://localhost:8000/api/auth/login/', json={'username': 'admin', 'password': 'admin123'})
if token_resp.status_code != 200:
    print(f"   ✗ Failed: {token_resp.status_code}")
    exit(1)

token = token_resp.json()['access']
print(f"   ✓ Got token: {token[:20]}...")

headers = {'Authorization': f'Bearer {token}'}

# Test endpoints
endpoints = [
    ('/api/energy/consommations/', 'Consommations'),
    ('/api/energy/anomalies/', 'Anomalies'),
    ('/api/energy/alertes/', 'Alertes'),
    ('/api/energy/foyers/', 'Foyers'),
]

for endpoint, name in endpoints:
    print(f"\n2. GET {endpoint}")
    resp = requests.get(f'http://localhost:8000{endpoint}', headers=headers)
    print(f"   Status: {resp.status_code}")
    
    data = resp.json()
    if isinstance(data, dict):
        if 'results' in data:
            print(f"   Count: {len(data['results'])}")
        else:
            print(f"   Keys: {list(data.keys())[:3]}")
    elif isinstance(data, list):
        print(f"   Count: {len(data)}")

print("\n" + "=" * 60)
