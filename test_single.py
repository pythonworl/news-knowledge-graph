import httpx
import json

def test():
    print("Starting single article POST...")
    try:
        # Use a specific known TechCrunch OpenAI article
        url = "https://techcrunch.com/2024/05/14/openai-ilya-sutskever-leaves/"
        
        response = httpx.post(
            "http://127.0.0.1:8000/articles", 
            json={"url": url}, 
            timeout=120.0
        )
        print("Article Status:", response.status_code)
        print("Article Body:", json.dumps(response.json(), indent=2))
    except Exception as e:
        print("Article test failed:", e)
        return

    print("\nGetting People...")
    try:
        response = httpx.get("http://127.0.0.1:8000/people")
        print("People Status:", response.status_code)
        people = response.json()
        print("People list:", json.dumps(people, indent=2))
    except Exception as e:
        print("Failed getting people:", e)

if __name__ == "__main__":
    test()
