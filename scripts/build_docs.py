#!/usr/bin/env python3
"""Build static HTML guide pages from MDX source files.

Run from the api-docs-public/ root:
    python3 scripts/build_docs.py
"""

import os
import re
import sys
import yaml
import markdown as md_lib
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PAGES_DIR = BASE_DIR / "fern" / "docs" / "pages"
NAV_FILE = BASE_DIR / "fern" / "versions" / "v1.yml"

ACCENT = "#1e3a5f"

CALLOUT_ICONS = {
    "info": "ℹ️",
    "warning": "⚠️",
    "tip": "💡",
    "danger": "🚨",
    "success": "✅",
}


# ---------------------------------------------------------------------------
# Navigation parsing
# ---------------------------------------------------------------------------

def section_to_slug(title):
    return title.lower().replace(" ", "-").replace("&", "and")


def parse_nav(nav_data):
    """Return (flat_pages, nav_sections).

    flat_pages: list of {url, title, mdx_path, section, subsection}
    nav_sections: list of {title, slug, pages, subsections}
    """
    pages = []
    nav_sections = []

    for item in nav_data.get("navigation", []):
        if "api" in item:
            continue  # Skip API reference section
        if "section" not in item:
            continue

        sec_title = item["section"]
        sec_slug = section_to_slug(sec_title)
        nav_sec = {"title": sec_title, "slug": sec_slug, "pages": [], "subsections": []}

        for content in item.get("contents", []):
            if "page" in content:
                filename = Path(content["path"]).name
                url = f"{sec_slug}/{Path(filename).stem}"
                entry = {
                    "url": url,
                    "title": content["page"],
                    "mdx_path": PAGES_DIR / filename,
                    "section": sec_title,
                    "subsection": None,
                }
                pages.append(entry)
                nav_sec["pages"].append({"title": content["page"], "url": url})
            elif "section" in content:
                sub_title = content["section"]
                sub_pages = []
                for sub in content.get("contents", []):
                    if "page" not in sub:
                        continue
                    filename = Path(sub["path"]).name
                    url = f"{sec_slug}/{Path(filename).stem}"
                    entry = {
                        "url": url,
                        "title": sub["page"],
                        "mdx_path": PAGES_DIR / filename,
                        "section": sec_title,
                        "subsection": sub_title,
                    }
                    pages.append(entry)
                    sub_pages.append({"title": sub["page"], "url": url})
                nav_sec["subsections"].append({"title": sub_title, "pages": sub_pages})

        nav_sections.append(nav_sec)

    return pages, nav_sections


# ---------------------------------------------------------------------------
# MDX conversion
# ---------------------------------------------------------------------------

def parse_frontmatter(text):
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if m:
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except Exception:
            fm = {}
        return fm, text[m.end():]
    return {}, text


def md(text):
    """Convert a markdown snippet to HTML."""
    return md_lib.markdown(text, extensions=["tables", "fenced_code"])


def render_callout(intent, inner):
    icon = CALLOUT_ICONS.get(intent, "ℹ️")
    inner_html = md(inner.strip())
    return f'<div class="callout callout-{intent}">{icon} {inner_html}</div>'


def render_steps(inner):
    # Steps are delimited by ### headers (possibly indented)
    parts = re.split(r"(?m)^\s{0,4}#{2,3} ", inner)
    items_html = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        lines = part.split("\n", 1)
        title = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""
        body_html = md(body) if body else ""
        items_html.append(f"<li><strong>{title}</strong>{body_html}</li>")
    return '<ol class="steps">' + "".join(items_html) + "</ol>"


# Unique placeholder so markdown doesn't mangle component HTML
_HOLDER = "ZQCOMPONENTZQ"
_HOLDER_RE = re.compile(r"ZQCOMPONENTZQ(\d+)ZQENDCOMPONENTZQ")


def convert_mdx(text):
    """Convert MDX body (post-frontmatter) to HTML."""
    store = {}
    counter = [0]

    def stash(html):
        key = counter[0]
        counter[0] += 1
        store[key] = html
        return f"\n\n{_HOLDER}{key}ZQENDCOMPONENTZQ\n\n"

    # <Steps> ... </Steps>
    def on_steps(m):
        return stash(render_steps(m.group(1)))

    text = re.sub(r"<Steps>(.*?)</Steps>", on_steps, text, flags=re.DOTALL)

    # <Callout intent="..."> ... </Callout>
    def on_callout_intent(m):
        return stash(render_callout(m.group(1), m.group(2)))

    text = re.sub(
        r'<Callout\s+intent="([^"]+)">(.*?)</Callout>',
        on_callout_intent,
        text,
        flags=re.DOTALL,
    )

    # <Callout> ... </Callout> (no intent)
    def on_callout(m):
        return stash(render_callout("info", m.group(1)))

    text = re.sub(r"<Callout>(.*?)</Callout>", on_callout, text, flags=re.DOTALL)

    # <Card ...> ... </Card> — strip tags, keep content as markdown
    text = re.sub(r"<Card[^>]*>(.*?)</Card>", r"\1", text, flags=re.DOTALL)

    # api: links → API reference root
    text = re.sub(r"\[([^\]]+)\]\(api:[^)]+\)", r"[\1](/)", text)

    # Convert remaining markdown to HTML
    html = md(text)

    # Re-inject stashed components
    html = _HOLDER_RE.sub(lambda m: store[int(m.group(1))], html)

    return html


def mdx_to_html(mdx_text):
    fm, body = parse_frontmatter(mdx_text)
    return fm, convert_mdx(body)


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

CSS = """\
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",sans-serif;font-size:15px;line-height:1.65;color:#1a1a2e;background:#fff;display:flex;min-height:100vh}

/* Sidebar */
.sidebar{width:260px;min-width:260px;background:#f8f9fb;border-right:1px solid #e5e7eb;padding:24px 0;position:fixed;top:0;left:0;bottom:0;overflow-y:auto}
.sidebar-logo{display:block;font-size:17px;font-weight:700;color:#1e3a5f;text-decoration:none;padding:0 20px 16px;border-bottom:1px solid #e5e7eb;margin-bottom:12px;letter-spacing:-.02em}
.sidebar-api-ref{display:block;font-size:12.5px;color:#1e3a5f;text-decoration:none;padding:6px 12px;margin:0 12px 16px;border-radius:6px;border:1px solid #1e3a5f33;font-weight:500;text-align:center}
.sidebar-api-ref:hover{background:#1e3a5f0d}
.nav-section{margin-bottom:4px}
.nav-section-title{font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.09em;color:#9ca3af;padding:8px 20px 3px}
.nav-subsection-title{font-size:10.5px;font-weight:600;color:#b0b8c4;padding:6px 20px 2px 28px;text-transform:uppercase;letter-spacing:.07em}
.nav-link{display:block;font-size:13.5px;color:#374151;text-decoration:none;padding:5px 20px;transition:background .1s,color .1s}
.nav-link:hover{background:#e9ecf0;color:#1e3a5f}
.nav-link.active{background:#1e3a5f14;color:#1e3a5f;font-weight:600;border-left:3px solid #1e3a5f;padding-left:17px}

/* Main */
.main{margin-left:260px;flex:1;padding:52px 64px;max-width:960px}
.page-meta{margin-bottom:32px}
.page-description{color:#6b7280;font-size:15.5px;margin-top:6px}

/* Typography */
h1{font-size:28px;font-weight:700;color:#111827;line-height:1.25;margin-bottom:4px}
h2{font-size:19px;font-weight:700;color:#1f2937;margin-top:44px;margin-bottom:12px;border-bottom:1px solid #e5e7eb;padding-bottom:6px}
h3{font-size:15.5px;font-weight:600;color:#374151;margin-top:28px;margin-bottom:8px}
h4{font-size:14px;font-weight:600;color:#4b5563;margin-top:20px;margin-bottom:6px}
p{margin-bottom:14px}
a{color:#1e3a5f;text-decoration:underline}
a:hover{color:#2d5a8e}
ul,ol{margin:10px 0 16px 24px}
li{margin-bottom:5px}
strong{font-weight:600}

/* Code */
code{font-family:"Menlo","Monaco","Consolas","Courier New",monospace;font-size:13px;background:#f3f4f6;padding:2px 5px;border-radius:4px;color:#c2185b}
pre{background:#1a1a2e;color:#e2e8f0;border-radius:8px;padding:20px 24px;overflow-x:auto;margin:16px 0;font-size:13px;line-height:1.55}
pre code{background:none;padding:0;color:inherit;font-size:inherit}

/* Tables */
table{border-collapse:collapse;width:100%;margin:16px 0;font-size:13.5px}
th{background:#f3f4f6;font-weight:600;color:#374151;text-align:left;padding:8px 12px;border:1px solid #d1d5db}
td{padding:8px 12px;border:1px solid #e5e7eb;color:#4b5563;vertical-align:top}
tr:nth-child(even) td{background:#fafafa}

/* Callouts */
.callout{border-left:4px solid;padding:12px 16px;border-radius:0 6px 6px 0;margin:16px 0;font-size:14px;line-height:1.5}
.callout p{margin:0}
.callout-info{border-color:#3b82f6;background:#eff6ff;color:#1d4ed8}
.callout-warning{border-color:#f59e0b;background:#fffbeb;color:#92400e}
.callout-danger{border-color:#ef4444;background:#fef2f2;color:#991b1b}
.callout-tip{border-color:#10b981;background:#ecfdf5;color:#065f46}
.callout-success{border-color:#10b981;background:#ecfdf5;color:#065f46}

/* Steps */
ol.steps{list-style:none;margin:16px 0;padding:0;counter-reset:step-counter}
ol.steps li{counter-increment:step-counter;padding:16px 16px 16px 60px;position:relative;margin-bottom:10px;border:1px solid #e5e7eb;border-radius:8px;background:#fafafa}
ol.steps li::before{content:counter(step-counter);position:absolute;left:16px;top:16px;width:28px;height:28px;background:#1e3a5f;color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;line-height:1}
ol.steps li p{margin:4px 0 0}

/* Mobile */
@media(max-width:768px){.sidebar{display:none}.main{margin-left:0;padding:28px 20px}}
"""


def sidebar_html(nav_sections, current_url):
    parts = ['<nav class="sidebar">']
    parts.append('<a href="/" class="sidebar-logo">BRZ Public API</a>')
    parts.append('<a href="/" class="sidebar-api-ref">API Reference ↗</a>')

    for sec in nav_sections:
        parts.append('<div class="nav-section">')
        parts.append(f'<div class="nav-section-title">{sec["title"]}</div>')

        for page in sec["pages"]:
            active = " active" if current_url == page["url"] else ""
            parts.append(
                f'<a href="/{page["url"]}/" class="nav-link{active}">{page["title"]}</a>'
            )

        for sub in sec["subsections"]:
            parts.append(
                f'<div class="nav-subsection-title">{sub["title"]}</div>'
            )
            for page in sub["pages"]:
                active = " active" if current_url == page["url"] else ""
                parts.append(
                    f'<a href="/{page["url"]}/" class="nav-link{active}">{page["title"]}</a>'
                )

        parts.append("</div>")

    parts.append("</nav>")
    return "\n".join(parts)


PAGE_TMPL = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — BRZ API Docs</title>
<meta name="description" content="{description}">
<link rel="icon" type="image/png" href="/brand-logo.png">
<style>
{css}
</style>
</head>
<body>
{sidebar}
<main class="main">
<div class="page-meta">
<h1>{title}</h1>
{desc_p}
</div>
{content}
</main>
</body>
</html>
"""


def build_page(page, nav_sections, fm, content_html):
    title = fm.get("title", page["title"])
    description = fm.get("description", "")
    desc_p = f'<p class="page-description">{description}</p>' if description else ""
    return PAGE_TMPL.format(
        title=title,
        description=description,
        css=CSS,
        sidebar=sidebar_html(nav_sections, page["url"]),
        desc_p=desc_p,
        content=content_html,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not NAV_FILE.exists():
        print(f"ERROR: {NAV_FILE} not found. Run from api-docs-public/ root.", file=sys.stderr)
        sys.exit(1)

    nav_data = yaml.safe_load(NAV_FILE.read_text())
    pages, nav_sections = parse_nav(nav_data)

    built = 0
    for page in pages:
        if not page["mdx_path"].exists():
            print(f"  SKIP {page['url']} (source not found: {page['mdx_path'].name})")
            continue

        mdx_text = page["mdx_path"].read_text(encoding="utf-8")
        fm, content_html = mdx_to_html(mdx_text)
        full_html = build_page(page, nav_sections, fm, content_html)

        out = BASE_DIR / page["url"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(full_html, encoding="utf-8")
        print(f"  OK  /{page['url']}/")
        built += 1

    print(f"\n{built}/{len(pages)} pages built.")


if __name__ == "__main__":
    main()
