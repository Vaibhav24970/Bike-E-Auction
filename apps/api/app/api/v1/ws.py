from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websocket.manager import manager
from app.core.security import decode_access_token
from jose import JWTError

router = APIRouter(tags=["WebSockets"])

@router.websocket("/auction/{auction_id}")
async def websocket_auction_endpoint(
    websocket: WebSocket, 
    auction_id: str,
    token: str = Query(None)
):
    if not token:
        await websocket.close(code=1008, reason="Missing token")
        return
        
    try:
        decode_access_token(token)
    except JWTError:
        await websocket.close(code=1008, reason="Invalid token")
        return

    await manager.connect(websocket, auction_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        # Expected disconnect
        pass
    except Exception as e:
        # Handle unexpected drops
        pass
    finally:
        manager.disconnect(websocket, auction_id)
