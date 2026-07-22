import fitz
import re
import sys

def get_section(path, start, end):
    doc = fitz.open(path)
    text = doc[0].get_text("text", sort=True)
    doc.close()
    text = text.replace("\u2022", "•").replace("\ufffd", "•")
    m = re.search(rf"{re.escape(start)}\s*\n(.*?)\n\s*{re.escape(end)}", text, re.DOTALL)
    return m.group(1) if m else None

def parse_achievements(body):
    if not body:
        return []
    parts = re.split(r"(?:^|\n)\s*•\s*(?:\n|$)?", body)
    items = []
    for p in parts:
        t = re.sub(r"\s+", " ", p).strip()
        if t and ":" in t:
            items.append(t)
    return items

def parse_skill_lines(body):
    if not body:
        return []
    body = re.sub(r"(?:^|\n)\s*•\s*", "\n", body)
    body = re.sub(r"\s+", " ", body).strip()
    labels = ["Engines & Frameworks", "Languages", "Target Platforms", "Tools & IDEs"]
    results = []
    for i, label in enumerate(labels):
        token = label + ":"
        if token not in body:
            continue
        start = body.index(token) + len(token)
        rest = body[start:]
        next_pos = len(rest)
        for nl in labels[i + 1 :]:
            idx = rest.find(nl + ":")
            if idx != -1:
                next_pos = min(next_pos, idx)
        val = rest[:next_pos].strip()
        results.append(f"{label}: {val}")
    return results

def colon_spacing(path, phrase):
    doc = fitz.open(path)
    text = doc[0].get_text("text")
    doc.close()
    idx = text.find(phrase)
    if idx == -1:
        return None
    return repr(text[idx : idx + len(phrase) + 5])

paths = [
    ("MAIN", r"C:\Work\Portfolio\miniport-html5up\portfolio\PrakashAngappan-Resume.pdf"),
    ("ATS", r"C:\Users\aprak\Downloads\files\Prakash_Angappan_Resume_ATS.pdf"),
]

for label, path in paths:
    print("=" * 70, label, path)
    ka_body = get_section(path, "KEY ACHIEVEMENTS", "TECHNICAL SKILLS")
    ts_body = get_section(path, "TECHNICAL SKILLS", "PROFESSIONAL EXPERIENCE")

    achievements = parse_achievements(ka_body)
    print("\nKEY ACHIEVEMENTS (%d):" % len(achievements))
    for i, a in enumerate(achievements, 1):
        print("%d. %s" % (i, a))

    skills = parse_skill_lines(ts_body)
    print("\nTECHNICAL SKILLS (%d lines):" % len(skills))
    for s in skills:
        print(s)

    print("\nColon spacing check (Revenue...):")
    print(colon_spacing(path, "Casino Mini Games):"))
    print()
