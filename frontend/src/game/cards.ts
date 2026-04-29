import type { DecisionCard } from "./types";

function card(
  id: string,
  zone: DecisionCard["zone"],
  title: string,
  ecoLabel: string,
  ecoCarbon: number,
  ecoHealth: number,
  ecoCost: number,
  quickLabel: string,
  quickCarbon: number,
  quickHealth: number,
  quickCost: number
): DecisionCard {
  return {
    id,
    zone,
    title,
    ecoChoice: {
      label: ecoLabel,
      carbonDelta: ecoCarbon,
      healthDelta: ecoHealth,
      cost: ecoCost
    },
    quickChoice: {
      label: quickLabel,
      carbonDelta: quickCarbon,
      healthDelta: quickHealth,
      cost: quickCost
    }
  };
}

export const DECISION_CARDS: DecisionCard[] = [
  card("downtown-commute-plan", "transport", "Downtown Commute Plan", "Build a Metro Line", -8, 5, 8500, "Add More Highways", 10, -3, 800),
  card("neighborhood-streets", "transport", "Neighborhood Streets", "Install Bike Lanes", -5, 3, 4200, "Add More Highways", 10, -3, 800),
  card("regional-expansion", "transport", "Regional Expansion", "Build a Metro Line", -8, 5, 8500, "Expand Airport", 12, -2, 700),
  card("power-grid-upgrade", "energy", "Power Grid Upgrade", "Build Solar Farm", -10, 8, 12000, "Build Coal Plant", 15, -10, 600),
  card("future-energy-mix", "energy", "Future Energy Mix", "Wind Turbines", -8, 6, 9500, "Natural Gas Plant", 8, -4, 700),
  card("industrial-demand-spike", "energy", "Industrial Demand Spike", "Build Solar Farm", -10, 8, 12000, "Natural Gas Plant", 8, -4, 700),
  card("regional-reliability-vote", "energy", "Regional Reliability Vote", "Wind Turbines", -8, 6, 9500, "Build Coal Plant", 15, -10, 600),
  card("community-waste-strategy", "waste", "Community Waste Strategy", "Recycling Program", -4, 4, 3500, "Open Landfill", 6, -5, 300),
  card("food-waste-response", "waste", "Food Waste Response", "Composting Initiative", -3, 3, 2800, "Open Landfill", 6, -5, 300),
  card("school-sustainability-drive", "waste", "School Sustainability Drive", "Recycling Program", -4, 4, 3500, "Open Landfill", 6, -5, 300),
  card("vacant-lot-decision", "greenspace", "Vacant Lot Decision", "Plant Urban Forest", -7, 7, 5500, "Build Shopping Mall", 9, -6, 400),
  card("riverfront-redevelopment", "greenspace", "Riverfront Redevelopment", "Plant Urban Forest", -7, 7, 5500, "Build Shopping Mall", 9, -6, 400),
  card("tourism-growth-debate", "transport", "Tourism Growth Debate", "Install Bike Lanes", -5, 3, 4200, "Expand Airport", 12, -2, 700),
  card("industrial-overflow", "waste", "Industrial Overflow", "Waste to Energy Plant", -6, 4, 7000, "Open Landfill", 6, -5, 300),
  card("city-cleanup-campaign", "waste", "City Cleanup Campaign", "Zero Waste Policy", -8, 6, 6500, "Open Landfill", 6, -5, 300),
  card("school-recycling-drive", "waste", "School Recycling Drive", "Composting Initiative", -3, 3, 2800, "Open Landfill", 6, -5, 300),
  card("rooftop-revolution", "greenspace", "Rooftop Revolution", "Green Rooftop Program", -5, 6, 6000, "Build Shopping Mall", 9, -6, 400),
  card("community-garden-vote", "greenspace", "Community Garden Vote", "Urban Farm Network", -4, 5, 4500, "Build Shopping Mall", 9, -6, 400),
  card("solar-or-trees-debate", "greenspace", "Solar or Trees Debate", "Community Solar Garden", -7, 5, 8000, "Build Shopping Mall", 9, -6, 400),
  card("clean-energy-summit", "energy", "Clean Energy Summit", "Geothermal Plant", -9, 7, 11000, "Build Coal Plant", 15, -10, 600)
];
