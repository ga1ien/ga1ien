#!/usr/bin/env python3
"""Render a dark terminal card as SVG frames, then a GIF.

GitHub will play a GIF. SMIL inside an SVG <img> often dies in camo.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path("/tmp/ga1ien-readme")
FRAMES = ROOT / "assets" / "frames"
OUT_SVG = ROOT / "assets" / "term.svg"
OUT_GIF = ROOT / "assets" / "term.gif"
OUT_PNG = ROOT / "assets" / "term.png"

W, H = 880, 456
FONT = "Menlo, Monaco, ui-monospace, monospace"


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def text(x: int, y: int, body: str, fill: str, size: int = 14) -> str:
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" '
        f'font-family="{FONT}" font-size="{size}">{esc(body)}</text>'
    )


def prompt(y: int, cmd: str) -> str:
    return (
        f'<text x="28" y="{y}" font-family="{FONT}" font-size="14">'
        f'<tspan fill="#3f3f3f">$</tspan>'
        f'<tspan dx="10" fill="#e8e8e8">{esc(cmd)}</tspan>'
        f"</text>"
    )


def cursor(x: int, y: int, on: bool) -> str:
    if not on:
        return ""
    return (
        f'<rect x="{x}" y="{y - 12}" width="8" height="14" fill="#ccff00"/>'
    )


def chrome() -> str:
    return f"""
  <rect width="{W}" height="{H}" rx="16" fill="#000000"/>
  <rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="16" fill="none" stroke="#222"/>
  <rect width="4" height="{H}" rx="2" fill="#ccff00"/>
  <rect x="4" width="{W - 4}" height="42" rx="16" fill="#0b0b0b"/>
  <rect x="4" y="28" width="{W - 4}" height="14" fill="#0b0b0b"/>
  <circle cx="26" cy="21" r="5" fill="#ff5f57"/>
  <circle cx="44" cy="21" r="5" fill="#febc2e"/>
  <circle cx="62" cy="21" r="5" fill="#28c840"/>
  {text(84, 25, "ga1ien@braintied", "#666666", 12)}
"""


# Concrete stack. Second column starts at 148 so the card is dense, not airy.
STACK = [
    ("ora", "agent operating system"),
    ("", "identities persist in cortex. machines do not."),
    ("watchtower", "session intelligence"),
    ("", "every session captured and searchable"),
    ("sentigen", "meetings, mail, crm, tasks"),
    ("", "the company of record"),
    ("kit", "one companion over every product"),
    ("", "same surface. different brains."),
    ("kulti", "live stage"),
    ("", "agents ship while people watch."),
]

FEED = [
    ("watchtower", "session captured"),
    ("ora", "identity hydrated"),
    ("sentigen", "meeting closed"),
    ("kit", "surface composed"),
    ("kulti", "room live"),
]


def stack_lines(count: int) -> str:
    parts: list[str] = []
    y = 108
    for i, (name, desc) in enumerate(STACK):
        if i >= count:
            break
        if name:
            parts.append(text(28, y, name, "#8a8a8a"))
            parts.append(text(148, y, desc, "#e4e4e4"))
        else:
            parts.append(text(148, y, desc, "#6a6a6a"))
        y += 22
    return "\n".join(parts)


def feed_lines(count: int) -> str:
    parts = [
        f'<line x1="600" y1="64" x2="600" y2="{H - 28}" stroke="#1a1a1a"/>',
        text(620, 80, "live", "#ccff00", 12),
    ]
    y = 108
    for i, (name, event) in enumerate(FEED):
        if i >= count:
            break
        parts.append(text(620, y, name, "#6a6a6a", 13))
        parts.append(text(620, y + 18, event, "#d4d4d4", 13))
        y += 44
    return "\n".join(parts)


def scene(
    cmd: str,
    n_stack: int,
    n_feed: int,
    status_cmd: str | None,
    show_status: bool,
    cursor_on: bool,
    cursor_at: str,
) -> str:
    bits = [chrome(), prompt(72, cmd)]
    if n_stack:
        bits.append(stack_lines(n_stack))
    if n_feed:
        bits.append(feed_lines(n_feed))
    y_status_prompt = 108 + 22 * len(STACK) + 24
    if status_cmd is not None:
        bits.append(prompt(y_status_prompt, status_cmd))
    if show_status:
        bits.append(text(28, y_status_prompt + 26, "running", "#ccff00"))
    # cursor
    if cursor_at == "cmd":
        # after typed command
        x = 28 + 9 + 10 + int(len(cmd) * 8.4)
        bits.append(cursor(x, 72, cursor_on))
    elif cursor_at == "status":
        x = 28 + 9 + 10 + int(len(status_cmd or "") * 8.4)
        bits.append(cursor(x, y_status_prompt, cursor_on))
    elif cursor_at == "end":
        bits.append(cursor(108, y_status_prompt + 28, cursor_on))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W * 2}" height="{H * 2}" '
        f'viewBox="0 0 {W} {H}">\n{"".join(bits)}\n</svg>\n'
    )


def write_svg(path: Path, svg: str) -> None:
    path.write_text(svg)


def raster(svg_path: Path, png_path: Path) -> None:
    subprocess.run(
        ["rsvg-convert", "-w", str(W * 2), str(svg_path), "-o", str(png_path)],
        check=True,
    )


def main() -> None:
    FRAMES.mkdir(parents=True, exist_ok=True)
    for old in FRAMES.glob("*"):
        old.unlink()

    timeline: list[tuple[str, int]] = []  # png, duration_cs (centiseconds)

    def add(svg: str, hold: int) -> None:
        i = len(timeline)
        svg_path = FRAMES / f"{i:03d}.svg"
        png_path = FRAMES / f"{i:03d}.png"
        write_svg(svg_path, svg)
        raster(svg_path, png_path)
        timeline.append((str(png_path), hold))

    # boot: empty prompt, cursor blink
    for on in (True, False, True, False, True):
        add(scene("", 0, 0, None, False, on, "cmd"), 22)

    # type `stack`
    typed = ""
    for ch in "stack":
        typed += ch
        add(scene(typed, 0, 0, None, False, True, "cmd"), 11)
    add(scene("stack", 0, 0, None, False, False, "cmd"), 22)

    # reveal stack, two lines at a time (name + detail)
    for n in range(1, len(STACK) + 1):
        add(scene("stack", n, 0, None, False, False, "cmd"), 18 if STACK[n - 1][0] else 11)

    # live feed ticks in
    for n in range(1, len(FEED) + 1):
        add(scene("stack", len(STACK), n, None, False, False, "cmd"), 20)

    # type `status`
    add(scene("stack", len(STACK), len(FEED), "", False, True, "status"), 28)
    typed = ""
    for ch in "status":
        typed += ch
        add(scene("stack", len(STACK), len(FEED), typed, False, True, "status"), 11)

    # hold: running + cursor blink. GIF delay is cheap; unique frames stay 2.
    for _ in range(16):
        add(scene("stack", len(STACK), len(FEED), "status", True, True, "end"), 42)
        add(scene("stack", len(STACK), len(FEED), "status", True, False, "end"), 42)

    # last frame is the still
    final = scene("stack", len(STACK), len(FEED), "status", True, True, "end")
    write_svg(OUT_SVG, final)
    raster(OUT_SVG, OUT_PNG)

    # concat demuxer with per-frame durations
    list_path = FRAMES / "list.txt"
    lines = []
    for png, cs in timeline:
        # ffmpeg concat duration is seconds
        lines.append(f"file '{png}'")
        lines.append(f"duration {cs / 100:.2f}")
    # last file must repeat
    lines.append(f"file '{timeline[-1][0]}'")
    list_path.write_text("\n".join(lines) + "\n")

    palette = FRAMES / "palette.png"
    # Do not resample to a fixed fps. The last cut flattened the hold
    # because fps=12 ignored per-frame duration.
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
            "-vf", "scale=880:-1:flags=lanczos,palettegen=max_colors=48:stats_mode=diff",
            str(palette),
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
            "-i", str(palette),
            "-lavfi", "scale=880:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3",
            "-vsync", "passthrough",
            "-loop", "0",
            str(OUT_GIF),
        ],
        check=True,
        capture_output=True,
    )
    total_s = sum(cs for _, cs in timeline) / 100
    print(f"gif={OUT_GIF} bytes={OUT_GIF.stat().st_size}")
    print(f"png={OUT_PNG} bytes={OUT_PNG.stat().st_size}")
    print(f"frames={len(timeline)} duration={total_s:.1f}s")


if __name__ == "__main__":
    main()
