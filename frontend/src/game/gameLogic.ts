import { BOARD_TILES, DECISION_CARDS } from "./cards";
import type {
  ChoiceType,
  DecisionCard,
  EndSummary,
  EventCard,
  GameOverReason,
  GameState,
  PlayerState,
  Winner,
  WinnerSummary
} from "./types";

export const STARTING_BUDGET = 65_000;
export const STARTING_CARBON = 42;
export const STARTING_HEALTH = 78;
export const STARTING_RESILIENCE = 20;
export const TOTAL_ROUNDS = 12;

function clamp(value: number, minimum: number, maximum: number): number {
  return Math.max(minimum, Math.min(maximum, value));
}

function createPlayer(name: string): PlayerState {
  return {
    name,
    budget: STARTING_BUDGET,
    support: 50,
    greenPoints: 0,
    ecoChoices: 0,
    quickChoices: 0,
    policies: [],
    tile: 0,
    decisions: 0,
    bankrupt: false,
    carbonContribution: 0
  };
}

function syncPlayer(player: PlayerState): PlayerState {
  const decisions = player.ecoChoices + player.quickChoices;
  return {
    ...player,
    decisions,
    bankrupt: player.budget <= 0
  };
}

function syncState(state: GameState): GameState {
  const player1 = syncPlayer({ ...state.player1 });
  const player2 = syncPlayer({ ...state.player2 });
  return {
    ...state,
    player1,
    player2,
    carbonLevel: state.carbon,
    cityHealth: state.health,
    currentCard: state.selectedCard,
    zoneScores: {
      transport: 0,
      energy: 0,
      waste: 0,
      greenspace: 0
    }
  };
}

function drawDecisionCard(zone: string, excludeId?: string, randomValue = Math.random): DecisionCard {
  const zoneCards = DECISION_CARDS.filter((card) => card.zone === zone && card.id !== excludeId);
  const pool = zoneCards.length > 0 ? zoneCards : DECISION_CARDS.filter((card) => card.id !== excludeId);
  const source = pool.length > 0 ? pool : DECISION_CARDS;
  const index = Math.floor(randomValue() * source.length);
  return source[index]!;
}

function applyEffect(state: GameState, player: PlayerState, effect: [number, number, number, number, number]) {
  let [carbonDelta, healthDelta, budgetDelta, supportDelta, greenPoints] = effect;
  if (state.carbon >= 80 && carbonDelta > 0) {
    carbonDelta += 2;
  }
  if (state.resilience >= 50 && healthDelta < 0) {
    healthDelta += 2;
  }

  state.carbon = clamp(state.carbon + carbonDelta, 0, 100);
  state.health = clamp(state.health + healthDelta, 0, 100);
  player.budget = Math.max(0, player.budget + budgetDelta);
  player.support = clamp(player.support + supportDelta, 0, 100);
  player.greenPoints += greenPoints;
  player.carbonContribution += carbonDelta;
  if (greenPoints > 0) {
    state.resilience = clamp(state.resilience + greenPoints * 2, 0, 100);
  }
}

function unlockPolicies(state: GameState, player: PlayerState, messages: string[]) {
  if (player.ecoChoices >= 3 && !player.policies.includes("Carbon Tax")) {
    player.policies = [...player.policies, "Carbon Tax"];
    state.carbon = clamp(state.carbon - 5, 0, 100);
    messages.push("Policy unlocked: Carbon Tax lowers city carbon.");
  }
  if (player.support >= 70 && !player.policies.includes("Citizen Volunteers")) {
    player.policies = [...player.policies, "Citizen Volunteers"];
    state.health = clamp(state.health + 5, 0, 100);
    state.resilience = clamp(state.resilience + 8, 0, 100);
    messages.push("Policy unlocked: Citizen Volunteers improve health.");
  }
}

function endGame(state: GameState, reason: GameOverReason): GameState {
  const scores = calculateScores(state);
  return syncState({
    ...state,
    gameOver: true,
    gameOverReason: reason,
    winner: scores[0] === scores[1] ? "draw" : scores[0] > scores[1] ? 1 : 2,
    scores,
    phase: "end",
    selectedCard: null,
    selectedEvent: null
  });
}

export function createInitialState(): GameState {
  return syncState({
    round: 1,
    maxRounds: TOTAL_ROUNDS,
    currentPlayer: 1,
    carbon: STARTING_CARBON,
    health: STARTING_HEALTH,
    resilience: STARTING_RESILIENCE,
    dice: 1,
    message: "Roll the dice. Land on a district and solve its decision.",
    player1: createPlayer("Player 1"),
    player2: createPlayer("Player 2"),
    boardTiles: BOARD_TILES,
    selectedCard: null,
    selectedEvent: null,
    gameOver: false,
    gameOverReason: null,
    winner: null,
    scores: null,
    phase: "play",
    lastMove: null,
    carbonLevel: STARTING_CARBON,
    cityHealth: STARTING_HEALTH,
    currentCard: null,
    zoneScores: { transport: 0, energy: 0, waste: 0, greenspace: 0 }
  });
}

export function rollDice(state: GameState, randomValue = Math.random): GameState {
  if (state.gameOver || state.selectedCard || state.selectedEvent) {
    return state;
  }

  const nextState: GameState = {
    ...state,
    player1: { ...state.player1 },
    player2: { ...state.player2 },
    boardTiles: [...state.boardTiles],
    selectedCard: state.selectedCard,
    selectedEvent: state.selectedEvent,
    scores: state.scores ? [...state.scores] as [number, number] : null,
    lastMove: state.lastMove ? { ...state.lastMove, effect: [...state.lastMove.effect] as [number, number, number, number, number] } : null,
    currentCard: state.currentCard,
    zoneScores: { ...state.zoneScores }
  };

  const playerKey = nextState.currentPlayer === 1 ? "player1" : "player2";
  const actingPlayer = { ...nextState[playerKey] };
  const dice = Math.floor(randomValue() * 6) + 1;
  actingPlayer.tile = (actingPlayer.tile + dice) % nextState.boardTiles.length;
  nextState[playerKey] = actingPlayer;
  nextState.dice = dice;
  const zone = nextState.boardTiles[actingPlayer.tile]!.zone;
  nextState.selectedCard = drawDecisionCard(zone, nextState.selectedCard?.id, randomValue);
  nextState.selectedEvent = null;
  nextState.message = `${actingPlayer.name} rolled ${dice} and landed on ${zone}.`;
  nextState.phase = "play";
  return syncState(nextState);
}

export function makeChoice(state: GameState, choice: ChoiceType): GameState {
  if (state.gameOver) {
    return state;
  }
  if (!state.selectedCard && !state.selectedEvent) {
    return state;
  }

  const nextState: GameState = {
    ...state,
    player1: { ...state.player1 },
    player2: { ...state.player2 },
    boardTiles: [...state.boardTiles],
    selectedCard: state.selectedCard,
    selectedEvent: state.selectedEvent,
    scores: state.scores ? [...state.scores] as [number, number] : null,
    lastMove: null,
    currentCard: state.currentCard,
    zoneScores: { ...state.zoneScores }
  };

  const playerKey = nextState.currentPlayer === 1 ? "player1" : "player2";
  const actingPlayer = { ...nextState[playerKey] };
  nextState[playerKey] = actingPlayer;

  if (nextState.selectedEvent) {
    applyEffect(nextState, actingPlayer, nextState.selectedEvent.effect);
    nextState.selectedEvent = null;
    nextState.message = `${actingPlayer.name} resolved the event.`;
  } else if (nextState.selectedCard) {
    const card = nextState.selectedCard;
    const effect = choice === "eco" ? card.ecoEffect : card.quickEffect;
    applyEffect(nextState, actingPlayer, effect);
    if (choice === "eco") {
      actingPlayer.ecoChoices += 1;
      nextState.message = `${actingPlayer.name} chose the sustainable plan.`;
    } else {
      actingPlayer.quickChoices += 1;
      nextState.message = `${actingPlayer.name} chose the cheaper quick fix.`;
    }
    const unlockMessages: string[] = [];
    unlockPolicies(nextState, actingPlayer, unlockMessages);
    if (unlockMessages.length > 0) {
      nextState.message = `${nextState.message} ${unlockMessages.join(" ")}`;
    }
    nextState.lastMove = {
      player: nextState.currentPlayer,
      choice,
      zone: card.zone,
      cardId: card.id,
      choiceLabel: choice === "eco" ? card.eco : card.quick,
      effect,
      timestamp: Date.now()
    };
    nextState.selectedCard = null;
  }

  nextState[playerKey] = syncPlayer(actingPlayer);

  if (actingPlayer.budget <= 0) {
    nextState.message = `${actingPlayer.name} went bankrupt.`;
    return endGame(nextState, "bankruptcy");
  }
  if (nextState.carbon >= 100 || nextState.health <= 0) {
    nextState.message = "The city collapsed from environmental damage.";
    return endGame(nextState, "collapse");
  }

  if (nextState.currentPlayer === 2) {
    nextState.round += 1;
  }
  nextState.currentPlayer = nextState.currentPlayer === 1 ? 2 : 1;

  if (nextState.round > nextState.maxRounds) {
    nextState.message = "The final round is complete.";
    return endGame(nextState, "rounds_complete");
  }

  return syncState(nextState);
}

export function calculateScores(state: GameState): [number, number] {
  const scorePlayer = (player: PlayerState) => {
    let score = player.greenPoints * 10 + player.support + Math.floor(player.budget / 2000) + state.health + (100 - state.carbon) + player.policies.length * 12;
    if (player.budget <= 0) {
      score -= 80;
    }
    return score;
  };

  return [scorePlayer(state.player1), scorePlayer(state.player2)];
}

export function checkWinner(state: GameState): Winner {
  const scores = state.scores ?? calculateScores(state);
  if (scores[0] === scores[1]) {
    return "draw";
  }
  return scores[0] > scores[1] ? 1 : 2;
}

export function getWinnerSummary(state: GameState): WinnerSummary {
  const winner = state.winner ?? checkWinner(state);
  if (winner === "draw") {
    return {
      winner,
      winnerName: null,
      loserName: null,
      reason: "Scores were tied after the final round"
    };
  }

  const winnerPlayer = winner === 1 ? state.player1 : state.player2;
  const loserPlayer = winner === 1 ? state.player2 : state.player1;
  return {
    winner,
    winnerName: winnerPlayer.name,
    loserName: loserPlayer.name,
    reason: state.gameOverReason === "bankruptcy" ? `${loserPlayer.name} went bankrupt` : "earned the highest city score"
  };
}

export function getPlayerRating(player: PlayerState): { label: string; color: string } {
  const ratio = player.decisions > 0 ? player.ecoChoices / player.decisions : 0;
  if (ratio >= 0.75) {
    return { label: "Green Hero", color: "#4ade80" };
  }
  if (ratio >= 0.5) {
    return { label: "Eco Planner", color: "#a3e635" };
  }
  if (ratio >= 0.25) {
    return { label: "City Planner", color: "#fbbf24" };
  }
  return { label: "Carbon Criminal", color: "#f87171" };
}

export function getEndSummary(state: GameState): EndSummary {
  return {
    title: state.carbon < 80 && state.health > 0 ? "City Survived!" : "Challenge Ended",
    subtitle: state.message,
    color: state.carbon < 80 && state.health > 0 ? "#22c55e" : "#ef4444"
  };
}

