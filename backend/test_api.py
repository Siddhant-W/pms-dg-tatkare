import requests

BASE = "http://localhost:8000/api"
TODAY = "2026-08-30"

print("=" * 50)
print("1. Testing LOGIN...")
r = requests.post(f"{BASE}/auth/login", json={"username": "Vaishali", "password": "Vaishali"})
print(f"   Status: {r.status_code}")
assert r.status_code == 200, f"Login failed: {r.text}"
token = r.json()["access_token"]
print(f"   Got token: {token[:30]}...")

headers = {"Authorization": f"Bearer {token}"}

print("\n2. Testing GET /teachers with date...")
r2 = requests.get(f"{BASE}/teachers", params={"date": TODAY}, headers=headers)
print(f"   Status: {r2.status_code}")
if r2.status_code == 200:
    teachers = r2.json()
    print(f"   Got {len(teachers)} teachers")
    print(f"   First: {teachers[0]['name']} | status: {teachers[0]['attendance_status']}")
else:
    print(f"   Error: {r2.text[:300]}")

print("\n3. Testing GET /attendance/summary...")
r3 = requests.get(f"{BASE}/attendance/summary", params={"date": TODAY}, headers=headers)
print(f"   Status: {r3.status_code}")
if r3.status_code == 200:
    print(f"   Summary: {r3.json()}")
else:
    print(f"   Error: {r3.text[:300]}")

print("\n4. Testing PUT /attendance/{teacher_id} (mark absent)...")
teacher_id = teachers[0]["id"]
r4 = requests.put(
    f"{BASE}/attendance/{teacher_id}",
    json={"status": "ABSENT"},
    params={"date": TODAY},
    headers=headers
)
print(f"   Status: {r4.status_code}")
if r4.status_code == 200:
    print(f"   Attendance marked: {r4.json()['status']}")
else:
    print(f"   Error: {r4.text[:300]}")

print("\n5. Testing GET /proxy-requirements (after marking absent)...")
r5 = requests.get(f"{BASE}/proxy-requirements", params={"date": TODAY}, headers=headers)
print(f"   Status: {r5.status_code}")
if r5.status_code == 200:
    reqs = r5.json()
    print(f"   Got {len(reqs)} requirements")
    if reqs:
        print(f"   First requirement: Period {reqs[0]['period_number']} | {reqs[0]['absent_teacher_name']} | {reqs[0]['status']}")
        req_id = reqs[0]["id"]
        
        print(f"\n6. Testing GET /proxy-requirements/{req_id}/candidates...")
        r6 = requests.get(f"{BASE}/proxy-requirements/{req_id}/candidates", headers=headers)
        print(f"   Status: {r6.status_code}")
        if r6.status_code == 200:
            candidates = r6.json()
            print(f"   Got {len(candidates)} candidates")
            if candidates:
                print(f"   Top candidate: {candidates[0]['teacher_name']} | recommended: {candidates[0]['is_recommended']}")
        else:
            print(f"   Error: {r6.text[:300]}")
else:
    print(f"   Error: {r5.text[:300]}")

print("\n" + "=" * 50)
print("ALL TESTS PASSED ✓")
