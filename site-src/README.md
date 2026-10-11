# bytesizedacademy.org website

The website is plain HTML served by GitHub Pages straight from the root of this repo's `main` branch (custom domain in `CNAME`, `.nojekyll` turns off Jekyll). Episode folders like `2026-10-11-ep01/` are served too, so lesson pages play `video.mp4` from the same site.

Edit the sources here, then rebuild. Don't hand-edit the generated HTML (`index.html`, `lessons/`, `about/`, `privacy/`, `terms/`, `404.html`, `sitemap.xml`, `robots.txt`).

```
python3 site-src/build.py
```

Standard library only. If Pillow is installed it also writes small card images to `assets/thumbs/`; otherwise cards use the full cover.

## Add a lesson (one per posted episode)

1. Make sure the episode folder (`YYYY-MM-DD-epNN/` with `video.mp4` and `thumbnail.png`) is in the repo.
2. Copy a file in `site-src/lessons/` to `epNN-<slug>.md` and fill in the front matter: `ep`, `slug`, `title`, `series`, `series_blurb`, `topic`, `date` (post date), `summary`, `video`, `poster`, `instagram` (reel link, once posted) `seo_title` (the search-result title, under about 60 characters, phrased the way people search, e.g. "What Is an IP Address? IP Addresses Explained Simply"), `duration` (video length as ISO 8601, e.g. `PT1M4S`, from `ffprobe`) and optionally `next_title` (shown as "Coming next" on the newest lesson; remove it from the previous lesson) and `description` (search snippet; defaults to the summary).
3. Write the article: an `> **In one bite:**` callout, then `##` sections that go a little deeper than the script (key terms, a "Try it yourself", common mix-ups, the CCNA tie-in), then a `## Quiz` ("Test your knowledge", 3 to 5 multiple-choice questions, format below), then `## Sources` matching `sources/epNN.md`, and last a `## Transcript` with the voiceover text (`animations/audio/epNN-vo.txt`, numbers written as digits).
4. Run the build and commit everything it changed.

Markdown supported: `##`/`###` headings, paragraphs, `-` and `1.` lists, `>` callouts, `**bold**`, `*italic*`, `` `code` ``, `[links](url)`.

## Quiz format

```
## Quiz

### What does an IP address do?
- [x] Tells the network where to deliver data
- [ ] Stores your passwords
- [ ] Makes your Wi-Fi faster
> One-sentence explanation shown after checking.
```

One `###` per question, one `- [x]` correct option, mix up where the right answer sits, and only ask about things the lesson actually teaches. Scores are saved in the visitor's browser only (`assets/js/site.js`) and show as badges on lesson cards.

## SEO the build takes care of

Every build regenerates, for every lesson: JSON-LD structured data (Organization, WebSite, Article, VideoObject with transcript and duration, BreadcrumbList), Open Graph and Twitter tags with a 1200x630 share image in `assets/og/`, descriptive alt text, `sitemap.xml` with video and image entries, `robots.txt`, `llms.txt` and `llms-full.txt` (the full text of every lesson for AI assistants), and `site.webmanifest`. After the site is live, add it to Google Search Console and submit the sitemap.

## Other pages

`site-src/pages/*.md` (about, privacy, terms, 404). The privacy policy and terms are linked from the footer and are the URLs to give TikTok and Meta app reviews: https://bytesizedacademy.org/privacy/ and https://bytesizedacademy.org/terms/.
