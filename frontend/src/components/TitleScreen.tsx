import { useEffect, useMemo, useRef } from "react";
import type { CSSProperties } from "react";
import { useNavigate } from "react-router-dom";

export default function TitleScreen() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const navigate = useNavigate();
  const stars = useMemo(
    () =>
      Array.from({ length: 90 }, (_, index) => ({
        x: (index * 137) % 1280,
        y: 40 + ((index * 91) % 320),
        size: 1 + (index % 2),
        twinkleOffset: index * 0.5
      })),
    []
  );

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return undefined;
    }

    const context = canvas.getContext("2d");
    if (!context) {
      return undefined;
    }

    let frameId = 0;
    let start = performance.now();

    const draw = (time: number) => {
      const elapsed = (time - start) / 1000;
      context.clearRect(0, 0, canvas.width, canvas.height);

      const gradient = context.createLinearGradient(0, 0, 0, canvas.height);
      gradient.addColorStop(0, "#0f172a");
      gradient.addColorStop(0.6, "#111827");
      gradient.addColorStop(1, "#1f2937");
      context.fillStyle = gradient;
      context.fillRect(0, 0, canvas.width, canvas.height);

      for (const star of stars) {
        const alpha = 0.35 + ((Math.sin(elapsed * 1.6 + star.twinkleOffset) + 1) / 2) * 0.65;
        context.fillStyle = `rgba(255,255,255,${alpha})`;
        context.beginPath();
        context.arc(star.x, star.y, star.size, 0, Math.PI * 2);
        context.fill();
      }

      const bands = [
        { y: 560, color: "#0b1220", speed: 18, height: [70, 110, 90, 130] },
        { y: 605, color: "#111827", speed: 32, height: [120, 80, 150, 95] }
      ];

      bands.forEach((band, bandIndex) => {
        const offset = (elapsed * band.speed) % 240;
        for (let index = -2; index < 12; index += 1) {
          let cursor = index * 180 - offset;
          band.height.forEach((height, hIndex) => {
            context.fillStyle = band.color;
            context.fillRect(cursor, band.y - height - (bandIndex * 18), 34 + hIndex * 18, height);
            cursor += 48 + hIndex * 14;
          });
        }
      });

      context.fillStyle = "#111827";
      context.fillRect(0, 640, canvas.width, 80);

      frameId = window.requestAnimationFrame(draw);
    };

    frameId = window.requestAnimationFrame(draw);
    return () => window.cancelAnimationFrame(frameId);
  }, [stars]);

  const primaryButtonStyle: CSSProperties = {
    width: 280,
    padding: "16px 24px",
    borderRadius: 999,
    border: "none",
    background: "#00C853",
    color: "#ffffff",
    fontSize: 18,
    fontWeight: 700,
    boxShadow: "0 16px 40px rgba(0, 200, 83, 0.28)",
    transition: "transform 180ms ease, filter 180ms ease"
  };

  const secondaryButtonStyle: CSSProperties = {
    ...primaryButtonStyle,
    background: "transparent",
    color: "#00C853",
    border: "2px solid #00C853",
    boxShadow: "none"
  };

  return (
    <div className="page-center">
      <div
        className="glass-panel"
        style={{
          width: "min(100%, 1180px)",
          minHeight: 680,
          borderRadius: 32,
          overflow: "hidden",
          position: "relative"
        }}
      >
        <canvas
          ref={canvasRef}
          width={1280}
          height={720}
          style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}
        />
        <div
          style={{
            position: "relative",
            zIndex: 1,
            minHeight: 680,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "48px 32px"
          }}
        >
          <div style={{ textAlign: "center", maxWidth: 760 }}>
            <div style={{ fontSize: 68, fontWeight: 800, color: "#00C853", letterSpacing: 2 }}>
              CARBON QUEST
            </div>
            <div style={{ marginTop: 12, fontSize: 28, color: "#f8fafc", fontWeight: 700 }}>
              City Builder Challenge
            </div>
            <div style={{ marginTop: 14, fontSize: 16, color: "#94A3B8" }}>
              Build a thriving city. Don&apos;t tip the Carbon Meter.
            </div>

            <div style={{ marginTop: 34, display: "flex", justifyContent: "center", gap: 16, flexWrap: "wrap" }}>
              <button
                style={primaryButtonStyle}
                onMouseEnter={(event) => {
                  event.currentTarget.style.filter = "brightness(1.08)";
                  event.currentTarget.style.transform = "scale(1.03)";
                }}
                onMouseLeave={(event) => {
                  event.currentTarget.style.filter = "brightness(1)";
                  event.currentTarget.style.transform = "scale(1)";
                }}
                onClick={() => navigate("/local")}
              >
                🏙 Start Local Game
              </button>
              <button
                style={secondaryButtonStyle}
                onMouseEnter={(event) => {
                  event.currentTarget.style.background = "#00C853";
                  event.currentTarget.style.color = "#ffffff";
                  event.currentTarget.style.transform = "scale(1.03)";
                }}
                onMouseLeave={(event) => {
                  event.currentTarget.style.background = "transparent";
                  event.currentTarget.style.color = "#00C853";
                  event.currentTarget.style.transform = "scale(1)";
                }}
                onClick={() => navigate("/online")}
              >
                🌐 Start Online Session
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
