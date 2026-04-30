import { useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";

import { getBackendWsBase, useWebSocket } from "../hooks/useWebSocket";
import type { GameState, ServerMessage } from "../game/types";

interface LocationState {
  sessionId?: string;
  player?: 1;
}

export default function CreateParty() {
  const navigate = useNavigate();
  const location = useLocation();
  const { code = "" } = useParams();
  const state = (location.state as LocationState | null) ?? null;
  const sessionId = state?.sessionId ?? sessionStorage.getItem(`carbon-quest-party:${code}`) ?? "";
  const [copied, setCopied] = useState(false);
  const [waitingFlash, setWaitingFlash] = useState(false);
  const [countdown, setCountdown] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pendingState = useRef<GameState | null>(null);

  useEffect(() => {
    if (!sessionId) {
      navigate("/online", { replace: true });
    } else {
      sessionStorage.setItem(`carbon-quest-player:${sessionId}`, "1");
      sessionStorage.setItem(`carbon-quest-party:${code}`, sessionId);
    }
  }, [code, navigate, sessionId]);

  const wsUrl = useMemo(() => {
    if (!sessionId) {
      return null;
    }
    return `${getBackendWsBase()}/ws/${sessionId}?player=1`;
  }, [sessionId]);

  const { status, sendMessage } = useWebSocket(wsUrl, {
    reconnect: true,
    onMessage: (message: ServerMessage) => {
      if (message.type === "ERROR") {
        if (/session not found/i.test(message.message)) {
          navigate("/online", { replace: true });
          return;
        }
        setError(message.message);
      }
      if (message.type === "PLAYER_JOINED") {
        setWaitingFlash(true);
        window.setTimeout(() => setWaitingFlash(false), 1500);
      }
      if (message.type === "GAME_START") {
        pendingState.current = message.state;
        setCountdown((current) => current ?? 3);
        setError(null);
      }
      if (message.type === "PARTY_REVOKED") {
        navigate("/online", { replace: true });
      }
    }
  });

  useEffect(() => {
    if (countdown === null) {
      return undefined;
    }
    if (countdown <= 0) {
      navigate(`/game/${sessionId}`, {
        replace: true,
        state: {
          player: 1,
          partyCode: code,
          initialState: pendingState.current
        }
      });
      return undefined;
    }

    const timer = window.setTimeout(() => setCountdown((value) => (value === null ? null : value - 1)), 1000);
    return () => window.clearTimeout(timer);
  }, [code, countdown, navigate, sessionId]);

  return (
    <div className="page-center">
      <div
        className="glass-panel"
        style={{
          width: "min(100%, 720px)",
          minHeight: 620,
          borderRadius: 28,
          padding: "48px 48px 40px",
          position: "relative",
          display: "grid",
          alignContent: "start",
          gap: 24
        }}
      >
        <button
          onClick={() => {
            sendMessage({ type: "QUIT" });
            navigate("/online");
          }}
          style={{
            position: "absolute",
            top: 22,
            left: 22,
            border: "none",
            background: "transparent",
            color: "#cbd5e1",
            fontWeight: 700,
            fontSize: 16
          }}
        >
          &larr; Back
        </button>

        <div style={{ textAlign: "center", marginTop: 8 }}>
          <div style={{ color: "#94A3B8", fontSize: 22, fontWeight: 700 }}>Party Code</div>
          <div style={{ marginTop: 18, display: "inline-flex", alignItems: "center", gap: 16 }}>
            <div
              style={{
                color: "#00C853",
                fontSize: 48,
                fontWeight: 900,
                letterSpacing: 12,
                fontFamily: "ui-monospace, SFMono-Regular, Consolas, monospace"
              }}
            >
              {code}
            </div>
            <button
              onClick={async () => {
                await navigator.clipboard.writeText(code);
                setCopied(true);
                window.setTimeout(() => setCopied(false), 2000);
              }}
              style={{
                border: "1px solid rgba(148, 163, 184, 0.25)",
                background: "rgba(15, 23, 42, 0.8)",
                color: copied ? "#4ade80" : "#cbd5e1",
                borderRadius: 999,
                width: 44,
                height: 44,
                fontSize: 20
              }}
              title={copied ? "Copied!" : "Copy code"}
            >
              {copied ? "OK" : "Copy"}
            </button>
          </div>
          <div style={{ marginTop: 10, fontSize: 13, color: "#64748B", lineHeight: 1.7 }}>
            Share this code with your friend. They'll enter it on the Start Online Session screen to join your game.
            <br />
            This code expires when the game ends or you leave.
          </div>
        </div>

        <div style={{ height: 40 }} />

        <div style={{ display: "grid", justifyItems: "center", gap: 18 }}>
          <div
            style={{
              width: 88,
              height: 88,
              borderRadius: "50%",
              border: "2px solid rgba(0, 200, 83, 0.32)",
              display: "grid",
              placeItems: "center",
              boxShadow: "0 0 0 14px rgba(0, 200, 83, 0.06)"
            }}
          >
            <div style={{ fontSize: 28 }}>P2</div>
          </div>

          {!waitingFlash ? (
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc" }}>
                {countdown === null ? "Waiting for Player 2..." : "Starting game..."}
              </div>
              {countdown !== null && (
                <div style={{ marginTop: 18, fontSize: 52, fontWeight: 900, color: "#00C853" }}>
                  {countdown > 0 ? countdown : "GO"}
                </div>
              )}
              {status !== "open" && countdown === null ? (
                <div style={{ marginTop: 12, color: "#94A3B8", fontSize: 14 }}>Connecting to session...</div>
              ) : null}
            </div>
          ) : (
            <div style={{ fontSize: 28, fontWeight: 800, color: "#4ade80" }}>Player 2 Connected!</div>
          )}
        </div>

        <div style={{ minHeight: 20, textAlign: "center", color: "#f87171" }}>{error}</div>
      </div>
    </div>
  );
}
