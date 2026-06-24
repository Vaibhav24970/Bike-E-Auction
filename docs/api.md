# API Reference

A quick breakdown of the REST APIs and WebSocket events for the E-Auction Backend.

## Auth Flow
We're using JSON Web Tokens (JWT) for authentication. 
Pass the token in the `Authorization` header like this: `Bearer <your_jwt_token>`

If something goes wrong, the API throws a standard 400/401/404 with a `detail` string:
```json
{ "detail": "Human-readable error description" }
```

---

## 1. Auth API (`/api/v1/auth`)

- **POST `/api/v1/auth/register`**
  - **Auth:** No
  - **Body:** `email`, `password`, `first_name`, `last_name`, `phone`
- **POST `/api/v1/auth/login`**
  - **Auth:** No (Rate Limited)
  - **Body:** `email`, `password`
  - **Returns:** `{ "access_token": "...", "token_type": "bearer" }`
- **GET `/api/v1/auth/me`**
  - **Auth:** Yes

---

## 2. Bike API (`/api/v1/bikes`)

- **GET `/api/v1/bikes/`** - List all bikes
- **GET `/api/v1/bikes/{id}`** - Get bike details
- **POST `/api/v1/bikes/`** - Admin only. Create a bike.
- **PATCH `/api/v1/bikes/{id}`** - Admin only. Update a bike.
- **DELETE `/api/v1/bikes/{id}`** - Admin only. Delete a bike.

---

## 3. Auctions API (`/api/v1/auctions`)

- **GET `/api/v1/auctions/`** - List all auctions
- **GET `/api/v1/auctions/{id}`** - Get auction details
- **POST `/api/v1/auctions/`** - Admin only. Schedule an auction.

---

## 4. Bids API (`/api/v1/bids`)

- **GET `/api/v1/bids/auction/{auction_id}`** - Get paginated bid history.
- **POST `/api/v1/bids/auction/{auction_id}`** 
  - **Auth:** Yes (Rate Limited)
  - **Body:** `{ "amount": 25000 }`

---

## 5. WebSockets (`/api/v1/ws`)

Connect here to get live updates for a specific auction so you don't have to poll the REST API.

**URL:** `ws://.../api/v1/ws/auction/{auction_id}?token={your_jwt}`
*(Note: We require a JWT to connect just to prevent anonymous actors from exhausting server connections, even though the data is public).*

### Events you'll receive from the server:

**BID_PLACED**
Fired when someone successfully places a bid.
```json
{
  "type": "BID_PLACED",
  "data": { "amount": 25000, "bidder_name": "Jane Doe", "timestamp": "2026-06-24T03:15:00Z" }
}
```

**AUCTION_EXTENDED**
Fired if a bid is placed in the final 30 seconds (up to 3 times max).
```json
{
  "type": "AUCTION_EXTENDED",
  "data": { "new_end_time": "2026-06-24T03:17:00Z", "extension_count": 1 }
}
```

**AUCTION_STARTED / AUCTION_ENDED**
Fired by the background worker when the clock hits the start/end times.
```json
{
  "type": "AUCTION_ENDED",
  "data": { "auction_id": "auc-123", "winner_id": "user-456", "final_price": 25000 }
}
```
