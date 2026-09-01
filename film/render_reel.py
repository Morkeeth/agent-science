#!/usr/bin/env python3
"""Render demo/seg-flipbook.mp4 from HTML cards + hosted screenshots.

Fallback when the flipbook sibling repo is absent. Scene timings match
film/lay_voice.py cues (agent-science.json scene starts).
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCREENS = ROOT / "docs" / "assets" / "screens"
OUT = ROOT / "demo" / "seg-flipbook.mp4"
WORK = ROOT / "demo" / ".reel-build"
W, H = 1280, 720
FPS = 25

# Scene start seconds — visibility at 10.5s, CONTRARY at 22s (teleprompter)
CUES = [0.5, 10.5, 22.0, 34.0, 44.0, 53.0, 63.0, 72.0, 80.0, 90.0, 98.0]

SCENES = [
    {
        "kind": "card",
        "kicker": "00 · hook",
        "big": "Your agent websearches.<br>You get one answer.",
        "line": "You never see what was skipped.",
    },
    {
        "kind": "shot",
        "kicker": "01 · visibility",
        "image": "08-visibility-ui.png",
        "caption": "Pane 1b — angles searched, shallow-route warnings, source balance",
    },
    {
        "kind": "shot",
        "kicker": "02 · contrary",
        "image": "08-visibility-ui.png",
        "overlay": "CONTRARY TO RESEARCH",
        "caption": "When the field outruns the paper — named why",
    },
    {
        "kind": "card",
        "kicker": "03 · rule",
        "head": "Cite the document, or print that you could not.",
        "on_cam": "LOCATE → VERIFY → STAMP — enforced in the constructor",
    },
    {
        "kind": "shot",
        "kicker": "04 · sourced",
        "image": "04-registry-search.png",
        "caption": "Exact sentence from the instrument — not a summary",
    },
    {
        "kind": "card",
        "kicker": "05 · refuse",
        "head": "Copyright never evaluated is not permission.",
        "on_cam": "Refuse with a named cause — not permission.",
    },
    {
        "kind": "card",
        "kicker": "06 · honest",
        "head": "We pointed Agent Science at our own marketing.",
        "on_cam": "It refused our headline — the object did not support the claim.",
    },
    {
        "kind": "card",
        "kicker": "07 · compound",
        "head": "Shelf remembers. Parallel drops.",
        "on_cam": "RUN A: 1 Parallel · RUN B: 0 Parallel · 1 corpus hit — sealed.",
        "line": "A=1 → B=0",
    },
    {
        "kind": "shot",
        "kicker": "08 · truths",
        "image": "07-truths-dashboard.png",
        "caption": "265+ claims · ranked queries · field signals",
    },
    {
        "kind": "shot",
        "kicker": "09 · partners",
        "image": "06-partners-json.png",
        "caption": "Parallel · Gemini · Cloud Run · ADK — GET /partners",
    },
    {
        "kind": "card",
        "kicker": "10 · close",
        "head": "Agent Science.",
        "on_cam": "agent-science-568004190078.us-central1.run.app",
        "big": "Ask once.<br>Shelf compounds.",
        "line": "Link in the description.",
    },
]


def _html(scene: dict) -> str:
    img_uri = ""
    overlay = ""
    if scene.get("kind") == "shot":
        path = SCREENS / scene["image"]
        if not path.exists():
            raise SystemExit(f"missing screenshot: {path}")
        img_uri = path.resolve().as_uri()
        if scene.get("overlay"):
            overlay = (
                f'<div class="stamp">{scene["overlay"]}</div>'
            )
    big = scene.get("big", "")
    head = scene.get("head", "")
    line = scene.get("line", "")
    on_cam = scene.get("on_cam", "")
    caption = scene.get("caption", "")
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
:root {{
  --bg:#0b0d10; --panel:#12161c; --line:#232a33; --ink:#e9edf2; --muted:#8b95a3;
  --accent:#B42318; --mono:ui-monospace,Menlo,Consolas,monospace;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
}}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{
  width:{W}px; height:{H}px; background:var(--bg); color:var(--ink);
  font-family:var(--sans); overflow:hidden;
}}
.brand {{
  position:absolute; top:18px; right:22px; font-family:var(--mono); font-size:11px;
  letter-spacing:.16em; color:var(--muted); text-transform:uppercase; z-index:5;
}}
.kicker {{
  position:absolute; top:18px; left:22px; font-family:var(--mono); font-size:12px;
  letter-spacing:.18em; color:var(--muted); text-transform:uppercase; z-index:5;
}}
.card {{
  position:absolute; inset:0; padding:72px 56px 48px; display:flex; flex-direction:column;
}}
.big {{ font-size:46px; font-weight:600; line-height:1.08; letter-spacing:-.02em; }}
.head {{ font-size:32px; font-weight:600; line-height:1.12; margin-top:auto; }}
.on-cam {{ color:var(--muted); font-size:15px; margin-top:12px; max-width:58ch; }}
.line {{ font-family:var(--mono); color:var(--accent); font-size:16px; margin-top:14px; }}
.spacer {{ flex:1; }}
.shot-wrap {{
  position:absolute; inset:48px 32px 32px; border:1px solid var(--line); background:var(--panel);
  overflow:hidden; display:flex; align-items:flex-start; justify-content:center;
}}
.shot-wrap img {{ width:100%; height:auto; display:block; }}
.caption {{
  position:absolute; left:32px; right:32px; bottom:18px; font-family:var(--mono);
  font-size:13px; color:var(--muted); background:rgba(11,13,16,.88); padding:8px 12px;
}}
.stamp {{
  position:absolute; top:24px; right:24px; background:var(--accent); color:#fff;
  font-family:var(--mono); font-size:13px; font-weight:700; letter-spacing:.08em;
  padding:10px 14px; transform:rotate(-4deg); box-shadow:0 8px 24px rgba(0,0,0,.45);
}}
.bar {{ position:absolute; left:0; right:0; bottom:0; height:4px; background:#1a2028; }}
.bar i {{ display:block; height:100%; width:100%; background:var(--accent); }}
</style></head><body>
<div class="brand">Agent Science · Agentic Cinema</div>
<div class="kicker">{scene.get("kicker", "")}</div>
""" + (
        f"""<div class="shot-wrap"><img src="{img_uri}" alt="">{overlay}</div>
<div class="caption">{caption}</div>"""
        if scene.get("kind") == "shot"
        else f"""<div class="card">
  <div class="spacer"></div>
  {f'<div class="big">{big}</div>' if big else ''}
  {f'<div class="head">{head}</div>' if head else ''}
  {f'<div class="on-cam">{on_cam}</div>' if on_cam else ''}
  {f'<div class="line">{line}</div>' if line else ''}
  <div class="spacer"></div>
</div>"""
    ) + """<div class="bar"><i></i></div></body></html>"""


def durations() -> list[float]:
    ends = CUES[1:] + [104.0]
    return [round(e - s, 3) for s, e in zip(CUES, ends)]


def render_pngs() -> list[pathlib.Path]:
    from playwright.sync_api import sync_playwright

    WORK.mkdir(parents=True, exist_ok=True)
    paths: list[pathlib.Path] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H})
        for i, scene in enumerate(SCENES):
            html = _html(scene)
            tmp = WORK / f"scene-{i:02d}.html"
            tmp.write_text(html, encoding="utf-8")
            page.goto(tmp.as_uri(), wait_until="load")
            page.wait_for_timeout(200)
            out = WORK / f"frame-{i:02d}.png"
            page.screenshot(path=str(out), type="png")
            paths.append(out)
            print(f"rendered {out.name}  ({durations()[i]:.1f}s)")
        browser.close()
    return paths


def mux_video(pngs: list[pathlib.Path]) -> None:
    durs = durations()
    concat = WORK / "concat.txt"
    lines = []
    for png, dur in zip(pngs, durs):
        lines.append(f"file '{png.resolve()}'")
        lines.append(f"duration {dur}")
    lines.append(f"file '{pngs[-1].resolve()}'")
    concat.write_text("\n".join(lines) + "\n", encoding="utf-8")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(concat),
            "-vf", f"fps={FPS},format=yuv420p",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            str(OUT),
        ],
        check=True,
    )
    dur = float(
        subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(OUT)],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    )
    print(f"WROTE {OUT}  {dur:.1f}s")


def main() -> int:
    if len(SCENES) != len(CUES):
        raise SystemExit(f"{len(SCENES)} scenes vs {len(CUES)} cues")
    pngs = render_pngs()
    mux_video(pngs)
    meta = {"scenes": len(SCENES), "cues": CUES, "durations": durations()}
    (WORK / "manifest.json").write_text(json.dumps(meta, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
