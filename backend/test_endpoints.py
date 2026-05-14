#!/usr/bin/env python
"""Quick test of all endpoints."""
import requests
import json

BASE_URL = "http://localhost:8000"

# Test credentials
admin1_email = "houdamouttalib@gmail.com"
admin1_password = "pass123"
admin2_email = "youneseljonhy@gmail.com"
admin2_password = "pass123"

def get_token(email, password, username=None):
    """Get JWT token."""
    # Use username if provided, otherwise derive from email
    if not username:
        username = email.split("@")[0]
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login/",
        json={"username": username, "password": password}
    )
    if response.status_code == 200:
        return response.json().get("access")
    print(f"Login failed for {username}: {response.status_code}")
    print(response.text)
    return None

def test_endpoint(endpoint, token, admin_name):
    """Test an endpoint."""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/api{endpoint}"
    response = requests.get(url, headers=headers)
    
    status = "✓" if response.status_code == 200 else "✗"
    count = "N/A"
    
    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(data, dict):
                if 'count' in data:
                    count = data['count']
                elif 'results' in data:
                    count = len(data['results'])
        except:
            pass
    
    print(f"  {status} {endpoint:40} [{response.status_code}] Count: {count}")
    
    return response.status_code == 200

print("=" * 80)
print("TESTING ALL ENDPOINTS")
print("=" * 80)

# Test Admin 1
print("\n[ADMIN 1] houdamouttalib@gmail.com")
token1 = get_token(admin1_email, admin1_password, "admin_houda")

if token1:
    print("  Endpoints:")
    test_endpoint("/admin/dashboard/", token1, "Admin1")
    test_endpoint("/admin/residents/", token1, "Admin1")
    test_endpoint("/admin/foyers/", token1, "Admin1")
    test_endpoint("/admin/anomalies/", token1, "Admin1")
    test_endpoint("/admin/analytics/consumption/", token1, "Admin1")
    test_endpoint("/admin/analytics/top-consumers/", token1, "Admin1")
    test_endpoint("/admin/analytics/stats/", token1, "Admin1")
else:
    print("  Failed to get token!")

# Test Admin 2
print("\n[ADMIN 2] youneseljonhy@gmail.com")
token2 = get_token(admin2_email, admin2_password, "admin_younes")

if token2:
    print("  Endpoints:")
    test_endpoint("/admin/dashboard/", token2, "Admin2")
    test_endpoint("/admin/residents/", token2, "Admin2")
    test_endpoint("/admin/foyers/", token2, "Admin2")
    test_endpoint("/admin/anomalies/", token2, "Admin2")
    test_endpoint("/admin/analytics/consumption/", token2, "Admin2")
    test_endpoint("/admin/analytics/top-consumers/", token2, "Admin2")
    test_endpoint("/admin/analytics/stats/", token2, "Admin2")
else:
    print("  Failed to get token!")

print("\n" + "=" * 80)
print("TESTING COMPLETE")
print("=" * 80)
