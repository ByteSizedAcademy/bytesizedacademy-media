#!/usr/bin/env python3
"""Build the bytesizedacademy.org website.

Reads lesson articles from site-src/lessons/*.md and pages from
site-src/pages/*.md, and writes plain HTML into the repository root, where
GitHub Pages serves it, plus sitemap.xml, robots.txt, llms.txt,
llms-full.txt and JSON-LD structured data. Standard library only; Pillow
(when installed) makes card thumbnails and 1200x630 share images.

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


def abs_url(path):
    return path if path.startswith("http") else SITE_URL + path


ORG = {
    "@type": "Organization",
    "@id": f"{SITE_URL}/#org",
    "name": SITE_NAME,
    "url": f"{SITE_URL}/",
    "logo": {"@type": "ImageObject", "url": f"{SITE_URL}/assets/img/logo-512.png", "width": 512, "height": 512},
    "email": EMAIL,
    "description": "Free one-minute video lessons that explain big topics simply.",
    "sameAs": [INSTAGRAM, KOFI],
}
WEBSITE = {
    "@type": "WebSite",
    "@id": f"{SITE_URL}/#website",
    "name": SITE_NAME,
    "alternateName": "Byte Sized Academy: " + TAGLINE,
    "url": f"{SITE_URL}/",
    "inLanguage": "en-US",
    "publisher": {"@id": f"{SITE_URL}/#org"},
}


def breadcrumbs(items):
    """items: [(name, path)], Home is added first."""
    items = [("Home", "/")] + items
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": abs_url(p)}
            for i, (n, p) in enumerate(items)
        ],
    }


def page(title, body, *, path, description, image=None, image_alt=None, kind="website",
         graph=(), noindex=False, extra_meta="", head_title=None):
    image = image or DEFAULT_OG
    image_alt = image_alt or f"{SITE_NAME}: {TAGLINE}"
    full_title = head_title or (f"{title} | {SITE_NAME}" if title != SITE_NAME else f"{SITE_NAME} | {TAGLINE}")
    canonical = SITE_URL + path
    nav = [("/lessons/", "Lessons"), ("/about/", "About")]
    links = "".join(
        f'<a href="{href}"{CURRENT if path.startswith(href) else ""}>{label}</a>'
        for href, label in nav
    )
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
    ld = json.dumps({"@context": "https://schema.org", "@graph": [ORG, WEBSITE, *graph]}, ensure_ascii=False)
    year = date.today().year
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canonical}">
<meta name="author" content="{SITE_NAME}">
<meta name="theme-color" content="#17120F">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:locale" content="en_US">
<meta property="og:type" content="{kind}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{abs_url(image)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(image_alt)}">
{extra_meta}<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{abs_url(image)}">
<meta name="twitter:image:alt" content="{esc(image_alt)}">
<link rel="icon" type="image/png" sizes="64x64" href="/assets/img/favicon-64.png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="sitemap" type="application/xml" href="/sitemap.xml">
<link rel="preload" href="/assets/fonts/bricolage-grotesque-latin-800-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/site.css">
<script type="application/ld+json">{ld}</script>
<script src="/assets/js/site.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="/" aria-label="{SITE_NAME} home"><img src="/assets/img/cookie-256.png" alt="" width="36" height="36"><span>Byte Sized <b>Academy</b></span></a>
    <nav class="site-nav" aria-label="Main">{links}<a class="nav-follow" href="{INSTAGRAM}" rel="noopener me" target="_blank">Instagram</a><a class="btn btn-small" href="{KOFI}" rel="noopener" target="_blank">{HEART}Support</a></nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-row">
    <div>
      <a class="brand" href="/" aria-label="{SITE_NAME} home"><img src="/assets/img/cookie-256.png" alt="" width="28" height="28"><span>Byte Sized <b>Academy</b></span></a>
      <p class="muted">{TAGLINE}. Big topics explained simply, in one minute or less.</p>
      <p class="muted">Our lessons are free and ad-free. If they help you, you can chip in to keep them coming.</p>
      <a class="btn btn-small" href="{KOFI}" rel="noopener" target="_blank">{HEART}Support us on Ko-fi</a>
    </div>
    <nav aria-label="Footer">
      <a href="/lessons/">Lessons</a>
      <a href="/about/">About</a>
      <a href="{INSTAGRAM}" rel="noopener me" target="_blank">Instagram</a>
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


# ---------- images (Pillow optional) ----------

DEFAULT_OG = "/assets/img/og-default.png"


def fresh(dest, *sources):
    return dest.exists() and all(dest.stat().st_mtime >= s.stat().st_mtime for s in sources if s.exists())


def card_image(lesson):
    """A small JPEG of the cover for cards."""
    src = ROOT / lesson["poster"]
    dest = ROOT / "assets" / "thumbs" / f"ep{lesson['ep']}.jpg"
    if fresh(dest, src):
        return "/" + dest.relative_to(ROOT).as_posix()
    try:
        from PIL import Image
        im = Image.open(src).convert("RGB")
        im.thumbnail((540, 960))
        dest.parent.mkdir(parents=True, exist_ok=True)
        im.save(dest, "JPEG", quality=82, optimize=True, progressive=True)
        return "/" + dest.relative_to(ROOT).as_posix()
    except Exception:
        return "/" + lesson["poster"]


def og_image(dest_rel, eyebrow, title, side_image, sub="Explained in one minute or less"):
    """A 1200x630 share image: title on the left, cover or logo on the right."""
    dest = ROOT / dest_rel.lstrip("/")
    side = ROOT / side_image.lstrip("/")
    if fresh(dest, side, Path(__file__)):
        return dest_rel
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
    except ImportError:
        return dest_rel if dest.exists() else None
    fonts = ROOT / "assets" / "fonts"
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), "#17120F")
    glow = Image.new("RGB", (W, H), "#17120F")
    ImageDraw.Draw(glow).ellipse((700, -150, 1350, 500), fill="#5A2A0C")
    im = Image.blend(im, glow.filter(ImageFilter.GaussianBlur(120)), 1.0)
    d = ImageDraw.Draw(im)
    disp = lambda s: ImageFont.truetype(str(fonts / "bricolage-grotesque-latin-800-normal.woff2"), s)
    body = lambda s: ImageFont.truetype(str(fonts / "atkinson-hyperlegible-latin-700-normal.woff2"), s)
    # right: cover crop or logo
    pic = Image.open(side).convert("RGB")
    if pic.height > pic.width:  # portrait cover: crop to its content area
        pic = pic.crop((0, int(pic.height * 0.13), pic.width, int(pic.height * 0.87)))
        pic.thumbnail((10_000, 530))
        x0, y0 = W - pic.width - 60, (H - pic.height) // 2
        mask = Image.new("L", pic.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, *pic.size), 28, fill=255)
        d.rounded_rectangle((x0 - 2, y0 - 2, x0 + pic.width + 1, y0 + pic.height + 1), 30, outline="#3A2E26", width=2)
        im.paste(pic, (x0, y0), mask)
        text_w = x0 - 130
    else:
        pic.thumbnail((380, 380))
        mask = Image.new("L", pic.size, 0)
        ImageDraw.Draw(mask).ellipse((0, 0, *pic.size), fill=255)
        x0 = W - pic.width - 90
        im.paste(pic, (x0, (H - pic.height) // 2), mask)
        text_w = x0 - 150
    # left: logo, eyebrow, title, sub
    logo = Image.open(ROOT / "assets/img/cookie-256.png").convert("RGB").resize((56, 56))
    lm = Image.new("L", (56, 56), 0)
    ImageDraw.Draw(lm).ellipse((0, 0, 56, 56), fill=255)
    im.paste(logo, (70, 62), lm)
    d.text((140, 74), "Byte Sized", font=disp(30), fill="#FFF4E6")
    d.text((140 + d.textlength("Byte Sized ", font=disp(30)), 74), "Academy", font=disp(30), fill="#FF7A1A")
    size = 76
    while True:
        f = disp(size)
        words, lines, cur = title.split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= text_w:
                cur = t
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
        if len(lines) <= 3 or size <= 48:
            break
        size -= 4
    block = len(lines) * size * 1.08
    y = max(170, (H - block) // 2 + 10)
    d.text((70, y - 48), eyebrow.upper(), font=body(22), fill="#FF7A1A")
    for line in lines:
        d.text((70, y), line, font=f, fill="#FFF4E6")
        y += size * 1.08
    d.text((70, y + 18), sub, font=body(26), fill="#A8988A")
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, optimize=True)
    print("wrote", dest_rel)
    return dest_rel


def lesson_card(l, heading="h3", eager=False):
    loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return f"""<a class="card" href="/lessons/{l['slug']}/" data-slug="{l['slug']}">
  <span class="card-media"><img src="{l['card']}" alt="{esc(l['cover_alt'])}" {loading} decoding="async" width="540" height="960"><span class="play" aria-hidden="true"></span></span>
  <span class="card-body">
    <span class="eyebrow">{esc(l['series'])} · EP{l['ep']}</span>
    <{heading} class="card-title">{esc(l['title'])}</{heading}>
    <span class="card-text">{esc(l['summary'])}</span>
  </span>
</a>"""


def iso_seconds(duration):
    m = re.fullmatch(r"PT(?:(\d+)M)?(?:(\d+)S)?", duration or "")
    return int(m.group(1) or 0) * 60 + int(m.group(2) or 0) if m else None


def video_ld(l):
    v = {
        "@type": "VideoObject",
        "@id": f"{l['url']}#video",
        "name": l["title"],
        "description": l["summary"],
        "thumbnailUrl": [abs_url("/" + l["poster"]), abs_url(l["og"])],
        "uploadDate": l["date"] + "T00:00:00-07:00",
        "contentUrl": abs_url("/" + l["video"]),
        "inLanguage": "en-US",
        "isFamilyFriendly": True,
        "educationalLevel": "Beginner",
        "learningResourceType": "Concept overview",
        "publisher": {"@id": f"{SITE_URL}/#org"},
    }
    if l.get("duration"):
        v["duration"] = l["duration"]
    if l.get("transcript"):
        v["transcript"] = l["transcript"]
    if l.get("instagram"):
        v["sameAs"] = l["instagram"]
    return v


def parse_quiz(md):
    """### Question / - [x] right / - [ ] wrong / > explanation"""
    qs = []
    for line in md.splitlines():
        s = line.strip()
        if s.startswith("### "):
            qs.append({"q": s[4:], "options": [], "answer": None, "explain": ""})
        elif qs and re.match(r"- \[[ xX]\] ", s):
            if s[3] in "xX":
                qs[-1]["answer"] = len(qs[-1]["options"])
            qs[-1]["options"].append(s[6:])
        elif qs and s.startswith(">"):
            qs[-1]["explain"] = (qs[-1]["explain"] + " " + s[1:].strip()).strip()
    for q in qs:
        if q["answer"] is None or len(q["options"]) < 2:
            raise SystemExit(f"Quiz question needs 2+ options and one [x]: {q['q']}")
    return qs


def render_quiz(l):
    qs = l["quiz"]
    fields = []
    for i, q in enumerate(qs):
        opts = "".join(
            f'<label class="opt"><input type="radio" name="q{i + 1}" value="{j}"><span>{inline(o)}</span></label>'
            for j, o in enumerate(q["options"]))
        fields.append(f"""<fieldset class="q" data-answer="{q['answer']}">
  <legend><span class="qn">{i + 1}</span>{inline(q['q'])}</legend>
  {opts}
  <p class="explain" hidden><strong class="verdict"></strong> {inline(q['explain'])}</p>
</fieldset>""")
    answers = "".join(f"<li>{inline(q['q'])} <strong>{inline(q['options'][q['answer']])}</strong>. {inline(q['explain'])}</li>" for q in qs)
    return f"""<section class="quiz" id="test-your-knowledge" aria-labelledby="quiz-h" data-quiz="{l['slug']}">
  <p class="eyebrow">Test your knowledge</p>
  <h2 id="quiz-h">Quick quiz: {esc(l['title'])}</h2>
  <p class="muted">{len(qs)} multiple-choice questions. Pick one answer for each, then check how you did.</p>
  <form class="quiz-form" novalidate>
{''.join(fields)}
    <div class="quiz-actions">
      <button type="submit" class="btn">Check my answers</button>
      <button type="button" class="btn btn-ghost" data-retry hidden>Try again</button>
      <p class="score" role="status" aria-live="polite"></p>
    </div>
  </form>
  <noscript><details class="quiz-answers"><summary>Show the answers</summary><ol>{answers}</ol></details></noscript>
</section>"""


def quiz_ld(l):
    return {
        "@type": "Quiz",
        "@id": f"{l['url']}#quiz",
        "name": f"Quiz: {l['title']}",
        "about": {"@type": "Thing", "name": l["title"]},
        "educationalLevel": "Beginner",
        "inLanguage": "en-US",
        "isAccessibleForFree": True,
        "hasPart": [{
            "@type": "Question",
            "eduQuestionType": "Multiple choice",
            "learningResourceType": "Practice problem",
            "text": q["q"],
            "acceptedAnswer": {"@type": "Answer", "text": q["options"][q["answer"]], "answerExplanation": {"@type": "Comment", "text": q["explain"]}},
            "suggestedAnswer": [{"@type": "Answer", "text": o} for j, o in enumerate(q["options"]) if j != q["answer"]],
        } for q in l["quiz"]],
    }


# ---------- pages ----------

def build_lesson(l, prev, nxt):
    sources = ""
    if l.get("sources_md"):
        sources = f'<section class="sources" aria-labelledby="sources"><h2 id="sources">Sources</h2>{markdown(l["sources_md"])}</section>'
    transcript = ""
    if l.get("transcript"):
        transcript = f'<details class="transcript"><summary><h2 id="transcript">Video transcript</h2></summary>{markdown(l["transcript"])}</details>'
    social = ""
    if l.get("instagram"):
        social = f'<a class="btn btn-ghost" href="{esc(l["instagram"])}" rel="noopener" target="_blank">Watch on Instagram</a>'
    pager = []
    if prev:
        pager.append(f'<a class="pager-prev" href="/lessons/{prev["slug"]}/" rel="prev"><span class="muted">Previous</span>{esc(prev["title"])}</a>')
    if nxt:
        pager.append(f'<a class="pager-next" href="/lessons/{nxt["slug"]}/" rel="next"><span class="muted">Next lesson</span>{esc(nxt["title"])}</a>')
    elif l.get("next_title"):
        pager.append(f'<div class="pager-next is-soon"><span class="muted">Coming next</span>{esc(l["next_title"])}</div>')
    posted = date.fromisoformat(l["date"]).strftime("%B %-d, %Y")
    series_path = f"/lessons/#{slugify(l['series'])}"
    graph = [
        {
            "@type": ["Article", "LearningResource"],
            "@id": f"{l['url']}#article",
            "headline": l["seo_title"],
            "name": l["title"],
            "description": l["summary"],
            "url": l["url"],
            "mainEntityOfPage": l["url"],
            "image": [abs_url(l["og"]), abs_url("/" + l["poster"])],
            "datePublished": l["date"],
            "dateModified": l.get("updated", l["date"]),
            "inLanguage": "en-US",
            "author": {"@id": f"{SITE_URL}/#org"},
            "publisher": {"@id": f"{SITE_URL}/#org"},
            "isPartOf": {"@type": "CreativeWorkSeries", "name": l["series"], "url": abs_url(series_path)},
            "about": l["title"],
            "educationalLevel": "Beginner",
            "learningResourceType": "Video lesson with article",
            "isAccessibleForFree": True,
            "timeRequired": l.get("duration", "PT1M"),
            "video": {"@id": f"{l['url']}#video"},
            "wordCount": len(l["body"].split()),
        },
        video_ld(l),
        breadcrumbs([("Lessons", "/lessons/"), (l["series"], series_path), (l["title"], f"/lessons/{l['slug']}/")]),
    ]
    if l.get("quiz"):
        graph.append(quiz_ld(l))
    body = f"""<article class="lesson wrap">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/lessons/">Lessons</a><span aria-hidden="true">/</span><a href="{series_path}">{esc(l['series'])}</a></nav>
  <div class="lesson-grid">
    <div class="lesson-video">
      <div class="phone">
        <video controls playsinline preload="metadata" poster="/{esc(l['poster'])}" width="1080" height="1920" title="{esc(l['title'])} (video lesson)" aria-label="Video lesson: {esc(l['title'])}">
          <source src="/{esc(l['video'])}" type="video/mp4">
          <p>Your browser can't play this video. <a href="/{esc(l['video'])}">Download the lesson video</a>.</p>
        </video>
      </div>
      <div class="video-actions">{social}</div>
    </div>
    <div class="lesson-text">
      <p class="eyebrow">{esc(l['series'])} · Episode {int(l['ep'])}{(' · ' + esc(l['topic'])) if l.get('topic') else ''}</p>
      <h1>{esc(l['title'])}</h1>
      <p class="lede">{esc(l['summary'])}</p>
      <p class="meta muted">Posted <time datetime="{l['date']}">{posted}</time> · About a 1 minute watch, {l['read_min']} minute read{' · <a href="#test-your-knowledge">Take the quiz</a>' if l.get('quiz') else ''}</p>
      <div class="prose">
{markdown(l['body'])}
      </div>
      {render_quiz(l) if l.get("quiz") else ""}
      {sources}
      {transcript}
      <aside class="support">
        <div><b>Enjoyed this bite?</b><span>Byte Sized Academy is free and ad-free. A small tip helps us make the next lesson.</span></div>
        <a class="btn" href="{KOFI}" rel="noopener" target="_blank">{HEART}Support on Ko-fi</a>
      </aside>
      <nav class="pager" aria-label="More lessons">{''.join(pager)}</nav>
    </div>
  </div>
</article>"""
    extra = (f'<meta property="article:published_time" content="{l["date"]}">\n'
             f'<meta property="article:modified_time" content="{l.get("updated", l["date"])}">\n'
             f'<meta property="article:section" content="{esc(l["series"])}">\n'
             f'<meta property="og:video" content="{abs_url("/" + l["video"])}">\n'
             f'<meta property="og:video:type" content="video/mp4">\n')
    write(f"lessons/{l['slug']}/index.html",
          page(l["title"], body, path=f"/lessons/{l['slug']}/", description=l["description"],
               head_title=l["head_title"], image=l["og"],
               image_alt=f"{l['title']} ({l['series']} episode {int(l['ep'])})",
               kind="article", graph=graph, extra_meta=extra))


def group_series(lessons):
    series = {}
    for l in lessons:
        series.setdefault(l["series"], []).append(l)
    return series


def build_home(lessons):
    latest = lessons[-1]
    recent = list(reversed(lessons))[:6]
    series = group_series(lessons)
    body = f"""<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <p class="eyebrow">{TAGLINE}</p>
      <h1>Big topics, <span class="hl">explained simply</span>, in one minute or less.</h1>
      <p class="lede">Byte Sized Academy makes free, one-minute video lessons you can finish while your coffee cools. Every lesson has a page like this one, with a little more detail and the sources behind it.</p>
      <div class="hero-actions">
        <a class="btn" href="/lessons/{latest['slug']}/">Start with the newest lesson</a>
        <a class="btn btn-ghost" href="/lessons/">Browse all lessons</a>
      </div>
    </div>
    <a class="hero-card" href="/lessons/{latest['slug']}/" aria-label="Newest lesson: {esc(latest['title'])}">
      <img src="{latest['card']}" alt="{esc(latest['cover_alt'])}" width="540" height="960" fetchpriority="high">
      <span class="hero-badge">New · EP{latest['ep']}</span>
    </a>
  </div>
</section>
<section class="wrap section" aria-labelledby="latest">
  <div class="section-head"><h2 id="latest">Latest lessons</h2><a href="/lessons/">See all lessons</a></div>
  <div class="cards">{''.join(lesson_card(l) for l in recent)}</div>
</section>
<section class="wrap section" aria-labelledby="how">
  <div class="section-head"><h2 id="how">How it works</h2></div>
  <ol class="steps">
    <li><h3>Watch</h3><span>One idea per video, about a minute long. Tiny topics stack up into big ones.</span></li>
    <li><h3>Read</h3><span>Each lesson's page goes a bit further, with the key terms and a quick thing to try.</span></li>
    <li><h3>Check</h3><span>Every fact links to the sources we used, so you can dig deeper or double-check us.</span></li>
  </ol>
</section>
<section class="wrap section" aria-labelledby="series">
  <div class="section-head"><h2 id="series">Series</h2></div>
  <div class="series-list">
    {''.join(f'<a class="series" href="/lessons/#{slugify(name)}"><h3>{esc(name)}</h3><span>{esc(ls[0].get("series_blurb", ""))}</span><span class="muted">{len(ls)} lesson{"s" if len(ls) != 1 else ""}</span></a>' for name, ls in series.items())}
    <div class="series is-soon"><h3>More subjects</h3><span>New subjects are on the way. Follow along to catch them first.</span><a href="{INSTAGRAM}" rel="noopener" target="_blank">@bytesizedacademyeducation</a></div>
  </div>
</section>"""
    write("index.html", page(SITE_NAME, body, path="/",
                             head_title=f"{SITE_NAME} | Free One-Minute Video Lessons, Explained Simply",
                             description="Free one-minute video lessons that explain big topics simply, starting with computer networking. Each lesson has a written guide, key terms and sources."))


def build_lessons_index(lessons):
    blocks = []
    for name, ls in group_series(lessons).items():
        blocks.append(f"""<section class="section" id="{slugify(name)}" aria-labelledby="{slugify(name)}-h">
  <div class="section-head"><h2 id="{slugify(name)}-h">{esc(name)}</h2><span class="muted">{len(ls)} lesson{"s" if len(ls) != 1 else ""}</span></div>
  <p class="muted series-blurb">{esc(ls[0].get('series_blurb', ''))}</p>
  <div class="cards">{''.join(lesson_card(l) for l in ls)}</div>
</section>""")
    body = f"""<div class="wrap page-head">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><span>Lessons</span></nav>
  <p class="eyebrow">All lessons</p>
  <h1>Lessons</h1>
  <p class="lede">Every short we post, in order, with a written guide and sources.</p>
</div>
<div class="wrap">{''.join(blocks)}</div>"""
    graph = [
        {
            "@type": "CollectionPage",
            "@id": f"{SITE_URL}/lessons/#page",
            "name": "Lessons",
            "url": f"{SITE_URL}/lessons/",
            "isPartOf": {"@id": f"{SITE_URL}/#website"},
            "mainEntity": {
                "@type": "ItemList",
                "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "url": l["url"], "name": l["title"]}
                    for i, l in enumerate(lessons)
                ],
            },
        },
        breadcrumbs([("Lessons", "/lessons/")]),
    ]
    write("lessons/index.html", page("Lessons", body, path="/lessons/", graph=graph,
                                     head_title=f"All Lessons: One-Minute Video Lessons | {SITE_NAME}",
                                     description="Every Byte Sized Academy lesson, sorted by series: one-minute videos with a written guide, key terms and sources."))


def build_page(p):
    body = f"""<article class="wrap page">
  <div class="page-head"><p class="eyebrow">{esc(p.get('eyebrow', SITE_NAME))}</p><h1>{esc(p['title'])}</h1>
  {f'<p class="lede">{esc(p["lede"])}</p>' if p.get('lede') else ''}</div>
  <div class="prose">
{markdown(p['body'])}
  </div>
</article>"""
    slug = p["slug"]
    path = "/404.html" if slug == "404" else f"/{slug}/"
    out = "404.html" if slug == "404" else f"{slug}/index.html"
    graph = [] if slug == "404" else [breadcrumbs([(p["title"], path)])]
    if slug == "about":
        graph.append({"@type": "AboutPage", "url": SITE_URL + path, "about": {"@id": f"{SITE_URL}/#org"}})
    write(out, page(p["title"], body, path=path, graph=graph, noindex=slug == "404",
                    description=p.get("description", p.get("lede", ""))))


def build_sitemap(lessons, pages):
    newest = max(l.get("updated", l["date"]) for l in lessons)
    entries = [(f"{SITE_URL}/", newest, ""), (f"{SITE_URL}/lessons/", newest, "")]
    for l in lessons:
        dur = iso_seconds(l.get("duration"))
        video = f"""
    <video:video>
      <video:thumbnail_loc>{abs_url('/' + l['poster'])}</video:thumbnail_loc>
      <video:title>{esc(l['title'])}</video:title>
      <video:description>{esc(l['summary'])}</video:description>
      <video:content_loc>{abs_url('/' + l['video'])}</video:content_loc>{f'''
      <video:duration>{dur}</video:duration>''' if dur else ''}
      <video:publication_date>{l['date']}T00:00:00-07:00</video:publication_date>
      <video:family_friendly>yes</video:family_friendly>
    </video:video>
    <image:image><image:loc>{abs_url('/' + l['poster'])}</image:loc></image:image>"""
        entries.append((l["url"], l.get("updated", l["date"]), video))
    for p in pages:
        if p["slug"] != "404":
            entries.append((f"{SITE_URL}/{p['slug']}/", p.get("updated", newest), ""))
    body = "".join(f"\n  <url>\n    <loc>{u}</loc>\n    <lastmod>{m}</lastmod>{x}\n  </url>" for u, m, x in entries)
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
          '        xmlns:video="http://www.google.com/schemas/sitemap-video/1.1"\n'
          f'        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">{body}\n</urlset>\n')
    write("robots.txt", "# Byte Sized Academy: everyone is welcome to crawl, including AI assistants.\n"
          "User-agent: *\nAllow: /\nDisallow: /site-src/\n\n"
          f"Sitemap: {SITE_URL}/sitemap.xml\n")


def strip_md(text):
    """Turn site Markdown into plain-text-friendly Markdown for llms files."""
    return re.sub(r"\]\((/[^)]*)\)", lambda m: f"]({SITE_URL}{m.group(1)})", text)


def build_llms(lessons, pages):
    series = group_series(lessons)
    lines = [f"# {SITE_NAME}", "",
             f"> {SITE_NAME} ({SITE_URL}) makes free, one-minute educational videos that explain big topics simply. "
             "Each lesson page has the video, a beginner-friendly article that goes a bit deeper, a transcript and cited sources. "
             f"Videos post on Instagram at @bytesizedacademyeducation. Contact: {EMAIL}.", "",
             "Lessons are written and produced with help from AI tools and checked against the sources listed on each page. "
             "Please cite the lesson URL when you use our explanations.", ""]
    for name, ls in series.items():
        lines += [f"## {name}", "", ls[0].get("series_blurb", ""), ""]
        lines += [f"- [{l['title']}]({l['url']}): {l['summary']}" for l in ls]
        lines.append("")
    lines += ["## About", "",
              f"- [About {SITE_NAME}]({SITE_URL}/about/): what we make and how lessons are made",
              f"- [All lessons]({SITE_URL}/lessons/): every lesson, sorted by series", "",
              "## Optional", "",
              f"- [Full text of every lesson]({SITE_URL}/llms-full.txt): all lesson articles and transcripts in one Markdown file",
              f"- [Privacy policy]({SITE_URL}/privacy/)",
              f"- [Terms of service]({SITE_URL}/terms/)",
              f"- [Support us on Ko-fi]({KOFI})", ""]
    write("llms.txt", "\n".join(lines))
    full = [f"# {SITE_NAME}: full lesson text", "",
            f"> Every lesson from {SITE_URL}, newest last. Each section is one lesson: its article, sources and video transcript.", ""]
    for l in lessons:
        full += [f"## {l['title']}", "",
                 f"URL: {l['url']}  ",
                 f"Series: {l['series']}, episode {int(l['ep'])}  ",
                 f"Posted: {l['date']}  ",
                 f"Video: {abs_url('/' + l['video'])}", "",
                 l["summary"], "",
                 re.sub(r"^## ", "### ", strip_md(l["body"]), flags=re.M), ""]
        if l.get("sources_md"):
            full += ["### Sources", "", l["sources_md"], ""]
        if l.get("transcript"):
            full += ["### Video transcript", "", l["transcript"], ""]
    write("llms-full.txt", "\n".join(full))


def build_manifest():
    write("site.webmanifest", json.dumps({
        "name": SITE_NAME, "short_name": "Byte Sized", "description": f"{TAGLINE}. Big topics explained simply.",
        "start_url": "/", "display": "standalone", "background_color": "#17120F", "theme_color": "#17120F",
        "icons": [{"src": "/assets/img/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
                  {"src": "/assets/img/logo-512.png", "sizes": "512x512", "type": "image/png"}],
    }, indent=2) + "\n")


def split_section(body, heading):
    head, sep, rest = body.partition(f"\n## {heading}")
    if not sep:
        return body, ""
    section, sep2, after = rest.partition("\n## ")
    return (head + (("\n## " + after) if sep2 else "")).strip(), section.strip()


def main():
    og_image(DEFAULT_OG, TAGLINE, "Big topics, explained simply, in one minute or less.",
             "/assets/img/logo-512.png", sub="Free video lessons · bytesizedacademy.org")
    lessons = []
    for path in sorted((SRC / "lessons").glob("*.md")):
        l = read_doc(path)
        l["body"], l["transcript"] = split_section(l["body"], "Transcript")
        l["body"], l["sources_md"] = split_section(l["body"], "Sources")
        l["body"], quiz_md = split_section(l["body"], "Quiz")
        l["quiz"] = parse_quiz(quiz_md) if quiz_md else []
        l.setdefault("seo_title", l["title"])
        # Search results show about 60 characters of a title and 155 of a description.
        full = f"{l['seo_title']} | {SITE_NAME}"
        l["head_title"] = full if len(full) <= 65 else l["seo_title"]
        more = " Watch the one-minute video, then read the guide with key terms and sources."
        l.setdefault("description", l["summary"] + (more if len(l["summary"]) + len(more) <= 160 else ""))
        l["url"] = f"{SITE_URL}/lessons/{l['slug']}/"
        l["read_min"] = max(1, round(len(l["body"].split()) / 200))
        l["card"] = card_image(l)
        l["cover_alt"] = f"Cover of {l['series']} episode {int(l['ep'])}: {l['title']}"
        l["og"] = og_image(f"/assets/og/{l['slug']}.png", f"{l['series']} · EP{l['ep']}", l["title"],
                           "/" + l["poster"]) or "/" + l["poster"]
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
    build_llms(lessons, pages)
    build_manifest()


if __name__ == "__main__":
    main()
