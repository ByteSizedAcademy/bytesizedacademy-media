#!/usr/bin/env python3
"""Build the bytesizedacademy.org website.

Reads lesson articles from site-src/lessons/*.md and pages from
site-src/pages/*.md, and writes plain HTML into the repository root, where
GitHub Pages serves it. Standard library only (Pillow is used for smaller
card images when it is installed).

    python3 site-src/build.py

Add a lesson: copy an existing site-src/lessons/epNN-*.md, change the front
matter and article, run this script, commit everything it changed.
"""
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "site-src"
SITE_URL = "https://bytesizedacademy.org"
SITE_NAME = "Byte Sized Academy"
TAGLINE = "Your one-minute classroom"
CURRENT = ' aria-current="page"'
INSTAGRAM = "https://www.instagram.com/bytesizedacademyeducation/"
EMAIL = "info@bytesizedacademy.org"
KOFI = "https://ko-fi.com/bytesizedacademy"
HEART = '<svg class="heart" viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M12 21s-7.5-4.6-9.9-9.2C.5 8.6 2.3 4.5 6.1 4.1c2.2-.2 4 1 5.9 3.1 1.9-2.1 3.7-3.3 5.9-3.1 3.8.4 5.6 4.5 4 7.7C19.5 16.4 12 21 12 21z"/></svg>'


# ---------- tiny markdown ----------

def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![*\w])\*([^*]+)\*(?!\w)", r"<em>\1</em>", text)

    def link(m):
        label, url = m.group(1), m.group(2)
        ext = url.startswith("http") and SITE_URL not in url
        attrs = ' rel="noopener" target="_blank"' if ext else ""
        return f'<a href="{html.escape(url)}"{attrs}>{label}</a>'

    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def markdown(md):
    """Headings (##, ###), paragraphs, - and 1. lists, > callouts, inline marks."""
    out, para, items, kind, quote = [], [], [], None, []

    def flush():
        nonlocal para, items, kind, quote
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
        if items:
            out.append(f"<{kind}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{kind}>")
        if quote:
            out.append(f'<aside class="callout">{markdown(chr(10).join(quote))}</aside>')
        para, items, kind, quote = [], [], None, []

    for line in md.strip().splitlines():
        s = line.strip()
        if s.startswith(">"):
            if para or items:
                flush()
            quote.append(s[1:].lstrip())
            continue
        if quote:
            flush()
        m = re.match(r"(#{2,3}) (.+)", s)
        if m:
            flush()
            lvl = len(m.group(1))
            out.append(f'<h{lvl} id="{slugify(m.group(2))}">{inline(m.group(2))}</h{lvl}>')
        elif re.match(r"[-*] ", s):
            if para or kind == "ol":
                flush()
            kind = "ul"
            items.append(s[2:])
        elif re.match(r"\d+\. ", s):
            if para or kind == "ul":
                flush()
            kind = "ol"
            items.append(s.split(" ", 1)[1])
        elif not s:
            flush()
        elif items:
            items[-1] += " " + s
        else:
            para.append(s)
    flush()
    return "\n".join(out)


def read_doc(path):
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    if text.startswith("---"):
        head, body = text[3:].split("\n---", 1)
        for line in head.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    meta["body"] = body.strip().replace("{{KOFI}}", KOFI)
    meta["source"] = path.name
    return meta


# ---------- layout ----------

def esc(s):
    return html.escape(str(s or ""))


def page(title, body, *, path, description, image="/assets/img/cookie-256.png", kind="website", extra_head=""):
    full_title = f"{title} · {SITE_NAME}" if title != SITE_NAME else f"{SITE_NAME} · {TAGLINE}"
    canonical = SITE_URL + path
    nav = [("/lessons/", "Lessons"), ("/about/", "About")]
    links = "".join(
        f'<a href="{href}"{CURRENT if path.startswith(href) else ""}>{label}</a>'
        for href, label in nav
    )
    year = date.today().year
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#17120F">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:type" content="{kind}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}{image}">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/png" href="/assets/img/favicon-64.png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/bricolage-grotesque-latin-800-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/site.css">
{extra_head}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="/"><img src="/assets/img/cookie-256.png" alt="" width="36" height="36"><span>Byte Sized <b>Academy</b></span></a>
    <nav class="site-nav" aria-label="Main">{links}<a class="nav-follow" href="{INSTAGRAM}" rel="noopener" target="_blank">Instagram</a><a class="btn btn-small" href="{KOFI}" rel="noopener" target="_blank">{HEART}Support</a></nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-row">
    <div>
      <a class="brand" href="/"><img src="/assets/img/cookie-256.png" alt="" width="28" height="28"><span>Byte Sized <b>Academy</b></span></a>
      <p class="muted">{TAGLINE}. Big topics explained simply, in one minute or less.</p>
      <p class="muted">Our lessons are free and ad-free. If they help you, you can chip in to keep them coming.</p>
      <a class="btn btn-small" href="{KOFI}" rel="noopener" target="_blank">{HEART}Support us on Ko-fi</a>
    </div>
    <nav aria-label="Footer">
      <a href="/lessons/">Lessons</a>
      <a href="/about/">About</a>
      <a href="{INSTAGRAM}" rel="noopener" target="_blank">Instagram</a>
      <a href="{KOFI}" rel="noopener" target="_blank">Ko-fi</a>
      <a href="mailto:{EMAIL}">{EMAIL}</a>
      <a href="/privacy/">Privacy</a>
      <a href="/terms/">Terms</a>
    </nav>
  </div>
  <div class="wrap"><p class="fine">&copy; {year} Byte Sized Academy</p></div>
</footer>
</body>
</html>
"""


def write(rel, content):
    out = ROOT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    print("wrote", rel)


def card_image(lesson):
    """A small JPEG of the cover for cards, when Pillow is available."""
    poster = lesson.get("poster", "")
    src = ROOT / poster
    dest = ROOT / "assets" / "thumbs" / f"ep{lesson['ep']}.jpg"
    if dest.exists() and src.exists() and dest.stat().st_mtime >= src.stat().st_mtime:
        return "/" + dest.relative_to(ROOT).as_posix()
    try:
        from PIL import Image
        im = Image.open(src).convert("RGB")
        im.thumbnail((540, 960))
        dest.parent.mkdir(parents=True, exist_ok=True)
        im.save(dest, "JPEG", quality=82, optimize=True, progressive=True)
        return "/" + dest.relative_to(ROOT).as_posix()
    except Exception:
        return "/" + poster


def lesson_card(l):
    return f"""<a class="card" href="/lessons/{l['slug']}/">
  <span class="card-media"><img src="{l['card']}" alt="" loading="lazy" width="540" height="960"><span class="play" aria-hidden="true"></span></span>
  <span class="card-body">
    <span class="eyebrow">{esc(l['series'])} · EP{l['ep']}</span>
    <span class="card-title">{esc(l['title'])}</span>
    <span class="card-text">{esc(l['summary'])}</span>
  </span>
</a>"""


# ---------- pages ----------

def build_lesson(l, prev, nxt):
    sources = ""
    if l.get("sources_md"):
        sources = f'<section class="sources" aria-labelledby="sources"><h2 id="sources">Sources</h2>{markdown(l["sources_md"])}</section>'
    social = ""
    if l.get("instagram"):
        social = f'<a class="btn btn-ghost" href="{esc(l["instagram"])}" rel="noopener" target="_blank">Watch on Instagram</a>'
    pager = []
    if prev:
        pager.append(f'<a class="pager-prev" href="/lessons/{prev["slug"]}/"><span class="muted">Previous</span>{esc(prev["title"])}</a>')
    if nxt:
        pager.append(f'<a class="pager-next" href="/lessons/{nxt["slug"]}/"><span class="muted">Next lesson</span>{esc(nxt["title"])}</a>')
    elif l.get("next_title"):
        pager.append(f'<div class="pager-next is-soon"><span class="muted">Coming next</span>{esc(l["next_title"])}</div>')
    posted = date.fromisoformat(l["date"]).strftime("%B %-d, %Y")
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "LearningResource",
        "name": l["title"],
        "description": l["summary"],
        "learningResourceType": "video lesson",
        "educationalLevel": "Beginner",
        "datePublished": l["date"],
        "isPartOf": {"@type": "CreativeWorkSeries", "name": l["series"]},
        "publisher": {"@type": "Organization", "name": SITE_NAME, "url": SITE_URL},
        "video": {
            "@type": "VideoObject",
            "name": l["title"],
            "description": l["summary"],
            "thumbnailUrl": f"{SITE_URL}/{l['poster']}",
            "contentUrl": f"{SITE_URL}/{l['video']}",
            "uploadDate": l["date"],
        },
    })
    body = f"""<article class="lesson wrap">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/lessons/">Lessons</a><span aria-hidden="true">/</span><span>{esc(l['series'])}</span></nav>
  <div class="lesson-grid">
    <div class="lesson-video">
      <div class="phone">
        <video controls playsinline preload="metadata" poster="/{esc(l['poster'])}" width="1080" height="1920">
          <source src="/{esc(l['video'])}" type="video/mp4">
        </video>
      </div>
      <div class="video-actions">{social}</div>
    </div>
    <div class="lesson-text">
      <p class="eyebrow">{esc(l['series'])} · Episode {int(l['ep'])}{(' · ' + esc(l['topic'])) if l.get('topic') else ''}</p>
      <h1>{esc(l['title'])}</h1>
      <p class="lede">{esc(l['summary'])}</p>
      <p class="meta muted">Posted {posted} · About a 1 minute watch, {l['read_min']} minute read</p>
      <div class="prose">
{markdown(l['body'])}
      </div>
      {sources}
      <aside class="support">
        <div><b>Enjoyed this bite?</b><span>Byte Sized Academy is free and ad-free. A small tip helps us make the next lesson.</span></div>
        <a class="btn" href="{KOFI}" rel="noopener" target="_blank">{HEART}Support on Ko-fi</a>
      </aside>
      <nav class="pager" aria-label="More lessons">{''.join(pager)}</nav>
    </div>
  </div>
</article>"""
    extra = f'<script type="application/ld+json">{jsonld}</script>\n'
    write(f"lessons/{l['slug']}/index.html",
          page(l["title"], body, path=f"/lessons/{l['slug']}/", description=l["summary"],
               image=l["card"], kind="article", extra_head=extra))


def build_home(lessons):
    latest = lessons[-1]
    recent = list(reversed(lessons))[:6]
    series = {}
    for l in lessons:
        series.setdefault(l["series"], []).append(l)
    body = f"""<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <p class="eyebrow">{TAGLINE}</p>
      <h1>Big topics, <span class="hl">explained simply</span>, in one minute or less.</h1>
      <p class="lede">Byte Sized Academy makes short video lessons you can finish while your coffee cools. Every lesson has a page like this one, with a little more detail and the sources behind it.</p>
      <div class="hero-actions">
        <a class="btn" href="/lessons/{latest['slug']}/">Start with the newest lesson</a>
        <a class="btn btn-ghost" href="/lessons/">Browse all lessons</a>
      </div>
    </div>
    <a class="hero-card" href="/lessons/{latest['slug']}/" aria-label="Newest lesson: {esc(latest['title'])}">
      <img src="{latest['card']}" alt="" width="540" height="960">
      <span class="hero-badge">New · EP{latest['ep']}</span>
    </a>
  </div>
</section>
<section class="wrap section">
  <div class="section-head"><h2>Latest lessons</h2><a href="/lessons/">See all</a></div>
  <div class="cards">{''.join(lesson_card(l) for l in recent)}</div>
</section>
<section class="wrap section">
  <div class="section-head"><h2>How it works</h2></div>
  <ol class="steps">
    <li><b>Watch</b><span>One idea per video, about a minute long. Tiny topics stack up into big ones.</span></li>
    <li><b>Read</b><span>Each lesson's page goes a bit further, with the key terms and a quick thing to try.</span></li>
    <li><b>Check</b><span>Every fact links to the sources we used, so you can dig deeper or double-check us.</span></li>
  </ol>
</section>
<section class="wrap section">
  <div class="section-head"><h2>Series</h2></div>
  <div class="series-list">
    {''.join(f'<a class="series" href="/lessons/#{slugify(name)}"><b>{esc(name)}</b><span>{esc(ls[0].get("series_blurb", ""))}</span><span class="muted">{len(ls)} lesson{"s" if len(ls) != 1 else ""}</span></a>' for name, ls in series.items())}
    <div class="series is-soon"><b>More subjects</b><span>New subjects are on the way. Follow along to catch them first.</span><a href="{INSTAGRAM}" rel="noopener" target="_blank">@bytesizedacademyeducation</a></div>
  </div>
</section>"""
    write("index.html", page(SITE_NAME, body, path="/",
                             description="Big topics explained simply, in one minute or less. Short video lessons with a written guide and sources for each one."))


def build_lessons_index(lessons):
    series = {}
    for l in lessons:
        series.setdefault(l["series"], []).append(l)
    blocks = []
    for name, ls in series.items():
        blocks.append(f"""<section class="section" id="{slugify(name)}">
  <div class="section-head"><h2>{esc(name)}</h2><span class="muted">{len(ls)} lesson{"s" if len(ls) != 1 else ""}</span></div>
  <p class="muted series-blurb">{esc(ls[0].get('series_blurb', ''))}</p>
  <div class="cards">{''.join(lesson_card(l) for l in ls)}</div>
</section>""")
    body = f"""<div class="wrap page-head">
  <p class="eyebrow">All lessons</p>
  <h1>Lessons</h1>
  <p class="lede">Every short we post, in order, with a written guide and sources.</p>
</div>
<div class="wrap">{''.join(blocks)}</div>"""
    write("lessons/index.html", page("Lessons", body, path="/lessons/",
                                     description="Every Byte Sized Academy lesson, sorted by series, with a written guide and sources."))


def build_page(p):
    body = f"""<article class="wrap page">
  <div class="page-head"><p class="eyebrow">{esc(p.get('eyebrow', SITE_NAME))}</p><h1>{esc(p['title'])}</h1>
  {f'<p class="lede">{esc(p["lede"])}</p>' if p.get('lede') else ''}</div>
  <div class="prose">
{markdown(p['body'])}
  </div>
</article>"""
    slug = p["slug"]
    path = "/" if slug == "404" else f"/{slug}/"
    out = "404.html" if slug == "404" else f"{slug}/index.html"
    write(out, page(p["title"], body, path=path, description=p.get("description", p.get("lede", ""))))


def build_sitemap(lessons, pages):
    urls = ["/", "/lessons/"] + [f"/lessons/{l['slug']}/" for l in lessons] + \
           [f"/{p['slug']}/" for p in pages if p["slug"] != "404"]
    body = "".join(f"<url><loc>{SITE_URL}{u}</loc></url>" for u in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")


def main():
    lessons = []
    for path in sorted((SRC / "lessons").glob("*.md")):
        l = read_doc(path)
        body, _, srcs = l["body"].partition("\n## Sources")
        l["body"], l["sources_md"] = body.strip(), srcs.strip()
        l["read_min"] = max(1, round(len(l["body"].split()) / 200))
        l["card"] = card_image(l)
        lessons.append(l)
    lessons.sort(key=lambda l: (l["date"], l["ep"]))
    for i, l in enumerate(lessons):
        build_lesson(l, lessons[i - 1] if i else None, lessons[i + 1] if i + 1 < len(lessons) else None)
    build_home(lessons)
    build_lessons_index(lessons)
    pages = [read_doc(p) for p in sorted((SRC / "pages").glob("*.md"))]
    for p in pages:
        build_page(p)
    build_sitemap(lessons, pages)


if __name__ == "__main__":
    main()
