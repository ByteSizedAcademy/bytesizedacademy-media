# bytesizedacademy.org website

The website is plain HTML served by GitHub Pages straight from the root of this repo's `main` branch (custom domain in `CNAME`, `.nojekyll` turns off Jekyll). Episode folders like `2026-10-11-ep01/` are served too, so lesson pages play `video.mp4` from the same site.

Edit the sources here, then rebuild. Don't hand-edit the generated HTML (`index.html`, `lessons/`, `about/`, `privacy/`, `terms/`, `404.html`, `sitemap.xml`, `robots.txt`).

```
python3 site-src/build.py
```

Standard library only. If Pillow is installed it also writes small card images to `assets/thumbs/`; otherwise cards use the full cover.

## Add a lesson (one per posted episode)

1. Make sure the episode folder (`YYYY-MM-DD-epNN/` with `video.mp4` and `thumbnail.png`) is in the repo.
2. Copy a file in `site-src/lessons/` to `epNN-<slug>.md` and fill in the front matter: `ep`, `slug`, `title`, `series`, `series_blurb`, `topic`, `date` (post date), `summary`, `video`, `poster`, `instagram` (reel link, once posted) and optionally `next_title` (shown as "Coming next" on the newest lesson; remove it from the previous lesson).
3. Write the article: an `> **In one bite:**` callout, then `##` sections that go a little deeper than the script (key terms, a "Try it yourself", common mix-ups, the CCNA tie-in), and a final `## Sources` list matching `sources/epNN.md`.
4. Run the build and commit everything it changed.

Markdown supported: `##`/`###` headings, paragraphs, `-` and `1.` lists, `>` callouts, `**bold**`, `*italic*`, `` `code` ``, `[links](url)`.

## Other pages

`site-src/pages/*.md` (about, privacy, terms, 404). The privacy policy and terms are linked from the footer and are the URLs to give TikTok and Meta app reviews: https://bytesizedacademy.org/privacy/ and https://bytesizedacademy.org/terms/.
