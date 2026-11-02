# Agent notes

Guidance for AI coding agents (and humans) working on Nost4lgia. Read this before
changing code.

## What this is

A native **LG webOS** app (id `tv.livingroom.shell`) containing two pages:

- `launcher/index.html` — "Home+ / Living Room", a flat app-launcher grid.
- `launcher/spelunkr.html` — **Nost4lgia**, a retro cable-TV guide + player that
  streams Internet Archive MP4s. The launcher's Nost4lgia tile does a top-level
  `window.location = "spelunkr.html"`; Back from the guide returns to
  `index.html`. Both are plain HTML/CSS/JS, no framework, no build step for the
  pages themselves.

Channel data is generated into `launcher/spelunkr-channels.js` (a
`window.SPELUNKR_CHANNELS` global) by `nost4lgia-src/build_channels.js`. It is
**not** committed — regenerate it with Node.

## The target is Chromium 68 (webOS 5) — this constrains everything

The TV's browser is old. **Do not use:**

- `inset: 0` → use explicit `top/right/bottom/left: 0` (inset is Chrome 87+).
- flex `gap` → use margins (`> * + * { margin-left }`), it's Chrome 84+.
- `globalThis`, `Object.fromEntries`, `Array.flat/flatMap`, `Promise.allSettled`,
  `crypto.randomUUID`, optional chaining `?.`, nullish `??` — all too new. Write
  ES5-ish JS: `var`, plain `function`, feature-check before use.
- Programmatic `scrollTop` on `overflow:hidden` is clamped to 0 — scroll with a
  `transform: translateY(...)` on an inner wrapper instead.

**Video:** webOS does **not** composite `<video>` inside a nested iframe (audio
only). Keep playback at the top level (that's why Nost4lgia is its own page, not
an iframe). Treat one hardware decoder as the limit — don't play two videos at
once (the guide preview is paused before tuning).

## Build / install / test

```bash
node nost4lgia-src/build_channels.js    # regenerate channel data
python build_ipk.py                     # -> dist/tv.livingroom.shell_<ver>_all.ipk
ares-install --device tv dist/tv.livingroom.shell_<ver>_all.ipk
ares-launch  --device tv tv.livingroom.shell
```

- **Bump the version** in `build_ipk.py` (3 places: `VERSION`, the `APPINFO`
  JSON, and the `CONTROL` block) on every install, or webOS may not replace the
  app.
- webOS 5 **rejects zero-timestamp ipk members** ("ipk verified failed").
  `build_ipk.py` already stamps a real mtime — keep that.
- **Test the UI fast** by serving `launcher/` over plain HTTP and opening
  `spelunkr.html` in a desktop browser. The guide/player/schedule logic all work
  there; only webOS-specific behavior (hardware video, the physical Back key =
  keyCode 461) needs the real TV. Remember the desktop browser is modern, so it
  will *not* reproduce Chromium-68 breakage — re-check the constraints above by
  hand.

## Data model

- `spelunkr-channels.js`: `{ channels: [{ n, id, name, emoji, color, desc, start,
  items: [{ t, y, d, u }] }] }` where `d` is duration in seconds and `u` is the
  full archive.org download URL. Items may come from a `mp4` **or** `file` field
  upstream — `build_channels.js` handles both.
- The schedule is deterministic: each channel's sequence starts at its first
  1992+ item (`curIndex`) anchored to the current half-hour, and advances by real
  program durations. The guide grid maps air times to a time axis so block width
  == runtime.

## Don't commit

Generated or personal files: `launcher/spelunkr-channels.js`, `dist/`, `*.ipk`,
`tv-app/`, the TV pairing/inventory files, and local control scripts. See
`.gitignore`.

## Respect the source

Channel curation comes from Spelunkr (https://spelunkr.tv). Credit them, don't
redistribute their data as your own, and keep this project clearly independent.
