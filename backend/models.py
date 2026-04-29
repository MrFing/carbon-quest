from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


Zone = Literal["transport", "energy", "waste", "greenspace"]
ChoiceType = Literal["eco", "quick"]
GameOverReason = Literal["bankruptcy", "collapse", "health", "rounds_complete"]
WinnerType = Literal[1, 2, "draw"]
PhaseType = Literal["playing", "gameover"]


class ChoiceModel(BaseModel):
    label: str
    carbonDelta: int
    healthDelta: int
    cost: int


class DecisionCardModel(BaseModel):
    id: str
    zone: Zone
    title: str
    ecoChoice: ChoiceModel
    quickChoice: ChoiceModel


class PlayerStateModel(BaseModel):
    name: str
    budget: int
    ecoChoices: int
    quickChoices: int
    carbonContribution: int
    bankrupt: bool
    decisions: int


class LastMoveModel(BaseModel):
    player: Literal[1, 2]
    choice: ChoiceType
    zone: Zone
    cardId: str
    choiceLabel: str
    carbonDelta: int
    healthDelta: int
    cost: int
    timestamp: int


class GameStateModel(BaseModel):
    round: int = Field(ge=1, le=15)
    currentPlayer: Literal[1, 2]
    carbonLevel: int = Field(ge=0, le=100)
    cityHealth: int = Field(ge=0, le=100)
    player1: PlayerStateModel
    player2: PlayerStateModel
    currentCard: DecisionCardModel
    zoneScores: dict[Zone, int]
    gameOver: bool
    gameOverReason: Optional[GameOverReason] = None
    winner: Optional[WinnerType] = None
    phase: PhaseType
    lastMove: Optional[LastMoveModel] = None


class PartyResponse(BaseModel):
    code: str
    sessionId: str


class ErrorMessage(BaseModel):
    type: str = "ERROR"
    message: str
