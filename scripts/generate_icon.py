"""Generate the app icon: a stylised face with neural/psychology nodes.

Outputs assets/icon.ico (multi-size: 256, 64, 48, 32, 16).
Run once with:  uv run python scripts/generate_icon.py
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw

# ── palette (matches theme.py) ──────────────────────────────────────────────
BG = (15, 23, 42, 255)          # slate-900  #0f172a
SURFACE = (30, 41, 59, 255)     # slate-800  #1e293b
ACCENT = (99, 102, 241, 255)    # indigo-500 #6366f1
ACCENT_L = (129, 140, 248, 255) # indigo-400 #818cf8
ACCENT_D = (79, 70, 229, 255)   # indigo-600 #4f46e5
TEXT = (241, 245, 249, 255)     # slate-100  #f1f5f9
NODE_GREEN = (34, 197, 94, 255) # green-500  #22c55e


def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    s = size / 256  # scale factor — everything below is designed at 256 px

    # ── rounded square background ──────────────────────────────────────────
    r = int(40 * s)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=BG)

    # ── outer glow ring around face (subtle) ───────────────────────────────
    cx, cy = size / 2, size * 0.46
    ring_r = size * 0.36
    lw = max(1, int(3 * s))
    d.ellipse(
        [cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r],
        outline=(*ACCENT[:3], 60),
        width=max(1, int(8 * s)),
    )

    # ── face oval ──────────────────────────────────────────────────────────
    fw, fh = size * 0.32, size * 0.40
    face_box = [cx - fw, cy - fh * 0.56, cx + fw, cy + fh * 0.44]
    d.ellipse(face_box, fill=SURFACE, outline=ACCENT_L, width=max(1, int(2.5 * s)))

    # ── eyes ───────────────────────────────────────────────────────────────
    ey = cy - fh * 0.06
    ew = fh * 0.09
    eh = fh * 0.07
    for ex in [cx - fw * 0.38, cx + fw * 0.38]:
        # iris
        d.ellipse([ex - ew, ey - eh, ex + ew, ey + eh], fill=ACCENT)
        # pupil
        pw = ew * 0.45
        d.ellipse([ex - pw, ey - pw, ex + pw, ey + pw], fill=(*ACCENT_D[:3], 220))
        # highlight
        hw = pw * 0.4
        d.ellipse(
            [ex - ew * 0.1 - hw, ey - eh * 0.35 - hw,
             ex - ew * 0.1 + hw, ey - eh * 0.35 + hw],
            fill=TEXT,
        )

    # ── nose (simple subtle line) ──────────────────────────────────────────
    ny_top = cy + fh * 0.08
    ny_bot = cy + fh * 0.24
    nw = fw * 0.08
    d.line([(cx, ny_top), (cx, ny_bot)], fill=(*ACCENT_L[:3], 80), width=max(1, int(1.5 * s)))
    d.arc(
        [cx - nw * 2, ny_bot - nw, cx + nw * 2, ny_bot + nw],
        start=200, end=340,
        fill=(*ACCENT_L[:3], 100),
        width=max(1, int(1.5 * s)),
    )

    # ── smile ──────────────────────────────────────────────────────────────
    smile_top = cy + fh * 0.30
    sw = fw * 0.45
    sh = fh * 0.12
    d.arc(
        [cx - sw, smile_top, cx + sw, smile_top + sh * 2],
        start=10, end=170,
        fill=ACCENT_L,
        width=max(1, int(2.5 * s)),
    )

    # ── neural node ring (psychology / analysis overlay) ───────────────────
    node_r = size * 0.42        # orbit radius
    n_nodes = 6
    node_dot = max(2, int(7 * s))
    line_w = max(1, int(1.5 * s))

    node_positions: list[tuple[float, float]] = []
    for i in range(n_nodes):
        angle = math.radians(i * 360 / n_nodes - 90)
        nx = cx + node_r * math.cos(angle)
        ny = cy + node_r * math.sin(angle) * 0.88  # slight vertical squash
        node_positions.append((nx, ny))

    # connecting lines between nodes (dashed look via short segments)
    for i, (x1, y1) in enumerate(node_positions):
        x2, y2 = node_positions[(i + 1) % n_nodes]
        # draw only every other connection to keep it clean
        if i % 2 == 0:
            d.line([(x1, y1), (x2, y2)], fill=(*ACCENT[:3], 70), width=line_w)
        # spoke to center
        d.line([(x1, y1), (cx, cy)], fill=(*ACCENT[:3], 40), width=line_w)

    # node dots
    colors = [ACCENT, NODE_GREEN, ACCENT_L, ACCENT, NODE_GREEN, ACCENT_L]
    for (nx, ny), color in zip(node_positions, colors):
        d.ellipse(
            [nx - node_dot, ny - node_dot, nx + node_dot, ny + node_dot],
            fill=color,
        )
        # outer glow ring on each node
        gr = node_dot + max(1, int(3 * s))
        d.ellipse(
            [nx - gr, ny - gr, nx + gr, ny + gr],
            outline=(*color[:3], 80),
            width=max(1, int(1.5 * s)),
        )

    # ── landmark dots on the face (MediaPipe-style) ────────────────────────
    lm_color = (*ACCENT_L[:3], 160)
    lm_r = max(1, int(2.5 * s))
    landmarks = [
        # brow ridge
        (cx - fw * 0.55, cy - fh * 0.18),
        (cx - fw * 0.28, cy - fh * 0.24),
        (cx, cy - fh * 0.26),
        (cx + fw * 0.28, cy - fh * 0.24),
        (cx + fw * 0.55, cy - fh * 0.18),
        # cheekbones
        (cx - fw * 0.68, cy + fh * 0.05),
        (cx + fw * 0.68, cy + fh * 0.05),
        # jaw line
        (cx - fw * 0.60, cy + fh * 0.25),
        (cx, cy + fh * 0.44),
        (cx + fw * 0.60, cy + fh * 0.25),
    ]
    for lx, ly in landmarks:
        d.ellipse([lx - lm_r, ly - lm_r, lx + lm_r, ly + lm_r], fill=lm_color)

    return img


def main() -> None:
    out_dir = Path(__file__).parents[1] / "assets"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "icon.ico"

    sizes = [256, 64, 48, 32, 16]
    frames = [draw_icon(sz) for sz in sizes]

    frames[0].save(
        out_path,
        format="ICO",
        sizes=[(sz, sz) for sz in sizes],
        append_images=frames[1:],
    )
    print(f"Icon saved: {out_path}")


if __name__ == "__main__":
    main()
