#!/usr/bin/env python3
"""Render agent-science flipbook reel locally when sibling flipbook repo is absent."""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FILM = Path(__file__).resolve().parent
SCREENS = ROOT / "docs" / "assets" / "screens"
OUT_MP4 = ROOT / "demo" / "seg-flipbook.mp4"
SPEC = FILM / "agent-science.json"

W, H = 1280, 720
BG = (11, 13, 16)
PANEL = (18, 22, 28)
INK = (233, 237, 242)
MUTED = (139, 149, 163)
ACCENT = (180, 35, 24)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _header(draw: ImageDraw.ImageDraw, brand: str, label: str, timecode: str) -> None:
    draw.line([(52, 44), (W - 52, 44)], fill=(35, 42, 51), width=1)
    draw.text((52, 18), brand, font=_font(14), fill=MUTED)
    draw.text((W - 52, 18), f"{timecode} · {label.split('·', 1)[-1].strip()}", font=_font(14), fill=MUTED, anchor="ra")


def _title_slide(scene: dict, brand: str) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    _header(draw, brand, scene["label"], scene["time"])
    y = 220
    for line in scene.get("headline", []):
        draw.text((52, y), line, font=_font(52, bold=True), fill=INK)
        y += 62
    if scene.get("subline"):
        draw.text((52, y + 8), scene["subline"], font=_font(22), fill=MUTED)
    if scene.get("footer"):
        draw.text((52, H - 90), scene["footer"], font=_font(20), fill=ACCENT)
    return img


def _stamp_slide(scene: dict, brand: str) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    _header(draw, brand, scene["label"], scene["time"])
    draw.text((52, 260), scene["headline"][0], font=_font(56, bold=True), fill=ACCENT)
    draw.text((52, 360), scene.get("subline", ""), font=_font(24), fill=MUTED)
    return img


def _compound_slide(scene: dict, brand: str) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    _header(draw, brand, scene["label"], scene["time"])
    y = 200
    for line in scene.get("headline", []):
        draw.text((52, y), line, font=_font(48, bold=True), fill=INK)
        y += 58
    draw.text((52, y + 12), scene.get("subline", ""), font=_font(22), fill=ACCENT)
    boxes = [("RUN A", "1 Parallel"), ("RUN B", "0 Parallel"), ("CORPUS", "1 hit")]
    bx = 52
    for title, val in boxes:
        draw.rounded_rectangle((bx, 430, bx + 220, 520), radius=8, fill=PANEL, outline=(35, 42, 51))
        draw.text((bx + 16, 448), title, font=_font(14), fill=MUTED)
        draw.text((bx + 16, 472), val, font=_font(28, bold=True), fill=INK)
        bx += 250
    return img


def _screenshot_slide(scene: dict, brand: str) -> Image.Image:
    src = SCREENS / scene["asset"]
    if not src.exists():
        raise SystemExit(f"missing screenshot: {src}")
    shot = Image.open(src).convert("RGB")
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    _header(draw, brand, scene["label"], scene["time"])
    area = (40, 70, W - 40, H - 70)
    aw, ah = area[2] - area[0], area[3] - area[1]
    sw, sh = shot.size
    scale = min(aw / sw, ah / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    shot = shot.resize((nw, nh), Image.Resampling.LANCZOS)
    x = area[0] + (aw - nw) // 2
    y = area[1] + (ah - nh) // 2
    img.paste(shot, (x, y))
    if scene.get("caption"):
        draw.rectangle((40, H - 58, W - 40, H - 24), fill=PANEL)
        draw.text((56, H - 50), scene["caption"], font=_font(18), fill=MUTED)
    return img


def render_scene(scene: dict, brand: str) -> Image.Image:
    kind = scene["type"]
    if kind == "title":
        return _title_slide(scene, brand)
    if kind == "stamp":
        return _stamp_slide(scene, brand)
    if kind == "compound":
        return _compound_slide(scene, brand)
    if kind == "screenshot":
        return _screenshot_slide(scene, brand)
    raise SystemExit(f"unknown scene type: {kind}")


def scene_to_clip(png: Path, duration: float, out: Path) -> None:
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-loop", "1", "-i", str(png),
            "-t", f"{duration:.3f}",
            "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
            "-r", "30",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            str(out),
        ],
        check=True,
    )


def concat_clips(clips: list[Path], out: Path) -> None:
    lst = out.with_suffix(".txt")
    lst.write_text("".join(f"file '{c}'\n" for c in clips))
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)],
        check=True,
    )


def main() -> int:
    spec = json.loads(SPEC.read_text())
    brand = spec.get("brand", "AGENT SCIENCE")
    scenes = spec["scenes"]
    OUT_MP4.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="as-film-") as tmp:
        tmp_path = Path(tmp)
        clips: list[Path] = []
        for i, scene in enumerate(scenes):
            png = tmp_path / f"scene-{i:02d}.png"
            clip = tmp_path / f"scene-{i:02d}.mp4"
            render_scene(scene, brand).save(png)
            scene_to_clip(png, float(scene["duration"]), clip)
            clips.append(clip)
            print(f"scene {i:02d} {scene['id']:12s} {scene['duration']:5.1f}s")
        concat_path = tmp_path / "concat.mp4"
        concat_clips(clips, concat_path)
        concat_path.replace(OUT_MP4)

    dur = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(OUT_MP4)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    print(f"WROTE {OUT_MP4}  {dur}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
