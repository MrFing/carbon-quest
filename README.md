# Carbon Quest: City Builder Challenge

## What Is It?
A 2-player turn-based digital board game built in Python + Pygame where two players share a city but compete to be the most responsible urban decision maker. The city lives or dies based on their collective choices, but one player can still win by being smarter with money and eco decisions than the other.

---

## Starting Conditions
Every game begins with:
- **Shared Carbon Meter:** starts at 50/100
- **Shared City Health:** starts at 100
- **Each player gets:** $100,000 budget individually
- **15 rounds total** — players alternate turns so each gets 15 decisions

---

## How a Turn Works

1. A **Decision Card** appears on the right panel
2. The card belongs to one of 4 zones: **Transport, Energy, Waste, or Green Space**
3. The card shows a scenario name like *"Community Waste Strategy"* and presents exactly **two choices:**

### ECO CHOICE 🌱
- The environmentally responsible option
- **Costs significantly more money** (e.g. $8,500 for a metro line)
- **Reduces carbon** on the shared meter
- **Improves city health**
- Example: *"Build a Metro Line — Carbon -8, Cost $8,500, Health +5"*

### QUICK CHOICE ⚡
- The cheap, dirty shortcut
- **Costs much less money** (e.g. $1,200)
- **Increases carbon** on the shared meter
- **Damages city health**
- Example: *"Expand Airport — Carbon +12, Cost $1,200, Health -2"*

4. Current player clicks their choice
5. Their budget is deducted, carbon meter shifts, city health updates
6. Turn passes to the other player

---

## The Four Zones

### 🚗 Transport
Decisions about how people move around the city. Metro lines, bike lanes, highways, airport expansion. Eco options build sustainable transit infrastructure. Quick options add more car-centric infrastructure.

### ⚡ Energy
Decisions about how the city powers itself. Solar farms, wind turbines, coal plants, nuclear power. Eco options are expensive but massively reduce carbon. Quick options are cheap but spike carbon and damage health badly.

### 🗑️ Waste
Decisions about how the city handles its garbage. Recycling programs, composting, landfills, zero waste policies. Smaller carbon swings but consistent health impacts.

### 🌳 Green Space
Decisions about land use. Urban forests, community gardens, green rooftops vs shopping malls and commercial development. Balanced carbon and health effects.

---

## What Can End the Game Early

### 💸 Bankruptcy
If any player's budget hits $0 mid-game the game stops immediately. A full screen **BANKRUPT!** overlay appears in red with screen shake. The other player wins instantly regardless of carbon level. End screen shows *"[Winner] Wins! [Loser] ran out of money!"*

### ☠️ Carbon Collapse
If the shared carbon meter hits 100 at any point the city collapses. Game ends immediately. Winner is still determined by who contributed less carbon individually.

### 💔 City Health Zero
If city health drops to 0 the city is unlivable. Game ends. Same winner determination applies.

---

## How the Winner Is Decided

The game tracks each player's **individual carbon contribution** — meaning the net sum of all carbon changes caused by their personal choices across their turns.

**Winner determination order:**

1. **Bankruptcy** — if one player goes bankrupt, the other wins automatically
2. **Carbon contribution** — player whose choices caused less total carbon rise wins
3. **Tiebreaker 1** — player with more eco choices wins
4. **Tiebreaker 2** — player with more remaining budget wins
5. **True tie** — "It's a Draw!"

---

## Budget Strategy

This is where the game gets interesting. Eco choices cost 5–15x more than quick choices:

| Decision | ECO Cost | QUICK Cost |
|---|---|---|
| Build Solar Farm | $12,000 | $1,500 |
| Metro Line | $8,500 | $1,200 |
| Recycling Program | $3,500 | $500 |
| Urban Forest | $5,500 | $800 |

With $100,000 and 15 turns, a player who always picks eco choices will run out around round 10–12. This forces real strategic decisions — do you spend big on eco now or pace yourself? If you go bankrupt before your opponent you lose regardless of how green you played.

---

## Warning Systems

| Budget Remaining | Warning |
|---|---|
| Below $15,000 | Budget turns yellow, "⚠ Low Funds" blinks |
| Below $5,000 | Budget turns red, "⚠ Critical Funds!" + warning beep |
| $0 | Bankruptcy triggered immediately |

Carbon meter also warns:
- At 80+ the meter pulses red with a warning
- Screen shake begins at critical levels

---

## The City Visual

The left panel shows a living city skyline that reacts to decisions:
- **Sky color** shifts from deep blue-purple → warm orange → red as carbon rises
- **Buildings** change color: grey default → green tint after eco choices → red/dark after bad choices
- **Wind turbines** appear in the Energy zone after green energy choices
- **Trees and streetlamps** line the road at the bottom
- **Smoke particles** puff from buildings after quick choices
- **Leaf particles** fall after eco choices
- **Stars** in the night sky, a moon in the background
- **4 labeled zones** across the bottom: Transport, Energy, Waste, Green Space

---

## End Screen

Shows:
- Game outcome title (City Survived / City Collapsed / Bankrupt)
- **Winner banner** with trophy, winner name, and reason they won
- **Two player stat cards** side by side showing:
  - Total decisions made
  - Eco choices count
  - Quick choices count
  - Carbon contribution (net + or -)
  - Remaining budget
  - BANKRUPT badge if applicable
- **Eco Score Rating** for each player:
  - 🌱 Green Hero (75–100% eco)
  - ♻️ Eco Planner (50–74% eco)
  - ⚠️ City Planner (25–49% eco)
  - ☠️ Carbon Criminal (below 25% eco)
- **Replay** and **Quit** buttons

---

## Screens Flow

```
Title Screen → [SPACE] → Game Screen → [Win/Lose trigger] → End Screen → [Replay/Quit]
```

---

## Technical
- Python + Pygame
- Renders on 1280×720 base surface, smoothscaled to native resolution
- Supports 720p, 1080p, 1440p, 4K
- Unsupported resolutions fall back to 720p with a notification
- Borderless windowed mode for easy Alt+Tab and PrtScr
- Stable 60 FPS enforced
- PyInstaller packaged into a single `.exe` file
