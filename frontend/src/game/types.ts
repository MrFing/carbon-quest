export type Zone = "transport" | "energy" | "waste" | "greenspace";
export type ChoiceType = "eco" | "quick";
export type Winner = 1 | 2 | "draw" | null;
export type GameOverReason = "bankruptcy" | "collapse" | "health" | "rounds_complete" | null;
export type GamePhase = "playing" | "gameover";

export interface Choice {
  label: string;
  carbonDelta: number;
  healthDelta: number;
  cost: number;
}

export interface DecisionCard {
  id: string;
  zone: Zone;
  title: string;
  ecoChoice: Choice;
  quickChoice: Choice;
}

export interface PlayerState {
  name: string;
  budget: number;
  ecoChoices: number;
  quickChoices: number;
  carbonContribution: number;
  bankrupt: boolean;
  decisions: number;
}

export interface LastMove {
  player: 1 | 2;
  choice: ChoiceType;
  zone: Zone;
  cardId: string;
  choiceLabel: string;
  carbonDelta: number;
  healthDelta: number;
  cost: number;
  timestamp: number;
}

export interface GameState {
  round: number;
  currentPlayer: 1 | 2;
  carbonLevel: number;
  cityHealth: number;
  player1: PlayerState;
  player2: PlayerState;
  currentCard: DecisionCard;
  zoneScores: Record<Zone, number>;
  gameOver: boolean;
  gameOverReason: GameOverReason;
  winner: Winner;
  phase: GamePhase;
  lastMove: LastMove | null;
}

export interface WinnerSummary {
  winner: Winner;
  reason: string | null;
  loserName: string | null;
  winnerName: string | null;
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
  | { type: "MAKE_CHOICE"; choice: ChoiceType }
  | { type: "PLAY_AGAIN" }
  | { type: "QUIT" };
