import httpx
import json

def test():
    print("Starting Rescan (1 page)...")
    try:
        response = httpx.post("http://127.0.0.1:8000/rescan", json={"pages": 1}, timeout=120.0)
        print("Rescan Status:", response.status_code)
        print("Rescan Body:", json.dumps(response.json(), indent=2))
    except Exception as e:
        print("Rescan failed:", e)
        return

    print("\nGetting People...")
    try:
        response = httpx.get("http://127.0.0.1:8000/people")
        print("People Status:", response.status_code)
        people = response.json()
        print("People list:", json.dumps(people, indent=2))
        
        if people:
            first_person = people[0]["id"]
            print(f"\nGetting Details for {first_person}...")
            response = httpx.get(f"http://127.0.0.1:8000/people/{first_person}")
            print(f"Details Status:", response.status_code)
            print(f"Details Body:", json.dumps(response.json(), indent=2))
    except Exception as e:
        print("Failed getting people:", e)

if __name__ == "__main__":
    test()
