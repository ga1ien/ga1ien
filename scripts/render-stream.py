#!/usr/bin/env python3
"""Editor window that types real Watchtower source. GIF is what GitHub will play."""
from __future__ import annotations

import html
import subprocess
from pathlib import Path

ROOT = Path("/tmp/ga1ien-readme")
FRAMES = ROOT / "assets" / "stream-frames"
OUT_GIF = ROOT / "assets" / "stream.gif"
OUT_PNG = ROOT / "assets" / "stream.png"

W, H = 520, 520
FONT = "Menlo, Monaco, ui-monospace, monospace"

# Exact lines from braintied/watchtower src/inngest/session-analyzer.ts
STREAM = [
    "export function createSessionAnalyzer(client: Inngest) {",
    "  return client.createFunction(",
    "    {",
    "      id: 'watchtower/session-analyzer',",
    "      name: 'Watchtower: Session Analyzer',",
    "      concurrency: [{ limit: 2 }],",
    "      retries: 2,",
    "    },",
    "    { event: 'watchtower/coding-session.received' },",
    "    async ({ event, step }) => {",
    "      const { session_id } = event.data;",
    "",
    "      const session = await step.run('fetch-session', async () => {",
    "        const { data, error } = await queryWatchtower(",
    "          'coding_sessions',",
    "        )",
    "          .select('id, session_key, metadata')",
    "          .eq('id', session_id)",
    "          .single();",
    "        if (error !== null) throw new Error(error.message);",
    "        return data;",
    "      });",
    "",
    "      const { redacted } = redactSecrets(rawContent);",
    "      await analyzeWithHaiku(redacted);",
    "      await embedText(redacted);",
    "    },",
    "  );",
    "}",
]


KEYWORDS = {
    "export", "function", "return", "async", "await", "const", "if",
    "throw", "new", "null",
}


def colorize(line: str) -> str:
    if line.lstrip().startswith("//"):
        return f'<tspan fill="#6e7681">{html.escape(line)}</tspan>'
    out: list[str] = []
    i = 0
    while i < len(line):
        ch = line[i]
        if ch in "'\"":
            q = ch
            j = i + 1
            while j < len(line) and line[j] != q:
                j += 1
            j = min(j + 1, len(line))
            out.append(f'<tspan fill="#a5d6ff">{html.escape(line[i:j])}</tspan>')
            i = j
            continue
        if ch.isalpha() or ch == "_":
            j = i
            while j < len(line) and (line[j].isalnum() or line[j] == "_"):
                j += 1
            word = line[i:j]
            fill = "#ff7b72" if word in KEYWORDS else "#e6edf3"
            if word in {"createSessionAnalyzer", "queryWatchtower", "redactSecrets", "analyzeWithHaiku", "embedText", "createFunction"}:
                fill = "#d2a8ff"
            out.append(f'<tspan fill="{fill}">{html.escape(word)}</tspan>')
            i = j
            continue
        out.append(f'<tspan fill="#8b949e">{html.escape(ch)}</tspan>')
        i += 1
    return "".join(out)


def chrome(tab: str) -> str:
    return f"""
  <rect width="{W}" height="{H}" rx="12" fill="#000000"/>
  <rect x="0.6" y="0.6" width="{W-1.2}" height="{H-1.2}" rx="12" fill="none" stroke="#222"/>
  <rect width="3" height="{H}" rx="2" fill="#ccff00"/>
  <rect x="3" width="{W-3}" height="36" fill="#0a0a0a"/>
  <circle cx="22" cy="18" r="4.5" fill="#ff5f57"/>
  <circle cx="38" cy="18" r="4.5" fill="#febc2e"/>
  <circle cx="54" cy="18" r="4.5" fill="#28c840"/>
  <rect x="78" y="8" width="240" height="20" rx="4" fill="#161616"/>
  <text x="88" y="22" fill="#ccff00" font-family="{FONT}" font-size="11">{html.escape(tab)}</text>
"""


def scene(n_lines: int, cursor_on: bool) -> str:
    bits = [chrome("session-analyzer.ts")]
    y = 58
    visible = STREAM[:n_lines]
    for i, line in enumerate(visible, start=1):
        bits.append(
            f'<text x="14" y="{y}" fill="#3d3d3d" font-family="{FONT}" font-size="11">{i:2}</text>'
        )
        bits.append(
            f'<text x="40" y="{y}" xml:space="preserve" font-family="{FONT}" font-size="11">{colorize(line)}</text>'
        )
        y += 15
    if cursor_on and n_lines < len(STREAM):
        # caret at next line start
        bits.append(f'<rect x="40" y="{y - 12}" width="7" height="12" fill="#ccff00"/>')
    elif cursor_on:
        bits.append(f'<rect x="40" y="{y - 12}" width="7" height="12" fill="#ccff00"/>')
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*2}" height="{H*2}" '
        f'viewBox="0 0 {W} {H}">{"".join(bits)}</svg>'
    )


def main() -> None:
    FRAMES.mkdir(parents=True, exist_ok=True)
    for old in FRAMES.glob("*"):
        old.unlink()

    timeline: list[tuple[str, int]] = []

    def add(n: int, cursor: bool, hold: int) -> None:
        i = len(timeline)
        svg = FRAMES / f"{i:03d}.svg"
        png = FRAMES / f"{i:03d}.png"
        svg.write_text(scene(n, cursor))
        subprocess.run(["rsvg-convert", "-w", str(W * 2), str(svg), "-o", str(png)], check=True)
        timeline.append((str(png), hold))

    # boot blink on empty editor
    for on in (True, False, True):
        add(0, on, 10)

    # stream lines
    for n in range(1, len(STREAM) + 1):
        add(n, True, 7 if STREAM[n - 1].strip() else 4)

    # hold + blink
    for on in (True, False, True, False, True, False, True):
        add(len(STREAM), on, 14)

    final = scene(len(STREAM), True)
    (ROOT / "assets" / "stream.svg").write_text(final)
    subprocess.run(
        ["rsvg-convert", "-w", str(W * 2), str(ROOT / "assets" / "stream.svg"), "-o", str(OUT_PNG)],
        check=True,
    )

    list_path = FRAMES / "list.txt"
    lines = []
    for png, cs in timeline:
        lines.append(f"file '{png}'")
        lines.append(f"duration {cs / 100:.2f}")
    lines.append(f"file '{timeline[-1][0]}'")
    list_path.write_text("\n".join(lines) + "\n")

    palette = FRAMES / "palette.png"
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
            "-vf", "fps=12,scale=520:-1:flags=lanczos,palettegen=max_colors=40:stats_mode=diff",
            str(palette),
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
            "-i", str(palette),
            "-lavfi", "fps=12,scale=520:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=2",
            "-loop", "0",
            str(OUT_GIF),
        ],
        check=True,
        capture_output=True,
    )
    print(f"gif={OUT_GIF.stat().st_size} png={OUT_PNG.stat().st_size} frames={len(timeline)}")


if __name__ == "__main__":
    main()
