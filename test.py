import asyncio
import httpx


SIGNUP_URL = "http://localhost:8080/api/users/signup"

async def send_signup_request(client: httpx.AsyncClient, i: int):
    await asyncio.sleep(0.1)

    payload = {
        "name": f"User {i}",
        "email": f"testuser{i}@example.com",
        "password": "StrongPassword123!",
        "phone_no": 9999999999
    }
    try:
        response = await client.post(SIGNUP_URL, json=payload)
        return i, response.status_code
    except Exception as e:
        return i, f"Error: {str(e)}"

async def make_1000_signup_requests():
    async with httpx.AsyncClient(timeout=100.0) as client:
        tasks = [send_signup_request(client, i) for i in range(1000, 2000)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, result in enumerate(results):
            print(f"Request {i}: {result}")

if __name__ == "__main__":
    asyncio.run(make_1000_signup_requests())