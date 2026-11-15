#!/usr/bin/env python3
"""Proof figure for the EmergencyNumbers table-order finding."""
from PIL import Image, ImageDraw, ImageFont

INTER = "/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf"
MONO = "/usr/share/fonts/truetype/sand-box/google/IBM Plex Mono/IBMPlexMono-Regular.ttf"
MONO_MED = "/usr/share/fonts/truetype/sand-box/google/IBM Plex Mono/IBMPlexMono-Medium.ttf"
MONO_BOLD = "/usr/share/fonts/truetype/sand-box/google/IBM Plex Mono/IBMPlexMono-SemiBold.ttf"

W, H = 1600, 1100
BG = (16, 18, 22)
PANEL = (28, 31, 38)
INK = (236, 237, 240)
MUTED = (156, 163, 175)
LINE = (48, 53, 64)
RED = (232, 93, 93)
GREEN = (62, 180, 126)
AMBER = (232, 176, 80)
BLUE = (130, 170, 230)


def font(path, size, weight=None):
    f = ImageFont.truetype(path, size)
    if weight is not None and path.endswith(".ttf") and "Variable" in path:
        try:
            f.set_variation_by_axes([14, weight])
        except Exception:
            pass
    return f


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    title = font(INTER, 44, 650)
    sub = font(INTER, 20, 450)
    label = font(INTER, 15, 600)
    qf = font(INTER, 20, 500)
    af = font(MONO_MED, 17)
    hf = font(INTER, 16, 600)
    foot = font(INTER, 15, 400)

    d.text((56, 36), "LabRat attaches the wrong emergency number", font=title, fill=INK)
    d.text(
        (56, 92),
        "EmergencyNumbers.kt walks a fixed country table and returns the first regex hit. Sentence order does not matter.",
        font=sub,
        fill=MUTED,
    )

    # table
    x0, y0, x1, y1 = 48, 140, W - 48, 980
    d.rounded_rectangle([x0, y0, x1, y1], 16, fill=PANEL)

    cols = [x0 + 24, x0 + 24 + 760, x0 + 24 + 760 + 360]
    headers = ["Question", "Function returns", "Should return"]
    hy = y0 + 18
    for i, h in enumerate(headers):
        d.text((cols[i], hy), h.upper(), font=hf, fill=MUTED)

    d.line([x0 + 16, hy + 32, x1 - 16, hy + 32], fill=LINE, width=1)

    rows = [
        (
            "What are the emergency numbers in Japan and China?",
            "Japan  110 / 119",
            "Japan and China",
            True,
        ),
        (
            "What are the emergency numbers in China and Japan?",
            "Japan  110 / 119   (same result)",
            "China and Japan",
            False,
        ),
        (
            "Flying from Thailand to Japan. Snake bite. What number do I call in Japan?",
            "Thailand  191 / 1669",
            "Japan  110 / 119",
            False,
        ),
        (
            "Chest pain in the United States after a trip to Thailand. What should I do?",
            "Thailand  191 / 1669",
            "United States  911",
            False,
        ),
        (
            "China's consulate in Chiang Mai, Northern Thailand.  (golden)",
            "Thailand  191 / 1669",
            "China, or no line",
            True,
        ),
        (
            "New South Wales is Australia, not the United Kingdom…  (golden)",
            "United Kingdom  999 / 112",
            "Australia, or both",
            True,
        ),
        (
            "Which emergency numbers should I know in the US?",
            "None\n(“the US” does not match)",
            "United States  911",
            False,
        ),
        (
            "Which emergency numbers should I know in the U.S.?",
            "United States  911",
            "United States  911",
            True,
        ),
    ]

    row_h = 96
    top = hy + 44
    for i, (q, got, want, golden) in enumerate(rows):
        y = top + i * row_h
        if i % 2 == 0:
            d.rectangle([x0 + 8, y - 8, x1 - 8, y + row_h - 16], fill=(34, 38, 46))
        # question
        qlines = wrap(d, q, qf, 740)
        d.text((cols[0], y + 8), qlines[0], font=qf, fill=INK)
        if len(qlines) > 1:
            d.text((cols[0], y + 34), qlines[1], font=qf, fill=INK)
        if golden:
            d.text((cols[0], y + 62), "PINNED IN routing-leaves.json", font=label, fill=AMBER)

        wrong = "None" in got or "Japan" in got and "China and Japan" in q or "Thailand" in got or "United Kingdom" in got
        if want.startswith("United States") and got.startswith("United States"):
            wrong = False
            color = GREEN
        else:
            color = RED if wrong or got.startswith("Japan") or got.startswith("Thailand") or got.startswith("United Kingdom") or got.startswith("None") else GREEN
            if got.startswith("United States"):
                color = GREEN

        for j, line in enumerate(got.split("\n")):
            d.text((cols[1], y + 12 + j * 22), line, font=af, fill=color)
        d.text((cols[2], y + 18), want, font=af, fill=GREEN if color == GREEN else BLUE)

    d.text(
        (56, 1000),
        "Reproduction: python3 repro/repro.py  ·  853 / 853 golden emergencyLine cases match  ·  labrat-boar-fork @606923a  ·  15 Nov 2026, Asia/Calcutta",
        font=foot,
        fill=MUTED,
    )
    d.text(
        (56, 1028),
        "Caller: HealthGate.fixedText  ·  Thailand is first in COUNTRIES; Japan is before China; “the US” is not in the United States regex.",
        font=foot,
        fill=MUTED,
    )

    out = "/workspace/bounties/poidh-1520/proof/emergency-table.png"
    img.save(out, "PNG", optimize=True)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
