import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";

import type { ChoiceType, GameState, Zone } from "../game/types";
import { getSkyColors } from "../utils/carbonGradient";
import HUD from "./HUD";
import CarbonMeter from "./CarbonMeter";
import CardPanel from "./CardPanel";
import EndScreen from "./EndScreen";

interface GameBoardProps {
  state: GameState;
  canPlay: boolean;
  currentBudget: number;
  disabledMessage?: string | null;
  onChoice: (choice: ChoiceType) => void;
  onPlayAgain: () => void;
  onQuit: () => void;
  showBankruptcyOverlay?: boolean;
  onDismissBankruptcyOverlay?: () => void;
}

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  maxLife: number;
  size: number;
  color: string;
  kind: "leaf" | "smoke";
}

const zoneCenters: Record<Zone, { x: number; y: number }> = {
  transport: { x: 150, y: 440 },
  energy: { x: 360, y: 420 },
  waste: { x: 570, y: 450 },
  greenspace: { x: 760, y: 445 }
};

const zoneBuildings: Record<Zone, Array<{ x: number; y: number; width: number; height: number }>> = {
  transport: [
    { x: 48, y: 244, width: 36, height: 270 },
    { x: 92, y: 318, width: 84, height: 196 },
    { x: 150, y: 380, width: 48, height: 134 }
  ],
  energy: [
    { x: 252, y: 266, width: 40, height: 248 },
    { x: 302, y: 324, width: 90, height: 190 },
    { x: 364, y: 368, width: 46, height: 146 }
  ],
  waste: [
    { x: 454, y: 336, width: 78, height: 178 },
    { x: 520, y: 272, width: 40, height: 242 },
    { x: 574, y: 388, width: 52, height: 126 }
  ],
  greenspace: [
    { x: 660, y: 290, width: 38, height: 224 },
    { x: 708, y: 344, width: 84, height: 170 },
    { x: 766, y: 388, width: 46, height: 126 }
  ]
};

function scoreColor(score: number): string {
  const amount = Math.max(-6, Math.min(6, score));
  if (amount >= 0) {
    const t = amount / 6;
    return `rgb(${Math.round(122 - 88 * t)}, ${Math.round(130 + 88 * t)}, ${Math.round(144 - 24 * t)})`;
  }
  const t = Math.abs(amount) / 6;
  return `rgb(${Math.round(122 + 120 * t)}, ${Math.round(130 - 60 * t)}, ${Math.round(144 - 70 * t)})`;
}

export default function GameBoard({
  state,
  canPlay,
  currentBudget,
  disabledMessage,
  onChoice,
  onPlayAgain,
  onQuit,
  showBankruptcyOverlay = false,
  onDismissBankruptcyOverlay
}: GameBoardProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const outerRef = useRef<HTMLDivElement | null>(null);
  const stateRef = useRef(state);
  const lastMoveRef = useRef<number | null>(state.lastMove?.timestamp ?? null);
  const particlesRef = useRef<Particle[]>([]);
  const shakeUntilRef = useRef(0);
  const displayCarbonRef = useRef(state.carbonLevel);
  const scaleRef = useRef(1);
  const [scale, setScale] = useState(1);

  const stars = useMemo(
    () =>
      Array.from({ length: 60 }, (_, index) => ({
        x: 22 + ((index * 119) % 860),
        y: 28 + ((index * 53) % 210),
        size: 1 + (index % 2),
        offset: index * 0.35
      })),
    []
  );

  stateRef.current = state;

  useLayoutEffect(() => {
    const resize = () => {
      const width = Math.min(window.innerWidth - 32, 1280);
      const nextScale = width / 1280;
      scaleRef.current = nextScale;
      setScale(nextScale);
    };
    resize();
    window.addEventListener("resize", resize);
    return () => window.removeEventListener("resize", resize);
  }, []);

  useEffect(() => {
    const moveTimestamp = state.lastMove?.timestamp ?? null;
    if (moveTimestamp && moveTimestamp !== lastMoveRef.current && state.lastMove) {
      lastMoveRef.current = moveTimestamp;
      const center = zoneCenters[state.lastMove.zone];
      const isEco = state.lastMove.choice === "eco";
      for (let index = 0; index < 18; index += 1) {
        const angle = isEco ? Math.PI + (index / 18) * Math.PI : Math.PI + ((index * 0.8) / 18) * Math.PI;
        const speed = isEco ? 32 + index * 2 : 24 + index * 1.6;
        particlesRef.current.push({
          x: center.x,
          y: center.y,
          vx: Math.cos(angle) * speed,
          vy: Math.sin(angle) * speed,
          life: isEco ? 1.2 : 1.4,
          maxLife: isEco ? 1.2 : 1.4,
          size: isEco ? 6 + (index % 3) : 8 + (index % 4),
          color: isEco ? "#22c55e" : "#94a3b8",
          kind: isEco ? "leaf" : "smoke"
        });
      }
      if (state.lastMove.choice === "quick" || state.carbonLevel >= 80) {
        shakeUntilRef.current = performance.now() + 600;
      }
    }
  }, [state.carbonLevel, state.lastMove]);

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
    let lastFrame = performance.now();

    const draw = (now: number) => {
      const dt = Math.min(0.033, (now - lastFrame) / 1000);
      lastFrame = now;
      const currentState = stateRef.current;
      displayCarbonRef.current += (currentState.carbonLevel - displayCarbonRef.current) * Math.min(1, dt * 6);

      context.clearRect(0, 0, 1280, 720);
      context.fillStyle = "#0d1117";
      context.fillRect(0, 0, 1280, 720);

      const shake = now < shakeUntilRef.current ? 4 : 0;
      const shakeX = shake > 0 ? Math.sin(now / 24) * shake : 0;
      const shakeY = shake > 0 ? Math.cos(now / 28) * shake * 0.6 : 0;

      context.save();
      context.translate(shakeX, shakeY);
      drawScene(context, currentState, displayCarbonRef.current, particlesRef.current, stars, now, dt);
      context.restore();

      frameId = window.requestAnimationFrame(draw);
    };

    frameId = window.requestAnimationFrame(draw);
    return () => window.cancelAnimationFrame(frameId);
  }, [stars]);

  useEffect(() => {
    const listener = (event: KeyboardEvent) => {
      if (event.code === "Space" && showBankruptcyOverlay) {
        event.preventDefault();
        onDismissBankruptcyOverlay?.();
      }
    };
    window.addEventListener("keydown", listener);
    return () => window.removeEventListener("keydown", listener);
  }, [onDismissBankruptcyOverlay, showBankruptcyOverlay]);

  return (
    <div className="page-center" style={{ alignItems: "flex-start", paddingTop: 24, paddingBottom: 24 }}>
      <div
        ref={outerRef}
        style={{
          width: "min(calc(100vw - 32px), 1280px)",
          height: 720 * scale,
          position: "relative"
        }}
      >
        <div
          style={{
            width: 1280,
            height: 720,
            position: "absolute",
            inset: 0,
            transform: `scale(${scale})`,
            transformOrigin: "top left"
          }}
        >
          <canvas ref={canvasRef} width={1280} height={720} style={{ position: "absolute", inset: 0, width: 1280, height: 720 }} />
          <HUD state={state} />
          <CarbonMeter value={state.carbonLevel} />
          <CardPanel card={state.currentCard} currentBudget={currentBudget} canPlay={canPlay && !state.gameOver} disabledMessage={disabledMessage} onChoice={onChoice} />

          {showBankruptcyOverlay ? (
            <div
              style={{
                position: "absolute",
                inset: 0,
                background: "rgba(0,0,0,0.72)",
                display: "grid",
                placeItems: "center"
              }}
            >
              <div
                style={{
                  width: 800,
                  height: 320,
                  borderRadius: 20,
                  background: "#1a0000",
                  border: "3px solid #ef4444",
                  display: "grid",
                  placeItems: "center",
                  textAlign: "center",
                  padding: 24
                }}
              >
                <div style={{ fontSize: 64, fontWeight: 900, color: "#ef4444" }}>BANKRUPT!</div>
                <div style={{ fontSize: 24, color: "#fca5a5" }}>{state.currentPlayer === 1 ? state.player1.name : state.player2.name} has run out of money!</div>
                <div style={{ fontSize: 18, color: "#94a3b8" }}>The city cannot sustain further investment.</div>
                <div style={{ fontSize: 16, color: "#64748b" }}>Press SPACE to see results</div>
              </div>
            </div>
          ) : null}

          {state.gameOver && (!showBankruptcyOverlay || state.gameOverReason !== "bankruptcy") ? (
            <EndScreen state={state} onPlayAgain={onPlayAgain} onQuit={onQuit} />
          ) : null}
        </div>
      </div>
    </div>
  );
}

function drawScene(
  context: CanvasRenderingContext2D,
  state: GameState,
  carbonLevel: number,
  particles: Particle[],
  stars: Array<{ x: number; y: number; size: number; offset: number }>,
  now: number,
  dt: number
) {
  const [skyTop, skyMid, skyBottom] = getSkyColors(carbonLevel);
  const gradient = context.createLinearGradient(0, 90, 0, 630);
  gradient.addColorStop(0, skyTop);
  gradient.addColorStop(0.65, skyMid);
  gradient.addColorStop(1, skyBottom);
  context.fillStyle = gradient;
  context.fillRect(0, 90, 900, 630);

  context.fillStyle = "#111827";
  context.fillRect(900, 90, 380, 630);
  context.strokeStyle = "rgba(255,255,255,0.12)";
  context.beginPath();
  context.moveTo(908, 90);
  context.lineTo(908, 720);
  context.stroke();

  stars.forEach((star) => {
    const alpha = 0.35 + ((Math.sin(now / 800 + star.offset) + 1) / 2) * 0.65;
    context.fillStyle = `rgba(255,255,255,${alpha})`;
    context.beginPath();
    context.arc(star.x, star.y + 100, star.size, 0, Math.PI * 2);
    context.fill();
  });

  context.fillStyle = "rgba(255, 190, 150, 0.75)";
  context.beginPath();
  context.arc(740, 180, 34, 0, Math.PI * 2);
  context.fill();

  context.fillStyle = "#1f2937";
  context.beginPath();
  context.moveTo(0, 430);
  context.lineTo(160, 320);
  context.lineTo(300, 380);
  context.lineTo(460, 300);
  context.lineTo(640, 368);
  context.lineTo(820, 310);
  context.lineTo(900, 370);
  context.lineTo(900, 720);
  context.lineTo(0, 720);
  context.closePath();
  context.fill();

  context.fillStyle = "#111827";
  for (let x = 24; x < 900; x += 82) {
    const height = 80 + ((x / 18) % 5) * 18;
    context.fillRect(x, 460 - height, 32 + ((x / 24) % 3) * 10, height);
  }

  (Object.keys(zoneBuildings) as Zone[]).forEach((zone) => {
    const color = scoreColor(state.zoneScores[zone]);
    zoneBuildings[zone].forEach((building) => {
      context.fillStyle = color;
      context.fillRect(building.x, building.y, building.width, building.height);
      context.strokeStyle = "rgba(9, 14, 24, 0.9)";
      context.strokeRect(building.x, building.y, building.width, building.height);
      context.fillStyle = "rgba(255, 220, 120, 0.75)";
      for (let row = building.y + 12; row < building.y + building.height - 12; row += 18) {
        for (let col = building.x + 8; col < building.x + building.width - 8; col += 16) {
          context.fillRect(col, row, 6, 9);
        }
      }
    });
  });

  context.fillStyle = "#374151";
  context.fillRect(0, 620, 900, 100);
  context.fillStyle = "#111827";
  context.fillRect(0, 644, 900, 76);
  context.strokeStyle = "#94a3b8";
  context.beginPath();
  context.moveTo(0, 620);
  context.lineTo(900, 620);
  context.stroke();
  context.fillStyle = "#e5e7eb";
  for (let x = 0; x < 900; x += 40) {
    context.fillRect(x, 680, 20, 4);
  }

  for (const x of [52, 210, 372, 528, 690]) {
    context.fillStyle = "#8b5a2b";
    context.fillRect(x, 608, 6, 18);
    context.fillStyle = "#22c55e";
    context.beginPath();
    context.arc(x + 3, 602, 12, 0, Math.PI * 2);
    context.fill();
  }

  for (const x of [306, 358]) {
    context.strokeStyle = "#e2e8f0";
    context.lineWidth = 2;
    context.beginPath();
    context.moveTo(x, 610);
    context.lineTo(x, 568);
    context.stroke();
    const rotation = now / 500;
    for (const offset of [0, Math.PI * 0.66, Math.PI * 1.33]) {
      context.beginPath();
      context.moveTo(x, 568);
      context.lineTo(x + Math.cos(rotation + offset) * 16, 568 + Math.sin(rotation + offset) * 16);
      context.stroke();
    }
  }

  context.fillStyle = "#94a3b8";
  context.font = "14px Arial";
  context.textAlign = "center";
  context.fillText("Transport", 112, 708);
  context.fillText("Energy", 312, 708);
  context.fillText("Waste", 512, 708);
  context.fillText("Green Space", 712, 708);

  const turnColor = state.currentPlayer === 1 ? "#00ff88" : "#a78bfa";
  const turnText = `${state.currentPlayer === 1 ? "Player 1" : "Player 2"}'s Turn`;
  context.font = "bold 42px Arial";
  const textWidth = context.measureText(turnText).width;
  context.fillStyle = "rgba(0,0,0,0.42)";
  roundRect(context, 450 - textWidth / 2 - 20, 174, textWidth + 40, 52, 26);
  context.fill();
  const pulse = Math.sin(now / 400);
  const alpha = 0.7 + ((pulse + 1) / 2) * 0.3;
  context.fillStyle = turnColor;
  context.globalAlpha = alpha;
  context.beginPath();
  context.arc(430 - textWidth / 2, 200, 10 + pulse * 2, 0, Math.PI * 2);
  context.fill();
  context.fillText(turnText, 450, 212);
  context.globalAlpha = 1;

  for (let index = particles.length - 1; index >= 0; index -= 1) {
    const particle = particles[index];
    particle.life -= dt;
    if (particle.life <= 0) {
      particles.splice(index, 1);
      continue;
    }
    particle.x += particle.vx * dt;
    particle.y += particle.vy * dt;
    particle.vy += particle.kind === "leaf" ? 12 * dt : -6 * dt;
    const alphaParticle = particle.life / particle.maxLife;
    context.globalAlpha = alphaParticle;
    context.fillStyle = particle.color;
    context.beginPath();
    context.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
    context.fill();
    context.globalAlpha = 1;
  }
}

function roundRect(context: CanvasRenderingContext2D, x: number, y: number, width: number, height: number, radius: number) {
  context.beginPath();
  context.moveTo(x + radius, y);
  context.arcTo(x + width, y, x + width, y + height, radius);
  context.arcTo(x + width, y + height, x, y + height, radius);
  context.arcTo(x, y + height, x, y, radius);
  context.arcTo(x, y, x + width, y, radius);
  context.closePath();
}
