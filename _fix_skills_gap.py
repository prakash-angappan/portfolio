"""Increase gap between Professional Summary and SKILLS heading only."""
from __future__ import annotations

import shutil
from pathlib import Path

import fitz

SRC = Path(r"C:\Users\aprak\Downloads\files\Prakash_Angappan_Resume.pdf")
OUT = SRC
OUT_PORTFOLIO = Path(r"C:\Work\Portfolio\miniport-html5up\portfolio\PrakashAngappan-Resume.pdf")
ROOT = Path(r"C:\Work\Portfolio\miniport-html5up")

# Shift SKILLS header (+ its underline drawings nearby) downward
SHIFT = 8.0
ACCENT = (0x1F / 255, 0x36 / 255, 0x64 / 255)  # ~#1F3664 from original title color 2046052


def main():
    doc = fitz.open(SRC)
    page = doc[0]

    # Find SKILLS text span
    skills_span = None
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                if span["text"].strip() == "SKILLS":
                    skills_span = dict(span)
                    break

    if not skills_span:
        raise SystemExit("SKILLS heading not found")

    rect = fitz.Rect(skills_span["bbox"])
    # Also cover the underline under SKILLS (drawn slightly below the text)
    underline_band = fitz.Rect(34, rect.y1 - 1, 578, rect.y1 + 6)

    # Measure gap before change
    # Find last summary line
    last_sum = None
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            text = "".join(s["text"] for s in line["spans"]).replace("\xa0", " ")
            if "lifecycle" in text.lower():
                last_sum = fitz.Rect(line["bbox"])

    before = rect.y0 - (last_sum.y1 if last_sum else 0)
    print(f"Gap before: {before:.1f}pt")

    # Redact SKILLS text
    page.add_redact_annot(
        fitz.Rect(rect.x0 - 1, rect.y0 - 1, rect.x1 + 2, rect.y1 + 2),
        fill=(1, 1, 1),
    )
    # White out old underline area
    page.add_redact_annot(underline_band, fill=(1, 1, 1))
    page.apply_redactions()

    # Redraw SKILLS lower
    font = fitz.Font(fontfile=str(ROOT / "_Carlito-Bold.ttf"))
    tw = fitz.TextWriter(page.rect)
    new_origin = (skills_span["origin"][0], skills_span["origin"][1] + SHIFT)
    tw.append(fitz.Point(new_origin), "SKILLS", font=font, fontsize=skills_span["size"])
    tw.write_text(page, color=ACCENT)

    # Redraw underline under new SKILLS (match original style: thin accent line)
    new_y = rect.y1 + SHIFT + 1.5
    page.draw_line(
        fitz.Point(34.1, new_y),
        fitz.Point(577.9, new_y),
        color=ACCENT,
        width=1.0,
    )

    tmp = OUT.with_suffix(".tmp.pdf")
    doc.save(tmp, garbage=4, deflate=True)
    doc.close()
    shutil.move(str(tmp), str(OUT))
    shutil.copy2(OUT, OUT_PORTFOLIO)

    v = fitz.open(OUT)
    page = v[0]
    skills_y = None
    last_sum = None
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            text = "".join(s["text"] for s in line["spans"]).replace("\xa0", " ")
            if text.strip() == "SKILLS":
                skills_y = fitz.Rect(line["bbox"]).y0
            if "lifecycle" in text.lower():
                last_sum = fitz.Rect(line["bbox"])
    gap = skills_y - last_sum.y1
    print(f"Gap after: {gap:.1f}pt")
    pix = page.get_pixmap(clip=fitz.Rect(20, 85, 590, 240), matrix=fitz.Matrix(2, 2))
    pix.save(str(ROOT / "_sum_gap_preview.png"))
    v.close()
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
