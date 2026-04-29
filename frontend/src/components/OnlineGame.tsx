import { useState } from "react";
import { useNavigate } from "react-router-dom";

import JoinParty from "./JoinParty";
import { getBackendHttpBase } from "../hooks/useWebSocket";
import type { PartyResponse } from "../game/types";

export default function OnlineGame() {
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const createParty = async () => {
    setError(null);
    setLoading(true);
    try {
      const response = await fetch(`${getBackendHttpBase()}/api/create-party`, {
        method: "POST"
      });
      if (!response.ok) {
        throw new Error("Unable to create a party right now.");
      }
      const payload = (await response.json()) as PartyResponse;
      sessionStorage.setItem(`carbon-quest-party:${payload.code}`, payload.sessionId);
      sessionStorage.setItem(`carbon-quest-player:${payload.sessionId}`, "1");
      navigate(`/party/${payload.code}`, { state: { sessionId: payload.sessionId, player: 1 } });
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to create a party.");
    } finally {
      setLoading(false);
    }
  };

  const joinParty = async () => {
    setError(null);
    if (code.trim().length !== 6) {
      setError("Party codes must be 6 characters.");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${getBackendHttpBase()}/api/party/${code.trim()}`);
      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || "Could not join that party.");
      }
      const payload = (await response.json()) as PartyResponse;
      sessionStorage.setItem(`carbon-quest-player:${payload.sessionId}`, "2");
      navigate(`/game/${payload.sessionId}`, { state: { player: 2, partyCode: payload.code } });
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to join the party.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-center">
      <div
        className="glass-panel"
        style={{
          width: "min(100%, 640px)",
          borderRadius: 28,
          padding: "56px 48px",
          display: "grid",
          gap: 28,
          justifyItems: "center"
        }}
      >
        <JoinParty code={code} loading={loading} error={error} onCodeChange={setCode} onJoin={joinParty} />

        <div style={{ color: "#64748B", fontWeight: 700 }}>— or —</div>

        <div style={{ display: "grid", gap: 16, justifyItems: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 800, color: "#f8fafc" }}>Create Party</div>
          <button
            onClick={createParty}
            disabled={loading}
            style={{
              width: 400,
              height: 58,
              borderRadius: 999,
              border: "2px solid #00C853",
              background: "transparent",
              color: "#00C853",
              fontWeight: 800,
              fontSize: 18
            }}
          >
            {loading ? "Preparing..." : "Create Party"}
          </button>
        </div>
      </div>
    </div>
  );
}
