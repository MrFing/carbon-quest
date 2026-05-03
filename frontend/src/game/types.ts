export type Zone = "Transport" | "Energy" | "Waste" | "Green Space" | "Consumption" | "Community";
export type ChoiceType = "eco" | "quick";
export type Winner = 1 | 2 | "draw" | null;
export type GameOverReason = "bankruptcy" | "collapse" | "rounds_complete" | null;
export type GamePhase = "play" | "end";
export type EffectTuple = [number, number, number, number, number];

export interface ChoiceSummary {
  label: string;
  carbonDelta: number;
  healthDelta: number;
  cost: number;
  supportDelta: number;
  greenPoints: number;
}

export interface DecisionCard {
  id: string;
  title: string;
  zone: Zone;
  eco: string;
  quick: string;
  ecoEffect: EffectTuple;
  quickEffect: EffectTuple;
  fact: string;
  ecoChoice: ChoiceSummary;
  quickChoice: ChoiceSummary;
}

export interface EventCard {
  id: string;
  title: string;
  text: string;
  effect: EffectTuple;
}

export interface Tile {
  index: number;
  zone: Zone;
}

export interface PlayerState {
  name: string;
  budget: number;
  support: number;
  greenPoints: number;
  ecoChoices: number;
  quickChoices: number;
  policies: string[];
  tile: number;
  decisions: number;
  bankrupt: boolean;
  carbonContribution: number;
}

export interface LastMove {
  player: 1 | 2;
  choice: ChoiceType;
  zone: Zone;
  cardId: string;
  choiceLabel: string;
  effect: EffectTuple;
  timestamp: number;
}

export interface GameState {
  round: number;
  maxRounds: number;
  currentPlayer: 1 | 2;
  carbon: number;
  health: number;
  resilience: number;
  dice: number;
  message: string;
  player1: PlayerState;
  player2: PlayerState;
  boardTiles: Tile[];
  selectedCard: DecisionCard | null;
  selectedEvent: EventCard | null;
  gameOver: boolean;
  gameOverReason: GameOverReason;
  winner: Winner;
  scores: [number, number] | null;
  phase: GamePhase;
  lastMove: LastMove | null;
  carbonLevel: number;
  cityHealth: number;
  currentCard: DecisionCard | null;
  zoneScores: Record<string, number>;
}

export interface WinnerSummary {
  winner: Winner;
  winnerName: string | null;
  loserName: string | null;
  reason: string | null;
}

export interface EndSummary {
  title: string;
  subtitle: string;
  color: string;
}

export interface PartyResponse {
  code: string;
  sessionId: string;
}

export type ServerMessage =
  | { type: "PARTY_CREATED"; code: string; sessionId: string }
  | { type: "PLAYER_JOINED" }
  | { type: "GAME_START"; state: GameState }
  | { type: "STATE_UPDATE"; state: GameState }
  | { type: "GAME_OVER"; state: GameState; winner: Winner }
  | { type: "PLAYER_DISCONNECTED"; player?: 1 | 2 }
  | { type: "PARTY_REVOKED" }
  | { type: "ERROR"; message: string };

export type ClientMessage =
  | { type: "ROLL_DICE" }
  | { type: "MAKE_CHOICE"; choice: ChoiceType }
  | { type: "PLAY_AGAIN" }
  | { type: "QUIT" };
