// Build a local, self-contained channel database from Spelunkr's public data.
// Fetched here (no CORS limits); the TV app then reads the local JSON and streams
// the same archive.org videos directly. Run: node nost4lgia-src/build_channels.js
const fs = require("fs");

const BASE = "https://data.spelunkr.tv/";
const OUT = "C:/Users/nicol/living-room/launcher/spelunkr-channels.js";
const MAX_ITEMS = 80; // plenty for a continuously-playing channel; keeps size sane

// Our own channel names (independent of Spelunkr's). Keyed by channel id.
const RENAME = {
  "saturday-morning": "CEREAL HOUR",
  "primetime": "PRIME CUTS",
  "syndicate": "RERUN ALLEY",
  "late-nite-local": "PUBLIC ACCESS",
  "happy-trees": "HAPPY ACCIDENTS",
  "computer-chronicles": "BOOT DISK",
  "open-mic": "LOCAL TALENT",
  "library-card": "STORYTIME",
  "nature-preserve": "WILDLANDS",
  "unpaid-programming": "AS SEEN ON TV",
  "radio-active-tv": "HEAVY ROTATION",
  "latchkey-tv": "AFTER SCHOOL",
  "kersplat": "SLIME TIME",
  "final-frontier": "DEEP SPACE",
  "rocket-punch": "MECHA ZONE",
  "ovatv": "RENTAL VAULT",
  "toonertia": "ACTION BLOCK",
  "late-nite-swimclub": "DEEP END",
  "warp-zone": "HIGH SCORE",
  "homeroom": "GUIDANCE",
  "mandatory-viewing": "ONBOARDING",
  "fallout-shelter": "Fallout",
  "dusty-trails": "HIGH NOON",
  "gumshoe": "Noir",
  "it-came-from": "CREATURE FEATURE",
  "daily-dread": "NIGHTMARE FUEL",
  "graveyard-shift": "MONSTER HOST",
  "ray-gun": "ATOMIC AGE",
  "signpost": "THE OTHER SIDE",
  "rubber-hose": "INKWELL",
  "meddling-kids": "SPOOKY KIDS",
  "suplex": "MAT CLASSIC",
  "vacation-slides": "HOME MOVIES",
  "waku-waku": "GAME SHOW JP"
};

// Dev/test channels kept in the data but hidden from the guide (the app only
// shows them with ?debug). Bumps-only + test pattern.
const HIDDEN = new Set(["oops-all-bumps", "test-pattern"]);

// Dial numbers for real channels that have none upstream (otherwise the app
// drops them into a 900+ fallback range).
const DIAL = { "waku-waku": 700 };

(async () => {
  const lineup = await (await fetch(BASE + "lineup.json")).json();
  const channels = [];

  for (const c of lineup.channels) {
    const vers = c.versions && c.versions.length ? c.versions[c.versions.length - 1] : null;
    const manPath = vers && vers.manifest
      ? vers.manifest
      : "manifests/" + c.id + "/v" + (c.version || 1) + ".json";

    let man;
    try {
      const res = await fetch(BASE + manPath);
      if (!res.ok) throw new Error("HTTP " + res.status);
      man = await res.json();
    } catch (e) {
      console.log("skip", c.id, "-", e.message);
      continue;
    }

    const items = (man.items || [])
      .filter((it) => it && it.id && (it.mp4 || it.file))
      .slice(0, MAX_ITEMS)
      .map((it) => ({
        t: it.title || it.id,
        y: it.year || "",
        d: it.duration || 0,
        u: "https://archive.org/download/" + it.id + "/" + encodeURIComponent(it.mp4 || it.file),
      }));

    if (!items.length) { console.log("empty", c.id); continue; }

    channels.push({
      n: (c.dial !== undefined && c.dial !== null) ? c.dial : DIAL[c.id],
      id: c.id,
      name: RENAME[c.id] || c.name,
      emoji: c.emoji || "",
      color: c.color || "#8a8a8a",
      desc: c.description || "",
      start: (vers && vers.startIndex) || 0,
      hidden: HIDDEN.has(c.id) || undefined, // kept in data, dropped from the guide
      items: items,
    });
    console.log("ch", String(c.dial).padStart(3), c.name, "-", items.length, "items");
  }

  channels.sort((a, b) => (a.n || 0) - (b.n || 0));
  // Written as a JS global so the TV app can load it via <script> (packaged
  // webOS apps can't fetch() local files).
  fs.writeFileSync(OUT, "window.SPELUNKR_CHANNELS=" + JSON.stringify({ channels: channels }) + ";");
  const kb = (fs.statSync(OUT).size / 1024).toFixed(0);
  console.log("\nWROTE", OUT, kb + "KB,", channels.length, "channels");
})().catch((e) => console.log("FATAL:", e.message));
