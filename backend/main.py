from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from models import ErrorMessage, GameStateModel, PartyResponse
from session_manager import Session, session_manager


app = FastAPI(title="Carbon Quest Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "*")],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def safe_send(websocket: WebSocket | None, payload: dict[str, Any]) -> None:
    if websocket is None:
        return
    await websocket.send_json(payload)


async def broadcast(session: Session, payload: dict[str, Any]) -> None:
    await safe_send(session.player1_ws, payload)
    await safe_send(session.player2_ws, payload)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/create-party", response_model=PartyResponse)
async def create_party() -> PartyResponse:
    session = session_manager.create_session()
    return PartyResponse(code=session.party_code, sessionId=session.session_id)


@app.get("/api/party/{code}", response_model=PartyResponse)
async def get_party(code: str) -> PartyResponse:
    session = session_manager.get_session_by_code(code)
    if session is None:
        raise HTTPException(status_code=404, detail="Party code not found.")
    if session.player2_ws is not None:
        raise HTTPException(status_code=409, detail="Party is already full.")
    if session.status == "ended":
        raise HTTPException(status_code=410, detail="This party has ended.")
    return PartyResponse(code=session.party_code, sessionId=session.session_id)


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, player: int) -> None:
    session = session_manager.get_session_by_id(session_id)
    if session is None:
        await websocket.accept()
        await websocket.send_json(ErrorMessage(message="Session not found.").model_dump())
        await websocket.close()
        return

    if player not in (1, 2):
        await websocket.accept()
        await websocket.send_json(ErrorMessage(message="Player must be 1 or 2.").model_dump())
        await websocket.close()
        return

    if player == 2 and session.player2_ws is not None:
        await websocket.accept()
        await websocket.send_json(ErrorMessage(message="This party is already full.").model_dump())
        await websocket.close()
        return

    await websocket.accept()
    session.set_socket(player, websocket)

    try:
        if player == 1:
            await safe_send(
                websocket,
                {
                    "type": "PARTY_CREATED",
                    "code": session.party_code,
                    "sessionId": session.session_id,
                },
            )
        if session.both_connected():
            session.status = "playing"
            await broadcast(session, {"type": "PLAYER_JOINED"})
            await broadcast(session, {"type": "GAME_START", "state": session.game.get_state()})
        elif player == 2:
            await safe_send(websocket, {"type": "GAME_START", "state": session.game.get_state()})

        while True:
            payload = await websocket.receive_json()
            message_type = payload.get("type")

            if message_type == "MAKE_CHOICE":
                try:
                    state = session.game.make_choice(player, payload.get("choice"))
                except ValueError as exc:
                    await safe_send(websocket, ErrorMessage(message=str(exc)).model_dump())
                    continue

                if state["gameOver"]:
                    session.status = "ended"
                    await broadcast(session, {"type": "GAME_OVER", "state": state, "winner": state["winner"]})
                else:
                    await broadcast(session, {"type": "STATE_UPDATE", "state": state})
            elif message_type == "PLAY_AGAIN":
                session.play_again_votes.add(player)
                if len(session.play_again_votes) == 2 or session.connected_players() == 1:
                    session.play_again_votes.clear()
                    session.game.reset()
                    session.status = "playing" if session.both_connected() else "waiting"
                    await broadcast(session, {"type": "GAME_START", "state": session.game.get_state()})
            elif message_type == "QUIT":
                await broadcast(session, {"type": "PARTY_REVOKED"})
                session_manager.remove_session(session.session_id)
                break
            else:
                await safe_send(websocket, ErrorMessage(message="Unsupported message type.").model_dump())
    except WebSocketDisconnect:
        other = session.other_socket(player)
        session.set_socket(player, None)
        if other is not None:
            await safe_send(other, {"type": "PLAYER_DISCONNECTED"})
            await safe_send(other, {"type": "PARTY_REVOKED"})
        session_manager.remove_session(session.session_id)
