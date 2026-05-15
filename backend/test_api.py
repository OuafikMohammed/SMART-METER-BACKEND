#!/usr/bin/env python
"""Test the SmartMeter API endpoints to verify data flow."""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

print("\n" + "=" * 70)
print("SMARTMETER API ENDPOINTS TEST")
print("=" * 70)

# Step 1: Get auth token
print("\n[TEST 1] Authenticating...")
print("-" * 70)

auth_data = {
    "username": "admin_smartmeter",
    "password": "admin123"
}

response = requests.post(f"{API_URL}/auth/login/", json=auth_data)

if response.status_code != 200:
    print(f"✗ Auth failed: {response.status_code}")
    print(f"  Response: {response.text}")
    exit(1)

data = response.json()
token = data.get('access')
print(f"✓ Authentication successful")
print(f"  Token: {token[:30]}...")

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Step 2: Get Foyers
print("\n[TEST 2] Get Foyers...")
print("-" * 70)

response = requests.get(f"{API_URL}/energy/foyers/", headers=headers)
foyers = response.json()
if isinstance(foyers, dict):
    foyer_list = foyers.get('results', foyers)
else:
    foyer_list = foyers

print(f"✓ Retrieved {len(foyer_list)} foyers")
for foyer in foyer_list[:2]:
    print(f"  - {foyer.get('numero_foyer', 'N/A')}: {foyer.get('adresse', 'N/A')}")

# Step 3: Get Consumption Data
print("\n[TEST 3] Get Consumption Data...")
print("-" * 70)

response = requests.get(f"{API_URL}/energy/consommations/", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code != 200:
    print(f"✗ Failed: {response.text}")
else:
    try:
        consumptions = response.json()
        if isinstance(consumptions, dict):
            cons_list = consumptions.get('results', consumptions)
        else:
            cons_list = consumptions

        print(f"✓ Retrieved {len(cons_list)} consumption records")
        if cons_list:
            print(f"  Latest: {cons_list[0].get('timestamp', 'N/A')} - {cons_list[0].get('kwh', 'N/A')} kWh")
    except Exception as e:
        print(f"✗ Error parsing response: {e}")
        print(f"Response text: {response.text[:200]}")

# Step 4: Get Anomalies
print("\n[TEST 4] Get Anomalies...")
print("-" * 70)

response = requests.get(f"{API_URL}/energy/anomalies/", headers=headers)
anomalies = response.json()
if isinstance(anomalies, dict):
    anom_list = anomalies.get('results', anomalies)
else:
    anom_list = anomalies

print(f"✓ Retrieved {len(anom_list)} anomalies")
by_status = {}
for anom in anom_list:
    status = anom.get('statut', 'UNKNOWN')
    by_status[status] = by_status.get(status, 0) + 1

for status, count in by_status.items():
    print(f"  - {status}: {count}")

# Step 5: Get Alerts
print("\n[TEST 5] Get Alerts...")
print("-" * 70)

response = requests.get(f"{API_URL}/energy/alertes/", headers=headers)
if response.status_code == 200:
    alerts = response.json()
    if isinstance(alerts, dict):
        alert_list = alerts.get('results', alerts)
    else:
        alert_list = alerts
    
    print(f"✓ Retrieved {len(alert_list)} alerts")
    by_status = {}
    for alert in alert_list:
        status = alert.get('statut', 'UNKNOWN')
        by_status[status] = by_status.get(status, 0) + 1
    
    for status, count in by_status.items():
        print(f"  - {status}: {count}")
else:
    print(f"✗ Failed to retrieve alerts: {response.status_code}")

# Step 6: Test Consumption Stats
print("\n[TEST 6] Consumption Statistics...")
print("-" * 70)

response = requests.get(f"{API_URL}/energy/consommations/consumption-stats/", headers=headers)
if response.status_code == 200:
    stats = response.json()
    print(f"✓ Consumption stats retrieved")
    print(f"  - Total: {stats.get('total', 0)} kWh")
    print(f"  - Average: {stats.get('avg', 0)} kWh")
    print(f"  - Peak hour: {stats.get('peak', '00:00')}")
else:
    print(f"✗ Stats endpoint failed: {response.status_code}")

print("\n" + "=" * 70)
print("✓ API TESTS COMPLETE")
print("=" * 70 + "\n")
