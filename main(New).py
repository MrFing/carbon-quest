import math
import random
import sys
from dataclasses import dataclass

import pygame


pygame.init()
pygame.mixer.pre_init(44100, -16, 1, 512)

WIDTH, HEIGHT = 1280, 720
SCREEN = pygame.display.set_mode(
    (WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
DISPLAY_W, DISPLAY_H = SCREEN.get_size()
SCALE = 1
OFFSET_X = 0
OFFSET_Y = 0
pygame.display.set_caption("Carbon Quest: Strategy Board")
CLOCK = pygame.time.Clock()

UI_FONT = "Segoe UI"
FONT_TITLE = pygame.font.SysFont(UI_FONT, 46, bold=True)
FONT_H1 = pygame.font.SysFont(UI_FONT, 30, bold=True)
FONT_H2 = pygame.font.SysFont(UI_FONT, 22, bold=True)
FONT_BODY = pygame.font.SysFont(UI_FONT, 18)
FONT_SMALL = pygame.font.SysFont(UI_FONT, 15)
FONT_TINY = pygame.font.SysFont(UI_FONT, 12)

BG = (21, 25, 35)
PANEL = (31, 41, 55)
PANEL_2 = (17, 24, 39)
INK = (8, 13, 24)
WHITE = (238, 242, 255)
MUTED = (148, 163, 184)
GREEN = (34, 197, 94)
RED = (239, 68, 68)
YELLOW = (250, 204, 21)
BLUE = (96, 165, 250)
PURPLE = (167, 139, 250)
ORANGE = (251, 146, 60)

ZONE_COLORS = {
    "Transport": (88, 180, 255),
    "Energy": (255, 215, 0),
    "Waste": (166, 118, 84),
    "Green Space": (52, 211, 153),
    "Consumption": (244, 114, 182),
    "Community": (251, 146, 60),
    "Event": (167, 139, 250),
}


def clamp(value, low, high):
    return max(low, min(high, value))


def money(value):
    return f"${value:,}"


def to_game_pos(pos):
    x = int((pos[0] - OFFSET_X) / SCALE)
    y = int((pos[1] - OFFSET_Y) / SCALE)
    return x, y


def draw_text(surface, font, text, color, pos, center=False):
    image = font.render(str(text), True, color)
    rect = image.get_rect(
        center=pos) if center else image.get_rect(topleft=pos)
    if font not in (FONT_TINY, FONT_SMALL) and color != MUTED:
        shadow = font.render(str(text), True, (0, 0, 0))
        surface.blit(shadow, rect.move(2, 2))
    surface.blit(image, rect)
    return rect


def wrap_text(font, text, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = word if not current else f"{current} {word}"
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_gradient_background(surface):
    top = (16, 24, 45)
    mid = (26, 56, 78)
    bottom = (18, 22, 34)
    for y in range(HEIGHT):
        t = y / HEIGHT
        color = lerp_color(top, mid, min(
            1.0, t * 1.4)) if t < 0.62 else lerp_color(mid, bottom, (t - 0.62) / 0.38)
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))
    for i in range(34):
        x = (i * 79 + 31) % WIDTH
        y = 34 + (i * 47) % 230
        pygame.draw.circle(surface, (255, 255, 255), (x, y), 1)


def draw_glow(surface, rect, color, amount=34, radius=18):
    overlay = pygame.Surface(
        (rect.width + 24, rect.height + 24), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (*color, amount),
                     overlay.get_rect(), border_radius=radius + 12)
    surface.blit(overlay, (rect.x - 12, rect.y - 12))


def draw_pill(surface, rect, text, color, text_color=WHITE):
    pygame.draw.rect(surface, color, rect, border_radius=rect.height // 2)
    pygame.draw.rect(surface, (255, 255, 255), rect,
                     1, border_radius=rect.height // 2)
    draw_text(surface, FONT_TINY, text, text_color, rect.center, center=True)


def draw_zone_icon(surface, zone, center, color):
    x, y = center
    if zone == "Transport":
        pygame.draw.polygon(
            surface, color, [(x, y - 12), (x - 14, y + 10), (x + 14, y + 10)])
        pygame.draw.line(surface, INK, (x, y - 6), (x, y + 8), 2)
    elif zone == "Energy":
        pygame.draw.circle(surface, color, center, 12, 3)
        for angle in (0, 120, 240):
            radians = math.radians(angle)
            pygame.draw.line(surface, color, center, (x +
                             math.cos(radians) * 16, y + math.sin(radians) * 16), 2)
    elif zone == "Waste":
        pygame.draw.rect(surface, color, (x - 11, y -
                         9, 22, 20), 3, border_radius=4)
        pygame.draw.line(surface, color, (x - 14, y - 12), (x + 14, y - 12), 3)
    elif zone == "Green Space":
        pygame.draw.ellipse(surface, color, (x - 15, y - 10, 28, 20))
        pygame.draw.line(surface, INK, (x - 8, y + 7), (x + 9, y - 7), 2)
    elif zone == "Consumption":
        pygame.draw.rect(surface, color, (x - 13, y -
                         6, 26, 18), 3, border_radius=3)
        pygame.draw.arc(surface, color, (x - 8, y - 16,
                        16, 18), math.pi, math.tau, 3)
    elif zone == "Community":
        pygame.draw.circle(surface, color, (x - 8, y - 2), 7, 2)
        pygame.draw.circle(surface, color, (x + 8, y - 2), 7, 2)
        pygame.draw.arc(surface, color, (x - 18, y - 2, 36, 24), 0, math.pi, 2)
    else:
        pygame.draw.polygon(
            surface, color, [(x, y - 15), (x + 14, y), (x, y + 15), (x - 14, y)])


def draw_panel(surface, rect, fill=PANEL, border=(71, 85, 105), radius=12):
    pygame.draw.rect(surface, (3, 7, 18), rect.move(
        5, 7), border_radius=radius)
    pygame.draw.rect(surface, fill, rect, border_radius=radius)
    pygame.draw.rect(surface, border, rect, 2, border_radius=radius)


class Button:
    def __init__(self, rect, text, color=BLUE):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover = False

    def update(self, mouse):
        self.hover = self.rect.collidepoint(mouse)

    def clicked(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        game_pos = to_game_pos(event.pos)
        return self.rect.collidepoint(game_pos)

    def draw(self, surface):
        fill = tuple(min(255, c + 28)
                     for c in self.color) if self.hover else self.color
        if self.hover:
            draw_glow(surface, self.rect, self.color, 55, 20)
        pygame.draw.rect(surface, (4, 8, 18),
                         self.rect.move(0, 4), border_radius=20)
        pygame.draw.rect(surface, fill, self.rect, border_radius=20)
        pygame.draw.rect(surface, lerp_color(fill, WHITE, 0.22), (self.rect.x, self.rect.y, self.rect.width,
                         self.rect.height // 2), border_top_left_radius=20, border_top_right_radius=20)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=20)
        draw_text(surface, FONT_SMALL, self.text,
                  WHITE, self.rect.center, center=True)


@dataclass
class Decision:
    title: str
    zone: str
    eco: str
    quick: str
    eco_effect: tuple
    quick_effect: tuple
    fact: str


@dataclass
class Event:
    title: str
    text: str
    effect: tuple


class Player:
    def __init__(self, name, color, start_tile):
        self.name = name
        self.color = color
        self.tile = start_tile
        self.budget = 65000
        self.support = 50
        self.green_points = 0
        self.eco_choices = 0
        self.quick_choices = 0
        self.policies = []


class CarbonQuest:
    def __init__(self):
        self.state = "title"
        self.turn = 0
        self.round = 1
        self.max_rounds = 12
        self.carbon = 42
        self.health = 78
        self.resilience = 20
        self.dice = 1
        self.message = "Press SPACE to begin."
        self.selected_card = None
        self.selected_event = None
        self.animation_t = 0.0
        self.board_tiles = self.make_board()
        self.players = [
            Player("Player 1", GREEN, 0),
            Player("Player 2", PURPLE, 0),
        ]
        self.decisions = self.make_decisions()
        self.events = self.make_events()
        self.policy_buttons = []
        self.roll_button = Button((1065, 660, 160, 38), "Roll Dice", BLUE)
        self.eco_button = Button((930, 660, 140, 38), "Eco Plan", GREEN)
        self.quick_button = Button((1085, 660, 140, 38), "Quick Fix", RED)
        self.rules_button = Button((1090, 28, 140, 38), "Rules", ORANGE)
        self.back_button = Button((40, 650, 140, 42), "Back", BLUE)
        self.restart_button = Button((525, 640, 140, 44), "Restart", GREEN)
        self.quit_button = Button((690, 640, 120, 44), "Quit", RED)

    def make_board(self):
        zones = [
            "Transport", "Energy", "Waste", "Green Space", "Consumption", "Community",
            "Transport", "Energy", "Waste", "Green Space", "Consumption", "Community",
            "Transport", "Energy", "Waste", "Green Space", "Consumption", "Community",
            "Transport", "Energy", "Waste", "Green Space", "Consumption", "Community",
        ]
        positions = []
        left, top, size, gap = 55, 110, 86, 10
        for i in range(7):
            positions.append((left + i * (size + gap), top))
        for i in range(1, 5):
            positions.append((left + 6 * (size + gap), top + i * (size + gap)))
        for i in range(5, -1, -1):
            positions.append((left + i * (size + gap), top + 4 * (size + gap)))
        for i in range(3, 0, -1):
            positions.append((left, top + i * (size + gap)))
        return [
            {"zone": zones[i % len(zones)],
             "rect": pygame.Rect(*pos, size, size)}
            for i, pos in enumerate(positions)
        ]

    def make_decisions(self):
        return [
            Decision("Rush-Hour Problem", "Transport", "Metro + bike parking", "More flyovers",
                     (-9, 4, -8500, 5, 4), (10, -3, -2500, -4, 0),
                     "Public transport reduces emissions per passenger and traffic pollution."),
            Decision("Electricity Demand", "Energy", "Solar plus battery storage", "Coal backup plant",
                     (-12, 5, -12000, 4, 5), (14, -8, -2200, -6, 0),
                     "Renewable energy costs more at first but lowers future carbon."),
            Decision("Market Waste", "Waste", "Recycling and compost hubs", "Open dumping site",
                     (-6, 5, -4200, 3, 3), (8, -7, -1200, -5, 0),
                     "Separating waste cuts landfill methane and keeps streets cleaner."),
            Decision("Vacant Land", "Green Space", "Urban forest and rain garden", "Shopping complex",
                     (-8, 7, -6000, 2, 4), (9, -5, -1500, -2, 1),
                     "Green spaces absorb carbon, reduce heat, and improve public health."),
            Decision("Food Habits", "Consumption", "Local low-meat food campaign", "Mega fast-food drive",
                     (-5, 3, -3000, 6, 3), (7, -3, -900, -3, 0),
                     "Consumption choices also create carbon through transport and packaging."),
            Decision("Neighbourhood Plan", "Community", "Library and community garden", "Cut public programs",
                     (-4, 6, -5200, 8, 3), (5, -6, -700, -8, 0),
                     "Community projects build support for long-term climate action."),
            Decision("Airport Expansion", "Transport", "Rail link to airport", "Add new runway",
                     (-5, 3, -7000, 3, 3), (13, -2, -3000, -4, 0),
                     "Travel infrastructure changes carbon footprints for many years."),
            Decision("Power Shortage", "Energy", "Wind farm partnership", "Diesel generator contracts",
                     (-9, 4, -9000, 2, 4), (11, -5, -2000, -4, 0),
                     "Short-term cheap energy can create long-term pollution costs."),
        ]

    def make_events(self):
        return [
            Event("Heat Wave", "High carbon makes heat worse. Resilience protects the city.",
                  (7, -8, -2000, -4, 0)),
            Event("Climate Grant", "A national grant rewards green planning.",
                  (-3, 2, 7000, 5, 2)),
            Event("Public Protest", "Citizens demand cleaner transport and waste systems.",
                  (2, -2, -1000, -8, 0)),
            Event("Innovation Fair",
                  "Clean technology becomes cheaper this round.", (-4, 1, 3000, 4, 2)),
            Event("Flood Warning", "Green spaces and resilience reduce damage.",
                  (5, -6, -3000, -3, 0)),
        ]

    def current_player(self):
        return self.players[self.turn]

    def reset(self):
        self.__init__()
        self.state = "play"
        self.message = "Roll the dice. Land on a district and solve its decision."

    def apply_effect(self, effect, actor):
        carbon, health, budget, support, green_points = effect
        if self.carbon >= 80 and carbon > 0:
            carbon += 2
        if self.resilience >= 50 and health < 0:
            health += 2
        self.carbon = clamp(self.carbon + carbon, 0, 100)
        self.health = clamp(self.health + health, 0, 100)
        actor.budget = max(0, actor.budget + budget)
        actor.support = clamp(actor.support + support, 0, 100)
        actor.green_points += green_points
        if green_points > 0:
            self.resilience = clamp(self.resilience + green_points * 2, 0, 100)

    def roll(self):
        if self.selected_card or self.selected_event:
            return
        player = self.current_player()
        self.dice = random.randint(1, 6)
        player.tile = (player.tile + self.dice) % len(self.board_tiles)
        zone = self.board_tiles[player.tile]["zone"]
        zone_cards = [card for card in self.decisions if card.zone == zone]
        self.selected_card = random.choice(zone_cards or self.decisions)
        self.message = f"{player.name} rolled {self.dice} and landed on {zone}."

    def choose(self, eco):
        player = self.current_player()
        if self.selected_event:
            self.apply_effect(self.selected_event.effect, player)
            self.selected_event = None
            self.end_turn()
            return
        if not self.selected_card:
            return
        card = self.selected_card
        if eco:
            self.apply_effect(card.eco_effect, player)
            player.eco_choices += 1
            self.message = f"{player.name} chose the sustainable plan."
        else:
            self.apply_effect(card.quick_effect, player)
            player.quick_choices += 1
            self.message = f"{player.name} chose the cheaper quick fix."
        self.selected_card = None
        self.unlock_policy(player)
        self.end_turn()

    def unlock_policy(self, player):
        if player.eco_choices >= 3 and "Carbon Tax" not in player.policies:
            player.policies.append("Carbon Tax")
            self.carbon = clamp(self.carbon - 5, 0, 100)
            self.message += " Policy unlocked: Carbon Tax lowers city carbon."
        if player.support >= 70 and "Citizen Volunteers" not in player.policies:
            player.policies.append("Citizen Volunteers")
            self.health = clamp(self.health + 5, 0, 100)
            self.resilience = clamp(self.resilience + 8, 0, 100)
            self.message += " Policy unlocked: Citizen Volunteers improve health."

    def end_turn(self):
        player = self.current_player()
        if player.budget <= 0:
            self.state = "end"
            self.message = f"{player.name} went bankrupt."
            return
        if self.carbon >= 100 or self.health <= 0:
            self.state = "end"
            self.message = "The city collapsed from environmental damage."
            return
        if self.turn == 1:
            self.round += 1
        self.turn = 1 - self.turn
        if self.round > self.max_rounds:
            self.state = "end"
            self.message = "The final round is complete."

    def winner(self):
        scores = []
        for p in self.players:
            score = (
                p.green_points * 10
                + p.support
                + p.budget // 2000
                + self.health
                + (100 - self.carbon)
                + len(p.policies) * 12
            )
            if p.budget <= 0:
                score -= 80
            scores.append(score)
        if scores[0] == scores[1]:
            return None, scores
        return 0 if scores[0] > scores[1] else 1, scores

    def update(self):
        self.animation_t += 1 / 60
        mouse = to_game_pos(pygame.mouse.get_pos())
        for button in [self.roll_button, self.eco_button, self.quick_button, self.rules_button,
                       self.back_button, self.restart_button, self.quit_button]:
            button.update(mouse)

    def handle_events(self):
        for event in pygame.event.get():
            is_left_click = event.type == pygame.MOUSEBUTTONDOWN and getattr(
                event, "button", None) == 1
            game_click = to_game_pos(event.pos) if is_left_click else None
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if self.state == "title" and event.key == pygame.K_SPACE:
                    self.reset()
                elif self.state == "play" and event.key == pygame.K_r:
                    self.roll()
                elif self.state == "play" and event.key == pygame.K_1:
                    self.choose(True)
                elif self.state == "play" and event.key == pygame.K_2:
                    self.choose(False)
            if self.rules_button.clicked(event):
                self.state = "rules"
            if self.state == "rules" and self.back_button.clicked(event):
                self.state = "play"
            if self.state == "title" and event.type == pygame.MOUSEBUTTONDOWN:
                self.reset()
            if self.state == "play":
                roll_area = pygame.Rect(880, 646, 360, 62)
                eco_area = pygame.Rect(910, 646, 170, 62)
                quick_area = pygame.Rect(1075, 646, 170, 62)
                if not (self.selected_card or self.selected_event) and is_left_click and (
                    self.roll_button.clicked(
                        event) or roll_area.collidepoint(game_click)
                ):
                    self.roll()
                elif self.selected_card or self.selected_event:
                    if is_left_click and (self.eco_button.clicked(event) or eco_area.collidepoint(game_click)):
                        self.choose(True)
                    elif is_left_click and (self.quick_button.clicked(event) or quick_area.collidepoint(game_click)):
                        self.choose(False)
            if self.state == "end":
                if self.restart_button.clicked(event):
                    self.reset()
                if self.quit_button.clicked(event):
                    pygame.quit()
                    sys.exit()

    def draw_board(self, surface):
        board_panel = pygame.Rect(35, 88, 685, 522)
        draw_panel(surface, board_panel, (14, 24, 37), (55, 75, 96), 18)

        centers = [tile["rect"].center for tile in self.board_tiles]
        if len(centers) > 1:
            pygame.draw.lines(surface, (79, 102, 128), True, centers, 5)
            pygame.draw.lines(surface, (15, 23, 42), True, centers, 2)

        for i, tile in enumerate(self.board_tiles):
            rect = tile["rect"]
            zone = tile["zone"]
            color = ZONE_COLORS[zone]
            active = any(p.tile == i for p in self.players)
            if active:
                draw_glow(surface, rect, color, 76, 14)
            pygame.draw.rect(surface, (4, 8, 18),
                             rect.move(0, 4), border_radius=14)
            pygame.draw.rect(surface, color, rect, border_radius=14)
            highlight = pygame.Rect(
                rect.x, rect.y, rect.width, rect.height // 2)
            pygame.draw.rect(surface, lerp_color(color, WHITE, 0.28), highlight,
                             border_top_left_radius=14, border_top_right_radius=14)
            pygame.draw.rect(surface, (15, 23, 42), rect, 3, border_radius=14)
            draw_text(surface, FONT_TINY, str(i + 1),
                      (15, 23, 42), (rect.x + 8, rect.y + 5))
            draw_zone_icon(surface, zone, (rect.centerx, rect.y + 34), INK)
            for j, line in enumerate(wrap_text(FONT_TINY, zone, rect.width - 10)[:2]):
                draw_text(surface, FONT_TINY, line, (15, 23, 42),
                          (rect.centerx, rect.y + 58 + j * 13), center=True)
        for p in self.players:
            rect = self.board_tiles[p.tile]["rect"]
            offset = -14 if p.name.endswith("1") else 14
            pulse = int(math.sin(self.animation_t * 5) * 2)
            pos = (rect.centerx + offset, rect.centery + 24 + pulse)
            pygame.draw.circle(surface, (0, 0, 0),
                               (pos[0] + 2, pos[1] + 3), 16)
            pygame.draw.circle(surface, p.color, pos, 16)
            pygame.draw.circle(surface, WHITE, pos, 16, 2)
            draw_text(surface, FONT_SMALL, p.name[-1], WHITE, pos, center=True)

    def draw_city_visual(self, surface):
        rect = pygame.Rect(155, 230, 455, 190)
        pollution = self.carbon / 100
        draw_panel(surface, rect.inflate(24, 24),
                   (12, 18, 30), (55, 75, 96), 16)
        sky_top = lerp_color((62, 132, 190), (130, 70, 75), pollution)
        sky_bottom = lerp_color((252, 178, 104), (146, 76, 69), pollution)
        for y in range(rect.height):
            color = lerp_color(sky_top, sky_bottom, y / rect.height)
            pygame.draw.line(surface, color, (rect.x, rect.y + y),
                             (rect.right, rect.y + y))
        pygame.draw.circle(surface, (255, 218, 130),
                           (rect.right - 60, rect.y + 45), 28)
        pygame.draw.polygon(surface, (36, 46, 57), [(rect.x, rect.bottom), (rect.x, rect.bottom - 45), (rect.x + 130,
                            rect.bottom - 80), (rect.x + 250, rect.bottom - 54), (rect.right, rect.bottom - 95), (rect.right, rect.bottom)])
        for x, h in [(190, 90), (245, 120), (320, 75), (380, 130), (465, 95), (530, 118)]:
            b = pygame.Rect(x, rect.bottom - h, 42, h)
            shade = lerp_color((45, 55, 72), (82, 65, 66), pollution)
            pygame.draw.rect(surface, shade, b, border_radius=5)
            pygame.draw.rect(surface, (10, 15, 24), b, 2, border_radius=5)
            for wy in range(b.y + 12, b.bottom - 10, 20):
                pygame.draw.rect(surface, (255, 230, 140),
                                 (b.x + 12, wy, 8, 10), border_radius=2)
        tree_count = max(1, self.resilience // 12)
        for i in range(tree_count):
            x = rect.x + 25 + i * 45
            pygame.draw.rect(surface, (94, 60, 35),
                             (x, rect.bottom - 28, 8, 22))
            pygame.draw.circle(surface, GREEN, (x + 4, rect.bottom - 35), 15)
        haze = pygame.Surface(rect.size, pygame.SRCALPHA)
        haze.fill((230, 80, 60, int(75 * pollution)))
        surface.blit(haze, rect.topleft)
        pygame.draw.rect(surface, WHITE, rect, 2, border_radius=10)
        draw_text(surface, FONT_TINY, "Live city view changes with carbon and resilience",
                  WHITE, (rect.centerx, rect.bottom + 16), center=True)

    def draw_meters(self, surface):
        draw_panel(surface, pygame.Rect(742, 86, 510, 245),
                   (14, 23, 38), (55, 75, 96), 18)
        draw_text(surface, FONT_H2, "City Dashboard", WHITE, (765, 102))
        labels = [
            ("Carbon", self.carbon, RED),
            ("Health", self.health, GREEN),
            ("Resilience", self.resilience, BLUE),
        ]
        for i, (label, value, color) in enumerate(labels):
            x, y = 765, 140 + i * 58
            draw_text(surface, FONT_H2, f"{label}: {value}", color, (x, y))
            bar = pygame.Rect(x + 145, y + 5, 320, 18)
            pygame.draw.rect(surface, (15, 23, 42), bar, border_radius=10)
            fill = pygame.Rect(
                bar.x + 2, bar.y + 2, int((bar.width - 4) * value / 100), bar.height - 4)
            pygame.draw.rect(surface, color, fill, border_radius=8)

    def draw_player_panel(self, surface):
        for i, p in enumerate(self.players):
            rect = pygame.Rect(742 + i * 260, 338, 245, 142)
            border = p.color if i == self.turn and self.state == "play" else (
                71, 85, 105)
            if i == self.turn and self.state == "play":
                draw_glow(surface, rect, p.color, 58, 16)
            draw_panel(surface, rect, PANEL_2, border)
            draw_pill(surface, pygame.Rect(rect.right - 84, rect.y + 14, 62, 22),
                      "TURN" if i == self.turn and self.state == "play" else "WAIT",
                      p.color if i == self.turn and self.state == "play" else (51, 65, 85))
            draw_text(surface, FONT_H2, p.name, p.color,
                      (rect.x + 16, rect.y + 12))
            draw_text(surface, FONT_SMALL,
                      f"Budget: {money(p.budget)}", WHITE, (rect.x + 16, rect.y + 48))
            draw_text(surface, FONT_SMALL,
                      f"Support: {p.support}", WHITE, (rect.x + 16, rect.y + 72))
            draw_text(surface, FONT_SMALL,
                      f"Green points: {p.green_points}", GREEN, (rect.x + 16, rect.y + 96))
            policies = ", ".join(p.policies) if p.policies else "None"
            for j, line in enumerate(wrap_text(FONT_TINY, f"Policies: {policies}", 205)[:1]):
                draw_text(surface, FONT_TINY, line, MUTED,
                          (rect.x + 16, rect.y + 121 + j * 15))

    def effect_summary(self, effect):
        carbon, health, budget, support, green_points = effect
        first = f"Carbon {carbon:+d}   Health {health:+d}"
        second = f"Budget {money(budget)}   Support {support:+d}"
        if green_points:
            second += f"   Green +{green_points}"
        return first, second

    def draw_card(self, surface):
        rect = pygame.Rect(742, 490, 510, 150)
        draw_panel(surface, rect, PANEL_2, (71, 85, 105))
        if self.selected_event:
            card = self.selected_event
            pygame.draw.rect(surface, PURPLE, (rect.x, rect.y, 8, rect.height),
                             border_top_left_radius=12, border_bottom_left_radius=12)
            draw_text(surface, FONT_H2,
                      f"EVENT: {card.title}", PURPLE, (rect.x + 16, rect.y + 12))
            for i, line in enumerate(wrap_text(FONT_SMALL, card.text, 460)[:3]):
                draw_text(surface, FONT_SMALL, line, WHITE,
                          (rect.x + 16, rect.y + 45 + i * 20))
            draw_text(surface, FONT_TINY, "Choose either action to resolve the event.",
                      YELLOW, (rect.x + 16, rect.y + 122))
            return
        if not self.selected_card:
            draw_text(surface, FONT_H2, f"{self.current_player().name}'s Turn", self.current_player(
            ).color, (rect.x + 16, rect.y + 12))
            draw_pill(surface, pygame.Rect(rect.right - 138, rect.y + 14, 108, 24),
                      f"Round {min(self.round, self.max_rounds)}/{self.max_rounds}", BLUE)
            draw_text(surface, FONT_BODY,
                      f"Dice: {self.dice}", WHITE, (rect.x + 16, rect.y + 54))
            draw_text(surface, FONT_BODY, "Roll to draw a city decision card.",
                      MUTED, (rect.x + 110, rect.y + 54))
            draw_text(surface, FONT_SMALL, "R = Roll   |   1 = Eco   |   2 = Quick",
                      YELLOW, (rect.x + 16, rect.y + 98))
            return
        card = self.selected_card
        eco_effect_1, eco_effect_2 = self.effect_summary(card.eco_effect)
        quick_effect_1, quick_effect_2 = self.effect_summary(card.quick_effect)
        pygame.draw.rect(surface, ZONE_COLORS[card.zone], (
            rect.x, rect.y, 8, rect.height), border_top_left_radius=12, border_bottom_left_radius=12)
        draw_zone_icon(surface, card.zone, (rect.right - 32,
                       rect.y + 32), ZONE_COLORS[card.zone])
        draw_text(surface, FONT_H2, card.title,
                  ZONE_COLORS[card.zone], (rect.x + 16, rect.y + 8))
        eco_rect = pygame.Rect(rect.x + 16, rect.y + 42, 225, 66)
        quick_rect = pygame.Rect(rect.x + 256, rect.y + 42, 225, 66)
        pygame.draw.rect(surface, (16, 80, 45), eco_rect, border_radius=9)
        pygame.draw.rect(surface, (100, 25, 25), quick_rect, border_radius=9)
        draw_text(surface, FONT_SMALL, "ECO CHOICE",
                  (134, 239, 172), (eco_rect.x + 12, eco_rect.y + 7))
        draw_text(surface, FONT_TINY, card.eco, WHITE,
                  (eco_rect.x + 12, eco_rect.y + 27))
        draw_text(surface, FONT_TINY, eco_effect_1, WHITE,
                  (eco_rect.x + 12, eco_rect.y + 42))
        draw_text(surface, FONT_TINY, eco_effect_2, WHITE,
                  (eco_rect.x + 12, eco_rect.y + 55))
        draw_text(surface, FONT_SMALL, "QUICK CHOICE", (254, 202, 202),
                  (quick_rect.x + 12, quick_rect.y + 7))
        draw_text(surface, FONT_TINY, card.quick, WHITE,
                  (quick_rect.x + 12, quick_rect.y + 27))
        draw_text(surface, FONT_TINY, quick_effect_1, WHITE,
                  (quick_rect.x + 12, quick_rect.y + 42))
        draw_text(surface, FONT_TINY, quick_effect_2, WHITE,
                  (quick_rect.x + 12, quick_rect.y + 55))
        for i, line in enumerate(wrap_text(FONT_TINY, card.fact, 470)[:2]):
            draw_text(surface, FONT_TINY, line, MUTED,
                      (rect.x + 16, rect.y + 116 + i * 14))

    def draw_action_bar(self, surface):
        rect = pygame.Rect(742, 646, 510, 62)
        active_color = self.current_player().color
        draw_panel(surface, rect, (12, 20, 34), active_color, 16)
        if self.selected_card or self.selected_event:
            draw_text(surface, FONT_SMALL, "Choose action",
                      YELLOW, (rect.x + 18, rect.y + 10))
            draw_text(surface, FONT_TINY, "Keyboard: 1 or 2",
                      MUTED, (rect.x + 18, rect.y + 35))
            self.eco_button.draw(surface)
            self.quick_button.draw(surface)
        else:
            draw_text(surface, FONT_SMALL, "Ready",
                      YELLOW, (rect.x + 18, rect.y + 10))
            draw_text(surface, FONT_TINY, "Roll for a district card.",
                      MUTED, (rect.x + 18, rect.y + 35))
            self.roll_button.draw(surface)

    def draw_title(self, surface):
        draw_gradient_background(surface)
        hero = pygame.Rect(120, 75, 1040, 570)
        draw_panel(surface, hero, (14, 24, 38), (74, 222, 128), 26)
        self.draw_city_visual(surface)
        draw_text(surface, FONT_TITLE, "Carbon Quest",
                  GREEN, (WIDTH // 2, 125), center=True)
        draw_text(surface, FONT_H1, "Strategy Board",
                  WHITE, (WIDTH // 2, 172), center=True)
        draw_text(surface, FONT_H2, "A two-player city-life board game about carbon choices",
                  MUTED, (WIDTH // 2, 205), center=True)
        for i, zone in enumerate(["Transport", "Energy", "Waste", "Green Space", "Consumption", "Community"]):
            chip = pygame.Rect(250 + i * 130, 470, 112, 26)
            draw_pill(surface, chip, zone, ZONE_COLORS[zone], (15, 23, 42))
        lines = [
            "Roll dice, move through districts, solve real city problems, unlock policies,",
            "and balance carbon, health, public support, resilience, and budget.",
        ]
        for i, line in enumerate(lines):
            draw_text(surface, FONT_BODY, line, WHITE if i ==
                      0 else MUTED, (WIDTH // 2, 525 + i * 28), center=True)
        draw_text(surface, FONT_H1, "Press SPACE or click to start",
                  YELLOW, (WIDTH // 2, 600), center=True)
        self.rules_button.draw(surface)

    def draw_rules(self, surface):
        draw_gradient_background(surface)
        panel = pygame.Rect(55, 42, 1170, 620)
        draw_panel(surface, panel, (14, 24, 38), (74, 222, 128), 22)
        draw_text(surface, FONT_TITLE, "Rule Sheet",
                  GREEN, (WIDTH // 2, 75), center=True)
        rules = [
            "Objective: survive 12 rounds with low carbon, good city health, enough budget, and high green points.",
            "Players take turns rolling the dice and moving around the digital board.",
            "Each district gives a city-life decision: Transport, Energy, Waste, Green Space, Consumption, or Community.",
            "Eco Plans cost more but reduce carbon, improve health, support, resilience, and green points.",
            "Quick Fixes cost less but usually increase carbon and damage health or public support.",
            "Event tiles create surprises such as heat waves, floods, grants, protests, and innovation fairs.",
            "Policies unlock when players make enough eco choices or gain high support.",
            "The city loses if carbon reaches 100, health reaches 0, or a player goes bankrupt.",
            "Winner: highest final score from green points, support, budget, health, low carbon, and policies.",
        ]
        y = 130
        for rule in rules:
            pygame.draw.circle(surface, YELLOW, (90, y + 9), 5)
            for j, line in enumerate(wrap_text(FONT_BODY, rule, 1030)):
                draw_text(surface, FONT_BODY, line, WHITE, (110, y + j * 24))
            y += 58
        self.back_button.draw(surface)

    def draw_play(self, surface):
        draw_gradient_background(surface)
        pygame.draw.rect(surface, (8, 13, 24, 180), (0, 0, WIDTH, 78))
        pygame.draw.line(surface, (55, 75, 96), (0, 78), (WIDTH, 78), 2)
        draw_text(surface, FONT_H1, "Carbon Quest", GREEN, (55, 35))
        message_rect = pygame.Rect(330, 29, 610, 30)
        pygame.draw.rect(surface, (12, 20, 34), message_rect, border_radius=15)
        draw_text(surface, FONT_SMALL,
                  self.message[:72], WHITE, (message_rect.x + 16, message_rect.y + 6))
        self.rules_button.draw(surface)
        self.draw_board(surface)
        self.draw_city_visual(surface)
        self.draw_meters(surface)
        self.draw_player_panel(surface)
        self.draw_card(surface)
        self.draw_action_bar(surface)

    def draw_end(self, surface):
        draw_gradient_background(surface)
        winner, scores = self.winner()
        panel = pygame.Rect(145, 50, 990, 610)
        draw_panel(surface, panel, (14, 24, 38), (74, 222, 128), 24)
        title = "City Survived!" if self.carbon < 80 and self.health > 0 else "Challenge Ended"
        draw_text(surface, FONT_TITLE, title, GREEN if self.carbon <
                  80 else RED, (WIDTH // 2, 80), center=True)
        draw_text(surface, FONT_H2, self.message,
                  WHITE, (WIDTH // 2, 130), center=True)
        if winner is None:
            draw_text(surface, FONT_H1, "It is a draw!",
                      YELLOW, (WIDTH // 2, 205), center=True)
        else:
            draw_text(surface, FONT_H1, f"{self.players[winner].name} wins!",
                      self.players[winner].color, (WIDTH // 2, 205), center=True)
        draw_text(surface, FONT_BODY,
                  f"Final carbon: {self.carbon}  |  Health: {self.health}  |  Resilience: {self.resilience}", WHITE, (WIDTH // 2, 260), center=True)
        for i, p in enumerate(self.players):
            rect = pygame.Rect(260 + i * 410, 320, 350, 210)
            draw_panel(surface, rect, PANEL_2, p.color)
            draw_text(surface, FONT_H1, p.name, p.color,
                      (rect.centerx, rect.y + 30), center=True)
            draw_text(surface, FONT_BODY,
                      f"Score: {scores[i]}", WHITE, (rect.x + 35, rect.y + 75))
            draw_text(surface, FONT_BODY,
                      f"Budget: {money(p.budget)}", WHITE, (rect.x + 35, rect.y + 105))
            draw_text(surface, FONT_BODY,
                      f"Eco / Quick: {p.eco_choices} / {p.quick_choices}", WHITE, (rect.x + 35, rect.y + 135))
            draw_text(surface, FONT_BODY,
                      f"Policies: {len(p.policies)}", WHITE, (rect.x + 35, rect.y + 165))
        self.restart_button.draw(surface)
        self.quit_button.draw(surface)

    def draw(self):
        surface = SCREEN
        if self.state == "title":
            self.draw_title(surface)
        elif self.state == "rules":
            self.draw_rules(surface)
        elif self.state == "end":
            self.draw_end(surface)
        else:
            self.draw_play(surface)
        pygame.display.flip()

    def run(self):
        while True:
            CLOCK.tick(60)
            self.update()
            self.handle_events()
            self.draw()


if __name__ == "__main__":
    CarbonQuest().run()
# Yo Aarav Singh. This game is best
