import { useEffect, useLayoutEffect, useMemo, useRef, useState, type CSSProperties } from "react";

import type { ChoiceType, DecisionCard, GameState, PlayerState, Zone } from "../game/types";
import { RULES_TEXT, ZONE_COLORS } from "../game/cards";
import { calculateScores } from "../game/gameLogic";
import { formatBudget } from "../utils/formatBudget";

interface GameBoardProps {
  state: GameState;
  canPlay: boolean;
  disabledMessage?: string | null;
  onRoll: () => void;
  onChoice: (choice: ChoiceType) => void;
  onPlayAgain: () => void;
  onQuit: () => void;
}

const WIDTH = 1280;
const HEIGHT = 720;
const FONT_FAMILY = '"Segoe UI", Arial, sans-serif';
const BG = "#151923";
const PANEL = "#1f2937";
const PANEL_2 = "#111827";
const INK = "#080d18";
const WHITE = "#eef2ff";
const MUTED = "#94a3b8";
const GREEN = "#22c55e";
const RED = "#ef4444";
const YELLOW = "#facc15";
const BLUE = "#60a5fa";
const PURPLE = "#a78bfa";
const ORANGE = "#fb923c";

const BOARD_POSITIONS = buildBoardPositions();

function clamp(value: number, low: number, high: number) {
  return Math.max(low, Math.min(high, value));
}

export default function GameBoard({ state, canPlay, disabledMessage, onRoll, onChoice, onPlayAgain, onQuit }: GameBoardProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const stateRef = useRef(state);
  const [scale, setScale] = useState(1);
  const [showRules, setShowRules] = useState(false);

  stateRef.current = state;

  useLayoutEffect(() => {
    const resize = () => {
      const widthScale = Math.min((window.innerWidth - 32) / WIDTH, 1);
      const heightScale = Math.min((window.innerHeight - 32) / HEIGHT, 1);
      setScale(Math.max(0.5, Math.min(widthScale, heightScale)));
    };
    resize();
    window.addEventListener("resize", resize);
    return () => window.removeEventListener("resize", resize);
  }, []);

  useEffect(() => {
    const listener = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        if (showRules) {
          setShowRules(false);
        }
        return;
      }
      if (stateRef.current.gameOver) {
        return;
      }
      if ((event.key === "r" || event.key === "R") && canPlay && !stateRef.current.selectedCard && !stateRef.current.selectedEvent) {
        onRoll();
      }
      if (event.key === "1" && canPlay && (stateRef.current.selectedCard || stateRef.current.selectedEvent)) {
        onChoice("eco");
      }
      if (event.key === "2" && canPlay && (stateRef.current.selectedCard || stateRef.current.selectedEvent)) {
        onChoice("quick");
      }
    };
    window.addEventListener("keydown", listener);
    return () => window.removeEventListener("keydown", listener);
  }, [canPlay, onChoice, onRoll, showRules]);

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
    const drawFrame = () => {
      const currentState = stateRef.current;
      context.clearRect(0, 0, WIDTH, HEIGHT);
      drawGradientBackground(context);
      if (showRules) {
        drawRulesScreen(context);
      } else if (currentState.gameOver) {
        drawEndScreen(context, currentState);
      } else {
        drawPlayScreen(context, currentState);
      }
      frameId = window.requestAnimationFrame(drawFrame);
    };

    frameId = window.requestAnimationFrame(drawFrame);
    return () => window.cancelAnimationFrame(frameId);
  }, [showRules]);

  const showDecisionButtons = !state.gameOver && !!(state.selectedCard || state.selectedEvent);
  const showRollButton = !state.gameOver && !state.selectedCard && !state.selectedEvent;

  return (
    <div className="page-center" style={{ alignItems: "flex-start", paddingTop: 16, paddingBottom: 16 }}>
      <div
        style={{
          width: WIDTH * scale,
          height: HEIGHT * scale,
          position: "relative"
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: 0,
            width: WIDTH,
            height: HEIGHT,
            transform: `scale(${scale})`,
            transformOrigin: "top left"
          }}
        >
          <canvas ref={canvasRef} width={WIDTH} height={HEIGHT} style={{ position: "absolute", inset: 0, width: WIDTH, height: HEIGHT }} />

          {!state.gameOver && !showRules ? (
            <button style={buttonStyle(1090, 28, 140, 38, ORANGE)} onClick={() => setShowRules(true)}>
              Rules
            </button>
          ) : null}

          {showRules ? (
            <button style={buttonStyle(40, 650, 140, 42, BLUE)} onClick={() => setShowRules(false)}>
              Back
            </button>
          ) : null}

          {!showRules && !state.gameOver && showRollButton ? (
            <button style={buttonStyle(1065, 660, 140, 38, BLUE, !canPlay)} onClick={onRoll} disabled={!canPlay}>
              Roll Dice
            </button>
          ) : null}

          {!showRules && !state.gameOver && showDecisionButtons ? (
            <>
              <button style={buttonStyle(930, 660, 140, 38, GREEN, !canPlay)} onClick={() => onChoice("eco")} disabled={!canPlay}>
                Eco Plan
              </button>
              <button style={buttonStyle(1085, 660, 140, 38, RED, !canPlay)} onClick={() => onChoice("quick")} disabled={!canPlay}>
                Quick Fix
              </button>
            </>
          ) : null}

          {state.gameOver && !showRules ? (
            <>
              <button style={buttonStyle(525, 640, 140, 44, GREEN)} onClick={onPlayAgain}>
                Restart
              </button>
              <button style={buttonStyle(690, 640, 120, 44, RED)} onClick={onQuit}>
                Quit
              </button>
            </>
          ) : null}

          {!showRules && !state.gameOver && disabledMessage ? (
            <div
              style={{
                position: "absolute",
                left: 742,
                top: 646,
                width: 510,
                height: 62,
                borderRadius: 16,
                background: "rgba(2, 6, 23, 0.7)",
                display: "grid",
                placeItems: "center",
                textAlign: "center",
                padding: 16,
                color: WHITE,
                fontWeight: 700,
                pointerEvents: "none"
              }}
            >
              {disabledMessage}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

function drawPlayScreen(context: CanvasRenderingContext2D, state: GameState) {
  context.fillStyle = "rgba(8, 13, 24, 0.85)";
  context.fillRect(0, 0, WIDTH, 78);
  context.strokeStyle = "#374b60";
  context.lineWidth = 2;
  context.beginPath();
  context.moveTo(0, 78);
  context.lineTo(WIDTH, 78);
  context.stroke();

  drawText(context, "700 30px \"Segoe UI\", Arial, sans-serif", "Carbon Quest", GREEN, 55, 35);
  roundRectFill(context, 330, 29, 610, 30, 15, "#0c1422");
  drawText(context, "15px \"Segoe UI\", Arial, sans-serif", state.message.slice(0, 88), WHITE, 346, 48);

  drawBoard(context, state);
  drawCityVisual(context, state);
  drawMeters(context, state);
  drawPlayerPanels(context, state);
  drawDecisionPanel(context, state);
  drawActionBar(context, state);
}

function drawRulesScreen(context: CanvasRenderingContext2D) {
  const panel = { x: 55, y: 42, width: 1170, height: 620 };
  drawPanel(context, panel.x, panel.y, panel.width, panel.height, 22, "#0e1826", "#4ade80");
  drawCenteredText(context, "800 46px \"Segoe UI\", Arial, sans-serif", "Rule Sheet", GREEN, WIDTH / 2, 76);
  let y = 130;
  RULES_TEXT.forEach((rule) => {
    context.fillStyle = YELLOW;
    context.beginPath();
    context.arc(90, y + 8, 5, 0, Math.PI * 2);
    context.fill();
    const lines = wrapText(context, "18px \"Segoe UI\", Arial, sans-serif", rule, 1030);
    lines.forEach((line, index) => {
      drawText(context, "18px \"Segoe UI\", Arial, sans-serif", line, WHITE, 110, y + 16 + index * 24);
    });
    y += 58;
  });
}

function drawEndScreen(context: CanvasRenderingContext2D, state: GameState) {
  const panel = { x: 145, y: 50, width: 990, height: 610 };
  drawPanel(context, panel.x, panel.y, panel.width, panel.height, 24, "#0e1826", "#4ade80");
  const scores = state.scores ?? calculateScores(state);
  const winner = state.winner;
  const title = state.carbon < 80 && state.health > 0 ? "City Survived!" : "Challenge Ended";
  drawCenteredText(context, "800 46px \"Segoe UI\", Arial, sans-serif", title, state.carbon < 80 && state.health > 0 ? GREEN : RED, WIDTH / 2, 80);
  drawCenteredText(context, "700 22px \"Segoe UI\", Arial, sans-serif", state.message, WHITE, WIDTH / 2, 130);
  drawCenteredText(
    context,
    "700 30px \"Segoe UI\", Arial, sans-serif",
    winner === "draw" ? "It is a draw!" : `${winner === 1 ? state.player1.name : state.player2.name} wins!`,
    winner === "draw" ? YELLOW : winner === 1 ? GREEN : PURPLE,
    WIDTH / 2,
    205
  );
  drawCenteredText(
    context,
    "18px \"Segoe UI\", Arial, sans-serif",
    `Final carbon: ${state.carbon}  |  Health: ${state.health}  |  Resilience: ${state.resilience}`,
    WHITE,
    WIDTH / 2,
    260
  );

  [state.player1, state.player2].forEach((player, index) => {
    const x = 260 + index * 410;
    drawPanel(context, x, 320, 350, 210, 16, PANEL_2, index === 0 ? GREEN : PURPLE);
    drawCenteredText(context, "700 30px \"Segoe UI\", Arial, sans-serif", player.name, index === 0 ? GREEN : PURPLE, x + 175, 350);
    drawText(context, "18px \"Segoe UI\", Arial, sans-serif", `Score: ${scores[index]}`, WHITE, x + 35, 395);
    drawText(context, "18px \"Segoe UI\", Arial, sans-serif", `Budget: ${formatBudget(player.budget)}`, WHITE, x + 35, 425);
    drawText(context, "18px \"Segoe UI\", Arial, sans-serif", `Eco / Quick: ${player.ecoChoices} / ${player.quickChoices}`, WHITE, x + 35, 455);
    drawText(context, "18px \"Segoe UI\", Arial, sans-serif", `Policies: ${player.policies.length}`, WHITE, x + 35, 485);
  });
}

function drawBoard(context: CanvasRenderingContext2D, state: GameState) {
  drawPanel(context, 35, 88, 685, 522, 18, "#0e1825", "#374b60");

  const centers = BOARD_POSITIONS.map((position) => [position.x + 43, position.y + 43] as const);
  context.strokeStyle = "#4f6680";
  context.lineWidth = 5;
  context.beginPath();
  centers.forEach(([x, y], index) => {
    if (index === 0) {
      context.moveTo(x, y);
    } else {
      context.lineTo(x, y);
    }
  });
  context.closePath();
  context.stroke();

  context.strokeStyle = "#0f172a";
  context.lineWidth = 2;
  context.beginPath();
  centers.forEach(([x, y], index) => {
    if (index === 0) {
      context.moveTo(x, y);
    } else {
      context.lineTo(x, y);
    }
  });
  context.closePath();
  context.stroke();

  state.boardTiles.forEach((tile, index) => {
    const rect = BOARD_POSITIONS[index]!;
    const color = ZONE_COLORS[tile.zone] ?? BLUE;
    const active = state.player1.tile === index || state.player2.tile === index;
    if (active) {
      drawGlow(context, rect.x, rect.y, rect.width, rect.height, color, 0.42);
    }
    roundRectFill(context, rect.x, rect.y + 4, rect.width, rect.height, 14, "#040812");
    roundRectFill(context, rect.x, rect.y, rect.width, rect.height, 14, color);
    roundRectFill(context, rect.x, rect.y, rect.width, rect.height / 2, 14, lerpColor(color, WHITE, 0.28));
    roundRectStroke(context, rect.x, rect.y, rect.width, rect.height, 14, "#0f172a", 3);
    drawText(context, "12px \"Segoe UI\", Arial, sans-serif", String(index + 1), INK, rect.x + 8, rect.y + 18);
    drawZoneIcon(context, tile.zone, rect.x + rect.width / 2, rect.y + 34, INK);
    const lines = wrapText(context, "12px \"Segoe UI\", Arial, sans-serif", tile.zone, rect.width - 10).slice(0, 2);
    lines.forEach((line, lineIndex) => {
      drawCenteredText(context, "12px \"Segoe UI\", Arial, sans-serif", line, INK, rect.x + rect.width / 2, rect.y + 62 + lineIndex * 13);
    });
  });

  drawPlayerToken(context, BOARD_POSITIONS[state.player1.tile]!, GREEN, "1", -14);
  drawPlayerToken(context, BOARD_POSITIONS[state.player2.tile]!, PURPLE, "2", 14);
}

function drawCityVisual(context: CanvasRenderingContext2D, state: GameState) {
  const x = 155;
  const y = 230;
  const width = 455;
  const height = 190;
  const pollution = state.carbon / 100;
  drawPanel(context, x - 12, y - 12, width + 24, height + 24, 16, "#0c1220", "#374b60");

  const skyTop = lerpColor("#3e84be", "#82464b", pollution);
  const skyBottom = lerpColor("#fcb268", "#924c45", pollution);
  const gradient = context.createLinearGradient(0, y, 0, y + height);
  gradient.addColorStop(0, skyTop);
  gradient.addColorStop(1, skyBottom);
  context.fillStyle = gradient;
  context.fillRect(x, y, width, height);

  context.fillStyle = "rgba(255,218,130,0.95)";
  context.beginPath();
  context.arc(x + width - 60, y + 45, 28, 0, Math.PI * 2);
  context.fill();

  context.fillStyle = "#24303b";
  context.beginPath();
  context.moveTo(x, y + height);
  context.lineTo(x, y + height - 45);
  context.lineTo(x + 130, y + height - 80);
  context.lineTo(x + 250, y + height - 54);
  context.lineTo(x + width, y + height - 95);
  context.lineTo(x + width, y + height);
  context.closePath();
  context.fill();

  [
    [190, 90],
    [245, 120],
    [320, 75],
    [380, 130],
    [465, 95],
    [530, 118]
  ].forEach(([offsetX, buildingHeight]) => {
    const bx = offsetX;
    const buildingX = bx;
    const buildingY = y + height - buildingHeight;
    const shade = lerpColor("#2d3748", "#524142", pollution);
    roundRectFill(context, buildingX, buildingY, 42, buildingHeight, 5, shade);
    roundRectStroke(context, buildingX, buildingY, 42, buildingHeight, 5, "#0a0f18", 2);
    context.fillStyle = "#ffe68c";
    for (let windowY = buildingY + 12; windowY < buildingY + buildingHeight - 10; windowY += 20) {
      roundRectFill(context, buildingX + 12, windowY, 8, 10, 2, "#ffe68c");
    }
  });

  const treeCount = Math.max(1, Math.floor(state.resilience / 12));
  for (let index = 0; index < treeCount; index += 1) {
    const treeX = x + 25 + index * 45;
    context.fillStyle = "#5e3c23";
    context.fillRect(treeX, y + height - 28, 8, 22);
    context.fillStyle = GREEN;
    context.beginPath();
    context.arc(treeX + 4, y + height - 35, 15, 0, Math.PI * 2);
    context.fill();
  }

  context.fillStyle = `rgba(230,80,60,${0.3 * pollution})`;
  context.fillRect(x, y, width, height);
  roundRectStroke(context, x, y, width, height, 10, WHITE, 2);
  drawCenteredText(context, "12px \"Segoe UI\", Arial, sans-serif", "Live city view changes with carbon and resilience", WHITE, x + width / 2, y + height + 16);
}

function drawMeters(context: CanvasRenderingContext2D, state: GameState) {
  drawPanel(context, 742, 86, 510, 245, 18, "#0e1726", "#374b60");
  drawText(context, "700 22px \"Segoe UI\", Arial, sans-serif", "City Dashboard", WHITE, 765, 118);
  const labels: Array<[string, number, string]> = [
    ["Carbon", state.carbon, RED],
    ["Health", state.health, GREEN],
    ["Resilience", state.resilience, BLUE]
  ];

  labels.forEach(([label, value, color], index) => {
    const x = 765;
    const y = 150 + index * 58;
    drawText(context, "700 22px \"Segoe UI\", Arial, sans-serif", `${label}: ${value}`, color, x, y);
    roundRectFill(context, x + 145, y - 9, 320, 18, 10, "#0f172a");
    roundRectFill(context, x + 147, y - 7, Math.max(0, (316 * value) / 100), 14, 8, color);
  });
}

function drawPlayerPanels(context: CanvasRenderingContext2D, state: GameState) {
  [state.player1, state.player2].forEach((player, index) => {
    const rectX = 742 + index * 260;
    const rectY = 338;
    const accent = index === 0 ? GREEN : PURPLE;
    const isActive = state.currentPlayer === index + 1;
    if (isActive) {
      drawGlow(context, rectX, rectY, 245, 142, accent, 0.32);
    }
    drawPanel(context, rectX, rectY, 245, 142, 12, PANEL_2, isActive ? accent : "#475569");
    drawPill(context, rectX + 161, rectY + 14, 62, 22, isActive ? "TURN" : "WAIT", isActive ? accent : "#334155");
    drawText(context, "700 22px \"Segoe UI\", Arial, sans-serif", player.name, accent, rectX + 16, rectY + 34);
    drawText(context, "15px \"Segoe UI\", Arial, sans-serif", `Budget: ${formatBudget(player.budget)}`, WHITE, rectX + 16, rectY + 64);
    drawText(context, "15px \"Segoe UI\", Arial, sans-serif", `Support: ${player.support}`, WHITE, rectX + 16, rectY + 88);
    drawText(context, "15px \"Segoe UI\", Arial, sans-serif", `Green points: ${player.greenPoints}`, GREEN, rectX + 16, rectY + 112);
    drawText(context, "12px \"Segoe UI\", Arial, sans-serif", `Policies: ${player.policies.length > 0 ? player.policies.join(", ") : "None"}`.slice(0, 34), MUTED, rectX + 16, rectY + 132);
  });
}

function drawDecisionPanel(context: CanvasRenderingContext2D, state: GameState) {
  drawPanel(context, 742, 490, 510, 150, 12, PANEL_2, "#475569");
  if (state.selectedEvent) {
    context.fillStyle = PURPLE;
    roundRectFill(context, 742, 490, 8, 150, 12, PURPLE);
    drawText(context, "700 30px \"Segoe UI\", Arial, sans-serif", `EVENT: ${state.selectedEvent.title}`, PURPLE, 758, 520);
    wrapText(context, "15px \"Segoe UI\", Arial, sans-serif", state.selectedEvent.text, 460).slice(0, 3).forEach((line, index) => {
      drawText(context, "15px \"Segoe UI\", Arial, sans-serif", line, WHITE, 758, 552 + index * 20);
    });
    drawText(context, "12px \"Segoe UI\", Arial, sans-serif", "Pick an action", YELLOW, 758, 620);
    return;
  }

  if (!state.selectedCard) {
    const activeColor = state.currentPlayer === 1 ? GREEN : PURPLE;
    drawText(context, "700 30px \"Segoe UI\", Arial, sans-serif", `${state.currentPlayer === 1 ? state.player1.name : state.player2.name}'s Turn`, activeColor, 758, 520);
    drawPill(context, 1114, 504, 108, 24, `Round ${Math.min(state.round, state.maxRounds)}/${state.maxRounds}`, BLUE);
    drawText(context, "18px \"Segoe UI\", Arial, sans-serif", `Dice: ${state.dice}`, WHITE, 758, 566);
    return;
  }

  const card = state.selectedCard;
  const zoneColor = ZONE_COLORS[card.zone] ?? BLUE;
  roundRectFill(context, 742, 490, 8, 150, 12, zoneColor);
  drawText(context, "700 30px \"Segoe UI\", Arial, sans-serif", card.title, zoneColor, 758, 518);
  drawZoneIcon(context, card.zone, 1220, 522, zoneColor);

  drawChoiceBox(context, 758, 550, 225, 75, "ECO", "#10502d", "#86efac", card.eco, card.ecoEffect);
  drawChoiceBox(context, 998, 550, 225, 75, "QUICK", "#641919", "#fecaca", card.quick, card.quickEffect);
}

function drawActionBar(context: CanvasRenderingContext2D, state: GameState) {
  const accent = state.currentPlayer === 1 ? GREEN : PURPLE;
  drawPanel(context, 742, 646, 510, 62, 16, "#0c1422", accent);
  if (state.selectedCard || state.selectedEvent) {
    drawText(context, "15px \"Segoe UI\", Arial, sans-serif", "Choose action", YELLOW, 760, 670);
    drawText(context, "12px \"Segoe UI\", Arial, sans-serif", "Keyboard: 1 or 2", MUTED, 760, 694);
  } else {
    drawText(context, "15px \"Segoe UI\", Arial, sans-serif", "Ready", YELLOW, 760, 670);
    drawText(context, "12px \"Segoe UI\", Arial, sans-serif", "Roll for a district card.", MUTED, 760, 694);
  }
}

function drawChoiceBox(
  context: CanvasRenderingContext2D,
  x: number,
  y: number,
  width: number,
  height: number,
  title: string,
  background: string,
  titleColor: string,
  body: string,
  effect: [number, number, number, number, number]
) {
  drawPanel(context, x, y, width, height, 9, background, background);
  drawText(context, "700 15px \"Segoe UI\", Arial, sans-serif", title, titleColor, x + 12, y + 18);
  drawText(context, "12px \"Segoe UI\", Arial, sans-serif", body, WHITE, x + 12, y + 38);
  drawText(context, "12px \"Segoe UI\", Arial, sans-serif", `Carbon ${effect[0] >= 0 ? "+" : ""}${effect[0]}   Health ${effect[1] >= 0 ? "+" : ""}${effect[1]}`, WHITE, x + 12, y + 55);
  drawText(context, "12px \"Segoe UI\", Arial, sans-serif", `Cost: ${formatBudget(Math.abs(effect[2]))}`, WHITE, x + 12, y + 68);
}

function drawPlayerToken(context: CanvasRenderingContext2D, rect: { x: number; y: number; width: number; height: number }, color: string, label: string, offset: number) {
  const x = rect.x + rect.width / 2 + offset;
  const y = rect.y + rect.height / 2 + 24;
  context.fillStyle = "rgba(0,0,0,0.6)";
  context.beginPath();
  context.arc(x + 2, y + 3, 16, 0, Math.PI * 2);
  context.fill();
  context.fillStyle = color;
  context.beginPath();
  context.arc(x, y, 16, 0, Math.PI * 2);
  context.fill();
  context.strokeStyle = WHITE;
  context.lineWidth = 2;
  context.beginPath();
  context.arc(x, y, 16, 0, Math.PI * 2);
  context.stroke();
  drawCenteredText(context, "700 15px \"Segoe UI\", Arial, sans-serif", label, WHITE, x, y + 5);
}

function buildBoardPositions() {
  const positions: Array<{ x: number; y: number; width: number; height: number }> = [];
  const left = 55;
  const top = 110;
  const size = 86;
  const gap = 10;
  for (let index = 0; index < 7; index += 1) {
    positions.push({ x: left + index * (size + gap), y: top, width: size, height: size });
  }
  for (let index = 1; index < 5; index += 1) {
    positions.push({ x: left + 6 * (size + gap), y: top + index * (size + gap), width: size, height: size });
  }
  for (let index = 5; index >= 0; index -= 1) {
    positions.push({ x: left + index * (size + gap), y: top + 4 * (size + gap), width: size, height: size });
  }
  for (let index = 3; index > 0; index -= 1) {
    positions.push({ x: left, y: top + index * (size + gap), width: size, height: size });
  }
  return positions;
}

function drawGradientBackground(context: CanvasRenderingContext2D) {
  const top = "#10182d";
  const mid = "#1a384e";
  const bottom = "#121622";
  for (let y = 0; y < HEIGHT; y += 1) {
    const t = y / HEIGHT;
    const color = t < 0.62 ? lerpColor(top, mid, Math.min(1, t * 1.4)) : lerpColor(mid, bottom, (t - 0.62) / 0.38);
    context.strokeStyle = color;
    context.beginPath();
    context.moveTo(0, y);
    context.lineTo(WIDTH, y);
    context.stroke();
  }
  context.fillStyle = "rgba(255,255,255,0.9)";
  for (let index = 0; index < 34; index += 1) {
    const x = (index * 79 + 31) % WIDTH;
    const y = 34 + (index * 47) % 230;
    context.beginPath();
    context.arc(x, y, 1.2, 0, Math.PI * 2);
    context.fill();
  }
}

function drawPanel(context: CanvasRenderingContext2D, x: number, y: number, width: number, height: number, radius: number, fill: string, border: string) {
  roundRectFill(context, x + 5, y + 7, width, height, radius, "#030712");
  roundRectFill(context, x, y, width, height, radius, fill);
  roundRectStroke(context, x, y, width, height, radius, border, 2);
}

function drawPill(context: CanvasRenderingContext2D, x: number, y: number, width: number, height: number, text: string, color: string) {
  roundRectFill(context, x, y, width, height, height / 2, color);
  roundRectStroke(context, x, y, width, height, height / 2, WHITE, 1);
  drawCenteredText(context, "12px \"Segoe UI\", Arial, sans-serif", text, WHITE, x + width / 2, y + height / 2 + 4);
}

function drawGlow(context: CanvasRenderingContext2D, x: number, y: number, width: number, height: number, color: string, alpha: number) {
  roundRectFill(context, x - 12, y - 12, width + 24, height + 24, 26, withAlpha(color, alpha));
}

function drawZoneIcon(context: CanvasRenderingContext2D, zone: Zone, centerX: number, centerY: number, color: string) {
  context.strokeStyle = color;
  context.fillStyle = color;
  context.lineWidth = 3;
  if (zone === "Transport") {
    context.beginPath();
    context.moveTo(centerX, centerY - 12);
    context.lineTo(centerX - 14, centerY + 10);
    context.lineTo(centerX + 14, centerY + 10);
    context.closePath();
    context.stroke();
    context.beginPath();
    context.moveTo(centerX, centerY - 6);
    context.lineTo(centerX, centerY + 8);
    context.stroke();
  } else if (zone === "Energy") {
    context.beginPath();
    context.arc(centerX, centerY, 12, 0, Math.PI * 2);
    context.stroke();
    [0, 120, 240].forEach((angle) => {
      const radians = (angle * Math.PI) / 180;
      context.beginPath();
      context.moveTo(centerX, centerY);
      context.lineTo(centerX + Math.cos(radians) * 16, centerY + Math.sin(radians) * 16);
      context.stroke();
    });
  } else if (zone === "Waste") {
    roundRectStroke(context, centerX - 11, centerY - 9, 22, 20, 4, color, 3);
    context.beginPath();
    context.moveTo(centerX - 14, centerY - 12);
    context.lineTo(centerX + 14, centerY - 12);
    context.stroke();
  } else if (zone === "Green Space") {
    context.beginPath();
    context.ellipse(centerX, centerY, 14, 10, 0, 0, Math.PI * 2);
    context.stroke();
    context.beginPath();
    context.moveTo(centerX - 8, centerY + 7);
    context.lineTo(centerX + 9, centerY - 7);
    context.stroke();
  } else if (zone === "Consumption") {
    roundRectStroke(context, centerX - 13, centerY - 6, 26, 18, 3, color, 3);
    context.beginPath();
    context.arc(centerX, centerY - 7, 8, Math.PI, Math.PI * 2);
    context.stroke();
  } else {
    context.beginPath();
    context.arc(centerX - 8, centerY - 2, 7, 0, Math.PI * 2);
    context.stroke();
    context.beginPath();
    context.arc(centerX + 8, centerY - 2, 7, 0, Math.PI * 2);
    context.stroke();
    context.beginPath();
    context.arc(centerX, centerY + 10, 18, 0, Math.PI);
    context.stroke();
  }
}

function roundRectFill(context: CanvasRenderingContext2D, x: number, y: number, width: number, height: number, radius: number, color: string) {
  context.fillStyle = color;
  context.beginPath();
  context.moveTo(x + radius, y);
  context.arcTo(x + width, y, x + width, y + height, radius);
  context.arcTo(x + width, y + height, x, y + height, radius);
  context.arcTo(x, y + height, x, y, radius);
  context.arcTo(x, y, x + width, y, radius);
  context.closePath();
  context.fill();
}

function roundRectStroke(context: CanvasRenderingContext2D, x: number, y: number, width: number, height: number, radius: number, color: string, lineWidth: number) {
  context.strokeStyle = color;
  context.lineWidth = lineWidth;
  context.beginPath();
  context.moveTo(x + radius, y);
  context.arcTo(x + width, y, x + width, y + height, radius);
  context.arcTo(x + width, y + height, x, y + height, radius);
  context.arcTo(x, y + height, x, y, radius);
  context.arcTo(x, y, x + width, y, radius);
  context.closePath();
  context.stroke();
}

function drawText(context: CanvasRenderingContext2D, font: string, text: string, color: string, x: number, y: number) {
  context.font = font;
  context.textAlign = "left";
  context.textBaseline = "middle";
  if (!font.startsWith("12px") && color !== MUTED) {
    context.fillStyle = "rgba(0,0,0,0.6)";
    context.fillText(text, x + 2, y + 2);
  }
  context.fillStyle = color;
  context.fillText(text, x, y);
}

function drawCenteredText(context: CanvasRenderingContext2D, font: string, text: string, color: string, x: number, y: number) {
  context.font = font;
  context.textAlign = "center";
  context.textBaseline = "middle";
  if (!font.startsWith("12px") && color !== MUTED) {
    context.fillStyle = "rgba(0,0,0,0.6)";
    context.fillText(text, x + 2, y + 2);
  }
  context.fillStyle = color;
  context.fillText(text, x, y);
}

function wrapText(context: CanvasRenderingContext2D, font: string, text: string, maxWidth: number) {
  context.font = font;
  const words = text.split(" ");
  const lines: string[] = [];
  let current = "";
  words.forEach((word) => {
    const test = current ? `${current} ${word}` : word;
    if (context.measureText(test).width <= maxWidth) {
      current = test;
    } else {
      if (current) {
        lines.push(current);
      }
      current = word;
    }
  });
  if (current) {
    lines.push(current);
  }
  return lines;
}

function lerpColor(start: string, end: string, t: number) {
  const a = hexToRgb(start);
  const b = hexToRgb(end);
  return `rgb(${Math.round(a.r + (b.r - a.r) * t)}, ${Math.round(a.g + (b.g - a.g) * t)}, ${Math.round(a.b + (b.b - a.b) * t)})`;
}

function withAlpha(color: string, alpha: number) {
  const rgb = hexToRgb(color);
  return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${alpha})`;
}

function hexToRgb(color: string) {
  const hex = color.replace("#", "");
  const value = parseInt(hex, 16);
  return {
    r: (value >> 16) & 255,
    g: (value >> 8) & 255,
    b: value & 255
  };
}

function buttonStyle(x: number, y: number, width: number, height: number, color: string, disabled = false): CSSProperties {
  return {
    position: "absolute",
    left: x,
    top: y,
    width,
    height,
    borderRadius: 20,
    border: "2px solid rgba(255,255,255,0.8)",
    background: disabled ? "rgba(71,85,105,0.5)" : color,
    color: WHITE,
    font: `700 15px ${FONT_FAMILY}`,
    boxShadow: disabled ? "none" : "0 6px 0 rgba(0,0,0,0.3)",
    cursor: disabled ? "not-allowed" : "pointer"
  };
}

