#!/usr/bin/env python
"""
SmartMeter API Endpoint Testing Script
Tests all CRUD operations for both Admin and Resident users
"""

import requests
import json
from datetime import datetime, timedelta
import sys

# Configuration
API_URL = "http://localhost:8000/api"
TEST_RESULTS = []

# Global variables for tokens
admin_token = None
resident_token = None
admin2_token = None
resident2_token = None
admin_id = None
resident_id = None
admin_residents = []
created_reading_id = None
admin_created_reading_id = None

# Test Credentials
ADMIN_1 = {
    "email": "houdamouttalib@gmail.com",
    "password": "pass123"
}

RESIDENT_1 = {
    "email": "abdelwadoud@gmail.com",
    "password": "pass123"
}

ADMIN_2 = {
    "email": "youneseljonhy@gmail.com",
    "password": "pass123"
}

RESIDENT_2_ADMIN2 = {
    "email": "abdelwadoudomrachi@gmail.com",
    "password": "pass123"
}

# ==================== UTILITIES ====================

def log_test(name, passed, message=""):
    """Log test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    TEST_RESULTS.append((name, passed))
    print(f"{status}: {name}")
    if message:
        print(f"       {message}")

def make_request(method, endpoint, data=None, token=None):
    """Make API request"""
    url = f"{API_URL}{endpoint}"
    headers = {
        "Content-Type": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers)
        elif method == "POST":
            resp = requests.post(url, json=data, headers=headers)
        elif method == "PATCH":
            resp = requests.patch(url, json=data, headers=headers)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers)
        return resp
    except Exception as e:
        print(f"Request error: {e}")
        return None

# ==================== AUTHENTICATION TESTS ====================

def test_auth():
    """Test authentication endpoints"""
    print("\n" + "="*60)
    print("AUTHENTICATION TESTS")
    print("="*60)
    
    global admin_token, resident_token, admin2_token, resident2_token, admin_id, resident_id
    
    # Test Admin 1 Login
    resp = make_request("POST", "/auth/login/", ADMIN_1)
    passed = resp and resp.status_code == 200
    log_test("Admin 1 Login", passed, f"Status: {resp.status_code if resp else 'No response'}")
    
    if passed:
        data = resp.json()
        admin_token = data.get("access")
        admin_id = data.get("user", {}).get("id")
        print(f"       Token: {admin_token[:20]}...")
        print(f"       Admin ID: {admin_id}")
    else:
        if resp:
            print(f"       Response: {resp.text}")
    
    # Test Resident Login
    resp = make_request("POST", "/auth/login/", RESIDENT_1)
    passed = resp and resp.status_code == 200
    log_test("Resident 1 Login", passed, f"Status: {resp.status_code if resp else 'No response'}")
    
    if passed:
        data = resp.json()
        resident_token = data.get("access")
        resident_id = data.get("user", {}).get("id")
        print(f"       Token: {resident_token[:20]}...")
        print(f"       Resident ID: {resident_id}")
    else:
        if resp:
            print(f"       Response: {resp.text}")
    
    # Test Admin 2 Login
    resp = make_request("POST", "/auth/login/", ADMIN_2)
    passed = resp and resp.status_code == 200
    log_test("Admin 2 Login", passed, f"Status: {resp.status_code if resp else 'No response'}")
    
    if passed:
        admin2_token = resp.json().get("access")
    else:
        if resp:
            print(f"       Response: {resp.text}")
    
    # Test Resident 2 (Admin 2) Login
    resp = make_request("POST", "/auth/login/", RESIDENT_2_ADMIN2)
    passed = resp and resp.status_code == 200
    log_test("Resident 2 (Admin 2) Login", passed, f"Status: {resp.status_code if resp else 'No response'}")
    
    if passed:
        resident2_token = resp.json().get("access")
    else:
        if resp:
            print(f"       Response: {resp.text}")
    
    # Test Get Current User (only if admin_token exists)
    if admin_token:
        resp = make_request("GET", "/auth/me/", token=admin_token)
        passed = resp and resp.status_code == 200
        log_test("Get Current User (Admin)", passed, 
                 f"User: {resp.json().get('email')}" if passed else "")

# ==================== ADMIN ENDPOINTS TESTS ====================

def test_admin_endpoints():
    """Test admin-specific endpoints"""
    print("\n" + "="*60)
    print("ADMIN ENDPOINTS TESTS")
    print("="*60)
    
    global admin_residents
    
    # Get Residents List
    resp = make_request("GET", "/admin/residents/", token=admin_token)
    passed = resp and resp.status_code == 200
    log_test("Admin Get Residents List", passed)
    
    if passed:
        data = resp.json()
        admin_residents = data.get("residents", [])
        print(f"       Found {len(admin_residents)} residents")
    
    # Get Admin Dashboard
    resp = make_request("GET", "/admin/dashboard/", token=admin_token)
    passed = resp and resp.status_code == 200
    log_test("Admin Get Dashboard", passed)
    
    if passed:
        data = resp.json()
        total_consumption = data.get("total_consumption_kwh", 0)
        residents_count = data.get("total_residents", 0)
        print(f"       Total Consumption: {total_consumption} kWh")
        print(f"       Total Residents: {residents_count}")

# ==================== RESIDENT ENDPOINTS TESTS ====================

def test_resident_endpoints():
    """Test resident-specific endpoints"""
    print("\n" + "="*60)
    print("RESIDENT ENDPOINTS TESTS")
    print("="*60)
    
    # Get Resident Dashboard
    resp = make_request("GET", "/resident/dashboard/", token=resident_token)
    passed = resp and resp.status_code == 200
    log_test("Resident Get Dashboard", passed)
    
    if passed:
        data = resp.json()
        total_consumption = data.get("total_consumption_kwh", 0)
        meter_id = data.get("meter_id", "")
        print(f"       Meter ID: {meter_id}")
        print(f"       Total Consumption: {total_consumption} kWh")
    
    # Get Resident Readings
    resp = make_request("GET", "/resident/readings/", token=resident_token)
    passed = resp and resp.status_code == 200
    log_test("Resident Get Readings", passed)
    
    if passed:
        data = resp.json()
        readings_count = len(data) if isinstance(data, list) else 0
        print(f"       Found {readings_count} readings")

# ==================== CRUD OPERATIONS TESTS ====================

def test_crud_operations():
    """Test Create, Read, Update, Delete operations"""
    print("\n" + "="*60)
    print("CRUD OPERATIONS TESTS")
    print("="*60)
    
    global created_reading_id
    
    # CREATE - Resident creates a reading
    new_reading = {
        "meter_id": "MTR-ADM1-001",
        "timestamp": (datetime.now()).isoformat(),
        "consumption_kwh": 7.5,
        "tariff_type": "standard"
    }
    
    resp = make_request("POST", "/resident/readings/", new_reading, resident_token)
    passed = resp and resp.status_code == 201
    log_test("CREATE Reading (Resident)", passed)
    
    if passed:
        created_reading = resp.json()
        created_reading_id = created_reading.get("id")
        print(f"       Created Reading ID: {created_reading_id}")
        print(f"       Consumption: {created_reading.get('consumption_kwh')} kWh")
    else:
        created_reading_id = None
        print(f"       Response: {resp.text if resp else 'No response'}")
    
    # READ - Get the created reading
    if created_reading_id:
        resp = make_request("GET", f"/resident/readings/?meter_id=MTR-ADM1-001", 
                          token=resident_token)
        passed = resp and resp.status_code == 200
        log_test("READ Readings (Resident)", passed)
        
        if passed:
            readings = resp.json()
            print(f"       Found {len(readings)} readings")
    
    # UPDATE - Resident updates a reading
    if created_reading_id:
        updated_data = {
            "consumption_kwh": 8.2
        }
        
        resp = make_request("PATCH", f"/resident/readings/{created_reading_id}/", 
                          updated_data, resident_token)
        passed = resp and resp.status_code == 200
        log_test("UPDATE Reading (Resident)", passed)
        
        if passed:
            updated_reading = resp.json()
            print(f"       Updated Consumption: {updated_reading.get('consumption_kwh')} kWh")
    
    # DELETE - Resident deletes a reading
    if created_reading_id:
        resp = make_request("DELETE", f"/resident/readings/{created_reading_id}/", 
                          token=resident_token)
        passed = resp and resp.status_code in [200, 204]
        log_test("DELETE Reading (Resident)", passed)

# ==================== ADMIN CRUD TESTS ====================

def test_admin_crud():
    """Test admin CRUD operations on resident readings"""
    print("\n" + "="*60)
    print("ADMIN CRUD OPERATIONS TESTS")
    print("="*60)
    
    if not admin_residents or len(admin_residents) == 0:
        print("⚠️  No residents found for admin, skipping admin CRUD tests")
        return
    
    target_resident_id = admin_residents[0].get("id")
    print(f"Using resident ID: {target_resident_id}")
    
    global admin_created_reading_id
    
    # CREATE - Admin creates reading for resident
    new_reading = {
        "meter_id": "MTR-TEST-001",
        "timestamp": (datetime.now()).isoformat(),
        "consumption_kwh": 6.3,
        "tariff_type": "peak"
    }
    
    resp = make_request("POST", 
                       f"/admin/residents/{target_resident_id}/readings/", 
                       new_reading, admin_token)
    passed = resp and resp.status_code == 201
    log_test("CREATE Reading (Admin for Resident)", passed)
    
    if passed:
        created = resp.json()
        admin_created_reading_id = created.get("id")
        print(f"       Created Reading ID: {admin_created_reading_id}")
    else:
        admin_created_reading_id = None
        print(f"       Response: {resp.text if resp else 'No response'}")
    
    # READ - Admin gets resident readings
    resp = make_request("GET", 
                       f"/admin/residents/{target_resident_id}/readings/", 
                       token=admin_token)
    passed = resp and resp.status_code == 200
    log_test("READ Resident Readings (Admin)", passed)
    
    if passed:
        readings = resp.json()
        print(f"       Found {len(readings)} readings")
    
    # UPDATE - Admin updates reading
    if admin_created_reading_id:
        updated_data = {
            "consumption_kwh": 7.1
        }
        
        resp = make_request("PATCH", 
                           f"/admin/residents/{target_resident_id}/readings/{admin_created_reading_id}/",
                           updated_data, admin_token)
        passed = resp and resp.status_code == 200
        log_test("UPDATE Reading (Admin)", passed)
        
        if passed:
            print(f"       Updated successfully")
    
    # DELETE - Admin deletes reading
    if admin_created_reading_id:
        resp = make_request("DELETE", 
                           f"/admin/residents/{target_resident_id}/readings/{admin_created_reading_id}/",
                           token=admin_token)
        passed = resp and resp.status_code in [200, 204]
        log_test("DELETE Reading (Admin)", passed)

# ==================== PERMISSION TESTS ====================

def test_permissions():
    """Test permission restrictions"""
    print("\n" + "="*60)
    print("PERMISSION TESTS")
    print("="*60)
    
    # Resident should NOT access admin endpoints
    resp = make_request("GET", "/admin/residents/", token=resident_token)
    passed = resp and resp.status_code == 403
    log_test("Resident Cannot Access Admin Endpoints", passed)
    
    # Resident should NOT see other residents' data
    other_resident_id = resident_id + 100  # Fake ID
    resp = make_request("GET", f"/admin/residents/{other_resident_id}/readings/", 
                       token=resident_token)
    passed = resp and resp.status_code != 200
    log_test("Resident Cannot Access Other Residents Data", passed)

# ==================== SUMMARY ====================

def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total = len(TEST_RESULTS)
    passed = sum(1 for _, p in TEST_RESULTS if p)
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ✓")
    print(f"Failed: {failed} ✗")
    
    if failed > 0:
        print("\nFailed Tests:")
        for name, passed_flag in TEST_RESULTS:
            if not passed_flag:
                print(f"  - {name}")
    
    pass_rate = (passed / total * 100) if total > 0 else 0
    print(f"\nPass Rate: {pass_rate:.1f}%")
    
    return failed == 0

# ==================== MAIN ====================

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "SmartMeter API Test Suite" + " "*18 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        test_auth()
        test_admin_endpoints()
        test_resident_endpoints()
        test_crud_operations()
        test_admin_crud()
        test_permissions()
        
        success = print_summary()
        
        return 0 if success else 1
    
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
