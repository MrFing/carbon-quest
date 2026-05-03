import type { DecisionCard, EffectTuple, EventCard, Tile, Zone } from "./types";

function createChoice(label: string, effect: EffectTuple) {
  return {
    label,
    carbonDelta: effect[0],
    healthDelta: effect[1],
    cost: Math.abs(effect[2]),
    supportDelta: effect[3],
    greenPoints: effect[4]
  };
}

function createDecision(
  id: string,
  title: string,
  zone: Zone,
  eco: string,
  quick: string,
  ecoEffect: EffectTuple,
  quickEffect: EffectTuple,
  fact: string
): DecisionCard {
  return {
    id,
    title,
    zone,
    eco,
    quick,
    ecoEffect,
    quickEffect,
    fact,
    ecoChoice: createChoice(eco, ecoEffect),
    quickChoice: createChoice(quick, quickEffect)
  };
}

function createEvent(id: string, title: string, text: string, effect: EffectTuple): EventCard {
  return { id, title, text, effect };
}

export const BOARD_ZONES: Zone[] = [
  "Transport", "Energy", "Waste", "Green Space", "Consumption", "Community",
  "Transport", "Energy", "Waste", "Green Space", "Consumption", "Community",
  "Transport", "Energy", "Waste", "Green Space", "Consumption", "Community",
  "Transport", "Energy", "Waste", "Green Space", "Consumption", "Community"
];

export const BOARD_TILES: Tile[] = BOARD_ZONES.map((zone, index) => ({ index, zone }));

export const DECISION_CARDS: DecisionCard[] = [
  createDecision(
    "rush-hour-problem",
    "Rush-Hour Problem",
    "Transport",
    "Metro + bike parking",
    "More flyovers",
    [-9, 4, -8500, 5, 4],
    [10, -3, -2500, -4, 0],
    "Public transport reduces emissions per passenger and traffic pollution."
  ),
  createDecision(
    "electricity-demand",
    "Electricity Demand",
    "Energy",
    "Solar plus battery storage",
    "Coal backup plant",
    [-12, 5, -12000, 4, 5],
    [14, -8, -2200, -6, 0],
    "Renewable energy costs more at first but lowers future carbon."
  ),
  createDecision(
    "market-waste",
    "Market Waste",
    "Waste",
    "Recycling and compost hubs",
    "Open dumping site",
    [-6, 5, -4200, 3, 3],
    [8, -7, -1200, -5, 0],
    "Separating waste cuts landfill methane and keeps streets cleaner."
  ),
  createDecision(
    "vacant-land",
    "Vacant Land",
    "Green Space",
    "Urban forest and rain garden",
    "Shopping complex",
    [-8, 7, -6000, 2, 4],
    [9, -5, -1500, -2, 1],
    "Green spaces absorb carbon, reduce heat, and improve public health."
  ),
  createDecision(
    "food-habits",
    "Food Habits",
    "Consumption",
    "Local low-meat food campaign",
    "Mega fast-food drive",
    [-5, 3, -3000, 6, 3],
    [7, -3, -900, -3, 0],
    "Consumption choices also create carbon through transport and packaging."
  ),
  createDecision(
    "neighbourhood-plan",
    "Neighbourhood Plan",
    "Community",
    "Library and community garden",
    "Cut public programs",
    [-4, 6, -5200, 8, 3],
    [5, -6, -700, -8, 0],
    "Community projects build support for long-term climate action."
  ),
  createDecision(
    "airport-expansion",
    "Airport Expansion",
    "Transport",
    "Rail link to airport",
    "Add new runway",
    [-5, 3, -7000, 3, 3],
    [13, -2, -3000, -4, 0],
    "Travel infrastructure changes carbon footprints for many years."
  ),
  createDecision(
    "power-shortage",
    "Power Shortage",
    "Energy",
    "Wind farm partnership",
    "Diesel generator contracts",
    [-9, 4, -9000, 2, 4],
    [11, -5, -2000, -4, 0],
    "Short-term cheap energy can create long-term pollution costs."
  )
];

export const EVENT_CARDS: EventCard[] = [
  createEvent("heat-wave", "Heat Wave", "High carbon makes heat worse. Resilience protects the city.", [7, -8, -2000, -4, 0]),
  createEvent("climate-grant", "Climate Grant", "A national grant rewards green planning.", [-3, 2, 7000, 5, 2]),
  createEvent("public-protest", "Public Protest", "Citizens demand cleaner transport and waste systems.", [2, -2, -1000, -8, 0]),
  createEvent("innovation-fair", "Innovation Fair", "Clean technology becomes cheaper this round.", [-4, 1, 3000, 4, 2]),
  createEvent("flood-warning", "Flood Warning", "Green spaces and resilience reduce damage.", [5, -6, -3000, -3, 0])
];

export const RULES_TEXT = [
  "Objective: survive 12 rounds with low carbon, good city health, enough budget, and high green points.",
  "Players take turns rolling the dice and moving around the digital board.",
  "Each district gives a city-life decision: Transport, Energy, Waste, Green Space, Consumption, or Community.",
  "Eco Plans cost more but reduce carbon, improve health, support, resilience, and green points.",
  "Quick Fixes cost less but usually increase carbon and damage health or public support.",
  "Event tiles create surprises such as heat waves, floods, grants, protests, and innovation fairs.",
  "Policies unlock when players make enough eco choices or gain high support.",
  "The city loses if carbon reaches 100, health reaches 0, or a player goes bankrupt.",
  "Winner: highest final score from green points, support, budget, health, low carbon, and policies."
];

export const ZONE_COLORS: Record<Zone, string> = {
  Transport: "#58b4ff",
  Energy: "#ffd700",
  Waste: "#a67654",
  "Green Space": "#34d399",
  Consumption: "#f472b6",
  Community: "#fb923c"
};
