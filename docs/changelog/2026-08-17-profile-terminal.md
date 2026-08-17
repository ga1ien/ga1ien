**Created:** 2026-08-17 (PT)
**Updated:** 2026-08-17 (PT)
**Version:** 1
**Repo/branch:** ga1ien/ga1ien · main
**Session/agent:** grok 01a01067
**What this is:** what shipped on the public GitHub profile this session

# GitHub profile terminal

The personal profile at github.com/ga1ien was empty (bio blank, one pin on claude-cache, private username repo holding a Next.js GBuilds site). The first README repeated the left rail and wrapped "Ora is the agent OS" into garbage. A noise-field SVG looked like olive sludge. A two-column live-code stream was rejected.

## What shipped

- Public `ga1ien/ga1ien` is README-only. The old GBuilds site is parked private at `ga1ien/gbuilds-site`.
- About: `Founder of Braintied. Twenty years as a photographer and creative director. First line of code: April 2025.`
- Header: 18.7s factory terminal GIF (`assets/term.gif`, 1.7 MB). Stack types in, live column ticks, then ~13s on `running` with a blinking cursor.
- Under it: static factory map (`assets/map.png`) and links to braintied.com, kulti.live, founder, brands.
- Pins (set in the UI): `braintied/watchtower`, `agentlog`, `research`, `kimi-router`. `kimi-router` was unarchived so the card no longer says Public archive.
- `ga1ien/claude-cache` README, description, and homepage point at `braintied/watchtower`. Repo stays for existing installs.
- Org `braintied/.github` profile got the same terminal language.

## Measurement

```
ffprobe on assets/term.gif
frames=66  total=18.76s  max_frame=0.44s
```

An earlier cut looked short because `ffmpeg -vf fps=12` flattened every hold frame to 1/12s. Hold is now per-frame delay, two reused blink frames.

## Defects found

- `ga1ien/ga1ien` was already taken by a site that contained X OAuth client IDs. Making it public as-is would have leaked them.
- GitHub has no public API for Customize your pins. GraphQL `updateItemsPinnedOnProfile` is gone.
- Profile README always sits above pins. Nothing can be placed underneath them.
- WebGL and SVG-as-img CSS/SMIL are not a reliable motion path. GIF is.
- `kimi-router` was archived; pinning it printed Public archive.
- A code-stream pane of `session-analyzer.ts` was built and then pulled. It did not look good.

## Deliberately not done

- Did not make Sentigen, Ora, or stack public.
- Did not publish a `@braintied/*` profile-stream package. Asked, then told to stop.
- Did not add mermaid. It would render in GitHub's default skin next to this header.
- Did not list the four pinned repos again in the README.
- Production deploy was not in scope. Push is not live for Vercel; this is GitHub only.
