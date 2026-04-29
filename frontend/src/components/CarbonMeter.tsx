import { useEffect, useState } from "react";

interface CarbonMeterProps {
  value: number;
}

export default function CarbonMeter({ value }: CarbonMeterProps) {
  const [displayValue, setDisplayValue] = useState(value);

  useEffect(() => {
    let frameId = 0;
    let current = displayValue;

    const animate = () => {
      current += (value - current) * 0.12;
      if (Math.abs(value - current) < 0.15) {
        current = value;
      }
      setDisplayValue(current);
      if (current !== value) {
        frameId = window.requestAnimationFrame(animate);
      }
    };

    frameId = window.requestAnimationFrame(animate);
    return () => window.cancelAnimationFrame(frameId);
  }, [displayValue, value]);

  const fillHeight = Math.max(0, Math.min(216, (displayValue / 100) * 216));

  return (
    <div
      style={{
        position: "absolute",
        left: 910,
        top: 95,
        width: 370,
        height: 320,
        background: "#101826",
        borderRadius: 18,
        border: "1px solid rgba(255,255,255,0.08)"
      }}
    >
      <div style={{ position: "absolute", left: 1095, top: 108, transform: "translateX(-50%)", color: "#aaaacc", fontSize: 15, fontWeight: 800 }}>
        CARBON LEVEL
      </div>
      <div
        style={{
          position: "absolute",
          left: 1035,
          top: 120,
          width: 120,
          height: 24,
          borderRadius: 12,
          background: "#1a1a3e",
          border: "2px solid #ffd700",
          display: "grid",
          placeItems: "center",
          color: "#ffd700",
          fontSize: 14
        }}
      >
        {Math.round(displayValue)}/100
      </div>
      <div
        style={{
          position: "absolute",
          left: 1010,
          top: 148,
          width: 60,
          height: 220,
          background: "#0d1b2a",
          borderRadius: 10,
          border: "2px solid #334466",
          overflow: "hidden"
        }}
      >
        <div
          style={{
            position: "absolute",
            left: 2,
            bottom: 2,
            width: 56,
            height: fillHeight,
            borderRadius: 8,
            background: "linear-gradient(180deg, #ff4444 0%, #ffd700 48%, #00ff88 100%)",
            transition: "height 600ms ease"
          }}
        />
      </div>

      {[0, 25, 50, 75, 100].map((tick) => {
        const y = 366 - (tick / 100) * 216;
        return (
          <div key={tick}>
            <div style={{ position: "absolute", left: 1072, top: y, width: 6, height: 1, background: "#445566" }} />
            <div style={{ position: "absolute", left: 1082, top: y - 8, color: "#8899aa", fontSize: 11 }}>{tick}</div>
          </div>
        );
      })}
    </div>
  );
}
