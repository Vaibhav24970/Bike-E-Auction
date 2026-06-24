from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

print('--- Testing /health ---')
response = client.get('/health')
print(f'Status: {response.status_code}')
print(f'Body: {response.json()}')

print('\n--- Testing Login ---')
response = client.post('/api/v1/auth/login', json={'email': 'admin@eauction.dev', 'password': 'Admin@123456'})
print(f'Status: {response.status_code}')
data = response.json()
print(f'Access Token Received: {"Yes" if "access_token" in data else "No"}')
token = data.get('access_token')

if token:
    print('\n--- Testing /me ---')
    response = client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {token}'})
    print(f'Status: {response.status_code}')
    print(f'User: {response.json().get("email")} ({response.json().get("role")})')

    print('\n--- Testing Auctions List ---')
    response = client.get('/api/v1/auctions')
    print(f'Status: {response.status_code}')
    auctions = response.json()
    print(f'Found {len(auctions)} auctions.')
    for a in auctions:
        print(f'  - {a["title"]} (Status: {a["status"]}, Current Bid: {a["current_bid"]})')

