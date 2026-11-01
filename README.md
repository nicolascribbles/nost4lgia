# Nost4lgia

**A retro cable-TV experience for LG webOS TVs.** Nost4lgia turns your old LG TV
into a 90s cable box: a full-screen, remote-driven channel guide and player that
streams public-domain and archival video from the [Internet Archive](https://archive.org),
laid out like a classic on-screen TV guide — with a real time grid, number-key
tuning, and "set a reminder to switch channels" scheduling.

It ships inside a minimal home-screen launcher (**Home+ / "Living Room"**) so you
can jump straight into your apps and Nost4lgia without wading through the stock
webOS home screen.

> Built for a 2020 LG UN7000 (webOS 5.x, Chromium 68) but should run on any
> webOS TV that supports Developer Mode.

---

## Credit & how this is different

The idea of "cable TV, but weirder" — curated channels of archival footage that
play on a synced broadcast clock — comes from **[Spelunkr](https://spelunkr.tv)**.
All credit for that concept goes to them, and Nost4lgia pulls its channel lineup
from Spelunkr's public data. Please support the original.

Nost4lgia is **not** a copy of the Spelunkr web app. It is an independent,
open-source project with different goals:

| | Spelunkr (web) | Nost4lgia (this project) |
|---|---|---|
| Platform | Website in a browser | Native **webOS app** sideloaded onto the TV |
| Navigation | Mouse / pointer first | **TV-remote first** — D-pad, OK, number keys, Back |
| Guide | Channel-switcher UI | **Classic EPG grid** with a real time axis and proportionally-sized program blocks |
| Scheduling | Live synced broadcast | A local schedule you can browse ahead in, with **"remind me and switch" alerts** |
| Playback | Site's player | Plays Internet Archive MP4s directly in the TV's `<video>` |
| Look | Modern | **Vaporwave / Y2K** theme, monospace type |
| Runs | On spelunkr.tv's servers | Entirely on your TV + a local data file; no accounts |

If you just want the polished hosted experience, use Spelunkr. If you want a
hackable, remote-first channel grid running natively on an old LG TV, this is that.

---

## Features

- **Classic TV-guide grid** — channels down the left, a real clock time-axis
  across the top, and program blocks whose width matches their actual runtime
  (a 15-minute show is half a 30-minute slot).
- **Remote-native controls** — arrow keys to move, OK to watch, **0–9 to tune by
  channel number**, Back to step out (player → guide → launcher).
- **Live channel preview** in the guide's top-left corner.
- **Reminders** — highlight a show airing later, press OK, and when it's time a
  popup asks whether to switch to that channel.
- **Home+ launcher** — a fast, flat grid of your streaming apps; Nost4lgia is one
  of the tiles.
- Tuned for webOS 5's old Chromium (polyfill-free, no modern CSS/JS that breaks).

## Controls

**Guide**
- `▲ ▼` — change channel
- `◄ ►` — move through time (On now → later)
- `OK` — watch the highlighted show (if on now) or set/clear a **reminder** (if later)
- `0–9` — jump to a channel number
- `Back` — exit to the Home+ launcher

**Player**
- `▲ ▼` — channel up / down
- `◄ ►` — seek 15s
- `OK` — open the guide
- `0–9` — tune by number
- `Back` — back to the guide

---

## How it works

1. **Channel data** is baked into a single JavaScript file at build time
   (`launcher/spelunkr-channels.js`) by `spelunkr-src/build_channels.js`, which
   reads Spelunkr's public lineup/manifests and records each program's Internet
   Archive id, file, title, year, and duration. (This file is **not** committed —
   you generate it; see Setup.)
2. **The app** (`launcher/spelunkr.html`) reads that data, builds the schedule
   from each program's duration anchored to the current half hour, and plays the
   archive.org MP4s directly in a `<video>` element.
3. **Packaging** (`build_ipk.py`) assembles a webOS `.ipk` by hand (no SDK needed)
   with real file timestamps so webOS 5 will accept it.

No proxy or server is required at runtime — the TV streams from archive.org
directly, and all channel data is local.

---

## Setup

### 1. Enable Developer Mode on the TV
1. Install the **Developer Mode** app from the LG Content Store (needs a free LG
   account).
2. Open it, sign in, turn **Dev Mode Status** on (the TV reboots), then turn on
   **Key Server**. Note the **IP address** and **passphrase** it shows.

### 2. Install tooling on your computer
```bash
npm install -g @webosose/ares-cli
```
You also need **Node.js 18+** (for `build_channels.js`'s global `fetch`) and
**Python 3** with Pillow (`pip install pillow`) for the icon generation in
`build_ipk.py`.

Register the TV (replace the IP; enter the passphrase when asked):
```bash
ares-setup-device --add tv --info "host=<TV_IP> port=9922 username=prisoner"
ares-novacom --device tv --getkey
```

### 3. Build the channel data + package
```bash
node spelunkr-src/build_channels.js     # writes launcher/spelunkr-channels.js
python build_ipk.py                      # writes dist/tv.livingroom.shell_<ver>_all.ipk
```

### 4. Install and launch
```bash
ares-install --device tv dist/tv.livingroom.shell_2.2.0_all.ipk
ares-launch  --device tv tv.livingroom.shell
```

### Tip: one-button access
webOS won't let an app replace the physical Home button, but you can **long-press
a number key (1–9)** on the LG remote and assign the Living Room app as a
shortcut — then that number jumps straight in with no stock-home flash.

> Dev-mode apps stay installed only while Developer Mode is active; LG requires
> periodic renewal via the Dev Mode app.

---

## Project layout

```
launcher/
  index.html            Home+ launcher (the grid you land on)
  spelunkr.html         Nost4lgia — the TV guide + player
  logos/                channel + app icons (SVG)
  spelunkr-channels.js  generated channel data (not committed)
spelunkr-src/
  build_channels.js     fetches Spelunkr's public data -> spelunkr-channels.js
build_ipk.py            packages everything into a webOS .ipk
AGENTS.md               notes for AI coding agents
```

## License

[MIT](LICENSE) © Nicola Riker Urdaneta. Not affiliated with LG or Spelunkr.
Streamed content belongs to its respective owners / the Internet Archive.
