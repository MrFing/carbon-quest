import { useEffect, useLayoutEffect, useRef, useState, type CSSProperties } from "react";

import type { ChoiceType, DecisionCard, EventCard, GameState, PlayerState, Zone } from "../game/types";
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
const WHITE = "#eef2ff";
const MUTED = "#94a3b8";
const GREEN = "#22c55e";
const RED = "#ef4444";
const YELLOW = "#facc15";
const BLUE = "#60a5fa";
const PURPLE = "#a78bfa";
const ORANGE = "#fb923c";
const PANEL_FILL = "#111827";

const BOARD_POSITIONS = buildBoardPositions();

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
  const activePlayer = state.currentPlayer === 1 ? state.player1 : state.player2;

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

          {!showRules && !state.gameOver ? (
            <>
              <button style={buttonStyle(1090, 28, 140, 38, ORANGE)} onClick={() => setShowRules(true)}>
                Rules
              </button>
              {renderCityVisualOverlay(state)}
              {renderDashboardPanel(state)}
              {renderPlayerPanel(state.player1, 742, 338, GREEN, state.currentPlayer === 1)}
              {renderPlayerPanel(state.player2, 1002, 338, PURPLE, state.currentPlayer === 2)}
              {renderDecisionPanel(state, activePlayer)}
              {renderActionBar(state, canPlay, disabledMessage, showDecisionButtons, onRoll, onChoice)}
              {renderPlayerToken(state.player1, GREEN, "1", -14)}
              {renderPlayerToken(state.player2, PURPLE, "2", 14)}
            </>
          ) : null}

          {showRules ? (
            <button style={buttonStyle(40, 650, 140, 42, BLUE)} onClick={() => setShowRules(false)}>
              Back
            </button>
          ) : null}

          {state.gameOver && !showRules ? (
            <>
              {renderEndOverlay(state)}
              <button style={buttonStyle(525, 640, 140, 44, GREEN)} onClick={onPlayAgain}>
                Restart
              </button>
              <button style={buttonStyle(690, 640, 120, 44, RED)} onClick={onQuit}>
                Quit
              </button>
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}

function renderCityVisualOverlay(state: GameState) {
  const pollution = clamp(state.carbon / 100, 0, 1);
  const skyTop = lerpColor("#3e84be", "#82464b", pollution);
  const skyBottom = lerpColor("#fcb268", "#924c45", pollution);
  const buildings = [
    { left: 35, height: 90 },
    { left: 90, height: 120 },
    { left: 165, height: 75 },
    { left: 225, height: 130 },
    { left: 310, height: 95 },
    { left: 375, height: 118 }
  ];
  const treeCount = Math.max(1, Math.floor(state.resilience / 12));

  return (
    <div style={overlayPanelStyle(143, 218, 479, 214, 16, "#0c1220", "#374b60")}>
      <div
        style={{
          position: "absolute",
          left: 12,
          top: 12,
          width: 455,
          height: 190,
          overflow: "hidden",
          borderRadius: 10,
          border: "2px solid #eef2ff",
          background: `linear-gradient(180deg, ${skyTop} 0%, ${skyBottom} 100%)`
        }}
      >
        <div
          style={{
            position: "absolute",
            right: 32,
            top: 18,
            width: 56,
            height: 56,
            borderRadius: "50%",
            background: "#ffd682"
          }}
        />
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            bottom: 0,
            height: 95,
            background: "#24303b",
            clipPath: "polygon(0 100%, 0 76%, 28% 58%, 55% 72%, 100% 50%, 100% 100%)"
          }}
        />
        {buildings.map((building, index) => (
          <div
            key={`${building.left}-${index}`}
            style={{
              position: "absolute",
              left: building.left,
              bottom: 0,
              width: 42,
              height: building.height,
              borderRadius: 5,
              background: lerpColor("#2d3748", "#524142", pollution),
              border: "2px solid #0a0f18"
            }}
          >
            {Array.from({ length: Math.max(1, Math.floor((building.height - 20) / 20)) }).map((_, windowIndex) => (
              <div
                key={windowIndex}
                style={{
                  position: "absolute",
                  left: 12,
                  top: 12 + windowIndex * 20,
                  width: 8,
                  height: 10,
                  borderRadius: 2,
                  background: "#ffe68c"
                }}
              />
            ))}
          </div>
        ))}
        {Array.from({ length: treeCount }).map((_, index) => {
          const left = 25 + index * 45;
          return (
            <div key={left} style={{ position: "absolute", left, bottom: 0, width: 30, height: 42 }}>
              <div style={{ position: "absolute", left: 11, bottom: 0, width: 8, height: 22, background: "#5e3c23" }} />
              <div style={{ position: "absolute", left: 0, bottom: 15, width: 30, height: 30, borderRadius: "50%", background: GREEN }} />
            </div>
          );
        })}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: `rgba(230,80,60,${0.3 * pollution})`
          }}
        />
      </div>
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: -2,
          textAlign: "center",
          color: WHITE,
          font: `12px ${FONT_FAMILY}`
        }}
      >
        Live city view changes with carbon and resilience
      </div>
    </div>
  );
}

function renderDashboardPanel(state: GameState) {
  const rows = [
    { label: "Carbon", value: state.carbon, color: RED },
    { label: "Health", value: state.health, color: GREEN },
    { label: "Resilience", value: state.resilience, color: BLUE }
  ];

  return (
    <div style={overlayPanelStyle(742, 86, 510, 245, 18, "#0e1726", "#374b60")}>
      <div style={{ position: "absolute", left: 23, top: 24, color: WHITE, font: `700 22px ${FONT_FAMILY}` }}>City Dashboard</div>
      {rows.map((row, index) => {
        const top = 88 + index * 58;
        return (
          <div key={row.label} style={{ position: "absolute", left: 23, right: 23, top }}>
            <div style={{ color: row.color, font: `700 22px ${FONT_FAMILY}` }}>{row.label}: {row.value}</div>
            <div style={{ position: "absolute", left: 220, top: 5, width: 245, height: 18, borderRadius: 10, background: "#0f172a" }}>
              <div
                style={{
                  width: `${clamp(row.value, 0, 100)}%`,
                  height: 14,
                  marginTop: 2,
                  marginLeft: 2,
                  borderRadius: 8,
                  background: row.color
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

function renderPlayerPanel(player: PlayerState, left: number, top: number, accent: string, isActive: boolean) {
  const policies = player.policies.length > 0 ? player.policies.join(", ") : "None";
  return (
    <div
      style={{
        ...overlayPanelStyle(left, top, 245, 142, 12, PANEL_FILL, isActive ? accent : "#475569"),
        boxShadow: isActive ? `0 0 0 8px ${withAlpha(accent, 0.12)}, 5px 7px 0 #030712` : "5px 7px 0 #030712"
      }}
    >
      <div style={{ position: "absolute", left: 16, top: 12, color: accent, font: `700 22px ${FONT_FAMILY}` }}>{player.name}</div>
      <div style={pillAbsoluteStyle(161, 14, 62, 22, isActive ? accent : "#334155")}>{isActive ? "TURN" : "WAIT"}</div>
      <div style={{ position: "absolute", left: 16, top: 48, color: WHITE, font: `15px ${FONT_FAMILY}` }}>Budget: {formatBudget(player.budget)}</div>
      <div style={{ position: "absolute", left: 16, top: 72, color: WHITE, font: `15px ${FONT_FAMILY}` }}>Support: {player.support}</div>
      <div style={{ position: "absolute", left: 16, top: 96, color: GREEN, font: `15px ${FONT_FAMILY}` }}>Green points: {player.greenPoints}</div>
      <div style={{ position: "absolute", left: 16, top: 121, color: MUTED, font: `12px ${FONT_FAMILY}` }}>Policies: {policies.slice(0, 28)}</div>
    </div>
  );
}

function renderDecisionPanel(state: GameState, activePlayer: PlayerState) {
  const left = 742;
  const top = 490;
  const width = 510;
  const height = 150;

  if (state.selectedEvent) {
    return (
      <div style={overlayPanelStyle(left, top, width, height, 12, PANEL_FILL, "#475569")}>
        <div style={{ position: "absolute", left: 0, top: 0, width: 8, height, borderRadius: "12px 0 0 12px", background: PURPLE }} />
        <div style={{ position: "absolute", left: 16, top: 12, color: PURPLE, font: `700 30px ${FONT_FAMILY}` }}>EVENT: {state.selectedEvent.title}</div>
        {wrapTextLines(state.selectedEvent.text, 64).slice(0, 3).map((line, index) => (
          <div key={index} style={{ position: "absolute", left: 16, top: 50 + index * 20, color: WHITE, font: `15px ${FONT_FAMILY}` }}>{line}</div>
        ))}
        <div style={{ position: "absolute", left: 16, top: 122, color: YELLOW, font: `12px ${FONT_FAMILY}` }}>Pick an action</div>
      </div>
    );
  }

  if (!state.selectedCard) {
    const accent = state.currentPlayer === 1 ? GREEN : PURPLE;
    return (
      <div style={overlayPanelStyle(left, top, width, height, 12, PANEL_FILL, "#475569")}>
        <div style={{ position: "absolute", left: 16, top: 12, color: accent, font: `700 30px ${FONT_FAMILY}` }}>{activePlayer.name}'s Turn</div>
        <div style={pillAbsoluteStyle(372, 14, 108, 24, BLUE)}>Round {Math.min(state.round, state.maxRounds)}/{state.maxRounds}</div>
        <div style={{ position: "absolute", left: 16, top: 54, color: WHITE, font: `18px ${FONT_FAMILY}` }}>Dice: {state.dice}</div>
      </div>
    );
  }

  const card = state.selectedCard;
  const zoneColor = ZONE_COLORS[card.zone] ?? BLUE;
  return (
    <div style={overlayPanelStyle(left, top, width, height, 12, PANEL_FILL, "#475569")}>
      <div style={{ position: "absolute", left: 0, top: 0, width: 8, height, borderRadius: "12px 0 0 12px", background: zoneColor }} />
      <div style={{ position: "absolute", left: 16, top: 8, color: zoneColor, font: `700 30px ${FONT_FAMILY}` }}>{card.title}</div>
      <div style={{ position: "absolute", right: 16, top: 20, width: 24, height: 24, borderRadius: 12, border: `3px solid ${zoneColor}` }} />
      {renderChoiceBox(card, "eco", 16, 60, "#10502d", "#86efac")}
      {renderChoiceBox(card, "quick", 256, 60, "#641919", "#fecaca")}
    </div>
  );
}

function renderChoiceBox(card: DecisionCard, choice: ChoiceType, left: number, top: number, background: string, labelColor: string) {
  const title = choice === "eco" ? "ECO" : "QUICK";
  const body = choice === "eco" ? card.eco : card.quick;
  const effect = choice === "eco" ? card.ecoEffect : card.quickEffect;
  return (
    <div
      style={{
        position: "absolute",
        left,
        top,
        width: 225,
        height: 75,
        borderRadius: 9,
        background
      }}
    >
      <div style={{ position: "absolute", left: 12, top: 7, color: labelColor, font: `700 15px ${FONT_FAMILY}` }}>{title}</div>
      <div style={{ position: "absolute", left: 12, top: 27, color: WHITE, font: `12px ${FONT_FAMILY}` }}>{body}</div>
      <div style={{ position: "absolute", left: 12, top: 42, color: WHITE, font: `12px ${FONT_FAMILY}` }}>Carbon {effect[0] >= 0 ? "+" : ""}{effect[0]}   Health {effect[1] >= 0 ? "+" : ""}{effect[1]}</div>
      <div style={{ position: "absolute", left: 12, top: 55, color: WHITE, font: `12px ${FONT_FAMILY}` }}>Cost: {formatBudget(Math.abs(effect[2]))}</div>
    </div>
  );
}

function renderActionBar(
  state: GameState,
  canPlay: boolean,
  disabledMessage: string | null | undefined,
  showDecisionButtons: boolean,
  onRoll: () => void,
  onChoice: (choice: ChoiceType) => void
) {
  const accent = state.currentPlayer === 1 ? GREEN : PURPLE;
  return (
    <div style={overlayPanelStyle(742, 646, 510, 62, 16, "#0c1422", accent)}>
      <div style={{ position: "absolute", left: 18, top: 10, color: YELLOW, font: `15px ${FONT_FAMILY}` }}>
        {showDecisionButtons ? "Choose action" : "Ready"}
      </div>
      <div style={{ position: "absolute", left: 18, top: 35, color: MUTED, font: `12px ${FONT_FAMILY}` }}>
        {showDecisionButtons ? "Keyboard: 1 or 2" : "Roll for a district card."}
      </div>

      {showDecisionButtons ? (
        <>
          <button style={actionButtonStyle(188, 12, 140, 38, GREEN, !canPlay)} onClick={() => onChoice("eco")} disabled={!canPlay}>
            Eco Plan
          </button>
          <button style={actionButtonStyle(343, 12, 140, 38, RED, !canPlay)} onClick={() => onChoice("quick")} disabled={!canPlay}>
            Quick Fix
          </button>
        </>
      ) : (
        <button style={actionButtonStyle(323, 12, 140, 38, BLUE, !canPlay)} onClick={onRoll} disabled={!canPlay}>
          Roll Dice
        </button>
      )}

      {!canPlay && disabledMessage ? (
        <div
          style={{
            position: "absolute",
            inset: 0,
            borderRadius: 16,
            background: "rgba(2, 6, 23, 0.7)",
            display: "grid",
            placeItems: "center",
            textAlign: "center",
            padding: 16,
            color: WHITE,
            fontWeight: 700
          }}
        >
          {disabledMessage}
        </div>
      ) : null}
    </div>
  );
}

function renderPlayerToken(player: PlayerState, color: string, label: string, offset: number) {
  const rect = BOARD_POSITIONS[player.tile] ?? BOARD_POSITIONS[0]!;
  const x = rect.x + rect.width / 2 + offset;
  const y = rect.y + rect.height / 2 + 24;
  return (
    <div
      style={{
        position: "absolute",
        left: x - 16,
        top: y - 16,
        width: 32,
        height: 32,
        borderRadius: "50%",
        background: color,
        border: "2px solid #eef2ff",
        boxShadow: "2px 3px 0 rgba(0,0,0,0.6)",
        display: "grid",
        placeItems: "center",
        color: WHITE,
        font: `700 15px ${FONT_FAMILY}`
      }}
    >
      {label}
    </div>
  );
}

function renderEndOverlay(state: GameState) {
  const scores = state.scores ?? calculateScores(state);
  const winner = state.winner;
  const title = state.carbon < 80 && state.health > 0 ? "City Survived!" : "Challenge Ended";
  const titleColor = state.carbon < 80 && state.health > 0 ? GREEN : RED;
  const winnerColor = winner === "draw" ? YELLOW : winner === 1 ? GREEN : PURPLE;

  return (
    <div style={overlayPanelStyle(145, 50, 990, 610, 24, "#0e1826", "#4ade80")}>
      <div style={{ position: "absolute", left: 0, right: 0, top: 18, textAlign: "center", color: titleColor, font: `800 46px ${FONT_FAMILY}` }}>
        {title}
      </div>
      <div style={{ position: "absolute", left: 60, right: 60, top: 78, textAlign: "center", color: WHITE, font: `700 22px ${FONT_FAMILY}` }}>
        {state.message}
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 140, textAlign: "center", color: winnerColor, font: `700 30px ${FONT_FAMILY}` }}>
        {winner === "draw" ? "It is a draw!" : `${winner === 1 ? state.player1.name : state.player2.name} wins!`}
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 194, textAlign: "center", color: WHITE, font: `18px ${FONT_FAMILY}` }}>
        Final carbon: {state.carbon}  |  Health: {state.health}  |  Resilience: {state.resilience}
      </div>

      {[state.player1, state.player2].map((player, index) => {
        const left = 260 + index * 410;
        const accent = index === 0 ? GREEN : PURPLE;
        return (
          <div key={player.name} style={overlayPanelStyle(left, 320, 350, 210, 16, PANEL_FILL, accent)}>
            <div style={{ position: "absolute", left: 0, right: 0, top: 18, textAlign: "center", color: accent, font: `700 30px ${FONT_FAMILY}` }}>
              {player.name}
            </div>
            <div style={{ position: "absolute", left: 35, top: 75, color: WHITE, font: `18px ${FONT_FAMILY}` }}>
              Score: {scores[index]}
            </div>
            <div style={{ position: "absolute", left: 35, top: 105, color: WHITE, font: `18px ${FONT_FAMILY}` }}>
              Budget: {formatBudget(player.budget)}
            </div>
            <div style={{ position: "absolute", left: 35, top: 135, color: WHITE, font: `18px ${FONT_FAMILY}` }}>
              Eco / Quick: {player.ecoChoices} / {player.quickChoices}
            </div>
            <div style={{ position: "absolute", left: 35, top: 165, color: WHITE, font: `18px ${FONT_FAMILY}` }}>
              Policies: {player.policies.length}
            </div>
          </div>
        );
      })}
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

  drawText(context, `700 30px ${FONT_FAMILY}`, "Carbon Quest", GREEN, 55, 35);
  roundRectFill(context, 330, 29, 610, 30, 15, "#0c1422");
  drawText(context, `15px ${FONT_FAMILY}`, state.message.slice(0, 88), WHITE, 346, 48);

  drawBoard(context, state);
}

function drawRulesScreen(context: CanvasRenderingContext2D) {
  const panel = { x: 55, y: 42, width: 1170, height: 620 };
  drawPanel(context, panel.x, panel.y, panel.width, panel.height, 22, "#0e1826", "#4ade80");
  drawCenteredText(context, `800 46px ${FONT_FAMILY}`, "Rule Sheet", GREEN, WIDTH / 2, 76);
  let y = 130;
  RULES_TEXT.forEach((rule) => {
    context.fillStyle = YELLOW;
    context.beginPath();
    context.arc(90, y + 8, 5, 0, Math.PI * 2);
    context.fill();
    const lines = wrapText(context, `18px ${FONT_FAMILY}`, rule, 1030);
    lines.forEach((line, index) => {
      drawText(context, `18px ${FONT_FAMILY}`, line, WHITE, 110, y + 16 + index * 24);
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
  drawCenteredText(context, `800 46px ${FONT_FAMILY}`, title, state.carbon < 80 && state.health > 0 ? GREEN : RED, WIDTH / 2, 80);
  drawCenteredText(context, `700 22px ${FONT_FAMILY}`, state.message, WHITE, WIDTH / 2, 130);
  drawCenteredText(
    context,
    `700 30px ${FONT_FAMILY}`,
    winner === "draw" ? "It is a draw!" : `${winner === 1 ? state.player1.name : state.player2.name} wins!`,
    winner === "draw" ? YELLOW : winner === 1 ? GREEN : PURPLE,
    WIDTH / 2,
    205
  );
  drawCenteredText(
    context,
    `18px ${FONT_FAMILY}`,
    `Final carbon: ${state.carbon}  |  Health: ${state.health}  |  Resilience: ${state.resilience}`,
    WHITE,
    WIDTH / 2,
    260
  );

  [state.player1, state.player2].forEach((player, index) => {
    const x = 260 + index * 410;
    drawPanel(context, x, 320, 350, 210, 16, PANEL_FILL, index === 0 ? GREEN : PURPLE);
    drawCenteredText(context, `700 30px ${FONT_FAMILY}`, player.name, index === 0 ? GREEN : PURPLE, x + 175, 350);
    drawText(context, `18px ${FONT_FAMILY}`, `Score: ${scores[index]}`, WHITE, x + 35, 395);
    drawText(context, `18px ${FONT_FAMILY}`, `Budget: ${formatBudget(player.budget)}`, WHITE, x + 35, 425);
    drawText(context, `18px ${FONT_FAMILY}`, `Eco / Quick: ${player.ecoChoices} / ${player.quickChoices}`, WHITE, x + 35, 455);
    drawText(context, `18px ${FONT_FAMILY}`, `Policies: ${player.policies.length}`, WHITE, x + 35, 485);
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
    drawText(context, `12px ${FONT_FAMILY}`, String(index + 1), "#080d18", rect.x + 8, rect.y + 18);
    drawZoneIcon(context, tile.zone, rect.x + rect.width / 2, rect.y + 34, "#080d18");
    const lines = wrapText(context, `12px ${FONT_FAMILY}`, tile.zone, rect.width - 10).slice(0, 2);
    lines.forEach((line, lineIndex) => {
      drawCenteredText(context, `12px ${FONT_FAMILY}`, line, "#080d18", rect.x + rect.width / 2, rect.y + 62 + lineIndex * 13);
    });
  });
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

function wrapTextLines(text: string, maxLength: number) {
  const words = text.split(" ");
  const lines: string[] = [];
  let current = "";
  words.forEach((word) => {
    const test = current ? `${current} ${word}` : word;
    if (test.length <= maxLength) {
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

function clamp(value: number, low: number, high: number) {
  return Math.max(low, Math.min(high, value));
}

function overlayPanelStyle(x: number, y: number, width: number, height: number, radius: number, fill: string, border: string): CSSProperties {
  return {
    position: "absolute",
    left: x,
    top: y,
    width,
    height,
    borderRadius: radius,
    background: fill,
    border: `2px solid ${border}`,
    boxShadow: "5px 7px 0 #030712"
  };
}

function pillAbsoluteStyle(left: number, top: number, width: number, height: number, color: string): CSSProperties {
  return {
    position: "absolute",
    left,
    top,
    width,
    height,
    borderRadius: height / 2,
    background: color,
    border: "1px solid #eef2ff",
    color: WHITE,
    display: "grid",
    placeItems: "center",
    font: `12px ${FONT_FAMILY}`
  };
}

function buttonStyle(left: number, top: number, width: number, height: number, color: string): CSSProperties {
  return {
    position: "absolute",
    left,
    top,
    width,
    height,
    borderRadius: 20,
    border: "2px solid rgba(255,255,255,0.8)",
    background: color,
    color: WHITE,
    font: `700 15px ${FONT_FAMILY}`,
    boxShadow: "0 6px 0 rgba(0,0,0,0.3)",
    cursor: "pointer"
  };
}

function actionButtonStyle(left: number, top: number, width: number, height: number, color: string, disabled: boolean): CSSProperties {
  return {
    position: "absolute",
    left,
    top,
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
