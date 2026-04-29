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
  const player = (routeState?.player ?? Number(sessionStorage.getItem(`carbon-quest-player:${sessionId}`)) ?? 0) as 1 | 2;
  const [state, setState] = useState<GameState>(routeState?.initialState ?? createInitialState());
  const [hasRemoteState, setHasRemoteState] = useState(Boolean(routeState?.initialState));
  const [showBankruptcyOverlay, setShowBankruptcyOverlay] = useState(false);
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

  const { sendMessage } = useWebSocket(wsUrl, {
    onMessage: (message: ServerMessage) => {
      if (message.type === "GAME_START" || message.type === "STATE_UPDATE" || message.type === "GAME_OVER") {
        setState(message.state);
        setHasRemoteState(true);
        if (message.state.gameOverReason === "bankruptcy") {
          setShowBankruptcyOverlay(true);
        } else {
          setShowBankruptcyOverlay(false);
        }
      }
      if (message.type === "PLAYER_DISCONNECTED") {
        redirectHome("Player disconnected");
      }
      if (message.type === "PARTY_REVOKED") {
        redirectHome("Session ended");
      }
      if (message.type === "ERROR") {
        setToast(message.message);
      }
    }
  });

  const canPlay = hasRemoteState && !state.gameOver && state.currentPlayer === player;
  const currentBudget = player === 1 ? state.player1.budget : state.player2.budget;
  const disabledMessage = !canPlay && !state.gameOver ? `Waiting for Player ${state.currentPlayer}...` : null;

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
        currentBudget={currentBudget}
        disabledMessage={disabledMessage}
        onChoice={(choice) => sendMessage({ type: "MAKE_CHOICE", choice })}
        onPlayAgain={() => {
          setShowBankruptcyOverlay(false);
          sendMessage({ type: "PLAY_AGAIN" });
        }}
        onQuit={() => {
          sendMessage({ type: "QUIT" });
          navigate("/", { replace: true });
        }}
        showBankruptcyOverlay={showBankruptcyOverlay}
        onDismissBankruptcyOverlay={() => setShowBankruptcyOverlay(false)}
      />
    </div>
  );
}
