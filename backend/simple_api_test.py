#!/usr/bin/env python
"""Test SmartMeter API endpoints - simplified version."""
import requests
import json

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

print("\n" + "=" * 70)
print("SMARTMETER API QUICK TEST")
print("=" * 70)

# Authenticate
auth_response = requests.post(f"{API_URL}/auth/login/", json={
    "username": "admin_smartmeter",
    "password": "admin123"
})

if auth_response.status_code != 200:
    print(f"✗ Authentication failed: {auth_response.status_code}")
    print(f"  {auth_response.text}")
    exit(1)

token = auth_response.json().get('access')
headers = {'Authorization': f'Bearer {token}'}
print(f"✓ Authenticated successfully")

# Test endpoints
endpoints = [
    ('Foyers', '/energy/foyers/'),
    ('Consommations', '/energy/consommations/'),
    ('Anomalies', '/energy/anomalies/'),
    ('Alertes', '/energy/alertes/'),
]

for name, endpoint in endpoints:
    response = requests.get(f"{API_URL}{endpoint}", headers=headers)
    print(f"\n{name}:")
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            # Handle both paginated and non-paginated responses
            if isinstance(data, dict) and 'results' in data:
                count = len(data['results'])
                print(f"  ✓ Count: {count}")
            elif isinstance(data, list):
                print(f"  ✓ Count: {len(data)}")
            else:
                print(f"  ✓ OK: {type(data).__name__}")
        except Exception as e:
            print(f"  ✗ Parse error: {e}")
    else:
        print(f"  ✗ Error: {response.text[:100]}")

print("\n" + "=" * 70)
print("✓ API TEST COMPLETE")
print("=" * 70 + "\n")
