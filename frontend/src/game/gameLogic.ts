import { DECISION_CARDS } from "./cards";
import type {
  DecisionCard,
  EndSummary,
  GameOverReason,
  GameState,
  PlayerState,
  Winner,
  WinnerSummary
} from "./types";

export const STARTING_BUDGET = 100_000;
export const STARTING_CARBON = 30;
export const STARTING_HEALTH = 100;
export const TOTAL_ROUNDS = 15;

function clamp(value: number, minimum: number, maximum: number): number {
  return Math.max(minimum, Math.min(maximum, value));
}

function createPlayer(name: string): PlayerState {
  return {
    name,
    budget: STARTING_BUDGET,
    ecoChoices: 0,
    quickChoices: 0,
    carbonContribution: 0,
    bankrupt: false,
    decisions: 0
  };
}

function drawCard(excludeId?: string, randomValue = Math.random): DecisionCard {
  const pool = DECISION_CARDS.filter((card) => card.id !== excludeId);
  const source = pool.length > 0 ? pool : DECISION_CARDS;
  const index = Math.floor(randomValue() * source.length);
  return source[index]!;
}

export function createInitialState(randomValue = Math.random): GameState {
  return {
    round: 1,
    currentPlayer: 1,
    carbonLevel: STARTING_CARBON,
    cityHealth: STARTING_HEALTH,
    player1: createPlayer("Player 1"),
    player2: createPlayer("Player 2"),
    currentCard: drawCard(undefined, randomValue),
    zoneScores: {
      transport: 0,
      energy: 0,
      waste: 0,
      greenspace: 0
    },
    gameOver: false,
    gameOverReason: null,
    winner: null,
    phase: "playing",
    lastMove: null
  };
}

export function checkWinner(state: Pick<GameState, "player1" | "player2" | "gameOverReason">): Winner {
  if (state.gameOverReason === "bankruptcy") {
    if (state.player1.bankrupt && !state.player2.bankrupt) {
      return 2;
    }
    if (state.player2.bankrupt && !state.player1.bankrupt) {
      return 1;
    }
  }

  if (state.player1.carbonContribution < state.player2.carbonContribution) {
    return 1;
  }
  if (state.player2.carbonContribution < state.player1.carbonContribution) {
    return 2;
  }
  if (state.player1.ecoChoices > state.player2.ecoChoices) {
    return 1;
  }
  if (state.player2.ecoChoices > state.player1.ecoChoices) {
    return 2;
  }
  if (state.player1.budget > state.player2.budget) {
    return 1;
  }
  if (state.player2.budget > state.player1.budget) {
    return 2;
  }
  return "draw";
}

export function makeChoice(state: GameState, choice: "eco" | "quick", randomValue = Math.random): GameState {
  if (state.gameOver) {
    return state;
  }

  const nextState: GameState = {
    ...state,
    player1: { ...state.player1 },
    player2: { ...state.player2 },
    zoneScores: { ...state.zoneScores },
    currentCard: state.currentCard,
    lastMove: null
  };

  const playerKey = nextState.currentPlayer === 1 ? "player1" : "player2";
  const actingPlayer = { ...nextState[playerKey] };
  const selected = choice === "eco" ? nextState.currentCard.ecoChoice : nextState.currentCard.quickChoice;

  actingPlayer.budget = Math.max(0, actingPlayer.budget - selected.cost);
  actingPlayer.decisions += 1;
  if (choice === "eco") {
    actingPlayer.ecoChoices += 1;
  } else {
    actingPlayer.quickChoices += 1;
  }
  actingPlayer.carbonContribution += selected.carbonDelta;
  if (actingPlayer.budget <= 0) {
    actingPlayer.bankrupt = true;
  }
  nextState[playerKey] = actingPlayer;

  nextState.carbonLevel = clamp(nextState.carbonLevel + selected.carbonDelta, 0, 100);
  nextState.cityHealth = clamp(nextState.cityHealth + selected.healthDelta, 0, 100);
  nextState.zoneScores[nextState.currentCard.zone] += choice === "eco" ? 1 : -1;
  nextState.lastMove = {
    player: nextState.currentPlayer,
    choice,
    zone: nextState.currentCard.zone,
    cardId: nextState.currentCard.id,
    choiceLabel: selected.label,
    carbonDelta: selected.carbonDelta,
    healthDelta: selected.healthDelta,
    cost: selected.cost,
    timestamp: Date.now()
  };

  const endGame = (reason: GameOverReason): GameState => ({
    ...nextState,
    gameOver: true,
    gameOverReason: reason,
    winner: checkWinner({ player1: nextState.player1, player2: nextState.player2, gameOverReason: reason }),
    phase: "gameover"
  });

  if (actingPlayer.bankrupt) {
    return endGame("bankruptcy");
  }
  if (nextState.carbonLevel >= 100) {
    return endGame("collapse");
  }
  if (nextState.cityHealth <= 0) {
    return endGame("health");
  }

  if (nextState.currentPlayer === 2) {
    if (nextState.round >= TOTAL_ROUNDS) {
      return endGame("rounds_complete");
    }
    nextState.round += 1;
  }

  nextState.currentPlayer = nextState.currentPlayer === 1 ? 2 : 1;
  nextState.currentCard = drawCard(nextState.currentCard.id, randomValue);
  nextState.gameOver = false;
  nextState.gameOverReason = null;
  nextState.winner = null;
  nextState.phase = "playing";
  return nextState;
}

export function getWinnerSummary(state: GameState): WinnerSummary {
  const winner = state.winner ?? checkWinner(state);
  if (winner === "draw") {
    return {
      winner,
      winnerName: null,
      loserName: null,
      reason: "Both players performed equally"
    };
  }

  const winnerPlayer = winner === 1 ? state.player1 : state.player2;
  const loserPlayer = winner === 1 ? state.player2 : state.player1;
  let reason = "made greener decisions";

  if (state.gameOverReason === "bankruptcy") {
    reason = `${loserPlayer.name} ran out of money`;
  } else if (state.player1.carbonContribution === state.player2.carbonContribution) {
    if (state.player1.ecoChoices !== state.player2.ecoChoices) {
      reason = "made more eco choices";
    } else if (state.player1.budget !== state.player2.budget) {
      reason = "managed the budget better";
    }
  }

  return {
    winner,
    winnerName: winnerPlayer.name,
    loserName: loserPlayer.name,
    reason
  };
}

export function getPlayerRating(player: PlayerState): { label: string; color: string } {
  const ratio = player.ecoChoices / Math.max(1, player.decisions);
  if (ratio >= 0.75) {
    return { label: "🌱 Green Hero", color: "#4ade80" };
  }
  if (ratio >= 0.5) {
    return { label: "♻️ Eco Planner", color: "#a3e635" };
  }
  if (ratio >= 0.25) {
    return { label: "⚠️ City Planner", color: "#fbbf24" };
  }
  return { label: "☠️ Carbon Criminal", color: "#f87171" };
}

export function getEndSummary(state: GameState): EndSummary {
  if (state.gameOverReason === "bankruptcy") {
    return {
      title: "BANKRUPT!",
      subtitle: "Financial collapse halted the challenge.",
      color: "#ef4444"
    };
  }
  if (state.gameOverReason === "collapse") {
    return {
      title: "City Collapsed!",
      subtitle: "Carbon overload destroyed the city.",
      color: "#ef4444"
    };
  }
  if (state.gameOverReason === "health") {
    return {
      title: "City Collapsed!",
      subtitle: "The city could not survive the environmental damage.",
      color: "#ef4444"
    };
  }
  if (state.carbonLevel < 60) {
    return {
      title: "City Survived!",
      subtitle: "Green City! Outstanding teamwork.",
      color: "#22c55e"
    };
  }
  if (state.carbonLevel < 80) {
    return {
      title: "City Survived!",
      subtitle: "Recovering City. Room to improve.",
      color: "#22c55e"
    };
  }
  return {
    title: "City Survived!",
    subtitle: "City in Crisis. Barely made it.",
    color: "#22c55e"
  };
}
