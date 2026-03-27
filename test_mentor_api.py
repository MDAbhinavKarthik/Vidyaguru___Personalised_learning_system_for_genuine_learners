#!/usr/bin/env python
"""Test mentor API endpoint"""
import urllib.request
import json

try:
    url = "http://localhost:8000/api/v1/mentor/chat"
    data = json.dumps({"message": "hello"}).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req, timeout=5) as response:
        status = response.status
        content = response.read().decode('utf-8')
        print(f"Status: {status}")
        print(f"Response: {content[:500]}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
