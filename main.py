import os
import math
import random
import sys
import ctypes
from array import array
from dataclasses import dataclass

os.environ["SDL_VIDEO_CENTERED"] = "1"

import pygame


pygame.mixer.pre_init(44100, -16, 1, 512)
BASE_W = 1280
BASE_H = 720
SUPPORTED = [(1280, 720), (1920, 1080), (2560, 1440), (3840, 2160)]


def enable_windows_dpi_awareness():
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def detect_native_resolution():
    if sys.platform == "win32":
        try:
            from ctypes import wintypes

            class DEVMODEW(ctypes.Structure):
                _fields_ = [
                    ("dmDeviceName", wintypes.WCHAR * 32),
                    ("dmSpecVersion", wintypes.WORD),
                    ("dmDriverVersion", wintypes.WORD),
                    ("dmSize", wintypes.WORD),
                    ("dmDriverExtra", wintypes.WORD),
                    ("dmFields", wintypes.DWORD),
                    ("dmOrientation", ctypes.c_short),
                    ("dmPaperSize", ctypes.c_short),
                    ("dmPaperLength", ctypes.c_short),
                    ("dmPaperWidth", ctypes.c_short),
                    ("dmScale", ctypes.c_short),
                    ("dmCopies", ctypes.c_short),
                    ("dmDefaultSource", ctypes.c_short),
                    ("dmPrintQuality", ctypes.c_short),
                    ("dmColor", ctypes.c_short),
                    ("dmDuplex", ctypes.c_short),
                    ("dmYResolution", ctypes.c_short),
                    ("dmTTOption", ctypes.c_short),
                    ("dmCollate", ctypes.c_short),
                    ("dmFormName", wintypes.WCHAR * 32),
                    ("dmLogPixels", wintypes.WORD),
                    ("dmBitsPerPel", wintypes.DWORD),
                    ("dmPelsWidth", wintypes.DWORD),
                    ("dmPelsHeight", wintypes.DWORD),
                    ("dmDisplayFlags", wintypes.DWORD),
                    ("dmDisplayFrequency", wintypes.DWORD),
                    ("dmICMMethod", wintypes.DWORD),
                    ("dmICMIntent", wintypes.DWORD),
                    ("dmMediaType", wintypes.DWORD),
                    ("dmDitherType", wintypes.DWORD),
                    ("dmReserved1", wintypes.DWORD),
                    ("dmReserved2", wintypes.DWORD),
                    ("dmPanningWidth", wintypes.DWORD),
                    ("dmPanningHeight", wintypes.DWORD),
                ]

            mode = DEVMODEW()
            mode.dmSize = ctypes.sizeof(DEVMODEW)
            if ctypes.windll.user32.EnumDisplaySettingsW(None, -1, ctypes.byref(mode)):
                return int(mode.dmPelsWidth), int(mode.dmPelsHeight)
        except Exception:
            pass

    try:
        desktop_sizes = pygame.display.get_desktop_sizes()
        if desktop_sizes:
            width, height = desktop_sizes[0]
            if width and height:
                return int(width), int(height)
    except Exception:
        pass

    info = pygame.display.Info()
    width = int(info.current_w) if info.current_w else BASE_W
    height = int(info.current_h) if info.current_h else BASE_H
    return width, height


enable_windows_dpi_awareness()
pygame.init()

NATIVE_W, NATIVE_H = detect_native_resolution()

if (NATIVE_W, NATIVE_H) in SUPPORTED:
    RENDER_W, RENDER_H = NATIVE_W, NATIVE_H
    FULLSCREEN = True
    COMPAT_MODE = False
else:
    RENDER_W, RENDER_H = BASE_W, BASE_H
    FULLSCREEN = False
    COMPAT_MODE = True

if FULLSCREEN:
    SCREEN = pygame.display.set_mode((RENDER_W, RENDER_H), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
else:
    SCREEN = pygame.display.set_mode((RENDER_W, RENDER_H), pygame.SCALED | pygame.HWSURFACE | pygame.DOUBLEBUF)

pygame.display.set_caption("Carbon Quest: City Builder Challenge")

SCALE_X = RENDER_W / BASE_W
SCALE_Y = RENDER_H / BASE_H
SCALE = min(SCALE_X, SCALE_Y)


def S(value):
    return int(value * SCALE)


def SX(value):
    return int(value * SCALE_X)


def SY(value):
    return int(value * SCALE_Y)


BASE_SURFACE = pygame.Surface((BASE_W, BASE_H)).convert()

FONT_TITLE = pygame.font.SysFont("Arial", 48, bold=True)
FONT_HEADING = pygame.font.SysFont("Arial", 28, bold=True)
FONT_BODY = pygame.font.SysFont("Arial", 20)
FONT_BODY_BOLD = pygame.font.SysFont("Arial", 20, bold=True)
FONT_SMALL = pygame.font.SysFont("Arial", 14)
FONT_SMALL_BOLD = pygame.font.SysFont("Arial", 14, bold=True)
FONT_TINY = pygame.font.SysFont("Arial", 11)


FPS = 60
BG_COLOR = (26, 26, 46)
PANEL_COLOR = (22, 33, 62)
PANEL_DARK = (12, 18, 32)
GREEN = (0, 255, 136)
RED = (255, 68, 68)
YELLOW = (255, 215, 0)
WHITE = (240, 245, 255)
LIGHT_GRAY = (175, 184, 198)
GRAY = (122, 130, 144)
SHADOW = (8, 10, 18)
ZONE_COLORS = {
    "Transport": (88, 180, 255),
    "Energy": (255, 215, 0),
    "Waste": (166, 118, 84),
    "Green Space": (0, 255, 136),
}

HUD_RECT = pygame.Rect(0, 0, BASE_W, 90)
CITY_PANEL_RECT = pygame.Rect(0, 90, 790, 630)
RIGHT_PANEL_RECT = pygame.Rect(800, 90, 480, 630)
METER_CONTAINER_RECT = pygame.Rect(860, 100, 120, 280)
CARD_PANEL_RECT = pygame.Rect(820, 400, 450, 310)
TITLE_PARTICLE_RECT = pygame.Rect(100, 180, BASE_W - 200, 440)
END_PARTICLE_RECT = pygame.Rect(100, 60, BASE_W - 200, 420)


def clamp(value, low, high):
    return max(low, min(high, value))


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(color_a, color_b, t):
    return tuple(int(lerp(color_a[i], color_b[i], t)) for i in range(3))


def to_base_pos(pos):
    if RENDER_W == BASE_W and RENDER_H == BASE_H:
        return pos
    x = int(pos[0] * BASE_W / max(1, RENDER_W))
    y = int(pos[1] * BASE_H / max(1, RENDER_H))
    return x, y


def push_clip(surface, rect):
    previous = surface.get_clip()
    surface.set_clip(rect)
    return previous


def draw_alpha_outline(surface, rect, color, width=1, border_radius=0):
    if len(color) == 4:
        overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(overlay, color, overlay.get_rect(), width, border_radius=border_radius)
        surface.blit(overlay, rect.topleft)
        return
    pygame.draw.rect(surface, color, rect, width, border_radius=border_radius)


def draw_shadowed_text(surface, font, text, color, pos, center=False, shadow_offset=2):
    shadow = font.render(text, True, (0, 0, 0))
    text_surface = font.render(text, True, color)
    shadow_rect = shadow.get_rect(center=pos) if center else shadow.get_rect(topleft=pos)
    text_rect = text_surface.get_rect(center=pos) if center else text_surface.get_rect(topleft=pos)
    shadow_rect.x += shadow_offset
    shadow_rect.y += shadow_offset
    surface.blit(shadow, shadow_rect)
    surface.blit(text_surface, text_rect)


def draw_panel(surface, rect, fill_color, border_color=(255, 255, 255, 34), radius=16, shadow=True, border_width=1):
    if shadow:
        pygame.draw.rect(surface, SHADOW, rect.move(4, 5), border_radius=radius)
    pygame.draw.rect(surface, fill_color, rect, border_radius=radius)
    draw_alpha_outline(surface, rect, border_color, width=border_width, border_radius=radius)


def draw_symbol(surface, symbol, rect, color):
    if symbol == "transport":
        points = [(rect.centerx, rect.top), (rect.left, rect.bottom), (rect.right, rect.bottom)]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.line(surface, BG_COLOR, (rect.centerx, rect.top + 4), (rect.centerx, rect.bottom - 4), 2)
    elif symbol == "energy":
        pygame.draw.circle(surface, color, rect.center, rect.width // 2 - 2, 3)
        pygame.draw.circle(surface, color, rect.center, max(3, rect.width // 5))
    elif symbol == "waste":
        diamond = [(rect.centerx, rect.top), (rect.right, rect.centery), (rect.centerx, rect.bottom), (rect.left, rect.centery)]
        pygame.draw.polygon(surface, color, diamond, 3)
        inner = rect.inflate(-10, -10)
        pygame.draw.rect(surface, color, inner, 2, border_radius=4)
    elif symbol in ("green", "leaf"):
        leaf_rect = rect.inflate(-4, -2)
        pygame.draw.ellipse(surface, color, leaf_rect)
        pygame.draw.line(surface, WHITE, (leaf_rect.left + 4, leaf_rect.bottom - 4), (leaf_rect.right - 4, leaf_rect.top + 4), 2)
    elif symbol == "quick":
        bolt = [
            (rect.centerx - 5, rect.top),
            (rect.right - 5, rect.top + 2),
            (rect.centerx + 2, rect.centery),
            (rect.right - 2, rect.centery),
            (rect.left + 5, rect.bottom),
            (rect.centerx - 2, rect.centery + 4),
            (rect.left + 2, rect.centery + 4),
        ]
        pygame.draw.polygon(surface, color, bolt)


def zone_icon(zone):
    return {
        "Transport": "transport",
        "Energy": "energy",
        "Waste": "waste",
        "Green Space": "green",
    }.get(zone, "energy")


def generate_tone(frequency, duration=0.18, volume=0.28):
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        sample_rate = pygame.mixer.get_init()[0]
        samples = int(sample_rate * duration)
        buffer = array("h")
        amplitude = int(32767 * volume)
        for i in range(samples):
            t = i / sample_rate
            envelope = 1 - (i / samples)
            sample = int(amplitude * math.sin(2 * math.pi * frequency * t) * envelope)
            buffer.append(sample)
        return pygame.mixer.Sound(buffer=buffer.tobytes())
    except pygame.error:
        return None


@dataclass
class Choice:
    name: str
    carbon: int
    budget: int
    health: int


@dataclass
class DecisionCard:
    zone: str
    title: str
    eco_choice: Choice
    quick_choice: Choice


class Button:
    def __init__(self, rect, text, base_color, hover_color, text_color=WHITE, icon=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.icon = icon
        self.enabled = True
        self.hovered = False
        self.visible = True

    def set_rect(self, rect):
        self.rect = pygame.Rect(rect)

    def update(self, mouse_pos):
        self.hovered = self.visible and self.enabled and self.rect.collidepoint(mouse_pos)

    def handle_event(self, event, mouse_pos):
        if (
            self.visible
            and self.enabled
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(mouse_pos)
        ):
            return True
        return False

    def draw(self, surface, font):
        if not self.visible:
            return

        if self.hovered:
            glow_rect = self.rect.inflate(12, 12)
            glow = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(glow, (*self.base_color, 70), glow.get_rect(), border_radius=20)
            surface.blit(glow, glow_rect.topleft)

        pygame.draw.rect(surface, SHADOW, self.rect.move(0, 4), border_radius=18)
        fill = self.hover_color if self.hovered else self.base_color
        if not self.enabled:
            fill = lerp_color(fill, (90, 90, 90), 0.5)
        pygame.draw.rect(surface, fill, self.rect, border_radius=18)
        draw_alpha_outline(surface, self.rect, (255, 255, 255, 200), width=2, border_radius=18)

        text_center = self.rect.center
        if self.icon:
            icon_rect = pygame.Rect(self.rect.x + 14, self.rect.centery - 10, 20, 20)
            draw_symbol(surface, self.icon, icon_rect, WHITE)
            text_center = (self.rect.centerx + 8, self.rect.centery)
        draw_shadowed_text(surface, font, self.text, self.text_color, text_center, center=True)


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, velocity, color, lifetime, size, kind="circle", gravity=0.0, fade=True):
        self.particles.append(
            {
                "x": float(x),
                "y": float(y),
                "vx": float(velocity[0]),
                "vy": float(velocity[1]),
                "life": float(lifetime),
                "max_life": float(lifetime),
                "size": float(size),
                "color": color,
                "kind": kind,
                "gravity": gravity,
                "fade": fade,
                "rotation": random.uniform(0, math.pi * 2),
                "spin": random.uniform(-5, 5),
            }
        )

    def spawn_leaf_burst(self, center, count=18):
        for _ in range(count):
            angle = random.uniform(math.pi, math.pi * 2)
            speed = random.uniform(40, 120)
            vx = math.cos(angle) * speed + random.uniform(-15, 15)
            vy = math.sin(angle) * speed
            color = random.choice([(0, 255, 136), (76, 255, 173), (167, 255, 206)])
            self.emit(center[0], center[1], (vx, vy), color, random.uniform(0.8, 1.6), random.uniform(5, 10), kind="leaf", gravity=42)

    def spawn_smoke_burst(self, center, count=20):
        for _ in range(count):
            vx = random.uniform(-40, 40)
            vy = random.uniform(-120, -30)
            gray = random.randint(90, 150)
            self.emit(center[0], center[1], (vx, vy), (gray, gray, gray), random.uniform(1.0, 1.8), random.uniform(8, 16), kind="smoke", gravity=-8)

    def spawn_title_carbon(self, area_rect, count=2):
        for _ in range(count):
            x = random.uniform(area_rect.left, area_rect.right)
            y = area_rect.bottom + random.uniform(0, 40)
            self.emit(x, y, (random.uniform(-8, 8), random.uniform(-55, -25)), (140, 220, 180), random.uniform(1.8, 2.8), random.uniform(3, 7), kind="circle")

    def spawn_celebration(self, area_rect, count=16):
        for _ in range(count):
            x = random.uniform(area_rect.left, area_rect.right)
            y = area_rect.top + random.uniform(0, area_rect.height * 0.45)
            color = random.choice([GREEN, YELLOW, (110, 210, 255), WHITE, (255, 116, 116)])
            self.emit(x, y, (random.uniform(-70, 70), random.uniform(-20, 140)), color, random.uniform(1.0, 2.0), random.uniform(2, 5), kind="spark", gravity=42)

    def spawn_end_smoke(self, area_rect, count=10):
        for _ in range(count):
            x = random.uniform(area_rect.left, area_rect.right)
            y = area_rect.top + random.uniform(0, area_rect.height)
            color = random.choice([(255, 110, 110), (255, 200, 110), (180, 180, 190), (255, 90, 90)])
            self.emit(x, y, (random.uniform(-26, 26), random.uniform(-40, 40)), color, random.uniform(0.9, 1.6), random.uniform(2, 5), kind="circle", gravity=14)

    def update(self, dt):
        alive = []
        for particle in self.particles:
            particle["life"] -= dt
            if particle["life"] <= 0:
                continue
            particle["vx"] *= 0.992
            particle["vy"] += particle["gravity"] * dt
            particle["x"] += particle["vx"] * dt
            particle["y"] += particle["vy"] * dt
            particle["rotation"] += particle["spin"] * dt
            alive.append(particle)
        self.particles = alive

    def draw(self, surface, offset=(0, 0)):
        ox, oy = offset
        for particle in self.particles:
            alpha = int(255 * (particle["life"] / particle["max_life"])) if particle["fade"] else 255
            size = max(1, int(particle["size"]))
            particle_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
            color = (*particle["color"], alpha)
            center = (particle_surface.get_width() // 2, particle_surface.get_height() // 2)

            if particle["kind"] == "leaf":
                rect = pygame.Rect(0, 0, size * 2, size)
                rect.center = center
                pygame.draw.ellipse(particle_surface, color, rect)
                pygame.draw.line(
                    particle_surface,
                    (*WHITE, alpha),
                    (center[0] - size // 2, center[1] + size // 2),
                    (center[0] + size, center[1] - size // 2),
                    1,
                )
                particle_surface = pygame.transform.rotate(particle_surface, math.degrees(particle["rotation"]))
            elif particle["kind"] == "spark":
                pygame.draw.circle(particle_surface, color, center, size)
                pygame.draw.line(particle_surface, color, (center[0] - size, center[1]), (center[0] + size, center[1]), 1)
                pygame.draw.line(particle_surface, color, (center[0], center[1] - size), (center[0], center[1] + size), 1)
            else:
                pygame.draw.circle(particle_surface, color, center, size)

            draw_x = int(particle["x"] + ox - particle_surface.get_width() / 2)
            draw_y = int(particle["y"] + oy - particle_surface.get_height() / 2)
            surface.blit(particle_surface, (draw_x, draw_y))


class CityRenderer:
    def __init__(self):
        self.area = CITY_PANEL_RECT.copy()
        road_top = self.area.height - 94
        base_y = road_top - 8

        def make_cluster(start_x, specs):
            buildings = []
            for x_offset, width, height, style in specs:
                rect = pygame.Rect(start_x + x_offset, base_y - height, width, height)
                buildings.append({"rect": rect, "style": style})
            return buildings

        self.zone_layout = {
            "Transport": {
                "buildings": make_cluster(32, [(0, 34, 238, "skyscraper"), (42, 82, 156, "office"), (96, 46, 88, "shop")]),
                "label_pos": (98, road_top + 30),
                "accent": "transport",
            },
            "Energy": {
                "buildings": make_cluster(204, [(0, 38, 216, "skyscraper"), (48, 88, 148, "office"), (100, 44, 98, "shop")]),
                "label_pos": (275, road_top + 30),
                "accent": "energy",
            },
            "Waste": {
                "buildings": make_cluster(382, [(0, 76, 122, "office"), (58, 36, 194, "skyscraper"), (100, 48, 82, "shop")]),
                "label_pos": (451, road_top + 30),
                "accent": "waste",
            },
            "Green Space": {
                "buildings": make_cluster(540, [(0, 36, 176, "skyscraper"), (44, 80, 132, "office"), (96, 42, 86, "shop")]),
                "label_pos": (603, road_top + 30),
                "accent": "green",
            },
        }

        self.zone_centers = {
            zone: (
                self.area.x + sum(entry["rect"].centerx for entry in data["buildings"]) / len(data["buildings"]),
                self.area.y + base_y - 60,
            )
            for zone, data in self.zone_layout.items()
        }
        self.zone_visuals = {zone: {"score": 0.0, "target": 0.0} for zone in self.zone_layout}

        rng = random.Random(24)
        self.stars = []
        for _ in range(54):
            x = rng.randint(18, self.area.width - 18)
            y = rng.randint(18, int(self.area.height * 0.35))
            size = rng.randint(1, 2)
            self.stars.append((x, y, size))

    def set_zone_state(self, zone, score):
        if zone in self.zone_visuals:
            self.zone_visuals[zone]["target"] = clamp(score / 4.0, -1.0, 1.0)

    def update(self, dt):
        for zone in self.zone_visuals:
            current = self.zone_visuals[zone]["score"]
            target = self.zone_visuals[zone]["target"]
            self.zone_visuals[zone]["score"] = lerp(current, target, min(1.0, dt * 4.5))

    def _zone_color(self, zone):
        amount = self.zone_visuals[zone]["score"]
        if amount >= 0:
            return lerp_color(GRAY, ZONE_COLORS.get(zone, GREEN), amount)
        return lerp_color(GRAY, RED, abs(amount))

    def _draw_building(self, surface, rect, style, base_color, pollution):
        pygame.draw.rect(surface, SHADOW, rect.move(4, 5), border_radius=6)

        shade = base_color
        if style == "office":
            shade = lerp_color(base_color, (210, 210, 220), 0.08)
        elif style == "shop":
            shade = lerp_color(base_color, (250, 250, 255), 0.14)

        pygame.draw.rect(surface, shade, rect, border_radius=6)
        pygame.draw.rect(surface, (10, 12, 18), rect, 2, border_radius=6)

        window_color = lerp_color((252, 236, 120), (255, 160, 92), pollution * 0.85)
        step_x = 14 if style == "skyscraper" else 18
        step_y = 18 if style == "skyscraper" else 20
        margin_x = 7
        margin_y = 10
        for wx in range(rect.x + margin_x, rect.right - 8, step_x):
            for wy in range(rect.y + margin_y, rect.bottom - 16, step_y):
                window = pygame.Rect(wx, wy, 6 if style == "shop" else 7, 9)
                pygame.draw.rect(surface, window_color, window, border_radius=2)

        if style == "skyscraper":
            pygame.draw.line(surface, (220, 220, 230), (rect.centerx, rect.y), (rect.centerx, rect.y - 12), 2)
            pygame.draw.circle(surface, (220, 220, 230), (rect.centerx, rect.y - 12), 2)
        elif style == "shop":
            awning = pygame.Rect(rect.x + 4, rect.y + rect.height // 2 - 10, rect.width - 8, 12)
            pygame.draw.rect(surface, lerp_color(base_color, WHITE, 0.24), awning, border_radius=4)

    def draw(self, surface, carbon_level, offset=(0, 0)):
        ox, oy = offset
        area = self.area.move(ox, oy)
        pollution = carbon_level / 100.0
        clip_before = push_clip(surface, area)

        top_color = lerp_color((37, 42, 102), (89, 42, 60), pollution * 0.75)
        mid_color = lerp_color((79, 93, 162), (150, 78, 72), pollution * 0.65)
        horizon_color = lerp_color((255, 176, 112), (255, 120, 82), pollution)

        sky_surface = pygame.Surface(area.size)
        for y in range(area.height):
            blend = y / area.height
            color = lerp_color(top_color, mid_color, min(1.0, blend * 1.5))
            if blend > 0.58:
                color = lerp_color(color, horizon_color, (blend - 0.58) / 0.42)
            pygame.draw.line(sky_surface, color, (0, y), (area.width, y))
        surface.blit(sky_surface, area.topleft)

        star_color = lerp_color((255, 255, 255), (255, 208, 178), pollution * 0.35)
        if pollution < 0.92:
            for x, y, size in self.stars:
                pygame.draw.circle(surface, star_color, (area.x + x, area.y + y), size)

        haze = pygame.Surface(area.size, pygame.SRCALPHA)
        pygame.draw.rect(haze, (220, 70, 50, int(70 * pollution)), haze.get_rect())
        surface.blit(haze, area.topleft)

        hill_back = []
        hill_front = []
        for step in range(0, area.width + 26, 26):
            hill_back.append((area.x + step, area.bottom - 180 - math.sin(step * 0.012) * 24 - math.cos(step * 0.023) * 16))
            hill_front.append((area.x + step, area.bottom - 148 - math.sin(step * 0.017 + 1.2) * 32 - math.cos(step * 0.03) * 10))
        pygame.draw.polygon(surface, (38, 40, 63), [(area.left, area.bottom)] + hill_back + [(area.right, area.bottom)])
        pygame.draw.polygon(surface, (28, 30, 50), [(area.left, area.bottom)] + hill_front + [(area.right, area.bottom)])

        sun_color = lerp_color((255, 223, 154), (255, 136, 92), pollution)
        pygame.draw.circle(surface, sun_color, (area.right - 115, area.top + 96), 38)

        road_rect = pygame.Rect(area.left, area.bottom - 76, area.width, 76)
        pavement_rect = pygame.Rect(area.left, road_rect.y - 18, area.width, 18)
        pygame.draw.rect(surface, (56, 60, 74), pavement_rect)
        pygame.draw.rect(surface, (33, 36, 49), road_rect)
        pygame.draw.line(surface, (120, 128, 145), (area.left, pavement_rect.y), (area.right, pavement_rect.y), 2)
        pygame.draw.line(surface, (76, 82, 98), (area.left, road_rect.y + 2), (area.right, road_rect.y + 2), 2)

        dash_y = road_rect.y + road_rect.height // 2
        for dash_x in range(area.left + 24, area.right - 24, 52):
            pygame.draw.rect(surface, (245, 245, 245), (dash_x, dash_y, 26, 4), border_radius=2)

        for zone, data in self.zone_layout.items():
            zone_color = self._zone_color(zone)
            for building in data["buildings"]:
                draw_rect = building["rect"].move(area.x, area.y)
                self._draw_building(surface, draw_rect, building["style"], zone_color, pollution)

            if data["accent"] == "transport":
                track_y = pavement_rect.y - 12
                pygame.draw.line(surface, (18, 18, 24), (area.x + 24, track_y), (area.x + 158, track_y), 6)
                pygame.draw.line(surface, (120, 220, 255), (area.x + 40, track_y - 6), (area.x + 142, track_y - 6), 3)
            elif data["accent"] == "energy":
                for base_x in (area.x + 262, area.x + 320):
                    stem_bottom = pavement_rect.y - 10
                    pygame.draw.line(surface, (220, 220, 230), (base_x, stem_bottom), (base_x, stem_bottom - 44), 3)
                    center = (base_x, stem_bottom - 44)
                    for angle in (0, 120, 240):
                        radians = math.radians(angle + pygame.time.get_ticks() * 0.07)
                        tip = (center[0] + math.cos(radians) * 14, center[1] + math.sin(radians) * 14)
                        pygame.draw.line(surface, (230, 230, 240), center, tip, 2)
                    pygame.draw.circle(surface, (230, 230, 240), center, 3)
            elif data["accent"] == "waste":
                for bx in (area.x + 428, area.x + 456, area.x + 484):
                    bin_rect = pygame.Rect(bx, pavement_rect.y - 26, 18, 24)
                    pygame.draw.rect(surface, zone_color, bin_rect, border_radius=4)
                    pygame.draw.rect(surface, (15, 15, 20), bin_rect, 2, border_radius=4)
            elif data["accent"] == "green":
                for tx in (area.x + 566, area.x + 620):
                    trunk = pygame.Rect(tx, pavement_rect.y - 28, 6, 22)
                    pygame.draw.rect(surface, (104, 70, 38), trunk, border_radius=3)
                    pygame.draw.circle(surface, zone_color, (tx + 3, pavement_rect.y - 34), 16)

            label_pos = (area.x + data["label_pos"][0], area.y + data["label_pos"][1])
            draw_shadowed_text(surface, FONT_SMALL_BOLD, zone, LIGHT_GRAY, label_pos, center=True)

        for tree_x in (area.left + 38, area.left + 186, area.left + 340, area.left + 502, area.left + 640):
            trunk = pygame.Rect(tree_x, pavement_rect.y - 24, 6, 18)
            pygame.draw.rect(surface, (98, 67, 41), trunk, border_radius=3)
            pygame.draw.circle(surface, (58, 165, 96), (tree_x + 3, pavement_rect.y - 28), 12)

        for lamp_x in (area.left + 112, area.left + 286, area.left + 450, area.left + 606):
            pygame.draw.line(surface, (188, 194, 205), (lamp_x, pavement_rect.y), (lamp_x, pavement_rect.y - 30), 3)
            pygame.draw.circle(surface, (255, 237, 166), (lamp_x, pavement_rect.y - 34), 5)

        surface.set_clip(clip_before)


class CarbonMeter:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.value = 50
        self.display_value = 50.0
        self.pulse_time = 0.0

    def set_value(self, value):
        self.value = clamp(value, 0, 100)

    def update(self, dt):
        self.display_value = lerp(self.display_value, self.value, min(1.0, dt * 4.8))
        self.pulse_time += dt

    def draw(self, surface, warning_active=False):
        frame = self.rect
        draw_panel(surface, frame, PANEL_COLOR, border_color=(255, 255, 255, 34), radius=16, border_width=1)
        clip_before = push_clip(surface, frame)

        draw_shadowed_text(surface, FONT_SMALL_BOLD, "CARBON LEVEL", LIGHT_GRAY, (frame.centerx, frame.y + 18), center=True)
        value_text = FONT_BODY_BOLD.render(f"{int(round(self.display_value))}/100", True, WHITE)
        value_text.set_alpha(220)
        value_rect = value_text.get_rect(center=(frame.centerx, frame.y + 44))
        surface.blit(value_text, value_rect)

        meter_outer_rect = pygame.Rect(frame.x + 36, frame.y + 68, 48, frame.height - 100)
        meter_inner_rect = meter_outer_rect.inflate(-10, -10)
        pygame.draw.rect(surface, (8, 12, 22), meter_outer_rect, border_radius=12)
        draw_alpha_outline(surface, meter_outer_rect, (255, 255, 255, 51), width=2, border_radius=12)

        fill_height = int((self.display_value / 100.0) * meter_inner_rect.height)
        meter_bottom = meter_inner_rect.bottom - 1
        surface.set_clip(meter_inner_rect)
        for i in range(fill_height):
            t = i / max(meter_inner_rect.height, 1)
            r = int(lerp(0, 255, t))
            g = int(lerp(255, 68, t))
            b = int(lerp(136, 68, t))
            y = meter_bottom - i
            pygame.draw.line(surface, (r, g, b), (meter_inner_rect.x, y), (meter_inner_rect.right - 1, y))
        surface.set_clip(None)

        for tick in range(0, 101, 25):
            y = meter_outer_rect.bottom - int((tick / 100.0) * meter_outer_rect.height)
            pygame.draw.line(surface, (76, 84, 108), (meter_outer_rect.right + 10, y), (meter_outer_rect.right + 22, y), 2)
            draw_shadowed_text(surface, FONT_SMALL, str(tick), LIGHT_GRAY, (meter_outer_rect.right + 26, y - 8))

        if self.value >= 80:
            pulse = (math.sin(self.pulse_time * 10) + 1) * 0.5
            alert = pygame.Surface(frame.size, pygame.SRCALPHA)
            pygame.draw.rect(alert, (255, 40, 40, int(40 + pulse * 80)), alert.get_rect(), 4, border_radius=16)
            surface.blit(alert, frame.topleft)
            draw_shadowed_text(surface, FONT_SMALL_BOLD, "CRITICAL", RED if warning_active else YELLOW, (frame.centerx, frame.bottom - 24), center=True)

        surface.set_clip(clip_before)


class HUD:
    def __init__(self):
        self.rect = HUD_RECT.copy()
        self.left_pill = pygame.Rect(10, 26, 200, 38)
        self.right_pill = pygame.Rect(1070, 26, 200, 38)
        self.health_bar = pygame.Rect(440, 60, 400, 14)

    def draw(self, surface, players, current_player, round_number, city_health):
        overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(overlay, (10, 16, 30, 210), overlay.get_rect())
        surface.blit(overlay, self.rect.topleft)
        pygame.draw.line(surface, (65, 82, 118), (0, self.rect.bottom - 1), (BASE_W, self.rect.bottom - 1), 2)
        clip_before = push_clip(surface, self.rect)

        for idx, pill in enumerate((self.left_pill, self.right_pill)):
            player = players[idx]
            is_current = idx == current_player
            border = GREEN if is_current else (106, 122, 156)
            if is_current:
                glow = pygame.Surface((pill.width + 10, pill.height + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow, (*GREEN, 60), glow.get_rect(), border_radius=26)
                surface.blit(glow, (pill.x - 5, pill.y - 5))
            pygame.draw.rect(surface, PANEL_COLOR, pill, border_radius=22)
            draw_alpha_outline(surface, pill, border, width=2, border_radius=22)
            dot_color = GREEN if is_current else (96, 108, 132)
            pygame.draw.circle(surface, dot_color, (pill.x + 16, pill.centery), 6)
            if is_current:
                pygame.draw.circle(surface, WHITE, (pill.x + 16, pill.centery), 2)
            draw_shadowed_text(surface, FONT_SMALL_BOLD, player["name"], WHITE, (pill.x + 28, pill.y + 7))
            budget_color = GREEN if player["budget"] >= 40 else YELLOW if player["budget"] >= 15 else RED
            draw_shadowed_text(surface, FONT_SMALL_BOLD, f"{player['budget']}c", budget_color, (pill.right - 58, pill.y + 7))

        draw_shadowed_text(surface, FONT_HEADING, f"Round {round_number} / 15", WHITE, (640, 18), center=True)
        draw_shadowed_text(surface, FONT_SMALL_BOLD, "CITY HEALTH", LIGHT_GRAY, (640, 44), center=True)
        pygame.draw.rect(surface, PANEL_DARK, self.health_bar, border_radius=8)
        draw_alpha_outline(surface, self.health_bar, (255, 255, 255, 180), width=2, border_radius=8)
        fill_width = int((clamp(city_health, 0, 100) / 100.0) * (self.health_bar.width - 4))
        fill_rect = pygame.Rect(self.health_bar.x + 2, self.health_bar.y + 2, fill_width, self.health_bar.height - 4)
        health_color = GREEN if city_health >= 60 else YELLOW if city_health >= 30 else RED
        pygame.draw.rect(surface, health_color, fill_rect, border_radius=6)
        draw_shadowed_text(surface, FONT_SMALL, str(int(city_health)), health_color, (self.health_bar.right + 18, self.health_bar.y - 1))
        surface.set_clip(clip_before)


class CardSystem:
    def __init__(self):
        self.card_rect = CARD_PANEL_RECT.copy()
        self.eco_button = Button((0, 0, 0, 0), "ECO CHOICE", (0, 180, 96), (0, 220, 120), icon="leaf")
        self.quick_button = Button((0, 0, 0, 0), "QUICK CHOICE", (204, 56, 56), (244, 76, 76), icon="quick")
        self.cards = self._build_cards()
        self.current_card = None
        self.current_index = -1
        self.slide_progress = 1.0
        self.slide_duration = 0.45
        self.show_card(random.randint(0, len(self.cards) - 1))

    def _build_cards(self):
        return [
            DecisionCard("Transport", "Downtown Commute Plan", Choice("Build a Metro Line", -8, -20, 5), Choice("Add More Highways", 10, -15, -3)),
            DecisionCard("Transport", "Neighborhood Streets", Choice("Install Bike Lanes", -5, -8, 3), Choice("Add More Highways", 10, -15, -3)),
            DecisionCard("Transport", "Regional Expansion", Choice("Build a Metro Line", -8, -20, 5), Choice("Expand Airport", 12, -25, -2)),
            DecisionCard("Energy", "Power Grid Upgrade", Choice("Build Solar Farm", -10, -30, 8), Choice("Build Coal Plant", 15, -10, -10)),
            DecisionCard("Energy", "Future Energy Mix", Choice("Wind Turbines", -8, -25, 6), Choice("Natural Gas Plant", 8, -12, -4)),
            DecisionCard("Energy", "Industrial Demand Spike", Choice("Build Solar Farm", -10, -30, 8), Choice("Natural Gas Plant", 8, -12, -4)),
            DecisionCard("Energy", "Regional Reliability Vote", Choice("Wind Turbines", -8, -25, 6), Choice("Build Coal Plant", 15, -10, -10)),
            DecisionCard("Waste", "Community Waste Strategy", Choice("Recycling Program", -4, -10, 4), Choice("Open Landfill", 6, -5, -5)),
            DecisionCard("Waste", "Food Waste Response", Choice("Composting Initiative", -3, -8, 3), Choice("Open Landfill", 6, -5, -5)),
            DecisionCard("Waste", "School Sustainability Drive", Choice("Recycling Program", -4, -10, 4), Choice("Open Landfill", 6, -5, -5)),
            DecisionCard("Green Space", "Vacant Lot Decision", Choice("Plant Urban Forest", -7, -15, 7), Choice("Build Shopping Mall", 9, 10, -6)),
            DecisionCard("Green Space", "Riverfront Redevelopment", Choice("Plant Urban Forest", -7, -15, 7), Choice("Build Shopping Mall", 9, 10, -6)),
            DecisionCard("Transport", "Tourism Growth Debate", Choice("Install Bike Lanes", -5, -8, 3), Choice("Expand Airport", 12, -25, -2)),
        ]

    def show_card(self, index=None):
        if index is None:
            choices = list(range(len(self.cards)))
            if len(choices) > 1 and self.current_index in choices:
                choices.remove(self.current_index)
            self.current_index = random.choice(choices)
        else:
            self.current_index = index
        self.current_card = self.cards[self.current_index]
        self.slide_progress = 0.0

    def update(self, dt, mouse_pos):
        self.slide_progress = min(1.0, self.slide_progress + dt / self.slide_duration)
        frame = self.current_rect()
        self.eco_button.set_rect((frame.x + 16, frame.y + 246, frame.width - 32, 26))
        self.quick_button.set_rect((frame.x + 16, frame.y + 278, frame.width - 32, 26))
        self.eco_button.update(mouse_pos)
        self.quick_button.update(mouse_pos)

    def current_rect(self):
        x = int(lerp(BASE_W + 40, self.card_rect.x, self.slide_progress))
        return self.card_rect.move(x - self.card_rect.x, 0)

    def handle_event(self, event, mouse_pos):
        if self.slide_progress < 0.92:
            return None
        if self.eco_button.handle_event(event, mouse_pos):
            return "eco"
        if self.quick_button.handle_event(event, mouse_pos):
            return "quick"
        return None

    def draw_badge(self, surface, x, y, text, color):
        text_surface = FONT_SMALL.render(text, True, color)
        badge_rect = pygame.Rect(x, y, text_surface.get_width() + 16, text_surface.get_height() + 8)
        pygame.draw.rect(surface, PANEL_DARK, badge_rect, border_radius=14)
        draw_alpha_outline(surface, badge_rect, color, width=2, border_radius=14)
        draw_shadowed_text(surface, FONT_SMALL, text, color, badge_rect.center, center=True)
        return badge_rect

    def draw(self, surface, current_budget):
        if not self.current_card:
            return

        frame = self.current_rect()
        draw_panel(surface, frame, PANEL_COLOR, border_color=(255, 255, 255, 34), radius=16, border_width=1)
        clip_before = push_clip(surface, frame)
        zone_color = ZONE_COLORS.get(self.current_card.zone, WHITE)

        header_rect = pygame.Rect(frame.x, frame.y, frame.width, 46)
        pygame.draw.rect(surface, zone_color, header_rect, border_top_left_radius=16, border_top_right_radius=16)
        icon_rect = pygame.Rect(header_rect.x + 16, header_rect.y + 11, 24, 24)
        draw_symbol(surface, zone_icon(self.current_card.zone), icon_rect, PANEL_DARK)
        draw_shadowed_text(surface, FONT_SMALL_BOLD, self.current_card.zone.upper(), PANEL_DARK, (header_rect.x + 50, header_rect.y + 12))

        content_x = frame.x + 16
        draw_shadowed_text(surface, FONT_BODY_BOLD, self.current_card.title, WHITE, (content_x, frame.y + 60))
        budget_badge = self.draw_badge(surface, content_x, frame.y + 88, f"Budget {current_budget}", LIGHT_GRAY)

        eco_rect = pygame.Rect(content_x, budget_badge.bottom + 10, frame.width - 32, 56)
        quick_rect = pygame.Rect(content_x, eco_rect.bottom + 10, frame.width - 32, 56)
        self.draw_choice_panel(surface, eco_rect, self.current_card.eco_choice, GREEN)
        self.draw_choice_panel(surface, quick_rect, self.current_card.quick_choice, RED)

        self.eco_button.draw(surface, FONT_SMALL_BOLD)
        self.quick_button.draw(surface, FONT_SMALL_BOLD)
        surface.set_clip(clip_before)

    def draw_choice_panel(self, surface, rect, choice, accent_color):
        pygame.draw.rect(surface, PANEL_DARK, rect, border_radius=16)
        draw_alpha_outline(surface, rect, (255, 255, 255, 34), width=1, border_radius=16)
        pygame.draw.rect(surface, accent_color, (rect.x, rect.y, 8, rect.height), border_top_left_radius=16, border_bottom_left_radius=16)
        draw_shadowed_text(surface, FONT_SMALL_BOLD, choice.name, WHITE, (rect.x + 18, rect.y + 7))

        badge_y = rect.y + 28
        x = rect.x + 18
        for text, color in (
            (f"Carbon {choice.carbon:+d}", GREEN if choice.carbon < 0 else RED),
            (f"Budget {choice.budget:+d}", GREEN if choice.budget > 0 else YELLOW),
            (f"Health {choice.health:+d}", GREEN if choice.health > 0 else RED),
        ):
            badge = self.draw_badge(surface, x, badge_y, text, color)
            x = badge.right + 8


class Game:
    def __init__(self):
        self.screen = SCREEN
        self.base_surface = BASE_SURFACE
        self.clock = pygame.time.Clock()
        self.hud = HUD()
        self.city = CityRenderer()
        self.carbon_meter = CarbonMeter(METER_CONTAINER_RECT)
        self.card_system = CardSystem()
        self.particles = ParticleSystem()
        self.replay_button = Button((540, 570, 180, 52), "Replay", (0, 180, 96), (0, 220, 120))
        self.quit_button = Button((760, 570, 180, 52), "Quit", (204, 56, 56), (244, 76, 76))

        self.sounds = {
            "eco": generate_tone(680, 0.17, 0.30),
            "quick": generate_tone(240, 0.20, 0.34),
            "warning": generate_tone(920, 0.12, 0.26),
            "click": generate_tone(500, 0.08, 0.22),
        }

        self.show_resolution_debug = True
        self.title_particles_timer = 0.0
        self.end_particles_timer = 0.0
        self.warning_played = False
        self.shake_time = 0.0
        self.shake_strength = 0.0
        self.title_float = 0.0
        self.compat_overlay_elapsed = 0.0
        self.running = True
        self.reset_game()

    def reset_game(self):
        self.state = "title"
        self.players = [
            {"name": "Player 1", "budget": 100, "eco": 0, "quick": 0, "decisions": 0},
            {"name": "Player 2", "budget": 100, "eco": 0, "quick": 0, "decisions": 0},
        ]
        self.current_player = 0
        self.completed_rounds = 0
        self.city_health = 100
        self.carbon_level = 50
        self.carbon_meter.set_value(50)
        self.zone_scores = {zone: 0 for zone in self.city.zone_layout}
        for zone in self.zone_scores:
            self.city.set_zone_state(zone, 0)
        self.card_system.show_card()
        self.particles = ParticleSystem()
        self.warning_played = False
        self.shake_time = 0.0
        self.shake_strength = 0.0
        self.title_particles_timer = 0.0
        self.end_particles_timer = 0.0
        self.compat_overlay_elapsed = 0.0
        self.result = {"title": "", "subtitle": ""}

    def play_sound(self, key):
        sound = self.sounds.get(key)
        if sound:
            sound.play()

    def start_gameplay(self):
        self.state = "game"
        self.particles = ParticleSystem()
        self.card_system.show_card()

    def current_round_number(self):
        return min(15, self.completed_rounds + 1)

    def apply_choice(self, choice_type):
        card = self.card_system.current_card
        choice = card.eco_choice if choice_type == "eco" else card.quick_choice
        player = self.players[self.current_player]

        player["budget"] = clamp(player["budget"] + choice.budget, 0, 250)
        player["decisions"] += 1
        player[choice_type] += 1

        self.carbon_level = clamp(self.carbon_level + choice.carbon, 0, 100)
        self.city_health = clamp(self.city_health + choice.health, 0, 100)
        self.carbon_meter.set_value(self.carbon_level)

        zone_delta = 1 if choice_type == "eco" else -1
        self.zone_scores[card.zone] += zone_delta
        self.city.set_zone_state(card.zone, self.zone_scores[card.zone])

        effect_center = self.city.zone_centers[card.zone]
        if choice_type == "eco":
            self.particles.spawn_leaf_burst(effect_center, count=20)
            self.play_sound("eco")
        else:
            self.particles.spawn_smoke_burst(effect_center, count=22)
            self.play_sound("quick")

        if self.carbon_level >= 80:
            self.shake_strength = 8 if self.carbon_level < 100 else 14
            self.shake_time = 0.45
        elif choice_type == "quick":
            self.shake_strength = 4
            self.shake_time = 0.18

        if self._check_immediate_end():
            return

        if self.current_player == 1:
            self.completed_rounds += 1

        if self.completed_rounds >= 15 and self.current_player == 1:
            self.finish_by_rounds()
            return

        self.current_player = 1 - self.current_player
        self.card_system.show_card()

    def finish_by_rounds(self):
        if self.carbon_level < 60:
            self.result = {"title": "Green City", "subtitle": "Your city balanced growth and sustainability."}
        elif self.carbon_level < 80:
            self.result = {"title": "Recovering City", "subtitle": "The city survived and has a cleaner future ahead."}
        else:
            self.result = {"title": "City in Crisis", "subtitle": "You finished the rounds, but carbon remains dangerously high."}
        self.state = "end"
        self.particles = ParticleSystem()

    def _check_immediate_end(self):
        if self.carbon_level >= 100:
            self.result = {"title": "City Collapsed", "subtitle": "Carbon overload pushed the city past the breaking point."}
            self.state = "end"
            self.particles = ParticleSystem()
            return True
        if self.city_health <= 0:
            self.result = {"title": "Health Crisis", "subtitle": "The city could not withstand the environmental damage."}
            self.state = "end"
            self.particles = ParticleSystem()
            return True
        return False

    def handle_events(self):
        mouse_pos = to_base_pos(pygame.mouse.get_pos())
        for event in pygame.event.get():
            base_event_pos = to_base_pos(event.pos) if hasattr(event, "pos") else mouse_pos

            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_F1:
                    self.show_resolution_debug = not self.show_resolution_debug
                elif self.state == "title" and event.key == pygame.K_SPACE:
                    self.play_sound("click")
                    self.start_gameplay()
            elif self.state == "game":
                choice = self.card_system.handle_event(event, base_event_pos)
                if choice:
                    self.apply_choice(choice)
            elif self.state == "end":
                if self.replay_button.handle_event(event, base_event_pos):
                    self.play_sound("click")
                    self.reset_game()
                    self.start_gameplay()
                elif self.quit_button.handle_event(event, base_event_pos):
                    self.play_sound("click")
                    self.running = False

        if self.state == "game":
            self.card_system.update(self.clock.get_time() / 1000.0, mouse_pos)
        elif self.state == "end":
            self.replay_button.update(mouse_pos)
            self.quit_button.update(mouse_pos)

    def update(self, dt):
        self.title_float += dt
        self.carbon_meter.update(dt)
        self.city.update(dt)
        self.particles.update(dt)

        if self.state == "title":
            self.compat_overlay_elapsed += dt
            self.title_particles_timer += dt
            while self.title_particles_timer >= 0.08:
                self.title_particles_timer -= 0.08
                self.particles.spawn_title_carbon(TITLE_PARTICLE_RECT, 2)
        elif self.state == "game":
            if self.carbon_level >= 80 and not self.warning_played:
                self.play_sound("warning")
                self.warning_played = True
            elif self.carbon_level < 80:
                self.warning_played = False
        elif self.state == "end":
            self.end_particles_timer += dt
            if "Green" in self.result["title"] or "Recovering" in self.result["title"]:
                while self.end_particles_timer >= 0.12:
                    self.end_particles_timer -= 0.12
                    self.particles.spawn_celebration(END_PARTICLE_RECT.move(0, -10), count=12)
            else:
                while self.end_particles_timer >= 0.16:
                    self.end_particles_timer -= 0.16
                    self.particles.spawn_end_smoke(END_PARTICLE_RECT, count=9)

        if self.shake_time > 0:
            self.shake_time -= dt
            if self.shake_time <= 0:
                self.shake_strength = 0

    def game_offset(self):
        if self.shake_time <= 0:
            return (0, 0)
        strength = self.shake_strength * (self.shake_time / 0.45)
        return (random.uniform(-strength, strength), random.uniform(-strength * 0.6, strength * 0.6))

    def draw_title(self):
        surface = self.base_surface
        top_color = (30, 34, 82)
        bottom_color = (255, 164, 96)
        for y in range(BASE_H):
            blend = y / BASE_H
            color = lerp_color(top_color, bottom_color, min(1.0, blend * 1.2))
            pygame.draw.line(surface, color, (0, y), (BASE_W, y))

        for x in range(0, BASE_W, 28):
            star_y = 40 + (x * 17) % 220
            size = 1 + ((x // 28) % 2)
            pygame.draw.circle(surface, WHITE, (x + 12, star_y), size)

        self._draw_title_silhouette(surface, 0.18, BASE_H - 142, (24, 30, 56), 232)
        self._draw_title_silhouette(surface, 0.33, BASE_H - 102, (16, 22, 42), 186)
        pygame.draw.rect(surface, (20, 24, 38), (0, BASE_H - 86, BASE_W, 86))

        title_y = 160 + math.sin(self.title_float * 2.1) * 5
        draw_shadowed_text(surface, FONT_TITLE, "Carbon Quest", GREEN, (BASE_W // 2, title_y), center=True)
        draw_shadowed_text(surface, FONT_HEADING, "City Builder Challenge", WHITE, (BASE_W // 2, 246), center=True)
        draw_shadowed_text(
            surface,
            FONT_BODY,
            "Build a thriving city without tipping the Carbon Meter.",
            LIGHT_GRAY,
            (BASE_W // 2, 292),
            center=True,
        )

        prompt_alpha = 130 + int((math.sin(self.title_float * 4.2) + 1) * 54)
        prompt = FONT_HEADING.render("Press SPACE to Start", True, WHITE)
        prompt.set_alpha(prompt_alpha)
        prompt_rect = prompt.get_rect(center=(BASE_W // 2, 610))
        surface.blit(prompt, prompt_rect)

        if COMPAT_MODE and self.compat_overlay_elapsed < 3.0:
            bar_alpha = max(0, 255 - int((self.compat_overlay_elapsed / 3.0) * 255))
            if bar_alpha > 0:
                bar_rect = pygame.Rect(0, BASE_H - 36, BASE_W, 36)
                overlay = pygame.Surface(bar_rect.size, pygame.SRCALPHA)
                overlay.fill((12, 16, 26, bar_alpha))
                surface.blit(overlay, bar_rect.topleft)
                text = FONT_SMALL.render("Display not natively supported — running in 720p compatibility mode", True, WHITE)
                text.set_alpha(bar_alpha)
                surface.blit(text, text.get_rect(center=bar_rect.center))

        self.particles.draw(surface)

    def _draw_title_silhouette(self, surface, speed, baseline, color, tile_width):
        offset = (self.title_float * speed * 220) % tile_width
        for index in range(-2, BASE_W // tile_width + 4):
            tile_x = int(index * tile_width - offset)
            widths = (36, 62, 42, 76)
            heights = (
                120 + (index % 4) * 16,
                84 + (index % 3) * 18,
                132 + ((index + 1) % 5) * 12,
                72 + ((index + 2) % 4) * 14,
            )
            cursor = tile_x
            for width, height in zip(widths, heights):
                rect = pygame.Rect(cursor, baseline - height, width, height)
                pygame.draw.rect(surface, color, rect, border_radius=5)
                cursor += width + 12

    def draw_game(self):
        surface = self.base_surface
        surface.fill(BG_COLOR)
        shake_offset = self.game_offset()

        right_bg = RIGHT_PANEL_RECT.copy()
        pygame.draw.rect(surface, PANEL_DARK, right_bg, border_radius=18)
        draw_alpha_outline(surface, right_bg, (255, 255, 255, 20), width=1, border_radius=18)

        divider_x = CITY_PANEL_RECT.right + 5
        pygame.draw.line(surface, (125, 146, 190), (divider_x, CITY_PANEL_RECT.top), (divider_x, CITY_PANEL_RECT.bottom), 2)

        self.hud.draw(surface, self.players, self.current_player, self.current_round_number(), self.city_health)

        city_clip = push_clip(surface, CITY_PANEL_RECT)
        self.city.draw(surface, self.carbon_level, offset=shake_offset)
        self.particles.draw(surface, offset=shake_offset)
        surface.set_clip(city_clip)

        self.carbon_meter.draw(surface, warning_active=self.carbon_level >= 80)
        self.card_system.draw(surface, self.players[self.current_player]["budget"])

    def eco_rating(self):
        total_decisions = sum(player["decisions"] for player in self.players)
        eco_choices = sum(player["eco"] for player in self.players)
        ratio = eco_choices / total_decisions if total_decisions else 0.5
        if ratio >= 0.6:
            return "\U0001F331 Green Hero", GREEN
        if ratio >= 0.4:
            return "\u26A0\uFE0F City Planner", YELLOW
        return "\u2620\uFE0F Carbon Criminal", RED

    def draw_end(self):
        surface = self.base_surface
        surface.fill(BG_COLOR)
        result_is_good = "Green" in self.result["title"] or "Recovering" in self.result["title"]

        panel = pygame.Rect(92, 64, 1096, 594)
        accent = GREEN if result_is_good else RED
        draw_panel(surface, panel, PANEL_COLOR, accent, radius=28, border_width=2)
        clip_before = push_clip(surface, panel)

        overlay = pygame.Surface(panel.size, pygame.SRCALPHA)
        pygame.draw.rect(overlay, (*accent, 24), overlay.get_rect(), border_radius=28)
        surface.blit(overlay, panel.topleft)

        draw_shadowed_text(surface, FONT_TITLE, self.result["title"], accent, (BASE_W // 2, 126), center=True)
        draw_shadowed_text(surface, FONT_BODY_BOLD, self.result["subtitle"], WHITE, (BASE_W // 2, 174), center=True)

        rating_text, rating_color = self.eco_rating()
        rating_rect = pygame.Rect(BASE_W // 2 - 170, 204, 340, 40)
        pygame.draw.rect(surface, PANEL_DARK, rating_rect, border_radius=20)
        draw_alpha_outline(surface, rating_rect, rating_color, width=2, border_radius=20)
        draw_shadowed_text(surface, FONT_BODY_BOLD, rating_text, rating_color, rating_rect.center, center=True)

        stats = [
            ("Final Carbon Level", str(self.carbon_level), self.carbon_level_color()),
            ("City Health", str(self.city_health), GREEN if self.city_health >= 50 else RED),
            ("Rounds Completed", str(self.completed_rounds), WHITE),
        ]
        for idx, (label, value, color) in enumerate(stats):
            stat_rect = pygame.Rect(154 + idx * 324, 270, 260, 98)
            pygame.draw.rect(surface, PANEL_DARK, stat_rect, border_radius=22)
            draw_alpha_outline(surface, stat_rect, color, width=2, border_radius=22)
            draw_shadowed_text(surface, FONT_SMALL_BOLD, label, LIGHT_GRAY, (stat_rect.centerx, stat_rect.y + 22), center=True)
            draw_shadowed_text(surface, FONT_HEADING, value, color, (stat_rect.centerx, stat_rect.y + 54), center=True)

        for idx, player in enumerate(self.players):
            player_rect = pygame.Rect(154 + idx * 486, 404, 470, 118)
            border = GREEN if idx == 0 else YELLOW
            pygame.draw.rect(surface, PANEL_DARK, player_rect, border_radius=24)
            draw_alpha_outline(surface, player_rect, border, width=2, border_radius=24)
            draw_shadowed_text(surface, FONT_BODY_BOLD, player["name"], WHITE, (player_rect.x + 20, player_rect.y + 16))
            draw_shadowed_text(surface, FONT_BODY, f"Decisions: {player['decisions']}", LIGHT_GRAY, (player_rect.x + 20, player_rect.y + 52))
            draw_shadowed_text(surface, FONT_BODY, f"Eco: {player['eco']}", GREEN, (player_rect.x + 206, player_rect.y + 52))
            draw_shadowed_text(surface, FONT_BODY, f"Quick: {player['quick']}", RED, (player_rect.x + 312, player_rect.y + 52))
            draw_shadowed_text(surface, FONT_BODY, f"Budget: {player['budget']}c", WHITE, (player_rect.x + 20, player_rect.y + 84))

        self.replay_button.set_rect((540, 570, 180, 52))
        self.quit_button.set_rect((760, 570, 180, 52))
        self.replay_button.draw(surface, FONT_BODY_BOLD)
        self.quit_button.draw(surface, FONT_BODY_BOLD)
        self.particles.draw(surface)
        surface.set_clip(clip_before)

    def carbon_level_color(self):
        value = self.carbon_level
        if value < 50:
            return lerp_color(GREEN, YELLOW, value / 50.0)
        return lerp_color(YELLOW, RED, (value - 50) / 50.0)

    def draw_resolution_debug(self):
        if not self.show_resolution_debug:
            return
        text = f"{RENDER_W}x{RENDER_H}" + (" [COMPAT]" if COMPAT_MODE else "")
        debug_surface = FONT_TINY.render(text, True, WHITE)
        debug_surface.set_alpha(68)
        debug_rect = debug_surface.get_rect(bottomright=(BASE_W - 10, BASE_H - 8))
        self.base_surface.blit(debug_surface, debug_rect)

    def present_frame(self):
        if RENDER_W == BASE_W and RENDER_H == BASE_H:
            self.screen.blit(self.base_surface, (0, 0))
        else:
            scaled = pygame.transform.smoothscale(self.base_surface, (RENDER_W, RENDER_H))
            self.screen.blit(scaled, (0, 0))
        pygame.display.flip()

    def draw(self):
        self.base_surface.fill(BG_COLOR)
        if self.state == "title":
            self.draw_title()
        elif self.state == "game":
            self.draw_game()
        else:
            self.draw_end()
        self.draw_resolution_debug()
        self.present_frame()

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()

# To build: pyinstaller --onefile --noconsole main.py
