import httpx
import time
import sys

url = "http://127.0.0.1:8000"

print("Waiting for port 8000 to open...", flush=True)
for i in range(10):
    try:
        r = httpx.get(f"{url}/health")
        if r.status_code == 200:
            print("Connected!", flush=True)
            break
    except Exception:
        pass
    time.sleep(1.5)
else:
    print("Could not connect to port 8000 after 15 seconds.", flush=True)
    sys.exit(1)

# Step 1: Login to get token
client = httpx.Client()
l = client.post(f"{url}/api/v1/auth/login", json={"email": "priya.sharma@gmail.com", "password": "Demo@2026"})
assert l.status_code == 200, f"Login failed: {l.text}"
token = l.json()["access_token"]
client.headers.update({"Authorization": f"Bearer {token}"})

print("\n--- 1. Currency Specification Endpoint ---")
r = client.get(f"{url}/api/v1/scans/currency/features/500")
print("Status:", r.status_code)
print("Data:", r.json(), "\n")

print("\n--- 2. Threat Intel Feed Endpoint ---")
r = client.get(f"{url}/api/v1/scans/threat-intel")
print("Status:", r.status_code)
print("Data count:", len(r.json().get("threats", [])))
print("Data sample:", r.json().get("threats", [{}])[0], "\n")

print("\n--- 3. Check Entity Endpoint (Safe UPI) ---")
r = client.get(f"{url}/api/v1/scans/check-entity", params={"query": "safe-upi@okaxis"})
print("Status:", r.status_code)
print("Data:", r.json(), "\n")

print("\n--- 4. Check Entity Endpoint (Blacklisted Domain) ---")
r = client.get(f"{url}/api/v1/scans/check-entity", params={"query": "sbi-kyc-update.com"})
print("Status:", r.status_code)
print("Data:", r.json(), "\n")

print("\n--- 5. Scam Call / Digital Arrest Transcript Endpoint ---")
r = client.post(
    f"{url}/api/v1/scans/scam-call",
    json={
        "transcript": "Hello citizen, this is TRAI department calling. Your Aadhaar has been linked to MDMA drug package. You are placed under digital arrest.",
        "language": "en"
    }
)
print("Status:", r.status_code)
print("Verdict:", r.json().get("result", {}).get("verdict"))
print("Summary:", r.json().get("result", {}).get("summary"), "\n")

print("\n--- 6. Deepfake Audio Analysis Endpoint ---")
mock_audio_bytes = b"RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00" + b"\x00" * 2000
files = {"file": ("test.wav", mock_audio_bytes, "audio/wav")}
r = client.post(
    f"{url}/api/v1/scans/deepfake-audio",
    files=files
)
print("Status:", r.status_code)
print("Verdict:", r.json().get("result", {}).get("verdict"))
print("Summary:", r.json().get("result", {}).get("summary"), "\n")
