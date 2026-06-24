import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from app.main import app
from app.api.v1.bids import get_bid_service
from app.api.deps import get_current_user
from app.models import User
from app.schemas import BidResponse, PaginatedBidHistory
from datetime import datetime

client = TestClient(app)

def override_get_current_user():
    return User(id="user123", email="test@test.com")

@pytest.fixture
def override_deps():
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear()

def test_place_bid_integration(override_deps):
    mock_service = AsyncMock()
    mock_service.place_bid.return_value = BidResponse(
        id="bid1",
        auction_id="auc1",
        user_id="user123",
        amount=5000,
        is_winning=True,
        created_at=datetime.utcnow()
    )
    
    app.dependency_overrides[get_bid_service] = lambda: mock_service
    
    response = client.post(
        "/api/v1/bids/auction/auc1",
        json={"amount": 5000}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 5000
    assert data["is_winning"] is True
    assert mock_service.place_bid.called

def test_get_bid_history_integration(override_deps):
    mock_service = AsyncMock()
    mock_service.get_bid_history.return_value = PaginatedBidHistory(
        items=[],
        total=0,
        page=1,
        size=20
    )
    
    app.dependency_overrides[get_bid_service] = lambda: mock_service
    
    response = client.get("/api/v1/bids/auction/auc1?page=1&size=20")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert mock_service.get_bid_history.called
