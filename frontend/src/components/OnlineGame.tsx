import { useState } from "react";
import { useNavigate } from "react-router-dom";

import JoinParty from "./JoinParty";
import { getBackendHttpBase } from "../hooks/useWebSocket";
import type { PartyResponse } from "../game/types";

function sleep(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: string; message?: string };
    if (typeof payload.detail === "string" && payload.detail.trim()) {
      return payload.detail;
    }
    if (typeof payload.message === "string" && payload.message.trim()) {
      return payload.message;
    }
  } catch {
    // Ignore JSON parsing issues and fall back to the HTTP status text.
  }

  return response.statusText || "Request failed.";
}

async function requestJsonWithRetry<T>(url: string, init?: RequestInit): Promise<T> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt < 3; attempt += 1) {
    try {
      const response = await fetch(url, init);
      if (response.ok) {
        return (await response.json()) as T;
      }

      const message = await readErrorMessage(response);
      const retryable = response.status >= 500 || response.status === 429;
      if (!retryable) {
        throw new Error(message);
      }
      lastError = new Error(message || "The server is temporarily unavailable.");
    } catch (error) {
      lastError = error instanceof Error ? error : new Error("Network request failed.");
    }

    if (attempt < 2) {
      await sleep(700 * (attempt + 1));
    }
  }

  throw lastError ?? new Error("Request failed.");
}

export default function OnlineGame() {
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const createParty = async () => {
    setError(null);
    setLoading(true);
    try {
      const payload = await requestJsonWithRetry<PartyResponse>(`${getBackendHttpBase()}/api/create-party`, {
        method: "POST"
      });
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
    const normalizedCode = code.trim().toUpperCase();
    if (normalizedCode.length !== 6) {
      setError("Party codes must be 6 characters.");
      return;
    }

    setLoading(true);
    try {
      const payload = await requestJsonWithRetry<PartyResponse>(`${getBackendHttpBase()}/api/party/${normalizedCode}`);
      sessionStorage.setItem(`carbon-quest-party:${payload.code}`, payload.sessionId);
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

        <div style={{ color: "#64748B", fontWeight: 700 }}>- or -</div>

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
