import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";

import GameBoard from "./GameBoard";
import { createInitialState } from "../game/gameLogic";
import type { GameState, ServerMessage } from "../game/types";
import { getBackendWsBase, useWebSocket } from "../hooks/useWebSocket";

interface RouteState {
  player?: 1 | 2;
  partyCode?: string;
  initialState?: GameState;
}

export default function OnlineSessionPage() {
  const { sessionId = "" } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const routeState = (location.state as RouteState | null) ?? null;
  const storedPlayer = Number(sessionStorage.getItem(`carbon-quest-player:${sessionId}`));
  const player = (routeState?.player ?? storedPlayer ?? 0) as 1 | 2;
  const [state, setState] = useState<GameState>(routeState?.initialState ?? createInitialState());
  const [hasRemoteState, setHasRemoteState] = useState(Boolean(routeState?.initialState));
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId || (player !== 1 && player !== 2)) {
      navigate("/online", { replace: true });
      return;
    }
    sessionStorage.setItem(`carbon-quest-player:${sessionId}`, String(player));
  }, [navigate, player, sessionId]);

  const wsUrl = useMemo(() => {
    if (!sessionId || (player !== 1 && player !== 2)) {
      return null;
    }
    return `${getBackendWsBase()}/ws/${sessionId}?player=${player}`;
  }, [player, sessionId]);

  const redirectHome = (message: string) => {
    setToast(message);
    window.setTimeout(() => navigate("/", { replace: true }), 1100);
  };

  const { status, sendMessage } = useWebSocket(wsUrl, {
    reconnect: true,
    onMessage: (message: ServerMessage) => {
      if (message.type === "GAME_START" || message.type === "STATE_UPDATE" || message.type === "GAME_OVER") {
        setState(message.state);
        setHasRemoteState(true);
        setToast(null);
      }
      if (message.type === "PLAYER_DISCONNECTED") {
        const disconnectedPlayer = message.player ?? (player === 1 ? 2 : 1);
        setToast(`Player ${disconnectedPlayer} disconnected. Waiting for them to reconnect...`);
      }
      if (message.type === "PARTY_REVOKED") {
        redirectHome("Session ended");
      }
      if (message.type === "ERROR") {
        if (/session not found/i.test(message.message)) {
          redirectHome("Session expired");
        } else {
          setToast(message.message);
        }
      }
    }
  });

  useEffect(() => {
    if (status === "connecting" && hasRemoteState) {
      setToast((current) => current ?? "Reconnecting to session...");
    }
    if (status === "open" && toast === "Reconnecting to session...") {
      setToast(null);
    }
  }, [hasRemoteState, status, toast]);

  const canPlay = hasRemoteState && !state.gameOver && state.currentPlayer === player;
  let disabledMessage: string | null = null;
  if (!hasRemoteState) {
    disabledMessage = player === 1 ? "Waiting for the session to start..." : "Waiting for Player 1 to start the game...";
  } else if (!canPlay && !state.gameOver) {
    disabledMessage = state.selectedCard || state.selectedEvent
      ? `Waiting for Player ${state.currentPlayer} to choose a plan...`
      : `Waiting for Player ${state.currentPlayer} to roll the dice...`;
  }

  return (
    <div style={{ position: "relative" }}>
      {toast ? (
        <div
          style={{
            position: "fixed",
            top: 24,
            left: "50%",
            transform: "translateX(-50%)",
            zIndex: 20,
            padding: "12px 18px",
            borderRadius: 999,
            background: "rgba(15, 23, 42, 0.92)",
            color: "#e2e8f0",
            border: "1px solid rgba(148, 163, 184, 0.24)"
          }}
        >
          {toast}
        </div>
      ) : null}

      <GameBoard
        state={state}
        canPlay={canPlay}
        disabledMessage={disabledMessage}
        onRoll={() => sendMessage({ type: "ROLL_DICE" })}
        onChoice={(choice) => sendMessage({ type: "MAKE_CHOICE", choice })}
        onPlayAgain={() => sendMessage({ type: "PLAY_AGAIN" })}
        onQuit={() => {
          sendMessage({ type: "QUIT" });
          navigate("/", { replace: true });
        }}
      />
    </div>
  );
}
