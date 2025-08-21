#!/usr/bin/env python3
"""
Simple test script to verify the backend API endpoints
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_login():
    """Test login endpoint"""
    print("\nTesting login endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "username": "christian",
            "password": "password123"
        })
        print(f"Login: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Token received: {data['access_token'][:20]}...")
            return data['access_token']
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Login failed: {e}")
        return None

def test_protected_endpoint(token):
    """Test a protected endpoint"""
    print("\nTesting protected endpoint...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"Protected endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"User: {data['username']} - {data['role']}")
            return True
        else:
            print(f"Protected endpoint failed: {response.text}")
            return False
    except Exception as e:
        print(f"Protected endpoint failed: {e}")
        return False

def test_optimization_start(token):
    """Test starting an optimization"""
    print("\nTesting optimization start...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/optimization/start", 
                               headers=headers,
                               json={"optimization_type": "laptop_supply_chain"})
        print(f"Optimization start: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Request ID: {data['request_id']}")
            return data['request_id']
        else:
            print(f"Optimization start failed: {response.text}")
            return None
    except Exception as e:
        print(f"Optimization start failed: {e}")
        return None

def test_optimization_progress(token, request_id):
    """Test getting optimization progress"""
    print("\nTesting optimization progress...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/optimization/progress/{request_id}", 
                              headers=headers)
        print(f"Progress check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data['status']}, Progress: {data['progress_percentage']}%")
            return True
        else:
            print(f"Progress check failed: {response.text}")
            return False
    except Exception as e:
        print(f"Progress check failed: {e}")
        return False

def main():
    print("🚀 Testing Supply Chain Agent API")
    print("=" * 40)
    
    # Test health
    if not test_health():
        print("❌ Health check failed. Is the backend running?")
        return
    
    # Test login
    token = test_login()
    if not token:
        print("❌ Login failed")
        return
    
    # Test protected endpoint
    if not test_protected_endpoint(token):
        print("❌ Protected endpoint test failed")
        return
    
    # Test optimization start
    request_id = test_optimization_start(token)
    if not request_id:
        print("❌ Optimization start failed")
        return
    
    # Wait a bit and test progress
    print("\nWaiting 3 seconds for optimization to progress...")
    time.sleep(3)
    
    if not test_optimization_progress(token, request_id):
        print("❌ Progress check failed")
        return
    
    print("\n✅ All tests passed! The API is working correctly.")
    print(f"\nYou can now:")
    print(f"1. Start the React frontend: cd supply-chain-ui && npm start")
    print(f"2. Login with: christian / password123")
    print(f"3. Test the optimization workflow")

if __name__ == "__main__":
    main()
