# Byte Sized Academy media

Public hosting for the short videos posted by **Byte Sized Academy** ([@bytesizedacademyeducation](https://www.instagram.com/bytesizedacademyeducation/)): one-minute lessons, starting with the Network Bytes (CCNA) series.

Instagram's posting API only accepts a video from a public web address, so each episode's files are added here when it's posted, and Instagram fetches them by their raw GitHub link.

## Layout

One folder per post, named `YYYY-MM-DD-epNN` (the post date, Pacific time, and the episode number):

| File | What it is |
|---|---|
| `video.mp4` | The finished short (1080x1920, about 60 seconds) |
| `thumbnail.png` | The cover image shown on the profile grid |

The website at **[bytesizedacademy.org](https://bytesizedacademy.org)** lives in [ByteSizedAcademy/bytesizedacademy](https://github.com/ByteSizedAcademy/bytesizedacademy) and plays these videos from **media.bytesizedacademy.org** (this repo, served by GitHub Pages).

Files are added automatically by the posting script in the production pipeline. Please don't rename or delete folders of posted episodes, since Instagram may re-fetch them.

## Brand

The cookie logo lives in `brand/` for anything that needs a link to it (Auth0's login page, social profiles): `logo.png` (1080x1080), `logo-512.png`, `logo-256.png` and `logo.svg`, served at `https://media.bytesizedacademy.org/brand/<file>`.
