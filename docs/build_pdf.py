"""Build the whole documentation set into one PDF book.

    python docs/build_pdf.py                      # -> docs/Nani-AI-Voice-Plush-Documentation.pdf

Markdown -> one styled HTML page (cover, contents, three parts) -> headless
Chrome/Edge prints it to PDF. Mermaid diagrams are rendered by mermaid.js in
the browser, so an internet connection is needed for the diagrams.

Needs: pip install markdown pypdf ; Google Chrome or Microsoft Edge.
"""
import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

import markdown

DOCS = Path(__file__).resolve().parent
REPO = DOCS.parent

PARTS = [
    ("Part I", "Tutorial — Build Your Own Talking Nani",
     "For readers with no background: rebuild the toy's hearing, speaking and bridge step by step.",
     ["tutorial/README.md"] + [f"tutorial/{n}" for n in sorted(
         p.name for p in (DOCS / "tutorial").glob("0*.md"))]),
    ("Part II", "Reference Documentation",
     "For engineers and reviewers: what was built, how it works, what was measured.",
     ["01-overview.md", "02-architecture.md", "03-hardware.md", "04-firmware.md",
      "05-laptop-brain.md", "06-results.md", "07-operations-runbook.md", "08-testing-quality.md",
      "09-project-history.md", "10-known-issues-roadmap.md"]),
    ("Part III", "Decisions, Terms and Sources",
     "The architecture decision records, the glossary, the references and the changelog.",
     ["adr/README.md"] + [f"adr/{p.name}" for p in sorted((DOCS / "adr").glob("0*.md"))]
     + ["glossary.md", "references.md", "../CHANGELOG.md"]),
]

CSS = r"""
@page { size: A4; margin: 20mm 18mm 20mm 18mm;
        @bottom-center { content: counter(page); font: 9pt 'Segoe UI', sans-serif; color: #898781; } }
@page :first { @bottom-center { content: none; } }
:root { --ink:#1b1b1a; --ink2:#52514e; --muted:#898781; --rule:#e1e0d9; --accent:#256abf;
        --accent-soft:#eef4fc; --code-bg:#f5f5f2; }
* { box-sizing: border-box; }
body { font: 10.5pt/1.55 Cambria, Georgia, 'Times New Roman', serif; color: var(--ink); margin: 0; }
h1, h2, h3, h4, .cover, .part, .toc { font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; }
h1 { font-size: 22pt; line-height: 1.2; margin: 0 0 6mm; color: var(--ink);
     padding-bottom: 3mm; border-bottom: 2px solid var(--accent); }
h2 { font-size: 14pt; margin: 8mm 0 2.5mm; color: var(--ink); break-after: avoid; }
h3 { font-size: 11.5pt; margin: 6mm 0 2mm; color: var(--ink2); break-after: avoid; }
p, li { orphans: 3; widows: 3; }
a { color: var(--accent); text-decoration: none; }
hr { border: 0; border-top: 1px solid var(--rule); margin: 6mm 0; }
code { font: 8.8pt Consolas, 'Cascadia Mono', monospace; background: var(--code-bg);
       padding: 0.5px 3px; border-radius: 3px; }
pre { background: var(--code-bg); border: 1px solid var(--rule); border-left: 3px solid var(--accent);
      border-radius: 4px; padding: 3mm 4mm; white-space: pre-wrap; word-break: break-word;
      font-size: 8.6pt; line-height: 1.45; break-inside: avoid; }
pre code { background: none; padding: 0; font-size: inherit; }
table { border-collapse: collapse; width: 100%; margin: 3mm 0 4mm; font-size: 9pt;
        font-family: 'Segoe UI', Arial, sans-serif; break-inside: auto; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
th { text-align: left; background: #f3f3f0; color: var(--ink); font-weight: 600; }
th, td { border-bottom: 1px solid var(--rule); padding: 1.6mm 2.2mm; vertical-align: top; }
table.meta { width: auto; font-size: 8.8pt; margin-bottom: 6mm; }
table.meta thead { display: none; }
table.meta td:first-child { color: var(--muted); padding-right: 6mm; }
blockquote { margin: 4mm 0; padding: 2.5mm 4mm; border-left: 4px solid var(--rule);
             background: #fafaf8; border-radius: 0 4px 4px 0; break-inside: avoid; }
blockquote p { margin: 1mm 0; }
blockquote.idea { border-color: var(--accent); background: var(--accent-soft); }
blockquote.check { border-color: #0ca30c; background: #effaef; }
blockquote.warn { border-color: #ec835a; background: #fdf3ee; }
img { max-width: 100%; display: block; margin: 4mm auto; break-inside: avoid; }
p > em:only-child { display: block; color: var(--ink2); font-size: 9pt; text-align: center; }
.mermaid { text-align: center; margin: 5mm 0; break-inside: avoid; background: none; border: 0; }
section.doc { break-before: page; }
.doc-path { font: 8pt 'Segoe UI', sans-serif; color: var(--muted); margin-bottom: 1mm;
            text-transform: uppercase; letter-spacing: .06em; }
.cover { height: 250mm; display: flex; flex-direction: column; justify-content: center; }
.cover .kicker { color: var(--accent); font-weight: 600; letter-spacing: .14em; text-transform: uppercase; font-size: 10pt; }
.cover h1 { font-size: 34pt; border: 0; margin: 4mm 0 2mm; padding: 0; }
.cover .sub { font-size: 15pt; color: var(--ink2); margin-bottom: 18mm; }
.cover .facts { font-size: 10pt; color: var(--ink2); border-top: 2px solid var(--accent); padding-top: 5mm; }
.cover .facts div { margin: 1.2mm 0; }
.part { break-before: page; height: 240mm; display: flex; flex-direction: column; justify-content: center; }
.part .num { color: var(--accent); font-weight: 600; letter-spacing: .14em; text-transform: uppercase; }
.part h1 { font-size: 28pt; border: 0; margin: 3mm 0; }
.part p { font-size: 12pt; color: var(--ink2); max-width: 140mm; }
.toc { break-before: page; }
.toc h1 { font-size: 20pt; }
.toc .p { margin: 5mm 0 1.5mm; font-weight: 600; color: var(--accent); }
.toc a { display: flex; justify-content: space-between; color: var(--ink); padding: 0.9mm 0;
         border-bottom: 1px dotted var(--rule); font-size: 10pt; }
.toc a .pg { color: var(--muted); font-variant-numeric: tabular-nums; }
"""


def slug(rel):
    return "doc-" + re.sub(r"[^a-z0-9]+", "-", rel.lower()).strip("-")


def title_of(md_text):
    m = re.search(r"^# (.+)$", md_text, flags=re.M)
    return m.group(1).strip() if m else "Untitled"


def convert(rel, all_rels):
    path = (DOCS / rel).resolve()
    text = path.read_text(encoding="utf-8")
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])

    # Mermaid code blocks -> live diagrams.
    body = re.sub(r'<pre><code class="language-mermaid">(.*?)</code></pre>',
                  r'<pre class="mermaid">\1</pre>', body, flags=re.S)

    # Images -> absolute file URIs.
    def img(m):
        return f'src="{(path.parent / html.unescape(m.group(1))).resolve().as_uri()}"'
    body = re.sub(r'src="(?!http)([^"]+)"', img, body)

    # Links: to another doc in the book -> in-PDF jump; to repo files -> plain path text.
    def link(m):
        href, label = html.unescape(m.group(1)), m.group(2)
        if href.startswith(("http://", "https://", "mailto:", "#")):
            return m.group(0)
        target = (path.parent / href.split("#")[0]).resolve()
        for r in all_rels:
            if (DOCS / r).resolve() == target:
                return f'<a href="#{slug(r)}">{label}</a>'
        return f"<span>{label}</span>"
    body = re.sub(r'<a href="([^"]+)">(.*?)</a>', link, body, flags=re.S)

    # Callout boxes by their leading emoji.
    for emoji, cls in (("💡", "idea"), ("✅", "check"), ("⚠️", "warn")):
        body = re.sub(rf"<blockquote>\s*<p>{emoji}", f'<blockquote class="{cls}">\n<p>{emoji}', body)

    # The "| | |" metadata table at the top of a doc: an empty header row.
    body = re.sub(r"<table>\s*<thead>\s*<tr>\s*<th></th>\s*<th></th>",
                  '<table class="meta"><thead><tr><th></th><th></th>', body, count=1)

    return title_of(text), f'<section class="doc" id="{slug(rel)}">' \
                           f'<div class="doc-path">{html.escape(rel.replace("../", ""))}</div>{body}</section>'


def build_html(pages=None):
    """`pages` maps doc rel-path -> printed page number (filled in on the second pass)."""
    pages = pages or {}
    all_rels = [r for _, _, _, rels in PARTS for r in rels]
    toc, parts_html = [], []
    for num, name, blurb, rels in PARTS:
        toc.append(f'<div class="p">{num} · {name}</div>')
        chunk = [f'<div class="part"><div class="num">{num}</div><h1>{name}</h1><p>{blurb}</p></div>']
        for rel in rels:
            title, sec = convert(rel, all_rels)
            toc.append(f'<a href="#{slug(rel)}"><span>{html.escape(title)}</span>'
                       f'<span class="pg">{pages.get(rel, "")}</span></a>')
            chunk.append(sec)
        parts_html.append("\n".join(chunk))

    cover = f"""<div class="cover">
      <div class="kicker">Project Documentation</div>
      <h1>Nani — AI Voice Plush</h1>
      <div class="sub">An ESP32-S3 talking toy connected to the Tutor Grandma web app</div>
      <div class="facts">
        <div>Hardware add-on for the Tutor Grandma buildathon project · Rayon Biswas</div>
        <div>Toy firmware · laptop bridge · website integration · tests</div>
        <div>Document set 1.0 · built {date.today().isoformat()}</div>
      </div></div>"""
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Nani AI Voice Plush Documentation</title>
<style>{CSS}</style>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>mermaid.initialize({{startOnLoad: true, theme: "neutral",
  flowchart: {{useMaxWidth: true}}, themeVariables: {{fontFamily: "Segoe UI, Arial"}}}});</script>
</head><body>{cover}<div class="toc"><h1>Contents</h1>{"".join(toc)}</div>
{"".join(parts_html)}</body></html>"""


def find_browser():
    for c in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              shutil.which("google-chrome"), shutil.which("chromium"), shutil.which("msedge")):
        if c and Path(c).exists():
            return c
    sys.exit("No Chrome or Edge found.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DOCS / "Nani-AI-Voice-Plush-Documentation.pdf"))
    ap.add_argument("--keep-html", action="store_true")
    args = ap.parse_args()

    from pypdf import PdfReader, PdfWriter

    tmp = Path(tempfile.mkdtemp())
    page = tmp / "book.html"
    out = Path(args.out).resolve()
    browser = find_browser()

    def render(pages):
        page.write_text(build_html(pages), encoding="utf-8")
        subprocess.run([browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--virtual-time-budget=30000", "--run-all-compositor-stages-before-draw",
                        f"--print-to-pdf={out}", page.as_uri()],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def locate():
        """Find each doc's first page by the path label printed above its title.
        Only the top of each page is searched, so a doc that merely *mentions*
        another file name (e.g. CHANGELOG.md) is not mistaken for its start."""
        texts = [(p.extract_text() or "").lower()[:120] for p in PdfReader(str(out)).pages]
        found = {}
        for _, _, _, rels in PARTS:
            for rel in rels:
                label = rel.replace("../", "").lower()
                found[rel] = next((i + 1 for i, t in enumerate(texts) if label in t), None)
        return found

    render({})                       # pass 1: layout
    pages = locate()
    render(pages)                    # pass 2: same layout, page numbers in the contents
    assert locate() == pages, "layout shifted between passes"

    # PDF bookmarks (the sidebar outline in any PDF viewer).
    reader, writer = PdfReader(str(out)), PdfWriter()
    writer.append(reader)
    for num, name, _, rels in PARTS:
        first = min(pages[r] for r in rels if pages[r]) - 2       # the part divider page
        parent = writer.add_outline_item(f"{num} · {name}", first)
        for rel in rels:
            if pages[rel]:
                title = title_of((DOCS / rel).read_text(encoding="utf-8"))
                writer.add_outline_item(title, pages[rel] - 1, parent=parent)
    writer.add_metadata({"/Title": "Nani AI Voice Plush — Project Documentation",
                         "/Subject": "ESP32-S3 voice plush toy for the Tutor Grandma web app"})
    with open(out, "wb") as f:
        writer.write(f)

    if args.keep_html:
        print("html:", page)
    missing = [r for r, p in pages.items() if not p]
    print(f"wrote {out}  ({len(PdfReader(str(out)).pages)} pages, "
          f"{out.stat().st_size / 1e6:.1f} MB, {len(pages) - len(missing)}/{len(pages)} docs located)")
    if missing:
        print("not located:", missing)


if __name__ == "__main__":
    main()
