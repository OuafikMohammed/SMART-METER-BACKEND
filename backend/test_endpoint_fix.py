#!/usr/bin/env python
import requests
import json

API_URL = "http://localhost:8000/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "test123"

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

print("✅ Login successful!")
data = login_response.json()
access_token = data['access']
print(f"   Token: {access_token[:50]}...")

# Step 2: Test the residents endpoint
print("\n2. Testing /api/admin/residents/...")
headers = {"Authorization": f"Bearer {access_token}"}
residents_response = requests.get(f"{API_URL}/admin/residents/", headers=headers)

print(f"   Status: {residents_response.status_code}")
if residents_response.status_code == 200:
    print("✅ Residents endpoint works!")
    result = residents_response.json()
    print(f"   Response: {json.dumps(result, indent=2, default=str)}")
else:
    print(f"❌ Error: {residents_response.status_code}")
    print(residents_response.json())
