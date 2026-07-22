"""Rebuild resume page-1 section spacing to be consistent (~13.7pt end→next title)."""
from __future__ import annotations

import shutil
from pathlib import Path

import fitz

BACKUP = Path(r"C:\Users\aprak\Downloads\files\Prakash_Angappan_Resume.backup.pdf")
OUT = Path(r"C:\Users\aprak\Downloads\files\Prakash_Angappan_Resume.pdf")
OUT_PORTFOLIO = Path(r"C:\Work\Portfolio\miniport-html5up\portfolio\PrakashAngappan-Resume.pdf")
ROOT = Path(r"C:\Work\Portfolio\miniport-html5up")

SUMMARY = (
    "Engineering leader with 17+ years of experience delivering 15+ games across "
    "console, PC and mobile. As Head of Engineering, I drive business success through "
    "predictable, on-time delivery while overseeing budgeting, technical strategy, "
    "resource planning, and cross-functional execution. I collaborate across Engineering, "
    "Design, Art, and QA to implement automation and AI-driven workflows that improve "
    "team productivity, reduce development friction, and optimize the entire game "
    "development lifecycle."
)

PROJECT_LINKS = {
    "Hands of Victory": "https://store.steampowered.com/app/2265080/Hands_of_Victory/",
    "Railflow": "https://play.google.com/store/apps/details?id=com.railflow.cargotransport",
    "Radiant Dark": "https://www.youtube.com/watch?v=T7I799DRj2U",
    "The Last Bastion": "https://store.steampowered.com/app/1520880/The_Last_Bastion/",
    "City Block Builder": "https://store.steampowered.com/app/1191800/City_Block_Builder/",
    "Jolly Rogers Pirates Rumble": "https://store.steampowered.com/app/876120/Jolly_Rogers_Pirates_Rumble/",
    "Desi Adda": "https://www.youtube.com/watch?v=UOg4AEiJsHs",
    "Cart Kings": "https://www.youtube.com/watch?v=T93d5E7Yhyo",
    "Kite Fight": "https://www.youtube.com/watch?v=KbZFrEOE95w",
}

LINK_BLUE = (0.05, 0.35, 0.85)
TEXT_DARK = (0x33 / 255, 0x33 / 255, 0x33 / 255)

FONTS = {
    "bold": fitz.Font(fontfile=str(ROOT / "_Carlito-Bold.ttf")),
    "regular": fitz.Font(fontfile=str(ROOT / "_Carlito-Regular.ttf")),
    "italic": fitz.Font(fontfile=str(ROOT / "_Carlito-Italic.ttf")),
}


def pad_rect(rect, pad=1.0):
    r = fitz.Rect(rect)
    return fitz.Rect(r.x0 - pad, r.y0 - pad, r.x1 + pad, r.y1 + pad)


def color_tuple(c: int):
    return ((c >> 16) & 255) / 255, ((c >> 8) & 255) / 255, (c & 255) / 255


def font_for(span_font: str) -> fitz.Font:
    if "Bold" in span_font:
        return FONTS["bold"]
    if "Italic" in span_font:
        return FONTS["italic"]
    return FONTS["regular"]


def find_line_containing(page, needle: str):
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            text = "".join(s["text"] for s in line.get("spans", []))
            if needle in text:
                return line
    return None


def find_span(page, exact_text: str, font_substr: str | None = None):
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                if span["text"] != exact_text:
                    continue
                if font_substr and font_substr not in span["font"]:
                    continue
                return span
    return None


def nearest_bullet(page, y_ref: float, x_max: float = 55.0):
    best, best_dy = None, 999.0
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                rect = fitz.Rect(span["bbox"])
                if rect.x1 > x_max or len(span["text"].strip()) > 2:
                    continue
                dy = abs(rect.y0 - y_ref)
                if dy < best_dy:
                    best_dy, best = dy, span
    return best if best_dy < 10 else None


def write_at_origin(page, items):
    by_color = {}
    for origin, text, font, fontsize, color in items:
        by_color.setdefault(color, []).append((origin, text, font, fontsize))
    for color, group in by_color.items():
        tw = fitz.TextWriter(page.rect)
        for origin, text, font, fontsize in group:
            tw.append(fitz.Point(origin), text, font=font, fontsize=fontsize)
        tw.write_text(page, color=color)


def wrap_text(text: str, font: fitz.Font, fontsize: float, max_width: float) -> list[str]:
    words = text.split()
    lines, current = [], ""
    for w in words:
        trial = w if not current else current + " " + w
        if font.text_length(trial, fontsize=fontsize) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def replace_summary(page):
    """4 lines at original 16pt leading so gap to SKILLS matches other sections (~13.7pt)."""
    lines = []
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            y = line["bbox"][1]
            if 115 <= y <= 180:
                text = "".join(s["text"] for s in line["spans"])
                if text.strip():
                    lines.append(line)
    if len(lines) < 3:
        raise RuntimeError("Summary lines not found")

    for line in lines:
        page.add_redact_annot(pad_rect(line["bbox"], 1.0), fill=(1, 1, 1))
    page.apply_redactions()

    font = FONTS["regular"]
    x0 = 34.1
    first_origin_y = lines[0]["spans"][0]["origin"][1]
    line_gap = 16.0  # original leading → last line ends ~178, SKILLS at 191.9 → ~13.7pt

    fontsize, max_width = 10.5, 555.0
    wrapped = wrap_text(SUMMARY, font, fontsize, max_width)
    if len(wrapped) > 4:
        wrapped = wrap_text(SUMMARY, font, fontsize, 565.0)
    if len(wrapped) > 4:
        fontsize = 10.25
        wrapped = wrap_text(SUMMARY, font, fontsize, 560.0)
    if len(wrapped) > 4:
        raise RuntimeError(f"Summary wraps to {len(wrapped)} lines")

    items = [
        ((x0, first_origin_y + i * line_gap), text, font, fontsize, TEXT_DARK)
        for i, text in enumerate(wrapped)
    ]
    write_at_origin(page, items)
    print(f"Summary: {len(wrapped)} lines @ {fontsize}pt, leading {line_gap}")


def fix_technical_domain(page):
    span = None
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for s in line.get("spans", []):
                if "Unity/C# Client Architecture" in s["text"]:
                    span = dict(s)
                    break
    if not span:
        raise RuntimeError("Technical Domain Unity/C# span not found")

    new_text = span["text"].replace("Unity/C# Client Architecture", "Unity")
    page.add_redact_annot(pad_rect(span["bbox"], 0.8), fill=(1, 1, 1))
    page.apply_redactions()
    write_at_origin(
        page,
        [(span["origin"], new_text, FONTS["regular"], span["size"], color_tuple(span["color"]))],
    )


def remove_languages_and_shift(page):
    lang_line = find_line_containing(page, "Languages:")
    plat_line = find_line_containing(page, "Target Platforms:")
    tools_line = find_line_containing(page, "Tools & IDEs:")
    if not all([lang_line, plat_line, tools_line]):
        raise RuntimeError("Missing Technical Skills lines")

    lang_rect = fitz.Rect(lang_line["bbox"])
    plat_rect = fitz.Rect(plat_line["bbox"])
    tools_rect = fitz.Rect(tools_line["bbox"])

    lang_bullet = nearest_bullet(page, lang_rect.y0)
    plat_bullet = nearest_bullet(page, plat_rect.y0)
    tools_bullet = nearest_bullet(page, tools_rect.y0)

    plat_spans = [dict(s) for s in plat_line["spans"]]
    tools_spans = [dict(s) for s in tools_line["spans"]]
    plat_bullet = dict(plat_bullet) if plat_bullet else None
    tools_bullet = dict(tools_bullet) if tools_bullet else None

    for span in (lang_bullet, plat_bullet, tools_bullet):
        if span:
            page.add_redact_annot(pad_rect(span["bbox"], 1.5), fill=(1, 1, 1))
    page.add_redact_annot(pad_rect(lang_rect, 1.2), fill=(1, 1, 1))
    page.add_redact_annot(pad_rect(plat_rect, 1.2), fill=(1, 1, 1))
    page.add_redact_annot(pad_rect(tools_rect, 1.2), fill=(1, 1, 1))
    page.apply_redactions()

    shift_plat = lang_rect.y0 - plat_rect.y0
    shift_tools = plat_rect.y0 - tools_rect.y0

    items = []
    if plat_bullet:
        ox, oy = plat_bullet["origin"]
        items.append(((ox, oy + shift_plat), "•", FONTS["regular"], plat_bullet["size"], color_tuple(plat_bullet["color"])))
    for s in plat_spans:
        ox, oy = s["origin"]
        items.append(((ox, oy + shift_plat), s["text"], font_for(s["font"]), s["size"], color_tuple(s["color"])))
    if tools_bullet:
        ox, oy = tools_bullet["origin"]
        items.append(((ox, oy + shift_tools), "•", FONTS["regular"], tools_bullet["size"], color_tuple(tools_bullet["color"])))
    for s in tools_spans:
        ox, oy = s["origin"]
        items.append(((ox, oy + shift_tools), s["text"], font_for(s["font"]), s["size"], color_tuple(s["color"])))
    write_at_origin(page, items)


def linkify_projects(page):
    targets = []
    for title, url in PROJECT_LINKS.items():
        span = find_span(page, title, "Italic") or find_span(page, title)
        if not span:
            print("WARNING missing:", title)
            continue
        targets.append((title, url, dict(span)))

    for _, _, span in targets:
        page.add_redact_annot(pad_rect(span["bbox"], 0.9), fill=(1, 1, 1))
    page.apply_redactions()

    items = [(span["origin"], title, FONTS["italic"], span["size"], LINK_BLUE) for title, url, span in targets]
    write_at_origin(page, items)
    for title, url, span in targets:
        page.insert_link({"kind": fitz.LINK_URI, "from": pad_rect(span["bbox"], 1.0), "uri": url})
    print(f"Linked {len(targets)} projects")


def measure_gaps(page):
    rows = []
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            t = "".join(s["text"] for s in line["spans"]).replace("\xa0", " ").strip()
            if t:
                rows.append((line["bbox"][1], line["bbox"][3], t))
    rows.sort()

    def gap_before(title: str):
        idx = next(i for i, (_, _, t) in enumerate(rows) if t == title)
        prev = rows[idx - 1]
        return title, rows[idx][0] - prev[1], prev[2][:40]

    gaps = [
        gap_before("SKILLS"),
        gap_before("KEY ACHIEVEMENTS"),
        gap_before("TECHNICAL SKILLS"),
    ]
    for name, gap, prev in gaps:
        print(f"  {prev!r} -> {name}: {gap:.1f}pt")
    return gaps


def main():
    doc = fitz.open(BACKUP)
    replace_summary(doc[0])
    fix_technical_domain(doc[0])
    remove_languages_and_shift(doc[0])
    linkify_projects(doc[1])

    tmp = OUT.with_suffix(".tmp.pdf")
    doc.save(tmp, garbage=4, deflate=True)
    doc.close()
    shutil.move(str(tmp), str(OUT))
    shutil.copy2(OUT, OUT_PORTFOLIO)

    v = fitz.open(OUT)
    print("Section gaps:")
    gaps = measure_gaps(v[0])
    # All end→title gaps should be ~13.7 (tolerance ±2)
    for name, gap, _ in gaps:
        assert 11.5 <= gap <= 16.0, f"{name} gap out of range: {gap:.1f}"
    print("OK - consistent section spacing")
    print("Wrote", OUT)
    v.close()


if __name__ == "__main__":
    main()
