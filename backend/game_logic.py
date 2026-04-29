from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Literal, Optional


Zone = Literal["transport", "energy", "waste", "greenspace"]
ChoiceType = Literal["eco", "quick"]
WinnerType = Literal[1, 2, "draw"]

STARTING_BUDGET = 100_000
STARTING_CARBON = 30
STARTING_HEALTH = 100
TOTAL_ROUNDS = 15


def clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))


@dataclass(frozen=True)
class Choice:
    label: str
    carbon_delta: int
    health_delta: int
    cost: int


@dataclass(frozen=True)
class DecisionCard:
    id: str
    zone: Zone
    title: str
    eco_choice: Choice
    quick_choice: Choice


def _card(
    card_id: str,
    zone: Zone,
    title: str,
    eco_label: str,
    eco_carbon: int,
    eco_health: int,
    eco_cost: int,
    quick_label: str,
    quick_carbon: int,
    quick_health: int,
    quick_cost: int,
) -> DecisionCard:
    return DecisionCard(
        id=card_id,
        zone=zone,
        title=title,
        eco_choice=Choice(eco_label, eco_carbon, eco_health, eco_cost),
        quick_choice=Choice(quick_label, quick_carbon, quick_health, quick_cost),
    )


CARDS: tuple[DecisionCard, ...] = (
    _card("downtown-commute-plan", "transport", "Downtown Commute Plan", "Build a Metro Line", -8, 5, 8500, "Add More Highways", 10, -3, 800),
    _card("neighborhood-streets", "transport", "Neighborhood Streets", "Install Bike Lanes", -5, 3, 4200, "Add More Highways", 10, -3, 800),
    _card("regional-expansion", "transport", "Regional Expansion", "Build a Metro Line", -8, 5, 8500, "Expand Airport", 12, -2, 700),
    _card("power-grid-upgrade", "energy", "Power Grid Upgrade", "Build Solar Farm", -10, 8, 12000, "Build Coal Plant", 15, -10, 600),
    _card("future-energy-mix", "energy", "Future Energy Mix", "Wind Turbines", -8, 6, 9500, "Natural Gas Plant", 8, -4, 700),
    _card("industrial-demand-spike", "energy", "Industrial Demand Spike", "Build Solar Farm", -10, 8, 12000, "Natural Gas Plant", 8, -4, 700),
    _card("regional-reliability-vote", "energy", "Regional Reliability Vote", "Wind Turbines", -8, 6, 9500, "Build Coal Plant", 15, -10, 600),
    _card("community-waste-strategy", "waste", "Community Waste Strategy", "Recycling Program", -4, 4, 3500, "Open Landfill", 6, -5, 300),
    _card("food-waste-response", "waste", "Food Waste Response", "Composting Initiative", -3, 3, 2800, "Open Landfill", 6, -5, 300),
    _card("school-sustainability-drive", "waste", "School Sustainability Drive", "Recycling Program", -4, 4, 3500, "Open Landfill", 6, -5, 300),
    _card("vacant-lot-decision", "greenspace", "Vacant Lot Decision", "Plant Urban Forest", -7, 7, 5500, "Build Shopping Mall", 9, -6, 400),
    _card("riverfront-redevelopment", "greenspace", "Riverfront Redevelopment", "Plant Urban Forest", -7, 7, 5500, "Build Shopping Mall", 9, -6, 400),
    _card("tourism-growth-debate", "transport", "Tourism Growth Debate", "Install Bike Lanes", -5, 3, 4200, "Expand Airport", 12, -2, 700),
    _card("industrial-overflow", "waste", "Industrial Overflow", "Waste to Energy Plant", -6, 4, 7000, "Open Landfill", 6, -5, 300),
    _card("city-cleanup-campaign", "waste", "City Cleanup Campaign", "Zero Waste Policy", -8, 6, 6500, "Open Landfill", 6, -5, 300),
    _card("school-recycling-drive", "waste", "School Recycling Drive", "Composting Initiative", -3, 3, 2800, "Open Landfill", 6, -5, 300),
    _card("rooftop-revolution", "greenspace", "Rooftop Revolution", "Green Rooftop Program", -5, 6, 6000, "Build Shopping Mall", 9, -6, 400),
    _card("community-garden-vote", "greenspace", "Community Garden Vote", "Urban Farm Network", -4, 5, 4500, "Build Shopping Mall", 9, -6, 400),
    _card("solar-or-trees-debate", "greenspace", "Solar or Trees Debate", "Community Solar Garden", -7, 5, 8000, "Build Shopping Mall", 9, -6, 400),
    _card("clean-energy-summit", "energy", "Clean Energy Summit", "Geothermal Plant", -9, 7, 11000, "Build Coal Plant", 15, -10, 600),
)


class CarbonQuestGame:
    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)
        self._last_card_id: Optional[str] = None
        self.reset()

    def reset(self) -> None:
        self.round = 1
        self.current_player: Literal[1, 2] = 1
        self.completed_rounds = 0
        self.carbon_level = STARTING_CARBON
        self.city_health = STARTING_HEALTH
        self.player1 = self._initial_player("Player 1")
        self.player2 = self._initial_player("Player 2")
        self.zone_scores: dict[Zone, int] = {
            "transport": 0,
            "energy": 0,
            "waste": 0,
            "greenspace": 0,
        }
        self.current_card = self._draw_card()
        self.game_over = False
        self.game_over_reason: Optional[str] = None
        self.winner: Optional[WinnerType] = None
        self.phase = "playing"
        self.last_move: Optional[dict] = None

    def _initial_player(self, name: str) -> dict:
        return {
            "name": name,
            "budget": STARTING_BUDGET,
            "ecoChoices": 0,
            "quickChoices": 0,
            "carbonContribution": 0,
            "bankrupt": False,
            "decisions": 0,
        }

    def _draw_card(self) -> DecisionCard:
        pool = [card for card in CARDS if card.id != self._last_card_id]
        if not pool:
            pool = list(CARDS)
        card = self._rng.choice(pool)
        self._last_card_id = card.id
        return card

    def _player_state(self, player: int) -> dict:
        return self.player1 if player == 1 else self.player2

    def make_choice(self, player: int, choice: ChoiceType) -> dict:
        if self.game_over:
            raise ValueError("The game is already over.")
        if player != self.current_player:
            raise ValueError("It is not your turn.")
        if choice not in ("eco", "quick"):
            raise ValueError("Choice must be 'eco' or 'quick'.")

        acting_player = self._player_state(player)
        selected = self.current_card.eco_choice if choice == "eco" else self.current_card.quick_choice

        acting_player["budget"] = max(0, acting_player["budget"] - selected.cost)
        acting_player["decisions"] += 1
        if choice == "eco":
            acting_player["ecoChoices"] += 1
        else:
            acting_player["quickChoices"] += 1
        acting_player["carbonContribution"] += selected.carbon_delta
        if acting_player["budget"] <= 0:
            acting_player["bankrupt"] = True

        self.carbon_level = clamp(self.carbon_level + selected.carbon_delta, 0, 100)
        self.city_health = clamp(self.city_health + selected.health_delta, 0, 100)
        self.zone_scores[self.current_card.zone] += 1 if choice == "eco" else -1
        self.last_move = {
            "player": player,
            "choice": choice,
            "zone": self.current_card.zone,
            "cardId": self.current_card.id,
            "choiceLabel": selected.label,
            "carbonDelta": selected.carbon_delta,
            "healthDelta": selected.health_delta,
            "cost": selected.cost,
            "timestamp": int(time.time() * 1000),
        }

        if acting_player["bankrupt"]:
            self._end_game("bankruptcy")
            return self.get_state()
        if self.carbon_level >= 100:
            self._end_game("collapse")
            return self.get_state()
        if self.city_health <= 0:
            self._end_game("health")
            return self.get_state()

        if player == 2:
            self.completed_rounds += 1
            if self.completed_rounds >= TOTAL_ROUNDS:
                self._end_game("rounds_complete")
                return self.get_state()
            self.round = min(TOTAL_ROUNDS, self.completed_rounds + 1)

        self.current_player = 2 if player == 1 else 1
        self.current_card = self._draw_card()
        return self.get_state()

    def _end_game(self, reason: str) -> None:
        self.game_over = True
        self.game_over_reason = reason
        self.phase = "gameover"
        self.winner = self.determine_winner()

    def determine_winner(self) -> WinnerType:
        if self.game_over_reason == "bankruptcy":
            if self.player1["bankrupt"] and not self.player2["bankrupt"]:
                return 2
            if self.player2["bankrupt"] and not self.player1["bankrupt"]:
                return 1

        if self.player1["carbonContribution"] < self.player2["carbonContribution"]:
            return 1
        if self.player2["carbonContribution"] < self.player1["carbonContribution"]:
            return 2

        if self.player1["ecoChoices"] > self.player2["ecoChoices"]:
            return 1
        if self.player2["ecoChoices"] > self.player1["ecoChoices"]:
            return 2

        if self.player1["budget"] > self.player2["budget"]:
            return 1
        if self.player2["budget"] > self.player1["budget"]:
            return 2
        return "draw"

    def get_state(self) -> dict:
        return {
            "round": self.round,
            "currentPlayer": self.current_player,
            "carbonLevel": self.carbon_level,
            "cityHealth": self.city_health,
            "player1": self.player1.copy(),
            "player2": self.player2.copy(),
            "currentCard": self._serialize_card(self.current_card),
            "zoneScores": self.zone_scores.copy(),
            "gameOver": self.game_over,
            "gameOverReason": self.game_over_reason,
            "winner": self.winner,
            "phase": self.phase,
            "lastMove": None if self.last_move is None else self.last_move.copy(),
        }

    def _serialize_card(self, card: DecisionCard) -> dict:
        return {
            "id": card.id,
            "zone": card.zone,
            "title": card.title,
            "ecoChoice": {
                "label": card.eco_choice.label,
                "carbonDelta": card.eco_choice.carbon_delta,
                "healthDelta": card.eco_choice.health_delta,
                "cost": card.eco_choice.cost,
            },
            "quickChoice": {
                "label": card.quick_choice.label,
                "carbonDelta": card.quick_choice.carbon_delta,
                "healthDelta": card.quick_choice.health_delta,
                "cost": card.quick_choice.cost,
            },
        }
