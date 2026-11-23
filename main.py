#!/usr/bin/env python3
"""News23 v5: one-page newspaper of Monday 23 November 2026.

Draws a 1024x1024 PNG with a hand-built 5x7 pixel font, using only the
Python standard library. No network, no randomness, no timestamps in the
output: two runs produce byte-identical files.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (246, 241, 228)
INK = (20, 20, 20)
RED = (200, 30, 30)
BLUE = (168, 205, 232)
GREEN = (46, 125, 62)
GREY = (110, 105, 95)
WHITE = (255, 255, 255)

# 5x7 pixel glyphs, written out by hand. Each glyph is 7 rows of 5 bits.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
}

BLANK = ("00000", "00000", "00000", "00000", "00000", "00000", "00000")


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        for i in range(w * h):
            self.px[i * 3] = bg[0]
            self.px[i * 3 + 1] = bg[1]
            self.px[i * 3 + 2] = bg[2]

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x, y, w, color, thick=1):
        for t in range(thick):
            for xx in range(x, x + w):
                self.set(xx, y + t, color)

    def vline(self, x, y, h, color, thick=1):
        for t in range(thick):
            for yy in range(y, y + h):
                self.set(x + t, yy, color)

    def rect_outline(self, x, y, w, h, color, thick=1):
        self.hline(x, y, w, color, thick)
        self.hline(x, y + h - thick, w, color, thick)
        self.vline(x, y, h, color, thick)
        self.vline(x + w - thick, y, h, color, thick)

    def line(self, x0, y0, x1, y1, color):
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        for i in range(steps + 1):
            x = x0 + dx * i // steps
            y = y0 + dy * i // steps
            self.set(x, y, color)

    def thick_line(self, x0, y0, x1, y1, color, thick):
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        half = thick // 2
        for i in range(steps + 1):
            x = x0 + dx * i // steps
            y = y0 + dy * i // steps
            self.fill_rect(x - half, y - half, thick, thick, color)

    def fill_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = math.isqrt(r * r - dy * dy)
            self.hline(cx - dx, cy + dy, dx * 2 + 1, color)

    def circle_outline(self, cx, cy, r, color, thick=2):
        for dy in range(-r, r + 1):
            dx = math.isqrt(r * r - dy * dy)
            for t in range(thick):
                d2 = math.isqrt(max(r * r - dy * dy, 0))
                self.set(cx - d2, cy + dy, color)
                self.set(cx + d2, cy + dy, color)

    def fill_polygon(self, pts, color, clip=None):
        # Scanline fill; clip is (cx, cy, r) circle or None.
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            nodes = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    x = x0 + (y - y0) * (x1 - x0) // (y1 - y0)
                    nodes.append(x)
            nodes.sort()
            for k in range(0, len(nodes) - 1, 2):
                for x in range(nodes[k], nodes[k + 1] + 1):
                    if clip is not None:
                        cx, cy, r = clip
                        if (x - cx) * (x - cx) + (y - cy) * (y - cy) > r * r:
                            continue
                    self.set(x, y, color)

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale if s else 0

    def draw_text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, BLANK)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale
        return cx

    def draw_text_center(self, cx, y, s, scale, color):
        w = self.text_width(s, scale)
        return self.draw_text(cx - w // 2, y, s, scale, color)

    def wrap(self, text, scale, max_w):
        words = text.split(" ")
        lines = []
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if self.text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


def draw_ship(cv, x, y, color):
    cv.fill_polygon([(x + 2, y + 26), (x + 34, y + 26), (x + 29, y + 37),
                     (x + 7, y + 37)], color)
    cv.vline(x + 17, y + 6, 20, color, 2)
    cv.fill_polygon([(x + 19, y + 6), (x + 30, y + 10), (x + 19, y + 14)],
                    RED)
    cv.hline(x + 2, y + 40, 32, color, 1)

def draw_missile(cv, x, y, color):
    cv.thick_line(x + 6, y + 34, x + 28, y + 10, color, 3)
    cv.fill_polygon([(x + 28, y + 4), (x + 34, y + 10), (x + 26, y + 12)],
                    RED)
    cv.fill_polygon([(x + 6, y + 34), (x + 12, y + 30), (x + 10, y + 38)],
                    color)
    cv.fill_rect(x + 30, y + 30, 4, 4, RED)

def draw_factory(cv, x, y, color):
    cv.fill_rect(x + 2, y + 24, 32, 14, color)
    cv.fill_rect(x + 4, y + 8, 6, 16, color)
    cv.fill_rect(x + 14, y + 14, 6, 10, color)
    cv.fill_rect(x + 24, y + 18, 5, 5, RED)
    cv.fill_rect(x + 8, y + 28, 4, 4, PAPER)
    cv.fill_rect(x + 16, y + 28, 4, 4, PAPER)
    cv.fill_rect(x + 24, y + 28, 4, 4, PAPER)
    cv.fill_rect(x + 6, y + 2, 4, 4, GREY)
    cv.fill_rect(x + 12, y + 0, 3, 3, GREY)

def draw_building(cv, x, y, color):
    cv.fill_rect(x + 6, y + 8, 26, 30, color)
    for r in range(3):
        for c in range(4):
            cv.fill_rect(x + 10 + c * 6, y + 12 + r * 8, 3, 4, PAPER)
    cv.fill_rect(x + 2, y + 34, 34, 4, RED)

def draw_ballot(cv, x, y, color):
    cv.fill_rect(x + 4, y + 16, 30, 20, color)
    cv.fill_rect(x + 12, y + 12, 14, 4, INK)
    cv.fill_rect(x + 8, y + 20, 22, 12, PAPER)
    cv.thick_line(x + 11, y + 26, x + 16, y + 30, RED, 3)
    cv.thick_line(x + 16, y + 30, x + 27, y + 22, RED, 3)

def draw_star(cv, x, y, color):
    cx, cy = x + 19, y + 20
    outer, inner = 17, 7
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = outer if i % 2 == 0 else inner
        pts.append((int(cx + r * math.cos(ang)), int(cy + r * math.sin(ang))))
    cv.fill_polygon(pts, color)


ICONS = {
    "ship": draw_ship,
    "missile": draw_missile,
    "factory": draw_factory,
    "building": draw_building,
    "ballot": draw_ballot,
    "star": draw_star,
}

CARDS = [
    ("UKRAINE", "ship",
     "UKRAINE HITS RUSSIAN WARSHIP OFF LIBYA",
     "7 SEA DRONES STRUCK THE MERKURY OFF BENGHAZI. KYIV CLAIMS IT SANK."),
    ("GULF", "missile",
     "IRAN HITS BAHRAIN, TANKERS HIT",
     "MISSILES AND DRONES HIT US BASES. 2 TANKERS HIT. ECHOES TODAY."),
    ("INDONESIA", "factory",
     "24 BODY BAGS AT CIKANDE",
     "THE SEARCH RESUMES TODAY AT THE BURNT CANDY FACTORY. 24 OUT. 34 MISSING."),
    ("UKRAINE", "building",
     "DRONE FLATTENS FLATS IN DYMER",
     "A RUSSIAN DRONE DESTROYED A FIVE-STOREY BLOCK. 14 MISSING AS RESCUERS DIG."),
    ("SOUTH KOREA", "ballot",
     "MINISTER QUITS OVER EXAM CHAOS",
     "EDUCATION CHIEF QUITS AFTER AN AI CHEATING SCANDAL SHOOK THE NATIONAL EXAM."),
    ("MEXICO", "star",
     "EL CHAPO ISIDRO CAUGHT",
     "FBI MOST WANTED. $5 MILLION REWARD. CAUGHT IN A SINALOA RAID. 11 KILLED."),
]


def draw_globe(cv, cx, cy, r):
    cv.fill_circle(cx, cy, r, BLUE)
    clip = (cx, cy, r - 2)
    cv.fill_polygon([(cx - 88, cy - 62), (cx - 30, cy - 78), (cx - 8, cy - 40),
                     (cx - 52, cy - 18), (cx - 92, cy - 30)], GREEN, clip)
    cv.fill_polygon([(cx + 18, cy - 70), (cx + 84, cy - 58), (cx + 66, cy - 8),
                     (cx + 30, cy - 22), (cx + 8, cy - 52)], GREEN, clip)
    cv.fill_polygon([(cx - 80, cy + 22), (cx - 20, cy + 14), (cx - 6, cy + 48),
                     (cx - 58, cy + 66), (cx - 90, cy + 44)], GREEN, clip)
    cv.fill_polygon([(cx + 26, cy + 26), (cx + 82, cy + 18), (cx + 92, cy + 62),
                     (cx + 52, cy + 78), (cx + 22, cy + 56)], GREEN, clip)
    # Latitude / longitude guide lines, faint.
    cv.hline(cx - r + 4, cy, r * 2 - 8, (140, 185, 215), 1)
    cv.vline(cx, cy - r + 4, r * 2 - 8, (140, 185, 215), 1)
    # Red crack, top to bottom.
    crack = [(cx + 4, cy - r + 6), (cx - 8, cy - 58), (cx + 10, cy - 18),
             (cx - 6, cy + 24), (cx + 12, cy + 62), (cx - 2, cy + r - 6)]
    for a, b in zip(crack, crack[1:]):
        cv.thick_line(a[0], a[1], b[0], b[1], RED, 5)
    cv.circle_outline(cx, cy, r, INK, 3)
    # Red NO DEAL banner across the middle.
    bx, by, bw, bh = cx - 112, cy - 19, 224, 38
    cv.fill_rect(bx, by, bw, bh, RED)
    cv.rect_outline(bx, by, bw, bh, INK, 2)
    cv.draw_text_center(cx, by + 7, "NO DEAL", 4, WHITE)


def draw_icon(cv, name, x, y):
    # Render the icon on a small scratch canvas, then blit it at 0.7 scale
    # so it sits clear of the headline's first line.
    tmp = Canvas(40, 42, PAPER)
    ICONS[name](tmp, 0, 0, INK)
    for py in range(42):
        for px in range(40):
            i = (py * 40 + px) * 3
            if tmp.px[i:i + 3] != bytes(PAPER):
                cv.set(x + px * 7 // 10, y + py * 7 // 10,
                       tuple(tmp.px[i:i + 3]))


def draw_card(cv, x, y, w, h, label, icon, headline, body):
    cv.rect_outline(x, y, w, h, INK, 2)
    cv.draw_text(x + 12, y + 10, label, 2, RED)
    draw_icon(cv, icon, x + w - 40, y + 2)
    head_lines = cv.wrap(headline, 3, w - 24)
    hy = y + 32
    for line in head_lines:
        cv.draw_text(x + 12, hy, line, 3, INK)
        hy += 23
    # Body gets whatever lines fit in the remaining space.
    room = y + h - 8 - (hy + 6)
    max_lines = max(room // 15, 1)
    body_lines = cv.wrap(body, 2, w - 24)[:max_lines]
    by = hy + 6
    for line in body_lines:
        cv.draw_text(x + 12, by, line, 2, INK)
        by += 15


def build():
    cv = Canvas(W, H, PAPER)
    cv.rect_outline(10, 10, W - 20, H - 20, INK, 3)

    # Masthead.
    cv.draw_text_center(W // 2, 24, "THE WORLD TODAY", 9, INK)
    cv.hline(24, 100, W - 48, INK, 2)
    cv.hline(24, 106, W - 48, INK, 2)

    # Dateline strip.
    cv.draw_text(24, 114, "ONE DAY, ONE PAGE", 2, INK)
    cv.draw_text_center(W // 2, 112, "MONDAY 23 NOVEMBER 2026", 3, RED)
    right = "ANTALYA - SEOUL"
    cv.draw_text(W - 24 - cv.text_width(right, 2), 114, right, 2, INK)
    cv.hline(24, 142, W - 48, INK, 2)

    # Hero, left.
    cv.draw_text(24, 156, "CLIMATE - COP31, ANTALYA", 2, RED)
    hero = cv.wrap("COP31 ENDS WITH NO DEAL", 6, 640)
    hy = 178
    for line in hero:
        cv.draw_text(24, hy, line, 6, INK)
        hy += 46
    body = cv.wrap(
        "TWO WEEKS OF TALKS, TWO DAYS OVERTIME - AND NO DEAL. "
        "THE EU AND 130 NATIONS REJECTED THE FINAL DRAFT. "
        "IT DID NOT NAME FOSSIL FUELS.", 3, 640)
    by = hy + 6
    for line in body:
        cv.draw_text(24, by, line, 3, INK)
        by += 26
    cv.draw_text(24, by + 6, '"WE DID ALL THAT WE COULD." - MURAT KURUM',
                 2, INK)

    # Globe, right.
    draw_globe(cv, 836, 275, 112)
    cv.draw_text_center(836, 400, "THE PACT THAT NEVER WAS", 2, GREY)

    # Day in numbers.
    cv.rect_outline(24, 428, 536, 104, INK, 2)
    cv.draw_text(36, 438, "THE DAY IN NUMBERS", 2, RED)
    for i, line in enumerate(("2 WEEKS OF TALKS - 0 DEALS",
                              "7 SEA DRONES, 1 WARSHIP",
                              "34 MISSING IN CIKANDE")):
        cv.draw_text(36, 462 + i * 24, line, 3, INK)

    # Six story cards, 3 columns x 2 rows.
    col_w, row_h, gap = 317, 160, 12
    for i, (label, icon, headline, body_text) in enumerate(CARDS):
        cx = 24 + (i % 3) * (col_w + gap)
        cy = 544 + (i // 3) * (row_h + gap)
        draw_card(cv, cx, cy, col_w, row_h, label, icon, headline, body_text)

    # Also today.
    cv.draw_text(24, 888, "ALSO TODAY", 3, RED)
    cv.draw_text(24, 916, "BELGIUM", 2, RED)
    cv.draw_text(24, 934, "ANTI-AUSTERITY STRIKE HALTS TRANSPORT.", 2, INK)
    cv.draw_text(530, 916, "CLEAN POWER PLEDGE", 2, RED)
    cv.draw_text(530, 934, "ABOUT 90 NATIONS BACK 35% BY 2035.", 2, INK)

    # Footer.
    cv.hline(24, 956, W - 48, INK, 2)
    cv.draw_text_center(W // 2, 966, "SOURCES: REUTERS, AP, AFP, AL JAZEERA, BBC",
                        2, GREY)
    cv.draw_text_center(
        W // 2, 986,
        "ALL STORIES FIRST REPORTED ON 23 NOV 2026 IN AT LEAST ONE TIME ZONE",
        2, GREY)
    return cv


def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    write_png(cv, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
