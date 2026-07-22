#!/usr/bin/env python3
"""Fetch and resize portfolio icons to 64x64 RGBA PNGs."""

from __future__ import annotations

import io
import os
import ssl
import struct
import sys
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
ICONS = ROOT / "portfolio" / "images" / "icons"

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

ICON_SOURCES: dict[str, tuple[str, str]] = {
    "frameworks/playmaker.png": (
        "https://assetstorev1-prd-cdn.unity3d.com/key-image/5c8b0d53-e77b-44af-9970-961e1f06492d.png",
        "Unity Asset Store Playmaker package 368 key-image (classic PM1)",
    ),
    "tools/sourcetree.png": (
        "https://cdn.jsdelivr.net/npm/@atlassian/brand-logos@1.3.0/dist/products/icons/sourcetree-neutral.svg",
        "Atlassian Design brand-logos sourcetree-neutral.svg",
    ),
    "tools/jira.png": (
        "https://cdn.jsdelivr.net/npm/@atlassian/brand-logos@1.3.0/dist/products/icons/jira-neutral.svg",
        "Atlassian Design brand-logos jira-neutral.svg",
    ),
    "tools/basecamp.png": (
        "https://basecamp.com/assets/images/general/logo-mark.webp",
        "Basecamp official logo mark (basecamp.com/assets/images/general/logo-mark.webp)",
    ),
    "tools/prodg.png": (
        "https://upload.wikimedia.org/wikipedia/commons/0/00/PlayStation_logo.svg",
        "Official PlayStation logo SVG (Wikimedia Commons; legacy ProDG toolchain association)",
    ),
}

FALLBACK_SOURCES: dict[str, tuple[str, str]] = {
    "tools/basecamp.png": (
        "https://basecamp.com/assets/images/help/basecamp.png",
        "Basecamp help site product logo PNG",
    ),
}


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "portfolio-icon-updater/1.0"})
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=30) as resp:
        return resp.read()


def is_valid_png(data: bytes) -> bool:
    return data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) >= 24


def load_image(data: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(data))
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    return img


def render_svg_to_rgba(svg_bytes: bytes, size: int = 512) -> Image.Image:
    try:
        import cairosvg  # type: ignore

        png_data = cairosvg.svg2png(bytestring=svg_bytes, output_width=size, output_height=size)
        return load_image(png_data)
    except Exception:
        pass

    try:
        from svglib.svglib import svg2rlg  # type: ignore
        from reportlab.graphics import renderPM  # type: ignore

        drawing = svg2rlg(io.BytesIO(svg_bytes))
        if drawing is None:
            raise ValueError("svg2rlg returned None")
        scale = size / max(drawing.width, drawing.height)
        drawing.width = drawing.width * scale
        drawing.height = drawing.height * scale
        drawing.scale(scale, scale)
        png_data = renderPM.drawToString(drawing, fmt="PNG")
        return load_image(png_data)
    except Exception as exc:
        raise RuntimeError(f"SVG rendering failed: {exc}") from exc


def to_icon_png(img: Image.Image, out_size: int = 64) -> bytes:
    w, h = img.size
    side = max(w, h)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(img, ((side - w) // 2, (side - h) // 2))
    resized = canvas.resize((out_size, out_size), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    resized.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def process_icon(rel_path: str, url: str, note: str) -> tuple[str, int, bool]:
    out_path = ICONS / rel_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    raw = fetch_bytes(url)
    lower_url = url.lower()
    if lower_url.endswith(".svg") or raw.lstrip().startswith(b"<"):
        img = render_svg_to_rgba(raw, size=512)
    else:
        img = load_image(raw)

    png_bytes = to_icon_png(img, 64)
    out_path.write_bytes(png_bytes)
    valid = is_valid_png(png_bytes)
    return url, len(png_bytes), valid


def main() -> int:
    results: dict[str, tuple[str, int, bool]] = {}

    for rel_path, (url, note) in ICON_SOURCES.items():
        try:
            results[rel_path] = (*process_icon(rel_path, url, note),)
            print(f"OK  {rel_path}")
            print(f"    source: {url}")
            print(f"    note:   {note}")
            print(f"    bytes:  {results[rel_path][1]}")
            print(f"    png:    {'valid' if results[rel_path][2] else 'INVALID'}")
        except Exception as primary_exc:
            fallback = FALLBACK_SOURCES.get(rel_path)
            if not fallback:
                print(f"FAIL {rel_path}: {primary_exc}", file=sys.stderr)
                return 1
            fb_url, fb_note = fallback
            try:
                results[rel_path] = (*process_icon(rel_path, fb_url, fb_note),)
                print(f"OK  {rel_path} (fallback)")
                print(f"    source: {fb_url}")
                print(f"    note:   {fb_note}")
                print(f"    bytes:  {results[rel_path][1]}")
                print(f"    png:    {'valid' if results[rel_path][2] else 'INVALID'}")
                print(f"    primary failed: {primary_exc}")
            except Exception as fb_exc:
                print(f"FAIL {rel_path}: primary={primary_exc}; fallback={fb_exc}", file=sys.stderr)
                return 1

    lyra = ICONS / "frameworks" / "lyra.png"
    if lyra.exists():
        lyra.unlink()
        print(f"DEL frameworks/lyra.png")

    print("\n--- SUMMARY ---")
    for key in [
        "frameworks/playmaker.png",
        "tools/prodg.png",
        "tools/sourcetree.png",
        "tools/jira.png",
        "tools/basecamp.png",
    ]:
        url, size, valid = results[key]
        print(f"{key}: {url} | {size} bytes | PNG {'OK' if valid else 'BAD'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
