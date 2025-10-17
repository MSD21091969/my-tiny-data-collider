"""Test casefile creation."""
import os
os.environ["USE_MOCKS"] = "true"

import asyncio
from fastapi.testclient import TestClient
from src.pydantic_api.app import app
import json

# Manually run startup events (TestClient doesn't do this automatically)
async def init_app():
    for event_handler in app.router.on_startup:
        if asyncio.iscoroutinefunction(event_handler):
            await event_handler()
        else:
            event_handler()

asyncio.run(init_app())

client = TestClient(app)

print("Testing POST /v1/casefiles/ endpoint...")
response = client.post(
    "/v1/casefiles/",
    params={"title": "Test Case", "description": "A test casefile"}
)

print(f"Status Code: {response.status_code}")
resp_json = response.json()
print(f"Response: {json.dumps(resp_json, indent=2)}")

if response.status_code == 200:
    print("\nSUCCESS: Casefile created successfully!")
else:
    print(f"\nFAILED: Error response")


