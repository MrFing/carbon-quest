from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Literal, Optional

Zone = Literal["Transport", "Energy", "Waste", "Green Space", "Consumption", "Community"]
ChoiceType = Literal["eco", "quick"]
GameOverReason = Literal["bankruptcy", "collapse", "rounds_complete"]
WinnerType = Literal[1, 2, "draw"]
EffectTuple = tuple[int, int, int, int, int]

STARTING_BUDGET = 65_000
STARTING_CARBON = 42
STARTING_HEALTH = 78
STARTING_RESILIENCE = 20
TOTAL_ROUNDS = 12
BOARD_ZONES: tuple[Zone, ...] = (
    "Transport",
    "Energy",
    "Waste",
    "Green Space",
    "Consumption",
    "Community",
) * 4


def clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))


@dataclass(frozen=True)
class DecisionCard:
    id: str
    title: str
    zone: Zone
    eco: str
    quick: str
    eco_effect: EffectTuple
    quick_effect: EffectTuple
    fact: str

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "zone": self.zone,
            "eco": self.eco,
            "quick": self.quick,
            "ecoEffect": list(self.eco_effect),
            "quickEffect": list(self.quick_effect),
            "fact": self.fact,
            "ecoChoice": _serialize_choice(self.eco, self.eco_effect),
            "quickChoice": _serialize_choice(self.quick, self.quick_effect),
        }


@dataclass(frozen=True)
class EventCard:
    id: str
    title: str
    text: str
    effect: EffectTuple

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "text": self.text,
            "effect": list(self.effect),
        }


def _serialize_choice(label: str, effect: EffectTuple) -> dict:
    carbon_delta, health_delta, cost_delta, support_delta, green_points = effect
    return {
        "label": label,
        "carbonDelta": carbon_delta,
        "healthDelta": health_delta,
        "cost": abs(cost_delta),
        "supportDelta": support_delta,
        "greenPoints": green_points,
    }


DECISION_CARDS: tuple[DecisionCard, ...] = (
    DecisionCard(
        "rush-hour-problem",
        "Rush-Hour Problem",
        "Transport",
        "Metro + bike parking",
        "More flyovers",
        (-9, 4, -8500, 5, 4),
        (10, -3, -2500, -4, 0),
        "Public transport reduces emissions per passenger and traffic pollution.",
    ),
    DecisionCard(
        "electricity-demand",
        "Electricity Demand",
        "Energy",
        "Solar plus battery storage",
        "Coal backup plant",
        (-12, 5, -12000, 4, 5),
        (14, -8, -2200, -6, 0),
        "Renewable energy costs more at first but lowers future carbon.",
    ),
    DecisionCard(
        "market-waste",
        "Market Waste",
        "Waste",
        "Recycling and compost hubs",
        "Open dumping site",
        (-6, 5, -4200, 3, 3),
        (8, -7, -1200, -5, 0),
        "Separating waste cuts landfill methane and keeps streets cleaner.",
    ),
    DecisionCard(
        "vacant-land",
        "Vacant Land",
        "Green Space",
        "Urban forest and rain garden",
        "Shopping complex",
        (-8, 7, -6000, 2, 4),
        (9, -5, -1500, -2, 1),
        "Green spaces absorb carbon, reduce heat, and improve public health.",
    ),
    DecisionCard(
        "food-habits",
        "Food Habits",
        "Consumption",
        "Local low-meat food campaign",
        "Mega fast-food drive",
        (-5, 3, -3000, 6, 3),
        (7, -3, -900, -3, 0),
        "Consumption choices also create carbon through transport and packaging.",
    ),
    DecisionCard(
        "neighbourhood-plan",
        "Neighbourhood Plan",
        "Community",
        "Library and community garden",
        "Cut public programs",
        (-4, 6, -5200, 8, 3),
        (5, -6, -700, -8, 0),
        "Community projects build support for long-term climate action.",
    ),
    DecisionCard(
        "airport-expansion",
        "Airport Expansion",
        "Transport",
        "Rail link to airport",
        "Add new runway",
        (-5, 3, -7000, 3, 3),
        (13, -2, -3000, -4, 0),
        "Travel infrastructure changes carbon footprints for many years.",
    ),
    DecisionCard(
        "power-shortage",
        "Power Shortage",
        "Energy",
        "Wind farm partnership",
        "Diesel generator contracts",
        (-9, 4, -9000, 2, 4),
        (11, -5, -2000, -4, 0),
        "Short-term cheap energy can create long-term pollution costs.",
    ),
)

EVENT_CARDS: tuple[EventCard, ...] = (
    EventCard(
        "heat-wave",
        "Heat Wave",
        "High carbon makes heat worse. Resilience protects the city.",
        (7, -8, -2000, -4, 0),
    ),
    EventCard(
        "climate-grant",
        "Climate Grant",
        "A national grant rewards green planning.",
        (-3, 2, 7000, 5, 2),
    ),
    EventCard(
        "public-protest",
        "Public Protest",
        "Citizens demand cleaner transport and waste systems.",
        (2, -2, -1000, -8, 0),
    ),
    EventCard(
        "innovation-fair",
        "Innovation Fair",
        "Clean technology becomes cheaper this round.",
        (-4, 1, 3000, 4, 2),
    ),
    EventCard(
        "flood-warning",
        "Flood Warning",
        "Green spaces and resilience reduce damage.",
        (5, -6, -3000, -3, 0),
    ),
)


class CarbonQuestGame:
    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)
        self.reset()

    def reset(self) -> None:
        self.round = 1
        self.max_rounds = TOTAL_ROUNDS
        self.current_player: Literal[1, 2] = 1
        self.carbon = STARTING_CARBON
        self.health = STARTING_HEALTH
        self.resilience = STARTING_RESILIENCE
        self.dice = 1
        self.message = "Roll the dice. Land on a district and solve its decision."
        self.player1 = self._create_player("Player 1")
        self.player2 = self._create_player("Player 2")
        self.board_tiles = [
            {"index": index, "zone": zone}
            for index, zone in enumerate(BOARD_ZONES)
        ]
        self.selected_card: Optional[DecisionCard] = None
        self.selected_event: Optional[EventCard] = None
        self.game_over = False
        self.game_over_reason: Optional[GameOverReason] = None
        self.winner: Optional[WinnerType] = None
        self.scores: Optional[tuple[int, int]] = None
        self.phase = "play"
        self.last_move: Optional[dict] = None

    def _create_player(self, name: str) -> dict:
        return {
            "name": name,
            "budget": STARTING_BUDGET,
            "support": 50,
            "greenPoints": 0,
            "ecoChoices": 0,
            "quickChoices": 0,
            "policies": [],
            "tile": 0,
            "decisions": 0,
            "bankrupt": False,
            "carbonContribution": 0,
        }

    def _player_state(self, player: int) -> dict:
        return self.player1 if player == 1 else self.player2

    def _sync_player(self, player: dict) -> dict:
        player["decisions"] = player["ecoChoices"] + player["quickChoices"]
        player["bankrupt"] = player["budget"] <= 0
        return player

    def _serialize_players(self) -> tuple[dict, dict]:
        return self._sync_player(self.player1.copy()), self._sync_player(self.player2.copy())

    def _draw_decision_card(self, zone: Zone) -> DecisionCard:
        zone_cards = [card for card in DECISION_CARDS if card.zone == zone]
        pool = zone_cards or list(DECISION_CARDS)
        return self._rng.choice(pool)

    def _apply_effect(self, effect: EffectTuple, actor: dict) -> None:
        carbon_delta, health_delta, budget_delta, support_delta, green_points = effect
        if self.carbon >= 80 and carbon_delta > 0:
            carbon_delta += 2
        if self.resilience >= 50 and health_delta < 0:
            health_delta += 2

        self.carbon = clamp(self.carbon + carbon_delta, 0, 100)
        self.health = clamp(self.health + health_delta, 0, 100)
        actor["budget"] = max(0, actor["budget"] + budget_delta)
        actor["support"] = clamp(actor["support"] + support_delta, 0, 100)
        actor["greenPoints"] += green_points
        actor["carbonContribution"] += carbon_delta
        if green_points > 0:
            self.resilience = clamp(self.resilience + green_points * 2, 0, 100)

    def _unlock_policies(self, actor: dict) -> list[str]:
        unlocked: list[str] = []
        if actor["ecoChoices"] >= 3 and "Carbon Tax" not in actor["policies"]:
            actor["policies"] = [*actor["policies"], "Carbon Tax"]
            self.carbon = clamp(self.carbon - 5, 0, 100)
            unlocked.append("Policy unlocked: Carbon Tax lowers city carbon.")
        if actor["support"] >= 70 and "Citizen Volunteers" not in actor["policies"]:
            actor["policies"] = [*actor["policies"], "Citizen Volunteers"]
            self.health = clamp(self.health + 5, 0, 100)
            self.resilience = clamp(self.resilience + 8, 0, 100)
            unlocked.append("Policy unlocked: Citizen Volunteers improve health.")
        return unlocked

    def roll_dice(self, player: int) -> dict:
        if self.game_over:
            raise ValueError("The game is already over.")
        if player != self.current_player:
            raise ValueError("It is not your turn.")
        if self.selected_card is not None or self.selected_event is not None:
            raise ValueError("Resolve the current decision before rolling again.")

        actor = self._player_state(player)
        self.dice = self._rng.randint(1, 6)
        actor["tile"] = (actor["tile"] + self.dice) % len(self.board_tiles)
        zone = self.board_tiles[actor["tile"]]["zone"]
        self.selected_card = self._draw_decision_card(zone)
        self.selected_event = None
        self.message = f"{actor['name']} rolled {self.dice} and landed on {zone}."
        self.phase = "play"
        return self.get_state()

    def make_choice(self, player: int, choice: ChoiceType) -> dict:
        if self.game_over:
            raise ValueError("The game is already over.")
        if player != self.current_player:
            raise ValueError("It is not your turn.")
        if choice not in ("eco", "quick"):
            raise ValueError("Choice must be 'eco' or 'quick'.")
        if self.selected_card is None and self.selected_event is None:
            raise ValueError("Roll the dice first.")

        actor = self._player_state(player)

        if self.selected_event is not None:
            self._apply_effect(self.selected_event.effect, actor)
            self.selected_event = None
            self.message = f"{actor['name']} resolved the event."
        else:
            card = self.selected_card
            assert card is not None
            effect = card.eco_effect if choice == "eco" else card.quick_effect
            self._apply_effect(effect, actor)
            if choice == "eco":
                actor["ecoChoices"] += 1
                self.message = f"{actor['name']} chose the sustainable plan."
            else:
                actor["quickChoices"] += 1
                self.message = f"{actor['name']} chose the cheaper quick fix."

            unlock_messages = self._unlock_policies(actor)
            if unlock_messages:
                self.message = f"{self.message} {' '.join(unlock_messages)}"

            self.last_move = {
                "player": player,
                "choice": choice,
                "zone": card.zone,
                "cardId": card.id,
                "choiceLabel": card.eco if choice == "eco" else card.quick,
                "effect": list(effect),
                "timestamp": None,
            }
            self.selected_card = None

        self._sync_player(actor)

        if actor["budget"] <= 0:
            self.message = f"{actor['name']} went bankrupt."
            return self._end_game("bankruptcy")
        if self.carbon >= 100 or self.health <= 0:
            self.message = "The city collapsed from environmental damage."
            return self._end_game("collapse")

        if self.current_player == 2:
            self.round += 1
        self.current_player = 2 if self.current_player == 1 else 1

        if self.round > self.max_rounds:
            self.message = "The final round is complete."
            return self._end_game("rounds_complete")

        return self.get_state()

    def _calculate_scores(self) -> tuple[int, int]:
        def score_player(player: dict) -> int:
            score = (
                player["greenPoints"] * 10
                + player["support"]
                + player["budget"] // 2000
                + self.health
                + (100 - self.carbon)
                + len(player["policies"]) * 12
            )
            if player["budget"] <= 0:
                score -= 80
            return score

        return score_player(self.player1), score_player(self.player2)

    def _determine_winner(self, scores: tuple[int, int]) -> WinnerType:
        if scores[0] == scores[1]:
            return "draw"
        return 1 if scores[0] > scores[1] else 2

    def _end_game(self, reason: GameOverReason) -> dict:
        self.game_over = True
        self.game_over_reason = reason
        self.phase = "end"
        self.selected_card = None
        self.selected_event = None
        self.scores = self._calculate_scores()
        self.winner = self._determine_winner(self.scores)
        return self.get_state()

    def get_state(self) -> dict:
        player1, player2 = self._serialize_players()
        state = {
            "round": self.round,
            "maxRounds": self.max_rounds,
            "currentPlayer": self.current_player,
            "carbon": self.carbon,
            "health": self.health,
            "resilience": self.resilience,
            "dice": self.dice,
            "message": self.message,
            "player1": player1,
            "player2": player2,
            "boardTiles": [tile.copy() for tile in self.board_tiles],
            "selectedCard": None if self.selected_card is None else self.selected_card.serialize(),
            "selectedEvent": None if self.selected_event is None else self.selected_event.serialize(),
            "gameOver": self.game_over,
            "gameOverReason": self.game_over_reason,
            "winner": self.winner,
            "scores": None if self.scores is None else list(self.scores),
            "phase": self.phase,
            "lastMove": None if self.last_move is None else self.last_move.copy(),
            "carbonLevel": self.carbon,
            "cityHealth": self.health,
            "currentCard": None if self.selected_card is None else self.selected_card.serialize(),
            "zoneScores": {
                "transport": 0,
                "energy": 0,
                "waste": 0,
                "greenspace": 0,
            },
        }
        return state
