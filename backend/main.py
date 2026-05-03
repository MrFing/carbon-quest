from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from models import ErrorMessage, PartyResponse
from session_manager import Session, session_manager

DISCONNECT_GRACE_SECONDS = 8

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("carbon_quest.backend")

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
    try:
        await websocket.send_json(payload)
    except Exception:
        logger.warning("Failed to send websocket payload", exc_info=True)


async def safe_close(websocket: WebSocket | None) -> None:
    if websocket is None:
        return
    try:
        await websocket.close()
    except Exception:
        logger.warning("Failed to close websocket cleanly", exc_info=True)


async def broadcast(session: Session, payload: dict[str, Any]) -> None:
    await safe_send(session.player1_ws, payload)
    await safe_send(session.player2_ws, payload)


async def finalize_disconnect(session_id: str, player: int, token: int) -> None:
    await asyncio.sleep(DISCONNECT_GRACE_SECONDS)
    session = session_manager.get_session_by_id(session_id)
    if session is None:
        return
    if session.disconnect_token(player) != token or session.get_socket(player) is not None:
        return

    if session.connected_players() == 0:
        logger.info("Removing abandoned session %s after both players disconnected", session_id)
        session_manager.remove_session(session_id)
        return

    logger.info("Player %s is still disconnected from session %s after grace period", player, session_id)
    await safe_send(session.other_socket(player), {"type": "PLAYER_DISCONNECTED", "player": player})


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok", "service": "carbon-quest-backend"}


@app.get("/health")
async def health_alias() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/create-party", response_model=PartyResponse)
async def create_party() -> PartyResponse:
    session = session_manager.create_session()
    logger.info("Created party %s for session %s", session.party_code, session.session_id)
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

    logger.info("Resolved party code %s to session %s", code.upper(), session.session_id)
    return PartyResponse(code=session.party_code, sessionId=session.session_id)


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, player: int) -> None:
    session = session_manager.get_session_by_id(session_id)
    if session is None:
        await websocket.accept()
        await websocket.send_json(ErrorMessage(message="Session not found or expired.").model_dump())
        await websocket.close()
        return

    if player not in (1, 2):
        await websocket.accept()
        await websocket.send_json(ErrorMessage(message="Player must be 1 or 2.").model_dump())
        await websocket.close()
        return

    previous_socket = session.get_socket(player)
    had_both_connected = session.both_connected()
    joining_second_player = player == 2 and session.player2_ws is None

    await websocket.accept()
    session.mark_connected(player, websocket)
    logger.info("Player %s connected to session %s", player, session_id)

    if previous_socket is not None and previous_socket is not websocket:
        await safe_send(previous_socket, ErrorMessage(message="This player reconnected from another tab.").model_dump())
        await safe_close(previous_socket)

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
            if joining_second_player and not had_both_connected:
                await broadcast(session, {"type": "PLAYER_JOINED"})
            await broadcast(session, {"type": "GAME_START", "state": session.game.get_state()})

        while True:
            payload = await websocket.receive_json()
            message_type = payload.get("type")

            if message_type == "ROLL_DICE":
                try:
                    state = session.game.roll_dice(player)
                except ValueError as exc:
                    await safe_send(websocket, ErrorMessage(message=str(exc)).model_dump())
                    continue
                await broadcast(session, {"type": "STATE_UPDATE", "state": state})
            elif message_type == "MAKE_CHOICE":
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
                logger.info("Player %s ended session %s", player, session_id)
                await broadcast(session, {"type": "PARTY_REVOKED"})
                session_manager.remove_session(session.session_id)
                break
            else:
                await safe_send(websocket, ErrorMessage(message="Unsupported message type.").model_dump())
    except WebSocketDisconnect:
        current_session = session_manager.get_session_by_id(session_id)
        if current_session is None:
            return
        if current_session.get_socket(player) is websocket:
            token = current_session.mark_disconnected(player)
            logger.info("Player %s disconnected from session %s, waiting for reconnect", player, session_id)
            asyncio.create_task(finalize_disconnect(session_id, player, token))
    except Exception:
        logger.exception("Unexpected websocket error in session %s for player %s", session_id, player)
        current_session = session_manager.get_session_by_id(session_id)
        if current_session is not None and current_session.get_socket(player) is websocket:
            token = current_session.mark_disconnected(player)
            asyncio.create_task(finalize_disconnect(session_id, player, token))
