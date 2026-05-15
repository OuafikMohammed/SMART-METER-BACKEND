#!/usr/bin/env python
import requests
import json

API_URL = "http://localhost:8000/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Step 1: Login to get JWT token
print("1. Logging in...")
login_response = requests.post(
    f"{API_URL}/auth/login/",
    json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.json())
    exit(1)

token = login_response.json().get('access')
print(f"✅ Login successful. Token: {token[:20]}...")

# Step 2: Get admin dashboard
print("\n2. Fetching admin dashboard...")
headers = {"Authorization": f"Bearer {token}"}
dashboard_response = requests.get(
    f"{API_URL}/energy/admin/dashboard/",
    headers=headers
)

if dashboard_response.status_code == 403:
    print(f"❌ Permission denied (403)")
    print(dashboard_response.json())
    exit(1)

if dashboard_response.status_code != 200:
    print(f"❌ Failed: {dashboard_response.status_code}")
    print(dashboard_response.json())
    exit(1)

data = dashboard_response.json()
print(f"✅ Dashboard retrieved successfully")
print(f"\nDashboard Data:")
print(f"  Total Residents: {data['total_residents']}")
print(f"  Total Consumption (kWh): {data['total_consumption_kwh']}")
print(f"  Total Cost Estimate (DH): {data['total_cost_estimate']}")
print(f"  Average per Resident: {data['average_consumption_per_resident']}")
print(f"  Number of Residents Data: {len(data['residents'])}")
print(f"  Number of Daily Data Points: {len(data['consumption_by_day'])}")

print(f"\nFirst 3 Residents:")
for i, resident in enumerate(data['residents'][:3]):
    print(f"  {i+1}. {resident['email']} ({resident['numero_foyer']}): {resident['total_consumption_kwh']} kWh, {resident['total_cost_estimate']} DH")

print(f"\nDaily Consumption (first 5 days):")
for i, day in enumerate(data['consumption_by_day'][:5]):
    print(f"  {day['date']}: {day['total_consumption_kwh']} kWh")
