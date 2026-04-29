import requests, json, base64, sys, os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def print_result(test_name, resp):
    status = "✅" if resp.status_code < 400 else "❌"
    print(f"  {status} [{resp.status_code}] {test_name}")
    try:
        print(f"     {json.dumps(resp.json(), indent=6)[:300]}")
    except:
        print(f"     {resp.text[:200]}")
    print()

def test_data(base_url):
    print("─── /data ────────────────────────────────────")
    print_result("GET /data",    requests.get(f"{base_url}/data"))
    print_result("POST /data",   requests.post(f"{base_url}/data",   json={"name": "TestItem", "value": 42}))
    print_result("PUT /data",    requests.put(f"{base_url}/data",    json={"id": 1, "name": "UpdatedItem"}))
    print_result("DELETE /data", requests.delete(f"{base_url}/data", json={"id": 1}))

def test_images(base_url):
    print("─── /images ──────────────────────────────────")
    fake_img = base64.b64encode(b"fake_image_bytes_for_testing").decode()
    print_result("POST analyze",   requests.post(f"{base_url}/images", json={"action": "analyze",   "image_base64": fake_img}))
    print_result("POST resize",    requests.post(f"{base_url}/images", json={"action": "resize",    "image_base64": fake_img, "width": 640, "height": 480}))
    print_result("POST thumbnail", requests.post(f"{base_url}/images", json={"action": "thumbnail", "image_base64": fake_img}))
    print_result("POST no image",  requests.post(f"{base_url}/images", json={"action": "analyze"}))

def test_users(base_url):
    print("─── /users ───────────────────────────────────")
    print_result("GET all users",  requests.get(f"{base_url}/users"))
    print_result("GET user ?id=1", requests.get(f"{base_url}/users", params={"id": "1"}))
    print_result("POST new user",  requests.post(f"{base_url}/users", json={"username": "dave", "email": "dave@test.com"}))
    print_result("PUT user",       requests.put(f"{base_url}/users",  json={"id": "2", "username": "bob_updated"}))
    print_result("DELETE user",    requests.delete(f"{base_url}/users", json={"id": "3"}))

def main():
    config = load_config()
    stage  = sys.argv[1] if len(sys.argv) > 1 else "dev"
    base   = config["endpoints"].get(stage)
    if not base:
        print(f"❌ Stage '{stage}' not found in config.json"); sys.exit(1)

    print(f"\n🧪 Testing stage: {stage.upper()}")
    print(f"   Base URL: {base}\n")

    test_data(base)
    test_images(base)
    test_users(base)
    print("🏁 Tests done.")

if __name__ == "__main__":
    main()
