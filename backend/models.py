from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

Zone = Literal["Transport", "Energy", "Waste", "Green Space", "Consumption", "Community"]
ChoiceType = Literal["eco", "quick"]
GameOverReason = Literal["bankruptcy", "collapse", "rounds_complete"]
WinnerType = Literal[1, 2, "draw"]
PhaseType = Literal["play", "end"]


class ChoiceSummaryModel(BaseModel):
    label: str
    carbonDelta: int
    healthDelta: int
    cost: int
    supportDelta: int
    greenPoints: int


class DecisionCardModel(BaseModel):
    id: str
    title: str
    zone: Zone
    eco: str
    quick: str
    ecoEffect: list[int] = Field(min_length=5, max_length=5)
    quickEffect: list[int] = Field(min_length=5, max_length=5)
    fact: str
    ecoChoice: ChoiceSummaryModel
    quickChoice: ChoiceSummaryModel


class EventCardModel(BaseModel):
    id: str
    title: str
    text: str
    effect: list[int] = Field(min_length=5, max_length=5)


class TileModel(BaseModel):
    index: int
    zone: Zone


class PlayerStateModel(BaseModel):
    name: str
    budget: int
    support: int
    greenPoints: int
    ecoChoices: int
    quickChoices: int
    policies: list[str]
    tile: int
    decisions: int
    bankrupt: bool
    carbonContribution: int


class LastMoveModel(BaseModel):
    player: Literal[1, 2]
    choice: ChoiceType
    zone: Zone
    cardId: str
    choiceLabel: str
    effect: list[int] = Field(min_length=5, max_length=5)
    timestamp: Optional[int] = None


class GameStateModel(BaseModel):
    round: int = Field(ge=1, le=13)
    maxRounds: int = Field(ge=1, le=12)
    currentPlayer: Literal[1, 2]
    carbon: int = Field(ge=0, le=100)
    health: int = Field(ge=0, le=100)
    resilience: int = Field(ge=0, le=100)
    dice: int = Field(ge=1, le=6)
    message: str
    player1: PlayerStateModel
    player2: PlayerStateModel
    boardTiles: list[TileModel]
    selectedCard: Optional[DecisionCardModel] = None
    selectedEvent: Optional[EventCardModel] = None
    gameOver: bool
    gameOverReason: Optional[GameOverReason] = None
    winner: Optional[WinnerType] = None
    scores: Optional[list[int]] = None
    phase: PhaseType
    lastMove: Optional[LastMoveModel] = None
    carbonLevel: int = Field(ge=0, le=100)
    cityHealth: int = Field(ge=0, le=100)
    currentCard: Optional[DecisionCardModel] = None
    zoneScores: dict[str, int]


class PartyResponse(BaseModel):
    code: str
    sessionId: str


class ErrorMessage(BaseModel):
    type: str = "ERROR"
    message: str
