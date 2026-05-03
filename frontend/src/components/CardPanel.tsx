import { useEffect, useState } from "react";

import { formatBudget } from "../utils/formatBudget";
import type { ChoiceType, DecisionCard } from "../game/types";

interface CardPanelProps {
  card: DecisionCard;
  currentBudget: number;
  canPlay: boolean;
  disabledMessage?: string | null;
  onChoice: (choice: ChoiceType) => void;
}

const zoneColors: Record<DecisionCard["zone"], string> = {
  "Transport": "#1d4ed8",
  "Energy": "#ca8a04",
  "Waste": "#92400e",
  "Green Space": "#166534",
  "Consumption": "#f472b6",
  "Community": "#fb923c"
};

export default function CardPanel({ card, currentBudget, canPlay, disabledMessage, onChoice }: CardPanelProps) {
  const [slidIn, setSlidIn] = useState(false);

  useEffect(() => {
    setSlidIn(false);
    const frame = window.requestAnimationFrame(() => setSlidIn(true));
    return () => window.cancelAnimationFrame(frame);
  }, [card.id]);

  const renderChoice = (label: string, value: number, color: string, background: string) => (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        height: 20,
        padding: "0 8px",
        borderRadius: 999,
        background,
        color,
        fontSize: 12,
        fontWeight: 700
      }}
    >
      {label} {value >= 0 ? `+${value}` : value}
    </div>
  );

  return (
    <div
      style={{
        position: "absolute",
        left: 918,
        top: 415,
        width: 354,
        height: 300,
        background: "#111827",
        border: "1px solid #1e293b",
        borderRadius: 12,
        overflow: "hidden",
        transform: `translateX(${slidIn ? 0 : 40}px)`,
        opacity: slidIn ? 1 : 0,
        transition: "transform 360ms ease, opacity 360ms ease"
      }}
    >
      <div
        style={{
          height: 40,
          background: zoneColors[card.zone],
          color: "#ffffff",
          display: "flex",
          alignItems: "center",
          gap: 10,
          padding: "0 12px",
          fontSize: 16,
          fontWeight: 800
        }}
      >
        <div style={{ width: 20, height: 20, borderRadius: card.zone === "Energy" ? "50%" : 4, border: "2px solid rgba(15,23,42,0.9)" }} />
        {card.zone.toUpperCase()}
      </div>

      <div style={{ padding: "10px 10px 0" }}>
        <div style={{ fontSize: 17, fontWeight: 800, color: "#ffffff" }}>{card.title}</div>
        <div style={{ marginTop: 8, display: "flex", justifyContent: "space-between", fontSize: 12 }}>
          <span style={{ color: "#4ade80", fontWeight: 800 }}>ECO CHOICE: {formatBudget(card.ecoChoice.cost)}</span>
          <span style={{ color: "#fb923c", fontWeight: 800 }}>QUICK CHOICE: {formatBudget(card.quickChoice.cost)}</span>
        </div>
        <div style={{ marginTop: 6, fontSize: 12, color: "#94a3b8" }}>Budget Left: {formatBudget(currentBudget)}</div>
      </div>

      {[
        { key: "eco" as const, title: card.ecoChoice.label, choice: card.ecoChoice, top: 99, accent: "#22c55e" },
        { key: "quick" as const, title: card.quickChoice.label, choice: card.quickChoice, top: 175, accent: "#ef4444" }
      ].map((entry) => (
        <div
          key={entry.key}
          style={{
            position: "absolute",
            left: 8,
            top: entry.top,
            width: 338,
            height: 68,
            borderRadius: 8,
            background: "#0f172a"
          }}
        >
          <div style={{ position: "absolute", left: 0, top: 0, width: 4, height: 68, background: entry.accent, borderRadius: "8px 0 0 8px" }} />
          <div style={{ padding: "6px 12px" }}>
            <div style={{ fontSize: 15, fontWeight: 800, color: "#ffffff" }}>{entry.title}</div>
            <div style={{ marginTop: 12, display: "flex", gap: 6 }}>
              {renderChoice("Carbon", entry.choice.carbonDelta, "#22c55e", "#166534")}
              {renderChoice("Budget", -entry.choice.cost, "#fbbf24", "#78350f")}
              {renderChoice("Health", entry.choice.healthDelta, "#60a5fa", "#1e3a5f")}
            </div>
          </div>
        </div>
      ))}

      <div style={{ position: "absolute", left: 8, top: 251, display: "flex", gap: 8 }}>
        <button
          onClick={() => onChoice("eco")}
          disabled={!canPlay}
          style={{
            width: 164,
            height: 40,
            border: "none",
            borderRadius: 999,
            background: "#16a34a",
            color: "#ffffff",
            fontSize: 14,
            fontWeight: 800,
            opacity: canPlay ? 1 : 0.4
          }}
        >
          Eco Choice
        </button>
        <button
          onClick={() => onChoice("quick")}
          disabled={!canPlay}
          style={{
            width: 164,
            height: 40,
            border: "none",
            borderRadius: 999,
            background: "#b91c1c",
            color: "#ffffff",
            fontSize: 14,
            fontWeight: 800,
            opacity: canPlay ? 1 : 0.4
          }}
        >
          Quick Choice
        </button>
      </div>

      {!canPlay && disabledMessage ? (
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: "rgba(2, 6, 23, 0.76)",
            display: "grid",
            placeItems: "center",
            textAlign: "center",
            padding: 24,
            color: "#cbd5e1",
            fontWeight: 700
          }}
        >
          {disabledMessage}
        </div>
      ) : null}
    </div>
  );
}
