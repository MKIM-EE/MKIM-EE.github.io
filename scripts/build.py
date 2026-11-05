#!/usr/bin/env python3
"""Pre-render data/*.json into static HTML so crawlers and LLM agents can read the site.

Usage (from repo root):  python scripts/build.py
Re-run this whenever data/*.json changes, then commit the regenerated HTML.

Each page contains marker pairs like
    <!--BUILD:sci-list--> ... <!--/BUILD:sci-list-->
and this script replaces whatever is between them.
"""
import json
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://mkim-ee.github.io"


def load(name):
    with open(ROOT / "data" / name, encoding="utf-8") as f:
        return json.load(f)


def esc(s):
    return escape(str(s), quote=True)


def highlight(authors, name):
    out = esc(authors)
    if name:
        out = out.replace(esc(name), f"<strong>{esc(name)}</strong>", 1)
    return out


def delay(i):
    return f"{i * 0.1:.1f}"


# ---------- renderers ----------
def pub_list(items, start=0):
    rows = []
    for i, it in enumerate(items):
        title = f'<span class="pub-title">{esc(it["title"])}</span>'
        if it.get("url"):
            title = (f'<a href="{esc(it["url"])}" target="_blank" rel="noopener noreferrer" '
                     f'class="pub-title-link">{title}</a>')
        rows.append(
            f'<div class="pub-item fade-in" style="animation-delay: {delay(start + i)}s">'
            f'{title}'
            f'<p class="pub-authors">{highlight(it["authors"], it.get("highlight"))}</p>'
            f'<p class="pub-venue">{esc(it["venue"])}, {esc(it["date"])}</p>'
            f'</div>'
        )
    return "\n".join(rows)


def patent_list(items, start=0):
    rows = []
    for i, it in enumerate(items):
        rows.append(
            f'<div class="pub-item fade-in" style="animation-delay: {delay(start + i)}s">'
            f'<span class="pub-title">{esc(it["title"])}</span>'
            f'<p class="pub-authors">{highlight(it["authors"], it.get("highlight"))}</p>'
            f'<p class="pub-venue">Patent Number: {esc(it["number"])}, {esc(it["date"])}</p>'
            f'</div>'
        )
    return "\n".join(rows)


def timeline(items, title_key, desc_key):
    return "\n".join(
        f'<div class="timeline-item"><div class="timeline-date">{esc(e["period"])}</div>'
        f'<div class="timeline-title">{esc(e[title_key])}</div>'
        f'<div class="timeline-description">{esc(e[desc_key])}</div></div>'
        for e in items
    )


PUBLISHER_LOGOS = {
    "IEEE": '<svg viewBox="0 0 120 40" xmlns="http://www.w3.org/2000/svg" aria-label="IEEE"><text x="0" y="30" font-family="Arial,sans-serif" font-weight="900" font-size="32" fill="#00629B">IEEE</text></svg>',
    "Elsevier": '<svg viewBox="0 0 120 40" xmlns="http://www.w3.org/2000/svg" aria-label="Elsevier"><text x="0" y="28" font-family="Arial,sans-serif" font-weight="700" font-size="20" fill="#FF6B00">Elsevier</text></svg>',
    "Wiley": '<svg viewBox="0 0 80 40" xmlns="http://www.w3.org/2000/svg" aria-label="Wiley"><text x="0" y="28" font-family="Arial,sans-serif" font-weight="700" font-size="22" fill="#003A70">Wiley</text></svg>',
    "Springer": '<svg viewBox="0 0 120 40" xmlns="http://www.w3.org/2000/svg" aria-label="Springer"><text x="0" y="28" font-family="Arial,sans-serif" font-weight="700" font-size="20" fill="#FF6C00">Springer</text></svg>',
    "MDPI": '<svg viewBox="0 0 80 40" xmlns="http://www.w3.org/2000/svg" aria-label="MDPI"><text x="0" y="28" font-family="Arial,sans-serif" font-weight="700" font-size="22" fill="#444444">MDPI</text></svg>',
}
ROLE_CLASS = {"Reviewer": "role-reviewer", "AE": "role-ae", "Guest Editor": "role-guest-editor"}


def service_cards(items):
    rows = []
    for s in items:
        logo = PUBLISHER_LOGOS.get(s["publisher"]) or \
            f'<span class="service-publisher-text">{esc(s["publisher"])}</span>'
        rows.append(
            f'<div class="service-card"><div class="service-logo">{logo}</div>'
            f'<div class="service-journal">{esc(s["journal"])}</div>'
            f'<span class="service-role-badge {ROLE_CLASS.get(s["role"], "")}">{esc(s["role"])}</span></div>'
        )
    return "\n".join(rows)


def badges(bs):
    return "".join(f'<span class="badge {esc(b)}">{esc(b.capitalize())}</span>' for b in (bs or []))


def activities(items):
    return "\n".join(
        f'<div class="activity-item" style="animation-delay: {delay(i)}s">'
        f'<strong>{esc(a["date"])}</strong><span>{esc(a["description"])}{badges(a.get("badges"))}</span></div>'
        for i, a in enumerate(items)
    )


def projects(items):
    return "\n".join(
        f'<div class="research-project fade-in" style="animation-delay: {delay(i)}s">'
        f'<div class="project-image-container"><img src="../assets/images/{esc(p["image"])}" '
        f'alt="{esc(p["image_alt"])}" class="project-image"></div>'
        f'<div class="project-details"><div class="project-title">{esc(p["title"])}</div>'
        f'<div class="project-description">{esc(p["description"])}</div></div></div>'
        for i, p in enumerate(items)
    )


def scholar_stats(sc):
    cells = "".join(
        f'<div class="scholar-stat"><span class="scholar-num">{sc[k]}</span>'
        f'<span class="scholar-label">{label}</span></div>'
        for k, label in (("citations", "Citations"), ("h_index", "h-index"), ("i10_index", "i10-index")))
    return (f'<a class="scholar-stats" href="{esc(sc["url"])}" target="_blank" rel="noopener noreferrer" '
            f'title="Google Scholar, updated {esc(sc["updated"])}">{cells}</a>')


# ---------- marker replacement ----------
def fill(path, blocks):
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    for name, html in blocks.items():
        pat = re.compile(rf"(<!--BUILD:{re.escape(name)}-->)(.*?)(<!--/BUILD:{re.escape(name)}-->)", re.S)
        if not pat.search(text):
            sys.exit(f"marker BUILD:{name} not found in {path}")
        text = pat.sub(lambda m: f"{m.group(1)}\n{html}\n{m.group(3)}", text, count=1)
    p.write_text(text, encoding="utf-8", newline="\n")
    print("built", path)


def main():
    prof, jr, conf, pat, res = (load(f) for f in
                                ("profile.json", "journals.json", "conferences.json", "patents.json", "research.json"))

    fill("index.html", {
        "name": esc(f'{prof["name"]} ({prof["name_ko"]})'),
        "photo": f'<img src="{esc(prof["photo"])}" alt="{esc(prof["name"])}" id="profile-img" style="cursor: pointer;" />',
        "title": esc(prof["title"]),
        "affiliation": esc(prof["affiliation"]),
        "email": esc(prof["email"]),
        "interests": "<strong>Research Interests:</strong> " + esc(", ".join(prof["research_interests"])),
        "scholar": scholar_stats(load("scholar.json")),
        "links": "".join(
            f'<a href="{esc(l["url"])}" class="profile-link" target="_blank" rel="noopener noreferrer">{esc(l["label"])}</a>'
            for l in prof["links"]),
        "education": timeline(prof["education"], "degree", "institution"),
        "experiences": timeline(prof["experiences"], "company", "title"),
        "service": service_cards(prof["academic_service"]),
        "activities": activities(prof["academic_activities"]),
    })
    fill("research/index.html", {"projects": projects(res["projects"])})
    fill("journals/index.html", {
        "sci-list": pub_list(jr["sci"], 0),
        "kci-list": pub_list(jr["kci"], len(jr["sci"])),
    })
    fill("conferences/index.html", {
        "intl-conf-list": pub_list(conf["international"], 0),
        "dom-conf-list": pub_list(conf["domestic"], len(conf["international"])),
    })
    fill("patents/index.html", {
        "patent-reg-list": patent_list(pat["registration"], 0),
        "patent-app-list": patent_list(pat["application"], len(pat["registration"])),
    })


if __name__ == "__main__":
    main()
