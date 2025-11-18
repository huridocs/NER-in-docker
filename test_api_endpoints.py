import httpx
import json

BASE_URL = "http://localhost:5070"

sample_text = "Barack Obama was born in Hawaii and served as the 44th President of the United States. He signed the Affordable Care Act into law. The United Nations headquarters is located in New York City."

print("=" * 80)
print("TESTING FLAIR vs LLM NER ENDPOINTS")
print("=" * 80)
print(f"\nSample text: {sample_text}\n")

print("\n1. Testing default endpoint (Flair)...")
response = httpx.post(f"{BASE_URL}/", data={"text": sample_text, "language": "en"}, timeout=30.0)

if response.status_code == 200:
    result = response.json()
    print(f"   Status: SUCCESS")
    print(f"   Found {len(result.get('groups', []))} entity groups")
    for group in result.get("groups", [])[:5]:
        print(f"     - {group.get('name')} ({group.get('type')})")
else:
    print(f"   Status: FAILED ({response.status_code})")

print("\n2. Testing /llm endpoint (LLM-based)...")
response = httpx.post(f"{BASE_URL}/llm", data={"text": sample_text, "language": "en"}, timeout=60.0)

if response.status_code == 200:
    result = response.json()
    print(f"   Status: SUCCESS")
    print(f"   Found {len(result.get('groups', []))} entity groups")
    for group in result.get("groups", [])[:5]:
        print(f"     - {group.get('name')} ({group.get('type')})")
else:
    print(f"   Status: FAILED ({response.status_code})")

print("\n3. Testing default endpoint with use_llm=true...")
response = httpx.post(f"{BASE_URL}/", data={"text": sample_text, "language": "en", "use_llm": "true"}, timeout=60.0)

if response.status_code == 200:
    result = response.json()
    print(f"   Status: SUCCESS")
    print(f"   Found {len(result.get('groups', []))} entity groups")
    for group in result.get("groups", [])[:5]:
        print(f"     - {group.get('name')} ({group.get('type')})")
else:
    print(f"   Status: FAILED ({response.status_code})")

print("\n" + "=" * 80)
print("TESTING COMPLETE")
print("=" * 80)
