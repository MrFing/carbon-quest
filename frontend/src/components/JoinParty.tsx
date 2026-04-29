import { useMemo } from "react";
import type { CSSProperties } from "react";

interface JoinPartyProps {
  code: string;
  loading: boolean;
  error: string | null;
  onCodeChange: (value: string) => void;
  onJoin: () => void;
}

export default function JoinParty({ code, loading, error, onCodeChange, onJoin }: JoinPartyProps) {
  const inputStyle = useMemo<CSSProperties>(
    () => ({
      width: 400,
      height: 64,
      borderRadius: 18,
      border: `2px solid ${error ? "#ef4444" : "#00C853"}`,
      background: "#161B22",
      color: "#f8fafc",
      fontSize: 24,
      textAlign: "center",
      letterSpacing: 8,
      outline: "none",
      boxShadow: error ? "0 0 0 4px rgba(239,68,68,0.12)" : "0 0 0 0 rgba(0,200,83,0)"
    }),
    [error]
  );

  return (
    <div style={{ display: "grid", gap: 16, justifyItems: "center" }}>
      <div style={{ fontSize: 28, fontWeight: 800, color: "#f8fafc" }}>Enter Party Code</div>
      <input
        value={code}
        onChange={(event) =>
          onCodeChange(
            event.target.value
              .toUpperCase()
              .replace(/[^A-Z0-9]/g, "")
              .slice(0, 6)
          )
        }
        placeholder="XXXXXX"
        style={inputStyle}
      />
      <button
        onClick={onJoin}
        disabled={loading}
        style={{
          width: 400,
          height: 58,
          borderRadius: 999,
          border: "none",
          background: "#00C853",
          color: "#ffffff",
          fontWeight: 800,
          fontSize: 18,
          boxShadow: "0 18px 40px rgba(0, 200, 83, 0.24)",
          opacity: loading ? 0.7 : 1
        }}
      >
        {loading ? "Connecting..." : "Join Game"}
      </button>
      <div
        style={{
          minHeight: 20,
          color: "#f87171",
          fontSize: 14,
          fontWeight: 700,
          transform: error ? "translateX(0)" : "translateX(0)"
        }}
      >
        {error}
      </div>
    </div>
  );
}
