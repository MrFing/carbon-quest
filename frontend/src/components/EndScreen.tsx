import { getEndSummary, getPlayerRating, getWinnerSummary } from "../game/gameLogic";
import type { GameState } from "../game/types";
import { formatBudget, getBudgetColor } from "../utils/formatBudget";

interface EndScreenProps {
  state: GameState;
  onPlayAgain: () => void;
  onQuit: () => void;
}

export default function EndScreen({ state, onPlayAgain, onQuit }: EndScreenProps) {
  const summary = getEndSummary(state);
  const winner = getWinnerSummary(state);

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        background: "rgba(3, 7, 18, 0.88)",
        display: "grid",
        placeItems: "center"
      }}
    >
      <div
        className="glass-panel"
        style={{
          width: 1140,
          minHeight: 668,
          borderRadius: 26,
          padding: "34px 40px",
          border: `${state.gameOverReason === "bankruptcy" ? 3 : 2}px solid ${state.gameOverReason === "bankruptcy" ? "#ef4444" : summary.color}`,
          position: "relative"
        }}
      >
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: state.gameOverReason === "bankruptcy" ? 52 : 44, fontWeight: 900, color: summary.color }}>{summary.title}</div>
          <div style={{ marginTop: 10, color: "#f8fafc", fontSize: 20 }}>{summary.subtitle}</div>
        </div>

        <div
          style={{
            width: 700,
            height: 100,
            margin: "40px auto 0",
            borderRadius: 16,
            background: winner.winner === "draw" ? "#1e293b" : state.gameOverReason === "bankruptcy" ? "#14532d" : "linear-gradient(135deg, #166534, #15803d)",
            border: `2px solid ${winner.winner === "draw" ? "#94a3b8" : state.gameOverReason === "bankruptcy" ? "#22c55e" : "#4ade80"}`,
            display: "grid",
            placeItems: "center",
            textAlign: "center"
          }}
        >
          {winner.winner === "draw" ? (
            <>
              <div style={{ fontSize: 32, fontWeight: 900, color: "#e2e8f0" }}>🤝 It&apos;s a Draw!</div>
              <div style={{ marginTop: -10, fontSize: 16, color: "#94a3b8" }}>Both players performed equally</div>
            </>
          ) : (
            <>
              <div style={{ fontSize: state.gameOverReason === "bankruptcy" ? 36 : 32, fontWeight: 900, color: "#ffffff" }}>🏆 {winner.winnerName} Wins!</div>
              <div style={{ marginTop: -8, fontSize: state.gameOverReason === "bankruptcy" ? 20 : 16, color: state.gameOverReason === "bankruptcy" ? "#fca5a5" : "#bbf7d0" }}>
                {state.gameOverReason === "bankruptcy" ? `${winner.loserName} ran out of money!` : `${winner.winnerName} ${winner.reason}`}
              </div>
            </>
          )}
        </div>

        <div style={{ marginTop: 38, display: "flex", justifyContent: "space-between" }}>
          {[state.player1, state.player2].map((player, index) => {
            const winnerIndex = winner.winner === "draw" ? null : winner.winner;
            const isWinner = winnerIndex === index + 1;
            const isBankrupt = player.bankrupt;
            const borderColor = winner.winner === "draw" ? "#94a3b8" : isWinner ? "#22c55e" : "#ef4444";
            const rating = getPlayerRating(player);
            const cardBackground = isBankrupt ? "rgba(38, 0, 0, 0.95)" : "#0f172a";
            return (
              <div key={player.name} style={{ width: 420 }}>
                <div
                  style={{
                    height: 180,
                    borderRadius: 12,
                    border: `2px solid ${borderColor}`,
                    background: cardBackground,
                    padding: 20,
                    position: "relative",
                    boxShadow: isWinner ? `0 0 0 10px ${borderColor}18, 0 0 0 20px ${borderColor}10` : "none"
                  }}
                >
                  <div style={{ fontSize: 24, fontWeight: 900, color: "#ffffff" }}>{player.name}</div>
                  {isBankrupt ? (
                    <div
                      style={{
                        position: "absolute",
                        top: 16,
                        right: 16,
                        padding: "4px 10px",
                        borderRadius: 999,
                        background: "#7f1d1d",
                        color: "#fecaca",
                        fontSize: 12,
                        fontWeight: 800
                      }}
                    >
                      💸 BANKRUPT
                    </div>
                  ) : null}
                  <div style={{ marginTop: 18, display: "grid", gap: 10, color: "#cbd5e1", fontSize: 16 }}>
                    <div>Total decisions: {player.decisions}</div>
                    <div style={{ color: "#4ade80" }}>Eco choices: {player.ecoChoices}</div>
                    <div style={{ color: "#f87171" }}>Quick choices: {player.quickChoices}</div>
                    <div style={{ color: player.carbonContribution <= 0 ? "#4ade80" : "#f87171" }}>Carbon Impact: {player.carbonContribution >= 0 ? `+${player.carbonContribution}` : player.carbonContribution}</div>
                    <div style={{ color: isBankrupt ? "#ef4444" : getBudgetColor(player.budget) }}>
                      {isBankrupt
                        ? "$0 — Out of funds"
                        : state.gameOverReason === "bankruptcy" && isWinner
                          ? `${formatBudget(player.budget)} remaining`
                          : `Final Budget: ${formatBudget(player.budget)}`}
                    </div>
                  </div>
                </div>
                <div style={{ marginTop: 18, textAlign: "center", fontSize: 18, fontWeight: 700, color: rating.color }}>{rating.label}</div>
              </div>
            );
          })}
        </div>

        <div style={{ marginTop: 54, display: "flex", justifyContent: "center", gap: 40 }}>
          <button
            onClick={onPlayAgain}
            style={{
              width: 160,
              height: 48,
              borderRadius: 999,
              border: "none",
              background: "#16a34a",
              color: "#ffffff",
              fontSize: 18,
              fontWeight: 800
            }}
          >
            Play Again
          </button>
          <button
            onClick={onQuit}
            style={{
              width: 160,
              height: 48,
              borderRadius: 999,
              border: "none",
              background: "#b91c1c",
              color: "#ffffff",
              fontSize: 18,
              fontWeight: 800
            }}
          >
            Quit
          </button>
        </div>
      </div>
    </div>
  );
}
