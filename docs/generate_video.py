"""
NutriAgent – Promotional Video Generator
Produces docs/NutriAgent_Testimonial.mp4 at 1280×720, 30 fps.
Requires: pillow, opencv-python-headless, numpy (all pre-installed)
"""

import os
import math
import sys
import textwrap
from pathlib import Path

# ── pillow ──────────────────────────────────────────────────────────────────
from PIL import Image, ImageDraw, ImageFont

# ── opencv ──────────────────────────────────────────────────────────────────
import cv2
import numpy as np

# ── config ──────────────────────────────────────────────────────────────────
W, H = 1280, 720
FPS = 30
OUTPUT = Path(__file__).parent / "NutriAgent_Testimonial.mp4"

# ── colours (match Tailwind config) ─────────────────────────────────────────
C = {
    "bg":        (249, 250, 251),   # gray-50
    "white":     (255, 255, 255),
    "primary":   (16, 185, 129),    # #10b981
    "primary_d": (5, 150, 105),     # #059669
    "primary_dk":(4, 120, 87),      # #047857
    "primary_bg":(236, 253, 245),   # #ecfdf5
    "primary_b": (167, 243, 208),   # #a7f3d0
    "accent_bg": (239, 246, 255),   # #eff6ff
    "gray_100":  (243, 244, 246),
    "gray_200":  (229, 231, 235),
    "gray_300":  (209, 213, 219),
    "gray_400":  (156, 163, 175),
    "gray_500":  (107, 114, 128),
    "gray_600":  (75, 85, 99),
    "gray_700":  (55, 65, 81),
    "gray_800":  (31, 41, 55),
    "gray_900":  (17, 24, 39),
    "border":    (243, 244, 246),
    "blue":      (59, 130, 246),
    "blue_bg":   (219, 234, 254),
    "amber":     (245, 158, 11),
    "amber_bg":  (255, 251, 235),
    "amber_b":   (253, 230, 138),
    "pink":      (236, 72, 153),
    "pink_bg":   (252, 231, 243),
    "purple_bg": (245, 243, 255),
    "purple_b":  (221, 214, 254),
    "green_bg":  (240, 253, 244),
    "red_bg":    (254, 242, 242),
    "red":       (239, 68, 68),
    "dark_green":(6, 78, 59),       # #064e3b
    "mid_green": (6, 95, 70),
    "deep_green":(4, 78, 59),
    "green_text":(6, 95, 70),       # #065f46
    "streak_bg": (255, 251, 235),
    "streak_fg": (180, 83, 9),
    "result_bg": (236, 253, 245),
    "result_b":  (167, 243, 208),
    "sidebar_w": 220,
}

def try_font(size, bold=False):
    """Return a PIL font; falls back gracefully."""
    candidates = []
    if bold:
        candidates = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        candidates = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()

# Pre-load common fonts
F = {}
for sz in [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 22, 24, 28, 32, 40, 48, 52, 56]:
    F[sz]  = try_font(sz, bold=False)
    F[f"{sz}b"] = try_font(sz, bold=True)

def new_frame(bg=None):
    if bg is None:
        bg = C["bg"]
    img = Image.new("RGB", (W, H), bg)
    return img, ImageDraw.Draw(img)

def rrect(draw, xy, r, fill, outline=None, width=1):
    """Rounded rectangle."""
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill,
                            outline=outline, width=width)

def text_c(draw, cx, y, txt, font, fill):
    """Centered text."""
    bb = draw.textbbox((0,0), txt, font=font)
    tw = bb[2] - bb[0]
    draw.text((cx - tw//2, y), txt, font=font, fill=fill)

def pill(draw, cx, y, txt, font, fg, bg, border=None, pad_x=16, pad_y=7):
    bb = draw.textbbox((0,0), txt, font=font)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    x0 = cx - tw//2 - pad_x
    x1 = cx + tw//2 + pad_x
    y0 = y
    y1 = y + th + pad_y*2
    rrect(draw, [x0, y0, x1, y1], 999, bg, border, 1)
    draw.text((x0+pad_x, y0+pad_y), txt, font=font, fill=fg)
    return y1

def leaf_icon(draw, cx, cy, size=18, col=(255,255,255)):
    """Draw a simple leaf shape."""
    s = size // 2
    pts = [(cx, cy-s), (cx+s, cy), (cx, cy+s//2), (cx-s//2, cy)]
    draw.polygon(pts, fill=col)
    draw.line([(cx, cy-s), (cx, cy+s//2)], fill=(255,255,255,180), width=1)

def sparkle_icon(draw, cx, cy, size=14, col=(255,255,255)):
    s = size // 2
    for angle in [0, 90, 45, 135]:
        rad = math.radians(angle)
        x1 = cx + int(s * math.cos(rad))
        y1 = cy + int(s * math.sin(rad))
        x2 = cx - int(s * math.cos(rad))
        y2 = cy - int(s * math.sin(rad))
        draw.line([(x1,y1),(x2,y2)], fill=col, width=2)
    draw.ellipse([cx-2, cy-2, cx+2, cy+2], fill=col)

def send_icon(draw, cx, cy, size=14, col=(255,255,255)):
    s = size // 2
    pts = [(cx-s, cy-s), (cx+s, cy), (cx-s, cy+s), (cx-s+4, cy)]
    draw.polygon(pts, fill=col)

def draw_logo_icon(draw, x, y, size=32, radius=8):
    rrect(draw, [x, y, x+size, y+size], radius, C["primary"])
    cx, cy = x+size//2, y+size//2
    leaf_icon(draw, cx, cy, size//2, (255,255,255))

def draw_ring(draw, cx, cy, r, stroke, pct, color, bg_color, stroke_w=10):
    """Draw a progress ring using polygon approximation."""
    segs = 100
    # Background ring
    pts_bg = []
    for i in range(segs+1):
        a = math.radians(i * 360 / segs - 90)
        pts_bg.append((cx + r*math.cos(a), cy + r*math.sin(a)))
    # Draw thick bg circle via concentric drawing
    for off in range(-stroke_w//2, stroke_w//2+1):
        rv = r + off
        if rv > 0:
            bbox = [cx-rv, cy-rv, cx+rv, cy+rv]
            draw.arc(bbox, 0, 360, fill=bg_color, width=1)
    # Foreground arc
    end_deg = pct * 360 - 90
    for off in range(-stroke_w//2, stroke_w//2+1):
        rv = r + off
        if rv > 0:
            bbox = [cx-rv, cy-rv, cx+rv, cy+rv]
            draw.arc(bbox, -90, end_deg, fill=color, width=1)

def progress_ring(img, draw, cx, cy, outer_r, inner_r, pct, color, bg_color):
    """Rasterise a thick ring using a mask."""
    # Use a larger temp image for anti-alias
    scale = 4
    sz = outer_r * 2 * scale + 8*scale
    tmp = Image.new("RGBA", (sz, sz), (0,0,0,0))
    td  = ImageDraw.Draw(tmp)
    tcx, tcy = sz//2, sz//2
    ro = outer_r * scale
    ri = inner_r * scale
    # bg donut
    td.ellipse([tcx-ro, tcy-ro, tcx+ro, tcy+ro], fill=(*bg_color, 255))
    td.ellipse([tcx-ri, tcy-ri, tcx+ri, tcy+ri], fill=(0,0,0,0))
    # fg arc
    if pct > 0:
        p = min(pct, 1.0)
        end_a = -90 + p * 360
        td.pieslice([tcx-ro, tcy-ro, tcx+ro, tcy+ro],
                    start=-90, end=end_a, fill=(*color, 255))
        td.ellipse([tcx-ri, tcy-ri, tcx+ri, tcy+ri], fill=(0,0,0,0))
    # Resize back
    disp = sz // scale
    tmp = tmp.resize((disp, disp), Image.LANCZOS)
    img.paste(tmp, (cx - disp//2, cy - disp//2), tmp)

def sidebar(draw, active_idx):
    """Draw the sidebar navigation."""
    sw = C["sidebar_w"]
    draw.rectangle([0, 0, sw, H], fill=C["white"])
    draw.line([sw, 0, sw, H], fill=C["gray_100"], width=1)
    # Logo
    draw.line([0, 52, sw, 52], fill=C["gray_100"], width=1)
    draw_logo_icon(draw, 18, 14, 28, 7)
    draw.text((54, 21), "NutriAgent", font=F["16b"], fill=C["gray_800"])

    icons_labels = [
        ("Dashboard", "⌂"),
        ("Log Meal",  "≡"),
        ("Diet Plan", "▦"),
        ("Chat",      "◉"),
        ("Profile",   "○"),
    ]
    for i, (label, icon) in enumerate(icons_labels):
        y = 68 + i * 38
        active = (i == active_idx)
        if active:
            rrect(draw, [8, y-2, sw-8, y+28], 10, C["primary_bg"])
            fg = C["primary_dk"]
        else:
            fg = C["gray_600"]
        draw.text((20, y+4), icon, font=F[16], fill=fg)
        draw.text((42, y+4), label, font=F["13b"] if active else F[13], fill=fg)

def caption(img, draw, text, y=None):
    if y is None:
        y = H - 56
    font = F[16]
    bb = draw.textbbox((0,0), text, font=font)
    tw = bb[2]-bb[0]
    pad_x, pad_y = 28, 10
    x0 = W//2 - tw//2 - pad_x
    x1 = W//2 + tw//2 + pad_x
    # Semi-transparent pill — draw with opacity trick
    overlay = Image.new("RGBA", img.size, (0,0,0,0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle([x0, y, x1, y+bb[3]-bb[1]+pad_y*2], 999,
                          fill=(6, 78, 59, 230))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay).convert("RGB")
    d2 = ImageDraw.Draw(img)
    d2.text((x0+pad_x, y+pad_y), text, font=font, fill=(255,255,255))
    return img

def card(draw, x, y, w, h, r=14):
    rrect(draw, [x, y, x+w, y+h], r, C["white"],
          outline=C["border"], width=1)

# ─────────────────────────────────────────────────────────────────────────────
# SCENE GENERATORS  (each returns a list of PIL Images = frames for that scene)
# ─────────────────────────────────────────────────────────────────────────────

def fade_in_out(frames_list, fade_frames=9):
    """Add fade-in and fade-out to a frame list."""
    result = []
    n = len(frames_list)
    for i, frm in enumerate(frames_list):
        alpha = 1.0
        if i < fade_frames:
            alpha = i / fade_frames
        elif i >= n - fade_frames:
            alpha = (n - 1 - i) / fade_frames
        if alpha < 1.0:
            black = Image.new("RGB", frm.size, (0,0,0))
            frm = Image.blend(black, frm, alpha)
        result.append(frm)
    return result

def make_frames(draw_fn, duration_s, fps=FPS):
    """Call draw_fn(t) -> Image for t in [0, duration_s]."""
    total = int(duration_s * fps)
    frames = []
    for i in range(total):
        t = i / fps
        frames.append(draw_fn(t))
    return frames


# ── SCENE 1: Title ───────────────────────────────────────────────────────────
def scene_title(t):
    img = Image.new("RGB", (W, H))
    # Gradient bg
    for y in range(H):
        r1,g1,b1 = 236,253,245
        r2,g2,b2 = 239,246,255
        frac = y/H
        px = (int(r1*(1-frac)+r2*frac), int(g1*(1-frac)+g2*frac), int(b1*(1-frac)+b2*frac))
        for x in range(W):
            img.putpixel((x,y), px)  # slow but fine for bg gradient
    # Faster: create gradient as numpy
    grad = np.zeros((H, W, 3), dtype=np.uint8)
    for row in range(H):
        f = row / H
        grad[row,:] = [int(236*(1-f)+239*f), int(253*(1-f)+246*f), int(245*(1-f)+255*f)]
    img = Image.fromarray(grad)
    draw = ImageDraw.Draw(img)

    # Animate: slide up
    slide = max(0, min(1, t / 0.8))
    base_y = int(H//2 - 140 + (1-slide)*60)

    # Logo icon
    ix = W//2 - 36
    rrect(draw, [ix, base_y, ix+72, base_y+72], 18, C["primary"])
    leaf_icon(draw, W//2, base_y+36, 32, (255,255,255))

    # Title
    title = "NutriAgent"
    text_c(draw, W//2, base_y+86, title, F["52b"], C["dark_green"])
    text_c(draw, W//2, base_y+148, "AI-Powered Multi-Agent Nutrition Assistant",
           F["22b"], C["primary_d"])
    text_c(draw, W//2, base_y+184,
           "Personalized diet plans · Meal logging · Health advisory · AI chat",
           F[16], C["gray_500"])

    # Pills
    if t > 0.9:
        pill_alpha = min(1.0, (t-0.9)/0.4)
        pills = ["🤖  IBM Granite LLM", "🧠  RAG · ChromaDB", "⚛️  React + FastAPI"]
        total_w = 0
        pill_data = []
        for p in pills:
            bb = draw.textbbox((0,0), p, font=F[13])
            pw = bb[2]-bb[0] + 32
            pill_data.append(pw)
            total_w += pw + 12
        sx = W//2 - total_w//2
        py = base_y + 232
        for pi, (p, pw) in enumerate(zip(pills, pill_data)):
            rrect(draw, [sx, py, sx+pw, py+34], 999, C["white"],
                  C["primary_b"], 1)
            draw.text((sx+16, py+9), p, font=F[13], fill=C["primary_dk"])
            sx += pw + 12

    return img


# ── SCENE 2: Login page ──────────────────────────────────────────────────────
def scene_login(t):
    grad = np.zeros((H, W, 3), dtype=np.uint8)
    for row in range(H):
        f = row/H
        grad[row,:] = [int(236*(1-f)+239*f), int(253*(1-f)+246*f), int(245*(1-f)+255*f)]
    img = Image.fromarray(grad)
    draw = ImageDraw.Draw(img)

    slide = min(1.0, t/0.5)
    card_w, card_h = 360, 430
    cx = W//2
    cy = int(H//2 - card_h//2 + (1-slide)*40)

    # Card shadow
    for sh in range(8, 0, -1):
        rrect(draw, [cx-card_w//2+sh, cy+sh, cx+card_w//2+sh, cy+card_h+sh],
              24, (int(200+sh*3),)*3)
    rrect(draw, [cx-card_w//2, cy, cx+card_w//2, cy+card_h], 24, C["white"])

    lx = cx - card_w//2 + 36
    # Logo
    draw_logo_icon(draw, lx, cy+32, 32, 8)
    draw.text((lx+42, cy+36), "NutriAgent", font=F["16b"], fill=C["gray_800"])
    draw.text((lx+42, cy+56), "AI Nutrition Platform", font=F[10], fill=C["gray_400"])

    draw.text((lx, cy+90), "Sign in", font=F["22b"], fill=C["gray_800"])
    draw.text((lx, cy+118), "Welcome back! Enter your credentials.",
              font=F[13], fill=C["gray_500"])

    # Email field
    fy = cy + 148
    draw.text((lx, fy), "Email", font=F["12b"], fill=C["gray_700"])
    rrect(draw, [lx, fy+18, cx+card_w//2-36, fy+46], 10,
          C["white"], C["gray_200"], 1)
    draw.text((lx+12, fy+26), "alex@example.com", font=F[13], fill=C["gray_400"])

    fy += 68
    draw.text((lx, fy), "Password", font=F["12b"], fill=C["gray_700"])
    rrect(draw, [lx, fy+18, cx+card_w//2-36, fy+46], 10,
          C["white"], C["gray_200"], 1)
    draw.text((lx+12, fy+26), "••••••••", font=F[13], fill=C["gray_600"])

    fy += 72
    rrect(draw, [lx, fy, cx+card_w//2-36, fy+40], 12, C["primary"])
    text_c(draw, cx, fy+10, "Sign In", F["14b"], (255,255,255))

    draw.text((cx - 96, cy+card_h-30),
              "Don't have an account?", font=F[12], fill=C["gray_400"])
    draw.text((cx + 46, cy+card_h-30), "Sign up", font=F["12b"], fill=C["primary_d"])

    # Caption
    cap_txt = "Secure login — start your nutrition journey"
    img = caption(img, draw, cap_txt)
    return img


# ── SCENE 3: Onboarding ──────────────────────────────────────────────────────
def scene_onboarding(t):
    grad = np.zeros((H, W, 3), dtype=np.uint8)
    for row in range(H):
        f = row/H
        grad[row,:] = [int(236*(1-f)+239*f), int(253*(1-f)+246*f), int(245*(1-f)+255*f)]
    img = Image.fromarray(grad)
    draw = ImageDraw.Draw(img)

    slide = min(1.0, t/0.5)
    cw, ch = 460, 510
    cx = W//2
    cy = int(H//2 - ch//2 + (1-slide)*40)

    for sh in range(6, 0, -1):
        rrect(draw, [cx-cw//2+sh, cy+sh, cx+cw//2+sh, cy+ch+sh],
              28, (int(205+sh*4),)*3)
    rrect(draw, [cx-cw//2, cy, cx+cw//2, cy+ch], 28, C["white"])

    # Header
    draw_logo_icon(draw, cx-cw//2+24, cy+20, 26, 7)
    draw.text((cx-cw//2+58, cy+26), "NutriAgent Setup", font=F["14b"], fill=C["gray_800"])
    draw.line([cx-cw//2, cy+56, cx+cw//2, cy+56], fill=C["gray_100"], width=1)

    # Step bars
    steps = ["Basic Info", "Health", "Preferences", "Goals"]
    sw = (cw - 56) // 4
    bx = cx-cw//2+28
    for si, sl in enumerate(steps):
        bw = sw - 6
        color = C["primary"] if si < 4 else C["gray_100"]
        rrect(draw, [bx, cy+66, bx+bw, cy+70], 999, color)
        text_c(draw, bx+bw//2, cy+73, sl, F[9], C["primary_d"] if si == 3 else C["gray_400"])
        bx += sw

    # Body
    by = cy + 96
    draw.text((cx-cw//2+28, by), "Fitness Goal", font=F["18b"], fill=C["gray_800"])
    goals = [("🔥 Lose Weight", True), ("⚖️ Maintain Weight", False),
             ("💪 Build Muscle", False), ("🏥 Disease Management", False)]
    gy = by + 28
    for label, selected in goals:
        bk = C["primary_bg"] if selected else C["white"]
        brd = C["primary_b"] if selected else C["gray_200"]
        fg2 = C["primary_dk"] if selected else C["gray_700"]
        rrect(draw, [cx-cw//2+28, gy, cx+cw//2-28, gy+38], 12, bk, brd, 1)
        draw.text((cx-cw//2+44, gy+11), label, font=F["13b"] if selected else F[13], fill=fg2)
        gy += 46

    # Health conditions
    draw.text((cx-cw//2+28, gy+4), "Health Conditions", font=F["14b"], fill=C["gray_700"])
    chips = [("Diabetes", True), ("Hypertension", False), ("Heart Disease", False),
             ("Obesity", False), ("Anemia", False)]
    chip_x = cx-cw//2+28
    chip_y = gy + 28
    for cname, on in chips:
        bb = draw.textbbox((0,0), cname, font=F[12])
        cw2 = bb[2]-bb[0] + 20
        if chip_x + cw2 > cx+cw//2-28:
            chip_x = cx-cw//2+28
            chip_y += 26
        bk = C["primary_bg"] if on else C["gray_100"]
        brd = C["primary_b"] if on else None
        fg3 = C["primary_dk"] if on else C["gray_600"]
        rrect(draw, [chip_x, chip_y, chip_x+cw2, chip_y+22], 999, bk,
              brd, 1 if brd else 0)
        draw.text((chip_x+10, chip_y+5), cname, font=F[12], fill=fg3)
        chip_x += cw2 + 8

    img = caption(img, draw, "4-step onboarding: goals, conditions, diet preference, activity level")
    return img


# ── SCENE 4: Dashboard ───────────────────────────────────────────────────────
def scene_dashboard(t):
    img = Image.new("RGB", (W, H), C["bg"])
    draw = ImageDraw.Draw(img)
    sidebar(draw, 0)

    sx = C["sidebar_w"] + 28
    sy = 20
    pw = W - sx - 28  # panel width

    # Greeting
    draw.text((sx, sy), "Good morning, Alex! 👋", font=F["18b"], fill=C["gray_800"])
    draw.text((sx, sy+28), "Here's your nutrition overview", font=F[12], fill=C["gray_500"])
    # Streak pill
    rrect(draw, [W-130, sy, W-20, sy+28], 12, C["streak_bg"])
    draw.text((W-120, sy+7), "⚡ 5 day streak", font=F["12b"], fill=C["streak_fg"])

    # ── Macros card ──────────────────────────────────────────────
    my = sy + 58
    card(draw, sx, my, pw, 145, 14)
    draw.text((sx+16, my+12), "Today's Progress", font=F["13b"], fill=C["gray_700"])

    ring_y = my + 50
    # Calorie ring
    progress_ring(img, draw, sx+66, ring_y, 48, 34,
                  1340/1800, C["primary"], C["gray_100"])
    draw = ImageDraw.Draw(img)
    text_c(draw, sx+66, ring_y-12, "🔥", F[10], C["primary"])
    text_c(draw, sx+66, ring_y-2, "1340", F["17b"], C["gray_800"])
    text_c(draw, sx+66, ring_y+18, "/1800", F[9], C["gray_400"])
    text_c(draw, sx+66, ring_y+48, "Calories", F[11], C["gray_500"])

    # Protein ring
    rx = sx + 165
    progress_ring(img, draw, rx, ring_y, 34, 24,
                  62/95, C["blue"], C["blue_bg"])
    draw = ImageDraw.Draw(img)
    text_c(draw, rx, ring_y-2, "62g", F["12b"], C["gray_800"])
    text_c(draw, rx, ring_y+14, "/95g", F[9], C["gray_400"])
    text_c(draw, rx, ring_y+42, "Protein", F[11], C["gray_500"])

    rx = sx + 250
    progress_ring(img, draw, rx, ring_y, 34, 24,
                  148/200, C["amber"], C["amber_bg"])
    draw = ImageDraw.Draw(img)
    text_c(draw, rx, ring_y-2, "148g", F["12b"], C["gray_800"])
    text_c(draw, rx, ring_y+14, "/200g", F[9], C["gray_400"])
    text_c(draw, rx, ring_y+42, "Carbs", F[11], C["gray_500"])

    rx = sx + 335
    progress_ring(img, draw, rx, ring_y, 34, 24,
                  28/55, C["pink"], C["pink_bg"])
    draw = ImageDraw.Draw(img)
    text_c(draw, rx, ring_y-2, "28g", F["12b"], C["gray_800"])
    text_c(draw, rx, ring_y+14, "/55g", F[9], C["gray_400"])
    text_c(draw, rx, ring_y+42, "Fat", F[11], C["gray_500"])

    # ── Weekly trend card ─────────────────────────────────────────
    wy = my + 160
    card(draw, sx, wy, pw, 155, 14)
    draw.text((sx+16, wy+12), "Weekly Calories Trend", font=F["13b"], fill=C["gray_700"])
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    heights = [62, 78, 55, 88, 70, 50, 40]
    bw = (pw - 60) // 7
    bx2 = sx + 30
    for di, (dy, bh) in enumerate(zip(days, heights)):
        alpha = 0.55 + 0.45 * (bh/88)
        col = tuple(int(c * alpha + 255*(1-alpha)) for c in C["primary"])
        rrect(draw, [bx2, wy+145-bh, bx2+bw-6, wy+145], 3, col)
        text_c(draw, bx2+bw//2-3, wy+147, dy, F[9], C["gray_400"])
        bx2 += bw

    # ── Deficiency alert ──────────────────────────────────────────
    ay = wy + 170
    rrect(draw, [sx, ay, sx+pw, ay+36], 12, C["amber_bg"], C["amber_b"], 1)
    draw.text((sx+12, ay+9), "⚠  Low iron this week — consider adding spinach or lentils",
              font=F[12], fill=(146, 64, 14))

    # ── Today's meals ─────────────────────────────────────────────
    ty = ay + 52
    draw.text((sx, ty), "Today's Meals", font=F["13b"], fill=C["gray_700"])
    draw.text((sx+pw-60, ty+1), "+ Log meal", font=F["13b"], fill=C["primary"])
    meals_data = [
        ("Dal Tadka + 2 Rotis", "Lunch · 12:30 PM", "480 kcal"),
        ("Oatmeal with Banana", "Breakfast · 8:00 AM", "320 kcal"),
    ]
    my2 = ty + 24
    for mname, msub, mkcal in meals_data:
        rrect(draw, [sx, my2, sx+pw, my2+52], 10, C["white"], C["border"], 1)
        draw.text((sx+14, my2+10), mname, font=F["13b"], fill=C["gray_800"])
        draw.text((sx+14, my2+28), msub, font=F[11], fill=C["gray_500"])
        bb = draw.textbbox((0,0), mkcal, font=F["13b"])
        draw.text((sx+pw-bb[2]-bb[0]-16, my2+18), mkcal,
                  font=F["13b"], fill=C["primary"])
        my2 += 58

    img = caption(img, draw, "Dashboard — calorie ring, macro rings, weekly trend, today's meals")
    return img


# ── SCENE 5: Log Meal ────────────────────────────────────────────────────────
def scene_log_meal(t):
    img = Image.new("RGB", (W, H), C["bg"])
    draw = ImageDraw.Draw(img)
    sidebar(draw, 1)

    sx = C["sidebar_w"] + 28
    sy = 22
    pw = W - sx - 28
    # Clamp to 560px wide
    pw = min(pw, 560)

    draw.text((sx, sy), "Log a Meal", font=F["18b"], fill=C["gray_800"])

    # Meal type selector
    mty = sy + 42
    draw.text((sx, mty), "Meal Type", font=F["12b"], fill=C["gray_700"])
    mtypes = ["Breakfast", "Lunch", "Dinner", "Snack"]
    mx2 = sx
    for mt in mtypes:
        bb = draw.textbbox((0,0), mt, font=F[12])
        bw2 = bb[2]-bb[0]+24
        on = mt == "Lunch"
        rrect(draw, [mx2, mty+20, mx2+bw2, mty+42], 8,
              C["primary_bg"] if on else C["gray_100"])
        draw.text((mx2+12, mty+26), mt, font=F["12b"] if on else F[12],
                  fill=C["primary_dk"] if on else C["gray_600"])
        mx2 += bw2 + 8

    # Card with tabs
    cy2 = mty + 54
    ch2 = 245
    card(draw, sx, cy2, pw, ch2, 14)

    # Tabs
    tabs = [("Text", True), ("Photo", False), ("Voice", False)]
    tx2 = sx+1
    for tab_name, on in tabs:
        bb = draw.textbbox((0,0), tab_name, font=F[13])
        tw2 = bb[2]-bb[0]+36
        fg4 = C["primary_d"] if on else C["gray_500"]
        draw.text((tx2+18, cy2+12), tab_name, font=F["13b"] if on else F[13], fill=fg4)
        if on:
            draw.line([tx2, cy2+37, tx2+tw2, cy2+37], fill=C["primary"], width=2)
        tx2 += tw2
    draw.line([sx+1, cy2+38, sx+pw-1, cy2+38], fill=C["gray_100"], width=1)

    # Text area
    ay2 = cy2+52
    draw.text((sx+16, ay2), "Describe your meal", font=F["12b"], fill=C["gray_700"])
    rrect(draw, [sx+16, ay2+18, sx+pw-16, ay2+118], 12, C["white"], C["gray_200"], 1)
    draw.text((sx+28, ay2+30),
              "I had a bowl of dal tadka with 2 rotis and some raita for lunch",
              font=F[13], fill=C["gray_600"])

    # Log button
    btn_y = ay2+128
    rrect(draw, [sx+16, btn_y, sx+pw-16, btn_y+38], 12, C["primary"])
    text_c(draw, sx+pw//2, btn_y+9, "✓  Log This Meal", F["14b"], (255,255,255))

    # Result card
    ry = cy2 + ch2 + 16
    rh = 195
    rrect(draw, [sx, ry, sx+pw, ry+rh], 14, C["result_bg"], C["result_b"], 1)

    # Check icon + title
    draw.text((sx+16, ry+14), "✓", font=F["16b"], fill=C["primary"])
    draw.text((sx+34, ry+14), "Meal Logged!", font=F["14b"], fill=C["green_text"])

    # Macro grid
    macros = [("Calories","480","kcal"), ("Protein","22","g"),
              ("Carbs","65","g"), ("Fat","12","g")]
    mg_w = (pw - 40) // 4
    mg_x = sx + 16
    for label, val, unit in macros:
        rrect(draw, [mg_x, ry+38, mg_x+mg_w-6, ry+80], 10, C["white"])
        text_c(draw, mg_x+mg_w//2-3, ry+42, label, F[10], C["gray_500"])
        text_c(draw, mg_x+mg_w//2-3, ry+56, val, F["14b"], C["gray_800"])
        text_c(draw, mg_x+mg_w//2-3, ry+70, unit, F[10], C["gray_400"])
        mg_x += mg_w

    # Food items
    draw.text((sx+16, ry+88), "Identified Items:", font=F["11b"], fill=C["gray_700"])
    foods = [("Dal Tadka (300g)", "312 kcal"),
             ("Roti (60g × 2)",   "168 kcal"),
             ("Raita (100g)",     " 60 kcal")]
    fi_y = ry + 104
    for fname, fkcal in foods:
        rrect(draw, [sx+16, fi_y, sx+pw-16, fi_y+22], 6, C["white"])
        draw.text((sx+26, fi_y+4), fname, font=F[12], fill=C["gray_700"])
        bb = draw.textbbox((0,0), fkcal, font=F[12])
        draw.text((sx+pw-26-bb[2], fi_y+4), fkcal, font=F[12], fill=C["gray_500"])
        fi_y += 26

    # Feedback
    draw.text((sx+16, ry+rh-26),
              "Great choice! You're at 74% of your daily calorie target.",
              font=F[12], fill=C["green_text"])

    img = caption(img, draw, "Log meals by text, photo upload, or voice — instant nutrition breakdown")
    return img


# ── SCENE 6: Diet Plan ───────────────────────────────────────────────────────
def scene_diet_plan(t):
    img = Image.new("RGB", (W, H), C["bg"])
    draw = ImageDraw.Draw(img)
    sidebar(draw, 2)

    sx = C["sidebar_w"] + 28
    sy = 22
    pw = W - sx - 28

    draw.text((sx, sy), "Weekly Diet Plan", font=F["18b"], fill=C["gray_800"])
    draw.text((sx, sy+28), "Target: 1,800 kcal/day", font=F[12], fill=C["gray_500"])

    # Regenerate button
    rrect(draw, [W-155, sy, W-28, sy+32], 10, C["primary"])
    text_c(draw, W-91, sy+7, "↻  Regenerate", F["12b"], (255,255,255))

    # Daily targets card
    ty2 = sy + 56
    card(draw, sx, ty2, pw, 72, 12)
    draw.text((sx+16, ty2+10), "DAILY TARGETS", font=F[10], fill=C["gray_400"])
    targets = [("1800","kcal","Calories",C["primary"]),
               ("95","g","Protein",C["blue"]),
               ("200","g","Carbs",C["amber"]),
               ("55","g","Fat",C["pink"])]
    tw3 = pw//4
    tx3 = sx+16
    for val, unit, lbl, col in targets:
        draw.text((tx3, ty2+26), val, font=F["18b"], fill=col)
        bb = draw.textbbox((0,0), val, font=F["18b"])
        draw.text((tx3+bb[2]+3, ty2+32), unit, font=F[10], fill=C["gray_400"])
        draw.text((tx3, ty2+50), lbl, font=F[11], fill=C["gray_500"])
        tx3 += tw3

    # Day cards
    dy3 = ty2 + 88
    days_data = [
        ("Monday",    "~1,820 kcal", True),
        ("Tuesday",   "~1,795 kcal", False),
        ("Wednesday", "~1,810 kcal", False),
        ("Thursday",  "~1,800 kcal", False),
    ]
    for dname, dkcal, expanded in days_data:
        dh = 130 if expanded else 52
        if dy3 + dh > H - 60:
            break
        card(draw, sx, dy3, pw, dh, 12)
        # Day icon
        rrect(draw, [sx+14, dy3+12, sx+42, dy3+40], 8, C["primary_bg"])
        draw.text((sx+22, dy3+20), "▦", font=F[14], fill=C["primary_d"])
        draw.text((sx+52, dy3+16), dname, font=F["14b"], fill=C["gray_800"])
        draw.text((sx+52, dy3+30), dkcal, font=F[11], fill=C["gray_500"])
        draw.text((sx+pw-28, dy3+18), "▲" if expanded else "▼",
                  font=F[12], fill=C["gray_400"])

        if expanded:
            # Breakfast section
            ms_y = dy3 + 56
            rrect(draw, [sx+14, ms_y, sx+pw-14, ms_y+68], 8,
                  C["amber_bg"], C["amber_b"], 1)
            draw.text((sx+24, ms_y+8), "🌅 Breakfast", font=F["12b"], fill=C["gray_700"])
            foods2 = [("Oatmeal", "80g", "302 kcal"), ("Banana", "120g", "107 kcal")]
            fy3 = ms_y+26
            for fn, fq, fk in foods2:
                draw.text((sx+24, fy3), f"• {fn} ({fq})", font=F[12], fill=C["gray_700"])
                bb = draw.textbbox((0,0), fk, font=F[12])
                draw.text((sx+pw-28-bb[2], fy3), fk, font=F[12], fill=C["gray_500"])
                fy3 += 18

        dy3 += dh + 8

    img = caption(img, draw, "AI-generated 7-day meal plan — allergen-filtered, TDEE-calibrated")
    return img


# ── SCENE 7: Chat ────────────────────────────────────────────────────────────
def scene_chat(t):
    img = Image.new("RGB", (W, H), C["bg"])
    draw = ImageDraw.Draw(img)
    sidebar(draw, 3)

    sx = C["sidebar_w"] + 28
    sy = 22
    pw = min(W - sx - 28, 640)

    # Header
    rrect(draw, [sx, sy, sx+36, sy+36], 10, C["primary"])
    sparkle_icon(draw, sx+18, sy+18, 14, (255,255,255))
    draw.text((sx+46, sy+4), "Nutrition AI", font=F["16b"], fill=C["gray_800"])
    draw.text((sx+46, sy+22), "Powered by RAG + IBM Granite", font=F[11], fill=C["gray_400"])

    # Messages
    messages = [
        ("assistant",
         "Hi! I'm your NutriAgent AI assistant. Ask me anything about nutrition,\nfood, your health goals, or meal planning.",
         "orchestrator"),
        ("user", "Is quinoa good for diabetes?", None),
        ("assistant",
         "Yes! Quinoa is excellent for diabetes. GI ~53, 8g protein per 100g.\nHigh fiber slows glucose absorption — helps stabilize blood sugar.",
         "advisory agent"),
        ("user", "What are the nutrition facts for lentil soup?", None),
        ("assistant",
         "Per 100g lentil soup: 116 kcal · Protein 9g · Carbs 20g · Fiber 7.9g.\nExcellent source of folate and iron. (Source: knowledge base)",
         "knowledge agent"),
    ]

    # Animate: reveal messages over time
    reveal = min(len(messages), int(t / 0.8) + 1)
    my3 = sy + 60
    for mi, (role, text, agent) in enumerate(messages[:reveal]):
        lines = text.split("\n")
        max_line_w = max(draw.textbbox((0,0), l, font=F[13])[2] for l in lines)
        bub_w = min(max_line_w + 28, int(pw * 0.75))
        line_h = 18
        bub_h = len(lines) * line_h + 20

        if role == "user":
            bx3 = sx + pw - bub_w - 4
            rrect(draw, [bx3, my3, bx3+bub_w, my3+bub_h], 14, C["primary"])
            for li, line in enumerate(lines):
                draw.text((bx3+14, my3+10+li*line_h), line, font=F[13], fill=(255,255,255))
            my3 += bub_h + 8
        else:
            rrect(draw, [sx, my3, sx+bub_w, my3+bub_h], 14, C["white"], C["border"], 1)
            for li, line in enumerate(lines):
                draw.text((sx+14, my3+10+li*line_h), line, font=F[13], fill=C["gray_700"])
            my3 += bub_h + 4
            if agent:
                rrect(draw, [sx, my3, sx+12+len(agent)*7, my3+18], 999, C["gray_100"])
                draw.text((sx+6, my3+3), f"◉ {agent}", font=F[10], fill=C["gray_500"])
                my3 += 24
            else:
                my3 += 6
        if my3 > H - 90:
            break

    # Input row
    rrect(draw, [sx, H-56, sx+pw-48, H-18], 12, C["white"], C["gray_200"], 1)
    draw.text((sx+14, H-44),
              "What foods are high in iron?", font=F[13], fill=C["gray_400"])
    rrect(draw, [sx+pw-44, H-56, sx+pw, H-18], 12, C["primary"])
    send_icon(draw, sx+pw-22, H-37, 14, (255,255,255))

    img = caption(img, draw,
                  "4 AI agents: Knowledge, Advisory, Recommendation, FoodLog — powered by IBM Granite + RAG")
    return img


# ── SCENE 8: End card ────────────────────────────────────────────────────────
def scene_end(t):
    # Deep green gradient
    grad = np.zeros((H, W, 3), dtype=np.uint8)
    for row in range(H):
        f = row/H
        grad[row,:] = [
            int(6*(1-f)+4*f),
            int(78*(1-f)+120*f),
            int(59*(1-f)+87*f)
        ]
    img = Image.fromarray(grad)
    draw = ImageDraw.Draw(img)

    slide = min(1.0, t/0.7)
    cy3 = int(H//2 - 140 + (1-slide)*50)

    # End icon
    ix2 = W//2 - 40
    rrect(draw, [ix2, cy3, ix2+80, cy3+80], 22,
          (255,255,255,30) if False else (20,100,70))
    draw.rounded_rectangle([ix2, cy3, ix2+80, cy3+80], 22,
                             outline=(255,255,255,60) if False else (100,200,150), width=2)
    leaf_icon(draw, W//2, cy3+40, 34, (255,255,255))

    # Title
    text_c(draw, W//2, cy3+96, "NutriAgent", F["56b"], (255,255,255))
    text_c(draw, W//2, cy3+162, "Personalized Nutrition Powered by AI",
           F["22b"], (110,231,183))

    # Pills
    if t > 0.5:
        pill_alpha = min(1.0, (t-0.5)/0.4)
        pills2 = ["📊 Dashboard & Tracking", "🍽️ Multimodal Meal Logging",
                  "📅 7-Day Diet Plans",    "🤖 Multi-Agent AI Chat",
                  "❤️  Health Advisory"]
        total_w2 = sum(
            draw.textbbox((0,0), p, font=F[13])[2] + 36 for p in pills2
        ) + 12 * (len(pills2)-1)
        px3 = W//2 - total_w2//2
        py2 = cy3 + 210
        for p in pills2:
            bb = draw.textbbox((0,0), p, font=F[13])
            pw3 = bb[2]-bb[0]+36
            # translucent pill
            overlay = Image.new("RGBA", img.size, (0,0,0,0))
            od = ImageDraw.Draw(overlay)
            od.rounded_rectangle([px3, py2, px3+pw3, py2+34], 999,
                                  fill=(255,255,255,20),
                                  outline=(255,255,255,40), width=1)
            img = img.convert("RGBA")
            img = Image.alpha_composite(img, overlay).convert("RGB")
            draw = ImageDraw.Draw(img)
            draw.text((px3+18, py2+9), p, font=F[13], fill=(255,255,255,220) if False else (220,255,230))
            px3 += pw3 + 12

    # Powered by
    text_c(draw, W//2, cy3+264,
           "Built with IBM Granite · LangChain · ChromaDB · React · FastAPI",
           F[14], (255, 255, 255))

    return img


# ─────────────────────────────────────────────────────────────────────────────
# MAIN: assemble all scenes → MP4
# ─────────────────────────────────────────────────────────────────────────────

SCENES = [
    (scene_title,     5.0),
    (scene_login,     5.5),
    (scene_onboarding,5.5),
    (scene_dashboard, 7.0),
    (scene_log_meal,  7.0),
    (scene_diet_plan, 7.0),
    (scene_chat,      7.0),
    (scene_end,       6.0),
]

def transition_frames(img_a, img_b, n=12):
    """Cross-dissolve between two PIL Images."""
    frames = []
    for i in range(n):
        alpha = i / n
        blended = Image.blend(img_a, img_b, alpha)
        frames.append(blended)
    return frames

def pil_to_cv(img):
    return cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)

def main():
    print("Generating NutriAgent_Testimonial.mp4 ...")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(OUTPUT), fourcc, FPS, (W, H))

    all_frames = []
    last_frame = None

    for scene_fn, dur in SCENES:
        print(f"  Rendering: {scene_fn.__name__} ({dur}s) ...")
        scene_frames = make_frames(scene_fn, dur)
        faded = fade_in_out(scene_frames, fade_frames=9)

        # Transition from previous scene
        if last_frame is not None and len(faded) > 0:
            xframes = transition_frames(last_frame, faded[0], n=15)
            for xf in xframes:
                writer.write(pil_to_cv(xf))

        for f in faded:
            writer.write(pil_to_cv(f))

        last_frame = faded[-1] if faded else last_frame

    writer.release()
    print(f"\nDONE  Video saved: {OUTPUT}")
    print(f"   Size: {OUTPUT.stat().st_size // 1024} KB")
    print(f"   Path: {OUTPUT.resolve()}")

if __name__ == "__main__":
    main()
