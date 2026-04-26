import pygame
import os
import math
import random
import sys
import ctypes
from array import array
from dataclasses import dataclass

os.environ["SDL_VIDEO_CENTERED"] = "1"


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
    SCREEN = pygame.display.set_mode(
        (RENDER_W, RENDER_H), pygame.NOFRAME | pygame.HWSURFACE | pygame.DOUBLEBUF)
else:
    SCREEN = pygame.display.set_mode(
        (RENDER_W, RENDER_H), pygame.SCALED | pygame.HWSURFACE | pygame.DOUBLEBUF)

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
FONT_ROUND = pygame.font.SysFont("Arial", 22, bold=True)
FONT_HEALTH_LABEL = pygame.font.SysFont("Arial", 12, bold=True)
FONT_ZONE_LABEL = pygame.font.SysFont("Arial", 14)
FONT_METER_TITLE = pygame.font.SysFont("Arial", 15, bold=True)
FONT_METER_VALUE = pygame.font.SysFont("Arial", 14)
FONT_CARD_HEADER = pygame.font.SysFont("Arial", 16, bold=True)
FONT_CARD_TITLE = pygame.font.SysFont("Arial", 17, bold=True)
FONT_CARD_TITLE_SMALL = pygame.font.SysFont("Arial", 14, bold=True)
FONT_CHOICE_NAME = pygame.font.SysFont("Arial", 15, bold=True)
FONT_BADGE = pygame.font.SysFont("Arial", 12)
FONT_BUTTON = pygame.font.SysFont("Arial", 14, bold=True)
FONT_HUD_NAME = pygame.font.SysFont("Arial", 16, bold=True)
FONT_HUD_BUDGET = pygame.font.SysFont("Arial", 14)
FONT_HUD_WARNING = pygame.font.SysFont("Arial", 12, bold=True)
FONT_TURN_INDICATOR = pygame.font.SysFont("Arial", 42, bold=True)
FONT_END_TITLE = pygame.font.SysFont("Arial", 44, bold=True)
FONT_END_SUBTITLE = pygame.font.SysFont("Arial", 20)
FONT_END_BANNER = pygame.font.SysFont("Arial", 32, bold=True)
FONT_END_BANNER_SUB = pygame.font.SysFont("Arial", 16)
FONT_END_CARD_TITLE = pygame.font.SysFont("Arial", 24, bold=True)
FONT_END_CARD_BODY = pygame.font.SysFont("Arial", 18)
FONT_END_CARD_SMALL = pygame.font.SysFont("Arial", 16)
FONT_END_BUTTON = pygame.font.SysFont("Arial", 18, bold=True)
FONT_BANKRUPT_END = pygame.font.SysFont("Arial", 52, bold=True)
FONT_BANKRUPTCY_TITLE = pygame.font.SysFont("Arial", 64, bold=True)
FONT_BANKRUPTCY_LINE = pygame.font.SysFont("Arial", 24)
FONT_BANKRUPTCY_BODY = pygame.font.SysFont("Arial", 18)
FONT_BANKRUPTCY_HINT = pygame.font.SysFont("Arial", 16)


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
ECO_COSTS = {
    "Build a Metro Line": 8500,
    "Add More Highways": 3000,
    "Install Bike Lanes": 4200,
    "Expand Airport": 2500,
    "Downtown Commute Plan": 5000,
    "Regional Expansion": 2000,
    "Build Solar Farm": 12000,
    "Build Coal Plant": 1800,
    "Wind Turbines": 9500,
    "Natural Gas Plant": 2200,
    "Nuclear Power": 15000,
    "Geothermal Plant": 11000,
    "Recycling Program": 3500,
    "Open Landfill": 1200,
    "Composting Initiative": 2800,
    "Waste to Energy Plant": 7000,
    "Zero Waste Policy": 6500,
    "Plant Urban Forest": 5500,
    "Build Shopping Mall": 1500,
    "Community Solar Garden": 8000,
    "Green Rooftop Program": 6000,
    "Urban Farm Network": 4500,
}
QUICK_COSTS = {
    "Build a Metro Line": 1200,
    "Add More Highways": 800,
    "Install Bike Lanes": 600,
    "Expand Airport": 700,
    "Downtown Commute Plan": 900,
    "Regional Expansion": 500,
    "Build Solar Farm": 1500,
    "Build Coal Plant": 600,
    "Wind Turbines": 1200,
    "Natural Gas Plant": 700,
    "Nuclear Power": 2000,
    "Geothermal Plant": 1800,
    "Recycling Program": 500,
    "Open Landfill": 300,
    "Composting Initiative": 400,
    "Waste to Energy Plant": 900,
    "Zero Waste Policy": 1100,
    "Plant Urban Forest": 800,
    "Build Shopping Mall": 400,
    "Community Solar Garden": 1000,
    "Green Rooftop Program": 900,
    "Urban Farm Network": 700,
}

HUD_RECT = pygame.Rect(0, 0, BASE_W, 90)
CITY_PANEL_RECT = pygame.Rect(0, 90, 900, 630)
RIGHT_PANEL_RECT = pygame.Rect(910, 90, 370, 630)
METER_CONTAINER_RECT = pygame.Rect(910, 95, 370, 320)
CARD_PANEL_RECT = pygame.Rect(918, 415, 354, 300)
TITLE_PARTICLE_RECT = pygame.Rect(100, 180, BASE_W - 200, 440)
END_PARTICLE_RECT = pygame.Rect(100, 60, BASE_W - 200, 420)
CITY_ZONE_LABEL_Y = 698
CITY_DASH_LINE_Y = 682


def clamp(value, low, high):
    return max(low, min(high, value))


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(color_a, color_b, t):
    return tuple(int(lerp(color_a[i], color_b[i], t)) for i in range(3))


def format_budget(amount):
    return f"${amount:,}"


def budget_color(amount):
    if amount < 5000:
        return (239, 68, 68)
    if amount <= 15000:
        return (251, 191, 36)
    return (34, 197, 94)


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
        pygame.draw.rect(overlay, color, overlay.get_rect(),
                         width, border_radius=border_radius)
        surface.blit(overlay, rect.topleft)
        return
    pygame.draw.rect(surface, color, rect, width, border_radius=border_radius)


def draw_alpha_line(surface, color, start_pos, end_pos, width=1):
    if len(color) == 4:
        min_x = min(start_pos[0], end_pos[0]) - width
        min_y = min(start_pos[1], end_pos[1]) - width
        max_x = max(start_pos[0], end_pos[0]) + width
        max_y = max(start_pos[1], end_pos[1]) + width
        overlay = pygame.Surface(
            (max_x - min_x + 2, max_y - min_y + 2), pygame.SRCALPHA)
        pygame.draw.line(
            overlay,
            color,
            (start_pos[0] - min_x, start_pos[1] - min_y),
            (end_pos[0] - min_x, end_pos[1] - min_y),
            width,
        )
        surface.blit(overlay, (min_x, min_y))
        return
    pygame.draw.line(surface, color, start_pos, end_pos, width)


def draw_shadowed_text(surface, font, text, color, pos, center=False, shadow_offset=2):
    shadow = font.render(text, True, (0, 0, 0))
    text_surface = font.render(text, True, color)
    shadow_rect = shadow.get_rect(
        center=pos) if center else shadow.get_rect(topleft=pos)
    text_rect = text_surface.get_rect(
        center=pos) if center else text_surface.get_rect(topleft=pos)
    shadow_rect.x += shadow_offset
    shadow_rect.y += shadow_offset
    surface.blit(shadow, shadow_rect)
    surface.blit(text_surface, text_rect)


def draw_panel(surface, rect, fill_color, border_color=(255, 255, 255, 34), radius=16, shadow=True, border_width=1):
    if shadow:
        pygame.draw.rect(surface, SHADOW, rect.move(
            4, 5), border_radius=radius)
    pygame.draw.rect(surface, fill_color, rect, border_radius=radius)
    draw_alpha_outline(surface, rect, border_color,
                       width=border_width, border_radius=radius)


def draw_gradient_rect(surface, rect, start_color, end_color, border_radius=0, vertical=True):
    gradient = pygame.Surface(rect.size, pygame.SRCALPHA)
    span = max(1, rect.height - 1 if vertical else rect.width - 1)
    if vertical:
        for y in range(rect.height):
            t = y / span
            color = lerp_color(start_color, end_color, t)
            pygame.draw.line(gradient, color, (0, y), (rect.width, y))
    else:
        for x in range(rect.width):
            t = x / span
            color = lerp_color(start_color, end_color, t)
            pygame.draw.line(gradient, color, (x, 0), (x, rect.height))

    if border_radius > 0:
        mask = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255),
                         mask.get_rect(), border_radius=border_radius)
        gradient.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    surface.blit(gradient, rect.topleft)


def draw_symbol(surface, symbol, rect, color):
    if symbol == "transport":
        points = [(rect.centerx, rect.top), (rect.left,
                                             rect.bottom), (rect.right, rect.bottom)]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.line(surface, BG_COLOR, (rect.centerx,
                         rect.top + 4), (rect.centerx, rect.bottom - 4), 2)
    elif symbol == "energy":
        pygame.draw.circle(surface, color, rect.center, rect.width // 2 - 2, 3)
        pygame.draw.circle(surface, color, rect.center,
                           max(3, rect.width // 5))
    elif symbol == "waste":
        diamond = [(rect.centerx, rect.top), (rect.right, rect.centery),
                   (rect.centerx, rect.bottom), (rect.left, rect.centery)]
        pygame.draw.polygon(surface, color, diamond, 3)
        inner = rect.inflate(-10, -10)
        pygame.draw.rect(surface, color, inner, 2, border_radius=4)
    elif symbol in ("green", "leaf"):
        leaf_rect = rect.inflate(-4, -2)
        pygame.draw.ellipse(surface, color, leaf_rect)
        pygame.draw.line(surface, WHITE, (leaf_rect.left + 4,
                         leaf_rect.bottom - 4), (leaf_rect.right - 4, leaf_rect.top + 4), 2)
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
            sample = int(amplitude * math.sin(2 *
                         math.pi * frequency * t) * envelope)
            buffer.append(sample)
        return pygame.mixer.Sound(buffer=buffer.tobytes())
    except pygame.error:
        return None


@dataclass
class Choice:
    name: str
    carbon: int
    health: int


@dataclass
class DecisionCard:
    zone: str
    title: str
    eco_choice: Choice
    quick_choice: Choice
    eco_cost: int
    quick_cost: int


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
        self.hovered = self.visible and self.enabled and self.rect.collidepoint(
            mouse_pos)

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
            pygame.draw.rect(glow, (*self.base_color, 70),
                             glow.get_rect(), border_radius=20)
            surface.blit(glow, glow_rect.topleft)

        pygame.draw.rect(surface, SHADOW, self.rect.move(
            0, 4), border_radius=18)
        fill = self.hover_color if self.hovered else self.base_color
        if not self.enabled:
            fill = lerp_color(fill, (90, 90, 90), 0.5)
        pygame.draw.rect(surface, fill, self.rect, border_radius=18)
        draw_alpha_outline(surface, self.rect, (255, 255,
                           255, 200), width=2, border_radius=18)

        text_center = self.rect.center
        if self.icon:
            icon_rect = pygame.Rect(
                self.rect.x + 14, self.rect.centery - 10, 20, 20)
            draw_symbol(surface, self.icon, icon_rect, WHITE)
            text_center = (self.rect.centerx + 8, self.rect.centery)
        draw_shadowed_text(surface, font, self.text,
                           self.text_color, text_center, center=True)


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
            color = random.choice(
                [(0, 255, 136), (76, 255, 173), (167, 255, 206)])
            self.emit(center[0], center[1], (vx, vy), color, random.uniform(
                0.8, 1.6), random.uniform(5, 10), kind="leaf", gravity=42)

    def spawn_smoke_burst(self, center, count=20):
        for _ in range(count):
            vx = random.uniform(-40, 40)
            vy = random.uniform(-120, -30)
            gray = random.randint(90, 150)
            self.emit(center[0], center[1], (vx, vy), (gray, gray, gray), random.uniform(
                1.0, 1.8), random.uniform(8, 16), kind="smoke", gravity=-8)

    def spawn_title_carbon(self, area_rect, count=2):
        for _ in range(count):
            x = random.uniform(area_rect.left, area_rect.right)
            y = area_rect.bottom + random.uniform(0, 40)
            self.emit(x, y, (random.uniform(-8, 8), random.uniform(-55, -25)), (140,
                      220, 180), random.uniform(1.8, 2.8), random.uniform(3, 7), kind="circle")

    def spawn_celebration(self, area_rect, count=16):
        for _ in range(count):
            x = random.uniform(area_rect.left, area_rect.right)
            y = area_rect.top + random.uniform(0, area_rect.height * 0.45)
            color = random.choice(
                [GREEN, YELLOW, (110, 210, 255), WHITE, (255, 116, 116)])
            self.emit(x, y, (random.uniform(-70, 70), random.uniform(-20, 140)), color,
                      random.uniform(1.0, 2.0), random.uniform(2, 5), kind="spark", gravity=42)

    def spawn_end_smoke(self, area_rect, count=10):
        for _ in range(count):
            x = random.uniform(area_rect.left, area_rect.right)
            y = area_rect.top + random.uniform(0, area_rect.height)
            color = random.choice(
                [(255, 110, 110), (255, 200, 110), (180, 180, 190), (255, 90, 90)])
            self.emit(x, y, (random.uniform(-26, 26), random.uniform(-40, 40)), color,
                      random.uniform(0.9, 1.6), random.uniform(2, 5), kind="circle", gravity=14)

    def spawn_floating_text(self, x, y, text, color):
        self.particles.append({
            "x": float(x),
            "y": float(y),
            "vx": 0.0,
            "vy": -40.0,
            "life": 3.5,
            "max_life": 3.5,
            "size": 0.0,
            "color": color,
            "kind": "text",
            "gravity": 0.0,
            "fade": True,
            "rotation": 0.0,
            "spin": 0.0,
            "text": text,
        })

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
            alpha = int(
                255 * (particle["life"] / particle["max_life"])) if particle["fade"] else 255
            size = max(1, int(particle["size"]))
            particle_surface = pygame.Surface(
                (size * 4, size * 4), pygame.SRCALPHA)
            color = (*particle["color"], alpha)
            center = (particle_surface.get_width() // 2,
                      particle_surface.get_height() // 2)

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
                particle_surface = pygame.transform.rotate(
                    particle_surface, math.degrees(particle["rotation"]))
            elif particle["kind"] == "spark":
                pygame.draw.circle(particle_surface, color, center, size)
                pygame.draw.line(
                    particle_surface, color, (center[0] - size, center[1]), (center[0] + size, center[1]), 1)
                pygame.draw.line(
                    particle_surface, color, (center[0], center[1] - size), (center[0], center[1] + size), 1)

            if particle["kind"] == "text":
                font_surface = FONT_HEADING.render(
                    particle["text"], True, particle["color"])
                font_surface.set_alpha(alpha)
                surface.blit(
                    font_surface, (int(particle["x"] + ox), int(particle["y"] + oy)))
                continue

            else:
                pygame.draw.circle(particle_surface, color, center, size)

            draw_x = int(particle["x"] + ox - particle_surface.get_width() / 2)
            draw_y = int(particle["y"] + oy -
                         particle_surface.get_height() / 2)
            surface.blit(particle_surface, (draw_x, draw_y))


class CityRenderer:
    def __init__(self):
        self.area = CITY_PANEL_RECT.copy()
        self.animation_time = 0.0
        road_top = self.area.height - 94
        base_y = road_top - 8

        def make_cluster(start_x, specs):
            buildings = []
            for x_offset, width, height, style in specs:
                rect = pygame.Rect(start_x + x_offset,
                                   base_y - height, width, height)
                buildings.append({"rect": rect, "style": style})
            return buildings

        self.zone_layout = {
            "Transport": {
                "buildings": make_cluster(32, [(0, 34, 238, "skyscraper"), (42, 82, 156, "office"), (96, 46, 88, "shop")]),
                "label_pos": (112, CITY_ZONE_LABEL_Y - self.area.y),
                "accent": "transport",
            },
            "Energy": {
                "buildings": make_cluster(232, [(0, 38, 216, "skyscraper"), (48, 88, 148, "office"), (100, 44, 98, "shop")]),
                "label_pos": (312, CITY_ZONE_LABEL_Y - self.area.y),
                "accent": "energy",
            },
            "Waste": {
                "buildings": make_cluster(432, [(0, 76, 122, "office"), (58, 36, 194, "skyscraper"), (100, 48, 82, "shop")]),
                "label_pos": (512, CITY_ZONE_LABEL_Y - self.area.y),
                "accent": "waste",
            },
            "Green Space": {
                "buildings": make_cluster(632, [(0, 36, 176, "skyscraper"), (44, 80, 132, "office"), (96, 42, 86, "shop")]),
                "label_pos": (712, CITY_ZONE_LABEL_Y - self.area.y),
                "accent": "green",
            },
        }

        self.zone_centers = {
            zone: (
                self.area.x +
                sum(entry["rect"].centerx for entry in data["buildings"]
                    ) / len(data["buildings"]),
                self.area.y + base_y - 60,
            )
            for zone, data in self.zone_layout.items()
        }
        self.zone_visuals = {zone: {"score": 0.0, "target": 0.0}
                             for zone in self.zone_layout}

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
        self.animation_time += dt
        for zone in self.zone_visuals:
            current = self.zone_visuals[zone]["score"]
            target = self.zone_visuals[zone]["target"]
            self.zone_visuals[zone]["score"] = lerp(
                current, target, min(1.0, dt * 4.5))

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

        window_color = lerp_color(
            (252, 236, 120), (255, 160, 92), pollution * 0.85)
        step_x = 14 if style == "skyscraper" else 18
        step_y = 18 if style == "skyscraper" else 20
        margin_x = 7
        margin_y = 10
        for wx in range(rect.x + margin_x, rect.right - 8, step_x):
            for wy in range(rect.y + margin_y, rect.bottom - 16, step_y):
                window = pygame.Rect(wx, wy, 6 if style == "shop" else 7, 9)
                pygame.draw.rect(surface, window_color,
                                 window, border_radius=2)

        if style == "skyscraper":
            pygame.draw.line(surface, (220, 220, 230), (rect.centerx,
                             rect.y), (rect.centerx, rect.y - 12), 2)
            pygame.draw.circle(surface, (220, 220, 230),
                               (rect.centerx, rect.y - 12), 2)
        elif style == "shop":
            awning = pygame.Rect(rect.x + 4, rect.y +
                                 rect.height // 2 - 10, rect.width - 8, 12)
            pygame.draw.rect(surface, lerp_color(
                base_color, WHITE, 0.24), awning, border_radius=4)

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

        star_color = lerp_color(
            (255, 255, 255), (255, 208, 178), pollution * 0.35)
        if pollution < 0.92:
            for x, y, size in self.stars:
                pygame.draw.circle(surface, star_color,
                                   (area.x + x, area.y + y), size)

        haze = pygame.Surface(area.size, pygame.SRCALPHA)
        pygame.draw.rect(haze, (220, 70, 50, int(
            70 * pollution)), haze.get_rect())
        surface.blit(haze, area.topleft)

        hill_back = []
        hill_front = []
        for step in range(0, area.width + 26, 26):
            hill_back.append((area.x + step, area.bottom - 180 -
                             math.sin(step * 0.012) * 24 - math.cos(step * 0.023) * 16))
            hill_front.append((area.x + step, area.bottom - 148 -
                              math.sin(step * 0.017 + 1.2) * 32 - math.cos(step * 0.03) * 10))
        pygame.draw.polygon(surface, (38, 40, 63), [
                            (area.left, area.bottom)] + hill_back + [(area.right, area.bottom)])
        pygame.draw.polygon(surface, (28, 30, 50), [
                            (area.left, area.bottom)] + hill_front + [(area.right, area.bottom)])

        sun_color = lerp_color((255, 223, 154), (255, 136, 92), pollution)
        pygame.draw.circle(surface, sun_color,
                           (area.right - 115, area.top + 96), 38)

        road_rect = pygame.Rect(area.left, area.bottom - 76, area.width, 76)
        pavement_rect = pygame.Rect(
            area.left, road_rect.y - 18, area.width, 18)
        pygame.draw.rect(surface, (56, 60, 74), pavement_rect)
        pygame.draw.rect(surface, (33, 36, 49), road_rect)
        pygame.draw.line(surface, (120, 128, 145), (area.left,
                         pavement_rect.y), (area.right, pavement_rect.y), 2)
        pygame.draw.line(surface, (76, 82, 98), (area.left,
                         road_rect.y + 2), (area.right, road_rect.y + 2), 2)

        dash_y = area.y + (CITY_DASH_LINE_Y - CITY_PANEL_RECT.y)
        for dash_x in range(area.left, area.left + 900, 40):
            pygame.draw.rect(surface, (51, 65, 85),
                             (dash_x, dash_y, 20, 4), border_radius=2)

        for zone, data in self.zone_layout.items():
            zone_color = self._zone_color(zone)
            for building in data["buildings"]:
                draw_rect = building["rect"].move(area.x, area.y)
                self._draw_building(surface, draw_rect,
                                    building["style"], zone_color, pollution)

            if data["accent"] == "transport":
                track_y = pavement_rect.y - 12
                pygame.draw.line(
                    surface, (18, 18, 24), (area.x + 24, track_y), (area.x + 158, track_y), 6)
                pygame.draw.line(surface, (120, 220, 255), (area.x +
                                 40, track_y - 6), (area.x + 142, track_y - 6), 3)
            elif data["accent"] == "energy":
                for base_x in (area.x + 262, area.x + 320):
                    stem_bottom = pavement_rect.y - 10
                    pygame.draw.line(
                        surface, (220, 220, 230), (base_x, stem_bottom), (base_x, stem_bottom - 44), 3)
                    center = (base_x, stem_bottom - 44)
                    for angle in (0, 120, 240):
                        radians = math.radians(
                            angle + self.animation_time * 70.0)
                        tip = (center[0] + math.cos(radians) * 14,
                               center[1] + math.sin(radians) * 14)
                        pygame.draw.line(
                            surface, (230, 230, 240), center, tip, 2)
                    pygame.draw.circle(surface, (230, 230, 240), center, 3)
            elif data["accent"] == "waste":
                for bx in (area.x + 428, area.x + 456, area.x + 484):
                    bin_rect = pygame.Rect(bx, pavement_rect.y - 26, 18, 24)
                    pygame.draw.rect(surface, zone_color,
                                     bin_rect, border_radius=4)
                    pygame.draw.rect(surface, (15, 15, 20),
                                     bin_rect, 2, border_radius=4)
            elif data["accent"] == "green":
                for tx in (area.x + 566, area.x + 620):
                    trunk = pygame.Rect(tx, pavement_rect.y - 28, 6, 22)
                    pygame.draw.rect(surface, (104, 70, 38),
                                     trunk, border_radius=3)
                    pygame.draw.circle(surface, zone_color,
                                       (tx + 3, pavement_rect.y - 34), 16)

            label_pos = (area.x + data["label_pos"]
                         [0], area.y + data["label_pos"][1])
            draw_shadowed_text(surface, FONT_ZONE_LABEL, zone,
                               (148, 163, 184), label_pos, center=True)

        for tree_x in (area.left + 38, area.left + 186, area.left + 340, area.left + 502, area.left + 640):
            trunk = pygame.Rect(tree_x, pavement_rect.y - 24, 6, 18)
            pygame.draw.rect(surface, (98, 67, 41), trunk, border_radius=3)
            pygame.draw.circle(surface, (58, 165, 96),
                               (tree_x + 3, pavement_rect.y - 28), 12)

        for lamp_x in (area.left + 112, area.left + 286, area.left + 450, area.left + 606):
            pygame.draw.line(surface, (188, 194, 205), (lamp_x,
                             pavement_rect.y), (lamp_x, pavement_rect.y - 30), 3)
            pygame.draw.circle(surface, (255, 237, 166),
                               (lamp_x, pavement_rect.y - 34), 5)

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
        self.display_value = lerp(
            self.display_value, self.value, min(1.0, dt * 4.8))
        self.pulse_time += dt

    def draw(self, surface, warning_active=False):
        frame = self.rect
        pygame.draw.rect(surface, PANEL_COLOR, frame, border_radius=16)
        draw_alpha_outline(surface, frame, (255, 255, 255,
                           22), width=1, border_radius=16)
        clip_before = push_clip(surface, frame)

        draw_shadowed_text(surface, FONT_METER_TITLE, "CARBON LEVEL",
                           (170, 170, 204), (1095, 108), center=True)

        value_pill = pygame.Rect(1035, 120, 120, 24)
        pygame.draw.rect(surface, (26, 26, 62), value_pill, border_radius=12)
        draw_alpha_outline(surface, value_pill, (255, 215, 0),
                           width=2, border_radius=12)
        draw_shadowed_text(surface, FONT_METER_VALUE,
                           f"{int(round(self.display_value))}/100", (255, 215, 0), value_pill.center, center=True)

        meter_outer_rect = pygame.Rect(1010, 148, 60, 220)
        meter_inner_rect = pygame.Rect(1012, 150, 56, 216)
        pygame.draw.rect(surface, (13, 27, 42),
                         meter_outer_rect, border_radius=10)
        draw_alpha_outline(surface, meter_outer_rect,
                           (51, 68, 102), width=2, border_radius=10)

        fill_height = int((self.display_value / 100.0) * 216)
        fill_top = 366 - fill_height
        surface.set_clip(meter_inner_rect)
        for row_index in range(fill_height):
            t = row_index / 216
            r = int(255 * t)
            g = int(255 * (1 - t))
            b = 50
            y = 366 - row_index
            if fill_top <= y <= 366:
                pygame.draw.line(
                    surface, (r, g, b), (meter_inner_rect.x, y), (meter_inner_rect.right - 1, y))
        surface.set_clip(frame)

        meter_top = 150
        meter_bottom = 366
        meter_height = 216
        for val in (0, 25, 50, 75, 100):
            label_y = meter_bottom - int((val / 100) * meter_height)
            pygame.draw.line(surface, (68, 85, 102),
                             (1072, label_y), (1078, label_y), 1)
            label_surface = FONT_TINY.render(str(val), True, (136, 153, 170))
            surface.blit(label_surface, (1082, label_y - 7))

        if self.value >= 80:
            pulse = (math.sin(self.pulse_time * 10) + 1) * 0.5
            alert = pygame.Surface(frame.size, pygame.SRCALPHA)
            pygame.draw.rect(alert, (255, 40, 40, int(
                40 + pulse * 80)), alert.get_rect(), 4, border_radius=16)
            surface.blit(alert, frame.topleft)
            draw_shadowed_text(surface, FONT_SMALL_BOLD, "CRITICAL",
                               RED if warning_active else YELLOW, (frame.centerx, frame.bottom - 24), center=True)

        surface.set_clip(clip_before)


class HUD:
    def __init__(self):
        self.rect = HUD_RECT.copy()
        self.left_pill = pygame.Rect(10, 12, 210, 48)
        self.right_pill = pygame.Rect(1060, 12, 210, 48)
        self.health_bar = pygame.Rect(440, 53, 400, 14)

    def draw(self, surface, players, current_player, round_number, city_health, flash_bankrupt_index=None, flash_active=False, blink_on=True):
        overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(overlay, (10, 16, 30, 210), overlay.get_rect())
        surface.blit(overlay, self.rect.topleft)
        pygame.draw.line(surface, (65, 82, 118), (0,
                         self.rect.bottom - 1), (BASE_W, self.rect.bottom - 1), 2)
        clip_before = push_clip(surface, self.rect)

        pill_specs = []
        for idx, player in enumerate(players):
            budget_text = format_budget(player["budget"])
            text_width = max(FONT_HUD_NAME.size(player["name"])[
                             0], FONT_HUD_BUDGET.size(budget_text)[0])
            width = max(210, text_width + 70)
            x = 10 if idx == 0 else BASE_W - 10 - width
            pill_specs.append(pygame.Rect(x, 12, width, 48))

        self.left_pill, self.right_pill = pill_specs

        for idx, pill in enumerate(pill_specs):
            player = players[idx]
            is_current = idx == current_player
            flash_this_pill = idx == flash_bankrupt_index and flash_active
            active_color = GREEN if idx == 0 else (167, 139, 250)
            inactive_border = (51, 65, 85)
            inactive_dot = (75, 85, 99)
            border = RED if flash_this_pill else active_color if is_current else inactive_border
            border_width = 2 if flash_this_pill else 3 if is_current else 1
            fill_color = (70, 12, 18) if flash_this_pill else PANEL_COLOR
            if is_current and not flash_this_pill:
                glow = pygame.Surface(
                    (pill.width + 10, pill.height + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow, (*active_color, 60),
                                 glow.get_rect(), border_radius=26)
                surface.blit(glow, (pill.x - 5, pill.y - 5))
            elif flash_this_pill:
                glow = pygame.Surface(
                    (pill.width + 16, pill.height + 16), pygame.SRCALPHA)
                pygame.draw.rect(glow, (239, 68, 68, 90),
                                 glow.get_rect(), border_radius=28)
                surface.blit(glow, (pill.x - 8, pill.y - 8))
            pygame.draw.rect(surface, fill_color, pill, border_radius=22)
            draw_alpha_outline(surface, pill, border,
                               width=border_width, border_radius=22)
            dot_color = RED if flash_this_pill else active_color if is_current else inactive_dot
            pygame.draw.circle(surface, dot_color,
                               (pill.x + 18, pill.y + 18), 6)
            draw_shadowed_text(surface, FONT_HUD_NAME,
                               player["name"], WHITE, (pill.x + 32, pill.y + 6))
            draw_shadowed_text(surface, FONT_HUD_BUDGET, format_budget(
                player["budget"]), budget_color(player["budget"]), (pill.x + 32, pill.y + 26))

            warning_text = None
            warning_color = None
            if player["budget"] < 5000:
                warning_text = "⚠ Critical Funds!"
                warning_color = (239, 68, 68)
            elif player["budget"] < 15000:
                warning_text = "⚠ Low Funds"
                warning_color = (251, 191, 36)
            if warning_text and blink_on:
                draw_shadowed_text(surface, FONT_HUD_WARNING, warning_text, warning_color, (
                    pill.centerx, pill.bottom + 2), center=True, shadow_offset=1)

        round_surface = FONT_ROUND.render(
            f"Round {round_number} / 15", True, WHITE)
        round_rect = round_surface.get_rect(center=(640, 18))
        shadow = FONT_ROUND.render(
            f"Round {round_number} / 15", True, (0, 0, 0))
        surface.blit(shadow, round_rect.move(2, 2))
        surface.blit(round_surface, round_rect)

        health_label = FONT_HEALTH_LABEL.render(
            "CITY HEALTH", True, LIGHT_GRAY)
        label_rect = health_label.get_rect(center=(640, 44))
        label_shadow = FONT_HEALTH_LABEL.render("CITY HEALTH", True, (0, 0, 0))
        surface.blit(label_shadow, label_rect.move(2, 2))
        surface.blit(health_label, label_rect)
        pygame.draw.rect(surface, PANEL_DARK, self.health_bar, border_radius=8)
        draw_alpha_outline(surface, self.health_bar,
                           (255, 255, 255, 180), width=2, border_radius=8)
        fill_width = int((clamp(city_health, 0, 100) / 100.0)
                         * (self.health_bar.width - 4))
        fill_rect = pygame.Rect(
            self.health_bar.x + 2, self.health_bar.y + 2, fill_width, self.health_bar.height - 4)
        health_color = GREEN if city_health >= 60 else YELLOW if city_health >= 30 else RED
        pygame.draw.rect(surface, health_color, fill_rect, border_radius=6)
        draw_shadowed_text(surface, FONT_SMALL, str(int(city_health)), health_color,
                           (self.health_bar.right + 28, self.health_bar.centery), center=True)
        surface.set_clip(clip_before)


class CardSystem:
    def __init__(self):
        self.card_rect = CARD_PANEL_RECT.copy()
        self.eco_button = Button(
            (0, 0, 0, 0), "ECO CHOICE", (0, 180, 96), (0, 220, 120), icon="leaf")
        self.quick_button = Button(
            (0, 0, 0, 0), "QUICK CHOICE", (204, 56, 56), (244, 76, 76), icon="quick")
        self.cards = self._build_cards()
        self.current_card = None
        self.current_index = -1
        self.slide_progress = 1.0
        self.slide_duration = 0.45
        self.show_card(random.randint(0, len(self.cards) - 1))

    def _build_cards(self):
        def make_choice(name, carbon, health):
            return Choice(name, carbon, health)

        def lookup_cost(cost_table, primary_name, fallback_name):
            if fallback_name in cost_table:
                return cost_table[fallback_name]
            return cost_table.get(primary_name, 1000)

        def make_card(zone, title, eco_name, eco_carbon, eco_health, quick_name, quick_carbon, quick_health):
            return DecisionCard(
                zone,
                title,
                make_choice(eco_name, eco_carbon, eco_health),
                make_choice(quick_name, quick_carbon, quick_health),
                lookup_cost(ECO_COSTS, eco_name, title),
                lookup_cost(QUICK_COSTS, quick_name, title),
            )

        return [
            make_card("Transport", "Downtown Commute Plan",
                      "Build a Metro Line", -8, 5, "Add More Highways", 10, -3),
            make_card("Transport", "Neighborhood Streets",
                      "Install Bike Lanes", -5, 3, "Add More Highways", 10, -3),
            make_card("Transport", "Regional Expansion",
                      "Build a Metro Line", -8, 5, "Expand Airport", 12, -2),
            make_card("Energy", "Power Grid Upgrade",
                      "Build Solar Farm", -10, 8, "Build Coal Plant", 15, -10),
            make_card("Energy", "Future Energy Mix",
                      "Wind Turbines", -8, 6, "Natural Gas Plant", 8, -4),
            make_card("Energy", "Industrial Demand Spike",
                      "Build Solar Farm", -10, 8, "Natural Gas Plant", 8, -4),
            make_card("Energy", "Regional Reliability Vote",
                      "Wind Turbines", -8, 6, "Build Coal Plant", 15, -10),
            make_card("Waste", "Community Waste Strategy",
                      "Recycling Program", -4, 4, "Open Landfill", 6, -5),
            make_card("Waste", "Food Waste Response",
                      "Composting Initiative", -3, 3, "Open Landfill", 6, -5),
            make_card("Waste", "School Sustainability Drive",
                      "Recycling Program", -4, 4, "Open Landfill", 6, -5),
            make_card("Green Space", "Vacant Lot Decision",
                      "Plant Urban Forest", -7, 7, "Build Shopping Mall", 9, -6),
            make_card("Green Space", "Riverfront Redevelopment",
                      "Plant Urban Forest", -7, 7, "Build Shopping Mall", 9, -6),
            make_card("Transport", "Tourism Growth Debate",
                      "Install Bike Lanes", -5, 3, "Expand Airport", 12, -2),
            make_card("Waste", "Industrial Overflow",
                      "Waste to Energy Plant", -6, 4, "Open Landfill", 6, -5),
            make_card("Waste", "City Cleanup Campaign",
                      "Zero Waste Policy", -8, 6, "Open Landfill", 6, -5),
            make_card("Waste", "School Recycling Drive",
                      "Composting Initiative", -3, 3, "Open Landfill", 6, -5),
            make_card("Green Space", "Rooftop Revolution",
                      "Green Rooftop Program", -5, 6, "Build Shopping Mall", 9, -6),
            make_card("Green Space", "Community Garden Vote",
                      "Urban Farm Network", -4, 5, "Build Shopping Mall", 9, -6),
            make_card("Green Space", "Solar or Trees Debate",
                      "Community Solar Garden", -7, 5, "Build Shopping Mall", 9, -6),
            make_card("Energy", "Clean Energy Summit",
                      "Geothermal Plant", -9, 7, "Build Coal Plant", 15, -10),
            make_card("Energy", "City Power Shortage",
                      "Nuclear Power", -12, 6, "Build Coal Plant", 15, -10),]

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
        self.slide_progress = min(
            1.0, self.slide_progress + dt / self.slide_duration)
        frame = self.current_rect()
        self.eco_button.set_rect(
            (926 + (frame.x - self.card_rect.x), 666, 164, 40))
        self.quick_button.set_rect(
            (1098 + (frame.x - self.card_rect.x), 666, 164, 40))
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
        text_surface = FONT_BADGE.render(text, True, color)
        badge_rect = pygame.Rect(x, y, text_surface.get_width() + 16, 20)
        pygame.draw.rect(surface, PANEL_DARK, badge_rect, border_radius=10)
        draw_shadowed_text(surface, FONT_BADGE, text, color,
                           badge_rect.center, center=True)
        return badge_rect

    def draw(self, surface, current_budget):
        if not self.current_card:
            return

        frame = self.current_rect()
        pygame.draw.rect(surface, (17, 24, 39), frame, border_radius=12)
        draw_alpha_outline(surface, frame, (30, 41, 59),
                           width=1, border_radius=12)
        clip_before = push_clip(surface, frame)
        zone_color = ZONE_COLORS.get(self.current_card.zone, WHITE)

        header_rect = pygame.Rect(frame.x, frame.y, 354, 40)
        pygame.draw.rect(surface, zone_color, header_rect,
                         border_top_left_radius=12, border_top_right_radius=12)
        icon_rect = pygame.Rect(frame.x + 12, frame.y + 10, 20, 20)
        draw_symbol(surface, zone_icon(
            self.current_card.zone), icon_rect, PANEL_DARK)
        zone_label_rect = FONT_CARD_HEADER.render(self.current_card.zone.upper(
        ), True, WHITE).get_rect(midleft=(frame.x + 40, frame.y + 20))
        draw_shadowed_text(surface, FONT_CARD_HEADER, self.current_card.zone.upper(
        ), WHITE, zone_label_rect.topleft)

        title_font = FONT_CARD_TITLE if FONT_CARD_TITLE.size(self.current_card.title)[
            0] <= 330 else FONT_CARD_TITLE_SMALL
        draw_shadowed_text(surface, title_font, self.current_card.title,
                           WHITE, (frame.x + 10, frame.y + 50))
        eco_cost_text = FONT_BADGE.render(
            f"ECO CHOICE: {format_budget(self.current_card.eco_cost)}", True, (74, 222, 128))
        quick_cost_text = FONT_BADGE.render(
            f"QUICK CHOICE: {format_budget(self.current_card.quick_cost)}", True, (251, 146, 60))
        surface.blit(eco_cost_text, (frame.x + 10, frame.y + 74))
        surface.blit(quick_cost_text, (frame.right - 10 -
                     quick_cost_text.get_width(), frame.y + 74))

        eco_rect = pygame.Rect(frame.x + 8, frame.y + 99, 338, 68)
        quick_rect = pygame.Rect(frame.x + 8, frame.y + 175, 338, 68)
        self.draw_choice_panel(
            surface, eco_rect, self.current_card.eco_choice, (34, 197, 94))
        self.draw_choice_panel(surface, quick_rect,
                               self.current_card.quick_choice, (239, 68, 68))

        self.draw_action_buttons(surface, frame)
        surface.set_clip(clip_before)

    def draw_choice_panel(self, surface, rect, choice, accent_color):
        pygame.draw.rect(surface, (15, 23, 42), rect, border_radius=8)
        pygame.draw.rect(surface, accent_color, (rect.x, rect.y, 4, rect.height),
                         border_top_left_radius=8, border_bottom_left_radius=8)
        draw_shadowed_text(surface, FONT_CHOICE_NAME,
                           choice.name, WHITE, (rect.x + 12, rect.y + 6))

        badge_y = rect.y + 30
        x = rect.x + 12
        badge_specs = [
            (f"Carbon {choice.carbon:+d}", (22, 101, 52), (34, 197, 94)),
            (f"Health {choice.health:+d}", (30, 58, 95), (96, 165, 250)),
        ]
        for text, bg_color, text_color in badge_specs:
            badge = self.draw_stat_badge(
                surface, x, badge_y, text, bg_color, text_color)
            x = badge.right + 6

    def draw_stat_badge(self, surface, x, y, text, bg_color, text_color):
        text_surface = FONT_BADGE.render(text, True, text_color)
        badge_rect = pygame.Rect(x, y, text_surface.get_width() + 16, 20)
        pygame.draw.rect(surface, bg_color, badge_rect, border_radius=10)
        draw_shadowed_text(surface, FONT_BADGE, text,
                           text_color, badge_rect.center, center=True)
        return badge_rect

    def draw_action_buttons(self, surface, frame):
        eco_button_rect = pygame.Rect(frame.x + 8, frame.y + 251, 164, 40)
        quick_button_rect = pygame.Rect(frame.x + 180, frame.y + 251, 164, 40)
        self.eco_button.set_rect(eco_button_rect)
        self.quick_button.set_rect(quick_button_rect)
        pygame.draw.rect(surface, (22, 163, 74),
                         eco_button_rect, border_radius=20)
        pygame.draw.circle(surface, (74, 222, 128),
                           (eco_button_rect.x + 18, eco_button_rect.y + 20), 8)
        draw_shadowed_text(surface, FONT_BUTTON, "ECO CHOICE",
                           WHITE, eco_button_rect.center, center=True)

        pygame.draw.rect(surface, (185, 28, 28),
                         quick_button_rect, border_radius=20)
        lightning_rect = pygame.Rect(
            quick_button_rect.x + 10, quick_button_rect.y + 10, 16, 20)
        draw_symbol(surface, "quick", lightning_rect, WHITE)
        draw_shadowed_text(surface, FONT_BUTTON, "QUICK CHOICE",
                           WHITE, quick_button_rect.center, center=True)


class Game:
    def __init__(self):
        self.screen = SCREEN
        self.base_surface = BASE_SURFACE
        self.clock = pygame.time.Clock()
        self.last_dt = 0.0
        self.hud = HUD()
        self.city = CityRenderer()
        self.carbon_meter = CarbonMeter(METER_CONTAINER_RECT)
        self.card_system = CardSystem()
        self.particles = ParticleSystem()
        self.replay_button = Button(
            (540, 570, 180, 52), "Replay", (0, 180, 96), (0, 220, 120))
        self.quit_button = Button(
            (760, 570, 180, 52), "Quit", (204, 56, 56), (244, 76, 76))

        self.sounds = {
            "eco": generate_tone(680, 0.17, 0.30),
            "quick": generate_tone(240, 0.20, 0.34),
            "warning": generate_tone(920, 0.12, 0.26),
            "click": generate_tone(500, 0.08, 0.22),
            "funds": generate_tone(1180, 0.10, 0.26),
        }

        self.show_resolution_debug = True
        self.title_particles_timer = 0.0
        self.end_particles_timer = 0.0
        self.warning_played = False
        self.shake_time = 0.0
        self.shake_strength = 0.0
        self.shake_duration = 0.45
        self.title_float = 0.0
        self.compat_overlay_elapsed = 0.0
        self.running = True
        self.reset_game()

    def reset_game(self):
        self.state = "title"
        self.players = [
            {"name": "Player 1", "budget": 100000,
                "eco": 0, "quick": 0, "decisions": 0},
            {"name": "Player 2", "budget": 100000,
                "eco": 0, "quick": 0, "decisions": 0},
        ]
        self.player1_carbon_contribution = 0
        self.player2_carbon_contribution = 0
        self.bankrupt_player_index = None
        self.bankruptcy_timer = 0.0
        self.critical_budget_warned = [False, False]
        self.turn_indicator_timer = 0.0
        self.current_player = 0
        self.completed_rounds = 0
        self.city_health = 100
        self.carbon_level = 30
        self.carbon_meter.set_value(30)
        self.zone_scores = {zone: 0 for zone in self.city.zone_layout}
        for zone in self.zone_scores:
            self.city.set_zone_state(zone, 0)
        self.card_system.show_card()
        self.particles = ParticleSystem()
        self.warning_played = False
        self.shake_time = 0.0
        self.shake_strength = 0.0
        self.shake_duration = 0.45
        self.title_particles_timer = 0.0
        self.end_particles_timer = 0.0
        self.compat_overlay_elapsed = 0.0
        self.end_cause = None
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

    def trigger_bankruptcy(self, player_index):
        self.players[player_index]["budget"] = 0
        self.bankrupt_player_index = player_index
        self.bankruptcy_timer = 0.0
        self.end_cause = "bankruptcy"
        self.state = "bankruptcy"
        self.shake_strength = 8
        self.shake_time = 1.5
        self.shake_duration = 1.5

    def maybe_warn_low_budget(self, player_index, previous_budget):
        current_budget = self.players[player_index]["budget"]
        if current_budget < 5000 <= previous_budget and not self.critical_budget_warned[player_index]:
            self.play_sound("funds")
            self.critical_budget_warned[player_index] = True

    def apply_choice(self, choice_type):
        card = self.card_system.current_card
        choice = card.eco_choice if choice_type == "eco" else card.quick_choice
        player = self.players[self.current_player]
        choice_cost = card.eco_cost if choice_type == "eco" else card.quick_cost

        previous_budget = player["budget"]
        player["budget"] = max(0, player["budget"] - choice_cost)
        player["decisions"] += 1
        player[choice_type] += 1
        if self.current_player == 0:
            self.player1_carbon_contribution += choice.carbon
        else:
            self.player2_carbon_contribution += choice.carbon

        self.carbon_level = clamp(self.carbon_level + choice.carbon, 0, 100)
        self.city_health = clamp(self.city_health + choice.health, 0, 100)
        self.carbon_meter.set_value(self.carbon_level)

        zone_delta = 1 if choice_type == "eco" else -1
        self.zone_scores[card.zone] += zone_delta
        self.city.set_zone_state(card.zone, self.zone_scores[card.zone])
        effect_center = self.city.zone_centers[card.zone]
        if choice_type == "eco":
            self.particles.spawn_leaf_burst(effect_center, count=20)
            self.particles.spawn_floating_text(
                effect_center[0] - 40, effect_center[1] - 60,
                f"Carbon {choice.carbon:+d}", (74, 222, 128))
            self.particles.spawn_floating_text(
                effect_center[0] - 40, effect_center[1] - 30,
                f"Health {choice.health:+d}", (96, 165, 250))
        else:
            self.particles.spawn_smoke_burst(effect_center, count=22)
            self.particles.spawn_floating_text(
                effect_center[0] - 40, effect_center[1] - 60,
                f"Carbon {choice.carbon:+d}", (239, 68, 68))
            self.particles.spawn_floating_text(
                effect_center[0] - 40, effect_center[1] - 30,
                f"Health {choice.health:+d}", (239, 68, 68))
        if self.carbon_level >= 80:
            self.shake_strength = 8 if self.carbon_level < 100 else 14
            self.shake_time = 0.45
            self.shake_duration = 0.45
        elif choice_type == "quick":
            self.shake_strength = 4
            self.shake_time = 0.18
            self.shake_duration = 0.18

        self.maybe_warn_low_budget(self.current_player, previous_budget)
        if player["budget"] <= 0:
            self.trigger_bankruptcy(self.current_player)
            return

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
        self.end_cause = "rounds_complete"
        if self.carbon_level < 60:
            self.result = {"title": "Green City",
                           "subtitle": "Your city balanced growth and sustainability."}
        elif self.carbon_level < 80:
            self.result = {"title": "Recovering City",
                           "subtitle": "The city survived and has a cleaner future ahead."}
        else:
            self.result = {"title": "City in Crisis",
                           "subtitle": "You finished the rounds, but carbon remains dangerously high."}
        self.state = "end"
        self.particles = ParticleSystem()

    def _check_immediate_end(self):
        if self.carbon_level >= 100:
            self.end_cause = "collapse"
            self.result = {"title": "City Collapsed",
                           "subtitle": "Carbon overload pushed the city past the breaking point."}
            self.state = "end"
            self.particles = ParticleSystem()
            return True
        if self.city_health <= 0:
            self.end_cause = "health"
            self.result = {"title": "Health Crisis",
                           "subtitle": "The city could not withstand the environmental damage."}
            self.state = "end"
            self.particles = ParticleSystem()
            return True
        return False

    def handle_events(self):
        mouse_pos = to_base_pos(pygame.mouse.get_pos())
        for event in pygame.event.get():
            base_event_pos = to_base_pos(event.pos) if hasattr(
                event, "pos") else mouse_pos

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
                elif self.state == "bankruptcy" and event.key == pygame.K_SPACE:
                    self.play_sound("click")
                    self.state = "end"
                    self.end_particles_timer = 0.0
                    self.particles = ParticleSystem()
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

        if self.state == "end":
            self.replay_button.update(mouse_pos)
            self.quit_button.update(mouse_pos)

    def update(self, dt):
        self.title_float += dt
        self.carbon_meter.update(dt)
        self.city.update(dt)
        self.particles.update(dt)

        mouse_pos = to_base_pos(pygame.mouse.get_pos())
        if self.state == "game":
            self.card_system.update(dt, mouse_pos)
        elif self.state == "end":
            self.replay_button.update(mouse_pos)
            self.quit_button.update(mouse_pos)
        elif self.state == "bankruptcy":
            self.bankruptcy_timer += dt

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
            if self.end_cause == "rounds_complete" and self.carbon_level < 80:
                while self.end_particles_timer >= 0.12:
                    self.end_particles_timer -= 0.12
                    self.particles.spawn_celebration(
                        END_PARTICLE_RECT.move(0, -10), count=12)
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
        strength = self.shake_strength * \
            (self.shake_time / max(self.shake_duration, 0.001))
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

        self._draw_title_silhouette(
            surface, 0.18, BASE_H - 142, (24, 30, 56), 232)
        self._draw_title_silhouette(
            surface, 0.33, BASE_H - 102, (16, 22, 42), 186)
        pygame.draw.rect(surface, (20, 24, 38), (0, BASE_H - 86, BASE_W, 86))

        title_y = 160 + math.sin(self.title_float * 2.1) * 5
        draw_shadowed_text(surface, FONT_TITLE, "Carbon Quest",
                           GREEN, (BASE_W // 2, title_y), center=True)
        draw_shadowed_text(surface, FONT_HEADING, "City Builder Challenge",
                           WHITE, (BASE_W // 2, 246), center=True)
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
            bar_alpha = max(
                0, 255 - int((self.compat_overlay_elapsed / 3.0) * 255))
            if bar_alpha > 0:
                bar_rect = pygame.Rect(0, BASE_H - 36, BASE_W, 36)
                overlay = pygame.Surface(bar_rect.size, pygame.SRCALPHA)
                overlay.fill((12, 16, 26, bar_alpha))
                surface.blit(overlay, bar_rect.topleft)
                text = FONT_SMALL.render(
                    "Display not natively supported — running in 720p compatibility mode", True, WHITE)
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
        shake_offset = self.game_offset() if self.state == "game" else (0, 0)
        blink_on = int(self.title_float / 0.5) % 2 == 0
        flash_active = (
            self.state == "bankruptcy"
            and self.bankrupt_player_index is not None
            and self.bankruptcy_timer < 1.5
            and int(self.bankruptcy_timer / 0.25) % 2 == 0
        )

        right_bg = RIGHT_PANEL_RECT.copy()
        pygame.draw.rect(surface, PANEL_DARK, right_bg, border_radius=18)
        draw_alpha_outline(surface, right_bg, (255, 255,
                           255, 20), width=1, border_radius=18)

        draw_alpha_line(surface, (255, 255, 255, 30), (908, 90), (908, 720), 1)

        self.hud.draw(
            surface,
            self.players,
            self.current_player,
            self.current_round_number(),
            self.city_health,
            flash_bankrupt_index=self.bankrupt_player_index,
            flash_active=flash_active,
            blink_on=blink_on,
        )

        city_clip = push_clip(surface, CITY_PANEL_RECT)
        self.city.draw(surface, self.carbon_level, offset=shake_offset)
        self.particles.draw(surface, offset=shake_offset)
        self.draw_turn_indicator(surface)
        surface.set_clip(city_clip)

        self.carbon_meter.draw(surface, warning_active=self.carbon_level >= 80)
        self.card_system.draw(
            surface, self.players[self.current_player]["budget"])

    def draw_turn_indicator(self, surface):
        # fade out after 2.5 seconds
        if self.turn_indicator_timer > 2.5:
            return

        fade = 1.0 - ((self.turn_indicator_timer - 2.0) /
                      0.5) if self.turn_indicator_timer > 2.0 else 1.0

        center_x = CITY_PANEL_RECT.width // 2
        center_y = 200
        player_name = "Player 1" if self.current_player == 0 else "Player 2"
        player_color = GREEN if self.current_player == 0 else (167, 139, 250)
        text = f"{player_name}'s Turn"
        text_width, text_height = FONT_TURN_INDICATOR.size(text)

        pill_rect = pygame.Rect(0, 0, text_width + 40, 52)
        pill_rect.center = (center_x, center_y)
        pill_surface = pygame.Surface(pill_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(pill_surface, (0, 0, 0),
                         pill_surface.get_rect(), border_radius=26)
        pill_surface.set_alpha(int(120 * fade))
        surface.blit(pill_surface, pill_rect.topleft)

        pulse = math.sin(pygame.time.get_ticks() / 400.0)
        alpha_value = int((180 + ((pulse + 1.0) * 0.5 * 75)) * fade)
        text_start_x = center_x - text_width // 2
        dot_radius = int(10 + pulse * 2)

        dot_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(dot_surface, player_color,
                           (16, 16), max(8, min(12, dot_radius)))
        dot_surface.set_alpha(alpha_value)
        surface.blit(dot_surface, (text_start_x - 36, center_y - 16))

        text_surface = FONT_TURN_INDICATOR.render(text, True, player_color)
        text_surface.set_alpha(alpha_value)
        text_rect = text_surface.get_rect(center=(center_x, center_y))
        surface.blit(text_surface, text_rect)

    def winner_summary(self):
        if self.end_cause == "bankruptcy" and self.bankrupt_player_index is not None:
            winner_index = 1 - self.bankrupt_player_index
            return {
                "index": winner_index,
                "name": self.players[winner_index]["name"],
                "reason": "managed the budget better",
                "loser": self.players[self.bankrupt_player_index]["name"],
            }

        contribution_a = self.player1_carbon_contribution
        contribution_b = self.player2_carbon_contribution
        if contribution_a < contribution_b:
            return {"index": 0, "name": "Player 1", "reason": "made greener decisions", "loser": "Player 2"}
        if contribution_b < contribution_a:
            return {"index": 1, "name": "Player 2", "reason": "made greener decisions", "loser": "Player 1"}

        eco_a = self.players[0]["eco"]
        eco_b = self.players[1]["eco"]
        if eco_a > eco_b:
            return {"index": 0, "name": "Player 1", "reason": "made more eco choices", "loser": "Player 2"}
        if eco_b > eco_a:
            return {"index": 1, "name": "Player 2", "reason": "made more eco choices", "loser": "Player 1"}

        if self.players[0]["budget"] > self.players[1]["budget"]:
            return {"index": 0, "name": "Player 1", "reason": "managed funds better", "loser": "Player 2"}
        if self.players[1]["budget"] > self.players[0]["budget"]:
            return {"index": 1, "name": "Player 2", "reason": "managed funds better", "loser": "Player 1"}
        return {"index": None, "name": None, "reason": None, "loser": None}

    def player_eco_rating(self, player):
        ratio = player["eco"] / max(1, player["decisions"])
        if ratio >= 0.75:
            return "🌱 Green Hero", (74, 222, 128)
        if ratio >= 0.5:
            return "♻️ Eco Planner", (163, 230, 53)
        if ratio >= 0.25:
            return "⚠️ City Planner", (251, 191, 36)
        return "☠️ Carbon Criminal", (248, 113, 113)

    def end_screen_summary(self):
        if self.end_cause == "bankruptcy":
            return {
                "title": "BANKRUPT!",
                "title_color": (239, 68, 68),
                "subtitle": "Financial collapse halted the challenge.",
            }
        if self.end_cause == "collapse":
            return {
                "title": "City Collapsed!",
                "title_color": (239, 68, 68),
                "subtitle": "Carbon overload destroyed the city.",
            }
        if self.end_cause == "rounds_complete":
            if self.carbon_level < 60:
                subtitle = "Green City! Outstanding teamwork."
            elif self.carbon_level < 80:
                subtitle = "Recovering City. Room to improve."
            else:
                subtitle = "City in Crisis. Barely made it."
            return {
                "title": "City Survived!",
                "title_color": (34, 197, 94),
                "subtitle": subtitle,
            }
        return {
            "title": "City Collapsed!",
            "title_color": (239, 68, 68),
            "subtitle": "The city could not survive the environmental damage.",
        }

    def draw_bankruptcy_overlay(self):
        surface = self.base_surface
        overlay = pygame.Surface((BASE_W, BASE_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        panel = pygame.Rect(240, 200, 800, 320)
        pygame.draw.rect(surface, (26, 0, 0), panel, border_radius=20)
        draw_alpha_outline(surface, panel, (239, 68, 68),
                           width=3, border_radius=20)

        pulse_scale = 1.0 + math.sin(self.bankruptcy_timer * 4.0) * 0.05
        title_surface = FONT_BANKRUPTCY_TITLE.render(
            "BANKRUPT!", True, (239, 68, 68))
        scaled_size = (
            max(1, int(title_surface.get_width() * pulse_scale)),
            max(1, int(title_surface.get_height() * pulse_scale)),
        )
        pulsed_title = pygame.transform.smoothscale(title_surface, scaled_size)
        title_rect = pulsed_title.get_rect(center=(640, 260))
        shadow = pygame.transform.smoothscale(
            FONT_BANKRUPTCY_TITLE.render("BANKRUPT!", True, (0, 0, 0)), scaled_size)
        surface.blit(shadow, title_rect.move(3, 3))
        surface.blit(pulsed_title, title_rect)

        bankrupt_name = self.players[self.bankrupt_player_index][
            "name"] if self.bankrupt_player_index is not None else "A player"
        draw_shadowed_text(surface, FONT_BANKRUPTCY_LINE,
                           f"{bankrupt_name} has run out of money!", (252, 165, 165), (640, 340), center=True)
        draw_shadowed_text(surface, FONT_BANKRUPTCY_BODY,
                           "The city cannot sustain further investment.", (148, 163, 184), (640, 390), center=True)
        if int(self.bankruptcy_timer / 0.5) % 2 == 0:
            draw_shadowed_text(surface, FONT_BANKRUPTCY_HINT,
                               "Press SPACE to see results", (100, 116, 139), (640, 440), center=True)

    def draw_trophy_icon(self, surface, center):
        cup_color = (255, 215, 0)
        pygame.draw.circle(surface, cup_color, (center[0], center[1] - 10), 14)
        pygame.draw.rect(
            surface, cup_color, (center[0] - 10, center[1] + 2, 20, 18), border_radius=4)
        pygame.draw.rect(
            surface, cup_color, (center[0] - 4, center[1] + 18, 8, 10), border_radius=3)
        pygame.draw.rect(surface, (210, 160, 30),
                         (center[0] - 14, center[1] + 26, 28, 6), border_radius=3)

    def draw_end_button(self, surface, button, base_color, hover_color):
        rect = button.rect
        fill = hover_color if button.hovered else base_color
        if button.hovered:
            glow_rect = rect.inflate(18, 18)
            glow = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(glow, (*base_color, 70),
                             glow.get_rect(), border_radius=30)
            surface.blit(glow, glow_rect.topleft)
        pygame.draw.rect(surface, SHADOW, rect.move(0, 4), border_radius=24)
        pygame.draw.rect(surface, fill, rect, border_radius=24)
        draw_alpha_outline(surface, rect, (255, 255, 255,
                           180), width=2, border_radius=24)
        draw_shadowed_text(surface, FONT_END_BUTTON,
                           button.text, WHITE, rect.center, center=True)

    def draw_end_player_card(self, surface, rect, player, contribution, winner_index, player_index):
        is_draw = winner_index is None
        is_winner = winner_index == player_index
        is_bankrupt = self.end_cause == "bankruptcy" and self.bankrupt_player_index == player_index
        border_color = (148, 163, 184) if is_draw else (
            34, 197, 94) if is_winner else (239, 68, 68)
        fill_color = (26, 0, 0) if is_bankrupt else (15, 23, 42)

        if is_winner:
            for inflate_by, alpha in ((10, 72), (20, 42), (30, 22)):
                glow_rect = rect.inflate(inflate_by, inflate_by)
                draw_alpha_outline(
                    surface, glow_rect, (*border_color, alpha), width=1, border_radius=16)

        pygame.draw.rect(surface, fill_color, rect, border_radius=12)
        draw_alpha_outline(surface, rect, border_color,
                           width=2, border_radius=12)
        clip_before = push_clip(surface, rect)

        draw_shadowed_text(surface, FONT_END_CARD_TITLE,
                           player["name"], WHITE, (rect.x + 20, rect.y + 18))
        if is_bankrupt:
            badge_rect = pygame.Rect(rect.right - 146, rect.y + 14, 126, 26)
            pygame.draw.rect(surface, (127, 29, 29),
                             badge_rect, border_radius=13)
            draw_alpha_outline(surface, badge_rect,
                               (239, 68, 68), width=1, border_radius=13)
            draw_shadowed_text(surface, FONT_HUD_WARNING, "💸 BANKRUPT",
                               (254, 202, 202), badge_rect.center, center=True, shadow_offset=1)

        draw_shadowed_text(surface, FONT_END_CARD_SMALL,
                           f"Total decisions: {player['decisions']}", LIGHT_GRAY, (rect.x + 20, rect.y + 56))
        draw_shadowed_text(surface, FONT_END_CARD_SMALL,
                           f"Eco choices: {player['eco']}", GREEN, (rect.x + 20, rect.y + 82))
        draw_shadowed_text(surface, FONT_END_CARD_SMALL,
                           f"Quick choices: {player['quick']}", RED, (rect.x + 20, rect.y + 108))

        if contribution < 0:
            impact_color = GREEN
        elif contribution > 0:
            impact_color = RED
        else:
            impact_color = LIGHT_GRAY
        draw_shadowed_text(
            surface,
            FONT_END_CARD_SMALL,
            f"Carbon Impact: {contribution:+d}",
            impact_color,
            (rect.x + 20, rect.y + 134),
        )
        if is_bankrupt:
            budget_text = "$0 — Out of funds"
            budget_text_color = (239, 68, 68)
        elif self.end_cause == "bankruptcy" and is_winner:
            budget_text = f"{format_budget(player['budget'])} remaining"
            budget_text_color = (34, 197, 94)
        else:
            budget_text = f"Final Budget: {format_budget(player['budget'])}"
            budget_text_color = budget_color(player["budget"])
        draw_shadowed_text(surface, FONT_END_CARD_SMALL, budget_text,
                           budget_text_color, (rect.x + 20, rect.y + 158))
        surface.set_clip(clip_before)

    def draw_end(self):
        surface = self.base_surface
        surface.fill(BG_COLOR)
        summary = self.end_screen_summary()
        winner = self.winner_summary()

        panel = pygame.Rect(70, 40, 1140, 668)
        border_width = 3 if self.end_cause == "bankruptcy" else 2
        border_color = (239, 68, 68) if self.end_cause == "bankruptcy" else (
            *summary["title_color"], 255)
        draw_panel(surface, panel, PANEL_COLOR, border_color,
                   radius=26, border_width=border_width)
        clip_before = push_clip(surface, panel)

        glow_overlay = pygame.Surface(panel.size, pygame.SRCALPHA)
        pygame.draw.rect(
            glow_overlay, (*summary["title_color"], 22), glow_overlay.get_rect(), border_radius=26)
        surface.blit(glow_overlay, panel.topleft)

        title_font = FONT_BANKRUPT_END if self.end_cause == "bankruptcy" else FONT_END_TITLE
        draw_shadowed_text(
            surface, title_font, summary["title"], summary["title_color"], (BASE_W // 2, 118), center=True)
        draw_shadowed_text(surface, FONT_END_SUBTITLE,
                           summary["subtitle"], WHITE, (BASE_W // 2, 168), center=True)
        if self.end_cause == "collapse" and winner["name"]:
            draw_shadowed_text(surface, FONT_END_SUBTITLE,
                               f"But {winner['name']} played better!", YELLOW, (BASE_W // 2, 212), center=True)

        banner_rect = pygame.Rect((BASE_W - 700) // 2, 280, 700, 100)
        if winner["name"]:
            if self.end_cause == "bankruptcy":
                pygame.draw.rect(surface, (20, 83, 45),
                                 banner_rect, border_radius=16)
                draw_alpha_outline(surface, banner_rect,
                                   (34, 197, 94), width=2, border_radius=16)
                draw_shadowed_text(surface, pygame.font.SysFont(
                    "Arial", 36, bold=True), f"🏆 {winner['name']} Wins!", WHITE, (banner_rect.centerx, banner_rect.y + 30), center=True)
                draw_shadowed_text(surface, FONT_END_SUBTITLE, f"{winner['loser']} ran out of money!", (
                    252, 165, 165), (banner_rect.centerx, banner_rect.y + 70), center=True)
            else:
                draw_gradient_rect(
                    surface, banner_rect, (22, 101, 52), (21, 128, 61), border_radius=16)
                draw_alpha_outline(surface, banner_rect,
                                   (74, 222, 128), width=2, border_radius=16)
                self.draw_trophy_icon(surface, (370, 330))
                draw_shadowed_text(surface, FONT_END_BANNER, f"🏆 {winner['name']} Wins!", WHITE, (
                    banner_rect.centerx, banner_rect.y + 32), center=True)
                draw_shadowed_text(
                    surface,
                    FONT_END_BANNER_SUB,
                    f"{winner['name']} {winner['reason']} this round",
                    (187, 247, 208),
                    (banner_rect.centerx, banner_rect.y + 70),
                    center=True,
                )
        else:
            pygame.draw.rect(surface, (30, 41, 59),
                             banner_rect, border_radius=16)
            draw_alpha_outline(surface, banner_rect,
                               (148, 163, 184), width=2, border_radius=16)
            draw_shadowed_text(surface, FONT_END_BANNER, "🤝 It's a Draw!", (
                226, 232, 240), (banner_rect.centerx, banner_rect.y + 32), center=True)
            draw_shadowed_text(
                surface,
                FONT_END_BANNER_SUB,
                "Both players performed equally",
                (148, 163, 184),
                (banner_rect.centerx, banner_rect.y + 70),
                center=True,
            )

        player_cards = [
            (pygame.Rect(180, 400, 420, 180),
             self.players[0], self.player1_carbon_contribution, 0),
            (pygame.Rect(660, 400, 420, 180),
             self.players[1], self.player2_carbon_contribution, 1),
        ]
        for rect, player, contribution, index in player_cards:
            self.draw_end_player_card(
                surface, rect, player, contribution, winner["index"], index)
            rating_text, rating_color = self.player_eco_rating(player)
            draw_shadowed_text(surface, FONT_END_CARD_BODY, rating_text,
                               rating_color, (rect.centerx, 600), center=True)

        self.replay_button.set_rect((460, 660, 160, 48))
        self.quit_button.set_rect((660, 660, 160, 48))
        self.draw_end_button(surface, self.replay_button,
                             (22, 163, 74), (34, 197, 94))
        self.draw_end_button(surface, self.quit_button,
                             (185, 28, 28), (220, 38, 38))
        self.particles.draw(surface)
        surface.set_clip(clip_before)

    def carbon_level_color(self):
        value = self.carbon_level
        if value < 50:
            return lerp_color(GREEN, YELLOW, value / 50.0)
        return lerp_color(YELLOW, RED, (value - 50) / 50.0)

    def draw_resolution_debug(self):
        fps_surface = FONT_TINY.render(
            f"FPS: {int(self.clock.get_fps())}", True, WHITE)
        fps_surface.set_alpha(85)
        self.base_surface.blit(fps_surface, (8, 708))

        if not self.show_resolution_debug:
            return
        text = f"{RENDER_W}x{RENDER_H}" + (" [COMPAT]" if COMPAT_MODE else "")
        debug_surface = FONT_TINY.render(text, True, WHITE)
        debug_surface.set_alpha(68)
        debug_rect = debug_surface.get_rect(
            bottomright=(BASE_W - 10, BASE_H - 8))
        self.base_surface.blit(debug_surface, debug_rect)

    def present_frame(self):
        source_surface = self.base_surface
        if self.state == "bankruptcy" and self.shake_time > 0:
            shake_surface = pygame.Surface((BASE_W, BASE_H))
            shake_surface.fill(BG_COLOR)
            shake_px = max(1, int(self.shake_strength *
                           (self.shake_time / max(self.shake_duration, 0.001))))
            shake_surface.blit(self.base_surface, (random.randint(-shake_px,
                               shake_px), random.randint(-shake_px, shake_px)))
            source_surface = shake_surface
        if RENDER_W == BASE_W and RENDER_H == BASE_H:
            self.screen.blit(source_surface, (0, 0))
        else:
            scaled = pygame.transform.smoothscale(
                source_surface, (RENDER_W, RENDER_H))
            self.screen.blit(scaled, (0, 0))
        pygame.display.flip()

    def draw(self):
        self.base_surface.fill(BG_COLOR)
        if self.state == "title":
            self.draw_title()
        elif self.state == "game":
            self.draw_game()
        elif self.state == "bankruptcy":
            self.draw_game()
            self.draw_bankruptcy_overlay()
        else:
            self.draw_end()
        self.draw_resolution_debug()
        self.present_frame()

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.last_dt = dt
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()

# To build: pyinstaller --onefile --noconsole main.py

import pygame
import os
import math
import random
import sys
import ctypes
from array import array
from dataclasses import dataclass

os.environ["SDL_VIDEO_CENTERED"] = "1"


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
    SCREEN = pygame.display.set_mode(
        (RENDER_W, RENDER_H), pygame.NOFRAME | pygame.HWSURFACE | pygame.DOUBLEBUF)
else:
    SCREEN = pygame.display.set_mode(
        (RENDER_W, RENDER_H), pygame.SCALED | pygame.HWSURFACE | pygame.DOUBLEBUF)

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
FONT_ROUND = pygame.font.SysFont("Arial", 22, bold=True)
FONT_HEALTH_LABEL = pygame.font.SysFont("Arial", 12, bold=True)
FONT_ZONE_LABEL = pygame.font.SysFont("Arial", 14)
FONT_METER_TITLE = pygame.font.SysFont("Arial", 15, bold=True)
FONT_METER_VALUE = pygame.font.SysFont("Arial", 14)
FONT_CARD_HEADER = pygame.font.SysFont("Arial", 16, bold=True)
FONT_CARD_TITLE = pygame.font.SysFont("Arial", 17, bold=True)
FONT_CARD_TITLE_SMALL = pygame.font.SysFont("Arial", 14, bold=True)
FONT_CHOICE_NAME = pygame.font.SysFont("Arial", 15, bold=True)
FONT_BADGE = pygame.font.SysFont("Arial", 12)
FONT_BUTTON = pygame.font.SysFont("Arial", 14, bold=True)
FONT_HUD_NAME = pygame.font.SysFont("Arial", 16, bold=True)
FONT_HUD_BUDGET = pygame.font.SysFont("Arial", 14)
FONT_HUD_WARNING = pygame.font.SysFont("Arial", 12, bold=True)
FONT_TURN_INDICATOR = pygame.font.SysFont("Arial", 42, bold=True)
FONT_END_TITLE = pygame.font.SysFont("Arial", 44, bold=True)
FONT_END_SUBTITLE = pygame.font.SysFont("Arial", 20)
FONT_END_BANNER = pygame.font.SysFont("Arial", 32, bold=True)
FONT_END_BANNER_SUB = pygame.font.SysFont("Arial", 16)
FONT_END_CARD_TITLE = pygame.font.SysFont("Arial", 24, bold=True)
FONT_END_CARD_BODY = pygame.font.SysFont("Arial", 18)
FONT_END_CARD_SMALL = pygame.font.SysFont("Arial", 16)
FONT_END_BUTTON = pygame.font.SysFont("Arial", 18, bold=True)
FONT_BANKRUPT_END = pygame.font.SysFont("Arial", 52, bold=True)
FONT_BANKRUPTCY_TITLE = pygame.font.SysFont("Arial", 64, bold=True)
FONT_BANKRUPTCY_LINE = pygame.font.SysFont("Arial", 24)
FONT_BANKRUPTCY_BODY = pygame.font.SysFont("Arial", 18)
FONT_BANKRUPTCY_HINT = pygame.font.SysFont("Arial", 16)


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
ECO_COSTS = {
    "Build a Metro Line": 8500,
    "Add More Highways": 3000,
    "Install Bike Lanes": 4200,
    "Expand Airport": 2500,
    "Downtown Commute Plan": 5000,
    "Regional Expansion": 2000,
    "Build Solar Farm": 12000,
    "Build Coal Plant": 1800,
    "Wind Turbines": 9500,
    "Natural Gas Plant": 2200,
    "Nuclear Power": 15000,
    "Geothermal Plant": 11000,
    "Recycling Program": 3500,
    "Open Landfill": 1200,
    "Composting Initiative": 2800,
    "Waste to Energy Plant": 7000,
    "Zero Waste Policy": 6500,
    "Plant Urban Forest": 5500,
    "Build Shopping Mall": 1500,
    "Community Solar Garden": 8000,
    "Green Rooftop Program": 6000,
    "Urban Farm Network": 4500,
}
QUICK_COSTS = {
    "Build a Metro Line": 1200,
    "Add More Highways": 800,
    "Install Bike Lanes": 600,
    "Expand Airport": 700,
    "Downtown Commute Plan": 900,
    "Regional Expansion": 500,
    "Build Solar Farm": 1500,
    "Build Coal Plant": 600,
    "Wind Turbines": 1200,
    "Natural Gas Plant": 700,
    "Nuclear Power": 2000,
    "Geothermal Plant": 1800,
    "Recycling Program": 500,
    "Open Landfill": 300,
    "Composting Initiative": 400,
    "Waste to Energy Plant": 900,
    "Zero Waste Policy": 1100,
    "Plant Urban Forest": 800,
    "Build Shopping Mall": 400,
    "Community Solar Garden": 1000,
    "Green Rooftop Program": 900,
    "Urban Farm Network": 700,
}

HUD_RECT = pygame.Rect(0, 0, BASE_W, 90)
CITY_PANEL_RECT = pygame.Rect(0, 90, 900, 630)
RIGHT_PANEL_RECT = pygame.Rect(910, 90, 370, 630)
METER_CONTAINER_RECT = pygame.Rect(910, 95, 370, 320)
CARD_PANEL_RECT = pygame.Rect(918, 415, 354, 300)
TITLE_PARTICLE_RECT = pygame.Rect(100, 180, BASE_W - 200, 440)
END_PARTICLE_RECT = pygame.Rect(100, 60, BASE_W - 200, 420)
CITY_ZONE_LABEL_Y = 698
CITY_DASH_LINE_Y = 682


def clamp(value, low, high):
    return max(low, min(high, value))


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(color_a, color_b, t):
    return tuple(int(lerp(color_a[i], color_b[i], t)) for i in range(3))


def format_budget(amount):
    return f"${amount:,}"


def budget_color(amount):
    if amount < 5000:
        return (239, 68, 68)
    if amount <= 15000:
        return (251, 191, 36)
    return (34, 197, 94)


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
        pygame.draw.rect(overlay, color, overlay.get_rect(),
                         width, border_radius=border_radius)
        surface.blit(overlay, rect.topleft)
        return
    pygame.draw.rect(surface, color, rect, width, border_radius=border_radius)


def draw_alpha_line(surface, color, start_pos, end_pos, width=1):
    if len(color) == 4:
        min_x = min(start_pos[0], end_pos[0]) - width
        min_y = min(start_pos[1], end_pos[1]) - width
        max_x = max(start_pos[0], end_pos[0]) + width
        max_y = max(start_pos[1], end_pos[1]) + width
        overlay = pygame.Surface(
            (max_x - min_x + 2, max_y - min_y + 2), pygame.SRCALPHA)
        pygame.draw.line(
            overlay,
            color,
            (start_pos[0] - min_x, start_pos[1] - min_y),
            (end_pos[0] - min_x, end_pos[1] - min_y),
            width,
        )
        surface.blit(overlay, (min_x, min_y))
        return
    pygame.draw.line(surface, color, start_pos, end_pos, width)


def draw_shadowed_text(surface, font, text, color, pos, center=False, shadow_offset=2):
    shadow = font.render(text, True, (0, 0, 0))
    text_surface = font.render(text, True, color)
    shadow_rect = shadow.get_rect(
        center=pos) if center else shadow.get_rect(topleft=pos)
    text_rect = text_surface.get_rect(
        center=pos) if center else text_surface.get_rect(topleft=pos)
    shadow_rect.x += shadow_offset
    shadow_rect.y += shadow_offset
    surface.blit(shadow, shadow_rect)
    surface.blit(text_surface, text_rect)


def draw_panel(surface, rect, fill_color, border_color=(255, 255, 255, 34), radius=16, shadow=True, border_width=1):
    if shadow:
        pygame.draw.rect(surface, SHADOW, rect.move(
            4, 5), border_radius=radius)
    pygame.draw.rect(surface, fill_color, rect, border_radius=radius)
    draw_alpha_outline(surface, rect, border_color,
                       width=border_width, border_radius=radius)


def draw_gradient_rect(surface, rect, start_color, end_color, border_radius=0, vertical=True):
    gradient = pygame.Surface(rect.size, pygame.SRCALPHA)
    span = max(1, rect.height - 1 if vertical else rect.width - 1)
    if vertical:
        for y in range(rect.height):
            t = y / span
            color = lerp_color(start_color, end_color, t)
            pygame.draw.line(gradient, color, (0, y), (rect.width, y))
    else:
        for x in range(rect.width):
            t = x / span
            color = lerp_color(start_color, end_color, t)
            pygame.draw.line(gradient, color, (x, 0), (x, rect.height))

    if border_radius > 0:
        mask = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255),
                         mask.get_rect(), border_radius=border_radius)
        gradient.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    surface.blit(gradient, rect.topleft)


def draw_symbol(surface, symbol, rect, color):
    if symbol == "transport":
        points = [(rect.centerx, rect.top), (rect.left,
                                             rect.bottom), (rect.right, rect.bottom)]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.line(surface, BG_COLOR, (rect.centerx,
                         rect.top + 4), (rect.centerx, rect.bottom - 4), 2)
    elif symbol == "energy":
        pygame.draw.circle(surface, color, rect.center, rect.width // 2 - 2, 3)
        pygame.draw.circle(surface, color, rect.center,
                           max(3, rect.width // 5))
    elif symbol == "waste":
        diamond = [(rect.centerx, rect.top), (rect.right, rect.centery),
                   (rect.centerx, rect.bottom), (rect.left, rect.centery)]
        pygame.draw.polygon(surface, color, diamond, 3)
        inner = rect.inflate(-10, -10)
        pygame.draw.rect(surface, color, inner, 2, border_radius=4)
    elif symbol in ("green", "leaf"):
        leaf_rect = rect.inflate(-4, -2)
        pygame.draw.ellipse(surface, color, leaf_rect)
        pygame.draw.line(surface, WHITE, (leaf_rect.left + 4,
                         leaf_rect.bottom - 4), (leaf_rect.right - 4, leaf_rect.top + 4), 2)
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
            sample = int(amplitude * math.sin(2 *
                         math.pi * frequency * t) * envelope)
            buffer.append(sample)
        return pygame.mixer.Sound(buffer=buffer.tobytes())
    except pygame.error:
        return None


@dataclass
class Choice:
    name: str
    carbon: int
    health: int


@dataclass
class DecisionCard:
    zone: str
    title: str
    eco_choice: Choice
    quick_choice: Choice
    eco_cost: int
    quick_cost: int


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
        self.hovered = self.visible and self.enabled and self.rect.collidepoint(
            mouse_pos)

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
            pygame.draw.rect(glow, (*self.base_color, 70),
                             glow.get_rect(), border_radius=20)
            surface.blit(glow, glow_rect.topleft)

        pygame.draw.rect(surface, SHADOW, self.rect.move(
            0, 4), border_radius=18)
        fill = self.hover_color if self.hovered else self.base_color
        if not self.enabled:
            fill = lerp_color(fill, (90, 90, 90), 0.5)
        pygame.draw.rect(surface, fill, self.rect, border_radius=18)
        draw_alpha_outline(surface, self.rect, (255, 255,
                           255, 200), width=2, border_radius=18)

        text_center = self.rect.center
        if self.icon:
            icon_rect = pygame.Rect(
                self.rect.x + 14, self.rect.centery - 10, 20, 20)
            draw_symbol(surface, self.icon, icon_rect, WHITE)
            text_center = (self.rect.centerx + 8, self.rect.centery)
        draw_shadowed_text(surface, font, self.text,
                           self.text_color, text_center, center=True)


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
            color = random.choice(
                [(0, 255, 136), (76, 255, 173), (167, 255, 206)])
            self.emit(center[0], center[1], (vx, vy), color, random.uniform(
                0.8, 1.6), random.uniform(5, 10), kind="leaf", gravity=42)

    def spawn_smoke_burst(self, center, count=20):
        for _ in range(count):
            vx = random.uniform(-40, 40)
            vy = random.uniform(-120, -30)
            gray = random.randint(90, 150)
            self.emit(center[0], center[1], (vx, vy), (gray, gray, gray), random.uniform(
                1.0, 1.8), random.uniform(8, 16), kind="smoke", gravity=-8)

    def spawn_title_carbon(self, area_rect, count=2):
        for _ in range(count):
            x = random.uniform(area_rect.left, area_rect.right)
            y = area_rect.bottom + random.uniform(0, 40)
            self.emit(x, y, (random.uniform(-8, 8), random.uniform(-55, -25)), (140,
                      220, 180), random.uniform(1.8, 2.8), random.uniform(3, 7), kind="circle")

    def spawn_celebration(self, area_rect, count=16):
        for _ in range(count):
            x = random.uniform(area_rect.left, area_rect.right)
            y = area_rect.top + random.uniform(0, area_rect.height * 0.45)
            color = random.choice(
                [GREEN, YELLOW, (110, 210, 255), WHITE, (255, 116, 116)])
            self.emit(x, y, (random.uniform(-70, 70), random.uniform(-20, 140)), color,
                      random.uniform(1.0, 2.0), random.uniform(2, 5), kind="spark", gravity=42)

    def spawn_end_smoke(self, area_rect, count=10):
        for _ in range(count):
            x = random.uniform(area_rect.left, area_rect.right)
            y = area_rect.top + random.uniform(0, area_rect.height)
            color = random.choice(
                [(255, 110, 110), (255, 200, 110), (180, 180, 190), (255, 90, 90)])
            self.emit(x, y, (random.uniform(-26, 26), random.uniform(-40, 40)), color,
                      random.uniform(0.9, 1.6), random.uniform(2, 5), kind="circle", gravity=14)

    def spawn_floating_text(self, x, y, text, color):
        self.particles.append({
            "x": float(x),
            "y": float(y),
            "vx": 0.0,
            "vy": -40.0,
            "life": 3.5,
            "max_life": 3.5,
            "size": 0.0,
            "color": color,
            "kind": "text",
            "gravity": 0.0,
            "fade": True,
            "rotation": 0.0,
            "spin": 0.0,
            "text": text,
        })

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
            alpha = int(
                255 * (particle["life"] / particle["max_life"])) if particle["fade"] else 255
            size = max(1, int(particle["size"]))
            particle_surface = pygame.Surface(
                (size * 4, size * 4), pygame.SRCALPHA)
            color = (*particle["color"], alpha)
            center = (particle_surface.get_width() // 2,
                      particle_surface.get_height() // 2)

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
                particle_surface = pygame.transform.rotate(
                    particle_surface, math.degrees(particle["rotation"]))
            elif particle["kind"] == "spark":
                pygame.draw.circle(particle_surface, color, center, size)
                pygame.draw.line(
                    particle_surface, color, (center[0] - size, center[1]), (center[0] + size, center[1]), 1)
                pygame.draw.line(
                    particle_surface, color, (center[0], center[1] - size), (center[0], center[1] + size), 1)

            if particle["kind"] == "text":
                font_surface = FONT_HEADING.render(
                    particle["text"], True, particle["color"])
                font_surface.set_alpha(alpha)
                surface.blit(
                    font_surface, (int(particle["x"] + ox), int(particle["y"] + oy)))
                continue

            else:
                pygame.draw.circle(particle_surface, color, center, size)

            draw_x = int(particle["x"] + ox - particle_surface.get_width() / 2)
            draw_y = int(particle["y"] + oy -
                         particle_surface.get_height() / 2)
            surface.blit(particle_surface, (draw_x, draw_y))


class CityRenderer:
    def __init__(self):
        self.area = CITY_PANEL_RECT.copy()
        self.animation_time = 0.0
        road_top = self.area.height - 94
        base_y = road_top - 8

        def make_cluster(start_x, specs):
            buildings = []
            for x_offset, width, height, style in specs:
                rect = pygame.Rect(start_x + x_offset,
                                   base_y - height, width, height)
                buildings.append({"rect": rect, "style": style})
            return buildings

        self.zone_layout = {
            "Transport": {
                "buildings": make_cluster(32, [(0, 34, 238, "skyscraper"), (42, 82, 156, "office"), (96, 46, 88, "shop")]),
                "label_pos": (112, CITY_ZONE_LABEL_Y - self.area.y),
                "accent": "transport",
            },
            "Energy": {
                "buildings": make_cluster(232, [(0, 38, 216, "skyscraper"), (48, 88, 148, "office"), (100, 44, 98, "shop")]),
                "label_pos": (312, CITY_ZONE_LABEL_Y - self.area.y),
                "accent": "energy",
            },
            "Waste": {
                "buildings": make_cluster(432, [(0, 76, 122, "office"), (58, 36, 194, "skyscraper"), (100, 48, 82, "shop")]),
                "label_pos": (512, CITY_ZONE_LABEL_Y - self.area.y),
                "accent": "waste",
            },
            "Green Space": {
                "buildings": make_cluster(632, [(0, 36, 176, "skyscraper"), (44, 80, 132, "office"), (96, 42, 86, "shop")]),
                "label_pos": (712, CITY_ZONE_LABEL_Y - self.area.y),
                "accent": "green",
            },
        }

        self.zone_centers = {
            zone: (
                self.area.x +
                sum(entry["rect"].centerx for entry in data["buildings"]
                    ) / len(data["buildings"]),
                self.area.y + base_y - 60,
            )
            for zone, data in self.zone_layout.items()
        }
        self.zone_visuals = {zone: {"score": 0.0, "target": 0.0}
                             for zone in self.zone_layout}

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
        self.animation_time += dt
        for zone in self.zone_visuals:
            current = self.zone_visuals[zone]["score"]
            target = self.zone_visuals[zone]["target"]
            self.zone_visuals[zone]["score"] = lerp(
                current, target, min(1.0, dt * 4.5))

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

        window_color = lerp_color(
            (252, 236, 120), (255, 160, 92), pollution * 0.85)
        step_x = 14 if style == "skyscraper" else 18
        step_y = 18 if style == "skyscraper" else 20
        margin_x = 7
        margin_y = 10
        for wx in range(rect.x + margin_x, rect.right - 8, step_x):
            for wy in range(rect.y + margin_y, rect.bottom - 16, step_y):
                window = pygame.Rect(wx, wy, 6 if style == "shop" else 7, 9)
                pygame.draw.rect(surface, window_color,
                                 window, border_radius=2)

        if style == "skyscraper":
            pygame.draw.line(surface, (220, 220, 230), (rect.centerx,
                             rect.y), (rect.centerx, rect.y - 12), 2)
            pygame.draw.circle(surface, (220, 220, 230),
                               (rect.centerx, rect.y - 12), 2)
        elif style == "shop":
            awning = pygame.Rect(rect.x + 4, rect.y +
                                 rect.height // 2 - 10, rect.width - 8, 12)
            pygame.draw.rect(surface, lerp_color(
                base_color, WHITE, 0.24), awning, border_radius=4)

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

        star_color = lerp_color(
            (255, 255, 255), (255, 208, 178), pollution * 0.35)
        if pollution < 0.92:
            for x, y, size in self.stars:
                pygame.draw.circle(surface, star_color,
                                   (area.x + x, area.y + y), size)

        haze = pygame.Surface(area.size, pygame.SRCALPHA)
        pygame.draw.rect(haze, (220, 70, 50, int(
            70 * pollution)), haze.get_rect())
        surface.blit(haze, area.topleft)

        hill_back = []
        hill_front = []
        for step in range(0, area.width + 26, 26):
            hill_back.append((area.x + step, area.bottom - 180 -
                             math.sin(step * 0.012) * 24 - math.cos(step * 0.023) * 16))
            hill_front.append((area.x + step, area.bottom - 148 -
                              math.sin(step * 0.017 + 1.2) * 32 - math.cos(step * 0.03) * 10))
        pygame.draw.polygon(surface, (38, 40, 63), [
                            (area.left, area.bottom)] + hill_back + [(area.right, area.bottom)])
        pygame.draw.polygon(surface, (28, 30, 50), [
                            (area.left, area.bottom)] + hill_front + [(area.right, area.bottom)])

        sun_color = lerp_color((255, 223, 154), (255, 136, 92), pollution)
        pygame.draw.circle(surface, sun_color,
                           (area.right - 115, area.top + 96), 38)

        road_rect = pygame.Rect(area.left, area.bottom - 76, area.width, 76)
        pavement_rect = pygame.Rect(
            area.left, road_rect.y - 18, area.width, 18)
        pygame.draw.rect(surface, (56, 60, 74), pavement_rect)
        pygame.draw.rect(surface, (33, 36, 49), road_rect)
        pygame.draw.line(surface, (120, 128, 145), (area.left,
                         pavement_rect.y), (area.right, pavement_rect.y), 2)
        pygame.draw.line(surface, (76, 82, 98), (area.left,
                         road_rect.y + 2), (area.right, road_rect.y + 2), 2)

        dash_y = area.y + (CITY_DASH_LINE_Y - CITY_PANEL_RECT.y)
        for dash_x in range(area.left, area.left + 900, 40):
            pygame.draw.rect(surface, (51, 65, 85),
                             (dash_x, dash_y, 20, 4), border_radius=2)

        for zone, data in self.zone_layout.items():
            zone_color = self._zone_color(zone)
            for building in data["buildings"]:
                draw_rect = building["rect"].move(area.x, area.y)
                self._draw_building(surface, draw_rect,
                                    building["style"], zone_color, pollution)

            if data["accent"] == "transport":
                track_y = pavement_rect.y - 12
                pygame.draw.line(
                    surface, (18, 18, 24), (area.x + 24, track_y), (area.x + 158, track_y), 6)
                pygame.draw.line(surface, (120, 220, 255), (area.x +
                                 40, track_y - 6), (area.x + 142, track_y - 6), 3)
            elif data["accent"] == "energy":
                for base_x in (area.x + 262, area.x + 320):
                    stem_bottom = pavement_rect.y - 10
                    pygame.draw.line(
                        surface, (220, 220, 230), (base_x, stem_bottom), (base_x, stem_bottom - 44), 3)
                    center = (base_x, stem_bottom - 44)
                    for angle in (0, 120, 240):
                        radians = math.radians(
                            angle + self.animation_time * 70.0)
                        tip = (center[0] + math.cos(radians) * 14,
                               center[1] + math.sin(radians) * 14)
                        pygame.draw.line(
                            surface, (230, 230, 240), center, tip, 2)
                    pygame.draw.circle(surface, (230, 230, 240), center, 3)
            elif data["accent"] == "waste":
                for bx in (area.x + 428, area.x + 456, area.x + 484):
                    bin_rect = pygame.Rect(bx, pavement_rect.y - 26, 18, 24)
                    pygame.draw.rect(surface, zone_color,
                                     bin_rect, border_radius=4)
                    pygame.draw.rect(surface, (15, 15, 20),
                                     bin_rect, 2, border_radius=4)
            elif data["accent"] == "green":
                for tx in (area.x + 566, area.x + 620):
                    trunk = pygame.Rect(tx, pavement_rect.y - 28, 6, 22)
                    pygame.draw.rect(surface, (104, 70, 38),
                                     trunk, border_radius=3)
                    pygame.draw.circle(surface, zone_color,
                                       (tx + 3, pavement_rect.y - 34), 16)

            label_pos = (area.x + data["label_pos"]
                         [0], area.y + data["label_pos"][1])
            draw_shadowed_text(surface, FONT_ZONE_LABEL, zone,
                               (148, 163, 184), label_pos, center=True)

        for tree_x in (area.left + 38, area.left + 186, area.left + 340, area.left + 502, area.left + 640):
            trunk = pygame.Rect(tree_x, pavement_rect.y - 24, 6, 18)
            pygame.draw.rect(surface, (98, 67, 41), trunk, border_radius=3)
            pygame.draw.circle(surface, (58, 165, 96),
                               (tree_x + 3, pavement_rect.y - 28), 12)

        for lamp_x in (area.left + 112, area.left + 286, area.left + 450, area.left + 606):
            pygame.draw.line(surface, (188, 194, 205), (lamp_x,
                             pavement_rect.y), (lamp_x, pavement_rect.y - 30), 3)
            pygame.draw.circle(surface, (255, 237, 166),
                               (lamp_x, pavement_rect.y - 34), 5)

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
        self.display_value = lerp(
            self.display_value, self.value, min(1.0, dt * 4.8))
        self.pulse_time += dt

    def draw(self, surface, warning_active=False):
        frame = self.rect
        pygame.draw.rect(surface, PANEL_COLOR, frame, border_radius=16)
        draw_alpha_outline(surface, frame, (255, 255, 255,
                           22), width=1, border_radius=16)
        clip_before = push_clip(surface, frame)

        draw_shadowed_text(surface, FONT_METER_TITLE, "CARBON LEVEL",
                           (170, 170, 204), (1095, 108), center=True)

        value_pill = pygame.Rect(1035, 120, 120, 24)
        pygame.draw.rect(surface, (26, 26, 62), value_pill, border_radius=12)
        draw_alpha_outline(surface, value_pill, (255, 215, 0),
                           width=2, border_radius=12)
        draw_shadowed_text(surface, FONT_METER_VALUE,
                           f"{int(round(self.display_value))}/100", (255, 215, 0), value_pill.center, center=True)

        meter_outer_rect = pygame.Rect(1010, 148, 60, 220)
        meter_inner_rect = pygame.Rect(1012, 150, 56, 216)
        pygame.draw.rect(surface, (13, 27, 42),
                         meter_outer_rect, border_radius=10)
        draw_alpha_outline(surface, meter_outer_rect,
                           (51, 68, 102), width=2, border_radius=10)

        fill_height = int((self.display_value / 100.0) * 216)
        fill_top = 366 - fill_height
        surface.set_clip(meter_inner_rect)
        for row_index in range(fill_height):
            t = row_index / 216
            r = int(255 * t)
            g = int(255 * (1 - t))
            b = 50
            y = 366 - row_index
            if fill_top <= y <= 366:
                pygame.draw.line(
                    surface, (r, g, b), (meter_inner_rect.x, y), (meter_inner_rect.right - 1, y))
        surface.set_clip(frame)

        meter_top = 150
        meter_bottom = 366
        meter_height = 216
        for val in (0, 25, 50, 75, 100):
            label_y = meter_bottom - int((val / 100) * meter_height)
            pygame.draw.line(surface, (68, 85, 102),
                             (1072, label_y), (1078, label_y), 1)
            label_surface = FONT_TINY.render(str(val), True, (136, 153, 170))
            surface.blit(label_surface, (1082, label_y - 7))

        if self.value >= 80:
            pulse = (math.sin(self.pulse_time * 10) + 1) * 0.5
            alert = pygame.Surface(frame.size, pygame.SRCALPHA)
            pygame.draw.rect(alert, (255, 40, 40, int(
                40 + pulse * 80)), alert.get_rect(), 4, border_radius=16)
            surface.blit(alert, frame.topleft)
            draw_shadowed_text(surface, FONT_SMALL_BOLD, "CRITICAL",
                               RED if warning_active else YELLOW, (frame.centerx, frame.bottom - 24), center=True)

        surface.set_clip(clip_before)


class HUD:
    def __init__(self):
        self.rect = HUD_RECT.copy()
        self.left_pill = pygame.Rect(10, 12, 210, 48)
        self.right_pill = pygame.Rect(1060, 12, 210, 48)
        self.health_bar = pygame.Rect(440, 53, 400, 14)

    def draw(self, surface, players, current_player, round_number, city_health, flash_bankrupt_index=None, flash_active=False, blink_on=True):
        overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(overlay, (10, 16, 30, 210), overlay.get_rect())
        surface.blit(overlay, self.rect.topleft)
        pygame.draw.line(surface, (65, 82, 118), (0,
                         self.rect.bottom - 1), (BASE_W, self.rect.bottom - 1), 2)
        clip_before = push_clip(surface, self.rect)

        pill_specs = []
        for idx, player in enumerate(players):
            budget_text = format_budget(player["budget"])
            text_width = max(FONT_HUD_NAME.size(player["name"])[
                             0], FONT_HUD_BUDGET.size(budget_text)[0])
            width = max(210, text_width + 70)
            x = 10 if idx == 0 else BASE_W - 10 - width
            pill_specs.append(pygame.Rect(x, 12, width, 48))

        self.left_pill, self.right_pill = pill_specs

        for idx, pill in enumerate(pill_specs):
            player = players[idx]
            is_current = idx == current_player
            flash_this_pill = idx == flash_bankrupt_index and flash_active
            active_color = GREEN if idx == 0 else (167, 139, 250)
            inactive_border = (51, 65, 85)
            inactive_dot = (75, 85, 99)
            border = RED if flash_this_pill else active_color if is_current else inactive_border
            border_width = 2 if flash_this_pill else 3 if is_current else 1
            fill_color = (70, 12, 18) if flash_this_pill else PANEL_COLOR
            if is_current and not flash_this_pill:
                glow = pygame.Surface(
                    (pill.width + 10, pill.height + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow, (*active_color, 60),
                                 glow.get_rect(), border_radius=26)
                surface.blit(glow, (pill.x - 5, pill.y - 5))
            elif flash_this_pill:
                glow = pygame.Surface(
                    (pill.width + 16, pill.height + 16), pygame.SRCALPHA)
                pygame.draw.rect(glow, (239, 68, 68, 90),
                                 glow.get_rect(), border_radius=28)
                surface.blit(glow, (pill.x - 8, pill.y - 8))
            pygame.draw.rect(surface, fill_color, pill, border_radius=22)
            draw_alpha_outline(surface, pill, border,
                               width=border_width, border_radius=22)
            dot_color = RED if flash_this_pill else active_color if is_current else inactive_dot
            pygame.draw.circle(surface, dot_color,
                               (pill.x + 18, pill.y + 18), 6)
            draw_shadowed_text(surface, FONT_HUD_NAME,
                               player["name"], WHITE, (pill.x + 32, pill.y + 6))
            draw_shadowed_text(surface, FONT_HUD_BUDGET, format_budget(
                player["budget"]), budget_color(player["budget"]), (pill.x + 32, pill.y + 26))

            warning_text = None
            warning_color = None
            if player["budget"] < 5000:
                warning_text = "⚠ Critical Funds!"
                warning_color = (239, 68, 68)
            elif player["budget"] < 15000:
                warning_text = "⚠ Low Funds"
                warning_color = (251, 191, 36)
            if warning_text and blink_on:
                draw_shadowed_text(surface, FONT_HUD_WARNING, warning_text, warning_color, (
                    pill.centerx, pill.bottom + 2), center=True, shadow_offset=1)

        round_surface = FONT_ROUND.render(
            f"Round {round_number} / 15", True, WHITE)
        round_rect = round_surface.get_rect(center=(640, 18))
        shadow = FONT_ROUND.render(
            f"Round {round_number} / 15", True, (0, 0, 0))
        surface.blit(shadow, round_rect.move(2, 2))
        surface.blit(round_surface, round_rect)

        health_label = FONT_HEALTH_LABEL.render(
            "CITY HEALTH", True, LIGHT_GRAY)
        label_rect = health_label.get_rect(center=(640, 44))
        label_shadow = FONT_HEALTH_LABEL.render("CITY HEALTH", True, (0, 0, 0))
        surface.blit(label_shadow, label_rect.move(2, 2))
        surface.blit(health_label, label_rect)
        pygame.draw.rect(surface, PANEL_DARK, self.health_bar, border_radius=8)
        draw_alpha_outline(surface, self.health_bar,
                           (255, 255, 255, 180), width=2, border_radius=8)
        fill_width = int((clamp(city_health, 0, 100) / 100.0)
                         * (self.health_bar.width - 4))
        fill_rect = pygame.Rect(
            self.health_bar.x + 2, self.health_bar.y + 2, fill_width, self.health_bar.height - 4)
        health_color = GREEN if city_health >= 60 else YELLOW if city_health >= 30 else RED
        pygame.draw.rect(surface, health_color, fill_rect, border_radius=6)
        draw_shadowed_text(surface, FONT_SMALL, str(int(city_health)), health_color,
                           (self.health_bar.right + 28, self.health_bar.centery), center=True)
        surface.set_clip(clip_before)


class CardSystem:
    def __init__(self):
        self.card_rect = CARD_PANEL_RECT.copy()
        self.eco_button = Button(
            (0, 0, 0, 0), "ECO CHOICE", (0, 180, 96), (0, 220, 120), icon="leaf")
        self.quick_button = Button(
            (0, 0, 0, 0), "QUICK CHOICE", (204, 56, 56), (244, 76, 76), icon="quick")
        self.cards = self._build_cards()
        self.current_card = None
        self.current_index = -1
        self.slide_progress = 1.0
        self.slide_duration = 0.45
        self.show_card(random.randint(0, len(self.cards) - 1))

    def _build_cards(self):
        def make_choice(name, carbon, health):
            return Choice(name, carbon, health)

        def lookup_cost(cost_table, primary_name, fallback_name):
            if fallback_name in cost_table:
                return cost_table[fallback_name]
            return cost_table.get(primary_name, 1000)

        def make_card(zone, title, eco_name, eco_carbon, eco_health, quick_name, quick_carbon, quick_health):
            return DecisionCard(
                zone,
                title,
                make_choice(eco_name, eco_carbon, eco_health),
                make_choice(quick_name, quick_carbon, quick_health),
                lookup_cost(ECO_COSTS, eco_name, title),
                lookup_cost(QUICK_COSTS, quick_name, title),
            )

        return [
            make_card("Transport", "Downtown Commute Plan",
                      "Build a Metro Line", -8, 5, "Add More Highways", 10, -3),
            make_card("Transport", "Neighborhood Streets",
                      "Install Bike Lanes", -5, 3, "Add More Highways", 10, -3),
            make_card("Transport", "Regional Expansion",
                      "Build a Metro Line", -8, 5, "Expand Airport", 12, -2),
            make_card("Energy", "Power Grid Upgrade",
                      "Build Solar Farm", -10, 8, "Build Coal Plant", 15, -10),
            make_card("Energy", "Future Energy Mix",
                      "Wind Turbines", -8, 6, "Natural Gas Plant", 8, -4),
            make_card("Energy", "Industrial Demand Spike",
                      "Build Solar Farm", -10, 8, "Natural Gas Plant", 8, -4),
            make_card("Energy", "Regional Reliability Vote",
                      "Wind Turbines", -8, 6, "Build Coal Plant", 15, -10),
            make_card("Waste", "Community Waste Strategy",
                      "Recycling Program", -4, 4, "Open Landfill", 6, -5),
            make_card("Waste", "Food Waste Response",
                      "Composting Initiative", -3, 3, "Open Landfill", 6, -5),
            make_card("Waste", "School Sustainability Drive",
                      "Recycling Program", -4, 4, "Open Landfill", 6, -5),
            make_card("Green Space", "Vacant Lot Decision",
                      "Plant Urban Forest", -7, 7, "Build Shopping Mall", 9, -6),
            make_card("Green Space", "Riverfront Redevelopment",
                      "Plant Urban Forest", -7, 7, "Build Shopping Mall", 9, -6),
            make_card("Transport", "Tourism Growth Debate",
                      "Install Bike Lanes", -5, 3, "Expand Airport", 12, -2),
            make_card("Waste", "Industrial Overflow",
                      "Waste to Energy Plant", -6, 4, "Open Landfill", 6, -5),
            make_card("Waste", "City Cleanup Campaign",
                      "Zero Waste Policy", -8, 6, "Open Landfill", 6, -5),
            make_card("Waste", "School Recycling Drive",
                      "Composting Initiative", -3, 3, "Open Landfill", 6, -5),
            make_card("Green Space", "Rooftop Revolution",
                      "Green Rooftop Program", -5, 6, "Build Shopping Mall", 9, -6),
            make_card("Green Space", "Community Garden Vote",
                      "Urban Farm Network", -4, 5, "Build Shopping Mall", 9, -6),
            make_card("Green Space", "Solar or Trees Debate",
                      "Community Solar Garden", -7, 5, "Build Shopping Mall", 9, -6),
            make_card("Energy", "Clean Energy Summit",
                      "Geothermal Plant", -9, 7, "Build Coal Plant", 15, -10),
            make_card("Energy", "City Power Shortage",
                      "Nuclear Power", -12, 6, "Build Coal Plant", 15, -10),]

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
        self.slide_progress = min(
            1.0, self.slide_progress + dt / self.slide_duration)
        frame = self.current_rect()
        self.eco_button.set_rect(
            (926 + (frame.x - self.card_rect.x), 666, 164, 40))
        self.quick_button.set_rect(
            (1098 + (frame.x - self.card_rect.x), 666, 164, 40))
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
        text_surface = FONT_BADGE.render(text, True, color)
        badge_rect = pygame.Rect(x, y, text_surface.get_width() + 16, 20)
        pygame.draw.rect(surface, PANEL_DARK, badge_rect, border_radius=10)
        draw_shadowed_text(surface, FONT_BADGE, text, color,
                           badge_rect.center, center=True)
        return badge_rect

    def draw(self, surface, current_budget):
        if not self.current_card:
            return

        frame = self.current_rect()
        pygame.draw.rect(surface, (17, 24, 39), frame, border_radius=12)
        draw_alpha_outline(surface, frame, (30, 41, 59),
                           width=1, border_radius=12)
        clip_before = push_clip(surface, frame)
        zone_color = ZONE_COLORS.get(self.current_card.zone, WHITE)

        header_rect = pygame.Rect(frame.x, frame.y, 354, 40)
        pygame.draw.rect(surface, zone_color, header_rect,
                         border_top_left_radius=12, border_top_right_radius=12)
        icon_rect = pygame.Rect(frame.x + 12, frame.y + 10, 20, 20)
        draw_symbol(surface, zone_icon(
            self.current_card.zone), icon_rect, PANEL_DARK)
        zone_label_rect = FONT_CARD_HEADER.render(self.current_card.zone.upper(
        ), True, WHITE).get_rect(midleft=(frame.x + 40, frame.y + 20))
        draw_shadowed_text(surface, FONT_CARD_HEADER, self.current_card.zone.upper(
        ), WHITE, zone_label_rect.topleft)

        title_font = FONT_CARD_TITLE if FONT_CARD_TITLE.size(self.current_card.title)[
            0] <= 330 else FONT_CARD_TITLE_SMALL
        draw_shadowed_text(surface, title_font, self.current_card.title,
                           WHITE, (frame.x + 10, frame.y + 50))
        eco_cost_text = FONT_BADGE.render(
            f"ECO CHOICE: {format_budget(self.current_card.eco_cost)}", True, (74, 222, 128))
        quick_cost_text = FONT_BADGE.render(
            f"QUICK CHOICE: {format_budget(self.current_card.quick_cost)}", True, (251, 146, 60))
        surface.blit(eco_cost_text, (frame.x + 10, frame.y + 74))
        surface.blit(quick_cost_text, (frame.right - 10 -
                     quick_cost_text.get_width(), frame.y + 74))

        eco_rect = pygame.Rect(frame.x + 8, frame.y + 99, 338, 68)
        quick_rect = pygame.Rect(frame.x + 8, frame.y + 175, 338, 68)
        self.draw_choice_panel(
            surface, eco_rect, self.current_card.eco_choice, (34, 197, 94))
        self.draw_choice_panel(surface, quick_rect,
                               self.current_card.quick_choice, (239, 68, 68))

        self.draw_action_buttons(surface, frame)
        surface.set_clip(clip_before)

    def draw_choice_panel(self, surface, rect, choice, accent_color):
        pygame.draw.rect(surface, (15, 23, 42), rect, border_radius=8)
        pygame.draw.rect(surface, accent_color, (rect.x, rect.y, 4, rect.height),
                         border_top_left_radius=8, border_bottom_left_radius=8)
        draw_shadowed_text(surface, FONT_CHOICE_NAME,
                           choice.name, WHITE, (rect.x + 12, rect.y + 6))

        badge_y = rect.y + 30
        x = rect.x + 12
        badge_specs = [
            (f"Carbon {choice.carbon:+d}", (22, 101, 52), (34, 197, 94)),
            (f"Health {choice.health:+d}", (30, 58, 95), (96, 165, 250)),
        ]
        for text, bg_color, text_color in badge_specs:
            badge = self.draw_stat_badge(
                surface, x, badge_y, text, bg_color, text_color)
            x = badge.right + 6

    def draw_stat_badge(self, surface, x, y, text, bg_color, text_color):
        text_surface = FONT_BADGE.render(text, True, text_color)
        badge_rect = pygame.Rect(x, y, text_surface.get_width() + 16, 20)
        pygame.draw.rect(surface, bg_color, badge_rect, border_radius=10)
        draw_shadowed_text(surface, FONT_BADGE, text,
                           text_color, badge_rect.center, center=True)
        return badge_rect

    def draw_action_buttons(self, surface, frame):
        eco_button_rect = pygame.Rect(frame.x + 8, frame.y + 251, 164, 40)
        quick_button_rect = pygame.Rect(frame.x + 180, frame.y + 251, 164, 40)
        self.eco_button.set_rect(eco_button_rect)
        self.quick_button.set_rect(quick_button_rect)
        pygame.draw.rect(surface, (22, 163, 74),
                         eco_button_rect, border_radius=20)
        pygame.draw.circle(surface, (74, 222, 128),
                           (eco_button_rect.x + 18, eco_button_rect.y + 20), 8)
        draw_shadowed_text(surface, FONT_BUTTON, "ECO CHOICE",
                           WHITE, eco_button_rect.center, center=True)

        pygame.draw.rect(surface, (185, 28, 28),
                         quick_button_rect, border_radius=20)
        lightning_rect = pygame.Rect(
            quick_button_rect.x + 10, quick_button_rect.y + 10, 16, 20)
        draw_symbol(surface, "quick", lightning_rect, WHITE)
        draw_shadowed_text(surface, FONT_BUTTON, "QUICK CHOICE",
                           WHITE, quick_button_rect.center, center=True)


class Game:
    def __init__(self):
        self.screen = SCREEN
        self.base_surface = BASE_SURFACE
        self.clock = pygame.time.Clock()
        self.last_dt = 0.0
        self.hud = HUD()
        self.city = CityRenderer()
        self.carbon_meter = CarbonMeter(METER_CONTAINER_RECT)
        self.card_system = CardSystem()
        self.particles = ParticleSystem()
        self.replay_button = Button(
            (540, 570, 180, 52), "Replay", (0, 180, 96), (0, 220, 120))
        self.quit_button = Button(
            (760, 570, 180, 52), "Quit", (204, 56, 56), (244, 76, 76))

        self.sounds = {
            "eco": generate_tone(680, 0.17, 0.30),
            "quick": generate_tone(240, 0.20, 0.34),
            "warning": generate_tone(920, 0.12, 0.26),
            "click": generate_tone(500, 0.08, 0.22),
            "funds": generate_tone(1180, 0.10, 0.26),
        }

        self.show_resolution_debug = True
        self.title_particles_timer = 0.0
        self.end_particles_timer = 0.0
        self.warning_played = False
        self.shake_time = 0.0
        self.shake_strength = 0.0
        self.shake_duration = 0.45
        self.title_float = 0.0
        self.compat_overlay_elapsed = 0.0
        self.running = True
        self.reset_game()

    def reset_game(self):
        self.state = "title"
        self.players = [
            {"name": "Player 1", "budget": 100000,
                "eco": 0, "quick": 0, "decisions": 0},
            {"name": "Player 2", "budget": 100000,
                "eco": 0, "quick": 0, "decisions": 0},
        ]
        self.player1_carbon_contribution = 0
        self.player2_carbon_contribution = 0
        self.bankrupt_player_index = None
        self.bankruptcy_timer = 0.0
        self.critical_budget_warned = [False, False]
        self.turn_indicator_timer = 0.0
        self.current_player = 0
        self.completed_rounds = 0
        self.city_health = 100
        self.carbon_level = 30
        self.carbon_meter.set_value(30)
        self.zone_scores = {zone: 0 for zone in self.city.zone_layout}
        for zone in self.zone_scores:
            self.city.set_zone_state(zone, 0)
        self.card_system.show_card()
        self.particles = ParticleSystem()
        self.warning_played = False
        self.shake_time = 0.0
        self.shake_strength = 0.0
        self.shake_duration = 0.45
        self.title_particles_timer = 0.0
        self.end_particles_timer = 0.0
        self.compat_overlay_elapsed = 0.0
        self.end_cause = None
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

    def trigger_bankruptcy(self, player_index):
        self.players[player_index]["budget"] = 0
        self.bankrupt_player_index = player_index
        self.bankruptcy_timer = 0.0
        self.end_cause = "bankruptcy"
        self.state = "bankruptcy"
        self.shake_strength = 8
        self.shake_time = 1.5
        self.shake_duration = 1.5

    def maybe_warn_low_budget(self, player_index, previous_budget):
        current_budget = self.players[player_index]["budget"]
        if current_budget < 5000 <= previous_budget and not self.critical_budget_warned[player_index]:
            self.play_sound("funds")
            self.critical_budget_warned[player_index] = True

    def apply_choice(self, choice_type):
        card = self.card_system.current_card
        choice = card.eco_choice if choice_type == "eco" else card.quick_choice
        player = self.players[self.current_player]
        choice_cost = card.eco_cost if choice_type == "eco" else card.quick_cost

        previous_budget = player["budget"]
        player["budget"] = max(0, player["budget"] - choice_cost)
        player["decisions"] += 1
        player[choice_type] += 1
        if self.current_player == 0:
            self.player1_carbon_contribution += choice.carbon
        else:
            self.player2_carbon_contribution += choice.carbon

        self.carbon_level = clamp(self.carbon_level + choice.carbon, 0, 100)
        self.city_health = clamp(self.city_health + choice.health, 0, 100)
        self.carbon_meter.set_value(self.carbon_level)

        zone_delta = 1 if choice_type == "eco" else -1
        self.zone_scores[card.zone] += zone_delta
        self.city.set_zone_state(card.zone, self.zone_scores[card.zone])
        effect_center = self.city.zone_centers[card.zone]
        if choice_type == "eco":
            self.particles.spawn_leaf_burst(effect_center, count=20)
            self.particles.spawn_floating_text(
                effect_center[0] - 40, effect_center[1] - 60,
                f"Carbon {choice.carbon:+d}", (74, 222, 128))
            self.particles.spawn_floating_text(
                effect_center[0] - 40, effect_center[1] - 30,
                f"Health {choice.health:+d}", (96, 165, 250))
        else:
            self.particles.spawn_smoke_burst(effect_center, count=22)
            self.particles.spawn_floating_text(
                effect_center[0] - 40, effect_center[1] - 60,
                f"Carbon {choice.carbon:+d}", (239, 68, 68))
            self.particles.spawn_floating_text(
                effect_center[0] - 40, effect_center[1] - 30,
                f"Health {choice.health:+d}", (239, 68, 68))
        if self.carbon_level >= 80:
            self.shake_strength = 8 if self.carbon_level < 100 else 14
            self.shake_time = 0.45
            self.shake_duration = 0.45
        elif choice_type == "quick":
            self.shake_strength = 4
            self.shake_time = 0.18
            self.shake_duration = 0.18

        self.maybe_warn_low_budget(self.current_player, previous_budget)
        if player["budget"] <= 0:
            self.trigger_bankruptcy(self.current_player)
            return

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
        self.end_cause = "rounds_complete"
        if self.carbon_level < 60:
            self.result = {"title": "Green City",
                           "subtitle": "Your city balanced growth and sustainability."}
        elif self.carbon_level < 80:
            self.result = {"title": "Recovering City",
                           "subtitle": "The city survived and has a cleaner future ahead."}
        else:
            self.result = {"title": "City in Crisis",
                           "subtitle": "You finished the rounds, but carbon remains dangerously high."}
        self.state = "end"
        self.particles = ParticleSystem()

    def _check_immediate_end(self):
        if self.carbon_level >= 100:
            self.end_cause = "collapse"
            self.result = {"title": "City Collapsed",
                           "subtitle": "Carbon overload pushed the city past the breaking point."}
            self.state = "end"
            self.particles = ParticleSystem()
            return True
        if self.city_health <= 0:
            self.end_cause = "health"
            self.result = {"title": "Health Crisis",
                           "subtitle": "The city could not withstand the environmental damage."}
            self.state = "end"
            self.particles = ParticleSystem()
            return True
        return False

    def handle_events(self):
        mouse_pos = to_base_pos(pygame.mouse.get_pos())
        for event in pygame.event.get():
            base_event_pos = to_base_pos(event.pos) if hasattr(
                event, "pos") else mouse_pos

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
                elif self.state == "bankruptcy" and event.key == pygame.K_SPACE:
                    self.play_sound("click")
                    self.state = "end"
                    self.end_particles_timer = 0.0
                    self.particles = ParticleSystem()
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

        if self.state == "end":
            self.replay_button.update(mouse_pos)
            self.quit_button.update(mouse_pos)

    def update(self, dt):
        self.title_float += dt
        self.carbon_meter.update(dt)
        self.city.update(dt)
        self.particles.update(dt)

        mouse_pos = to_base_pos(pygame.mouse.get_pos())
        if self.state == "game":
            self.card_system.update(dt, mouse_pos)
        elif self.state == "end":
            self.replay_button.update(mouse_pos)
            self.quit_button.update(mouse_pos)
        elif self.state == "bankruptcy":
            self.bankruptcy_timer += dt

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
            if self.end_cause == "rounds_complete" and self.carbon_level < 80:
                while self.end_particles_timer >= 0.12:
                    self.end_particles_timer -= 0.12
                    self.particles.spawn_celebration(
                        END_PARTICLE_RECT.move(0, -10), count=12)
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
        strength = self.shake_strength * \
            (self.shake_time / max(self.shake_duration, 0.001))
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

        self._draw_title_silhouette(
            surface, 0.18, BASE_H - 142, (24, 30, 56), 232)
        self._draw_title_silhouette(
            surface, 0.33, BASE_H - 102, (16, 22, 42), 186)
        pygame.draw.rect(surface, (20, 24, 38), (0, BASE_H - 86, BASE_W, 86))

        title_y = 160 + math.sin(self.title_float * 2.1) * 5
        draw_shadowed_text(surface, FONT_TITLE, "Carbon Quest",
                           GREEN, (BASE_W // 2, title_y), center=True)
        draw_shadowed_text(surface, FONT_HEADING, "City Builder Challenge",
                           WHITE, (BASE_W // 2, 246), center=True)
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
            bar_alpha = max(
                0, 255 - int((self.compat_overlay_elapsed / 3.0) * 255))
            if bar_alpha > 0:
                bar_rect = pygame.Rect(0, BASE_H - 36, BASE_W, 36)
                overlay = pygame.Surface(bar_rect.size, pygame.SRCALPHA)
                overlay.fill((12, 16, 26, bar_alpha))
                surface.blit(overlay, bar_rect.topleft)
                text = FONT_SMALL.render(
                    "Display not natively supported — running in 720p compatibility mode", True, WHITE)
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
        shake_offset = self.game_offset() if self.state == "game" else (0, 0)
        blink_on = int(self.title_float / 0.5) % 2 == 0
        flash_active = (
            self.state == "bankruptcy"
            and self.bankrupt_player_index is not None
            and self.bankruptcy_timer < 1.5
            and int(self.bankruptcy_timer / 0.25) % 2 == 0
        )

        right_bg = RIGHT_PANEL_RECT.copy()
        pygame.draw.rect(surface, PANEL_DARK, right_bg, border_radius=18)
        draw_alpha_outline(surface, right_bg, (255, 255,
                           255, 20), width=1, border_radius=18)

        draw_alpha_line(surface, (255, 255, 255, 30), (908, 90), (908, 720), 1)

        self.hud.draw(
            surface,
            self.players,
            self.current_player,
            self.current_round_number(),
            self.city_health,
            flash_bankrupt_index=self.bankrupt_player_index,
            flash_active=flash_active,
            blink_on=blink_on,
        )

        city_clip = push_clip(surface, CITY_PANEL_RECT)
        self.city.draw(surface, self.carbon_level, offset=shake_offset)
        self.particles.draw(surface, offset=shake_offset)
        self.draw_turn_indicator(surface)
        surface.set_clip(city_clip)

        self.carbon_meter.draw(surface, warning_active=self.carbon_level >= 80)
        self.card_system.draw(
            surface, self.players[self.current_player]["budget"])

    def draw_turn_indicator(self, surface):
        # fade out after 2.5 seconds
        if self.turn_indicator_timer > 2.5:
            return

        fade = 1.0 - ((self.turn_indicator_timer - 2.0) /
                      0.5) if self.turn_indicator_timer > 2.0 else 1.0

        center_x = CITY_PANEL_RECT.width // 2
        center_y = 200
        player_name = "Player 1" if self.current_player == 0 else "Player 2"
        player_color = GREEN if self.current_player == 0 else (167, 139, 250)
        text = f"{player_name}'s Turn"
        text_width, text_height = FONT_TURN_INDICATOR.size(text)

        pill_rect = pygame.Rect(0, 0, text_width + 40, 52)
        pill_rect.center = (center_x, center_y)
        pill_surface = pygame.Surface(pill_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(pill_surface, (0, 0, 0),
                         pill_surface.get_rect(), border_radius=26)
        pill_surface.set_alpha(int(120 * fade))
        surface.blit(pill_surface, pill_rect.topleft)

        pulse = math.sin(pygame.time.get_ticks() / 400.0)
        alpha_value = int((180 + ((pulse + 1.0) * 0.5 * 75)) * fade)
        text_start_x = center_x - text_width // 2
        dot_radius = int(10 + pulse * 2)

        dot_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(dot_surface, player_color,
                           (16, 16), max(8, min(12, dot_radius)))
        dot_surface.set_alpha(alpha_value)
        surface.blit(dot_surface, (text_start_x - 36, center_y - 16))

        text_surface = FONT_TURN_INDICATOR.render(text, True, player_color)
        text_surface.set_alpha(alpha_value)
        text_rect = text_surface.get_rect(center=(center_x, center_y))
        surface.blit(text_surface, text_rect)

    def winner_summary(self):
        if self.end_cause == "bankruptcy" and self.bankrupt_player_index is not None:
            winner_index = 1 - self.bankrupt_player_index
            return {
                "index": winner_index,
                "name": self.players[winner_index]["name"],
                "reason": "managed the budget better",
                "loser": self.players[self.bankrupt_player_index]["name"],
            }

        contribution_a = self.player1_carbon_contribution
        contribution_b = self.player2_carbon_contribution
        if contribution_a < contribution_b:
            return {"index": 0, "name": "Player 1", "reason": "made greener decisions", "loser": "Player 2"}
        if contribution_b < contribution_a:
            return {"index": 1, "name": "Player 2", "reason": "made greener decisions", "loser": "Player 1"}

        eco_a = self.players[0]["eco"]
        eco_b = self.players[1]["eco"]
        if eco_a > eco_b:
            return {"index": 0, "name": "Player 1", "reason": "made more eco choices", "loser": "Player 2"}
        if eco_b > eco_a:
            return {"index": 1, "name": "Player 2", "reason": "made more eco choices", "loser": "Player 1"}

        if self.players[0]["budget"] > self.players[1]["budget"]:
            return {"index": 0, "name": "Player 1", "reason": "managed funds better", "loser": "Player 2"}
        if self.players[1]["budget"] > self.players[0]["budget"]:
            return {"index": 1, "name": "Player 2", "reason": "managed funds better", "loser": "Player 1"}
        return {"index": None, "name": None, "reason": None, "loser": None}

    def player_eco_rating(self, player):
        ratio = player["eco"] / max(1, player["decisions"])
        if ratio >= 0.75:
            return "🌱 Green Hero", (74, 222, 128)
        if ratio >= 0.5:
            return "♻️ Eco Planner", (163, 230, 53)
        if ratio >= 0.25:
            return "⚠️ City Planner", (251, 191, 36)
        return "☠️ Carbon Criminal", (248, 113, 113)

    def end_screen_summary(self):
        if self.end_cause == "bankruptcy":
            return {
                "title": "BANKRUPT!",
                "title_color": (239, 68, 68),
                "subtitle": "Financial collapse halted the challenge.",
            }
        if self.end_cause == "collapse":
            return {
                "title": "City Collapsed!",
                "title_color": (239, 68, 68),
                "subtitle": "Carbon overload destroyed the city.",
            }
        if self.end_cause == "rounds_complete":
            if self.carbon_level < 60:
                subtitle = "Green City! Outstanding teamwork."
            elif self.carbon_level < 80:
                subtitle = "Recovering City. Room to improve."
            else:
                subtitle = "City in Crisis. Barely made it."
            return {
                "title": "City Survived!",
                "title_color": (34, 197, 94),
                "subtitle": subtitle,
            }
        return {
            "title": "City Collapsed!",
            "title_color": (239, 68, 68),
            "subtitle": "The city could not survive the environmental damage.",
        }

    def draw_bankruptcy_overlay(self):
        surface = self.base_surface
        overlay = pygame.Surface((BASE_W, BASE_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        panel = pygame.Rect(240, 200, 800, 320)
        pygame.draw.rect(surface, (26, 0, 0), panel, border_radius=20)
        draw_alpha_outline(surface, panel, (239, 68, 68),
                           width=3, border_radius=20)

        pulse_scale = 1.0 + math.sin(self.bankruptcy_timer * 4.0) * 0.05
        title_surface = FONT_BANKRUPTCY_TITLE.render(
            "BANKRUPT!", True, (239, 68, 68))
        scaled_size = (
            max(1, int(title_surface.get_width() * pulse_scale)),
            max(1, int(title_surface.get_height() * pulse_scale)),
        )
        pulsed_title = pygame.transform.smoothscale(title_surface, scaled_size)
        title_rect = pulsed_title.get_rect(center=(640, 260))
        shadow = pygame.transform.smoothscale(
            FONT_BANKRUPTCY_TITLE.render("BANKRUPT!", True, (0, 0, 0)), scaled_size)
        surface.blit(shadow, title_rect.move(3, 3))
        surface.blit(pulsed_title, title_rect)

        bankrupt_name = self.players[self.bankrupt_player_index][
            "name"] if self.bankrupt_player_index is not None else "A player"
        draw_shadowed_text(surface, FONT_BANKRUPTCY_LINE,
                           f"{bankrupt_name} has run out of money!", (252, 165, 165), (640, 340), center=True)
        draw_shadowed_text(surface, FONT_BANKRUPTCY_BODY,
                           "The city cannot sustain further investment.", (148, 163, 184), (640, 390), center=True)
        if int(self.bankruptcy_timer / 0.5) % 2 == 0:
            draw_shadowed_text(surface, FONT_BANKRUPTCY_HINT,
                               "Press SPACE to see results", (100, 116, 139), (640, 440), center=True)

    def draw_trophy_icon(self, surface, center):
        cup_color = (255, 215, 0)
        pygame.draw.circle(surface, cup_color, (center[0], center[1] - 10), 14)
        pygame.draw.rect(
            surface, cup_color, (center[0] - 10, center[1] + 2, 20, 18), border_radius=4)
        pygame.draw.rect(
            surface, cup_color, (center[0] - 4, center[1] + 18, 8, 10), border_radius=3)
        pygame.draw.rect(surface, (210, 160, 30),
                         (center[0] - 14, center[1] + 26, 28, 6), border_radius=3)

    def draw_end_button(self, surface, button, base_color, hover_color):
        rect = button.rect
        fill = hover_color if button.hovered else base_color
        if button.hovered:
            glow_rect = rect.inflate(18, 18)
            glow = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(glow, (*base_color, 70),
                             glow.get_rect(), border_radius=30)
            surface.blit(glow, glow_rect.topleft)
        pygame.draw.rect(surface, SHADOW, rect.move(0, 4), border_radius=24)
        pygame.draw.rect(surface, fill, rect, border_radius=24)
        draw_alpha_outline(surface, rect, (255, 255, 255,
                           180), width=2, border_radius=24)
        draw_shadowed_text(surface, FONT_END_BUTTON,
                           button.text, WHITE, rect.center, center=True)

    def draw_end_player_card(self, surface, rect, player, contribution, winner_index, player_index):
        is_draw = winner_index is None
        is_winner = winner_index == player_index
        is_bankrupt = self.end_cause == "bankruptcy" and self.bankrupt_player_index == player_index
        border_color = (148, 163, 184) if is_draw else (
            34, 197, 94) if is_winner else (239, 68, 68)
        fill_color = (26, 0, 0) if is_bankrupt else (15, 23, 42)

        if is_winner:
            for inflate_by, alpha in ((10, 72), (20, 42), (30, 22)):
                glow_rect = rect.inflate(inflate_by, inflate_by)
                draw_alpha_outline(
                    surface, glow_rect, (*border_color, alpha), width=1, border_radius=16)

        pygame.draw.rect(surface, fill_color, rect, border_radius=12)
        draw_alpha_outline(surface, rect, border_color,
                           width=2, border_radius=12)
        clip_before = push_clip(surface, rect)

        draw_shadowed_text(surface, FONT_END_CARD_TITLE,
                           player["name"], WHITE, (rect.x + 20, rect.y + 18))
        if is_bankrupt:
            badge_rect = pygame.Rect(rect.right - 146, rect.y + 14, 126, 26)
            pygame.draw.rect(surface, (127, 29, 29),
                             badge_rect, border_radius=13)
            draw_alpha_outline(surface, badge_rect,
                               (239, 68, 68), width=1, border_radius=13)
            draw_shadowed_text(surface, FONT_HUD_WARNING, "💸 BANKRUPT",
                               (254, 202, 202), badge_rect.center, center=True, shadow_offset=1)

        draw_shadowed_text(surface, FONT_END_CARD_SMALL,
                           f"Total decisions: {player['decisions']}", LIGHT_GRAY, (rect.x + 20, rect.y + 56))
        draw_shadowed_text(surface, FONT_END_CARD_SMALL,
                           f"Eco choices: {player['eco']}", GREEN, (rect.x + 20, rect.y + 82))
        draw_shadowed_text(surface, FONT_END_CARD_SMALL,
                           f"Quick choices: {player['quick']}", RED, (rect.x + 20, rect.y + 108))

        if contribution < 0:
            impact_color = GREEN
        elif contribution > 0:
            impact_color = RED
        else:
            impact_color = LIGHT_GRAY
        draw_shadowed_text(
            surface,
            FONT_END_CARD_SMALL,
            f"Carbon Impact: {contribution:+d}",
            impact_color,
            (rect.x + 20, rect.y + 134),
        )
        if is_bankrupt:
            budget_text = "$0 — Out of funds"
            budget_text_color = (239, 68, 68)
        elif self.end_cause == "bankruptcy" and is_winner:
            budget_text = f"{format_budget(player['budget'])} remaining"
            budget_text_color = (34, 197, 94)
        else:
            budget_text = f"Final Budget: {format_budget(player['budget'])}"
            budget_text_color = budget_color(player["budget"])
        draw_shadowed_text(surface, FONT_END_CARD_SMALL, budget_text,
                           budget_text_color, (rect.x + 20, rect.y + 158))
        surface.set_clip(clip_before)

    def draw_end(self):
        surface = self.base_surface
        surface.fill(BG_COLOR)
        summary = self.end_screen_summary()
        winner = self.winner_summary()

        panel = pygame.Rect(70, 40, 1140, 668)
        border_width = 3 if self.end_cause == "bankruptcy" else 2
        border_color = (239, 68, 68) if self.end_cause == "bankruptcy" else (
            *summary["title_color"], 255)
        draw_panel(surface, panel, PANEL_COLOR, border_color,
                   radius=26, border_width=border_width)
        clip_before = push_clip(surface, panel)

        glow_overlay = pygame.Surface(panel.size, pygame.SRCALPHA)
        pygame.draw.rect(
            glow_overlay, (*summary["title_color"], 22), glow_overlay.get_rect(), border_radius=26)
        surface.blit(glow_overlay, panel.topleft)

        title_font = FONT_BANKRUPT_END if self.end_cause == "bankruptcy" else FONT_END_TITLE
        draw_shadowed_text(
            surface, title_font, summary["title"], summary["title_color"], (BASE_W // 2, 118), center=True)
        draw_shadowed_text(surface, FONT_END_SUBTITLE,
                           summary["subtitle"], WHITE, (BASE_W // 2, 168), center=True)
        if self.end_cause == "collapse" and winner["name"]:
            draw_shadowed_text(surface, FONT_END_SUBTITLE,
                               f"But {winner['name']} played better!", YELLOW, (BASE_W // 2, 212), center=True)

        banner_rect = pygame.Rect((BASE_W - 700) // 2, 280, 700, 100)
        if winner["name"]:
            if self.end_cause == "bankruptcy":
                pygame.draw.rect(surface, (20, 83, 45),
                                 banner_rect, border_radius=16)
                draw_alpha_outline(surface, banner_rect,
                                   (34, 197, 94), width=2, border_radius=16)
                draw_shadowed_text(surface, pygame.font.SysFont(
                    "Arial", 36, bold=True), f"🏆 {winner['name']} Wins!", WHITE, (banner_rect.centerx, banner_rect.y + 30), center=True)
                draw_shadowed_text(surface, FONT_END_SUBTITLE, f"{winner['loser']} ran out of money!", (
                    252, 165, 165), (banner_rect.centerx, banner_rect.y + 70), center=True)
            else:
                draw_gradient_rect(
                    surface, banner_rect, (22, 101, 52), (21, 128, 61), border_radius=16)
                draw_alpha_outline(surface, banner_rect,
                                   (74, 222, 128), width=2, border_radius=16)
                self.draw_trophy_icon(surface, (370, 330))
                draw_shadowed_text(surface, FONT_END_BANNER, f"🏆 {winner['name']} Wins!", WHITE, (
                    banner_rect.centerx, banner_rect.y + 32), center=True)
                draw_shadowed_text(
                    surface,
                    FONT_END_BANNER_SUB,
                    f"{winner['name']} {winner['reason']} this round",
                    (187, 247, 208),
                    (banner_rect.centerx, banner_rect.y + 70),
                    center=True,
                )
        else:
            pygame.draw.rect(surface, (30, 41, 59),
                             banner_rect, border_radius=16)
            draw_alpha_outline(surface, banner_rect,
                               (148, 163, 184), width=2, border_radius=16)
            draw_shadowed_text(surface, FONT_END_BANNER, "🤝 It's a Draw!", (
                226, 232, 240), (banner_rect.centerx, banner_rect.y + 32), center=True)
            draw_shadowed_text(
                surface,
                FONT_END_BANNER_SUB,
                "Both players performed equally",
                (148, 163, 184),
                (banner_rect.centerx, banner_rect.y + 70),
                center=True,
            )

        player_cards = [
            (pygame.Rect(180, 400, 420, 180),
             self.players[0], self.player1_carbon_contribution, 0),
            (pygame.Rect(660, 400, 420, 180),
             self.players[1], self.player2_carbon_contribution, 1),
        ]
        for rect, player, contribution, index in player_cards:
            self.draw_end_player_card(
                surface, rect, player, contribution, winner["index"], index)
            rating_text, rating_color = self.player_eco_rating(player)
            draw_shadowed_text(surface, FONT_END_CARD_BODY, rating_text,
                               rating_color, (rect.centerx, 600), center=True)

        self.replay_button.set_rect((460, 660, 160, 48))
        self.quit_button.set_rect((660, 660, 160, 48))
        self.draw_end_button(surface, self.replay_button,
                             (22, 163, 74), (34, 197, 94))
        self.draw_end_button(surface, self.quit_button,
                             (185, 28, 28), (220, 38, 38))
        self.particles.draw(surface)
        surface.set_clip(clip_before)

    def carbon_level_color(self):
        value = self.carbon_level
        if value < 50:
            return lerp_color(GREEN, YELLOW, value / 50.0)
        return lerp_color(YELLOW, RED, (value - 50) / 50.0)

    def draw_resolution_debug(self):
        fps_surface = FONT_TINY.render(
            f"FPS: {int(self.clock.get_fps())}", True, WHITE)
        fps_surface.set_alpha(85)
        self.base_surface.blit(fps_surface, (8, 708))

        if not self.show_resolution_debug:
            return
        text = f"{RENDER_W}x{RENDER_H}" + (" [COMPAT]" if COMPAT_MODE else "")
        debug_surface = FONT_TINY.render(text, True, WHITE)
        debug_surface.set_alpha(68)
        debug_rect = debug_surface.get_rect(
            bottomright=(BASE_W - 10, BASE_H - 8))
        self.base_surface.blit(debug_surface, debug_rect)

    def present_frame(self):
        source_surface = self.base_surface
        if self.state == "bankruptcy" and self.shake_time > 0:
            shake_surface = pygame.Surface((BASE_W, BASE_H))
            shake_surface.fill(BG_COLOR)
            shake_px = max(1, int(self.shake_strength *
                           (self.shake_time / max(self.shake_duration, 0.001))))
            shake_surface.blit(self.base_surface, (random.randint(-shake_px,
                               shake_px), random.randint(-shake_px, shake_px)))
            source_surface = shake_surface
        if RENDER_W == BASE_W and RENDER_H == BASE_H:
            self.screen.blit(source_surface, (0, 0))
        else:
            scaled = pygame.transform.smoothscale(
                source_surface, (RENDER_W, RENDER_H))
            self.screen.blit(scaled, (0, 0))
        pygame.display.flip()

    def draw(self):
        self.base_surface.fill(BG_COLOR)
        if self.state == "title":
            self.draw_title()
        elif self.state == "game":
            self.draw_game()
        elif self.state == "bankruptcy":
            self.draw_game()
            self.draw_bankruptcy_overlay()
        else:
            self.draw_end()
        self.draw_resolution_debug()
        self.present_frame()

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.last_dt = dt
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()

# To build: pyinstaller --onefile --noconsole main.py
