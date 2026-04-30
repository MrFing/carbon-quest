from __future__ import annotations

import random
import string
import time
from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4

from fastapi import WebSocket

from game_logic import CarbonQuestGame

PARTY_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


@dataclass
class Session:
    session_id: str
    party_code: str
    game: CarbonQuestGame
    status: str = "waiting"
    player1_ws: Optional[WebSocket] = None
    player2_ws: Optional[WebSocket] = None
    play_again_votes: set[int] = field(default_factory=set)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    disconnect_tokens: dict[int, int] = field(default_factory=lambda: {1: 0, 2: 0})

    def touch(self) -> None:
        self.updated_at = time.time()

    def get_socket(self, player: int) -> Optional[WebSocket]:
        return self.player1_ws if player == 1 else self.player2_ws

    def set_socket(self, player: int, websocket: Optional[WebSocket]) -> None:
        if player == 1:
            self.player1_ws = websocket
        else:
            self.player2_ws = websocket
        self.touch()

    def other_socket(self, player: int) -> Optional[WebSocket]:
        return self.player2_ws if player == 1 else self.player1_ws

    def connected_players(self) -> int:
        return int(self.player1_ws is not None) + int(self.player2_ws is not None)

    def both_connected(self) -> bool:
        return self.player1_ws is not None and self.player2_ws is not None

    def mark_connected(self, player: int, websocket: WebSocket) -> None:
        self.disconnect_tokens[player] += 1
        self.set_socket(player, websocket)

    def mark_disconnected(self, player: int) -> int:
        self.disconnect_tokens[player] += 1
        self.set_socket(player, None)
        return self.disconnect_tokens[player]

    def disconnect_token(self, player: int) -> int:
        return self.disconnect_tokens[player]


class SessionManager:
    def __init__(self) -> None:
        self.sessions_by_id: dict[str, Session] = {}
        self.sessions_by_code: dict[str, Session] = {}

    def create_session(self) -> Session:
        session = Session(
            session_id=str(uuid4()),
            party_code=self._generate_party_code(),
            game=CarbonQuestGame(),
        )
        self.sessions_by_id[session.session_id] = session
        self.sessions_by_code[session.party_code] = session
        return session

    def get_session_by_id(self, session_id: str) -> Optional[Session]:
        return self.sessions_by_id.get(session_id)

    def get_session_by_code(self, code: str) -> Optional[Session]:
        return self.sessions_by_code.get(code.upper())

    def remove_session(self, session_id: str) -> None:
        session = self.sessions_by_id.pop(session_id, None)
        if session:
            self.sessions_by_code.pop(session.party_code, None)

    def _generate_party_code(self) -> str:
        while True:
            code = "".join(random.choice(PARTY_CODE_ALPHABET) for _ in range(6))
            if code not in self.sessions_by_code:
                return code


session_manager = SessionManager()
