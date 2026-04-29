import { formatBudget, getBudgetColor } from "../utils/formatBudget";
import type { GameState } from "../game/types";

interface HUDProps {
  state: GameState;
}

export default function HUD({ state }: HUDProps) {
  const players = [
    { key: 1 as const, data: state.player1, accent: "#00ff88", inactive: "#334155" },
    { key: 2 as const, data: state.player2, accent: "#a78bfa", inactive: "#334155" }
  ];

  return (
    <div style={{ position: "absolute", inset: 0, pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width: 1280,
          height: 90,
          background: "rgba(9, 14, 24, 0.84)",
          borderBottom: "1px solid rgba(148, 163, 184, 0.18)"
        }}
      />

      {players.map(({ key, data, accent, inactive }) => {
        const isActive = state.currentPlayer === key;
        const left = key === 1 ? 10 : 1280 - 10 - Math.max(210, 120 + Math.max(data.name.length * 8, formatBudget(data.budget).length * 8));
        const width = Math.max(210, 120 + Math.max(data.name.length * 8, formatBudget(data.budget).length * 8));
        const warningText = data.budget < 5_000 ? "⚠ Critical Funds!" : data.budget <= 15_000 ? "⚠ Low Funds" : null;
        return (
          <div key={key}>
            <div
              style={{
                position: "absolute",
                left,
                top: 12,
                width,
                height: 48,
                borderRadius: 999,
                background: "rgba(22, 27, 34, 0.96)",
                border: `${isActive ? 3 : 1}px solid ${isActive ? accent : inactive}`,
                boxShadow: isActive ? `0 0 0 10px ${accent}22` : "none",
                display: "grid",
                alignContent: "center",
                paddingLeft: 32
              }}
            >
              <div style={{ position: "absolute", left: 14, top: 16, width: 10, height: 10, borderRadius: "50%", background: isActive ? accent : "#4b5563" }} />
              <div style={{ fontSize: 16, fontWeight: 800, color: "#f8fafc", lineHeight: 1.1 }}>{data.name}</div>
              <div style={{ fontSize: 14, color: getBudgetColor(data.budget), lineHeight: 1.1 }}>{formatBudget(data.budget)}</div>
            </div>
            {warningText ? (
              <div
                style={{
                  position: "absolute",
                  left: left + width / 2,
                  top: 64,
                  transform: "translateX(-50%)",
                  fontSize: 12,
                  fontWeight: 800,
                  color: getBudgetColor(data.budget)
                }}
              >
                {warningText}
              </div>
            ) : null}
          </div>
        );
      })}

      <div style={{ position: "absolute", left: 640, top: 12, transform: "translateX(-50%)", textAlign: "center" }}>
        <div style={{ fontSize: 24, fontWeight: 900, color: "#f8fafc" }}>Round {state.round} / 15</div>
        <div style={{ marginTop: 12, fontSize: 12, fontWeight: 800, color: "#94a3b8" }}>CITY HEALTH</div>
        <div style={{ marginTop: 6, width: 400, height: 14, borderRadius: 999, overflow: "hidden", background: "#0f172a", border: "1px solid rgba(255,255,255,0.22)" }}>
          <div
            style={{
              width: `${state.cityHealth}%`,
              height: "100%",
              background: state.cityHealth >= 60 ? "#22c55e" : state.cityHealth >= 30 ? "#fbbf24" : "#ef4444",
              transition: "width 600ms ease"
            }}
          />
        </div>
      </div>
    </div>
  );
}
